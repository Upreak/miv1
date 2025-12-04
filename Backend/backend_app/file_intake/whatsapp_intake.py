# file_intake/whatsapp_intake.py
from fastapi import Request, HTTPException, UploadFile, File
from backend_app.file_intake.utils.qid_generator import generate_qid
from backend_app.file_intake.repositories.intake_repository import IntakeRepository
from backend_app.file_intake.services.storage_service import generate_presigned_url
from backend_app.file_intake.services.event_publisher import publish
from backend_app.db import SessionLocal
import logging

logger = logging.getLogger(__name__)

async def handle_whatsapp_document(request: Request, db: Session):
    """Handle WhatsApp document uploads"""
    try:
        # Parse WhatsApp webhook payload
        payload = await request.json()
        
        # Extract document info from WhatsApp message
        message = payload.get("entry", [{}])[0].get("changes", [{}])[0].get("messages", [{}])[0]
        if not message or message.get("type") != "document":
            raise HTTPException(status_code=400, detail="Not a document message")
        
        doc = message.get("document", {})
        filename = doc.get("filename")
        mime_type = doc.get("mime_type")
        size = doc.get("document_size", 0)
        sid = message.get("id")  # WhatsApp message ID as session ID
        
        # Generate QID and create intake record
        qid = generate_qid()
        repo = IntakeRepository(db)
        rec = repo.create_record(
            qid=qid, 
            source="whatsapp", 
            original_filename=filename, 
            filesize=size, 
            sid=sid, 
            mime_type=mime_type
        )
        
        # Generate presigned URL for S3 upload
        presigned = generate_presigned_url(qid, filename)
        
        logger.info(f"WhatsApp document intake: {qid} - {filename}")
        
        return {
            "status": "success",
            "qid": qid,
            "upload": presigned,
            "message": "Document queued for processing"
        }
        
    except Exception as e:
        logger.error(f"WhatsApp intake error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process WhatsApp document")

async def handle_whatsapp_text(request: Request, db: Session):
    """Handle WhatsApp text messages (could be resume text)"""
    try:
        payload = await request.json()
        
        # Extract text from WhatsApp message
        message = payload.get("entry", [{}])[0].get("changes", [{}])[0].get("messages", [{}])[0]
        if not message or message.get("type") != "text":
            raise HTTPException(status_code=400, detail="Not a text message")
        
        text = message.get("text", {}).get("body")
        sid = message.get("id")
        
        # For text messages, we could create a text intake record
        # This would bypass the file pipeline and go directly to text extraction
        qid = generate_qid()
        repo = IntakeRepository(db)
        rec = repo.create_record(
            qid=qid, 
            source="whatsapp_text", 
            original_filename="whatsapp_text.txt", 
            sid=sid, 
            metadata={"text_content": text}
        )
        
        logger.info(f"WhatsApp text intake: {qid} - {len(text)} chars")
        
        return {
            "status": "success",
            "qid": qid,
            "message": "Text message queued for processing"
        }
        
    except Exception as e:
        logger.error(f"WhatsApp text intake error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process WhatsApp text")