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
from backend_app.db.models.job_prescreen_questions import JobPrescreenQuestion
from backend_app.db.models.prescreen_answers import PrescreenAnswer
from backend_app.db.models.job_faq import JobFAQ
# Chatbot models
from backend_app.chatbot.models.session_model import Session
from backend_app.chatbot.models.message_log_model import MessageLog

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
    "SalesTask",
    "JobPrescreenQuestion",
    "PrescreenAnswer",
    "JobFAQ",
    # Chatbot models
    "Session",
    "MessageLog"
]