# file_intake/telegram_intake.py
from fastapi import Request, HTTPException, UploadFile, File
from backend_app.file_intake.utils.qid_generator import generate_qid
from backend_app.file_intake.repositories.intake_repository import IntakeRepository
from backend_app.file_intake.services.storage_service import generate_presigned_url
from backend_app.file_intake.services.event_publisher import publish
from backend_app.db import SessionLocal
import logging

logger = logging.getLogger(__name__)

async def handle_telegram_document(request: Request, db: Session):
    """Handle Telegram document uploads"""
    try:
        # Parse Telegram webhook payload
        payload = await request.json()
        
        # Extract document info from Telegram message
        message = payload.get("message", {})
        if not message or "document" not in message:
            raise HTTPException(status_code=400, detail="Not a document message")
        
        doc = message["document"]
        filename = doc.get("file_name")
        mime_type = doc.get("mime_type")
        file_id = doc.get("file_id")
        size = doc.get("file_size", 0)
        sid = str(message.get("message_id"))  # Telegram message ID as session ID
        
        # Generate QID and create intake record
        qid = generate_qid()
        repo = IntakeRepository(db)
        rec = repo.create_record(
            qid=qid, 
            source="telegram", 
            original_filename=filename, 
            filesize=size, 
            sid=sid, 
            mime_type=mime_type,
            metadata={"telegram_file_id": file_id}
        )
        
        # Generate presigned URL for S3 upload
        presigned = generate_presigned_url(qid, filename)
        
        logger.info(f"Telegram document intake: {qid} - {filename}")
        
        return {
            "status": "success",
            "qid": qid,
            "upload": presigned,
            "message": "Document queued for processing"
        }
        
    except Exception as e:
        logger.error(f"Telegram intake error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process Telegram document")

async def handle_telegram_text(request: Request, db: Session):
    """Handle Telegram text messages (could be resume text)"""
    try:
        payload = await request.json()
        
        # Extract text from Telegram message
        message = payload.get("message", {})
        if not message or "text" not in message:
            raise HTTPException(status_code=400, detail="Not a text message")
        
        text = message.get("text")
        sid = str(message.get("message_id"))
        
        # For text messages, we could create a text intake record
        # This would bypass the file pipeline and go directly to text extraction
        qid = generate_qid()
        repo = IntakeRepository(db)
        rec = repo.create_record(
            qid=qid, 
            source="telegram_text", 
            original_filename="telegram_text.txt", 
            sid=sid, 
            metadata={"text_content": text}
        )
        
        logger.info(f"Telegram text intake: {qid} - {len(text)} chars")
        
        return {
            "status": "success",
            "qid": qid,
            "message": "Text message queued for processing"
        }
        
    except Exception as e:
        logger.error(f"Telegram text intake error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process Telegram text")

async def handle_telegram_photo(request: Request, db: Session):
    """Handle Telegram photo uploads (resume images)"""
    try:
        payload = await request.json()
        
        # Extract photo info from Telegram message
        message = payload.get("message", {})
        if not message or "photo" not in message:
            raise HTTPException(status_code=400, detail="Not a photo message")
        
        photos = message["photo"]
        # Use the highest resolution photo
        photo = max(photos, key=lambda p: p.get("file_size", 0))
        file_id = photo.get("file_id")
        sid = str(message.get("message_id"))
        
        # Generate QID and create intake record
        qid = generate_qid()
        repo = IntakeRepository(db)
        rec = repo.create_record(
            qid=qid, 
            source="telegram_photo", 
            original_filename="telegram_resume.jpg", 
            sid=sid, 
            mime_type="image/jpeg",
            metadata={"telegram_file_id": file_id, "photo_info": photo}
        )
        
        # Generate presigned URL for S3 upload
        presigned = generate_presigned_url(qid, "telegram_resume.jpg")
        
        logger.info(f"Telegram photo intake: {qid}")
        
        return {
            "status": "success",
            "qid": qid,
            "upload": presigned,
            "message": "Photo queued for processing"
        }
        
    except Exception as e:
        logger.error(f"Telegram photo intake error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process Telegram photo")