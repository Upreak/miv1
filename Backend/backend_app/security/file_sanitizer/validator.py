"""
File validator - checks file size, extension, and MIME type.
"""

import logging
import mimetypes
from typing import Optional

logger = logging.getLogger(__name__)

# Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.txt', '.rtf'}
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain',
    'text/rtf'
}

def validate_file(file_bytes: bytes, filename: str) -> bool:
    """
    Validate file based on size, extension, and MIME type.
    
    Args:
        file_bytes: Raw file bytes
        filename: Original filename
        
    Returns:
        bool: True if file is valid
        
    Raises:
        ValueError: If file validation fails
    """
    logger.debug(f"Validating file: {filename}")
    
    # Check file size
    file_size = len(file_bytes)
    if file_size > MAX_FILE_SIZE:
        raise ValueError(f"File size {file_size} bytes exceeds maximum allowed size of {MAX_FILE_SIZE} bytes")
    
    if file_size == 0:
        raise ValueError("File is empty")
    
    # Check file extension
    file_extension = filename.lower()
    if '.' in file_extension:
        file_extension = file_extension[file_extension.rfind('.'):]
    
    if file_extension not in ALLOWED_EXTENSIONS:
        raise ValueError(f"File extension '{file_extension}' is not allowed. Allowed: {ALLOWED_EXTENSIONS}")
    
    # Check MIME type
    mime_type, _ = mimetypes.guess_type(filename)
    if mime_type and mime_type not in ALLOWED_MIME_TYPES:
        raise ValueError(f"MIME type '{mime_type}' is not allowed. Allowed: {ALLOWED_MIME_TYPES}")
    
    logger.debug(f"File validation passed: {filename}")
    return True