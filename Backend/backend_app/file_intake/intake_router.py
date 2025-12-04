"""
Intake Router - Main pipeline entry point for ALL ingestion sources.
Handles the complete flow: validation -> sanitization -> extraction -> candidate creation.
"""

import logging
from typing import Dict, Any, Optional
from backend_app.security.file_sanitizer.validator import validate_file
from backend_app.security.file_sanitizer.magic_bytes import detect_file_type
from backend_app.security.file_sanitizer.antivirus import scan_for_viruses
from backend_app.security.file_sanitizer.sanitizer import sanitize_text
from backend_app.text_extraction.final_97_percent_extractor import extract_text
from backend_app.services.candidate_creation_service import create_candidate_profile
from backend_app.services.brain_service import parse_resume_from_path

logger = logging.getLogger(__name__)


class IntakeRouter:
    """Main router for processing files from all sources."""

    @staticmethod
    def process_file(file_bytes: bytes, filename: str, source: str) -> Dict[str, Any]:
        """
        Main pipeline entry point for ALL ingestion sources.
        
        Args:
            file_bytes: Raw file bytes
            filename: Original filename
            source: Source identifier (website, whatsapp, telegram, email_ingestion)
            
        Returns:
            Dict with processing results
            
        Raises:
            ValueError: If file validation fails
            RuntimeError: If processing fails
        """
        logger.info(f"Processing file {filename} from source {source}")
        
        try:
            # Step 1: File validation
            logger.debug("Step 1: Validating file")
            validate_file(file_bytes, filename)
            
            # Step 2: Detect file type using magic bytes
            logger.debug("Step 2: Detecting file type")
            file_type = detect_file_type(file_bytes, filename)
            logger.debug(f"Detected file type: {file_type}")
            
            # Step 3: Antivirus scan
            logger.debug("Step 3: Scanning for viruses")
            scan_for_viruses(file_bytes, filename)
            
            # Step 4: Write temporary file for brain service
            logger.debug("Step 4: Writing temporary file for brain service")
            import tempfile
            from pathlib import Path
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as tf:
                tf.write(file_bytes)
                tmp_path = Path(tf.name)
            
            # Step 5: Parse resume using brain service
            logger.debug("Step 5: Parsing resume using brain service")
            brain_output = parse_resume_from_path(tmp_path, strategy="fast")
            
            # Step 6: Create candidate profile with parsed result
            logger.debug("Step 6: Creating candidate profile with parsed result")
            candidate_id = create_candidate_profile(
                raw_text=brain_output.get("response") or "",  # Store parsed response
                source=source,
                filename=filename,
                file_type=file_type
            )
            
            # Cleanup temporary file
            try:
                tmp_path.unlink(missing_ok=True)
            except Exception:
                logger.warning(f"Failed to cleanup temporary file: {tmp_path}")
            
            result = {
                "candidate_id": candidate_id,
                "status": "processed",
                "source": source,
                "filename": filename,
                "file_type": file_type,
                "provider_used": brain_output.get("provider"),
                "model_used": brain_output.get("model"),
                "success": brain_output.get("success"),
                "response_time": brain_output.get("response_time")
            }
            
            logger.info(f"Successfully processed file. Candidate ID: {candidate_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing file {filename}: {str(e)}", exc_info=True)
            raise RuntimeError(f"Failed to process file: {str(e)}")