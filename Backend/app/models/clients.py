from sqlalchemy import Column, String, TIMESTAMP, DATE, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from app.core.db import Base
import uuid

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    billing_address = Column(String)
    status = Column(String)  # 'Active', 'Inactive', 'Blacklisted'
    corporate_identity = Column(JSONB)  # { "gst": "...", "pan": "..." }
    contract_start_date = Column(DATE)
    contract_end_date = Column(DATE)
    account_manager_id = Column(PG_UUID(as_uuid=True), nullable=False)  # FK -> users.id
    created_from_lead_id = Column(PG_UUID(as_uuid=True))  # FK -> leads.id, Nullable