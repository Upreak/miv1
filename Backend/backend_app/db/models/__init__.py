"""
Database Models Package
"""
# Import all models to ensure they are registered with SQLAlchemy
from backend_app.db.models.users import User
from backend_app.db.models.system_settings import SystemSettings
from backend_app.db.models.external_job_postings import ExternalJobPosting
from backend_app.db.models.jobs import Job
from backend_app.db.models.candidate_profiles import CandidateProfile
from backend_app.db.models.candidate_work_history import CandidateWorkHistory
from backend_app.db.models.applications import Application
from backend_app.db.models.application_timeline import ApplicationTimeline
from backend_app.db.models.action_queue import ActionQueue
from backend_app.db.models.chat_messages import ChatMessage
from backend_app.db.models.activity_logs import ActivityLog
from backend_app.db.models.clients import Client
from backend_app.db.models.leads import Lead
from backend_app.db.models.sales_tasks import SalesTask

__all__ = [
    "User",
    "SystemSettings", 
    "ExternalJobPosting",
    "Job",
    "CandidateProfile",
    "CandidateWorkHistory",
    "Application",
    "ApplicationTimeline",
    "ActionQueue",
    "ChatMessage",
    "ActivityLog",
    "Client",
    "Lead",
    "SalesTask"
]