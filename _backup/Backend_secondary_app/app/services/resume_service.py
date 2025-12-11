from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
import uuid
from datetime import datetime
import json
import os
from fastapi import BackgroundTasks, UploadFile
import logging

logger = logging.getLogger(__name__)

class ResumeService:
    def __init__(self, db: Session):
        self.db = db
    
    async def process_resume(
        self, 
        file_id: str, 
        filename: str, 
        content_type: str, 
        file_content: bytes,
        background_tasks: BackgroundTasks
    ) -> Dict[str, Any]:
        """
        Process resume using consolidated_extractor
        """
        try:
            # Save temporary file
            temp_dir = "/tmp/resumes"
            os.makedirs(temp_dir, exist_ok=True)
            temp_file_path = f"{temp_dir}/{file_id}_{filename}"
            
            with open(temp_file_path, "wb") as f:
                f.write(file_content)
            
            # Import consolidated_extractor
            from app.text_extraction.consolidated_extractor import extract_with_logging
            
            # Process with consolidated_extractor
            result = await extract_with_logging(
                file_path=temp_file_path,
                filename=filename,
                content_type=content_type
            )
            
            # Calculate score and detect missing fields
            score = self.calculate_resume_score(result["extracted_text"])
            missing_fields = await self.detect_missing_fields(result["extracted_text"])
            
            # Clean up temp file
            os.remove(temp_file_path)
            
            return {
                "extracted_text": result["extracted_text"],
                "score": score,
                "module": result.get("module", "consolidated_extractor"),
                "missing_fields": missing_fields
            }
            
        except Exception as e:
            logger.error(f"Error processing resume: {str(e)}")
            raise Exception(f"Failed to process resume: {str(e)}")
    
    def calculate_resume_score(self, extracted_text: str) -> int:
        """
        Calculate resume completeness score based on missing fields
        """
        required_fields = [
            "name", "email", "phone", "education", 
            "experience", "skills", "summary"
        ]
        
        score = 100
        missing_count = 0
        
        for field in required_fields:
            if field.lower() not in extracted_text.lower():
                missing_count += 1
        
        # Deduct 10 points for each missing field
        score -= missing_count * 10
        
        return max(0, min(100, score))
    
    async def detect_missing_fields(self, extracted_text: str) -> List[str]:
        """
        Detect missing fields from extracted text
        """
        required_fields = [
            "name", "email", "phone", "education", 
            "experience", "skills", "summary", "address"
        ]
        
        missing_fields = []
        
        for field in required_fields:
            if field.lower() not in extracted_text.lower():
                missing_fields.append(field)
        
        return missing_fields
    
    async def parse_resume_text(self, extracted_text: str) -> Dict[str, Any]:
        """
        Parse extracted text into structured candidate data
        """
        try:
            # Basic parsing logic - in a real implementation, 
            # this would use more sophisticated NLP techniques
            candidate_data = {
                "personal_info": {},
                "education": [],
                "experience": [],
                "skills": [],
                "summary": "",
                "projects": []
            }
            
            # Simple text parsing (placeholder for actual implementation)
            lines = extracted_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Basic field detection
                if '@' in line and '.' in line:
                    candidate_data["personal_info"]["email"] = line
                elif any(char.isdigit() for char in line) and len(line.replace('-', '').replace(' ', '')) > 8:
                    candidate_data["personal_info"]["phone"] = line
                elif line.lower().startswith('summary') or line.lower().startswith('objective'):
                    candidate_data["summary"] = line
                elif any(skill in line.lower() for skill in ['python', 'java', 'javascript', 'react', 'node']):
                    candidate_data["skills"].append(line)
            
            return candidate_data
            
        except Exception as e:
            logger.error(f"Error parsing resume text: {str(e)}")
            raise Exception(f"Failed to parse resume text: {str(e)}")
    
    async def create_candidate_profile(self, candidate_data: Dict[str, Any]) -> str:
        """
        Create candidate profile from parsed data
        """
        try:
            # This would integrate with the candidate profile creation
            # For now, return a placeholder profile ID
            profile_id = str(uuid.uuid4())
            
            # In a real implementation, you would:
            # 1. Create/update candidate profile
            # 2. Create work history entries
            # 3. Save to database
            
            return profile_id
            
        except Exception as e:
            logger.error(f"Error creating candidate profile: {str(e)}")
            raise Exception(f"Failed to create candidate profile: {str(e)}")