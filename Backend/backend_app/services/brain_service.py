"""
Brain Service - Integration layer between intake pipeline and brain core.

This service provides a simple interface for the intake pipeline to call
the brain core for resume parsing and other AI tasks.
"""

import logging
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Try to load .env from project root (two levels up from brain_service)
    project_root = Path(__file__).parent.parent.parent
    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        logging.getLogger(__name__).info(f"Loaded .env from {env_path}")
    else:
        # Fallback to default location
        load_dotenv()
except ImportError:
    pass  # dotenv is optional

# Import the brain core
from backend_app.brain_module.brain_core import BrainCore

logger = logging.getLogger(__name__)

# Global brain core instance (singleton pattern)
_brain_core: Optional[BrainCore] = None

def get_brain_core(config_path: str = None) -> BrainCore:
    """
    Get or create a singleton brain core instance.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        BrainCore instance
    """
    global _brain_core
    if _brain_core is None:
        # Use default config path if none provided
        if config_path is None:
            config_path = "config/providers.yaml"
        _brain_core = BrainCore(config_path=config_path)
    return _brain_core

def parse_resume_from_path(file_path: Path, strategy: str = "fast") -> Dict[str, Any]:
    """
    Parse a resume file using the brain core.
    
    This function:
    1. Extracts text from the file using the brain core's extraction capabilities
    2. Sends the text to the brain core for parsing
    3. Returns the parsed result
    
    Args:
        file_path: Path to the resume file
        strategy: Extraction strategy (default: "fast")
        
    Returns:
        Dictionary with parsing results
    """
    brain = get_brain_core()
    
    logger.info(f"Parsing resume: {file_path}")
    
    try:
        # Process the file using brain core
        # The brain core will handle text extraction and AI parsing
        result = brain.process_input(
            input_data=file_path,  # Pass file path directly
            task_type="resume_parsing",
            preferred_provider=None  # Let brain core choose best provider
        )
        
        # Convert BrainResult to dictionary format
        output = {
            "success": result.success,
            "provider": result.provider,
            "model": result.model,
            "response": result.response,
            "usage": result.usage,
            "response_time": result.response_time,
            "error_message": result.error_message,
            "metadata": result.metadata,
            "output_file": result.output_file
        }
        
        logger.info(f"Resume parsing completed: success={result.success}, provider={result.provider}")
        return output
        
    except Exception as e:
        logger.error(f"Error parsing resume {file_path}: {e}")
        
        return {
            "success": False,
            "provider": "unknown",
            "model": "unknown",
            "response": "",
            "usage": {},
            "response_time": 0.0,
            "error_message": str(e),
            "metadata": {},
            "output_file": None
        }

def parse_text(text: str, task_type: str = "resume_parsing") -> Dict[str, Any]:
    """
    Parse text using the brain core.
    
    Args:
        text: Text to parse
        task_type: Type of parsing task
        
    Returns:
        Dictionary with parsing results
    """
    brain = get_brain_core()
    
    logger.info(f"Parsing text with task type: {task_type}")
    
    try:
        # Process the text using brain core
        result = brain.process_input(
            input_data=text,
            task_type=task_type,
            preferred_provider=None
        )
        
        # Convert BrainResult to dictionary format
        output = {
            "success": result.success,
            "provider": result.provider,
            "model": result.model,
            "response": result.response,
            "usage": result.usage,
            "response_time": result.response_time,
            "error_message": result.error_message,
            "metadata": result.metadata,
            "output_file": result.output_file
        }
        
        logger.info(f"Text parsing completed: success={result.success}, provider={result.provider}")
        return output
        
    except Exception as e:
        logger.error(f"Error parsing text: {e}")
        
        return {
            "success": False,
            "provider": "unknown",
            "model": "unknown",
            "response": "",
            "usage": {},
            "response_time": 0.0,
            "error_message": str(e),
            "metadata": {},
            "output_file": None
        }

def test_connection() -> Dict[str, Any]:
    """
    Test the brain service connection by sending a simple test message.
    
    Returns:
        Dictionary with test results
    """
    brain = get_brain_core()
    
    try:
        # Test with a simple message
        result = brain.test_api_channel_connection()
        
        return {
            "success": True,
            "test_results": result,
            "message": "Brain service connection test completed"
        }
        
    except Exception as e:
        logger.error(f"Brain service connection test failed: {e}")
        
        return {
            "success": False,
            "error_message": str(e),
            "message": "Brain service connection test failed"
        }

def get_brain_status() -> Dict[str, Any]:
    """
    Get the current status of the brain service.
    
    Returns:
        Dictionary with brain status information
    """
    brain = get_brain_core()
    
    try:
        status = brain.get_brain_status()
        
        return {
            "success": True,
            "status": status,
            "message": "Brain service status retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting brain status: {e}")
        
        return {
            "success": False,
            "error_message": str(e),
            "message": "Failed to get brain service status"
        }