"""
Leads Model
"""
from sqlalchemy import Column, String, Text, DATE, DECIMAL, TIMESTAMP, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from backend_app.db.connection import Base


class Lead(Base):
    """Leads model for CRM"""
    
    __tablename__ = "leads"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign key to owner
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Lead details
    company_name = Column(String(255), nullable=False)
    contact_person = Column(String(255), nullable=False)
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(20))
    
    # Lead status and details
    status = Column(Enum('New', 'Contacted', 'Qualified', 'Proposal', 'Negotiation', 'Converted', 'Lost', name='lead_status_enum'), default='New')
    service_type = Column(Enum('Permanent', 'Contract', 'RPO', 'Executive Search', name='service_type_enum'))
    estimated_value = Column(DECIMAL(12, 2))
    probability = Column(Integer)  # 0-100
    expected_close_date = Column(DATE)
    next_follow_up = Column(TIMESTAMP(timezone=True))
    source = Column(String(255))
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Lead(id={self.id}, company={self.company_name}, status={self.status})>"