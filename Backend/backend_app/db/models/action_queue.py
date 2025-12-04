"""
Action Queue Model
Manages the recruiter's "My Action Queue" panel.
"""
from sqlalchemy import Column, String, Text, TIMESTAMP, Boolean, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from backend_app.db.connection import Base


class ActionQueue(Base):
    """Action queue model for recruiter tasks"""
    
    __tablename__ = "action_queue"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign key to user (recruiter)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Task details
    type = Column(Enum('NEW_MATCHES', 'CHAT_FOLLOWUP', 'NO_RESPONSE', 'PARSE_FAILURE', 'INTERVENTION_NEEDED', name='action_type_enum'))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    priority = Column(Enum('High', 'Medium', 'Low', name='priority_enum'))
    
    # Related entities
    related_job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=True)
    related_candidate_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Status
    is_dismissed = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ActionQueue(id={self.id}, user_id={self.user_id}, type={self.type}, title={self.title})>"