"""
Email intake module - handles file processing from email attachments.
"""

from typing import Dict, Any
from backend_app.file_intake.intake_router import IntakeRouter

def process_email_attachment(file_bytes: bytes, filename: str, sender_email: str) -> Dict[str, Any]:
    """
    Process file attachment received via email.
    
    Args:
        file_bytes: Raw file bytes
        filename: Original filename
        sender_email: Email address of sender
        
    Returns:
        Dict with processing results
    """
    return IntakeRouter.process_file(
        file_bytes=file_bytes,
        filename=filename,
        source="email_ingestion"
    )