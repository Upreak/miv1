"""
Clients Model
"""
from sqlalchemy import Column, String, Text, DATE, TIMESTAMP, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from backend_app.db.connection import Base


class Client(Base):
    """Clients model for CRM"""
    
    __tablename__ = "clients"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Client details
    name = Column(String(255), nullable=False)
    billing_address = Column(Text)
    status = Column(Enum('Active', 'Inactive', 'Blacklisted', name='client_status_enum'), default='Active')
    corporate_identity = Column(String(500))  # JSONB as string for simplicity: { "gst": "...", "pan": "..." }
    
    # Contract details
    contract_start_date = Column(DATE)
    contract_end_date = Column(DATE)
    account_manager_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_from_lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id"), nullable=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Client(id={self.id}, name={self.name}, status={self.status})>"