"""
Security Scan Module - Cron Scheduler

Interface definitions for scheduled virus database maintenance.
"""

from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger


class CronScheduler(ABC):
    """Abstract base class for cron-based scheduling."""
    
    @abstractmethod
    def schedule_midnight_db_check(self) -> None:
        """
        Schedule daily virus database check at midnight.
        Trigger time: "0 0 * * *"
        """
        pass
    
    @abstractmethod
    def run_daily_db_maintenance(self) -> None:
        """
        Execute daily virus database maintenance tasks.
        This includes:
        - Validate DB
        - Reload engine if changed
        - Backup if valid
        - Log to /data/quarantine/logs/update.log
        """
        pass
    
    @abstractmethod
    def start(self) -> None:
        """
        Start the scheduler.
        """
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """
        Stop the scheduler.
        """
        pass


class APSchedulerManager(CronScheduler):
    """Concrete implementation using APScheduler."""
    
    def __init__(
        self,
        virus_update_manager: 'VirusUpdateManager',
        quarantine_manager: Optional['QuarantineManager'] = None
    ):
        """
        Initialize scheduler with virus update manager.
        
        Args:
            virus_update_manager: Manager for virus database operations
            quarantine_manager: Optional manager for quarantine operations
        """
        self.virus_update_manager = virus_update_manager
        self.quarantine_manager = quarantine_manager
        self.scheduler = BackgroundScheduler()
        self.logger = logging.getLogger(__name__)
    
    def schedule_midnight_db_check(self) -> None:
        """
        Schedule daily virus database check at midnight.
        Trigger time: "0 0 * * *"
        """
        # Schedule the daily maintenance task
        trigger = CronTrigger(hour=0, minute=0)  # 00:00 daily
        
        self.scheduler.add_job(
            func=self.run_daily_db_maintenance,
            trigger=trigger,
            id='daily_db_maintenance',
            name='Daily Virus Database Maintenance',
            replace_existing=True
        )
        
        if self.logger:
            self.logger.info("Scheduled daily virus database check at 00:00")
    
    def run_daily_db_maintenance(self) -> None:
        """
        Execute daily virus database maintenance tasks.
        This includes:
        - Validate DB
        - Reload engine if changed
        - Backup if valid
        - Log to /data/quarantine/logs/update.log
        """
        try:
            if self.logger:
                self.logger.info("Starting daily virus database maintenance")
            
            # 1. Validate virus database
            db_status = self.virus_update_manager.validate_virus_db()
            
            if self.logger:
                self.logger.info(
                    f"Database validation - Last Update: {db_status.last_update}, "
                    f"Checksum Valid: {db_status.checksum_valid}, "
                    f"Version: {db_status.db_version}"
                )
            
            # 2. If checksum is valid, backup the database
            if db_status.checksum_valid:
                backup_success = self.virus_update_manager.backup_db()
                
                if self.logger:
                    if backup_success:
                        self.logger.info("Database backup completed successfully")
                    else:
                        self.logger.error("Database backup failed")
            else:
                # 3. If checksum is invalid, restore from backup
                if self.logger:
                    self.logger.warning("Database checksum invalid, attempting restore from backup")
                
                restore_success = self.virus_update_manager.restore_backup_db()
                
                if restore_success:
                    # Reload engine after restore
                    reload_success = self.virus_update_manager.reload_clamav_engine()
                    
                    if self.logger:
                        if reload_success:
                            self.logger.info("Database restored and engine reloaded successfully")
                        else:
                            self.logger.error("Engine reload failed after restore")
                else:
                    if self.logger:
                        self.logger.error("Database restore from backup failed")
            
            # 4. Reload engine if database was updated or restored
            if db_status.checksum_valid:
                reload_success = self.virus_update_manager.reload_clamav_engine()
                
                if self.logger:
                    if reload_success:
                        self.logger.info("ClamAV engine reloaded successfully")
                    else:
                        self.logger.error("ClamAV engine reload failed")
            
            # 5. Log to update.log
            self._log_to_update_file(db_status)
            
            if self.logger:
                self.logger.info("Daily virus database maintenance completed")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Daily maintenance failed: {str(e)}")
    
    def start(self) -> None:
        """
        Start the scheduler.
        """
        if not self.scheduler.running:
            self.scheduler.start()
            
            if self.logger:
                self.logger.info("APScheduler started")
    
    def stop(self) -> None:
        """
        Stop the scheduler.
        """
        if self.scheduler.running:
            self.scheduler.shutdown(wait=True)
            
            if self.logger:
                self.logger.info("APScheduler stopped")
    
    def _log_to_update_file(self, db_status: 'VirusUpdateStatus') -> None:
        """
        Log maintenance results to update.log file.
        
        Args:
            db_status: Database status information
        """
        try:
            # Get log path from quarantine manager if available
            if self.quarantine_manager:
                log_path = self.quarantine_manager.get_log_path()
            else:
                # Default log path
                import os
                log_path = os.path.join("data", "quarantine", "logs")
                os.makedirs(log_path, exist_ok=True)
            
            log_file = os.path.join(log_path, "update.log")
            
            # Write log entry
            with open(log_file, 'a') as f:
                timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                log_entry = (
                    f"[{timestamp}] Daily Maintenance - "
                    f"Last Update: {db_status.last_update}, "
                    f"Checksum Valid: {db_status.checksum_valid}, "
                    f"Version: {db_status.db_version}\n"
                )
                f.write(log_entry)
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to write update log: {str(e)}")
    
    def add_custom_job(self, func, trigger, **kwargs):
        """
        Add a custom job to the scheduler.
        
        Args:
            func: Function to execute
            trigger: APScheduler trigger
            **kwargs: Additional job arguments
        """
        self.scheduler.add_job(func, trigger, **kwargs)
    
    def get_jobs(self):
        """
        Get all scheduled jobs.
        
        Returns:
            List of scheduled jobs
        """
        return self.scheduler.get_jobs()