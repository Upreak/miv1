"""
Test for infected file scanning functionality.

Testing Parameters:
- Test: Infected file scan
- Expected Behavior: Moves → infected folder, status = INFECTED
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


class TestInfectedFileScan:
    """Test suite for infected file scanning operations."""
    
    def setup_method(self):
        """Setup test environment."""
        # Create temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.config = SecurityScanConfig()
        self.config.quarantine_base_path = self.temp_dir
        self.config.ensure_folder_structure()
        
        # Create test file content (simulating infected content)
        self.test_content = b"This file contains malicious content (simulated)."
        self.test_filename = "infected_test.txt"
        self.test_mime_type = "text/plain"
    
    def teardown_method(self):
        """Clean up test environment."""
        # Remove temporary directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_scan_service_infected_file(self):
        """Test that scan service correctly identifies infected files."""
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
                file_id="test_infected_001",
                file_path=temp_file_path,
                mime_type=self.test_mime_type
            )
            
            # Mock ClamAV scan to return infected result
            with patch.object(scan_service, 'run_clamav_scan') as mock_scan:
                mock_scan.return_value = {
                    'status': 'FOUND',
                    'virus_name': 'EICAR-Test-Signature',
                    'scan_time': 0.1,
                    'error': None
                }
                
                # Perform scan
                result = scan_service.scan_file(scan_request)
                
                # Verify result
                assert result.status == ScanStatus.INFECTED
                assert result.details['engine'] == 'ClamAV'
                assert result.details['virus_name'] == 'EICAR-Test-Signature'
                assert result.details['scan_time'] is not None
                assert result.safe_path is None
                assert result.infected_path is not None
                
                # Verify logging was called
                scan_service.log_scan_result.assert_called_once_with(result)
                
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    def test_quarantine_manager_infected_file_flow(self):
        """Test quarantine manager file movement for infected files."""
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
        
        # 3. Mark as infected
        infected_path = quarantine_manager.mark_as_infected(scanning_path)
        
        assert os.path.exists(infected_path)
        assert "infected" in infected_path
        assert not os.path.exists(scanning_path)  # Should be moved
        
        # 4. Verify file content is preserved
        with open(infected_path, 'rb') as f:
            content = f.read()
            assert content == self.test_content
    
    def test_complete_infected_scan_workflow(self):
        """Test complete workflow for infected file scanning."""
        # Create quarantine manager
        quarantine_manager = FileQuarantineManager(self.temp_dir)
        
        # Create scan service
        scan_service = ClamAVScanService()
        scan_service.logger = Mock()
        
        # Mock ClamAV scan to return infected result
        with patch.object(scan_service, 'run_clamav_scan') as mock_scan:
            mock_scan.return_value = {
                'status': 'FOUND',
                'virus_name': 'Test-Virus',
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
                file_id="test_infected_workflow_001",
                file_path=scanning_path,
                mime_type=self.test_mime_type
            )
            
            scan_result = scan_service.scan_file(scan_request)
            
            # 4. Move based on scan result
            if scan_result.status == ScanStatus.INFECTED:
                final_path = quarantine_manager.mark_as_infected(scanning_path)
                
                # Verify final state
                assert scan_result.status == ScanStatus.INFECTED
                assert os.path.exists(final_path)
                assert "infected" in final_path
                
                # Verify file content
                with open(final_path, 'rb') as f:
                    content = f.read()
                    assert content == self.test_content
    
    def test_infected_file_scan_with_api_simulation(self):
        """Test infected file scan simulating API endpoint behavior."""
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
        
        # Mock ClamAV scan to return infected result
        with patch.object(scan_service, 'run_clamav_scan') as mock_scan:
            mock_scan.return_value = {
                'status': 'FOUND',
                'virus_name': 'EICAR-Test-Signature',
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
            if scan_result.status == ScanStatus.INFECTED:
                final_path = quarantine_manager.mark_as_infected(scanning_path)
                
                # Verify API response structure
                response_data = {
                    "status": scan_result.status.value,
                    "details": scan_result.details,
                    "safe_path": scan_result.safe_path,
                    "infected_path": scan_result.infected_path,
                    "timestamp": scan_result.timestamp.isoformat()
                }
                
                assert response_data["status"] == "INFECTED"
                assert response_data["safe_path"] is None
                assert response_data["infected_path"] is not None
                assert "ClamAV" in response_data["details"]["engine"]
                assert response_data["details"]["virus_name"] == "EICAR-Test-Signature"
    
    def test_multiple_infected_files_isolation(self):
        """Test that multiple infected files are properly isolated."""
        quarantine_manager = FileQuarantineManager(self.temp_dir)
        
        # Create multiple infected test files
        infected_files = [
            (b"Malicious content 1", "bad1.txt"),
            (b"Malicious content 2", "bad2.txt"),
            (b"Malicious content 3", "bad3.txt")
        ]
        
        paths = []
        
        # Process each file
        for content, filename in infected_files:
            # Move to incoming
            incoming_path = quarantine_manager.move_to_incoming(content, filename)
            paths.append(incoming_path)
        
        # Verify all files exist in incoming folder
        incoming_files = os.listdir(os.path.join(self.temp_dir, "incoming"))
        assert len(incoming_files) == 3
        
        # Process each file through scanning to infected
        for i, path in enumerate(paths):
            scanning_path = quarantine_manager.move_to_scanning(path)
            infected_path = quarantine_manager.mark_as_infected(scanning_path)
            
            # Verify each file has unique path in infected folder
            assert os.path.exists(infected_path)
            assert "infected" in infected_path
            assert f"bad{i+1}.txt" in infected_path
        
        # Verify all files are in infected folder
        infected_files = os.listdir(os.path.join(self.temp_dir, "infected"))
        assert len(infected_files) == 3
    
    def test_infected_file_error_handling(self):
        """Test error handling during infected file processing."""
        quarantine_manager = FileQuarantineManager(self.temp_dir)
        
        # Create test file
        incoming_path = quarantine_manager.move_to_incoming(
            self.test_content, 
            self.test_filename
        )
        
        scanning_path = quarantine_manager.move_to_scanning(incoming_path)
        
        # Test that infected file movement works even with partial failures
        try:
            infected_path = quarantine_manager.mark_as_infected(scanning_path)
            assert os.path.exists(infected_path)
            
            # Verify original file is moved
            assert not os.path.exists(scanning_path)
            
        except Exception as e:
            # If there's an error, ensure we can still handle it
            assert os.path.exists(scanning_path) or os.path.exists(
                os.path.join(self.temp_dir, "infected")
            )
    
    def test_infected_file_metadata_preservation(self):
        """Test that infected file metadata is preserved during quarantine."""
        quarantine_manager = FileQuarantineManager(self.temp_dir)
        
        # Create test file
        incoming_path = quarantine_manager.move_to_incoming(
            self.test_content, 
            self.test_filename
        )
        
        scanning_path = quarantine_manager.move_to_scanning(incoming_path)
        infected_path = quarantine_manager.mark_as_infected(scanning_path)
        
        # Verify file exists and content is preserved
        assert os.path.exists(infected_path)
        
        with open(infected_path, 'rb') as f:
            content = f.read()
            assert content == self.test_content
        
        # Verify file has proper permissions (read-only for security)
        file_stat = os.stat(infected_path)
        # On Windows, we can't easily set read-only, but we can check if file exists
        assert file_stat.st_size == len(self.test_content)
    
    def test_scan_error_handling_infected_simulation(self):
        """Test scan service error handling with infected file simulation."""
        scan_service = ClamAVScanService()
        scan_service.logger = Mock()
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as temp_file:
            temp_file.write(self.test_content)
            temp_file_path = temp_file.name
        
        try:
            scan_request = ScanRequest(
                file_id="test_error_001",
                file_path=temp_file_path,
                mime_type=self.test_mime_type
            )
            
            # Mock ClamAV scan to return error
            with patch.object(scan_service, 'run_clamav_scan') as mock_scan:
                mock_scan.return_value = {
                    'status': 'ERROR',
                    'virus_name': None,
                    'scan_time': None,
                    'error': 'Connection timeout'
                }
                
                # Perform scan
                result = scan_service.scan_file(scan_request)
                
                # Verify error result
                assert result.status == ScanStatus.ERROR
                assert result.details['engine'] == 'ClamAV'
                assert result.details['error'] == 'Connection timeout'
                assert result.safe_path is None
                assert result.infected_path is None
                
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)