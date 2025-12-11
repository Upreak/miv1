"""
Chat Messages Model
Stores the transcript for the Live Chat Co-Pilot.
"""
from sqlalchemy import Column, String, Text, TIMESTAMP, Enum, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from backend_app.db.connection import Base


class ChatMessage(Base):
    """Chat messages model for live chat transcripts"""
    
    __tablename__ = "chat_messages"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign key to application (context of the chat)
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id"))
    
    # Message details
    sender_type = Column(Enum('CANDIDATE', 'BOT', 'RECRUITER', name='sender_type_enum'))
    message_text = Column(Text, nullable=False)
    sent_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    is_read = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<ChatMessage(id={self.id}, application_id={self.application_id}, sender={self.sender_type})>"