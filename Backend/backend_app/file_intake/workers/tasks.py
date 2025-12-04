# file_intake/workers/tasks.py
from .celery_app import celery_app
from backend_app.file_intake.repositories.intake_repository import IntakeRepository
from backend_app.db import SessionLocal
from backend_app.file_intake.services.virus_scan_service import scan_file
from backend_app.file_intake.services.sanitizer_service import sanitize_and_normalize
from backend_app.file_intake.services.extraction_service import extract_text_for_qid
from backend_app.file_intake.services.brain_parse_service import parse_text_to_profile
from backend_app.file_intake.services.event_publisher import publish

@celery_app.task(name="file_intake.tasks.virus_scan_task")
def virus_scan_task(payload: dict):
    qid = payload["qid"]
    db = SessionLocal()
    repo = IntakeRepository(db)
    rec = repo.get_by_qid(qid)
    if not rec or not rec.storage_path:
        repo.update_status(qid, "failed", error_message="missing_storage_path")
        return
    result = scan_file(rec.storage_path)
    if not result["clean"]:
        repo.update_status(qid, "infected", error_message=result.get("virus_name"))
        return
    repo.update_status(qid, "clean")
    publish("sanitize_requested", {"qid": qid})

@celery_app.task(name="file_intake.tasks.sanitize_task")
def sanitize_task(payload: dict):
    qid = payload["qid"]
    db = SessionLocal()
    repo = IntakeRepository(db)
    rec = repo.get_by_qid(qid)
    new_path = sanitize_and_normalize(rec.storage_path)
    repo.update_status(qid, "sanitized", storage_path=new_path)
    publish("extract_requested", {"qid": qid})

@celery_app.task(name="file_intake.tasks.extract_task")
def extract_task(payload: dict):
    qid = payload["qid"]
    db = SessionLocal()
    repo = IntakeRepository(db)
    rec = repo.get_by_qid(qid)
    res = extract_text_for_qid(rec.storage_path, metadata={"qid": qid})
    if not res["success"]:
        repo.update_status(qid, "failed", error_message="extraction_failed")
        return
    # store extracted text in metadata (or separate table as you prefer)
    repo.update_status(qid, "extracted", metadata={"extracted_text": res["text"], "extract_module": res.get("module"), "extract_score": res.get("score")})
    publish("parse_requested", {"qid": qid, "extracted_text": res["text"]})

@celery_app.task(name="file_intake.tasks.parse_task")
def parse_task(payload: dict):
    qid = payload["qid"]
    text = payload.get("extracted_text", "")
    parsed = parse_text_to_profile(text, tag="resume")
    db = SessionLocal()
    repo = IntakeRepository(db)
    repo.update_status(qid, "parsed", metadata={"parsed": parsed})
    publish("finalize_requested", {"qid": qid, "parsed": parsed})

@celery_app.task(name="file_intake.tasks.finalize_task")
def finalize_task(payload: dict):
    qid = payload["qid"]
    db = SessionLocal()
    repo = IntakeRepository(db)
    # here you should call your profile writer to persist parsed data (omitted: call profile writer)
    repo.update_status(qid, "completed")