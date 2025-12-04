from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ResumeUploadResponse(BaseModel):
    file_id: str
    filename: str
    extracted_text: str
    score: int
    module: str
    missing_fields: List[str]
    message: str

class ResumeParseRequest(BaseModel):
    extracted_text: str

class ResumeParseResponse(BaseModel):
    candidate_data: Dict[str, Any]
    message: str

class MissingFieldsResponse(BaseModel):
    missing_fields: List[str]
    message: str