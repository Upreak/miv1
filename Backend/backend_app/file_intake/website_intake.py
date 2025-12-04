"""
Website intake module - handles resume uploads from web interface.
"""

from typing import Any
from backend_app.file_intake.intake_router import IntakeRouter

def process_website_upload(file_obj: Any) -> dict:
    """
    Process resume upload from website frontend.
    
    Args:
        file_obj: FastAPI UploadFile object
        
    Returns:
        Dict with processing results
    """
    file_bytes = file_obj.read()
    filename = file_obj.filename
    
    return IntakeRouter.process_file(
        file_bytes=file_bytes,
        filename=filename,
        source="website"
    )