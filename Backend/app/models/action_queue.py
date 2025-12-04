from sqlalchemy import Column, String, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.core.db import Base
import uuid

class ActionQueue(Base):
    __tablename__ = "action_queue"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(PG_UUID(as_uuid=True), nullable=False)  # FK -> users.id: The recruiter who needs to see this
    type = Column(String)  # 'NEW_MATCHES', 'CHAT_FOLLOWUP', 'NO_RESPONSE', 'PARSE_FAILURE', 'INTERVENTION_NEEDED'
    title = Column(String)
    description = Column(String)
    priority = Column(String)  # 'High', 'Medium', 'Low'
    related_job_id = Column(PG_UUID(as_uuid=True))  # FK -> jobs.id, Nullable
    related_candidate_id = Column(PG_UUID(as_uuid=True))  # FK -> users.id, Nullable
    is_dismissed = Column(String)  # Boolean stored as string
    created_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))