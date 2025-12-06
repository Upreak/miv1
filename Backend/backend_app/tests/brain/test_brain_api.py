"""
Brain Module API Tests

Comprehensive test suite for Brain Module API endpoints covering:
- Functional Tests (resume_parse, jd_parse, match, chat)
- Error Cases (missing mode, unsupported mode, empty text, provider failure)
- Contract Tests (ensure output format compliance)
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import status
import json

# Import the brain API module
from backend_app.api.v1.brain import router, BrainInputContract, BrainOutputContract
from backend_app.brain_module.brain_service import BrainService


class TestBrainAPI:
    """Test suite for Brain Module API endpoints"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.client = TestClient(router)
        
    def test_brain_health_check(self):
        """Test GET /brain/health endpoint"""
        response = self.client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "ok"
        
    def test_resume_parsing_test(self):
        """Test resume parsing functionality"""
        # Sample resume text
        resume_text = """
        John Doe
        Software Engineer
        
        Experience:
        - Senior Python Developer at Tech Corp (2020-2023)
        - Junior Developer at Startup Inc (2018-2020)
        
        Education:
        - MS Computer Science, University of Technology (2018)
        - BS Software Engineering, State University (2016)
        
        Skills: Python, JavaScript, React, Django, Node.js, SQL
        """
        
        request_data = {
            "mode": "resume_parse",
            "text": resume_text,
            "metadata": {
                "source": "pdf",
                "filename": "john_doe_resume.pdf"
            }
        }
        
        with patch('backend_app.api.v1.brain.brain_service.process') as mock_process:
            # Mock successful brain service response
            mock_process.return_value = AsyncMock(return_value={
                "qid": "test_qid",
                "success": True,
                "provider": "mock_provider",
                "model": "mock_model",
                "response": json.dumps({
                    "full_name": "John Doe",
                    "skills": ["Python", "JavaScript", "React", "Django", "Node.js", "SQL"],
                    "education": [
                        {"degree": "MS Computer Science", "year": "2018"},
                        {"degree": "BS Software Engineering", "year": "2016"}
                    ]
                }),
                "usage": {"input_tokens": 150, "output_tokens": 50, "total_tokens": 200},
                "error": None
            })
            
            response = self.client.post("/process", json=request_data)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            # Verify output contract compliance
            assert data["success"] is True
            assert data["mode"] == "resume_parse"
            assert data["intent"] == "parse_resume"
            assert "provider" in data
            assert "tokens" in data
            assert "metadata" in data
            assert "raw_response" in data
            assert "data" in data
            
            # Verify resume-specific data
            resume_data = data["data"]
            if isinstance(resume_data, dict):
                assert "full_name" in resume_data or "skills" in resume_data or "education" in resume_data