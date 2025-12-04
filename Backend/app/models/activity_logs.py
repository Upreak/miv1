from sqlalchemy import Column, String, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.core.db import Base
import uuid

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(PG_UUID(as_uuid=True))  # FK -> users.id, Nullable for System events
    action_type = Column(String)  # 'CREATED_JOB', 'APPLIED', 'CONVERTED_LEAD', 'LOGIN', 'USER_UPDATE'
    severity = Column(String)  # 'INFO', 'WARN', 'ERROR', 'SUCCESS'
    entity_id = Column(PG_UUID(as_uuid=True))  # ID of the job/application/lead
    description = Column(String)  # e.g., "John created a new job: React Dev"
    ip_address = Column(String)  # Request IP for security auditing
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))