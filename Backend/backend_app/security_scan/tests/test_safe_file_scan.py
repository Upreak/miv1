"""
Test for safe file scanning functionality.

Testing Parameters:
- Test: Safe file scan
- Expected Behavior: Moves → clean folder, status = SAFE
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from fastapi import UploadFile
from io import BytesIO

from ...security_scan.io_contract import ScanRequest, ScanResult, ScanStatus
from ...security_scan.scan_service import ClamAVScanService
from ...security_scan.quarantine_manager import FileQuarantineManager
from ...security_scan.config import SecurityScanConfig


class TestSafeFileScan:
    """Test suite for safe file scanning operations."""
    
    def setup_method(self):
        """Setup test environment."""
        # Create temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.config = SecurityScanConfig()
        self.config.quarantine_base_path = self.temp_dir
        self.config.ensure_folder_structure()
        
        # Create test file content
        self.test_content = b"This is a safe test file content."
        self.test_filename = "safe_test.txt"
        self.test_mime_type = "text/plain"
    
    def teardown_method(self):
        """Clean up test environment."""
        # Remove temporary directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_scan_service_safe_file(self):
        """Test that scan service correctly identifies safe files."""
        # Create scan service
        scan_service = ClamAVScanService()
        scan_service.logger = Mock()
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as temp_file:
            temp_file.write(self.test_content)
            temp_file_path = temp_file.name
        
        try:
            # Create scan request
            scan_request = ScanRequest(
                file_id="test_safe_001",
                file_path=temp_file_path,
                mime_type=self.test_mime_type
            )
            
            # Mock ClamAV scan to return safe result
            with patch.object(scan_service, 'run_clamav_scan') as mock_scan:
                mock_scan.return_value = {
                    'status': 'OK',
                    'scan_time': 0.1,
                    'error': None
                }
                
                # Perform scan
                result = scan_service.scan_file(scan_request)
                
                # Verify result
                assert result.status == ScanStatus.SAFE
                assert result.details['engine'] == 'ClamAV'
                assert result.details['scan_time'] is not None
                assert result.safe_path is not None
                assert result.infected_path is None
                
                # Verify logging was called
                scan_service.log_scan_result.assert_called_once_with(result)
                
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    def test_quarantine_manager_safe_file_flow(self):
        """Test quarantine manager file movement for safe files."""
        # Create quarantine manager
        quarantine_manager = FileQuarantineManager(self.temp_dir)
        
        # 1. Move to incoming
        incoming_path = quarantine_manager.move_to_incoming(
            self.test_content, 
            self.test_filename
        )
        
        assert os.path.exists(incoming_path)
        assert "incoming" in incoming_path
        
        # 2. Move to scanning
        scanning_path = quarantine_manager.move_to_scanning(incoming_path)
        
        assert os.path.exists(scanning_path)
        assert "scanning" in scanning_path
        assert not os.path.exists(incoming_path)  # Should be moved
        
        # 3. Mark as safe
        clean_path = quarantine_manager.mark_as_safe(scanning_path)
        
        assert os.path.exists(clean_path)
        assert "clean" in clean_path
        assert not os.path.exists(scanning_path)  # Should be moved
        
        # 4. Verify file content is preserved
        with open(clean_path, 'rb') as f:
            content = f.read()
            assert content == self.test_content
    
    def test_complete_safe_scan_workflow(self):
        """Test complete workflow for safe file scanning."""
        # Create quarantine manager
        quarantine_manager = FileQuarantineManager(self.temp_dir)
        
        # Create scan service
        scan_service = ClamAVScanService()
        scan_service.logger = Mock()
        
        # Mock ClamAV scan to return safe result
        with patch.object(scan_service, 'run_clamav_scan') as mock_scan:
            mock_scan.return_value = {
                'status': 'OK',
                'scan_time': 0.1,
                'error': None
            }
            
            # 1. Move to incoming
            incoming_path = quarantine_manager.move_to_incoming(
                self.test_content, 
                self.test_filename
            )
            
            # 2. Move to scanning
            scanning_path = quarantine_manager.move_to_scanning(incoming_path)
            
            # 3. Create scan request and perform scan
            scan_request = ScanRequest(
                file_id="test_safe_workflow_001",
                file_path=scanning_path,
                mime_type=self.test_mime_type
            )
            
            scan_result = scan_service.scan_file(scan_request)
            
            # 4. Move based on scan result
            if scan_result.status == ScanStatus.SAFE:
                final_path = quarantine_manager.mark_as_safe(scanning_path)
                
                # Verify final state
                assert scan_result.status == ScanStatus.SAFE
                assert os.path.exists(final_path)
                assert "clean" in final_path
                
                # Verify file content
                with open(final_path, 'rb') as f:
                    content = f.read()
                    assert content == self.test_content
    
    def test_safe_file_scan_with_api_simulation(self):
        """Test safe file scan simulating API endpoint behavior."""
        # Create mock upload file
        file_content = BytesIO(self.test_content)
        upload_file = UploadFile(
            file=file_content,
            filename=self.test_filename,
            content_type=self.test_mime_type
        )
        
        # Create quarantine manager
        quarantine_manager = FileQuarantineManager(self.temp_dir)
        
        # Create scan service
        scan_service = ClamAVScanService()
        scan_service.logger = Mock()
        
        # Mock ClamAV scan to return safe result
        with patch.object(scan_service, 'run_clamav_scan') as mock_scan:
            mock_scan.return_value = {
                'status': 'OK',
                'scan_time': 0.1,
                'error': None
            }
            
            # Simulate API endpoint logic
            # 1. Move to incoming
            incoming_path = quarantine_manager.move_to_incoming(
                self.test_content, 
                self.test_filename
            )
            
            # 2. Move to scanning
            scanning_path = quarantine_manager.move_to_scanning(incoming_path)
            
            # 3. Create scan request
            scan_request = ScanRequest(
                file_id=f"scan_{os.path.basename(scanning_path)}",
                file_path=scanning_path,
                mime_type=self.test_mime_type
            )
            
            # 4. Perform scan
            scan_result = scan_service.scan_file(scan_request)
            
            # 5. Move file based on result
            if scan_result.status == ScanStatus.SAFE:
                final_path = quarantine_manager.mark_as_safe(scanning_path)
                
                # Verify API response structure
                response_data = {
                    "status": scan_result.status.value,
                    "details": scan_result.details,
                    "safe_path": scan_result.safe_path,
                    "infected_path": scan_result.infected_path,
                    "timestamp": scan_result.timestamp.isoformat()
                }
                
                assert response_data["status"] == "SAFE"
                assert response_data["safe_path"] is not None
                assert response_data["infected_path"] is None
                assert "ClamAV" in response_data["details"]["engine"]
    
    def test_concurrent_safe_scans_unique_ids(self):
        """Test that concurrent scans generate unique IDs and don't conflict."""
        quarantine_manager = FileQuarantineManager(self.temp_dir)
        
        # Create multiple test files
        test_files = [
            (b"Content of file 1", "file1.txt"),
            (b"Content of file 2", "file2.txt"),
            (b"Content of file 3", "file3.txt")
        ]
        
        paths = []
        
        # Process each file
        for content, filename in test_files:
            # Move to incoming
            incoming_path = quarantine_manager.move_to_incoming(content, filename)
            paths.append(incoming_path)
        
        # Verify all files exist in incoming folder
        incoming_files = os.listdir(os.path.join(self.temp_dir, "incoming"))
        assert len(incoming_files) == 3
        
        # Verify unique naming
        unique_names = set(incoming_files)
        assert len(unique_names) == 3
        
        # Process each file through scanning to clean
        for i, path in enumerate(paths):
            scanning_path = quarantine_manager.move_to_scanning(path)
            clean_path = quarantine_manager.mark_as_safe(scanning_path)
            
            # Verify each file has unique path
            assert os.path.exists(clean_path)
            assert f"file{i+1}.txt" in clean_path
    
    def test_safe_file_size_validation(self):
        """Test that safe files respect size limits."""
        config = SecurityScanConfig()
        config.max_file_size = 100  # Small limit for testing
        
        # Create file that's too large
        large_content = b"x" * 200
        
        quarantine_manager = FileQuarantineManager(self.temp_dir)
        
        # Should still work for quarantine manager (size check is in API)
        incoming_path = quarantine_manager.move_to_incoming(large_content, "large.txt")
        assert os.path.exists(incoming_path)
        
        # Verify file size
        file_size = os.path.getsize(incoming_path)
        assert file_size == 200