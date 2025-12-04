"""
Magic bytes detector - identifies file type by examining file headers.
"""

import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Magic byte signatures for common file types
MAGIC_SIGNATURES = {
    'pdf': (b'%PDF-',),
    'doc': (b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1',),  # OLE2 signature
    'docx': (b'PK\x03\x04',),  # ZIP signature (DOCX is ZIP-based)
    'txt': (b'%', b'#', b'@', b'-', b' ', b'\t', b'\n'),  # Common text starters
    'rtf': (b'{\\rtf', b'\\rtf'),
}

def detect_file_type(file_bytes: bytes, filename: str) -> str:
    """
    Detect actual file type using magic bytes.
    
    Args:
        file_bytes: Raw file bytes
        filename: Original filename
        
    Returns:
        str: Detected file type
        
    Raises:
        ValueError: If file type cannot be detected
    """
    logger.debug(f"Detecting file type for: {filename}")
    
    # Get first 512 bytes for signature matching
    header = file_bytes[:512]
    
    # Try to match against known signatures
    for file_type, signatures in MAGIC_SIGNATURES.items():
        for signature in signatures:
            if header.startswith(signature):
                logger.debug(f"Detected file type: {file_type} for {filename}")
                return file_type
    
    # Fallback to extension-based detection
    file_extension = filename.lower()
    if '.' in file_extension:
        file_extension = file_extension[file_extension.rfind('.'):]
        
        extension_mapping = {
            '.pdf': 'pdf',
            '.doc': 'doc',
            '.docx': 'docx',
            '.txt': 'txt',
            '.rtf': 'rtf'
        }
        
        if file_extension in extension_mapping:
            logger.debug(f"Fallback detection: {extension_mapping[file_extension]} for {filename}")
            return extension_mapping[file_extension]
    
    raise ValueError(f"Unable to detect file type for {filename}. Header: {header[:20].hex()}")