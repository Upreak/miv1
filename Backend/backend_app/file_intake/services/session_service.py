# services/session_service.py
"""
Session Manager - Handles session lifecycle and state management.

This service provides:
- Session creation and management
- Session state tracking
- Session expiry handling
- Session metadata management
- Session validation
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from ..config.intake_config import get_config
from ..utils.logging_utils import get_logger
from ..utils.sid_generator import generate_sid, validate_sid_format
from ..models.session_model import FileSession, SessionStatus, SessionType
from ..repositories.intake_repository import get_intake_repository

logger = get_logger(__name__)


class SessionService:
    """Session management service for file intake."""
    
    def __init__(self, config=None):
        """
        Initialize session service.
        
        Args:
            config: Configuration object
        """
        self.config = config or get_config()
        self.repository = get_intake_repository(self.config)
        
        # Session configuration
        self.session_timeout = self.config.session.timeout_hours or 24
        self.max_files_per_session = self.config.session.max_files_per_session or 10
        self.max_file_size = self.config.session.max_file_size or 10485760  # 10MB
        
        logger.info("Session service initialized")
    
    def create_session(self, user_id: str, session_type: SessionType = SessionType.FILE_UPLOAD, 
                      metadata: Optional[Dict[str, Any]] = None) -> FileSession:
        """
        Create a new session.
        
        Args:
            user_id: User identifier
            session_type: Session type
            metadata: Optional session metadata
            
        Returns:
            FileSession: Created session
        """
        try:
            logger.info(f"Creating new session for user: {user_id}")
            
            # Generate session ID
            sid = generate_sid()
            
            # Calculate expiry time
            expires_at = datetime.utcnow() + timedelta(hours=self.session_timeout)
            
            # Create session
            session = FileSession(
                session_id=sid,
                user_id=user_id,
                session_type=session_type,
                expires_at=expires_at,
                metadata=metadata or {},
                max_file_size=self.max_file_size,
                max_files_per_session=self.max_files_per_session
            )
            
            # Save session
            self.repository.save_session(session)
            
            logger.info(f"Session created successfully: {sid}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to create session for user {user_id}: {str(e)}")
            raise RuntimeError(f"Failed to create session: {str(e)}")
    
    def get_session(self, sid: str) -> Optional[FileSession]:
        """
        Get session by ID.
        
        Args:
            sid: Session ID
            
        Returns:
            FileSession or None
        """
        try:
            if not validate_sid_format(sid):
                logger.warning(f"Invalid session ID format: {sid}")
                return None
            
            session = self.repository.get_session(sid)
            if not session:
                return None
            
            # Check if session is expired
            if session.is_expired():
                logger.warning(f"Session expired: {sid}")
                self.mark_session_expired(sid)
                return None
            
            return session
            
        except Exception as e:
            logger.error(f"Failed to get session {sid}: {str(e)}")
            return None
    
    def get_active_sessions(self, user_id: str) -> List[FileSession]:
        """
        Get active sessions for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of active sessions
        """
        try:
            sessions = self.repository.get_sessions_by_user(user_id)
            active_sessions = []
            
            for session in sessions:
                if not session.is_expired() and session.status == SessionStatus.ACTIVE:
                    active_sessions.append(session)
            
            return active_sessions
            
        except Exception as e:
            logger.error(f"Failed to get active sessions for user {user_id}: {str(e)}")
            return []
    
    def update_session_progress(self, sid: str, progress: int) -> bool:
        """
        Update session progress.
        
        Args:
            sid: Session ID
            progress: Progress percentage (0-100)
            
        Returns:
            bool: True if updated successfully
        """
        try:
            session = self.get_session(sid)
            if not session:
                logger.warning(f"Session not found: {sid}")
                return False
            
            session.update_progress(progress)
            self.repository.update_session(session)
            
            logger.info(f"Session progress updated: {sid} - {progress}%")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update session progress {sid}: {str(e)}")
            return False
    
    def add_file_to_session(self, sid: str, qid: str, filename: str, file_size: int) -> bool:
        """
        Add a file to a session.
        
        Args:
            sid: Session ID
            qid: File QID
            filename: Original filename
            file_size: File size in bytes
            
        Returns:
            bool: True if added successfully
        """
        try:
            session = self.get_session(sid)
            if not session:
                logger.warning(f"Session not found: {sid}")
                return False
            
            # Check file size limit
            if file_size > session.max_file_size:
                logger.warning(f"File size exceeds limit: {file_size} > {session.max_file_size}")
                return False
            
            # Check file count limit
            if session.file_count >= session.max_files_per_session:
                logger.warning(f"Session file count exceeded: {session.file_count} >= {session.max_files_per_session}")
                return False
            
            # Add file to session
            self.repository.add_file_to_session(sid, qid, filename, file_size)
            
            # Update session file count
            session.file_count += 1
            session.update_progress(int((session.processed_files / session.file_count) * 100))
            self.repository.update_session(session)
            
            logger.info(f"File added to session: {sid} - {qid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add file to session {sid}: {str(e)}")
            return False
    
    def mark_session_completed(self, sid: str) -> bool:
        """
        Mark a session as completed.
        
        Args:
            sid: Session ID
            
        Returns:
            bool: True if marked successfully
        """
        try:
            session = self.get_session(sid)
            if not session:
                logger.warning(f"Session not found: {sid}")
                return False
            
            session.mark_completed()
            self.repository.update_session(session)
            
            logger.info(f"Session completed: {sid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to mark session completed {sid}: {str(e)}")
            return False
    
    def mark_session_failed(self, sid: str, error_message: str) -> bool:
        """
        Mark a session as failed.
        
        Args:
            sid: Session ID
            error_message: Error message
            
        Returns:
            bool: True if marked successfully
        """
        try:
            session = self.get_session(sid)
            if not session:
                logger.warning(f"Session not found: {sid}")
                return False
            
            session.mark_failed(error_message)
            self.repository.update_session(session)
            
            logger.info(f"Session failed: {sid} - {error_message}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to mark session failed {sid}: {str(e)}")
            return False
    
    def mark_session_expired(self, sid: str) -> bool:
        """
        Mark a session as expired.
        
        Args:
            sid: Session ID
            
        Returns:
            bool: True if marked successfully
        """
        try:
            session = self.get_session(sid)
            if not session:
                logger.warning(f"Session not found: {sid}")
                return False
            
            session.status = SessionStatus.EXPIRED
            session.updated_at = datetime.utcnow()
            self.repository.update_session(session)
            
            logger.info(f"Session expired: {sid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to mark session expired {sid}: {str(e)}")
            return False
    
    def extend_session_expiry(self, sid: str, hours: int = 24) -> bool:
        """
        Extend session expiry time.
        
        Args:
            sid: Session ID
            hours: Hours to extend
            
        Returns:
            bool: True if extended successfully
        """
        try:
            session = self.get_session(sid)
            if not session:
                logger.warning(f"Session not found: {sid}")
                return False
            
            session.extend_expiry(hours)
            self.repository.update_session(session)
            
            logger.info(f"Session expiry extended: {sid} +{hours}h")
            return True
            
        except Exception as e:
            logger.error(f"Failed to extend session expiry {sid}: {str(e)}")
            return False
    
    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions.
        
        Returns:
            int: Number of sessions cleaned up
        """
        try:
            expired_sessions = self.repository.get_expired_sessions()
            cleaned_count = 0
            
            for session in expired_sessions:
                if self.mark_session_expired(session.session_id):
                    cleaned_count += 1
            
            logger.info(f"Cleaned up {cleaned_count} expired sessions")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {str(e)}")
            return 0
    
    def get_session_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get session statistics for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict with session statistics
        """
        try:
            sessions = self.repository.get_sessions_by_user(user_id)
            
            stats = {
                "total_sessions": len(sessions),
                "active_sessions": 0,
                "completed_sessions": 0,
                "failed_sessions": 0,
                "expired_sessions": 0,
                "total_files": 0,
                "processed_files": 0,
                "failed_files": 0
            }
            
            for session in sessions:
                stats["total_files"] += session.file_count
                stats["processed_files"] += session.processed_files
                stats["failed_files"] += session.failed_files
                
                if session.status == SessionStatus.ACTIVE:
                    stats["active_sessions"] += 1
                elif session.status == SessionStatus.COMPLETED:
                    stats["completed_sessions"] += 1
                elif session.status == SessionStatus.FAILED:
                    stats["failed_sessions"] += 1
                elif session.status == SessionStatus.EXPIRED:
                    stats["expired_sessions"] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get session statistics for user {user_id}: {str(e)}")
            return {}
    
    def validate_session_for_upload(self, sid: str, file_size: int) -> bool:
        """
        Validate if a session can accept a file upload.
        
        Args:
            sid: Session ID
            file_size: File size in bytes
            
        Returns:
            bool: True if valid
        """
        try:
            session = self.get_session(sid)
            if not session:
                return False
            
            # Check session status
            if session.status != SessionStatus.ACTIVE:
                return False
            
            # Check file size
            if file_size > session.max_file_size:
                return False
            
            # Check file count
            if session.file_count >= session.max_files_per_session:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate session {sid}: {str(e)}")
            return False


# Global session service instance
_session_service = None


def get_session_service(config=None) -> SessionService:
    """Get session service instance."""
    global _session_service
    if _session_service is None:
        _session_service = SessionService(config)
    return _session_service


def create_session(user_id: str, session_type: SessionType = SessionType.FILE_UPLOAD, 
                  metadata: Optional[Dict[str, Any]] = None) -> FileSession:
    """Create a new session."""
    service = get_session_service()
    return service.create_session(user_id, session_type, metadata)


def get_session(sid: str) -> Optional[FileSession]:
    """Get session by ID."""
    service = get_session_service()
    return service.get_session(sid)


def get_active_sessions(user_id: str) -> List[FileSession]:
    """Get active sessions for a user."""
    service = get_session_service()
    return service.get_active_sessions(user_id)