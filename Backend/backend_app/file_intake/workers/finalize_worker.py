"""
Finalize Worker - Handles final processing steps and cleanup.

This worker provides:
- Final status updates
- Cleanup operations
- Notification sending
- Reporting
- Archive management
- Retry mechanisms
- Logging and monitoring
"""

import logging
import time
import traceback
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from ..config.intake_config import get_config
from ..utils.logging_utils import get_logger, get_worker_logger

from ..services.event_publisher import get_event_publisher, EventType
from ..repositories.intake_repository import get_intake_repository
from ..services.profile_writer import ProfileWriter
from ..services.session_service import SessionService

logger = get_logger(__name__)
worker_logger = get_worker_logger(__name__)


class FinalizeWorker:
    """Finalize worker for handling final processing steps."""
    
    def __init__(self, config=None):
        """
        Initialize finalize worker.
        
        Args:
            config: Configuration object
        """
        self.config = config or get_config()
        self.event_publisher = get_event_publisher(self.config)
        self.repository = get_intake_repository(self.config)
        
        # Worker configuration
        self.max_retries = self.config.worker.max_retries
        self.retry_delay = self.config.worker.retry_delay
        self.timeout = self.config.worker.timeout
        
        # Archive configuration
        self.archive_enabled = self.config.storage.archive_enabled
        self.archive_retention_days = self.config.storage.archive_retention_days
        
        logger.info("Finalize worker initialized")
    
    def process_finalize_request(self, qid: str) -> bool:
        """
        Process finalize request.
        
        Args:
            qid: File QID to finalize
            
        Returns:
            bool: True if finalize completed successfully
        """
        try:
            worker_logger.info(f"Processing finalize request for QID: {qid}")
            
            # Get record
            record = self.repository.get_record(qid)
            if not record:
                worker_logger.error(f"Record not found for QID: {qid}")
                return False
            
            # Check if record is in completed state
            if record.status != "completed":
                worker_logger.warning(f"Record is not in completed state: {record.status}")
                return False
            
            # Perform finalization steps
            success = True
            
            # 1. Archive file if enabled
            if self.archive_enabled:
                if not self._archive_file(qid):
                    worker_logger.warning(f"Failed to archive file for QID: {qid}")
                    success = False
            
            # 2. Create candidate profile
            profile_created = self._create_candidate_profile(qid)
            if not profile_created:
                worker_logger.warning(f"Failed to create candidate profile for QID: {qid}")
                success = False
            
            # 3. Send notifications
            if not self._send_notifications(qid):
                worker_logger.warning(f"Failed to send notifications for QID: {qid}")
                success = False
            
            # 4. Update final status
            if success:
                self.repository.update_status(qid, "archived")
                worker_logger.info(f"Finalization completed successfully for QID: {qid}")
            else:
                self.repository.update_status(qid, "finalize_failed")
                worker_logger.warning(f"Finalization partially completed for QID: {qid}")
            
            # 5. Generate processing report
            report = self._generate_processing_report(qid)
            self.repository.save_processing_report(qid, report)
            
            # 6. Publish finalize completed event
            self.event_publisher.publish_processing_completed(qid, {
                "timestamp": datetime.utcnow().isoformat(),
                "final_status": "archived" if success else "finalize_failed",
                "processing_report": report,
                "profile_created": profile_created
            })
            
            return success
            
        except Exception as e:
            worker_logger.error(f"Finalization failed for QID {qid}: {str(e)}")
            worker_logger.error(traceback.format_exc())
            
            # Update status to failed
            self.repository.update_status(qid, "finalize_failed")
            self.repository.set_error(qid, f"Finalization failed: {str(e)}")
            
            return False
    
    def _create_candidate_profile(self, qid: str) -> bool:
        """
        Create candidate profile from parsed data.
        
        Args:
            qid: File QID to create profile for
            
        Returns:
            bool: True if profile created successfully
        """
        try:
            worker_logger.info(f"Creating candidate profile for QID: {qid}")
            
            # Get parsed result
            parsed_result = self.repository.get_parsed_output(qid)
            if not parsed_result:
                worker_logger.warning(f"No parsed result found for QID: {qid}")
                return False
            
            # Get record for user ID and source
            record = self.repository.get_record(qid)
            if not record:
                worker_logger.error(f"Record not found for QID: {qid}")
                return False
            
            # Create session service for database access
            session_service = SessionService()
            
            # Create profile writer
            profile_writer = ProfileWriter(session_service.db)
            
            # Create profile from parsed data
            profile = profile_writer.create_profile_from_parsed_data(
                parsed_data=parsed_result,
                user_id=record.user_id,
                source=record.source or "manual"
            )
            
            # Update record with profile ID
            self.repository.update_profile_id(qid, profile.id)
            
            worker_logger.info(f"Successfully created candidate profile for QID: {qid} (Profile ID: {profile.id})")
            return True
            
        except Exception as e:
            worker_logger.error(f"Failed to create candidate profile for QID {qid}: {str(e)}")
            return False
    
    def _archive_file(self, qid: str) -> bool:
        """
        Archive file after processing.
        
        Args:
            qid: File QID to archive
            
        Returns:
            bool: True if archived successfully
        """
        try:
            worker_logger.info(f"Archiving file for QID: {qid}")
            
            # Get record
            record = self.repository.get_record(qid)
            if not record:
                raise ValueError(f"Record not found for QID: {qid}")
            
            # Archive file (this would typically move the file to archive storage)
            # For now, we'll just update the record with archive information
            archive_metadata = {
                "archived_at": datetime.utcnow().isoformat(),
                "archive_path": f"archive/{qid}_{record.original_filename}",
                "retention_days": self.archive_retention_days
            }
            
            self.repository.update_archive_metadata(qid, archive_metadata)
            
            worker_logger.info(f"File archived successfully for QID: {qid}")
            return True
            
        except Exception as e:
            worker_logger.error(f"Failed to archive file for QID {qid}: {str(e)}")
            return False
    
    def _send_notifications(self, qid: str) -> bool:
        """
        Send notifications for completed processing.
        
        Args:
            qid: File QID to send notifications for
            
        Returns:
            bool: True if notifications sent successfully
        """
        try:
            worker_logger.info(f"Sending notifications for QID: {qid}")
            
            # Get record
            record = self.repository.get_record(qid)
            if not record:
                raise ValueError(f"Record not found for QID: {qid}")
            
            # Get parsed result
            parsed_result = self.repository.get_parsed_output(qid)
            
            # Prepare notification data
            notification_data = {
                "qid": qid,
                "filename": record.original_filename,
                "source": record.source,
                "user_id": record.user_id,
                "processed_at": datetime.utcnow().isoformat(),
                "confidence_score": parsed_result.get("confidence_score", 0) if parsed_result else 0,
                "contact_info": parsed_result.get("contact", {}) if parsed_result else {},
                "skills_count": len(parsed_result.get("skills", [])) if parsed_result else 0,
                "experience_count": len(parsed_result.get("experience", [])) if parsed_result else 0,
                "education_count": len(parsed_result.get("education", [])) if parsed_result else 0
            }
            
            # Send notification to user (if user exists)
            if record.user_id:
                self._send_user_notification(record.user_id, notification_data)
            
            # Send notification to system administrators
            self._send_admin_notification(notification_data)
            
            worker_logger.info(f"Notifications sent successfully for QID: {qid}")
            return True
            
        except Exception as e:
            worker_logger.error(f"Failed to send notifications for QID {qid}: {str(e)}")
            return False
    
    def _send_user_notification(self, user_id: str, notification_data: Dict[str, Any]):
        """
        Send notification to user.
        
        Args:
            user_id: User ID
            notification_data: Notification data
        """
        try:
            # This would typically send an email, SMS, or push notification
            # For now, we'll just log it
            worker_logger.info(f"Sending notification to user {user_id}: {notification_data}")
            
        except Exception as e:
            worker_logger.error(f"Failed to send user notification: {str(e)}")
    
    def _send_admin_notification(self, notification_data: Dict[str, Any]):
        """
        Send notification to system administrators.
        
        Args:
            notification_data: Notification data
        """
        try:
            # This would typically send an email or Slack notification
            # For now, we'll just log it
            worker_logger.info(f"Sending admin notification: {notification_data}")
            
        except Exception as e:
            worker_logger.error(f"Failed to send admin notification: {str(e)}")
    
    def _generate_processing_report(self, qid: str) -> Dict[str, Any]:
        """
        Generate processing report.
        
        Args:
            qid: File QID to generate report for
            
        Returns:
            Dict: Processing report
        """
        try:
            # Get record
            record = self.repository.get_record(qid)
            if not record:
                raise ValueError(f"Record not found for QID: {qid}")
            
            # Get processing history
            history = self.repository.get_processing_history(qid)
            
            # Get parsed result
            parsed_result = self.repository.get_parsed_output(qid)
            
            # Calculate processing time
            processing_time = self._calculate_processing_time(qid)
            
            # Generate report
            report = {
                "qid": qid,
                "filename": record.original_filename,
                "source": record.source,
                "user_id": record.user_id,
                "status": record.status,
                "created_at": record.created_at.isoformat(),
                "updated_at": record.updated_at.isoformat(),
                "processing_time": processing_time,
                "file_size": record.filesize,
                "mime_type": record.mime_type,
                "processing_history": history,
                "parsed_result": parsed_result,
                "archive_metadata": record.archive_metadata,
                "extraction_metadata": record.extraction_metadata,
                "parsing_metadata": record.parsing_metadata,
                "error_message": record.error_message
            }
            
            worker_logger.info(f"Processing report generated for QID: {qid}")
            return report
            
        except Exception as e:
            worker_logger.error(f"Failed to generate processing report for QID {qid}: {str(e)}")
            return {
                "qid": qid,
                "error": str(e),
                "generated_at": datetime.utcnow().isoformat()
            }
    
    def _calculate_processing_time(self, qid: str) -> float:
        """
        Calculate total processing time.
        
        Args:
            qid: File QID
            
        Returns:
            float: Processing time in seconds
        """
        record = self.repository.get_record(qid)
        if not record:
            return 0.0
        
        created_time = record.created_at
        updated_time = record.updated_at
        
        if updated_time:
            return (updated_time - created_time).total_seconds()
        else:
            return 0.0
    
    def cleanup_old_archives(self) -> int:
        """
        Clean up old archives based on retention policy.
        
        Returns:
            int: Number of archives cleaned up
        """
        try:
            worker_logger.info("Starting archive cleanup")
            
            # Calculate cutoff date
            cutoff_date = datetime.utcnow() - timedelta(days=self.archive_retention_days)
            
            # Get old archives
            old_archives = self.repository.get_old_archives(cutoff_date)
            
            cleaned_count = 0
            
            for archive in old_archives:
                try:
                    # Delete archive file
                    self._delete_archive_file(archive)
                    
                    # Update record
                    self.repository.update_status(archive.qid, "deleted")
                    
                    cleaned_count += 1
                    
                except Exception as e:
                    worker_logger.error(f"Failed to clean up archive {archive.qid}: {str(e)}")
            
            worker_logger.info(f"Archive cleanup completed. Cleaned {cleaned_count} archives.")
            return cleaned_count
            
        except Exception as e:
            worker_logger.error(f"Archive cleanup failed: {str(e)}")
            return 0
    
    def _delete_archive_file(self, archive):
        """
        Delete archive file.
        
        Args:
            archive: Archive record
        """
        try:
            # This would typically delete the file from storage
            # For now, we'll just log it
            worker_logger.info(f"Deleting archive file: {archive.qid}")
            
        except Exception as e:
            worker_logger.error(f"Failed to delete archive file {archive.qid}: {str(e)}")
            raise
    
    def get_worker_status(self) -> Dict[str, Any]:
        """
        Get worker status.
        
        Returns:
            Dict: Worker status information
        """
        try:
            # Get pending finalize requests
            pending_finalize = self.repository.get_records_by_status("completed")
            archived_count = self.repository.get_records_by_status("archived")
            
            return {
                "worker_id": "finalize_worker",
                "status": "active",
                "pending_finalize": len(pending_finalize),
                "archived_count": len(archived_count),
                "archive_enabled": self.archive_enabled,
                "archive_retention_days": self.archive_retention_days,
                "max_retries": self.max_retries,
                "retry_delay": self.retry_delay,
                "timeout": self.timeout
            }
            
        except Exception as e:
            logger.error(f"Failed to get worker status: {str(e)}")
            return {
                "worker_id": "finalize_worker",
                "status": "error",
                "error": str(e)
            }


def create_worker(config=None) -> FinalizeWorker:
    """Create finalize worker instance."""
    return FinalizeWorker(config)


def main():
    """Main worker entry point."""
    try:
        # Create worker
        worker = create_worker()
        
        # Subscribe to finalize requests
        event_publisher = get_event_publisher()
        
        def handle_finalize_request(event):
            """Handle finalize request event."""
            qid = event.qid
            worker_logger.info(f"Received finalize request for QID: {qid}")
            worker.process_finalize_request(qid)
        
        # Subscribe to events
        event_publisher.subscribe_to_event(EventType.PROCESSING_COMPLETED, handle_finalize_request)
        
        # Start processing events
        worker_logger.info("Finalize worker started")
        event_publisher.process_events(EventType.PROCESSING_COMPLETED)
        
    except KeyboardInterrupt:
        logger.info("Finalize worker stopped by user")
    except Exception as e:
        logger.error(f"Finalize worker failed: {str(e)}")
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    main()