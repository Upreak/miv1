from sqlalchemy import Column, String, TIMESTAMP, DECIMAL, DATE, Integer, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.core.db import Base
import uuid

class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    owner_id = Column(PG_UUID(as_uuid=True), nullable=False)  # FK -> users.id
    company_name = Column(String, nullable=False)
    contact_person = Column(String, nullable=False)
    contact_email = Column(String, nullable=False)
    contact_phone = Column(String, nullable=False)
    status = Column(String)  # 'New', 'Contacted', 'Qualified', 'Proposal', 'Negotiation', 'Converted', 'Lost'
    service_type = Column(String)  # 'Permanent', 'Contract', 'RPO', 'Executive Search'
    estimated_value = Column(DECIMAL)
    probability = Column(Integer)  # 0-100
    expected_close_date = Column(DATE)
    next_follow_up = Column(TIMESTAMP)
    source = Column(String)