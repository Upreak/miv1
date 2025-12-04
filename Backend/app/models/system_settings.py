from sqlalchemy import Column, String, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.db import Base
import uuid

class SystemSettings(Base):
    __tablename__ = "system_settings"
    
    key = Column(String, primary_key=True)
    value = Column(JSONB, nullable=False)
    description = Column(String)
    updated_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))
    updated_by = Column(PG_UUID(as_uuid=True), nullable=True)