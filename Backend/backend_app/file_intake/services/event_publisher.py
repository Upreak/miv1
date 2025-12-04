# file_intake/services/event_publisher.py
from backend_app.file_intake.workers.celery_app import celery_app

def publish(event_name: str, payload: dict):
    if event_name == "virus_scan_requested":
        celery_app.send_task("file_intake.tasks.virus_scan_task", args=[payload])
    elif event_name == "sanitize_requested":
        celery_app.send_task("file_intake.tasks.sanitize_task", args=[payload])
    elif event_name == "extract_requested":
        celery_app.send_task("file_intake.tasks.extract_task", args=[payload])
    elif event_name == "parse_requested":
        celery_app.send_task("file_intake.tasks.parse_task", args=[payload])
    elif event_name == "finalize_requested":
        celery_app.send_task("file_intake.tasks.finalize_task", args=[payload])
    else:
        celery_app.send_task("file_intake.tasks.generic_task", args=[event_name, payload])