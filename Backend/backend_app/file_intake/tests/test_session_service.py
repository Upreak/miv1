# tests/test_session_service.py
"""
Tests for the session service.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from backend_app.file_intake.services.session_service import SessionService, get_session_service
from backend_app.file_intake.models.session_model import FileSession, SessionStatus, SessionType


class TestSessionService:
    """Test cases for session service."""
    
    def setup_method(self):
        """Setup test method."""
        self.config = Mock()
        self.config.session.timeout_hours = 24
        self.config.session.max_files_per_session = 10
        self.config.session.max_file_size = 10485760  # 10MB
        
        self.service = SessionService(self.config)
    
    def test_create_session_success(self):
        """Test successful session creation."""
        # Mock repository
        mock_repo = Mock()
        self.service.repository = mock_repo
        
        # Mock session creation
        mock_session = Mock()
        mock_session.session_id = "SID-test-session"
        mock_session.user_id = "user123"
        mock_session.session_type = SessionType.FILE_UPLOAD
        mock_session.expires_at = datetime.utcnow() + timedelta(hours=24)
        mock_session.metadata = {}
        mock_session.max_file_size = 10485760
        mock_session.max_files_per_session = 10
        
        mock_repo.save_session.return_value = mock_session
        
        # Test session creation
        session = self.service.create_session("user123", SessionType.FILE_UPLOAD)
        
        # Assertions
        assert session.session_id == "SID-test-session"
        assert session.user_id == "user123"
        assert session.session_type == SessionType.FILE_UPLOAD
        assert session.expires_at is not None
        assert session.metadata == {}
        
        # Verify repository was called
        mock_repo.save_session.assert_called_once()
    
    def test_create_session_with_metadata(self):
        """Test session creation with metadata."""
        # Mock repository
        mock_repo = Mock()
        self.service.repository = mock_repo
        
        # Mock session creation
        mock_session = Mock()
        mock_session.session_id = "SID-test-session"
        mock_session.user_id = "user123"
        mock_session.session_type = SessionType.FILE_UPLOAD
        mock_session.expires_at = datetime.utcnow() + timedelta(hours=24)
        mock_session.metadata = {"source": "web", "campaign": "test"}
        mock_session.max_file_size = 10485760
        mock_session.max_files_per_session = 10
        
        mock_repo.save_session.return_value = mock_session
        
        # Test session creation with metadata
        metadata = {"source": "web", "campaign": "test"}
        session = self.service.create_session("user123", SessionType.FILE_UPLOAD, metadata)
        
        # Assertions
        assert session.metadata == metadata
        
        # Verify repository was called
        mock_repo.save_session.assert_called_once()
    
    def test_get_session_success(self):
        """Test successful session retrieval."""
        # Mock repository
        mock_repo = Mock()
        self.service.repository = mock_repo
        
        # Mock session
        mock_session = Mock()
        mock_session.session_id = "SID-test-session"
        mock_session.is_expired.return_value = False
        mock_repo.get_session.return_value = mock_session
        
        # Test session retrieval
        session = self.service.get_session("SID-test-session")
        
        # Assertions
        assert session is not None
        assert session.session_id == "SID-test-session"
        
        # Verify repository was called
        mock_repo.get_session.assert_called_once_with("SID-test-session")
    
    def test_get_session_invalid_format(self):
        """Test session retrieval with invalid format."""
        # Test with invalid SID format
        session = self.service.get_session("invalid-sid")
        assert session is None
    
    def test_get_session_expired(self):
        """Test session retrieval for expired session."""
        # Mock repository
        mock_repo = Mock()
        self.service.repository = mock_repo
        
        # Mock expired session
        mock_session = Mock()
        mock_session.session_id = "SID-test-session"
        mock_session.is_expired.return_value = True
        mock_repo.get_session.return_value = mock_session
        
        # Mock mark session expired
        mock_repo.update_session.return_value = None
        
        # Test session retrieval
        session = self.service.get_session("SID-test-session")
        
        # Assertions
        assert session is None
        
        # Verify session was marked as expired
        mock_repo.update_session.assert_called_once()
    
    def test_get_active_sessions_success(self):
        """Test successful active sessions retrieval."""
        # Mock repository
        mock_repo = Mock()
        self.service.repository = mock_repo
        
        # Mock sessions
        mock_session1 = Mock()
        mock_session1.is_expired.return_value = False
        mock_session1.status = SessionStatus.ACTIVE
        
        mock_session2 = Mock()
        mock_session2.is_expired.return_value = False
        mock_session2.status = SessionStatus.ACTIVE
        
        mock_session3 = Mock()
        mock_session3.is_expired.return_value = True
        mock_session3.status = SessionStatus.ACTIVE
        
        mock_repo.get_sessions_by_user.return_value = [mock_session1, mock_session2, mock_session3]
        
        # Test active sessions retrieval
        active_sessions = self.service.get_active_sessions("user123")
        
        # Assertions
        assert len(active_sessions) == 2
        assert all(session.status == SessionStatus.ACTIVE for session in active_sessions)
        
        # Verify repository was called
        mock_repo.get_sessions_by_user.assert_called_once_with("user123")
    
    def test_update_session_progress_success(self):
        """Test successful session progress update."""
        # Mock repository
        mock_repo = Mock()
        self.service.repository = mock_repo
        
        # Mock session
        mock_session = Mock()
        mock_session.session_id = "SID-test-session"
        mock_session.update_progress.return_value = None
        mock_repo.get_session.return_value = mock_session
        
        # Test progress update
        success = self.service.update_session_progress("SID-test-session", 50)
        
        # Assertions
        assert success is True
        mock_session.update_progress.assert_called_once_with(50)
        mock_repo.update_session.assert_called_once_with(mock_session)
    
    def test_update_session_progress_not_found(self):
        """Test progress update for non-existent session."""
        # Mock repository
        mock_repo = Mock()
        self.service.repository = mock_repo
        mock_repo.get_session.return_value = None
        
        # Test progress update
        success = self.service.update_session_progress("invalid-session", 50)
        
        # Assertions
        assert success is False
    
    def test_add_file_to_session_success(self):
        """Test successful file addition to session."""
        # Mock repository
        mock_repo = Mock()
        self.service.repository = mock_repo
        
        # Mock session
        mock_session = Mock()
        mock_session.session_id = "SID-test-session"
        mock_session.max_file_size = 10485760
        mock_session.max_files_per_session = 10
        mock_session.file_count = 5
        mock_session.processed_files = 3
        mock_session.update_progress.return_value = None
        mock_repo.get_session.return_value = mock_session
        
        # Test file addition
        success = self.service.add_file_to_session(
            "SID-test-session", 
            "QID-test-file", 
            "test.pdf", 
            1024
        )
        
        # Assertions
        assert success is True
        mock_repo.add_file_to_session.assert_called_once_with(
            "SID-test-session", 
            "QID-test-file", 
            "test.pdf", 
            1024
        )
        mock_session.update_progress.assert_called_once()
        mock_repo.update_session.assert_called_once_with(mock_session)
    
    def test_add_file_to_session_too_large(self):
        """Test file addition with file size exceeding limit."""
        # Mock repository
        mock_repo = Mock()
        self.service.repository = mock_repo
        
        # Mock session
        mock_session = Mock()
        mock_session.max_file_size = 10485760
        mock_session.max_files_per_session = 10
        mock_session.file_count = 5
        mock_repo.get_session.return_value = mock_session
        
        # Test file addition with oversized file
        success = self.service.add_file_to_session(
            "SID-test-session", 
            "QID-test-file", 
            "test.pdf", 
            20971520  # 20MB
        )
        
        # Assertions
        assert success is False
        mock_repo.add_file_to_session.assert_not_called()
    
    def test_add_file_to_session_count_exceeded(self):
        """Test file addition with file count exceeding limit."""
        # Mock repository
        mock_repo = Mock()
        self.service.repository = mock_repo
        
        # Mock session
        mock_session = Mock()
        mock_session.max_file_size = 10485760
        mock_session.max_files_per_session = 10
        mock_session.file_count = 10  # At limit
        mock_repo.get_session.return_value = mock_session
        
        # Test file addition with count exceeded
        success = self.service.add_file_to_session(
            "SID-test-session", 
            "QID-test-file", 
            "test.pdf", 
            1024
        )
        
        # Assertions
        assert success is False
        mock_repo.add_file_to_session.assert_not_called()
    
    def test_mark_session_completed_success(self):
        """Test successful session completion."""
        # Mock repository
        mock_repo = Mock()
        self.service.repository = mock_repo
        
        # Mock session
        mock_session = Mock()
        mock_session.session_id = "SID-test-session"
        mock_session.mark_completed.return_value = None
        mock_repo.get_session.return_value = mock_session
        
        # Test session completion
        success = self.service.mark_session_completed("SID-test-session")
        
        # Assertions
        assert success is True
        mock_session.mark_completed.assert_called_once()
        mock_repo.update_session.assert_called_once_with(mock_session)
    
    def test_mark_session_failed_success(self):
        """Test successful session failure."""
        # Mock repository
        mock_repo = Mock()
        self.service.repository = mock_repo
        
        # Mock session
        mock_session = Mock()
        mock_session.session_id = "SID-test-session"
        mock_session.mark_failed.return_value = None
        mock_repo.get_session.return_value = mock_session
        
        # Test session failure
        success = self.service.mark_session_failed("SID-test-session", "Processing failed")
        
        # Assertions
        assert success is True
        mock_session.mark_failed.assert_called_once_with("Processing failed")
        mock_repo.update_session.assert_called_once_with(mock_session)
    
    def test_extend_session_expiry_success(self):
        """Test successful session expiry extension."""
        # Mock repository
        mock_repo = Mock()
        self.service.repository = mock_repo
        
        # Mock session
        mock_session = Mock()
        mock_session.session_id = "SID-test-session"
        mock_session.extend_expiry.return_value = None
        mock_repo.get_session.return_value = mock_session
        
        # Test expiry extension
        success = self.service.extend_session_expiry("SID-test-session", 24)
        
        # Assertions
        assert success is True
        mock_session.extend_expiry.assert_called_once_with(24)
        mock_repo.update_session.assert_called_once_with(mock_session)
    
    def test_get_session_statistics_success(self):
        """Test successful session statistics retrieval."""
        # Mock repository
        mock_repo = Mock()
        self.service.repository = mock_repo
        
        # Mock sessions
        mock_session1 = Mock()
        mock_session1.status = SessionStatus.ACTIVE
        mock_session1.file_count = 5
        mock_session1.processed_files = 3
        mock_session1.failed_files = 1
        
        mock_session2 = Mock()
        mock_session2.status = SessionStatus.COMPLETED
        mock_session2.file_count = 3
        mock_session2.processed_files = 3
        mock_session2.failed_files = 0
        
        mock_session3 = Mock()
        mock_session3.status = SessionStatus.FAILED
        mock_session3.file_count = 2
        mock_session3.processed_files = 1
        mock_session3.failed_files = 1
        
        mock_repo.get_sessions_by_user.return_value = [mock_session1, mock_session2, mock_session3]
        
        # Test statistics retrieval
        stats = self.service.get_session_statistics("user123")
        
        # Assertions
        assert stats["total_sessions"] == 3
        assert stats["active_sessions"] == 1
        assert stats["completed_sessions"] == 1
        assert stats["failed_sessions"] == 1
        assert stats["total_files"] == 10
        assert stats["processed_files"] == 7
        assert stats["failed_files"] == 2
    
    def test_validate_session_for_upload_success(self):
        """Test successful session validation for upload."""
        # Mock repository
        mock_repo = Mock()
        self.service.repository = mock_repo
        
        # Mock session
        mock_session = Mock()
        mock_session.status = SessionStatus.ACTIVE
        mock_session.max_file_size = 10485760
        mock_session.max_files_per_session = 10
        mock_session.file_count = 5
        mock_repo.get_session.return_value = mock_session
        
        # Test validation
        valid = self.service.validate_session_for_upload("SID-test-session", 1024)
        
        # Assertions
        assert valid is True
    
    def test_validate_session_for_upload_failed_status(self):
        """Test session validation for upload with failed status."""
        # Mock repository
        mock_repo = Mock()
        self.service.repository = mock_repo
        
        # Mock session
        mock_session = Mock()
        mock_session.status = SessionStatus.FAILED
        mock_repo.get_session.return_value = mock_session
        
        # Test validation
        valid = self.service.validate_session_for_upload("SID-test-session", 1024)
        
        # Assertions
        assert valid is False
    
    def test_validate_session_for_upload_too_large(self):
        """Test session validation for upload with oversized file."""
        # Mock repository
        mock_repo = Mock()
        self.service.repository = mock_repo
        
        # Mock session
        mock_session = Mock()
        mock_session.status = SessionStatus.ACTIVE
        mock_session.max_file_size = 10485760
        mock_session.max_files_per_session = 10
        mock_session.file_count = 5
        mock_repo.get_session.return_value = mock_session
        
        # Test validation with oversized file
        valid = self.service.validate_session_for_upload("SID-test-session", 20971520)
        
        # Assertions
        assert valid is False
    
    def test_validate_session_for_upload_count_exceeded(self):
        """Test session validation for upload with count exceeded."""
        # Mock repository
        mock_repo = Mock()
        self.service.repository = mock_repo
        
        # Mock session
        mock_session = Mock()
        mock_session.status = SessionStatus.ACTIVE
        mock_session.max_file_size = 10485760
        mock_session.max_files_per_session = 10
        mock_session.file_count = 10  # At limit
        mock_repo.get_session.return_value = mock_session
        
        # Test validation with count exceeded
        valid = self.service.validate_session_for_upload("SID-test-session", 1024)
        
        # Assertions
        assert valid is False


class TestSessionServiceGlobal:
    """Test cases for global session service functions."""
    
    def test_get_session_service(self):
        """Test global session service retrieval."""
        with patch('backend_app.file_intake.services.session_service.SessionService') as mock_class:
            mock_instance = Mock()
            mock_class.return_value = mock_instance
            
            service = get_session_service()
            
            assert service == mock_instance
            mock_class.assert_called_once()
    
    def test_create_session_global(self):
        """Test global session creation."""
        with patch('backend_app.file_intake.services.session_service.get_session_service') as mock_get:
            mock_service = Mock()
            mock_session = Mock()
            mock_service.create_session.return_value = mock_session
            mock_get.return_value = mock_service
            
            session = create_session("user123")
            
            assert session == mock_session
            mock_service.create_session.assert_called_once_with("user123", None, None)
    
    def test_get_session_global(self):
        """Test global session retrieval."""
        with patch('backend_app.file_intake.services.session_service.get_session_service') as mock_get:
            mock_service = Mock()
            mock_session = Mock()
            mock_service.get_session.return_value = mock_session
            mock_get.return_value = mock_service
            
            session = get_session("SID-test-session")
            
            assert session == mock_session
            mock_service.get_session.assert_called_once_with("SID-test-session")
    
    def test_get_active_sessions_global(self):
        """Test global active sessions retrieval."""
        with patch('backend_app.file_intake.services.session_service.get_session_service') as mock_get:
            mock_service = Mock()
            mock_sessions = [Mock(), Mock()]
            mock_service.get_active_sessions.return_value = mock_sessions
            mock_get.return_value = mock_service
            
            sessions = get_active_sessions("user123")
            
            assert sessions == mock_sessions
            mock_service.get_active_sessions.assert_called_once_with("user123")


if __name__ == "__main__":
    pytest.main([__file__])