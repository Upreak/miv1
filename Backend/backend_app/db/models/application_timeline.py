"""
Application Timeline Model
Logs history of status changes for a specific application.
"""
from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from backend_app.db.connection import Base


class ApplicationTimeline(Base):
    """Application timeline model for status change history"""
    
    __tablename__ = "application_timeline"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign key to application
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id"))
    
    # Status change details
    previous_status = Column(String(100))
    new_status = Column(String(100))
    changed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    remarks = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ApplicationTimeline(id={self.id}, application_id={self.application_id}, changed_by={self.changed_by})>"