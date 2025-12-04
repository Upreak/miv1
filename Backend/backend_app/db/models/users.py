"""
User Model
Stores login credentials and global role.
"""
from sqlalchemy import Column, String, Boolean, TIMESTAMP, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from backend_app.db.connection import Base


class User(Base):
    """User model for authentication and core identity"""
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Authentication
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Profile
    role = Column(Enum('ADMIN', 'RECRUITER', 'SALES', 'CANDIDATE', 'MANAGER', name='user_role_enum'), nullable=False)
    full_name = Column(String(255), nullable=False)
    avatar_url = Column(String(500))
    
    # Status
    status = Column(Enum('Active', 'Inactive', name='user_status_enum'), default='Active')
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    last_login = Column(TIMESTAMP(timezone=True))
    last_active = Column(TIMESTAMP(timezone=True))
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"