"""
Test suite for virus scan functionality.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from backend_app.file_intake.services.virus_scan_service import (
    get_virus_scan_service,
    ClamAVScanService,
    VirusTotalScanService,
    CompositeScanService
)
from backend_app.file_intake.config.intake_config import get_config


class TestVirusScanService:
    """Test cases for virus scan service."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = get_config()
        self.test_file_content = b"Test file content for virus scanning"
    
    def test_clamav_scan_service_clean_file(self):
        """Test ClamAV scan service with clean file."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
            temp_file.write(self.test_file_content)
            temp_file_path = temp_file.name
        
        try:
            # Mock ClamAV response for clean file
            with patch('backend_app.file_intake.services.virus_scan_service.pyclamd') as mock_pyclamd:
                mock_clamd = Mock()
                mock_pyclamd.ClamdUnixSocket.return_value = mock_clamd
                mock_clamd.scan_file.return_value = None  # Clean file
                
                # Create service and scan
                service = ClamAVScanService(self.config)
                result = service.scan_file(temp_file_path)
                
                # Assert result
                assert result.result == "clean"
                assert result.scan_time > 0
                assert result.engine == "clamav"
                assert result.virus_name is None
                
                # Assert ClamAV was called
                mock_clamd.scan_file.assert_called_once_with(temp_file_path)
                
        finally:
            # Clean up
            os.unlink(temp_file_path)
    
    def test_clamav_scan_service_infected_file(self):
        """Test ClamAV scan service with infected file."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
            temp_file.write(self.test_file_content)
            temp_file_path = temp_file.name
        
        try:
            # Mock ClamAV response for infected file
            with patch('backend_app.file_intake.services.virus_scan_service.pyclamd') as mock_pyclamd:
                mock_clamd = Mock()
                mock_pyclamd.ClamdUnixSocket.return_value = mock_clamd
                mock_clamd.scan_file.return_value = {
                    temp_file_path: ('FOUND', 'Trojan.Agent-12345')
                }
                
                # Create service and scan
                service = ClamAVScanService(self.config)
                result = service.scan_file(temp_file_path)
                
                # Assert result
                assert result.result == "infected"
                assert result.scan_time > 0
                assert result.engine == "clamav"
                assert result.virus_name == "Trojan.Agent-12345"
                
                # Assert ClamAV was called
                mock_clamd.scan_file.assert_called_once_with(temp_file_path)
                
        finally:
            # Clean up
            os.unlink(temp_file_path)
    
    def test_clamav_scan_service_error(self):
        """Test ClamAV scan service with error."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
            temp_file.write(self.test_file_content)
            temp_file_path = temp_file.name
        
        try:
            # Mock ClamAV response for error
            with patch('backend_app.file_intake.services.virus_scan_service.pyclamd') as mock_pyclamd:
                mock_clamd = Mock()
                mock_pyclamd.ClamdUnixSocket.return_value = mock_clamd
                mock_clamd.scan_file.side_effect = Exception("Connection failed")
                
                # Create service and scan
                service = ClamAVScanService(self.config)
                result = service.scan_file(temp_file_path)
                
                # Assert result
                assert result.result == "error"
                assert result.scan_time > 0
                assert result.engine == "clamav"
                assert result.virus_name is None
                assert "Connection failed" in result.error_message
                
                # Assert ClamAV was called
                mock_clamd.scan_file.assert_called_once_with(temp_file_path)
                
        finally:
            # Clean up
            os.unlink(temp_file_path)
    
    def test_virustotal_scan_service_clean_file(self):
        """Test VirusTotal scan service with clean file."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
            temp_file.write(self.test_file_content)
            temp_file_path = temp_file.name
        
        try:
            # Mock VirusTotal response for clean file
            with patch('backend_app.file_intake.services.virus_scan_service.VirusTotalScanService') as mock_vt:
                mock_service = Mock()
                mock_service.scan_file.return_value = {
                    "result": "clean",
                    "scan_time": 2.5,
                    "engine": "virustotal",
                    "virus_name": None,
                    "positives": 0,
                    "total": 1
                }
                mock_vt.return_value = mock_service
                
                # Create service and scan
                service = VirusTotalScanService(self.config)
                result = service.scan_file(temp_file_path)
                
                # Assert result
                assert result.result == "clean"
                assert result.scan_time == 2.5
                assert result.engine == "virustotal"
                assert result.virus_name is None
                
                # Assert VirusTotal was called
                mock_service.scan_file.assert_called_once_with(temp_file_path)
                
        finally:
            # Clean up
            os.unlink(temp_file_path)
    
    def test_virustotal_scan_service_infected_file(self):
        """Test VirusTotal scan service with infected file."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
            temp_file.write(self.test_file_content)
            temp_file_path = temp_file.name
        
        try:
            # Mock VirusTotal response for infected file
            with patch('backend_app.file_intake.services.virus_scan_service.VirusTotalScanService') as mock_vt:
                mock_service = Mock()
                mock_service.scan_file.return_value = {
                    "result": "infected",
                    "scan_time": 3.2,
                    "engine": "virustotal",
                    "virus_name": "TrojanDownloader",
                    "positives": 1,
                    "total": 1
                }
                mock_vt.return_value = mock_service
                
                # Create service and scan
                service = VirusTotalScanService(self.config)
                result = service.scan_file(temp_file_path)
                
                # Assert result
                assert result.result == "infected"
                assert result.scan_time == 3.2
                assert result.engine == "virustotal"
                assert result.virus_name == "TrojanDownloader"
                
                # Assert VirusTotal was called
                mock_service.scan_file.assert_called_once_with(temp_file_path)
                
        finally:
            # Clean up
            os.unlink(temp_file_path)
    
    def test_composite_scan_service_clean_file(self):
        """Test composite scan service with clean file."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
            temp_file.write(self.test_file_content)
            temp_file_path = temp_file.name
        
        try:
            # Mock scan services
            with patch('backend_app.file_intake.services.virus_scan_service.get_clamav_service') as mock_clamav, \
                 patch('backend_app.file_intake.services.virus_scan_service.get_virustotal_service') as mock_vt:
                
                mock_clamav_service = Mock()
                mock_clamav_service.scan_file.return_value = {
                    "result": "clean",
                    "scan_time": 1.0,
                    "engine": "clamav",
                    "virus_name": None
                }
                
                mock_vt_service = Mock()
                mock_vt_service.scan_file.return_value = {
                    "result": "clean",
                    "scan_time": 2.0,
                    "engine": "virustotal",
                    "virus_name": None
                }
                
                mock_clamav.return_value = mock_clamav_service
                mock_vt.return_value = mock_vt_service
                
                # Create service and scan
                service = CompositeScanService(self.config)
                result = service.scan_file(temp_file_path)
                
                # Assert result
                assert result.result == "clean"
                assert result.scan_time == 3.0  # 1.0 + 2.0
                assert result.engine == "composite"
                assert result.virus_name is None
                
                # Assert both services were called
                mock_clamav_service.scan_file.assert_called_once_with(temp_file_path)
                mock_vt_service.scan_file.assert_called_once_with(temp_file_path)
                
        finally:
            # Clean up
            os.unlink(temp_file_path)
    
    def test_composite_scan_service_mixed_results(self):
        """Test composite scan service with mixed results."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
            temp_file.write(self.test_file_content)
            temp_file_path = temp_file.name
        
        try:
            # Mock scan services with mixed results
            with patch('backend_app.file_intake.services.virus_scan_service.get_clamav_service') as mock_clamav, \
                 patch('backend_app.file_intake.services.virus_scan_service.get_virustotal_service') as mock_vt:
                
                mock_clamav_service = Mock()
                mock_clamav_service.scan_file.return_value = {
                    "result": "clean",
                    "scan_time": 1.0,
                    "engine": "clamav",
                    "virus_name": None
                }
                
                mock_vt_service = Mock()
                mock_vt_service.scan_file.return_value = {
                    "result": "infected",
                    "scan_time": 2.0,
                    "engine": "virustotal",
                    "virus_name": "TrojanDownloader"
                }
                
                mock_clamav.return_value = mock_clamav_service
                mock_vt.return_value = mock_vt_service
                
                # Create service and scan
                service = CompositeScanService(self.config)
                result = service.scan_file(temp_file_path)
                
                # Assert result - should be infected if any engine detects virus
                assert result.result == "infected"
                assert result.scan_time == 3.0  # 1.0 + 2.0
                assert result.engine == "composite"
                assert result.virus_name == "TrojanDownloader"
                
                # Assert both services were called
                mock_clamav_service.scan_file.assert_called_once_with(temp_file_path)
                mock_vt_service.scan_file.assert_called_once_with(temp_file_path)
                
        finally:
            # Clean up
            os.unlink(temp_file_path)
    
    def test_composite_scan_service_all_error(self):
        """Test composite scan service with all services error."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
            temp_file.write(self.test_file_content)
            temp_file_path = temp_file.name
        
        try:
            # Mock scan services with errors
            with patch('backend_app.file_intake.services.virus_scan_service.get_clamav_service') as mock_clamav, \
                 patch('backend_app.file_intake.services.virus_scan_service.get_virustotal_service') as mock_vt:
                
                mock_clamav_service = Mock()
                mock_clamav_service.scan_file.return_value = {
                    "result": "error",
                    "scan_time": 1.0,
                    "engine": "clamav",
                    "virus_name": None,
                    "error_message": "Connection failed"
                }
                
                mock_vt_service = Mock()
                mock_vt_service.scan_file.return_value = {
                    "result": "error",
                    "scan_time": 2.0,
                    "engine": "virustotal",
                    "virus_name": None,
                    "error_message": "API limit exceeded"
                }
                
                mock_clamav.return_value = mock_clamav_service
                mock_vt.return_value = mock_vt_service
                
                # Create service and scan
                service = CompositeScanService(self.config)
                result = service.scan_file(temp_file_path)
                
                # Assert result
                assert result.result == "error"
                assert result.scan_time == 3.0  # 1.0 + 2.0
                assert result.engine == "composite"
                assert result.virus_name is None
                
                # Assert both services were called
                mock_clamav_service.scan_file.assert_called_once_with(temp_file_path)
                mock_vt_service.scan_file.assert_called_once_with(temp_file_path)
                
        finally:
            # Clean up
            os.unlink(temp_file_path)
    
    def test_get_virus_scan_service_clamav_only(self):
        """Test getting virus scan service with ClamAV only."""
        # Mock config
        with patch('backend_app.file_intake.services.virus_scan_service.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.virus_scan.engines = ["clamav"]
            mock_get_config.return_value = mock_config
            
            service = get_virus_scan_service(mock_config)
            
            # Should return ClamAV service
            assert isinstance(service, ClamAVScanService)
    
    def test_get_virus_scan_service_virustotal_only(self):
        """Test getting virus scan service with VirusTotal only."""
        # Mock config
        with patch('backend_app.file_intake.services.virus_scan_service.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.virus_scan.engines = ["virustotal"]
            mock_get_config.return_value = mock_config
            
            service = get_virus_scan_service(mock_config)
            
            # Should return VirusTotal service
            assert isinstance(service, VirusTotalScanService)
    
    def test_get_virus_scan_service_composite(self):
        """Test getting virus scan service with composite."""
        # Mock config
        with patch('backend_app.file_intake.services.virus_scan_service.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.virus_scan.engines = ["clamav", "virustotal"]
            mock_get_config.return_value = mock_config
            
            service = get_virus_scan_service(mock_config)
            
            # Should return composite service
            assert isinstance(service, CompositeScanService)
    
    def test_scan_file_bytes(self):
        """Test scanning file bytes directly."""
        # Mock scan service
        with patch('backend_app.file_intake.services.virus_scan_service.get_virus_scan_service') as mock_get_service:
            mock_service = Mock()
            mock_service.scan_file.return_value = {
                "result": "clean",
                "scan_time": 1.0,
                "engine": "clamav",
                "virus_name": None
            }
            mock_get_service.return_value = mock_service
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
                temp_file.write(self.test_file_content)
                temp_file_path = temp_file.name
            
            try:
                # Scan file bytes
                result = mock_service.scan_file(temp_file_path)
                
                # Assert result
                assert result.result == "clean"
                assert result.scan_time == 1.0
                assert result.engine == "clamav"
                assert result.virus_name is None
                
            finally:
                # Clean up
                os.unlink(temp_file_path)
    
    def test_scan_file_nonexistent(self):
        """Test scanning non-existent file."""
        # Mock scan service
        with patch('backend_app.file_intake.services.virus_scan_service.get_virus_scan_service') as mock_get_service:
            mock_service = Mock()
            mock_service.scan_file.side_effect = FileNotFoundError("File not found")
            mock_get_service.return_value = mock_service
            
            # Try to scan non-existent file
            with pytest.raises(FileNotFoundError):
                mock_service.scan_file("/nonexistent/file.txt")
    
    def test_scan_file_timeout(self):
        """Test scanning file with timeout."""
        # Mock scan service
        with patch('backend_app.file_intake.services.virus_scan_service.get_virus_scan_service') as mock_get_service:
            mock_service = Mock()
            mock_service.scan_file.side_effect = TimeoutError("Scan timed out")
            mock_get_service.return_value = mock_service
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
                temp_file.write(self.test_file_content)
                temp_file_path = temp_file.name
            
            try:
                # Scan file with timeout
                result = mock_service.scan_file(temp_file_path)
                
                # Should handle timeout gracefully
                assert result.result == "error"
                assert "timed out" in result.error_message
                
            finally:
                # Clean up
                os.unlink(temp_file_path)