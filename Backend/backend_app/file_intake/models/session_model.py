import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, DateTime, Boolean, JSON, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from ..db.base import Base


class SessionStatus(str, Enum):
    """Session status enumeration"""
    ACTIVE = "active"
    EXPIRED = "expired"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SessionType(str, Enum):
    """Session type enumeration"""
    FILE_UPLOAD = "file_upload"
    BATCH_PROCESSING = "batch_processing"
    RESUME_EXTRACTION = "resume_extraction"
    DOCUMENT_PARSING = "document_parsing"


class FileSession(Base):
    """File intake session model"""
    __tablename__ = "file_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    session_type = Column(SQLEnum(SessionType), nullable=False, default=SessionType.FILE_UPLOAD)
    status = Column(SQLEnum(SessionStatus), nullable=False, default=SessionStatus.ACTIVE)
    
    # Session metadata
    metadata = Column(JSON, nullable=True)  # Additional session-specific data
    progress = Column(Integer, default=0)  # Progress percentage (0-100)
    error_message = Column(String, nullable=True)
    
    # Timing
    created_at = Column(DateTime(timezone=True), server_default="now()")
    updated_at = Column(DateTime(timezone=True), server_default="now()", onupdate="now()")
    expires_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Processing results
    processing_results = Column(JSON, nullable=True)  # Results from processing steps
    file_count = Column(Integer, default=0)
    processed_files = Column(Integer, default=0)
    failed_files = Column(Integer, default=0)
    
    # Configuration
    max_file_size = Column(Integer, nullable=True)  # Max file size in bytes
    allowed_file_types = Column(JSON, nullable=True)  # List of allowed file extensions
    max_files_per_session = Column(Integer, default=10)
    
    # Security
    is_secure = Column(Boolean, default=True)
    encryption_key = Column(String, nullable=True)
    access_token = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<FileSession(id={self.id}, session_id={self.session_id}, status={self.status})>"
    
    def is_expired(self) -> bool:
        """Check if session has expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def update_progress(self, progress: int):
        """Update session progress"""
        self.progress = max(0, min(100, progress))
        self.updated_at = datetime.utcnow()
    
    def mark_completed(self):
        """Mark session as completed"""
        self.status = SessionStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def mark_failed(self, error_message: str):
        """Mark session as failed"""
        self.status = SessionStatus.FAILED
        self.error_message = error_message
        self.updated_at = datetime.utcnow()
    
    def mark_cancelled(self):
        """Mark session as cancelled"""
        self.status = SessionStatus.CANCELLED
        self.updated_at = datetime.utcnow()
    
    def extend_expiry(self, hours: int = 24):
        """Extend session expiry"""
        if self.expires_at:
            self.expires_at = self.expires_at + timedelta(hours=hours)
        else:
            self.expires_at = datetime.utcnow() + timedelta(hours=hours)
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "session_type": self.session_type.value,
            "status": self.status.value,
            "metadata": self.metadata,
            "progress": self.progress,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "processing_results": self.processing_results,
            "file_count": self.file_count,
            "processed_files": self.processed_files,
            "failed_files": self.failed_files,
            "max_file_size": self.max_file_size,
            "allowed_file_types": self.allowed_file_types,
            "max_files_per_session": self.max_files_per_session,
            "is_secure": self.is_secure
        }