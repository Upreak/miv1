from sqlalchemy import Column, String, Boolean, TIMESTAMP, Enum, UUID, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.core.db import Base
import uuid

class User(Base):
    __tablename__ = "users"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum('ADMIN', 'RECRUITER', 'SALES', 'CANDIDATE', 'MANAGER', name='user_roles'), nullable=False)
    full_name = Column(String, nullable=False)
    avatar_url = Column(String)
    status = Column(Enum('Active', 'Inactive', name='user_status'), default='Active')
    is_verified = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    last_login = Column(TIMESTAMP)
    last_active = Column(TIMESTAMP)