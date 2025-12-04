from sqlalchemy import Column, String, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.core.db import Base
import uuid

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    application_id = Column(PG_UUID(as_uuid=True), nullable=False)  # FK -> applications.id: Context of the chat (links Candidate + Job)
    sender_type = Column(String)  # 'CANDIDATE', 'BOT', 'RECRUITER'
    message_text = Column(String, nullable=False)
    sent_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    is_read = Column(String)  # Boolean stored as string