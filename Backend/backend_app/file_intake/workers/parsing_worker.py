"""
Parsing Worker - Handles brain parsing of extracted text.

This worker provides:
- Asynchronous text parsing
- Resume and document parsing
- Skill extraction
- Experience analysis
- Education parsing
- Contact information extraction
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

from ..services.brain_parse_service import get_brain_parse_service
from ..services.event_publisher import get_event_publisher, EventType
from ..repositories.intake_repository import get_intake_repository

logger = get_logger(__name__)
worker_logger = get_worker_logger(__name__)


class ParsingWorker:
    """Parsing worker for processing text parsing requests."""
    
    def __init__(self, config=None):
        """
        Initialize parsing worker.
        
        Args:
            config: Configuration object
        """
        self.config = config or get_config()
        self.brain_parse_service = get_brain_parse_service(self.config)
        self.event_publisher = get_event_publisher(self.config)
        self.repository = get_intake_repository(self.config)
        
        # Worker configuration
        self.max_retries = self.config.worker.max_retries
        self.retry_delay = self.config.worker.retry_delay
        self.timeout = self.config.worker.timeout
        
        logger.info("Parsing worker initialized")
    
    def process_parsing_request(self, qid: str) -> bool:
        """
        Process text parsing request.
        
        Args:
            qid: File QID to parse
            
        Returns:
            bool: True if parsing completed successfully
        """
        try:
            worker_logger.info(f"Processing parsing request for QID: {qid}")
            
            # Get record
            record = self.repository.get_record(qid)
            if not record:
                worker_logger.error(f"Record not found for QID: {qid}")
                return False
            
            # Update status to parsing
            self.repository.update_status(qid, "parsing")
            
            # Get extracted text
            extracted_text = self.repository.get_extracted_text(qid)
            if not extracted_text:
                error_msg = "No extracted text found for parsing"
                worker_logger.error(error_msg)
                self.repository.update_status(qid, "failed")
                self.repository.set_error(qid, error_msg)
                return False
            
            # Perform brain parsing
            parse_result = self._perform_parsing(qid, extracted_text)
            
            if parse_result.success:
                # Store parsed result
                parsed_output = parse_result.to_dict()
                self.repository.save_parsed_output(qid, parsed_output)
                
                # Update record with parsing metadata
                parsing_metadata = {
                    "parse_time": parse_result.parse_time,
                    "confidence_score": parse_result.confidence_score,
                    "document_type": parsed_output.get("metadata", {}).get("document_type", "unknown"),
                    "contact_info": parsed_output.get("contact"),
                    "skills_count": len(parsed_output.get("skills", [])),
                    "experience_count": len(parsed_output.get("experience", [])),
                    "education_count": len(parsed_output.get("education", [])),
                    "warnings": parse_result.warnings,
                    "errors": parse_result.errors
                }
                
                self.repository.update_parsing_metadata(qid, parsing_metadata)
                
                # Update candidate profile if user exists
                if record.user_id:
                    self._update_candidate_profile(record.user_id, parse_result)
                
                # Update status to completed
                self.repository.update_status(qid, "completed")
                
                # Publish parsing completed event
                self.event_publisher.publish_parse_completed(qid, {
                    "result": "success",
                    "confidence_score": parse_result.confidence_score,
                    "parse_time": parse_result.parse_time,
                    "document_type": parsed_output.get("metadata", {}).get("document_type", "unknown"),
                    "contact_info": parsed_output.get("contact"),
                    "skills_count": len(parsed_output.get("skills", [])),
                    "experience_count": len(parsed_output.get("experience", [])),
                    "education_count": len(parsed_output.get("education", [])),
                    "warnings": parse_result.warnings,
                    "errors": parse_result.errors
                })
                
                # Publish processing completed event
                self.event_publisher.publish_processing_completed(qid, {
                    "timestamp": datetime.utcnow().isoformat(),
                    "total_processing_time": self._get_processing_time(qid),
                    "final_status": "completed"
                })
                
                worker_logger.info(f"Parsing completed successfully for QID: {qid}")
                return True
            else:
                # Parsing failed
                self.repository.update_status(qid, "failed")
                self.repository.set_error(qid, f"Parsing failed: {parse_result.errors}")
                
                # Publish failed event
                self.event_publisher.publish_processing_failed(qid, {
                    "error": f"Parsing failed: {parse_result.errors}",
                    "stage": "parsing",
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                worker_logger.error(f"Parsing failed for QID: {qid}")
                return False
                
        except Exception as e:
            worker_logger.error(f"Parsing failed for QID {qid}: {str(e)}")
            worker_logger.error(traceback.format_exc())
            
            # Update status to failed
            self.repository.update_status(qid, "failed")
            self.repository.set_error(qid, f"Parsing failed: {str(e)}")
            
            # Publish failed event
            self.event_publisher.publish_processing_failed(qid, {
                "error": str(e),
                "stage": "parsing",
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return False
    
    def _perform_parsing(self, qid: str, text: str) -> Dict[str, Any]:
        """
        Perform brain parsing with retry logic.
        
        Args:
            qid: File QID to parse
            text: Extracted text to parse
            
        Returns:
            Dict: Parsing result
        """
        record = self.repository.get_record(qid)
        if not record:
            raise ValueError(f"Record not found for QID: {qid}")
        
        retry_count = 0
        
        while retry_count < self.max_retries:
            try:
                # Determine document type
                document_type = self._determine_document_type(qid)
                
                # Perform parsing
                result = self.brain_parse_service.parse_text(text, document_type)
                
                # Validate result
                if not self._validate_parse_result(result):
                    raise ValueError("Invalid parsing result")
                
                return result
                
            except Exception as e:
                retry_count += 1
                worker_logger.warning(f"Parsing attempt {retry_count} failed for QID {qid}: {str(e)}")
                
                if retry_count < self.max_retries:
                    # Wait before retry
                    time.sleep(self.retry_delay)
                else:
                    raise RuntimeError(f"Parsing failed after {self.max_retries} attempts: {str(e)}")
    
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
    
    def _validate_parse_result(self, result: Dict[str, Any]) -> bool:
        """
        Validate parsing result.
        
        Args:
            result: Parsing result to validate
            
        Returns:
            bool: True if result is valid
        """
        required_fields = ["success", "parse_time"]
        
        for field in required_fields:
            if field not in result:
                return False
        
        # Validate success flag
        if not isinstance(result["success"], bool):
            return False
        
        # Validate parse time
        if result["parse_time"] is not None and result["parse_time"] < 0:
            return False
        
        return True
    
    def _update_candidate_profile(self, user_id: str, parse_result: Dict[str, Any]):
        """
        Update candidate profile with parsed information.
        
        Args:
            user_id: User ID
            parse_result: Parse result
        """
        try:
            worker_logger.info(f"Updating candidate profile for user: {user_id}")
            
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
            
            # Extract education
            education = []
            if parse_result.get('education'):
                for edu in parse_result['education']:
                    education.append({
                        'institution': edu.get('institution'),
                        'degree': edu.get('degree'),
                        'field_of_study': edu.get('field_of_study'),
                        'start_date': edu.get('start_date'),
                        'end_date': edu.get('end_date')
                    })
            
            # Update candidate profile in database
            # This would typically call a candidate service
            worker_logger.info(f"Profile update data prepared for user: {user_id}")
            
        except Exception as e:
            worker_logger.error(f"Failed to update candidate profile for user {user_id}: {str(e)}")
            # Don't fail the pipeline if profile update fails
            pass
    
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
    
    def process_retry_request(self, qid: str) -> bool:
        """
        Process retry request for failed parsing.
        
        Args:
            qid: File QID to retry
            
        Returns:
            bool: True if retry completed successfully
        """
        try:
            worker_logger.info(f"Processing parsing retry request for QID: {qid}")
            
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
            
            # Process parsing request
            return self.process_parsing_request(qid)
            
        except Exception as e:
            worker_logger.error(f"Parsing retry failed for QID {qid}: {str(e)}")
            return False
    
    def get_worker_status(self) -> Dict[str, Any]:
        """
        Get worker status.
        
        Returns:
            Dict: Worker status information
        """
        try:
            # Get pending parsing requests
            pending_parsing = self.repository.get_records_by_status("parsing")
            queued_parsing = self.repository.get_records_by_status("queued")
            
            return {
                "worker_id": "parsing_worker",
                "status": "active",
                "pending_parsing": len(pending_parsing),
                "queued_parsing": len(queued_parsing),
                "max_retries": self.max_retries,
                "retry_delay": self.retry_delay,
                "timeout": self.timeout
            }
            
        except Exception as e:
            logger.error(f"Failed to get worker status: {str(e)}")
            return {
                "worker_id": "parsing_worker",
                "status": "error",
                "error": str(e)
            }


def create_worker(config=None) -> ParsingWorker:
    """Create parsing worker instance."""
    return ParsingWorker(config)


def main():
    """Main worker entry point."""
    try:
        # Create worker
        worker = create_worker()
        
        # Subscribe to parsing requests
        event_publisher = get_event_publisher()
        
        def handle_parsing_request(event):
            """Handle parsing request event."""
            qid = event.qid
            worker_logger.info(f"Received parsing request for QID: {qid}")
            worker.process_parsing_request(qid)
        
        def handle_retry_request(event):
            """Handle retry request event."""
            qid = event.qid
            worker_logger.info(f"Received parsing retry request for QID: {qid}")
            worker.process_retry_request(qid)
        
        # Subscribe to events
        event_publisher.subscribe_to_event(EventType.PARSE_REQUESTED, handle_parsing_request)
        event_publisher.subscribe_to_event(EventType.RETRY_REQUESTED, handle_retry_request)
        
        # Start processing events
        worker_logger.info("Parsing worker started")
        event_publisher.process_events(EventType.PARSE_REQUESTED)
        
    except KeyboardInterrupt:
        logger.info("Parsing worker stopped by user")
    except Exception as e:
        logger.error(f"Parsing worker failed: {str(e)}")
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    main()