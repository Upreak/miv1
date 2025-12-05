"""
File Extraction API Routes - Final Implementation
Exact specification: POST /api/v1/extraction/run
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import logging
import os
import json
import tempfile
from pathlib import Path
from datetime import datetime

from backend_app.text_extraction.consolidated_extractor import extract_with_logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/run")
async def run_extraction(
    file: UploadFile = File(..., description="File to extract text from"),
    document_type: str = Form(..., description="Type of document: resume | job_description | generic"),
    metadata: Optional[str] = Form(None, description="Optional JSON string with metadata")
):
    """
    Run text extraction on uploaded file
    """
    try:
        # Validate document_type
        valid_types = ["resume", "job_description", "generic"]
        if document_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid document_type. Must be one of: {', '.join(valid_types)}"
            )

        # Validate file presence
        if not file:
            raise HTTPException(status_code=400, detail="No file provided")

        # Parse metadata if provided
        metadata_dict = {}
        if metadata:
            try:
                metadata_dict = json.loads(metadata)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid metadata JSON format")

        # Validate file type (allow reasonable set of document types)
        allowed_types = {
            "application/pdf",
            "application/msword", 
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "image/jpeg",
            "image/jpg", 
            "image/png",
            "image/tiff"
        }
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.content_type}. Supported types: PDF, DOC, DOCX, JPG, PNG, TIFF"
            )

        # Check file size (10MB limit)
        content = await file.read()
        max_size = 10 * 1024 * 1024  # 10MB
        if len(content) > max_size:
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum file size is 10MB."
            )

        # Save file to temporary path
        temp_dir = "./temp_extractions"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Create unique filename to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        temp_filename = f"{timestamp}_{file.filename}"
        temp_file_path = os.path.join(temp_dir, temp_filename)
        
        try:
            # Write file to temporary location
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(content)

            # Convert to Path object for the extractor
            file_path = Path(temp_file_path)
            
            # Call the consolidated extractor
            logger.info(f"Starting extraction for file: {file.filename}, type: {document_type}")
            
            result = extract_with_logging(
                file_path=file_path,
                metadata=metadata_dict,
                quality_threshold=70
            )
            
            # Get the log ID from the logbook (we need to check the logbook table)
            log_id = None
            try:
                import sqlite3
                logbook_path = Path("logs/extraction_logbook.db")
                if logbook_path.exists():
                    with sqlite3.connect(str(logbook_path)) as conn:
                        cursor = conn.execute(
                            "SELECT id FROM extraction_logs ORDER BY id DESC LIMIT 1"
                        )
                        row = cursor.fetchone()
                        if row:
                            log_id = row[0]
            except Exception as e:
                logger.warning(f"Could not retrieve log_id: {e}")
                log_id = -1  # Use -1 as fallback

            # Prepare response according to exact specification format
            response = {
                "success": bool(result.get("success", False)),
                "document_type": document_type,
                "file_name": file.filename,
                "file_size": len(content),
                "module_used": result.get("module", ""),
                "text": result.get("text", ""),
                "score": float(result.get("score", 0.0)),
                "attempts": result.get("attempts", []),
                "metadata": metadata_dict,
                "log_id": log_id if log_id is not None else -1
            }
            
            logger.info(f"Extraction completed successfully for {file.filename}")
            return response
            
        finally:
            # Clean up temporary file
            try:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
            except Exception as e:
                logger.warning(f"Could not remove temp file {temp_file_path}: {e}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in extraction endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error during extraction: {str(e)}"
        )