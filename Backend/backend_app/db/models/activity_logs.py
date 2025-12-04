"""
Activity Logs Model
Global audit trail and dashboard feed.
"""
from sqlalchemy import Column, String, Text, TIMESTAMP, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from backend_app.db.connection import Base


class ActivityLog(Base):
    """Activity logs model for audit trail"""
    
    __tablename__ = "activity_logs"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign key to user (nullable for System events)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Action details
    action_type = Column(String(100), nullable=False)  # 'CREATED_JOB', 'APPLIED', 'CONVERTED_LEAD', 'LOGIN', 'USER_UPDATE'
    severity = Column(Enum('INFO', 'WARN', 'ERROR', 'SUCCESS', name='severity_enum'))
    entity_id = Column(UUID(as_uuid=True))  # ID of the job/application/lead
    description = Column(Text, nullable=False)  # e.g., "John created a new job: React Dev"
    
    # Metadata
    ip_address = Column(String(50))  # Request IP for security auditing
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ActivityLog(id={self.id}, action_type={self.action_type}, user_id={self.user_id})>"