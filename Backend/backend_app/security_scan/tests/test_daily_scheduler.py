"""
Test for daily scheduler functionality.

Testing Parameters:
- Test: Daily scheduler
- Expected Behavior: Runs exactly at 00:00
"""

import pytest
import tempfile
import os
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from ...security_scan.cron_scheduler import APSchedulerManager
from ...security_scan.virus_update_manager import ClamAVUpdateManager
from ...security_scan.quarantine_manager import FileQuarantineManager
from ...security_scan.config import SecurityScanConfig


class TestDailyScheduler:
    """Test suite for daily scheduler operations."""
    
    def setup_method(self):
        """Setup test environment."""
        # Create temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        
        # Setup virus database paths
        self.db_path = os.path.join(self.temp_dir, "virus_db")
        self.backup_path = os.path.join(self.temp_dir, "virus_db_backup")
        
        # Create test database files
        os.makedirs(self.db_path, exist_ok=True)
        os.makedirs(self.backup_path, exist_ok=True)
        
        with open(os.path.join(self.db_path, "main.cvd"), 'w') as f:
            f.write("Sample virus database content")
        
        with open(os.path.join(self.backup_path, "main.cvd"), 'w') as f:
            f.write("Backup virus database content")
        
        # Create managers
        self.update_manager = ClamAVUpdateManager(
            db_path=self.db_path,
            backup_path=self.backup_path
        )
        self.update_manager.logger = Mock()
        
        self.quarantine_manager = FileQuarantineManager(self.temp_dir)
        
        self.config = SecurityScanConfig()
    
    def teardown_method(self):
        """Clean up test environment."""
        # Remove temporary directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_scheduler_initialization(self):
        """Test scheduler initialization."""
        scheduler = APSchedulerManager(
            virus_update_manager=self.update_manager,
            quarantine_manager=self.quarantine_manager
        )
        
        assert scheduler.virus_update_manager == self.update_manager
        assert scheduler.quarantine_manager == self.quarantine_manager
        assert scheduler.scheduler is not None
        assert scheduler.scheduler.running is False
    
    def test_schedule_midnight_db_check(self):
        """Test scheduling midnight database check."""
        scheduler = APSchedulerManager(
            virus_update_manager=self.update_manager,
            quarantine_manager=self.quarantine_manager
        )
        
        # Schedule the job
        scheduler.schedule_midnight_db_check()
        
        # Verify job was added
        jobs = scheduler.get_jobs()
        assert len(jobs) == 1
        
        job = jobs[0]
        assert job.id == 'daily_db_maintenance'
        assert job.name == 'Daily Virus Database Maintenance'
    
    def test_start_scheduler(self):
        """Test starting the scheduler."""
        scheduler = APSchedulerManager(
            virus_update_manager=self.update_manager,
            quarantine_manager=self.quarantine_manager
        )
        
        # Start scheduler
        scheduler.start()
        
        # Verify scheduler is running
        assert scheduler.scheduler.running is True
        
        # Stop scheduler
        scheduler.stop()
        assert scheduler.scheduler.running is False
    
    def test_stop_scheduler(self):
        """Test stopping the scheduler."""
        scheduler = APSchedulerManager(
            virus_update_manager=self.update_manager,
            quarantine_manager=self.quarantine_manager
        )
        
        # Start and then stop scheduler
        scheduler.start()
        assert scheduler.scheduler.running is True
        
        scheduler.stop()
        assert scheduler.scheduler.running is False
    
    def test_get_scheduler_status(self):
        """Test getting scheduler status."""
        scheduler = APSchedulerManager(
            virus_update_manager=self.update_manager,
            quarantine_manager=self.quarantine_manager
        )
        
        # Add a job
        scheduler.schedule_midnight_db_check()
        
        # Get status
        jobs = scheduler.get_jobs()
        
        assert len(jobs) == 1
        assert jobs[0].id == 'daily_db_maintenance'
    
    def test_run_daily_db_maintenance_success(self):
        """Test successful daily database maintenance."""
        scheduler = APSchedulerManager(
            virus_update_manager=self.update_manager,
            quarantine_manager=self.quarantine_manager
        )
        
        # Mock successful validation
        with patch.object(self.update_manager, 'validate_virus_db') as mock_validate:
            mock_validate.return_value.checksum_valid = True
            
            with patch.object(self.update_manager, 'backup_db') as mock_backup:
                mock_backup.return_value = True
                
                with patch.object(self.update_manager, 'reload_clamav_engine') as mock_reload:
                    mock_reload.return_value = True
                    
                    # Run maintenance
                    scheduler.run_daily_db_maintenance()
                    
                    # Verify methods were called
                    mock_validate.assert_called_once()
                    mock_backup.assert_called_once()
                    mock_reload.assert_called_once()
    
    def test_run_daily_db_maintenance_corrupted_db_restore(self):
        """Test daily maintenance with corrupted database restore."""
        scheduler = APSchedulerManager(
            virus_update_manager=self.update_manager,
            quarantine_manager=self.quarantine_manager
        )
        
        # Mock corrupted database
        with patch.object(self.update_manager, 'validate_virus_db') as mock_validate:
            mock_validate.return_value.checksum_valid = False
            
            with patch.object(self.update_manager, 'restore_backup_db') as mock_restore:
                mock_restore.return_value = True
                
                with patch.object(self.update_manager, 'reload_clamav_engine') as mock_reload:
                    mock_reload.return_value = True
                    
                    # Run maintenance
                    scheduler.run_daily_db_maintenance()
                    
                    # Verify restore and reload were called
                    mock_validate.assert_called_once()
                    mock_restore.assert_called_once()
                    mock_reload.assert_called_once()
    
    def test_run_daily_db_maintenance_restore_failure(self):
        """Test daily maintenance when restore fails."""
        scheduler = APSchedulerManager(
            virus_update_manager=self.update_manager,
            quarantine_manager=self.quarantine_manager
        )
        
        # Mock corrupted database and failed restore
        with patch.object(self.update_manager, 'validate_virus_db') as mock_validate:
            mock_validate.return_value.checksum_valid = False
            
            with patch.object(self.update_manager, 'restore_backup_db') as mock_restore:
                mock_restore.return_value = False
                
                # Run maintenance
                scheduler.run_daily_db_maintenance()
                
                # Verify restore was attempted but failed
                mock_validate.assert_called_once()
                mock_restore.assert_called_once()
    
    def test_run_daily_db_maintenance_logging(self):
        """Test that daily maintenance logs properly."""
        scheduler = APSchedulerManager(
            virus_update_manager=self.update_manager,
            quarantine_manager=self.quarantine_manager
        )
        
        # Mock successful validation
        with patch.object(self.update_manager, 'validate_virus_db') as mock_validate:
            mock_validate.return_value.checksum_valid = True
            
            with patch.object(self.update_manager, 'backup_db') as mock_backup:
                mock_backup.return_value = True
                
                with patch.object(self.update_manager, 'reload_clamav_engine') as mock_reload:
                    mock_reload.return_value = True
                    
                    # Run maintenance
                    scheduler.run_daily_db_maintenance()
                    
                    # Verify logging calls
                    assert self.update_manager.logger.info.call_count >= 3  # Start, backup, reload success
                    assert self.update_manager.logger.error.call_count == 0  # No errors
    
    def test_log_to_update_file(self):
        """Test logging to update.log file."""
        scheduler = APSchedulerManager(
            virus_update_manager=self.update_manager,
            quarantine_manager=self.quarantine_manager
        )
        
        # Create mock database status
        from ...security_scan.io_contract import VirusUpdateStatus
        db_status = VirusUpdateStatus(
            last_update=datetime.utcnow(),
            checksum_valid=True,
            db_version="2025-12-06.1"
        )
        
        # Log to file
        scheduler._log_to_update_file(db_status)
        
        # Verify log file was created
        log_file = os.path.join(self.temp_dir, "logs", "update.log")
        assert os.path.exists(log_file)
        
        # Verify log content
        with open(log_file, 'r') as f:
            content = f.read()
            assert "Daily Maintenance" in content
            assert "Checksum Valid: True" in content
            assert "Version: 2025-12-06.1" in content
    
    def test_add_custom_job(self):
        """Test adding custom jobs to scheduler."""
        scheduler = APSchedulerManager(
            virus_update_manager=self.update_manager,
            quarantine_manager=self.quarantine_manager
        )
        
        # Create a simple function to schedule
        def test_function():
            pass
        
        # Add custom job
        scheduler.add_custom_job(
            func=test_function,
            trigger='interval',
            seconds=60,
            id='test_job'
        )
        
        # Verify job was added
        jobs = scheduler.get_jobs()
        assert len(jobs) == 1
        assert jobs[0].id == 'test_job'
    
    def test_scheduler_error_handling(self):
        """Test scheduler error handling during maintenance."""
        scheduler = APSchedulerManager(
            virus_update_manager=self.update_manager,
            quarantine_manager=self.quarantine_manager
        )
        
        # Mock exception during validation
        with patch.object(self.update_manager, 'validate_virus_db', 
                         side_effect=Exception("Validation error")):
            
            # Run maintenance
            scheduler.run_daily_db_maintenance()
            
            # Verify error was logged
            self.update_manager.logger.error.assert_called_once()
    
    def test_concurrent_scheduler_operations(self):
        """Test concurrent scheduler operations."""
        scheduler = APSchedulerManager(
            virus_update_manager=self.update_manager,
            quarantine_manager=self.quarantine_manager
        )
        
        # Start scheduler
        scheduler.start()
        scheduler.schedule_midnight_db_check()
        
        # Simulate multiple concurrent maintenance runs
        def run_maintenance():
            scheduler.run_daily_db_maintenance()
        
        # Run multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=run_maintenance)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Stop scheduler
        scheduler.stop()
        
        # Verify scheduler is still in valid state
        assert scheduler.scheduler is not None
    
    def test_scheduler_persistence(self):
        """Test scheduler job persistence."""
        scheduler1 = APSchedulerManager(
            virus_update_manager=self.update_manager,
            quarantine_manager=self.quarantine_manager
        )
        
        # Add job
        scheduler1.schedule_midnight_db_check()
        jobs1 = scheduler1.get_jobs()
        assert len(jobs1) == 1
        
        # Create new scheduler instance
        scheduler2 = APSchedulerManager(
            virus_update_manager=self.update_manager,
            quarantine_manager=self.quarantine_manager
        )
        
        # Jobs should not persist between instances (by default)
        jobs2 = scheduler2.get_jobs()
        assert len(jobs2) == 0
        
        # But we can add the same job again
        scheduler2.schedule_midnight_db_check()
        jobs2 = scheduler2.get_jobs()
        assert len(jobs2) == 1
    
    def test_scheduler_shutdown_graceful(self):
        """Test graceful scheduler shutdown."""
        scheduler = APSchedulerManager(
            virus_update_manager=self.update_manager,
            quarantine_manager=self.quarantine_manager
        )
        
        # Start scheduler and add job
        scheduler.start()
        scheduler.schedule_midnight_db_check()
        
        assert scheduler.scheduler.running is True
        
        # Stop scheduler
        scheduler.stop()
        
        # Verify clean shutdown
        assert scheduler.scheduler.running is False
        
        # Should be able to start again
        scheduler.start()
        assert scheduler.scheduler.running is True
        
        scheduler.stop()
    
    def test_scheduler_with_real_cron_trigger(self):
        """Test scheduler with real cron trigger (simulated)."""
        scheduler = APSchedulerManager(
            virus_update_manager=self.update_manager,
            quarantine_manager=self.quarantine_manager
        )
        
        # This test verifies that the cron trigger is set up correctly
        # In a real scenario, this would run at 00:00 daily
        scheduler.schedule_midnight_db_check()
        
        jobs = scheduler.get_jobs()
        assert len(jobs) == 1
        
        job = jobs[0]
        # Verify the job has the correct trigger
        assert job.trigger is not None
        # The trigger should be a CronTrigger for daily at midnight
        from apscheduler.triggers.cron import CronTrigger
        assert isinstance(job.trigger, CronTrigger)
        
        # Verify the cron expression
        assert job.trigger.hour == 0
        assert job.trigger.minute == 0