"""
Quarantine manager - handles storage and management of suspicious files.
"""

import logging
import os
import shutil
import hashlib
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

# Configuration
QUARANTINE_DIR = "quarantine"
QUARANTINE_ENABLED = True

def quarantine_file(file_bytes: bytes, filename: str, reason: str = "Suspicious file") -> Optional[str]:
    """
    Move suspicious file to quarantine storage.
    
    Args:
        file_bytes: Raw file bytes
        filename: Original filename
        reason: Reason for quarantine
        
    Returns:
        str: Quarantine file path, or None if quarantine failed
    """
    if not QUARANTINE_ENABLED:
        logger.warning("Quarantine is disabled")
        return None
    
    try:
        # Ensure quarantine directory exists
        os.makedirs(QUARANTINE_DIR, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_hash = hashlib.sha256(file_bytes).hexdigest()[:8]
        quarantine_filename = f"{timestamp}_{file_hash}_{filename}"
        quarantine_path = os.path.join(QUARANTINE_DIR, quarantine_filename)
        
        # Save file to quarantine
        with open(quarantine_path, 'wb') as f:
            f.write(file_bytes)
        
        # Create metadata file
        metadata_path = f"{quarantine_path}.meta"
        with open(metadata_path, 'w') as f:
            f.write(f"Original filename: {filename}\n")
            f.write(f"Quarantine reason: {reason}\n")
            f.write(f"Quarantine time: {datetime.now().isoformat()}\n")
            f.write(f"File hash (SHA256): {hashlib.sha256(file_bytes).hexdigest()}\n")
            f.write(f"File size: {len(file_bytes)} bytes\n")
        
        logger.warning(f"File quarantined: {quarantine_path}")
        return quarantine_path
        
    except Exception as e:
        logger.error(f"Failed to quarantine file {filename}: {str(e)}")
        return None

def list_quarantined_files() -> list:
    """
    List all quarantined files.
    
    Returns:
        list: List of quarantined file metadata
    """
    if not QUARANTINE_ENABLED:
        return []
    
    files = []
    
    try:
        if not os.path.exists(QUARANTINE_DIR):
            return files
        
        for filename in os.listdir(QUARANTINE_DIR):
            if filename.endswith('.meta'):
                metadata_path = os.path.join(QUARANTINE_DIR, filename)
                try:
                    with open(metadata_path, 'r') as f:
                        metadata = f.read()
                    files.append({
                        'filename': filename[:-5],  # Remove .meta extension
                        'metadata': metadata,
                        'path': metadata_path[:-5]  # Remove .meta extension
                    })
                except Exception as e:
                    logger.error(f"Failed to read metadata for {filename}: {str(e)}")
        
        return files
        
    except Exception as e:
        logger.error(f"Failed to list quarantined files: {str(e)}")
        return []

def restore_quarantined_file(quarantine_filename: str) -> Optional[bytes]:
    """
    Restore a file from quarantine.
    
    Args:
        quarantine_filename: Name of quarantined file
        
    Returns:
        bytes: File content, or None if restore failed
    """
    if not QUARANTINE_ENABLED:
        return None
    
    try:
        quarantine_path = os.path.join(QUARANTINE_DIR, quarantine_filename)
        
        if not os.path.exists(quarantine_path):
            logger.error(f"Quarantined file not found: {quarantine_filename}")
            return None
        
        with open(quarantine_path, 'rb') as f:
            content = f.read()
        
        # Remove from quarantine
        os.remove(quarantine_path)
        metadata_path = f"{quarantine_path}.meta"
        if os.path.exists(metadata_path):
            os.remove(metadata_path)
        
        logger.info(f"File restored from quarantine: {quarantine_filename}")
        return content
        
    except Exception as e:
        logger.error(f"Failed to restore quarantined file {quarantine_filename}: {str(e)}")
        return None

def delete_quarantined_file(quarantine_filename: str) -> bool:
    """
    Permanently delete a quarantined file.
    
    Args:
        quarantine_filename: Name of quarantined file
        
    Returns:
        bool: True if deletion succeeded
    """
    if not QUARANTINE_ENABLED:
        return False
    
    try:
        quarantine_path = os.path.join(QUARANTINE_DIR, quarantine_filename)
        
        if not os.path.exists(quarantine_path):
            logger.error(f"Quarantined file not found: {quarantine_filename}")
            return False
        
        # Remove file and metadata
        os.remove(quarantine_path)
        metadata_path = f"{quarantine_path}.meta"
        if os.path.exists(metadata_path):
            os.remove(metadata_path)
        
        logger.info(f"Quarantined file permanently deleted: {quarantine_filename}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to delete quarantined file {quarantine_filename}: {str(e)}")
        return False