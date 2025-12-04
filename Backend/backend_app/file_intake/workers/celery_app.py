# file_intake/workers/celery_app.py
from celery import Celery
import os

CELERY_BROKER = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

celery_app = Celery("file_intake", broker=CELERY_BROKER, backend=CELERY_BACKEND)
celery_app.conf.update(task_acks_late=True, worker_prefetch_multiplier=1)