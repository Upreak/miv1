"""
Virus Scan Worker - Handles virus scanning for uploaded files.

This worker provides:
- Asynchronous virus scanning
- Multiple engine support (ClamAV, VirusTotal, etc.)
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

from ..services.virus_scan_service import get_virus_scan_service
from ..services.event_publisher import get_event_publisher, EventType
from ..repositories.intake_repository import get_intake_repository

logger = get_logger(__name__)
worker_logger = get_worker_logger(__name__)


class VirusScanWorker:
    """Virus scan worker for processing virus scan requests."""
    
    def __init__(self, config=None):
        """
        Initialize virus scan worker.
        
        Args:
            config: Configuration object
        """
        self.config = config or get_config()
        self.virus_scan_service = get_virus_scan_service(self.config)
        self.event_publisher = get_event_publisher(self.config)
        self.repository = get_intake_repository(self.config)
        
        # Worker configuration
        self.max_retries = self.config.worker.max_retries
        self.retry_delay = self.config.worker.retry_delay
        self.timeout = self.config.worker.timeout
        
        logger.info("Virus scan worker initialized")
    
    def process_scan_request(self, qid: str) -> bool:
        """
        Process virus scan request.
        
        Args:
            qid: File QID to scan
            
        Returns:
            bool: True if scan completed successfully
        """
        try:
            worker_logger.info(f"Processing virus scan request for QID: {qid}")
            
            # Get record
            record = self.repository.get_record(qid)
            if not record:
                worker_logger.error(f"Record not found for QID: {qid}")
                return False
            
            # Update status to scanning
            self.repository.update_status(qid, "scanning")
            
            # Perform virus scan
            scan_results = self._perform_virus_scan(qid)
            
            # Check results
            infected_engines = []
            clean_engines = []
            
            for engine_name, result in scan_results.items():
                if result.result == "infected":
                    infected_engines.append({
                        "engine": engine_name,
                        "virus_name": result.virus_name,
                        "scan_time": result.scan_time
                    })
                    worker_logger.warning(f"Virus detected by {engine_name}: {result.virus_name}")
                else:
                    clean_engines.append({
                        "engine": engine_name,
                        "scan_time": result.scan_time
                    })
            
            # Determine overall result
            if infected_engines:
                # File is infected
                self.repository.mark_infected(qid, infected_engines[0]["virus_name"])
                self.repository.update_status(qid, "infected")
                
                # Publish scan completed event
                self.event_publisher.publish_virus_scan_completed(qid, {
                    "result": "infected",
                    "infected_engines": infected_engines,
                    "clean_engines": clean_engines,
                    "scan_time": sum(r.scan_time or 0 for r in scan_results.values())
                })
                
                worker_logger.info(f"Virus scan completed - INFECTED for QID: {qid}")
                return True
            else:
                # File is clean
                self.repository.update_status(qid, "clean")
                
                # Publish scan completed event
                self.event_publisher.publish_virus_scan_completed(qid, {
                    "result": "clean",
                    "clean_engines": clean_engines,
                    "scan_time": sum(r.scan_time or 0 for r in scan_results.values())
                })
                
                # Request sanitization
                self.event_publisher.publish_sanitize_requested(qid, {
                    "timestamp": datetime.utcnow().isoformat(),
                    "previous_status": "clean"
                })
                
                worker_logger.info(f"Virus scan completed - CLEAN for QID: {qid}")
                return True
                
        except Exception as e:
            worker_logger.error(f"Virus scan failed for QID {qid}: {str(e)}")
            worker_logger.error(traceback.format_exc())
            
            # Update status to failed
            self.repository.update_status(qid, "failed")
            self.repository.set_error(qid, f"Virus scan failed: {str(e)}")
            
            # Publish failed event
            self.event_publisher.publish_processing_failed(qid, {
                "error": str(e),
                "stage": "virus_scan",
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return False
    
    def _perform_virus_scan(self, qid: str) -> Dict[str, Any]:
        """
        Perform virus scan with retry logic.
        
        Args:
            qid: File QID to scan
            
        Returns:
            Dict: Scan results from all engines
        """
        record = self.repository.get_record(qid)
        if not record:
            raise ValueError(f"Record not found for QID: {qid}")
        
        scan_results = {}
        retry_count = 0
        
        while retry_count < self.max_retries:
            try:
                # Perform virus scan
                results = self.virus_scan_service.scan_file(record.storage_path)
                
                # Validate results
                for engine_name, result in results.items():
                    if not self._validate_scan_result(result):
                        raise ValueError(f"Invalid scan result from {engine_name}")
                
                scan_results = results
                break
                
            except Exception as e:
                retry_count += 1
                worker_logger.warning(f"Virus scan attempt {retry_count} failed for QID {qid}: {str(e)}")
                
                if retry_count < self.max_retries:
                    # Wait before retry
                    time.sleep(self.retry_delay)
                else:
                    raise RuntimeError(f"Virus scan failed after {self.max_retries} attempts: {str(e)}")
        
        return scan_results
    
    def _validate_scan_result(self, result: Dict[str, Any]) -> bool:
        """
        Validate virus scan result.
        
        Args:
            result: Scan result to validate
            
        Returns:
            bool: True if result is valid
        """
        required_fields = ["result", "scan_time"]
        
        for field in required_fields:
            if field not in result:
                return False
        
        # Validate result value
        if result["result"] not in ["clean", "infected", "error"]:
            return False
        
        # Validate scan time
        if result["scan_time"] is not None and result["scan_time"] < 0:
            return False
        
        return True
    
    def process_retry_request(self, qid: str) -> bool:
        """
        Process retry request for failed virus scan.
        
        Args:
            qid: File QID to retry
            
        Returns:
            bool: True if retry completed successfully
        """
        try:
            worker_logger.info(f"Processing virus scan retry request for QID: {qid}")
            
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
            
            # Process scan request
            return self.process_scan_request(qid)
            
        except Exception as e:
            worker_logger.error(f"Virus scan retry failed for QID {qid}: {str(e)}")
            return False
    
    def get_worker_status(self) -> Dict[str, Any]:
        """
        Get worker status.
        
        Returns:
            Dict: Worker status information
        """
        try:
            # Get pending scan requests
            pending_scans = self.repository.get_records_by_status("scanning")
            queued_scans = self.repository.get_records_by_status("queued")
            
            return {
                "worker_id": "virus_scan_worker",
                "status": "active",
                "pending_scans": len(pending_scans),
                "queued_scans": len(queued_scans),
                "max_retries": self.max_retries,
                "retry_delay": self.retry_delay,
                "timeout": self.timeout
            }
            
        except Exception as e:
            logger.error(f"Failed to get worker status: {str(e)}")
            return {
                "worker_id": "virus_scan_worker",
                "status": "error",
                "error": str(e)
            }


def create_worker(config=None) -> VirusScanWorker:
    """Create virus scan worker instance."""
    return VirusScanWorker(config)


def main():
    """Main worker entry point."""
    try:
        # Create worker
        worker = create_worker()
        
        # Subscribe to virus scan requests
        event_publisher = get_event_publisher()
        
        def handle_scan_request(event):
            """Handle virus scan request event."""
            qid = event.qid
            worker_logger.info(f"Received virus scan request for QID: {qid}")
            worker.process_scan_request(qid)
        
        def handle_retry_request(event):
            """Handle retry request event."""
            qid = event.qid
            worker_logger.info(f"Received virus scan retry request for QID: {qid}")
            worker.process_retry_request(qid)
        
        # Subscribe to events
        event_publisher.subscribe_to_event(EventType.VIRUS_SCAN_REQUESTED, handle_scan_request)
        event_publisher.subscribe_to_event(EventType.RETRY_REQUESTED, handle_retry_request)
        
        # Start processing events
        worker_logger.info("Virus scan worker started")
        event_publisher.process_events(EventType.VIRUS_SCAN_REQUESTED)
        
    except KeyboardInterrupt:
        logger.info("Virus scan worker stopped by user")
    except Exception as e:
        logger.error(f"Virus scan worker failed: {str(e)}")
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    main()