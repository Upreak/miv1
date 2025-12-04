"""
System Settings Model
Stores global configuration and feature flags.
"""
from sqlalchemy import Column, String, TIMESTAMP, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy import ForeignKey
import uuid
from backend_app.db.connection import Base


class SystemSettings(Base):
    """System settings model for global configuration"""
    
    __tablename__ = "system_settings"
    
    # Primary key
    key = Column(String(255), primary_key=True)
    
    # Settings
    value = Column(JSONB, nullable=False)
    description = Column(Text)
    
    # Metadata
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    def __repr__(self):
        return f"<SystemSettings(key={self.key})>"