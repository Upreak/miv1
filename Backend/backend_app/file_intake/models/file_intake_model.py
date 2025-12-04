# file_intake/models/file_intake_model.py
import uuid
from sqlalchemy import Column, String, Integer, Text, BigInteger, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class FileIntake(Base):
    __tablename__ = "file_intake_queue"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    qid = Column(String, unique=True, nullable=False, index=True)
    sid = Column(String, nullable=True)
    source = Column(String, nullable=False)  # web|whatsapp|telegram|email|api
    user_id = Column(String, nullable=True)
    original_filename = Column(String, nullable=True)
    sanitized_filename = Column(String, nullable=True)
    storage_path = Column(String, nullable=True)
    mime_type = Column(String, nullable=True)
    filesize = Column(BigInteger, nullable=True)
    status = Column(String, nullable=False, default="queued")
    error_message = Column(Text, nullable=True)
    profile_id = Column(String, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())