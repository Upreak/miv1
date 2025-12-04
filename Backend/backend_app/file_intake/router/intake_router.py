# file_intake/router/intake_router.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from backend_app.db import get_db
from backend_app.file_intake.utils.qid_generator import generate_qid
from backend_app.file_intake.repositories.intake_repository import IntakeRepository
from backend_app.file_intake.services.storage_service import generate_presigned_url
from backend_app.file_intake.services.event_publisher import publish
from pathlib import Path

router = APIRouter(prefix="/intake", tags=["intake"])

@router.post("/initiate-upload")
def initiate_upload(payload: dict, db: Session = Depends(get_db), user=Depends(lambda: None)):
    filename = payload.get("filename")
    mime = payload.get("mime")
    size = payload.get("size")
    sid = payload.get("sid")
    source = payload.get("source", "web")
    qid = generate_qid()
    repo = IntakeRepository(db)
    rec = repo.create_record(qid=qid, source=source, original_filename=filename, filesize=size, sid=sid, user_id=(user and user["sub"]), mime_type=mime)
    presigned = generate_presigned_url(qid, filename)
    return {"qid": qid, "upload": presigned}

@router.post("/complete-upload")
def complete_upload(payload: dict, db: Session = Depends(get_db)):
    qid = payload.get("qid")
    storage_path = payload.get("storage_path")
    repo = IntakeRepository(db)
    rec = repo.update_status(qid, "quarantined", storage_path=storage_path)
    if not rec:
        raise HTTPException(status_code=404, detail="QID not found")
    publish("virus_scan_requested", {"qid": qid})
    return {"ok": True, "qid": qid}

# Optional local server-endpoint for direct upload to server (if USE_S3 = false)
@router.post("/upload-to-server")
def upload_to_server(file: UploadFile = File(...), qid: str = None, db: Session = Depends(get_db)):
    if not qid:
        raise HTTPException(status_code=400, detail="Missing qid")
    dest_dir = Path("/data/quarantine") / qid
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / file.filename
    with dest.open("wb") as f:
        f.write(file.file.read())
    repo = IntakeRepository(db)
    repo.update_status(qid, "quarantined", storage_path=str(dest))
    publish("virus_scan_requested", {"qid": qid})
    return {"ok": True, "qid": qid}