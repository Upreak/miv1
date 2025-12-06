"""
Brain Module API Endpoint
Implements POST /api/v1/brain/process with frozen input/output contracts
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, validator
from typing import Dict, Any, Optional, Union
import json
import logging
from datetime import datetime

from backend_app.shared.exceptions import bad_request, validation_error
from backend_app.brain_module.brain_service import BrainService
from backend_app.brain_module.utils.logger import get_logger

logger = get_logger("brain_api")

# Valid modes
VALID_MODES = ["resume_parse", "jd_parse", "match", "chat"]

class BrainInputContract(BaseModel):
    """Frozen Brain Input Contract"""
    mode: str
    text: str
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('mode')
    def validate_mode(cls, v):
        if v not in VALID_MODES:
            raise ValueError(f"mode must be one of: {', '.join(VALID_MODES)}")
        return v
    
    @validator('text')
    def validate_text(cls, v):
        if not v or not v.strip():
            raise ValueError("text cannot be empty")
        return v.strip()
    
    @validator('metadata')
    def validate_metadata(cls, v):
        if v is not None and not isinstance(v, dict):
            raise ValueError("metadata must be an object or omitted")
        return v or {}

class BrainOutputContract(BaseModel):
    """Frozen Brain Output Contract"""
    success: bool
    mode: str
    intent: str
    data: Dict[str, Any]
    provider: str
    tokens: Dict[str, int]
    metadata: Dict[str, Any]
    raw_response: str

class BrainHealthResponse(BaseModel):
    """Health check response"""
    status: str

# Initialize brain service
brain_service = BrainService()

router = APIRouter()

@router.post("/process", response_model=BrainOutputContract)
async def process_brain_request(request: BrainInputContract):
    """
    Process brain request with frozen input/output contracts
    
    Validates:
    - mode must be one of: "resume_parse", "jd_parse", "match", "chat"
    - text cannot be empty
    - metadata must be object or omitted
    """
    try:
        logger.info("Processing brain request", extra={
            "mode": request.mode,
            "text_length": len(request.text),
            "metadata_keys": list(request.metadata.keys()) if request.metadata else []
        })
        
        # Validate input according to frozen contract
        if request.mode not in VALID_MODES:
            raise validation_error(
                f"mode must be one of: {', '.join(VALID_MODES)}",
                "INVALID_MODE"
            )
        
        if not request.text.strip():
            raise validation_error(
                "text cannot be empty",
                "EMPTY_TEXT"
            )
        
        # Special validation for match mode
        if request.mode == "match":
            candidate_data = request.metadata.get("candidate_data", "")
            jd_data = request.metadata.get("jd_data", "")
            if not candidate_data or not jd_data:
                raise validation_error(
                    "match mode requires 'candidate_data' and 'jd_data' in metadata",
                    "MISSING_MATCH_DATA"
                )
        
        # Route to BrainService for processing
        result = await _process_with_brain_service(request)
        
        # Validate output matches frozen contract
        return _validate_output_contract(result, request.mode)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error processing brain request", exc_info=True)
        raise internal_server_error(
            "Failed to process brain request",
            "BRAIN_PROCESSING_ERROR"
        )

@router.get("/health", response_model=BrainHealthResponse)
async def brain_health_check():
    """Brain module health check endpoint"""
    return BrainHealthResponse(status="ok")

async def _process_with_brain_service(request: BrainInputContract) -> Dict[str, Any]:
    """Process request through BrainService"""
    
    # Prepare data for brain service based on mode
    if request.mode == "match":
        # For match mode, combine candidate and job data
        candidate_data = request.metadata.get("candidate_data", "")
        jd_data = request.metadata.get("jd_data", "")
        text = f"Candidate: {candidate_data}\n\nJob: {jd_data}"
        intake_type = "match"
        meta = request.metadata
    else:
        text = request.text
        intake_type = request.mode
        meta = request.metadata
    
    # Create qitem for brain service
    qitem = {
        "qid": f"brain_{int(datetime.now().timestamp() * 1000)}",
        "text": text,
        "intake_type": intake_type,
        "meta": meta
    }
    
    # Process through brain service
    result = brain_service.process(qitem)
    
    # Parse provider response to extract structured data
    provider_response = result.get("response", "")
    parsed_data = _parse_provider_response(provider_response, request.mode)
    
    # Build intent based on mode
    intent = _determine_intent(request.mode)
    
    # Format tokens
    usage = result.get("usage", {})
    tokens = {
        "input": usage.get("input_tokens", 0) or usage.get("prompt_tokens", 0) or 0,
        "output": usage.get("output_tokens", 0) or usage.get("completion_tokens", 0) or 0,
        "total": usage.get("total_tokens", 0) or 0
    }
    
    return {
        "success": bool(result.get("success", False)),
        "mode": request.mode,
        "intent": intent,
        "data": parsed_data,
        "provider": result.get("provider", "unknown"),
        "tokens": tokens,
        "metadata": request.metadata,
        "raw_response": provider_response
    }

def _parse_provider_response(response: str, mode: str) -> Dict[str, Any]:
    """Parse provider response based on mode"""
    try:
        # Try to parse as JSON first
        if response.strip().startswith(('{', '[')):
            parsed = json.loads(response)
            return parsed if isinstance(parsed, dict) else {"raw": response}
        else:
            # Return as text for non-JSON responses
            return {"text": response}
    except json.JSONDecodeError:
        # Return raw response if JSON parsing fails
        return {"raw": response, "text": response}

def _determine_intent(mode: str) -> str:
    """Determine intent based on mode"""
    intent_map = {
        "resume_parse": "parse_resume",
        "jd_parse": "parse_job_description", 
        "match": "match_candidate_job",
        "chat": "conversational_response"
    }
    return intent_map.get(mode, "unknown_intent")

def _validate_output_contract(result: Dict[str, Any], mode: str) -> BrainOutputContract:
    """Validate and return output in frozen contract format"""
    
    # Ensure all required fields are present
    required_fields = ["success", "mode", "intent", "data", "provider", "tokens", "metadata", "raw_response"]
    for field in required_fields:
        if field not in result:
            result[field] = None if field in ["provider"] else ({}, "0", {})[field == "tokens"]
    
    # Validate success and data for certain modes
    if result["success"] and mode in ["resume_parse", "jd_parse"]:
        if not isinstance(result["data"], dict) or not result["data"]:
            logger.warning(f"Mode {mode} returned empty or invalid data")
    
    return BrainOutputContract(
        success=bool(result["success"]),
        mode=result["mode"],
        intent=result["intent"],
        data=result["data"] or {},
        provider=result["provider"] or "unknown",
        tokens=result["tokens"] or {"input": 0, "output": 0, "total": 0},
        metadata=result["metadata"] or {},
        raw_response=result["raw_response"] or ""
    )

# Exception helpers
def internal_server_error(message: str, error_code: str) -> HTTPException:
    """Create 500 Internal Server Error exception"""
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={"message": message, "error_code": error_code}
    )