"""
Test suite for parsing pipeline.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from backend_app.file_intake.services.brain_parse_service import (
    get_brain_parse_service,
    BrainParseService,
    ResumeParseService,
    DocumentParseService,
    CompositeParseService
)
from backend_app.file_intake.config.intake_config import get_config


class TestParseService:
    """Test cases for parsing service."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = get_config()
        self.test_text = """
        John Doe
        Software Engineer
        
        Email: john.doe@example.com
        Phone: +1 (555) 123-4567
        LinkedIn: linkedin.com/in/johndoe
        
        EXPERIENCE
        Senior Software Engineer | Tech Corp | 2020 - Present
        - Developed web applications using React and Node.js
        - Led team of 5 developers
        - Implemented microservices architecture
        
        Software Engineer | StartupXYZ | 2018 - 2020
        - Built RESTful APIs using Python and Django
        - Optimized database queries for better performance
        
        EDUCATION
        Bachelor of Science in Computer Science
        University of Technology | 2014 - 2018
        
        SKILLS
        Programming: Python, JavaScript, Java, C++
        Web: React, Node.js, HTML, CSS, Django
        Database: PostgreSQL, MySQL, MongoDB
        Tools: Git, Docker, AWS, CI/CD
        """
    
    def test_brain_parse_service(self):
        """Test brain parse service."""
        # Mock brain service
        with patch('backend_app.file_intake.services.brain_parse_service.get_brain_service') as mock_get_brain:
            mock_brain_service = Mock()
            mock_brain_service.parse_text.return_value = {
                "success": True,
                "response": {
                    "contact": {
                        "name": "John Doe",
                        "email": "john.doe@example.com",
                        "phone": "+1 (555) 123-4567",
                        "linkedin": "linkedin.com/in/johndoe"
                    },
                    "experience": [
                        {
                            "company": "Tech Corp",
                            "position": "Senior Software Engineer",
                            "start_date": "2020",
                            "end_date": "Present",
                            "description": "Developed web applications using React and Node.js. Led team of 5 developers. Implemented microservices architecture."
                        },
                        {
                            "company": "StartupXYZ",
                            "position": "Software Engineer",
                            "start_date": "2018",
                            "end_date": "2020",
                            "description": "Built RESTful APIs using Python and Django. Optimized database queries for better performance."
                        }
                    ],
                    "education": [
                        {
                            "institution": "University of Technology",
                            "degree": "Bachelor of Science",
                            "field_of_study": "Computer Science",
                            "start_date": "2014",
                            "end_date": "2018"
                        }
                    ],
                    "skills": [
                        {"name": "Python", "category": "Programming"},
                        {"name": "JavaScript", "category": "Programming"},
                        {"name": "Java", "category": "Programming"},
                        {"name": "C++", "category": "Programming"},
                        {"name": "React", "category": "Web"},
                        {"name": "Node.js", "category": "Web"},
                        {"name": "HTML", "category": "Web"},
                        {"name": "CSS", "category": "Web"},
                        {"name": "Django", "category": "Web"},
                        {"name": "PostgreSQL", "category": "Database"},
                        {"name": "MySQL", "category": "Database"},
                        {"name": "MongoDB", "category": "Database"},
                        {"name": "Git", "category": "Tools"},
                        {"name": "Docker", "category": "Tools"},
                        {"name": "AWS", "category": "Tools"},
                        {"name": "CI/CD", "category": "Tools"}
                    ],
                    "metadata": {
                        "document_type": "resume",
                        "confidence_score": 0.95,
                        "language": "en",
                        "word_count": 150,
                        "page_count": 1
                    }
                },
                "parse_time": 2.5,
                "provider": "openrouter",
                "model": "gpt-4",
                "confidence_score": 0.95,
                "warnings": [],
                "errors": []
            }
            mock_get_brain.return_value = mock_brain_service
            
            # Create service and parse
            service = BrainParseService(self.config)
            result = service.parse_text(self.test_text, "resume")
            
            # Assert result
            assert result.success is True
            assert result.response["contact"]["name"] == "John Doe"
            assert result.response["contact"]["email"] == "john.doe@example.com"
            assert len(result.response["experience"]) == 2
            assert len(result.response["education"]) == 1
            assert len(result.response["skills"]) == 16
            assert result.response["metadata"]["document_type"] == "resume"
            assert result.response["metadata"]["confidence_score"] == 0.95
            assert result.parse_time == 2.5
            assert result.provider == "openrouter"
            assert result.model == "gpt-4"
            assert result.confidence_score == 0.95
            assert result.warnings == []
            assert result.errors == []
            
            # Assert brain service was called
            mock_brain_service.parse_text.assert_called_once_with(self.test_text, "resume")
    
    def test_resume_parse_service(self):
        """Test resume parse service."""
        # Mock resume service
        with patch('backend_app.file_intake.services.brain_parse_service.get_resume_service') as mock_get_resume:
            mock_resume_service = Mock()
            mock_resume_service.parse_text.return_value = {
                "success": True,
                "response": {
                    "contact": {
                        "name": "John Doe",
                        "email": "john.doe@example.com",
                        "phone": "+1 (555) 123-4567"
                    },
                    "experience": [
                        {
                            "company": "Tech Corp",
                            "position": "Senior Software Engineer",
                            "start_date": "2020",
                            "end_date": "Present"
                        }
                    ],
                    "education": [
                        {
                            "institution": "University of Technology",
                            "degree": "Bachelor of Science",
                            "field_of_study": "Computer Science"
                        }
                    ],
                    "skills": [
                        {"name": "Python", "category": "Programming"},
                        {"name": "JavaScript", "category": "Programming"}
                    ],
                    "metadata": {
                        "document_type": "resume",
                        "confidence_score": 0.92,
                        "language": "en"
                    }
                },
                "parse_time": 1.8,
                "provider": "openrouter",
                "model": "gpt-4",
                "confidence_score": 0.92,
                "warnings": ["Some skills were not categorized"],
                "errors": []
            }
            mock_get_resume.return_value = mock_resume_service
            
            # Create service and parse
            service = ResumeParseService(self.config)
            result = service.parse_text(self.test_text, "resume")
            
            # Assert result
            assert result.success is True
            assert result.response["contact"]["name"] == "John Doe"
            assert len(result.response["experience"]) == 1
            assert len(result.response["education"]) == 1
            assert len(result.response["skills"]) == 2
            assert result.response["metadata"]["document_type"] == "resume"
            assert result.response["metadata"]["confidence_score"] == 0.92
            assert result.parse_time == 1.8
            assert result.provider == "openrouter"
            assert result.model == "gpt-4"
            assert result.confidence_score == 0.92
            assert result.warnings == ["Some skills were not categorized"]
            assert result.errors == []
            
            # Assert resume service was called
            mock_resume_service.parse_text.assert_called_once_with(self.test_text, "resume")
    
    def test_document_parse_service(self):
        """Test document parse service."""
        # Mock document service
        with patch('backend_app.file_intake.services.brain_parse_service.get_document_service') as mock_get_doc:
            mock_doc_service = Mock()
            mock_doc_service.parse_text.return_value = {
                "success": True,
                "response": {
                    "title": "Document Title",
                    "summary": "This is a document summary",
                    "key_points": ["Point 1", "Point 2", "Point 3"],
                    "metadata": {
                        "document_type": "general",
                        "confidence_score": 0.88,
                        "language": "en"
                    }
                },
                "parse_time": 1.2,
                "provider": "openrouter",
                "model": "gpt-4",
                "confidence_score": 0.88,
                "warnings": [],
                "errors": []
            }
            mock_get_doc.return_value = mock_doc_service
            
            # Create service and parse
            service = DocumentParseService(self.config)
            result = service.parse_text(self.test_text, "document")
            
            # Assert result
            assert result.success is True
            assert result.response["title"] == "Document Title"
            assert result.response["summary"] == "This is a document summary"
            assert len(result.response["key_points"]) == 3
            assert result.response["metadata"]["document_type"] == "general"
            assert result.response["metadata"]["confidence_score"] == 0.88
            assert result.parse_time == 1.2
            assert result.provider == "openrouter"
            assert result.model == "gpt-4"
            assert result.confidence_score == 0.88
            assert result.warnings == []
            assert result.errors == []
            
            # Assert document service was called
            mock_doc_service.parse_text.assert_called_once_with(self.test_text, "document")
    
    def test_composite_parse_service(self):
        """Test composite parse service."""
        # Mock parse services
        with patch('backend_app.file_intake.services.brain_parse_service.get_brain_service') as mock_brain, \
             patch('backend_app.file_intake.services.brain_parse_service.get_resume_service') as mock_resume, \
             patch('backend_app.file_intake.services.brain_parse_service.get_document_service') as mock_doc:
            
            mock_brain_service = Mock()
            mock_brain_service.parse_text.return_value = {
                "success": True,
                "response": {
                    "contact": {"name": "John Doe"},
                    "metadata": {"document_type": "resume", "confidence_score": 0.95}
                },
                "parse_time": 2.5,
                "provider": "openrouter",
                "model": "gpt-4",
                "confidence_score": 0.95,
                "warnings": [],
                "errors": []
            }
            
            mock_resume_service = Mock()
            mock_resume_service.parse_text.return_value = {
                "success": True,
                "response": {
                    "contact": {"name": "John Doe"},
                    "metadata": {"document_type": "resume", "confidence_score": 0.92}
                },
                "parse_time": 1.8,
                "provider": "openrouter",
                "model": "gpt-4",
                "confidence_score": 0.92,
                "warnings": [],
                "errors": []
            }
            
            mock_doc_service = Mock()
            mock_doc_service.parse_text.return_value = {
                "success": True,
                "response": {
                    "title": "Document Title",
                    "metadata": {"document_type": "general", "confidence_score": 0.88}
                },
                "parse_time": 1.2,
                "provider": "openrouter",
                "model": "gpt-4",
                "confidence_score": 0.88,
                "warnings": [],
                "errors": []
            }
            
            mock_brain.return_value = mock_brain_service
            mock_resume.return_value = mock_resume_service
            mock_doc.return_value = mock_doc_service
            
            # Create service and parse
            service = CompositeParseService(self.config)
            result = service.parse_text(self.test_text, "resume")
            
            # Assert result - should use brain service for resume
            assert result.success is True
            assert result.response["contact"]["name"] == "John Doe"
            assert result.response["metadata"]["document_type"] == "resume"
            assert result.response["metadata"]["confidence_score"] == 0.95
            assert result.parse_time == 2.5
            assert result.provider == "openrouter"
            assert result.model == "gpt-4"
            assert result.confidence_score == 0.95
            assert result.warnings == []
            assert result.errors == []
            
            # Assert brain service was called (for resume)
            mock_brain_service.parse_text.assert_called_once_with(self.test_text, "resume")
            mock_resume_service.parse_text.assert_not_called()
            mock_doc_service.parse_text.assert_not_called()
    
    def test_get_parse_service_brain(self):
        """Test getting parse service for brain."""
        # Mock config
        with patch('backend_app.file_intake.services.brain_parse_service.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.parsing.engines = ["brain"]
            mock_get_config.return_value = mock_config
            
            service = get_brain_parse_service(mock_config)
            
            # Should return brain service
            assert isinstance(service, BrainParseService)
    
    def test_get_parse_service_resume(self):
        """Test getting parse service for resume."""
        # Mock config
        with patch('backend_app.file_intake.services.brain_parse_service.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.parsing.engines = ["resume"]
            mock_get_config.return_value = mock_config
            
            service = get_brain_parse_service(mock_config)
            
            # Should return resume service
            assert isinstance(service, ResumeParseService)
    
    def test_get_parse_service_document(self):
        """Test getting parse service for document."""
        # Mock config
        with patch('backend_app.file_intake.services.brain_parse_service.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.parsing.engines = ["document"]
            mock_get_config.return_value = mock_config
            
            service = get_brain_parse_service(mock_config)
            
            # Should return document service
            assert isinstance(service, DocumentParseService)
    
    def test_get_parse_service_composite(self):
        """Test getting parse service for composite."""
        # Mock config
        with patch('backend_app.file_intake.services.brain_parse_service.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.parsing.engines = ["brain", "resume", "document"]
            mock_get_config.return_value = mock_config
            
            service = get_brain_parse_service(mock_config)
            
            # Should return composite service
            assert isinstance(service, CompositeParseService)
    
    def test_parse_text_empty(self):
        """Test parsing empty text."""
        # Mock parse service
        with patch('backend_app.file_intake.services.brain_parse_service.get_brain_parse_service') as mock_get_service:
            mock_service = Mock()
            mock_service.parse_text.return_value = {
                "success": False,
                "response": None,
                "parse_time": 0.1,
                "provider": "openrouter",
                "model": "gpt-4",
                "confidence_score": 0.0,
                "warnings": [],
                "errors": ["Empty text provided"]
            }
            mock_get_service.return_value = mock_service
            
            # Parse empty text
            result = mock_service.parse_text("", "resume")
            
            # Assert result
            assert result.success is False
            assert result.response is None
            assert result.parse_time == 0.1
            assert result.provider == "openrouter"
            assert result.model == "gpt-4"
            assert result.confidence_score == 0.0
            assert result.warnings == []
            assert result.errors == ["Empty text provided"]
    
    def test_parse_text_whitespace(self):
        """Test parsing whitespace-only text."""
        # Mock parse service
        with patch('backend_app.file_intake.services.brain_parse_service.get_brain_parse_service') as mock_get_service:
            mock_service = Mock()
            mock_service.parse_text.return_value = {
                "success": False,
                "response": None,
                "parse_time": 0.1,
                "provider": "openrouter",
                "model": "gpt-4",
                "confidence_score": 0.0,
                "warnings": [],
                "errors": ["Only whitespace provided"]
            }
            mock_get_service.return_value = mock_service
            
            # Parse whitespace text
            result = mock_service.parse_text("   \n\t  ", "resume")
            
            # Assert result
            assert result.success is False
            assert result.response is None
            assert result.parse_time == 0.1
            assert result.provider == "openrouter"
            assert result.model == "gpt-4"
            assert result.confidence_score == 0.0
            assert result.warnings == []
            assert result.errors == ["Only whitespace provided"]
    
    def test_parse_text_error(self):
        """Test parsing with error."""
        # Mock parse service
        with patch('backend_app.file_intake.services.brain_parse_service.get_brain_parse_service') as mock_get_service:
            mock_service = Mock()
            mock_service.parse_text.return_value = {
                "success": False,
                "response": None,
                "parse_time": 0.5,
                "provider": "openrouter",
                "model": "gpt-4",
                "confidence_score": 0.0,
                "warnings": [],
                "errors": ["Parsing failed: Invalid document format"]
            }
            mock_get_service.return_value = mock_service
            
            # Parse with error
            result = mock_service.parse_text(self.test_text, "resume")
            
            # Assert result
            assert result.success is False
            assert result.response is None
            assert result.parse_time == 0.5
            assert result.provider == "openrouter"
            assert result.model == "gpt-4"
            assert result.confidence_score == 0.0
            assert result.warnings == []
            assert result.errors == ["Parsing failed: Invalid document format"]
    
    def test_parse_text_timeout(self):
        """Test parsing with timeout."""
        # Mock parse service
        with patch('backend_app.file_intake.services.brain_parse_service.get_brain_parse_service') as mock_get_service:
            mock_service = Mock()
            mock_service.parse_text.side_effect = TimeoutError("Parsing timed out")
            mock_get_service.return_value = mock_service
            
            # Parse with timeout
            with pytest.raises(TimeoutError):
                mock_service.parse_text(self.test_text, "resume")
    
    def test_parse_text_large_document(self):
        """Test parsing large document."""
        # Create large text
        large_text = self.test_text * 100  # 100x larger
        
        # Mock parse service
        with patch('backend_app.file_intake.services.brain_parse_service.get_brain_parse_service') as mock_get_service:
            mock_service = Mock()
            mock_service.parse_text.return_value = {
                "success": True,
                "response": {
                    "contact": {"name": "John Doe"},
                    "metadata": {"document_type": "resume", "confidence_score": 0.85}
                },
                "parse_time": 5.0,
                "provider": "openrouter",
                "model": "gpt-4",
                "confidence_score": 0.85,
                "warnings": ["Large document processing took longer than expected"],
                "errors": []
            }
            mock_get_service.return_value = mock_service
            
            # Parse large text
            result = mock_service.parse_text(large_text, "resume")
            
            # Assert result
            assert result.success is True
            assert result.response["contact"]["name"] == "John Doe"
            assert result.response["metadata"]["document_type"] == "resume"
            assert result.response["metadata"]["confidence_score"] == 0.85
            assert result.parse_time == 5.0
            assert result.provider == "openrouter"
            assert result.model == "gpt-4"
            assert result.confidence_score == 0.85
            assert result.warnings == ["Large document processing took longer than expected"]
            assert result.errors == []
    
    def test_parse_text_unicode(self):
        """Test parsing Unicode text."""
        # Create Unicode text
        unicode_text = """
        张三
        软件工程师
        
        邮箱: zhangsan@example.com
        电话: +86 138 0000 0000
        
        经验
        高级软件工程师 | 科技公司 | 2020 - 至今
        - 使用React和Node.js开发Web应用
        - 领导5人开发团队
        - 实施微服务架构
        """
        
        # Mock parse service
        with patch('backend_app.file_intake.services.brain_parse_service.get_brain_parse_service') as mock_get_service:
            mock_service = Mock()
            mock_service.parse_text.return_value = {
                "success": True,
                "response": {
                    "contact": {
                        "name": "张三",
                        "email": "zhangsan@example.com",
                        "phone": "+86 138 0000 0000"
                    },
                    "experience": [
                        {
                            "company": "科技公司",
                            "position": "高级软件工程师",
                            "start_date": "2020",
                            "end_date": "至今"
                        }
                    ],
                    "metadata": {
                        "document_type": "resume",
                        "confidence_score": 0.90,
                        "language": "zh"
                    }
                },
                "parse_time": 3.0,
                "provider": "openrouter",
                "model": "gpt-4",
                "confidence_score": 0.90,
                "warnings": [],
                "errors": []
            }
            mock_get_service.return_value = mock_service
            
            # Parse Unicode text
            result = mock_service.parse_text(unicode_text, "resume")
            
            # Assert result
            assert result.success is True
            assert result.response["contact"]["name"] == "张三"
            assert result.response["contact"]["email"] == "zhangsan@example.com"
            assert result.response["contact"]["phone"] == "+86 138 0000 0000"
            assert len(result.response["experience"]) == 1
            assert result.response["metadata"]["document_type"] == "resume"
            assert result.response["metadata"]["confidence_score"] == 0.90
            assert result.response["metadata"]["language"] == "zh"
            assert result.parse_time == 3.0
            assert result.provider == "openrouter"
            assert result.model == "gpt-4"
            assert result.confidence_score == 0.90
            assert result.warnings == []
            assert result.errors == []
    
    def test_parse_text_invalid_document_type(self):
        """Test parsing with invalid document type."""
        # Mock parse service
        with patch('backend_app.file_intake.services.brain_parse_service.get_brain_parse_service') as mock_get_service:
            mock_service = Mock()
            mock_service.parse_text.return_value = {
                "success": False,
                "response": None,
                "parse_time": 0.2,
                "provider": "openrouter",
                "model": "gpt-4",
                "confidence_score": 0.0,
                "warnings": [],
                "errors": ["Invalid document type: invalid_type"]
            }
            mock_get_service.return_value = mock_service
            
            # Parse with invalid document type
            result = mock_service.parse_text(self.test_text, "invalid_type")
            
            # Assert result
            assert result.success is False
            assert result.response is None
            assert result.parse_time == 0.2
            assert result.provider == "openrouter"
            assert result.model == "gpt-4"
            assert result.confidence_score == 0.0
            assert result.warnings == []
            assert result.errors == ["Invalid document type: invalid_type"]
    
    def test_parse_text_confidence_threshold(self):
        """Test parsing with confidence threshold."""
        # Mock parse service with low confidence
        with patch('backend_app.file_intake.services.brain_parse_service.get_brain_parse_service') as mock_get_service:
            mock_service = Mock()
            mock_service.parse_text.return_value = {
                "success": True,
                "response": {
                    "contact": {"name": "John Doe"},
                    "metadata": {"document_type": "resume", "confidence_score": 0.60}
                },
                "parse_time": 1.5,
                "provider": "openrouter",
                "model": "gpt-4",
                "confidence_score": 0.60,
                "warnings": ["Low confidence score: 0.60"],
                "errors": []
            }
            mock_get_service.return_value = mock_service
            
            # Parse with low confidence
            result = mock_service.parse_text(self.test_text, "resume")
            
            # Assert result
            assert result.success is True
            assert result.response["contact"]["name"] == "John Doe"
            assert result.response["metadata"]["document_type"] == "resume"
            assert result.response["metadata"]["confidence_score"] == 0.60
            assert result.parse_time == 1.5
            assert result.provider == "openrouter"
            assert result.model == "gpt-4"
            assert result.confidence_score == 0.60
            assert result.warnings == ["Low confidence score: 0.60"]
            assert result.errors == []