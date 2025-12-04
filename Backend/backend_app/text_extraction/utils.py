"""
Text extraction utilities - helper functions for file processing.
"""

import logging
import os
import tempfile
from typing import Optional, BinaryIO

logger = logging.getLogger(__name__)

def create_temp_file(file_bytes: bytes, suffix: str = '') -> str:
    """
    Create a temporary file from bytes.
    
    Args:
        file_bytes: File content as bytes
        suffix: File extension (e.g., '.pdf', '.docx')
        
    Returns:
        str: Path to temporary file
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(file_bytes)
        return temp_file.name

def cleanup_temp_file(file_path: str) -> None:
    """
    Clean up temporary file.
    
    Args:
        file_path: Path to temporary file
    """
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
            logger.debug(f"Cleaned up temp file: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to clean up temp file {file_path}: {str(e)}")

def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename.
    
    Args:
        filename: Original filename
        
    Returns:
        str: File extension (lowercase, with dot)
    """
    if '.' in filename:
        return os.path.splitext(filename)[1].lower()
    return ''

def is_text_file(file_bytes: bytes, filename: str) -> bool:
    """
    Check if file is a plain text file.
    
    Args:
        file_bytes: File content as bytes
        filename: Original filename
        
    Returns:
        bool: True if text file
    """
    extension = get_file_extension(filename)
    if extension in ['.txt', '.text']:
        return True
    
    # Try to decode as UTF-8
    try:
        text = file_bytes.decode('utf-8')
        # Check if it's mostly printable characters
        printable_ratio = sum(1 for c in text if c.isprintable() or c.isspace()) / len(text)
        return printable_ratio > 0.8
    except UnicodeDecodeError:
        return False

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage.
    
    Args:
        filename: Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Remove path separators and special characters
    safe_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-')
    sanitized = ''.join(c for c in filename if c in safe_chars)
    
    # Ensure it's not empty and has reasonable length
    if not sanitized:
        sanitized = 'unknown_file'
    
    if len(sanitized) > 255:
        sanitized = sanitized[:255]
    
    return sanitized