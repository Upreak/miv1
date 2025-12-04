"""
Intake Router - Main pipeline entry point for ALL ingestion sources.
Handles the complete flow: validation -> sanitization -> extraction -> candidate creation.
"""

import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse

from .config.intake_config import get_config
from .utils.qid_generator import generate_qid
from .utils.mime_validator import validate_mime_type
from .utils.file_hasher import calculate_file_hash
from .utils.logging_utils import get_logger

from .services.intake_service import get_intake_service
from .services.storage_service import get_storage_service
from .services.virus_scan_service import get_virus_scan_service
from .services.sanitizer_service import get_sanitizer_service
from .services.extraction_service import get_extraction_service
from .services.brain_parse_service import get_brain_parse_service
from .services.event_publisher import get_event_publisher, EventType

from .repositories.intake_repository import get_intake_repository

logger = get_logger(__name__)
config = get_config()

# Create router
intake_router = APIRouter(
    prefix="/intake",
    tags=["file-intake"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)


class IntakeRouter:
    """Main router for processing files from all sources."""

    def __init__(self, config=None):
        """
        Initialize intake router.
        
        Args:
            config: Configuration object
        """
        self.config = config or get_config()
        self.intake_service = get_intake_service(self.config)
        self.storage_service = get_storage_service(self.config)
        self.virus_scan_service = get_virus_scan_service(self.config)
        self.sanitizer_service = get_sanitizer_service(self.config)
        self.extraction_service = get_extraction_service(self.config)
        self.brain_parse_service = get_brain_parse_service(self.config)
        self.event_publisher = get_event_publisher(self.config)
        self.repository = get_intake_repository(self.config)
        
        logger.info("Intake router initialized")

    def process_file(self, file_bytes: bytes, filename: str, source: str, user_id: Optional[str] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Main pipeline entry point for ALL ingestion sources.
        
        Args:
            file_bytes: Raw file bytes
            filename: Original filename
            source: Source identifier (website, whatsapp, telegram, email_ingestion)
            user_id: User ID (optional)
            session_id: Session ID (optional)
            
        Returns:
            Dict with processing results
            
        Raises:
            ValueError: If file validation fails
            RuntimeError: If processing fails
        """
        logger.info(f"Processing file {filename} from source {source}")
        
        try:
            # Step 1: Generate QID
            logger.debug("Step 1: Generating QID")
            qid = generate_qid()
            
            # Step 2: Validate file
            logger.debug("Step 2: Validating file")
            validate_mime_type(file_bytes, filename)
            
            # Step 3: Calculate file hash
            logger.debug("Step 3: Calculating file hash")
            file_hash = calculate_file_hash(file_bytes)
            
            # Step 4: Store file in quarantine
            logger.debug("Step 4: Storing file in quarantine")
            storage_path = self.storage_service.store_quarantine_file(qid, file_bytes, filename)
            
            # Step 5: Create intake record
            logger.debug("Step 5: Creating intake record")
            record = self.repository.create_record(
                qid=qid,
                sid=session_id,
                source=source,
                user_id=user_id,
                original_filename=filename,
                status="quarantined",
                mime_type=self._detect_mime_type(file_bytes, filename),
                filesize=len(file_bytes),
                storage_path=storage_path,
                file_hash=file_hash
            )
            
            # Step 6: Virus scan
            logger.debug("Step 6: Virus scanning")
            scan_result = self.virus_scan_service.scan_file(storage_path)
            
            if scan_result.result == "infected":
                logger.warning(f"Virus detected in {filename}: {scan_result.virus_name}")
                self.repository.mark_infected(qid, scan_result.virus_name)
                self.repository.update_status(qid, "infected")
                return {
                    "qid": qid,
                    "status": "infected",
                    "virus_name": scan_result.virus_name,
                    "error_message": f"Virus detected: {scan_result.virus_name}"
                }
            
            # Step 7: Sanitize file
            logger.debug("Step 7: Sanitizing file")
            sanitized_path = self.sanitizer_service.sanitize(storage_path)
            self.repository.update_path(qid, sanitized_path)
            self.repository.update_status(qid, "sanitized")
            
            # Step 8: Extract text
            logger.debug("Step 8: Extracting text")
            extraction_result = self.extraction_service.extract_text(sanitized_path)
            
            if not extraction_result.success:
                logger.error(f"Text extraction failed for {filename}")
                self.repository.update_status(qid, "extraction_failed")
                self.repository.set_error(qid, f"Extraction failed: {extraction_result.errors}")
                return {
                    "qid": qid,
                    "status": "extraction_failed",
                    "error_message": f"Extraction failed: {extraction_result.errors}"
                }
            
            self.repository.save_extracted_text(qid, extraction_result.text)
            self.repository.update_status(qid, "extracted")
            
            # Step 9: Parse with Brain
            logger.debug("Step 9: Parsing with Brain")
            parse_result = self.brain_parse_service.parse_text(extraction_result.text, "resume")
            
            if not parse_result.success:
                logger.error(f"Brain parsing failed for {filename}")
                self.repository.update_status(qid, "parsing_failed")
                self.repository.set_error(qid, f"Parsing failed: {parse_result.errors}")
                return {
                    "qid": qid,
                    "status": "parsing_failed",
                    "error_message": f"Parsing failed: {parse_result.errors}"
                }
            
            # Step 10: Update candidate profile
            logger.debug("Step 10: Updating candidate profile")
            if user_id:
                self.repository.update_candidate_profile(user_id, parse_result.response)
            
            self.repository.save_parsed_output(qid, parse_result.response)
            self.repository.update_status(qid, "completed")
            
            # Step 11: Archive file
            logger.debug("Step 11: Archiving file")
            archive_path = self.storage_service.archive_file(qid, sanitized_path)
            self.repository.update_path(qid, archive_path)
            self.repository.update_status(qid, "archived")
            
            # Step 12: Publish completion event
            logger.debug("Step 12: Publishing completion event")
            self.event_publisher.publish_event(
                EventType.PROCESSING_COMPLETED,
                {"qid": qid, "user_id": user_id, "source": source}
            )
            
            result = {
                "qid": qid,
                "status": "completed",
                "source": source,
                "filename": filename,
                "file_type": self._detect_mime_type(file_bytes, filename),
                "provider_used": parse_result.provider,
                "model_used": parse_result.model,
                "success": parse_result.success,
                "response_time": parse_result.parse_time,
                "confidence_score": parse_result.confidence_score,
                "candidate_id": user_id
            }
            
            logger.info(f"Successfully processed file. QID: {qid}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing file {filename}: {str(e)}", exc_info=True)
            raise RuntimeError(f"Failed to process file: {str(e)}")
    
    def _detect_mime_type(self, file_bytes: bytes, filename: str) -> str:
        """
        Detect MIME type from file bytes.
        
        Args:
            file_bytes: Raw file bytes
            filename: Original filename
            
        Returns:
            str: Detected MIME type
        """
        # This would use a proper MIME type detection library
        # For now, we'll use a simple implementation
        import magic
        
        try:
            mime = magic.Magic(mime=True)
            return mime.from_buffer(file_bytes)
        except Exception:
            # Fallback to extension-based detection
            ext = filename.split('.')[-1].lower()
            mime_map = {
                'pdf': 'application/pdf',
                'doc': 'application/msword',
                'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'txt': 'text/plain',
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'png': 'image/png',
                'gif': 'image/gif'
            }
            return mime_map.get(ext, 'application/octet-stream')


# Global router instance
router_instance = IntakeRouter(config)


@intake_router.post("/initiate-upload")
async def initiate_upload(
    filename: str = Form(...),
    filesize: int = Form(...),
    mime_type: str = Form(...),
    source: str = Form(...),
    user_id: Optional[str] = Form(None),
    session_id: Optional[str] = Form(None)
):
    """
    Initiate file upload process.
    
    Args:
        filename: Original filename
        filesize: File size in bytes
        mime_type: MIME type
        source: Source identifier
        user_id: User ID (optional)
        session_id: Session ID (optional)
        
    Returns:
        Dict with upload initiation details
    """
    try:
        result = router_instance.intake_service.initiate_upload(
            filename=filename,
            filesize=filesize,
            mime_type=mime_type,
            source=source,
            user_id=user_id,
            session_id=session_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error initiating upload: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@intake_router.post("/complete-upload")
async def complete_upload(
    qid: str = Form(...),
    file_hash: str = Form(...)
):
    """
    Complete file upload process.
    
    Args:
        qid: File QID
        file_hash: File hash
        
    Returns:
        Dict with completion result
    """
    try:
        result = router_instance.intake_service.complete_upload(qid, file_hash)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error completing upload: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@intake_router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    source: str = Form(...),
    user_id: Optional[str] = Form(None),
    session_id: Optional[str] = Form(None)
):
    """
    Upload and process file directly.
    
    Args:
        file: Uploaded file
        source: Source identifier
        user_id: User ID (optional)
        session_id: Session ID (optional)
        
    Returns:
        Dict with processing result
    """
    try:
        # Read file content
        file_bytes = await file.read()
        
        # Process file
        result = router_instance.process_file(
            file_bytes=file_bytes,
            filename=file.filename,
            source=source,
            user_id=user_id,
            session_id=session_id
        )
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@intake_router.get("/status/{qid}")
async def get_status(qid: str):
    """
    Get file processing status.
    
    Args:
        qid: File QID
        
    Returns:
        Dict with status information
    """
    try:
        result = router_instance.intake_service.get_status(qid)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@intake_router.get("/history/{qid}")
async def get_processing_history(qid: str):
    """
    Get file processing history.
    
    Args:
        qid: File QID
        
    Returns:
        List with processing history
    """
    try:
        result = router_instance.intake_service.get_processing_history(qid)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting history: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@intake_router.post("/retry/{qid}")
async def retry_processing(qid: str):
    """
    Retry failed file processing.
    
    Args:
        qid: File QID
        
    Returns:
        Dict with retry result
    """
    try:
        result = router_instance.intake_service.retry_processing(qid)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrying processing: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@intake_router.get("/worker-status")
async def get_worker_status():
    """
    Get worker status information.
    
    Returns:
        Dict with worker status
    """
    try:
        result = router_instance.intake_service.get_worker_status()
        return result
    except Exception as e:
        logger.error(f"Error getting worker status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@intake_router.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Dict with health status
    """
    try:
        # Check database connection
        record = router_instance.repository.get_record("test")
        
        # Check storage service
        storage_status = router_instance.storage_service.get_storage_status()
        
        # Check event publisher
        event_status = router_instance.event_publisher.get_publisher_status()
        
        return {
            "status": "healthy",
            "database": "connected",
            "storage": storage_status,
            "event_publisher": event_status,
            "timestamp": "2023-12-01T12:00:00Z"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": "2023-12-01T12:00:00Z"
            }
        )


# Include router in FastAPI app
# This would be done in the main FastAPI app
# app.include_router(intake_router)