"""
File Extraction API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
import logging
import os

from backend_app.db.connection import get_db
from backend_app.services.extraction import ExtractionService
from backend_app.models.users import User
from backend_app.services.auth import AuthService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload")
async def upload_and_extract(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    """Upload file and extract text using consolidated extractor"""
    extraction_service = ExtractionService(db)
    
    try:
        # Validate file type
        if file.content_type not in ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Please upload PDF, DOC, or DOCX files."
            )
        
        # Check file size
        content = await file.read()
        max_size = 10 * 1024 * 1024  # 10MB
        if len(content) > max_size:
            raise HTTPException(
                status_code=413,
                detail="File too large. Maximum file size is 10MB."
            )
        
        # Save uploaded file temporarily
        temp_dir = "./temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)
        temp_file_path = os.path.join(temp_dir, file.filename)
        
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(content)
        
        try:
            # Extract text using consolidated extractor
            result = await extraction_service.extract_text(
                file_path=temp_file_path,
                filename=file.filename,
                user_id=str(current_user.id)
            )
            
            # Clean up temp file
            os.remove(temp_file_path)
            
            return {
                "success": True,
                "filename": file.filename,
                "extracted_text": result.get("text", ""),
                "metadata": result.get("metadata", {}),
                "provider_used": result.get("provider_used", ""),
                "processing_time": result.get("processing_time", 0)
            }
            
        except Exception as e:
            # Clean up temp file on error
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            logger.error(f"Extraction failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Extraction failed: {str(e)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )


@router.get("/providers")
async def get_available_providers(
    db: AsyncSession = Depends(get_db)
):
    """Get list of available extraction providers"""
    extraction_service = ExtractionService(db)
    
    try:
        providers = await extraction_service.get_available_providers()
        return {
            "success": True,
            "providers": providers
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get providers: {str(e)}"
        )