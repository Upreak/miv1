"""
Session Model for Chatbot/Co-Pilot Module

Defines the Session model that stores persistent conversation state
for users across WhatsApp, Telegram, and Web platforms.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, DateTime, JSON, Enum, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum as PyEnum

Base = declarative_base()

class UserRole(PyEnum):
    """User roles in the chatbot system"""
    CANDIDATE = "candidate"
    RECRUITER = "recruiter"
    UNKNOWN = "unknown"

class ConversationState(PyEnum):
    """Conversation states for different workflows"""
    ONBOARDING = "onboarding"
    AWAITING_RESUME = "awaiting_resume"
    PROFILE_READY = "profile_ready"
    RECRUITER_FLOW = "recruiter_flow"
    CANDIDATE_FLOW = "candidate_flow"
    JOB_CREATION = "job_creation"
    MATCHING = "matching"
    APPLICATION = "application"
    IDLE = "idle"

class Session(Base):
    """
    Session model for storing conversation state
    
    Each user on WhatsApp/Telegram/Web needs a persistent conversation state.
    SID contains:
    - sid: Unique session identifier
    - user_id: User identifier from the main system
    - channel: Platform (whatsapp/telegram/web)
    - channel_user_id: Platform-specific user ID (phone/telegram_id)
    - role: User role (candidate/recruiter/unknown)
    - state: Current conversation state
    - context: JSON context data
    - created_at: Session creation time
    - updated_at: Last update time
    """
    
    __tablename__ = "chatbot_sessions"
    
    sid = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), nullable=True, index=True)
    channel = Column(String(20), nullable=False, index=True)  # whatsapp/telegram/web
    channel_user_id = Column(String(100), nullable=False, index=True)
    role = Column(Enum(UserRole), default=UserRole.UNKNOWN, nullable=False)
    state = Column(Enum(ConversationState), default=ConversationState.ONBOARDING, nullable=False)
    context = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Additional metadata
    last_message = Column(Text, nullable=True)
    message_count = Column(Integer, default=0, nullable=False)
    
    def __repr__(self):
        return f"<Session(sid='{self.sid}', channel='{self.channel}', role='{self.role}', state='{self.state}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary"""
        return {
            'sid': self.sid,
            'user_id': self.user_id,
            'channel': self.channel,
            'channel_user_id': self.channel_user_id,
            'role': self.role.value if self.role else None,
            'state': self.state.value if self.state else None,
            'context': self.context,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_message': self.last_message,
            'message_count': self.message_count
        }
    
    def update_context(self, key: str, value: Any) -> None:
        """Update context value"""
        if not self.context:
            self.context = {}
        self.context[key] = value
        self.updated_at = datetime.utcnow()
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get context value"""
        return self.context.get(key, default) if self.context else default
    
    def set_role(self, role: UserRole) -> None:
        """Set user role"""
        self.role = role
        self.updated_at = datetime.utcnow()
    
    def set_state(self, state: ConversationState) -> None:
        """Set conversation state"""
        self.state = state
        self.updated_at = datetime.utcnow()
    
    def increment_message_count(self) -> None:
        """Increment message count"""
        self.message_count += 1
        self.updated_at = datetime.utcnow()