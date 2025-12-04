# file_intake/repositories/intake_repository.py
from sqlalchemy.orm import Session
from backend_app.file_intake.models.file_intake_model import FileIntake

class IntakeRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_record(self, qid, source, original_filename, filesize=None, sid=None, user_id=None, mime_type=None, metadata=None):
        rec = FileIntake(
            qid=qid, source=source, original_filename=original_filename,
            filesize=filesize, sid=sid, user_id=user_id, mime_type=mime_type, status="queued", metadata=metadata or {}
        )
        self.db.add(rec)
        self.db.commit()
        self.db.refresh(rec)
        return rec

    def update_status(self, qid, status, storage_path=None, sanitized_filename=None, error_message=None, metadata=None):
        rec = self.db.query(FileIntake).filter(FileIntake.qid==qid).first()
        if not rec:
            return None
        rec.status = status
        if storage_path is not None:
            rec.storage_path = storage_path
        if sanitized_filename is not None:
            rec.sanitized_filename = sanitized_filename
        if error_message is not None:
            rec.error_message = error_message
        if metadata:
            rec.metadata = {**(rec.metadata or {}), **metadata}
        self.db.add(rec)
        self.db.commit()
        self.db.refresh(rec)
        return rec

    def get_by_qid(self, qid):
        return self.db.query(FileIntake).filter(FileIntake.qid==qid).first()
    
    def get_record(self, qid):
        return self.get_by_qid(qid)
    
    def get_parsed_output(self, qid):
        rec = self.get_by_qid(qid)
        return rec.metadata.get('parsed_output') if rec else None
    
    def get_processing_history(self, qid):
        rec = self.get_by_qid(qid)
        return rec.metadata.get('processing_history', []) if rec else []
    
    def update_archive_metadata(self, qid, archive_metadata):
        rec = self.get_by_qid(qid)
        if not rec:
            return None
        rec.metadata = {**(rec.metadata or {}), 'archive_metadata': archive_metadata}
        self.db.add(rec)
        self.db.commit()
        self.db.refresh(rec)
        return rec
    
    def save_processing_report(self, qid, report):
        rec = self.get_by_qid(qid)
        if not rec:
            return None
        rec.metadata = {**(rec.metadata or {}), 'processing_report': report}
        self.db.add(rec)
        self.db.commit()
        self.db.refresh(rec)
        return rec
    
    def set_error(self, qid, error_message):
        return self.update_status(qid, "failed", error_message=error_message)
    
    def update_profile_id(self, qid, profile_id):
        rec = self.get_by_qid(qid)
        if not rec:
            return None
        rec.profile_id = profile_id
        self.db.add(rec)
        self.db.commit()
        self.db.refresh(rec)
        return rec
    
    def get_records_by_status(self, status):
        return self.db.query(FileIntake).filter(FileIntake.status==status).all()
    
    def get_old_archives(self, cutoff_date):
        return self.db.query(FileIntake).filter(
            FileIntake.status == "archived",
            FileIntake.updated_at < cutoff_date
        ).all()