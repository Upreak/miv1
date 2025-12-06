"""
Security Scan Module - API Endpoints

FastAPI router for security scan operations.
"""

from typing import Optional
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
import os

from ..security_scan.io_contract import ScanRequest, ScanResult, VirusUpdateStatus, ScanStatus
from ..security_scan.scan_service import ClamAVScanService
from ..security_scan.quarantine_manager import FileQuarantineManager
from ..security_scan.virus_update_manager import ClamAVUpdateManager
from ..security_scan.cron_scheduler import APSchedulerManager
from ..security_scan.config import get_config


# Pydantic models for API
class ScanFileResponse(BaseModel):
    """Response model for file scan endpoint."""
    status: str
    details: dict
    safe_path: Optional[str] = None
    infected_path: Optional[str] = None
    timestamp: str


class VirusDBStatusResponse(BaseModel):
    """Response model for virus DB status endpoint."""
    last_update: str
    checksum_valid: bool
    db_version: str


class ManualRestoreResponse(BaseModel):
    """Response model for manual restore endpoint."""
    success: bool
    message: str


# Router setup
router = APIRouter(
    prefix="/security",
    tags=["Security Scan"],
    responses={404: {"description": "Not found"}}
)

# Setup logging
logger = logging.getLogger(__name__)


def get_scan_service() -> ClamAVScanService:
    """Dependency to get scan service instance."""
    config = get_config()
    scan_service = ClamAVScanService(clamav_socket=config.clamav_socket)
    scan_service.logger = logger
    return scan_service


def get_quarantine_manager() -> FileQuarantineManager:
    """Dependency to get quarantine manager instance."""
    config = get_config()
    quarantine_manager = FileQuarantineManager(config.quarantine_base_path)
    return quarantine_manager


def get_virus_update_manager() -> ClamAVUpdateManager:
    """Dependency to get virus update manager instance."""
    config = get_config()
    update_manager = ClamAVUpdateManager(
        db_path=config.virus_db_path,
        backup_path=config.backup_db_path,
        clamav_socket=config.clamav_socket
    )
    update_manager.logger = logger
    return update_manager


def get_scheduler() -> APSchedulerManager:
    """Dependency to get scheduler instance."""
    update_manager = get_virus_update_manager()
    quarantine_manager = get_quarantine_manager()
    scheduler = APSchedulerManager(update_manager, quarantine_manager)
    return scheduler


@router.post("/scan-file", response_model=ScanFileResponse)
async def scan_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    scan_service: ClamAVScanService = Depends(get_scan_service),
    quarantine_manager: FileQuarantineManager = Depends(get_quarantine_manager)
):
    """
    Scan an uploaded file for viruses.
    
    Workflow:
    1. Accept file upload
    2. Move to incoming folder
    3. Trigger scan
    4. Return ScanResult
    """
    try:
        # Validate file size
        config = get_config()
        content = await file.read()
        
        if len(content) > config.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {config.max_file_size} bytes"
            )
        
        # Validate MIME type
        if file.content_type not in config.allowed_mime_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.content_type}"
            )
        
        # Move to incoming folder
        incoming_path = quarantine_manager.move_to_incoming(content, file.filename)
        
        # Move to scanning folder
        scanning_path = quarantine_manager.move_to_scanning(incoming_path)
        
        # Create scan request
        scan_request = ScanRequest(
            file_id=f"scan_{os.path.basename(scanning_path)}",
            file_path=scanning_path,
            mime_type=file.content_type
        )
        
        # Perform scan
        scan_result = scan_service.scan_file(scan_request)
        
        # Move file based on scan result
        if scan_result.status == ScanStatus.SAFE:
            final_path = quarantine_manager.mark_as_safe(scanning_path)
            response_path = final_path
        elif scan_result.status == ScanStatus.INFECTED:
            final_path = quarantine_manager.mark_as_infected(scanning_path)
            response_path = final_path
        else:
            # ERROR status - keep in scanning folder for investigation
            response_path = scanning_path
        
        # Return scan result
        return ScanFileResponse(
            status=scan_result.status.value,
            details=scan_result.details,
            safe_path=scan_result.safe_path,
            infected_path=scan_result.infected_path,
            timestamp=scan_result.timestamp.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Scan file error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/virus-db-status", response_model=VirusDBStatusResponse)
async def get_virus_db_status(
    update_manager: ClamAVUpdateManager = Depends(get_virus_update_manager)
):
    """
    Get virus database status.
    
    Returns:
        VirusUpdateStatus: Database validation status
    """
    try:
        db_status = update_manager.validate_virus_db()
        
        return VirusDBStatusResponse(
            last_update=db_status.last_update.isoformat(),
            checksum_valid=db_status.checksum_valid,
            db_version=db_status.db_version
        )
        
    except Exception as e:
        logger.error(f"Get virus DB status error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/manual-db-restore", response_model=ManualRestoreResponse)
async def manual_db_restore(
    background_tasks: BackgroundTasks,
    update_manager: ClamAVUpdateManager = Depends(get_virus_update_manager)
):
    """
    Manually restore virus database from backup.
    
    Returns:
        bool: True if restore successful, False otherwise
    """
    try:
        # Perform restore in background
        success = update_manager.restore_backup_db()
        
        if success:
            # Reload engine after successful restore
            reload_success = update_manager.reload_clamav_engine()
            
            if reload_success:
                message = "Database restored and engine reloaded successfully"
            else:
                message = "Database restored but engine reload failed"
                success = False
        else:
            message = "Database restore failed"
        
        return ManualRestoreResponse(
            success=success,
            message=message
        )
        
    except Exception as e:
        logger.error(f"Manual DB restore error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start-scheduler")
async def start_scheduler(
    background_tasks: BackgroundTasks,
    scheduler: APSchedulerManager = Depends(get_scheduler)
):
    """
    Start the daily virus database maintenance scheduler.
    """
    try:
        scheduler.start()
        scheduler.schedule_midnight_db_check()
        
        jobs = scheduler.get_jobs()
        
        return {
            "message": "Scheduler started successfully",
            "scheduled_jobs": len(jobs),
            "jobs": [job.id for job in jobs]
        }
        
    except Exception as e:
        logger.error(f"Start scheduler error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop-scheduler")
async def stop_scheduler(
    scheduler: APSchedulerManager = Depends(get_scheduler)
):
    """
    Stop the daily virus database maintenance scheduler.
    """
    try:
        scheduler.stop()
        
        return {
            "message": "Scheduler stopped successfully"
        }
        
    except Exception as e:
        logger.error(f"Stop scheduler error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scheduler-status")
async def get_scheduler_status(
    scheduler: APSchedulerManager = Depends(get_scheduler)
):
    """
    Get current scheduler status and jobs.
    """
    try:
        jobs = scheduler.get_jobs()
        
        return {
            "running": scheduler.scheduler.running,
            "job_count": len(jobs),
            "jobs": [
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None
                }
                for job in jobs
            ]
        }
        
    except Exception as e:
        logger.error(f"Get scheduler status error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Health check endpoint for the security scan module.
    """
    return {
        "status": "healthy",
        "module": "security_scan",
        "version": "1.0.0"
    }