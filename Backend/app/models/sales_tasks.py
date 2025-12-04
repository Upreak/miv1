from sqlalchemy import Column, String, TIMESTAMP, DATE, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.core.db import Base
import uuid

class SalesTask(Base):
    __tablename__ = "sales_tasks"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    lead_id = Column(PG_UUID(as_uuid=True), nullable=False)  # FK -> leads.id
    title = Column(String, nullable=False)
    is_completed = Column(String)  # Boolean stored as string
    due_date = Column(DATE)
    assigned_to = Column(PG_UUID(as_uuid=True), nullable=False)  # FK -> users.id