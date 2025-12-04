"""
File Extraction Service
Handles file upload and text extraction using the consolidated extractor.
"""
from typing import Dict, Any, Optional
import logging
import time
import os
from sqlalchemy.ext.asyncio import AsyncSession

from backend_app.db.connection import get_db
from backend_app.text_extraction.consolidated_extractor import extract_with_logging

logger = logging.getLogger(__name__)


class ExtractionService:
    """Service for handling file extraction operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def extract_text(
        self, 
        file_path: str, 
        filename: str, 
        user_id: str
    ) -> Dict[str, Any]:
        """Extract text from uploaded file using consolidated extractor"""
        start_time = time.time()
        
        try:
            # Use the consolidated extractor
            result = extract_with_logging(
                file_path=file_path,
                filename=filename,
                user_id=user_id
            )
            
            processing_time = time.time() - start_time
            
            return {
                "text": result.get("text", ""),
                "metadata": result.get("metadata", {}),
                "provider_used": result.get("provider_used", ""),
                "processing_time": processing_time,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Extraction failed for file {filename}: {str(e)}")
            raise Exception(f"Text extraction failed: {str(e)}")
    
    async def get_available_providers(self) -> list:
        """Get list of available extraction providers"""
        # This would typically check the consolidated extractor's available providers
        # For now, return a static list
        return [
            "unstructured",
            "pdfminer",
            "pdfplumber",
            "tika",
            "grobid"
        ]
    
    async def validate_file(self, file_path: str, filename: str) -> bool:
        """Validate uploaded file"""
        try:
            # Check file exists
            if not os.path.exists(file_path):
                return False
            
            # Check file size
            file_size = os.path.getsize(file_path)
            max_size = 10 * 1024 * 1024  # 10MB
            if file_size > max_size:
                return False
            
            # Check file type based on extension
            allowed_extensions = ['.pdf', '.doc', '.docx']
            file_extension = os.path.splitext(filename)[1].lower()
            if file_extension not in allowed_extensions:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"File validation failed: {str(e)}")
            return False