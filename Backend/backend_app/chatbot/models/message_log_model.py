"""
Message Log Model for Chatbot/Co-Pilot Module

Defines the MessageLog model for storing conversation history
and tracking all interactions across different platforms.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, DateTime, JSON, Enum, Text, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

Base = declarative_base()

class MessageType(PyEnum):
    """Types of messages in the conversation"""
    USER = "user"
    BOT = "bot"
    SYSTEM = "system"
    ERROR = "error"

class MessageDirection(PyEnum):
    """Message direction"""
    INBOUND = "inbound"
    OUTBOUND = "outbound"

class MessageLog(Base):
    """
    Message log model for storing conversation history
    
    Tracks all messages across WhatsApp, Telegram, and Web platforms:
    - id: Unique message identifier
    - sid: Session identifier (foreign key)
    - message_id: Platform-specific message ID
    - type: Message type (user/bot/system/error)
    - direction: Message direction (inbound/outbound)
    - content: Message content
    - metadata: Additional message data
    - timestamp: Message timestamp
    - platform: Platform where message was sent/received
    """
    
    __tablename__ = "chatbot_message_logs"
    
    id = Column(String(36), primary_key=True, index=True)
    sid = Column(String(36), ForeignKey("chatbot_sessions.sid"), nullable=False, index=True)
    message_id = Column(String(100), nullable=True, index=True)  # Platform-specific message ID
    type = Column(Enum(MessageType), default=MessageType.USER, nullable=False)
    direction = Column(Enum(MessageDirection), default=MessageDirection.INBOUND, nullable=False)
    content = Column(Text, nullable=False)
    message_metadata = Column(JSON, default=dict, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    platform = Column(String(20), nullable=False)  # whatsapp/telegram/web
    
    # Additional fields for better tracking
    processed = Column(String(20), nullable=True)  # success/failed/pending
    response_time = Column(Integer, nullable=True)  # milliseconds
    skill_used = Column(String(50), nullable=True)  # Which skill handled this message
    
    # Relationship with session
    session = relationship("Session", backref="messages")
    
    def __repr__(self):
        return f"<MessageLog(id='{self.id}', sid='{self.sid}', type='{self.type}', direction='{self.direction}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message log to dictionary"""
        return {
            'id': self.id,
            'sid': self.sid,
            'message_id': self.message_id,
            'type': self.type.value if self.type else None,
            'direction': self.direction.value if self.direction else None,
            'content': self.content,
            'metadata': self.message_metadata,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'platform': self.platform,
            'processed': self.processed,
            'response_time': self.response_time,
            'skill_used': self.skill_used
        }
    
    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata value"""
        if not self.message_metadata:
            self.message_metadata = {}
        self.message_metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value"""
        return self.message_metadata.get(key, default) if self.message_metadata else default
    
    def mark_processed(self, status: str, response_time: Optional[int] = None) -> None:
        """Mark message as processed"""
        self.processed = status
        if response_time is not None:
            self.response_time = response_time
    
    def set_skill_used(self, skill_name: str) -> None:
        """Set which skill handled this message"""
        self.skill_used = skill_name