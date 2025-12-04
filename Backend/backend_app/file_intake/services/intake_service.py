"""
Intake Service - Central orchestrator for the file intake pipeline.

This service provides:
- Upload initiation and management
- Pipeline orchestration
- Status tracking
- Error handling
- Event publishing
- Integration with storage, virus scan, sanitizer, extraction, and parsing services
"""

import logging
import os
import tempfile
import uuid
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from pathlib import Path

from ..config.intake_config import get_config
from ..utils.qid_generator import generate_qid
from ..utils.sid_generator import generate_sid
from ..utils.mime_validator import validate_mime_type
from ..utils.file_hasher import calculate_file_hash
from ..utils.logging_utils import get_logger, get_security_logger

from .storage_service import get_storage_service
from .virus_scan_service import get_virus_scan_service
from .sanitizer_service import get_sanitizer_service
from .extraction_service import get_extraction_service
from .brain_parse_service import get_brain_parse_service

from ..repositories.intake_repository import get_intake_repository

logger = get_logger(__name__)
security_logger = get_security_logger()


class IntakeService:
    """Main intake service for orchestrating the file processing pipeline."""
    
    def __init__(self, config=None):
        """
        Initialize intake service.
        
        Args:
            config: Configuration object
        """
        self.config = config or get_config()
        
        # Initialize services
        self.storage_service = get_storage_service(self.config)
        self.virus_scan_service = get_virus_scan_service(self.config)
        self.sanitizer_service = get_sanitizer_service(self.config)
        self.extraction_service = get_extraction_service(self.config)
        self.brain_parse_service = get_brain_parse_service(self.config)
        self.repository = get_intake_repository(self.config)
        
        # Pipeline stages
        self.pipeline_stages = [
            "initiated",
            "quarantined",
            "scanned",
            "clean",
            "sanitized",
            "extracted",
            "parsed",
            "completed",
            "failed"
        ]
        
        logger.info("Intake service initialized")
    
    def initiate_upload(self, filename: str, filesize: int, mime_type: str, 
                       source: str, user_id: Optional[str] = None, 
                       session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Initiate file upload process.
        
        Args:
            filename: Original filename
            filesize: File size in bytes
            mime_type: MIME type of file
            source: Upload source (web, whatsapp, telegram, email)
            user_id: Optional user ID
            session_id: Optional session ID
            
        Returns:
            Dict: Upload initiation result
        """
        try:
            logger.info(f"Initiating upload for {filename} from {source}")
            
            # Generate QID
            qid = generate_qid()
            
            # Validate file type
            if not validate_mime_type(mime_type):
                raise ValueError(f"Invalid file type: {mime_type}")
            
            # Check file size
            if filesize > self.config.security.max_file_size:
                raise ValueError(f"File size exceeds maximum allowed: {filesize} bytes")
            
            # Generate storage path
            storage_path = self.storage_service.generate_storage_path(qid, filename)
            
            # Create database record
            record = self.repository.create_record(
                qid=qid,
                sid=session_id or generate_sid(),
                source=source,
                user_id=user_id,
                original_filename=filename,
                status="initiated",
                mime_type=mime_type,
                filesize=filesize,
                storage_path=storage_path
            )
            
            # Generate presigned upload URL
            upload_url = self.storage_service.generate_presigned_url(qid, filename)
            
            # Log security event
            security_logger.log_file_upload(
                file_id=qid,
                filename=filename,
                source=source,
                user_id=user_id,
                file_size=filesize,
                mime_type=mime_type
            )
            
            logger.info(f"Upload initiated for {filename} with QID: {qid}")
            
            return {
                "qid": qid,
                "upload_url": upload_url,
                "expires_at": self._get_upload_expiry(),
                "max_file_size": self.config.security.max_file_size,
                "allowed_types": self.config.security.allowed_file_types
            }
            
        except Exception as e:
            logger.error(f"Failed to initiate upload for {filename}: {str(e)}")
            raise RuntimeError(f"Upload initiation failed: {str(e)}")
    
    def complete_upload(self, qid: str, file_bytes: bytes) -> Dict[str, Any]:
        """
        Complete file upload and start processing pipeline.
        
        Args:
            qid: Upload QID
            file_bytes: File bytes
            
        Returns:
            Dict: Processing result
        """
        try:
            logger.info(f"Completing upload for QID: {qid}")
            
            # Get record
            record = self.repository.get_record(qid)
            if not record:
                raise ValueError(f"Record not found for QID: {qid}")
            
            # Update record status
            self.repository.update_status(qid, "quarantined")
            
            # Store file
            storage_path = self.storage_service.store_file(qid, record.original_filename, file_bytes)
            
            # Update record with storage path
            self.repository.update_storage_path(qid, storage_path)
            
            # Start processing pipeline
            processing_result = self._start_processing_pipeline(qid)
            
            logger.info(f"Upload completed for QID: {qid}")
            
            return {
                "qid": qid,
                "status": "processing",
                "processing_result": processing_result
            }
            
        except Exception as e:
            logger.error(f"Failed to complete upload for QID {qid}: {str(e)}")
            self.repository.update_status(qid, "failed")
            self.repository.set_error(qid, f"Upload completion failed: {str(e)}")
            raise RuntimeError(f"Upload completion failed: {str(e)}")
    
    def _start_processing_pipeline(self, qid: str) -> Dict[str, Any]:
        """
        Start the processing pipeline for a file.
        
        Args:
            qid: File QID
            
        Returns:
            Dict: Pipeline result
        """
        try:
            logger.info(f"Starting processing pipeline for QID: {qid}")
            
            # Get record
            record = self.repository.get_record(qid)
            if not record:
                raise ValueError(f"Record not found for QID: {qid}")
            
            # Start virus scan
            scan_result = self._perform_virus_scan(qid)
            
            if scan_result.result == "infected":
                self.repository.update_status(qid, "failed")
                self.repository.set_error(qid, f"Virus detected: {scan_result.virus_name}")
                return {
                    "status": "failed",
                    "error": f"Virus detected: {scan_result.virus_name}"
                }
            
            # File is clean, proceed to sanitization
            sanitize_result = self._perform_sanitization(qid)
            
            if not sanitize_result.success:
                self.repository.update_status(qid, "failed")
                self.repository.set_error(qid, f"Sanitization failed: {sanitize_result.errors}")
                return {
                    "status": "failed",
                    "error": f"Sanitization failed: {sanitize_result.errors}"
                }
            
            # Update record with sanitized path
            if sanitize_result.sanitized_path:
                self.repository.update_storage_path(qid, sanitize_result.sanitized_path)
                self.repository.update_filename(qid, sanitize_result.sanitized_filename)
            
            # Perform text extraction
            extract_result = self._perform_extraction(qid)
            
            if not extract_result.success:
                self.repository.update_status(qid, "failed")
                self.repository.set_error(qid, f"Extraction failed: {extract_result.errors}")
                return {
                    "status": "failed",
                    "error": f"Extraction failed: {extract_result.errors}"
                }
            
            # Store extracted text
            self.repository.save_extracted_text(qid, extract_result.text)
            
            # Perform brain parsing
            parse_result = self._perform_parsing(qid, extract_result.text)
            
            if not parse_result.success:
                self.repository.update_status(qid, "failed")
                self.repository.set_error(qid, f"Parsing failed: {parse_result.errors}")
                return {
                    "status": "failed",
                    "error": f"Parsing failed: {parse_result.errors}"
                }
            
            # Store parsed result
            self.repository.save_parsed_output(qid, parse_result.to_dict())
            
            # Update candidate profile if user exists
            if record.user_id and parse_result.success:
                self._update_candidate_profile(record.user_id, parse_result)
            
            # Mark as completed
            self.repository.update_status(qid, "completed")
            
            logger.info(f"Processing pipeline completed for QID: {qid}")
            
            return {
                "status": "completed",
                "parse_result": parse_result.to_dict(),
                "processing_time": self._get_processing_time(qid)
            }
            
        except Exception as e:
            logger.error(f"Pipeline processing failed for QID {qid}: {str(e)}")
            self.repository.update_status(qid, "failed")
            self.repository.set_error(qid, f"Pipeline failed: {str(e)}")
            raise RuntimeError(f"Pipeline processing failed: {str(e)}")
    
    def _perform_virus_scan(self, qid: str) -> Dict[str, Any]:
        """
        Perform virus scan on file.
        
        Args:
            qid: File QID
            
        Returns:
            Dict: Scan result
        """
        try:
            logger.info(f"Performing virus scan for QID: {qid}")
            
            # Get record
            record = self.repository.get_record(qid)
            if not record:
                raise ValueError(f"Record not found for QID: {qid}")
            
            # Perform virus scan
            scan_results = self.virus_scan_service.scan_file(record.storage_path)
            
            # Check if any engine detected virus
            for engine_name, result in scan_results.items():
                if result.result == "infected":
                    logger.warning(f"Virus detected by {engine_name}: {result.virus_name}")
                    return {
                        "result": "infected",
                        "engine": engine_name,
                        "virus_name": result.virus_name,
                        "scan_time": result.scan_time
                    }
            
            # File is clean
            logger.info(f"Virus scan passed for QID: {qid}")
            return {
                "result": "clean",
                "scan_time": sum(r.scan_time or 0 for r in scan_results.values())
            }
            
        except Exception as e:
            logger.error(f"Virus scan failed for QID {qid}: {str(e)}")
            raise RuntimeError(f"Virus scan failed: {str(e)}")
    
    def _perform_sanitization(self, qid: str) -> Dict[str, Any]:
        """
        Perform file sanitization.
        
        Args:
            qid: File QID
            
        Returns:
            Dict: Sanitization result
        """
        try:
            logger.info(f"Performing sanitization for QID: {qid}")
            
            # Get record
            record = self.repository.get_record(qid)
            if not record:
                raise ValueError(f"Record not found for QID: {qid}")
            
            # Perform sanitization
            sanitize_result = self.sanitizer_service.sanitize_file(record.storage_path)
            
            if sanitize_result.success:
                logger.info(f"Sanitization completed for QID: {qid}")
            else:
                logger.warning(f"Sanitization failed for QID: {qid}")
            
            return sanitize_result
            
        except Exception as e:
            logger.error(f"Sanitization failed for QID {qid}: {str(e)}")
            raise RuntimeError(f"Sanitization failed: {str(e)}")
    
    def _perform_extraction(self, qid: str) -> Dict[str, Any]:
        """
        Perform text extraction.
        
        Args:
            qid: File QID
            
        Returns:
            Dict: Extraction result
        """
        try:
            logger.info(f"Performing extraction for QID: {qid}")
            
            # Get record
            record = self.repository.get_record(qid)
            if not record:
                raise ValueError(f"Record not found for QID: {qid}")
            
            # Perform extraction
            extract_result = self.extraction_service.extract_text(record.storage_path)
            
            if extract_result.success:
                logger.info(f"Extraction completed for QID: {qid}, extracted {len(extract_result.text)} characters")
            else:
                logger.warning(f"Extraction failed for QID: {qid}")
            
            return extract_result
            
        except Exception as e:
            logger.error(f"Extraction failed for QID {qid}: {str(e)}")
            raise RuntimeError(f"Extraction failed: {str(e)}")
    
    def _perform_parsing(self, qid: str, text: str) -> Dict[str, Any]:
        """
        Perform brain parsing.
        
        Args:
            qid: File QID
            text: Extracted text
            
        Returns:
            Dict: Parsing result
        """
        try:
            logger.info(f"Performing parsing for QID: {qid}")
            
            # Determine document type
            document_type = self._determine_document_type(qid)
            
            # Perform parsing
            parse_result = self.brain_parse_service.parse_text(text, document_type)
            
            if parse_result.success:
                logger.info(f"Parsing completed for QID: {qid}, confidence: {parse_result.confidence_score}")
            else:
                logger.warning(f"Parsing failed for QID: {qid}")
            
            return parse_result
            
        except Exception as e:
            logger.error(f"Parsing failed for QID {qid}: {str(e)}")
            raise RuntimeError(f"Parsing failed: {str(e)}")
    
    def _determine_document_type(self, qid: str) -> str:
        """
        Determine document type based on file characteristics.
        
        Args:
            qid: File QID
            
        Returns:
            str: Document type
        """
        # Get record
        record = self.repository.get_record(qid)
        if not record:
            raise ValueError(f"Record not found for QID: {qid}")
        
        # Determine document type based on MIME type and filename
        mime_type = record.mime_type.lower()
        filename = record.original_filename.lower()
        
        if mime_type == 'application/pdf':
            return "document"
        elif mime_type in ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            # Check if it's likely a resume
            resume_keywords = ['resume', 'cv', 'curriculum', 'vitae', 'developer', 'engineer', 'manager']
            if any(keyword in filename for keyword in resume_keywords):
                return "resume"
            return "document"
        elif mime_type in ['text/plain']:
            # Check if it's likely a resume
            resume_keywords = ['resume', 'cv', 'curriculum', 'vitae']
            if any(keyword in filename for keyword in resume_keywords):
                return "resume"
            return "document"
        else:
            return "document"
    
    def _update_candidate_profile(self, user_id: str, parse_result: Dict[str, Any]):
        """
        Update candidate profile with parsed information.
        
        Args:
            user_id: User ID
            parse_result: Parse result
        """
        try:
            logger.info(f"Updating candidate profile for user: {user_id}")
            
            # Extract contact information
            contact_info = {}
            if parse_result.get('contact'):
                contact = parse_result['contact']
                contact_info = {
                    'email': contact.get('email'),
                    'phone': contact.get('phone'),
                    'linkedin': contact.get('linkedin'),
                    'github': contact.get('github'),
                    'location': contact.get('location')
                }
            
            # Extract skills
            skills = []
            if parse_result.get('skills'):
                skills = [skill['name'] for skill in parse_result['skills']]
            
            # Extract experience
            experience = []
            if parse_result.get('experience'):
                for exp in parse_result['experience']:
                    experience.append({
                        'company': exp.get('company'),
                        'position': exp.get('position'),
                        'start_date': exp.get('start_date'),
                        'end_date': exp.get('end_date'),
                        'description': exp.get('description')
                    })
            
            # Update candidate profile in database
            # This would typically call a candidate service
            logger.info(f"Profile update data prepared for user: {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to update candidate profile for user {user_id}: {str(e)}")
            # Don't fail the pipeline if profile update fails
            pass
    
    def get_upload_status(self, qid: str) -> Dict[str, Any]:
        """
        Get upload status.
        
        Args:
            qid: Upload QID
            
        Returns:
            Dict: Status information
        """
        try:
            record = self.repository.get_record(qid)
            if not record:
                raise ValueError(f"Record not found for QID: {qid}")
            
            return {
                "qid": qid,
                "status": record.status,
                "original_filename": record.original_filename,
                "mime_type": record.mime_type,
                "filesize": record.filesize,
                "created_at": record.created_at.isoformat(),
                "updated_at": record.updated_at.isoformat(),
                "error_message": record.error_message
            }
            
        except Exception as e:
            logger.error(f"Failed to get status for QID {qid}: {str(e)}")
            raise RuntimeError(f"Status check failed: {str(e)}")
    
    def get_processing_history(self, qid: str) -> List[Dict[str, Any]]:
        """
        Get processing history for a file.
        
        Args:
            qid: File QID
            
        Returns:
            List: Processing history
        """
        try:
            record = self.repository.get_record(qid)
            if not record:
                raise ValueError(f"Record not found for QID: {qid}")
            
            # Get processing history from repository
            history = self.repository.get_processing_history(qid)
            
            return history
            
        except Exception as e:
            logger.error(f"Failed to get processing history for QID {qid}: {str(e)}")
            raise RuntimeError(f"History retrieval failed: {str(e)}")
    
    def retry_processing(self, qid: str) -> Dict[str, Any]:
        """
        Retry processing for a failed file.
        
        Args:
            qid: File QID
            
        Returns:
            Dict: Retry result
        """
        try:
            logger.info(f"Retrying processing for QID: {qid}")
            
            # Get record
            record = self.repository.get_record(qid)
            if not record:
                raise ValueError(f"Record not found for QID: {qid}")
            
            # Check if file is in failed state
            if record.status != "failed":
                raise ValueError(f"File is not in failed state: {record.status}")
            
            # Clear error message
            self.repository.clear_error(qid)
            
            # Start processing pipeline
            processing_result = self._start_processing_pipeline(qid)
            
            logger.info(f"Processing retry completed for QID: {qid}")
            
            return {
                "qid": qid,
                "status": "processing",
                "processing_result": processing_result
            }
            
        except Exception as e:
            logger.error(f"Retry processing failed for QID {qid}: {str(e)}")
            raise RuntimeError(f"Retry processing failed: {str(e)}")
    
    def _get_upload_expiry(self) -> str:
        """Get upload expiry timestamp."""
        expiry_time = datetime.utcnow() + self.config.upload.expiry_duration
        return expiry_time.isoformat()
    
    def _get_processing_time(self, qid: str) -> float:
        """Get processing time in seconds."""
        record = self.repository.get_record(qid)
        if not record:
            return 0.0
        
        created_time = record.created_at
        updated_time = record.updated_at
        
        if updated_time:
            return (updated_time - created_time).total_seconds()
        else:
            return 0.0


# Global intake service instance
def get_intake_service(config=None) -> IntakeService:
    """Get intake service instance."""
    if config is None:
        config = get_config()
    return IntakeService(config)