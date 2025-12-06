"""
Test for virus database validation functionality.

Testing Parameters:
- Test: Virus DB validation
- Expected Behavior: Corrupted DB → Fallback → restore backup
"""

import pytest
import tempfile
import os
import shutil
from unittest.mock import Mock, patch, MagicMock

from ...security_scan.virus_update_manager import ClamAVUpdateManager
from ...security_scan.config import SecurityScanConfig


class TestVirusDBValidation:
    """Test suite for virus database validation operations."""
    
    def setup_method(self):
        """Setup test environment."""
        # Create temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "virus_db")
        self.backup_path = os.path.join(self.temp_dir, "virus_db_backup")
        
        # Create test database files
        os.makedirs(self.db_path, exist_ok=True)
        os.makedirs(self.backup_path, exist_ok=True)
        
        # Create sample database files
        with open(os.path.join(self.db_path, "main.cvd"), 'w') as f:
            f.write("Sample virus database content")
        
        with open(os.path.join(self.backup_path, "main.cvd"), 'w') as f:
            f.write("Backup virus database content")
        
        self.config = SecurityScanConfig()
    
    def teardown_method(self):
        """Clean up test environment."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_validate_virus_db_success(self):
        """Test successful virus database validation."""
        update_manager = ClamAVUpdateManager(
            db_path=self.db_path,
            backup_path=self.backup_path
        )
        update_manager.logger = Mock()
        
        # Mock successful validation
        with patch.object(update_manager, '_validate_db_checksum', return_value=True):
            with patch.object(update_manager, '_get_db_version', return_value="2025-12-06.1"):
                with patch.object(update_manager, '_get_last_update_time') as mock_time:
                    mock_time.return_value = Mock()
                    
                    result = update_manager.validate_virus_db()
                    
                    assert result.checksum_valid is True
                    assert result.db_version == "2025-12-06.1"
                    assert result.last_update is not None
    
    def test_validate_virus_db_missing_files(self):
        """Test virus database validation when files are missing."""
        # Remove database files
        shutil.rmtree(self.db_path)
        
        update_manager = ClamAVUpdateManager(
            db_path=self.db_path,
            backup_path=self.backup_path
        )
        update_manager.logger = Mock()
        
        result = update_manager.validate_virus_db()
        
        assert result.checksum_valid is False
        assert result.db_version == "unknown"
        assert result.last_update.year == 1  # datetime.min
    
    def test_validate_virus_db_corrupted_checksum(self):
        """Test virus database validation with corrupted checksum."""
        update_manager = ClamAVUpdateManager(
            db_path=self.db_path,
            backup_path=self.backup_path
        )
        update_manager.logger = Mock()
        
        # Mock failed checksum validation
        with patch.object(update_manager, '_validate_db_checksum', return_value=False):
            with patch.object(update_manager, '_get_db_version', return_value="2025-12-06.1"):
                with patch.object(update_manager, '_get_last_update_time') as mock_time:
                    mock_time.return_value = Mock()
                    
                    result = update_manager.validate_virus_db()
                    
                    assert result.checksum_valid is False
                    assert result.db_version == "2025-12-06.1"
    
    def test_validate_virus_db_exception_handling(self):
        """Test virus database validation exception handling."""
        update_manager = ClamAVUpdateManager(
            db_path=self.db_path,
            backup_path=self.backup_path
        )
        update_manager.logger = Mock()
        
        # Mock exception during validation
        with patch.object(update_manager, '_validate_db_checksum', 
                         side_effect=Exception("Validation error")):
            result = update_manager.validate_virus_db()
            
            assert result.checksum_valid is False
            assert result.db_version == "error"
            assert result.last_update.year == 1  # datetime.min
            
            # Verify error was logged
            update_manager.logger.error.assert_called_once()
    
    def test_restore_backup_db_success(self):
        """Test successful database restore from backup."""
        update_manager = ClamAVUpdateManager(
            db_path=self.db_path,
            backup_path=self.backup_path
        )
        update_manager.logger = Mock()
        
        # Remove current database to simulate corruption
        shutil.rmtree(self.db_path)
        
        # Restore from backup
        result = update_manager.restore_backup_db()
        
        assert result is True
        assert os.path.exists(self.db_path)
        assert os.path.exists(os.path.join(self.db_path, "main.cvd"))
        
        # Verify success was logged
        update_manager.logger.info.assert_called_with("Virus database restored from backup")
    
    def test_restore_backup_db_no_backup(self):
        """Test database restore when backup doesn't exist."""
        # Remove backup
        shutil.rmtree(self.backup_path)
        
        update_manager = ClamAVUpdateManager(
            db_path=self.db_path,
            backup_path=self.backup_path
        )
        update_manager.logger = Mock()
        
        result = update_manager.restore_backup_db()
        
        assert result is False
        
        # Verify error was logged
        update_manager.logger.error.assert_called_with("Backup database not found")
    
    def test_restore_backup_db_exception(self):
        """Test database restore exception handling."""
        update_manager = ClamAVUpdateManager(
            db_path=self.db_path,
            backup_path=self.backup_path
        )
        update_manager.logger = Mock()
        
        # Mock shutil.copytree to raise exception
        with patch('shutil.copytree', side_effect=Exception("Copy error")):
            result = update_manager.restore_backup_db()
            
            assert result is False
            
            # Verify error was logged
            update_manager.logger.error.assert_called_with("Database restore failed: Copy error")
    
    def test_backup_db_success(self):
        """Test successful database backup."""
        # Remove existing backup
        shutil.rmtree(self.backup_path)
        
        update_manager = ClamAVUpdateManager(
            db_path=self.db_path,
            backup_path=self.backup_path
        )
        update_manager.logger = Mock()
        
        result = update_manager.backup_db()
        
        assert result is True
        assert os.path.exists(self.backup_path)
        assert os.path.exists(os.path.join(self.backup_path, "main.cvd"))
        
        # Verify success was logged
        update_manager.logger.info.assert_called_with("Virus database backup created")
    
    def test_backup_db_no_database(self):
        """Test database backup when database doesn't exist."""
        # Remove database
        shutil.rmtree(self.db_path)
        
        update_manager = ClamAVUpdateManager(
            db_path=self.db_path,
            backup_path=self.backup_path
        )
        update_manager.logger = Mock()
        
        result = update_manager.backup_db()
        
        assert result is False
        
        # Verify error was logged
        update_manager.logger.error.assert_called_with("Database path does not exist")
    
    def test_backup_db_exception(self):
        """Test database backup exception handling."""
        update_manager = ClamAVUpdateManager(
            db_path=self.db_path,
            backup_path=self.backup_path
        )
        update_manager.logger = Mock()
        
        # Mock shutil.copytree to raise exception
        with patch('shutil.copytree', side_effect=Exception("Backup error")):
            result = update_manager.backup_db()
            
            assert result is False
            
            # Verify error was logged
            update_manager.logger.error.assert_called_with("Database backup failed: Backup error")
    
    def test_reload_clamav_engine_success(self):
        """Test successful ClamAV engine reload."""
        update_manager = ClamAVUpdateManager(
            db_path=self.db_path,
            backup_path=self.backup_path
        )
        update_manager.logger = Mock()
        
        # Mock successful reload (in real implementation, this would call freshclam)
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock()
            
            result = update_manager.reload_clamav_engine()
            
            assert result is True
            
            # Verify info was logged
            update_manager.logger.info.assert_called_with("ClamAV engine reload initiated")
    
    def test_reload_clamav_engine_exception(self):
        """Test ClamAV engine reload exception handling."""
        update_manager = ClamAVUpdateManager(
            db_path=self.db_path,
            backup_path=self.backup_path
        )
        update_manager.logger = Mock()
        
        # Mock subprocess.run to raise exception
        with patch('subprocess.run', side_effect=Exception("Reload error")):
            result = update_manager.reload_clamav_engine()
            
            assert result is False
            
            # Verify error was logged
            update_manager.logger.error.assert_called_with("ClamAV engine reload failed: Reload error")
    
    def test_validate_db_checksum_success(self):
        """Test successful database checksum validation."""
        update_manager = ClamAVUpdateManager(
            db_path=self.db_path,
            backup_path=self.backup_path
        )
        
        # This is a placeholder test - real implementation would calculate actual checksums
        result = update_manager._validate_db_checksum()
        
        # For now, we expect True as the method returns True in the placeholder
        assert result is True
    
    def test_get_db_version(self):
        """Test getting database version."""
        update_manager = ClamAVUpdateManager(
            db_path=self.db_path,
            backup_path=self.backup_path
        )
        
        # This is a placeholder test - real implementation would read version from files
        result = update_manager._get_db_version()
        
        # For now, we expect the placeholder version
        assert result == "2025-12-06.1"
    
    def test_get_last_update_time(self):
        """Test getting last update time."""
        update_manager = ClamAVUpdateManager(
            db_path=self.db_path,
            backup_path=self.backup_path
        )
        
        result = update_manager._get_last_update_time()
        
        # Should return a datetime object (not datetime.min)
        assert result.year > 1  # Not datetime.min
    
    def test_get_last_update_time_missing_db(self):
        """Test getting last update time when database is missing."""
        # Remove database
        shutil.rmtree(self.db_path)
        
        update_manager = ClamAVUpdateManager(
            db_path=self.db_path,
            backup_path=self.backup_path
        )
        
        result = update_manager._get_last_update_time()
        
        # Should return datetime.min when database doesn't exist
        assert result.year == 1  # datetime.min
    
    def test_complete_db_recovery_scenario(self):
        """Test complete database recovery scenario."""
        update_manager = ClamAVUpdateManager(
            db_path=self.db_path,
            backup_path=self.backup_path
        )
        update_manager.logger = Mock()
        
        # 1. Simulate corrupted database
        with patch.object(update_manager, '_validate_db_checksum', return_value=False):
            validation_result = update_manager.validate_virus_db()
            assert validation_result.checksum_valid is False
        
        # 2. Restore from backup
        restore_result = update_manager.restore_backup_db()
        assert restore_result is True
        
        # 3. Verify restore worked by checking files exist
        assert os.path.exists(os.path.join(self.db_path, "main.cvd"))
        
        # 4. Reload engine
        reload_result = update_manager.reload_clamav_engine()
        assert reload_result is True
        
        # 5. Verify all operations were logged
        assert update_manager.logger.info.call_count >= 2  # Restore + Reload
        assert update_manager.logger.error.call_count >= 1  # Validation failure
    
    def test_backup_before_restore_scenario(self):
        """Test backup before restore scenario."""
        update_manager = ClamAVUpdateManager(
            db_path=self.db_path,
            backup_path=self.backup_path
        )
        update_manager.logger = Mock()
        
        # 1. Create backup of current (good) database
        backup_result = update_manager.backup_db()
        assert backup_result is True
        
        # 2. Simulate database corruption by removing files
        shutil.rmtree(self.db_path)
        
        # 3. Restore from backup
        restore_result = update_manager.restore_backup_db()
        assert restore_result is True
        
        # 4. Verify database was restored
        assert os.path.exists(self.db_path)
        assert os.path.exists(os.path.join(self.db_path, "main.cvd"))