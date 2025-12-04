"""
Extraction Worker - Handles text extraction from uploaded files.

This worker provides:
- Asynchronous text extraction
- Multiple format support (PDF, DOC, DOCX, images, etc.)
- Retry mechanisms
- Logging and monitoring
- Dead letter queue handling
"""

import logging
import time
import traceback
from typing import Dict, Any, Optional
from datetime import datetime

from ..config.intake_config import get_config
from ..utils.logging_utils import get_logger, get_worker_logger

from ..services.extraction_service import get_extraction_service
from ..services.event_publisher import get_event_publisher, EventType
from ..repositories.intake_repository import get_intake_repository

logger = get_logger(__name__)
worker_logger = get_worker_logger(__name__)


class ExtractionWorker:
    """Extraction worker for processing text extraction requests."""
    
    def __init__(self, config=None):
        """
        Initialize extraction worker.
        
        Args:
            config: Configuration object
        """
        self.config = config or get_config()
        self.extraction_service = get_extraction_service(self.config)
        self.event_publisher = get_event_publisher(self.config)
        self.repository = get_intake_repository(self.config)
        
        # Worker configuration
        self.max_retries = self.config.worker.max_retries
        self.retry_delay = self.config.worker.retry_delay
        self.timeout = self.config.worker.timeout
        
        logger.info("Extraction worker initialized")
    
    def process_extraction_request(self, qid: str) -> bool:
        """
        Process text extraction request.
        
        Args:
            qid: File QID to extract text from
            
        Returns:
            bool: True if extraction completed successfully
        """
        try:
            worker_logger.info(f"Processing extraction request for QID: {qid}")
            
            # Get record
            record = self.repository.get_record(qid)
            if not record:
                worker_logger.error(f"Record not found for QID: {qid}")
                return False
            
            # Update status to extracting
            self.repository.update_status(qid, "extracting")
            
            # Perform text extraction
            extraction_result = self._perform_extraction(qid)
            
            if extraction_result.success:
                # Store extracted text
                self.repository.save_extracted_text(qid, extraction_result.text)
                
                # Update record with extraction metadata
                extraction_metadata = {
                    "extraction_time": extraction_result.extraction_time,
                    "file_size": extraction_result.file_size,
                    "hash_value": extraction_result.hash_value,
                    "confidence_score": extraction_result.confidence_score,
                    "language": extraction_result.language,
                    "warnings": extraction_result.warnings,
                    "errors": extraction_result.errors
                }
                
                self.repository.update_extraction_metadata(qid, extraction_metadata)
                
                # Update status to extracted
                self.repository.update_status(qid, "extracted")
                
                # Publish extraction completed event
                self.event_publisher.publish_extraction_completed(qid, {
                    "result": "success",
                    "text_length": len(extraction_result.text) if extraction_result.text else 0,
                    "extraction_time": extraction_result.extraction_time,
                    "confidence_score": extraction_result.confidence_score,
                    "warnings": extraction_result.warnings,
                    "errors": extraction_result.errors
                })
                
                # Request parsing
                self.event_publisher.publish_parse_requested(qid, {
                    "timestamp": datetime.utcnow().isoformat(),
                    "previous_status": "extracted"
                })
                
                worker_logger.info(f"Extraction completed successfully for QID: {qid}")
                return True
            else:
                # Extraction failed
                self.repository.update_status(qid, "failed")
                self.repository.set_error(qid, f"Extraction failed: {extraction_result.errors}")
                
                # Publish failed event
                self.event_publisher.publish_processing_failed(qid, {
                    "error": f"Extraction failed: {extraction_result.errors}",
                    "stage": "extraction",
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                worker_logger.error(f"Extraction failed for QID: {qid}")
                return False
                
        except Exception as e:
            worker_logger.error(f"Extraction failed for QID {qid}: {str(e)}")
            worker_logger.error(traceback.format_exc())
            
            # Update status to failed
            self.repository.update_status(qid, "failed")
            self.repository.set_error(qid, f"Extraction failed: {str(e)}")
            
            # Publish failed event
            self.event_publisher.publish_processing_failed(qid, {
                "error": str(e),
                "stage": "extraction",
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return False
    
    def _perform_extraction(self, qid: str) -> Dict[str, Any]:
        """
        Perform text extraction with retry logic.
        
        Args:
            qid: File QID to extract text from
            
        Returns:
            Dict: Extraction result
        """
        record = self.repository.get_record(qid)
        if not record:
            raise ValueError(f"Record not found for QID: {qid}")
        
        retry_count = 0
        
        while retry_count < self.max_retries:
            try:
                # Perform text extraction
                result = self.extraction_service.extract_text(record.storage_path)
                
                # Validate result
                if not self._validate_extraction_result(result):
                    raise ValueError("Invalid extraction result")
                
                return result
                
            except Exception as e:
                retry_count += 1
                worker_logger.warning(f"Extraction attempt {retry_count} failed for QID {qid}: {str(e)}")
                
                if retry_count < self.max_retries:
                    # Wait before retry
                    time.sleep(self.retry_delay)
                else:
                    raise RuntimeError(f"Extraction failed after {self.max_retries} attempts: {str(e)}")
    
    def _validate_extraction_result(self, result: Dict[str, Any]) -> bool:
        """
        Validate extraction result.
        
        Args:
            result: Extraction result to validate
            
        Returns:
            bool: True if result is valid
        """
        required_fields = ["success", "extraction_time"]
        
        for field in required_fields:
            if field not in result:
                return False
        
        # Validate success flag
        if not isinstance(result["success"], bool):
            return False
        
        # Validate extraction time
        if result["extraction_time"] is not None and result["extraction_time"] < 0:
            return False
        
        return True
    
    def process_retry_request(self, qid: str) -> bool:
        """
        Process retry request for failed extraction.
        
        Args:
            qid: File QID to retry
            
        Returns:
            bool: True if retry completed successfully
        """
        try:
            worker_logger.info(f"Processing extraction retry request for QID: {qid}")
            
            # Get record
            record = self.repository.get_record(qid)
            if not record:
                worker_logger.error(f"Record not found for QID: {qid}")
                return False
            
            # Check if record is in failed state
            if record.status != "failed":
                worker_logger.warning(f"Record is not in failed state: {record.status}")
                return False
            
            # Clear error message
            self.repository.clear_error(qid)
            
            # Process extraction request
            return self.process_extraction_request(qid)
            
        except Exception as e:
            worker_logger.error(f"Extraction retry failed for QID {qid}: {str(e)}")
            return False
    
    def get_worker_status(self) -> Dict[str, Any]:
        """
        Get worker status.
        
        Returns:
            Dict: Worker status information
        """
        try:
            # Get pending extraction requests
            pending_extractions = self.repository.get_records_by_status("extracting")
            queued_extractions = self.repository.get_records_by_status("queued")
            
            return {
                "worker_id": "extraction_worker",
                "status": "active",
                "pending_extractions": len(pending_extractions),
                "queued_extractions": len(queued_extractions),
                "max_retries": self.max_retries,
                "retry_delay": self.retry_delay,
                "timeout": self.timeout
            }
            
        except Exception as e:
            logger.error(f"Failed to get worker status: {str(e)}")
            return {
                "worker_id": "extraction_worker",
                "status": "error",
                "error": str(e)
            }


def create_worker(config=None) -> ExtractionWorker:
    """Create extraction worker instance."""
    return ExtractionWorker(config)


def main():
    """Main worker entry point."""
    try:
        # Create worker
        worker = create_worker()
        
        # Subscribe to extraction requests
        event_publisher = get_event_publisher()
        
        def handle_extraction_request(event):
            """Handle extraction request event."""
            qid = event.qid
            worker_logger.info(f"Received extraction request for QID: {qid}")
            worker.process_extraction_request(qid)
        
        def handle_retry_request(event):
            """Handle retry request event."""
            qid = event.qid
            worker_logger.info(f"Received extraction retry request for QID: {qid}")
            worker.process_retry_request(qid)
        
        # Subscribe to events
        event_publisher.subscribe_to_event(EventType.EXTRACTION_REQUESTED, handle_extraction_request)
        event_publisher.subscribe_to_event(EventType.RETRY_REQUESTED, handle_retry_request)
        
        # Start processing events
        worker_logger.info("Extraction worker started")
        event_publisher.process_events(EventType.EXTRACTION_REQUESTED)
        
    except KeyboardInterrupt:
        logger.info("Extraction worker stopped by user")
    except Exception as e:
        logger.error(f"Extraction worker failed: {str(e)}")
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    main()