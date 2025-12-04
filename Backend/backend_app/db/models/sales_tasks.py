"""
Sales Tasks Model
Tracks tasks associated with leads.
"""
from sqlalchemy import Column, String, Boolean, DATE, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from backend_app.db.connection import Base


class SalesTask(Base):
    """Sales tasks model for lead tasks"""
    
    __tablename__ = "sales_tasks"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign key to lead
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"))
    
    # Task details
    title = Column(String(500), nullable=False)
    is_completed = Column(Boolean, default=False)
    due_date = Column(DATE)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<SalesTask(id={self.id}, title={self.title}, lead_id={self.lead_id})>"