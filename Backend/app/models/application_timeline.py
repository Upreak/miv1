from sqlalchemy import Column, String, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.core.db import Base
import uuid

class ApplicationTimeline(Base):
    __tablename__ = "application_timeline"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    application_id = Column(PG_UUID(as_uuid=True), nullable=False)  # FK -> applications.id
    previous_status = Column(String)
    new_status = Column(String)
    changed_by = Column(PG_UUID(as_uuid=True))  # FK -> users.id
    remarks = Column(String)
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))