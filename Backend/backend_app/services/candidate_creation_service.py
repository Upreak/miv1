"""
Candidate creation service - stores raw/sanitized text and creates candidate records.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Mock database storage (replace with actual DB integration)
candidates_db = {}

def create_candidate_profile(
    raw_text: str, 
    source: str, 
    filename: str = None,
    file_type: str = None
) -> str:
    """
    Create a candidate profile with extracted text.
    
    Args:
        raw_text: Extracted and sanitized text
        source: Source of the resume (website, whatsapp, etc.)
        filename: Original filename (optional)
        file_type: Detected file type (optional)
        
    Returns:
        str: Candidate ID
        
    Raises:
        ValueError: If text is empty
    """
    if not raw_text or not raw_text.strip():
        raise ValueError("Extracted text cannot be empty")
    
    # Generate unique candidate ID
    candidate_id = f"CAND-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    
    # Create candidate profile
    candidate_profile = {
        'id': candidate_id,
        'created_at': datetime.now().isoformat(),
        'source': source,
        'filename': filename,
        'file_type': file_type,
        'raw_text_length': len(raw_text),
        'raw_text': raw_text,
        'status': 'created',
        'parsed': False,
        'ai_analysis_complete': False
    }
    
    # Store in mock database
    candidates_db[candidate_id] = candidate_profile
    
    logger.info(f"Created candidate profile: {candidate_id} from {source}")
    logger.debug(f"Candidate text preview: {raw_text[:100]}...")
    
    return candidate_id

def get_candidate_profile(candidate_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve candidate profile by ID.
    
    Args:
        candidate_id: Candidate ID
        
    Returns:
        Dict: Candidate profile or None if not found
    """
    return candidates_db.get(candidate_id)

def update_candidate_status(candidate_id: str, status: str, **kwargs) -> bool:
    """
    Update candidate status and other fields.
    
    Args:
        candidate_id: Candidate ID
        status: New status
        **kwargs: Additional fields to update
        
    Returns:
        bool: True if update succeeded
    """
    if candidate_id not in candidates_db:
        logger.warning(f"Attempted to update non-existent candidate: {candidate_id}")
        return False
    
    candidates_db[candidate_id]['status'] = status
    candidates_db[candidate_id].update(kwargs)
    
    logger.info(f"Updated candidate {candidate_id} status to: {status}")
    return True

def list_candidates(limit: int = 50) -> list:
    """
    List all candidates (for admin purposes).
    
    Args:
        limit: Maximum number of candidates to return
        
    Returns:
        list: List of candidate profiles
    """
    return list(candidates_db.values())[:limit]

def delete_candidate(candidate_id: str) -> bool:
    """
    Delete a candidate profile.
    
    Args:
        candidate_id: Candidate ID
        
    Returns:
        bool: True if deletion succeeded
    """
    if candidate_id in candidates_db:
        del candidates_db[candidate_id]
        logger.info(f"Deleted candidate: {candidate_id}")
        return True
    else:
        logger.warning(f"Attempted to delete non-existent candidate: {candidate_id}")
        return False