from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.core.db import get_db
from app.schemas.resume import ResumeUploadResponse, ResumeParseRequest, ResumeParseResponse, MissingFieldsResponse
from app.services.resume_service import ResumeService
import uuid
from datetime import datetime

router = APIRouter()

@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        allowed_types = ["application/pdf", "application/msword", 
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Please upload PDF or DOC/DOCX files."
            )
        
        file_content = await file.read()
        file_id = str(uuid.uuid4())
        
        resume_service = ResumeService(db)
        result = await resume_service.process_resume(file_id, file.filename, file.content_type, file_content, background_tasks)
        
        return ResumeUploadResponse(
            file_id=file_id,
            filename=file.filename,
            extracted_text=result["extracted_text"],
            score=result["score"],
            module=result["module"],
            missing_fields=result["missing_fields"],
            message="Resume processed successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing resume: {str(e)}"
        )

@router.post("/parse", response_model=ResumeParseResponse)
async def parse_resume(
    parse_request: ResumeParseRequest,
    db: Session = Depends(get_db)
):
    try:
        resume_service = ResumeService(db)
        candidate_data = await resume_service.parse_resume_text(parse_request.extracted_text)
        
        return ResumeParseResponse(
            candidate_data=candidate_data,
            message="Resume parsed successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error parsing resume: {str(e)}"
        )

@router.post("/missing-fields", response_model=MissingFieldsResponse)
async def get_missing_fields(
    parse_request: ResumeParseRequest,
    db: Session = Depends(get_db)
):
    try:
        resume_service = ResumeService(db)
        missing_fields = await resume_service.detect_missing_fields(parse_request.extracted_text)
        
        return MissingFieldsResponse(
            missing_fields=missing_fields,
            message="Missing fields detected successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error detecting missing fields: {str(e)}"
        )