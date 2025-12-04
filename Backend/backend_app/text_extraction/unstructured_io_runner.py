"""
Unstructured.io runner - handles text extraction using Unstructured.io API.
"""

import logging
import requests
import os
from typing import Optional

logger = logging.getLogger(__name__)

# Configuration
UNSTRUCTURED_API_URL = os.getenv('UNSTRUCTURED_API_URL', 'https://api.unstructured.io/general/v0/general')
UNSTRUCTURED_API_KEY = os.getenv('UNSTRUCTURED_API_KEY')

def extract_with_unstructured(file_bytes: bytes, filename: str, file_type: str) -> Optional[str]:
    """
    Extract text using Unstructured.io API.
    
    Args:
        file_bytes: File content as bytes
        filename: Original filename
        file_type: Detected file type
        
    Returns:
        str: Extracted text or None if extraction failed
    """
    if not UNSTRUCTURED_API_KEY:
        logger.warning("Unstructured.io API key not configured")
        return None
    
    try:
        # Prepare files for upload
        files = {
            'files': (filename, file_bytes)
        }
        
        # Prepare headers
        headers = {
            'Authorization': f'Bearer {UNSTRUCTURED_API_KEY}'
        }
        
        # Prepare form data
        data = {
            'strategy': 'hi_res',  # Use high-resolution strategy for better accuracy
            'include_page_breaks': 'true',
            'languages': ['eng']
        }
        
        logger.debug(f"Calling Unstructured.io API for {filename}")
        
        # Make API request
        response = requests.post(
            UNSTRUCTURED_API_URL,
            headers=headers,
            files=files,
            data=data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract text from response
            extracted_text = ""
            for element in result:
                if 'text' in element:
                    extracted_text += element['text'] + '\n\n'
            
            logger.debug(f"Unstructured.io extraction successful for {filename}")
            return extracted_text.strip()
        
        else:
            logger.error(f"Unstructured.io API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Unstructured.io extraction failed for {filename}: {str(e)}")
        return None