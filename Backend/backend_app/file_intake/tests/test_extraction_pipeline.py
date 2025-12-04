"""
Test suite for extraction pipeline.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from backend_app.file_intake.services.extraction_service import (
    get_extraction_service,
    TextExtractionService,
    PDFExtractionService,
    DocumentExtractionService,
    CompositeExtractionService
)
from backend_app.file_intake.config.intake_config import get_config


class TestExtractionService:
    """Test cases for extraction service."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = get_config()
        self.test_file_content = b"Test file content for extraction"
        self.test_pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n"
        self.test_docx_content = b"PK\x03\x04"  # DOCX header
    
    def test_text_extraction_service(self):
        """Test text extraction service."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
            temp_file.write(self.test_file_content)
            temp_file_path = temp_file.name
        
        try:
            # Mock text extraction
            with patch('backend_app.file_intake.services.extraction_service.extract_text') as mock_extract:
                mock_extract.return_value = {
                    "success": True,
                    "text": "Test file content for extraction",
                    "extraction_time": 0.5,
                    "confidence_score": 0.95,
                    "language": "en",
                    "warnings": [],
                    "errors": []
                }
                
                # Create service and extract
                service = TextExtractionService(self.config)
                result = service.extract_text(temp_file_path)
                
                # Assert result
                assert result.success is True
                assert result.text == "Test file content for extraction"
                assert result.extraction_time == 0.5
                assert result.confidence_score == 0.95
                assert result.language == "en"
                assert result.warnings == []
                assert result.errors == []
                
                # Assert extraction was called
                mock_extract.assert_called_once_with(temp_file_path)
                
        finally:
            # Clean up
            os.unlink(temp_file_path)
    
    def test_pdf_extraction_service(self):
        """Test PDF extraction service."""
        # Create temporary PDF file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(self.test_pdf_content)
            temp_file_path = temp_file.name
        
        try:
            # Mock PDF extraction
            with patch('backend_app.file_intake.services.extraction_service.extract_pdf_text') as mock_extract:
                mock_extract.return_value = {
                    "success": True,
                    "text": "PDF content extracted successfully",
                    "extraction_time": 1.2,
                    "confidence_score": 0.88,
                    "language": "en",
                    "warnings": ["Some text was not recognized"],
                    "errors": []
                }
                
                # Create service and extract
                service = PDFExtractionService(self.config)
                result = service.extract_text(temp_file_path)
                
                # Assert result
                assert result.success is True
                assert result.text == "PDF content extracted successfully"
                assert result.extraction_time == 1.2
                assert result.confidence_score == 0.88
                assert result.language == "en"
                assert result.warnings == ["Some text was not recognized"]
                assert result.errors == []
                
                # Assert extraction was called
                mock_extract.assert_called_once_with(temp_file_path)
                
        finally:
            # Clean up
            os.unlink(temp_file_path)
    
    def test_document_extraction_service(self):
        """Test document extraction service."""
        # Create temporary DOCX file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_file:
            temp_file.write(self.test_docx_content)
            temp_file_path = temp_file.name
        
        try:
            # Mock document extraction
            with patch('backend_app.file_intake.services.extraction_service.extract_document_text') as mock_extract:
                mock_extract.return_value = {
                    "success": True,
                    "text": "Document content extracted successfully",
                    "extraction_time": 0.8,
                    "confidence_score": 0.92,
                    "language": "en",
                    "warnings": [],
                    "errors": []
                }
                
                # Create service and extract
                service = DocumentExtractionService(self.config)
                result = service.extract_text(temp_file_path)
                
                # Assert result
                assert result.success is True
                assert result.text == "Document content extracted successfully"
                assert result.extraction_time == 0.8
                assert result.confidence_score == 0.92
                assert result.language == "en"
                assert result.warnings == []
                assert result.errors == []
                
                # Assert extraction was called
                mock_extract.assert_called_once_with(temp_file_path)
                
        finally:
            # Clean up
            os.unlink(temp_file_path)
    
    def test_composite_extraction_service(self):
        """Test composite extraction service."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
            temp_file.write(self.test_file_content)
            temp_file_path = temp_file.name
        
        try:
            # Mock extraction services
            with patch('backend_app.file_intake.services.extraction_service.get_text_service') as mock_text, \
                 patch('backend_app.file_intake.services.extraction_service.get_pdf_service') as mock_pdf, \
                 patch('backend_app.file_intake.services.extraction_service.get_document_service') as mock_doc:
                
                mock_text_service = Mock()
                mock_text_service.extract_text.return_value = {
                    "success": True,
                    "text": "Test file content for extraction",
                    "extraction_time": 0.5,
                    "confidence_score": 0.95,
                    "language": "en",
                    "warnings": [],
                    "errors": []
                }
                
                mock_pdf_service = Mock()
                mock_pdf_service.extract_text.return_value = {
                    "success": True,
                    "text": "PDF content extracted successfully",
                    "extraction_time": 1.2,
                    "confidence_score": 0.88,
                    "language": "en",
                    "warnings": [],
                    "errors": []
                }
                
                mock_doc_service = Mock()
                mock_doc_service.extract_text.return_value = {
                    "success": True,
                    "text": "Document content extracted successfully",
                    "extraction_time": 0.8,
                    "confidence_score": 0.92,
                    "language": "en",
                    "warnings": [],
                    "errors": []
                }
                
                mock_text.return_value = mock_text_service
                mock_pdf.return_value = mock_pdf_service
                mock_doc.return_value = mock_doc_service
                
                # Create service and extract
                service = CompositeExtractionService(self.config)
                result = service.extract_text(temp_file_path)
                
                # Assert result
                assert result.success is True
                assert result.text == "Test file content for extraction"
                assert result.extraction_time == 0.5
                assert result.confidence_score == 0.95
                assert result.language == "en"
                assert result.warnings == []
                assert result.errors == []
                
                # Assert text service was called (for .txt file)
                mock_text_service.extract_text.assert_called_once_with(temp_file_path)
                mock_pdf_service.extract_text.assert_not_called()
                mock_doc_service.extract_text.assert_not_called()
                
        finally:
            # Clean up
            os.unlink(temp_file_path)
    
    def test_get_extraction_service_text(self):
        """Test getting extraction service for text files."""
        # Mock config
        with patch('backend_app.file_intake.services.extraction_service.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.extraction.engines = ["text"]
            mock_get_config.return_value = mock_config
            
            service = get_extraction_service(mock_config)
            
            # Should return text service
            assert isinstance(service, TextExtractionService)
    
    def test_get_extraction_service_pdf(self):
        """Test getting extraction service for PDF files."""
        # Mock config
        with patch('backend_app.file_intake.services.extraction_service.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.extraction.engines = ["pdf"]
            mock_get_config.return_value = mock_config
            
            service = get_extraction_service(mock_config)
            
            # Should return PDF service
            assert isinstance(service, PDFExtractionService)
    
    def test_get_extraction_service_document(self):
        """Test getting extraction service for document files."""
        # Mock config
        with patch('backend_app.file_intake.services.extraction_service.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.extraction.engines = ["document"]
            mock_get_config.return_value = mock_config
            
            service = get_extraction_service(mock_config)
            
            # Should return document service
            assert isinstance(service, DocumentExtractionService)
    
    def test_get_extraction_service_composite(self):
        """Test getting extraction service for composite."""
        # Mock config
        with patch('backend_app.file_intake.services.extraction_service.get_config') as mock_get_config:
            mock_config = Mock()
            mock_config.extraction.engines = ["text", "pdf", "document"]
            mock_get_config.return_value = mock_config
            
            service = get_extraction_service(mock_config)
            
            # Should return composite service
            assert isinstance(service, CompositeExtractionService)
    
    def test_extract_text_bytes(self):
        """Test extracting text from file bytes."""
        # Mock extraction service
        with patch('backend_app.file_intake.services.extraction_service.get_extraction_service') as mock_get_service:
            mock_service = Mock()
            mock_service.extract_text.return_value = {
                "success": True,
                "text": "Test file content for extraction",
                "extraction_time": 0.5,
                "confidence_score": 0.95,
                "language": "en",
                "warnings": [],
                "errors": []
            }
            mock_get_service.return_value = mock_service
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
                temp_file.write(self.test_file_content)
                temp_file_path = temp_file.name
            
            try:
                # Extract text
                result = mock_service.extract_text(temp_file_path)
                
                # Assert result
                assert result.success is True
                assert result.text == "Test file content for extraction"
                assert result.extraction_time == 0.5
                assert result.confidence_score == 0.95
                assert result.language == "en"
                assert result.warnings == []
                assert result.errors == []
                
            finally:
                # Clean up
                os.unlink(temp_file_path)
    
    def test_extract_text_nonexistent(self):
        """Test extracting text from non-existent file."""
        # Mock extraction service
        with patch('backend_app.file_intake.services.extraction_service.get_extraction_service') as mock_get_service:
            mock_service = Mock()
            mock_service.extract_text.side_effect = FileNotFoundError("File not found")
            mock_get_service.return_value = mock_service
            
            # Try to extract from non-existent file
            with pytest.raises(FileNotFoundError):
                mock_service.extract_text("/nonexistent/file.txt")
    
    def test_extract_text_error(self):
        """Test extracting text with error."""
        # Mock extraction service
        with patch('backend_app.file_intake.services.extraction_service.get_extraction_service') as mock_get_service:
            mock_service = Mock()
            mock_service.extract_text.return_value = {
                "success": False,
                "text": None,
                "extraction_time": 0.5,
                "confidence_score": 0.0,
                "language": None,
                "warnings": [],
                "errors": ["Extraction failed: Invalid file format"]
            }
            mock_get_service.return_value = mock_service
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
                temp_file.write(self.test_file_content)
                temp_file_path = temp_file.name
            
            try:
                # Extract text
                result = mock_service.extract_text(temp_file_path)
                
                # Assert result
                assert result.success is False
                assert result.text is None
                assert result.extraction_time == 0.5
                assert result.confidence_score == 0.0
                assert result.language is None
                assert result.warnings == []
                assert result.errors == ["Extraction failed: Invalid file format"]
                
            finally:
                # Clean up
                os.unlink(temp_file_path)
    
    def test_extract_text_timeout(self):
        """Test extracting text with timeout."""
        # Mock extraction service
        with patch('backend_app.file_intake.services.extraction_service.get_extraction_service') as mock_get_service:
            mock_service = Mock()
            mock_service.extract_text.side_effect = TimeoutError("Extraction timed out")
            mock_get_service.return_value = mock_service
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
                temp_file.write(self.test_file_content)
                temp_file_path = temp_file.name
            
            try:
                # Extract text
                result = mock_service.extract_text(temp_file_path)
                
                # Should handle timeout gracefully
                assert result.success is False
                assert result.errors == ["Extraction timed out"]
                
            finally:
                # Clean up
                os.unlink(temp_file_path)
    
    def test_extract_text_large_file(self):
        """Test extracting text from large file."""
        # Create large file content
        large_content = b"A" * (10 * 1024 * 1024)  # 10MB
        
        # Mock extraction service
        with patch('backend_app.file_intake.services.extraction_service.get_extraction_service') as mock_get_service:
            mock_service = Mock()
            mock_service.extract_text.return_value = {
                "success": True,
                "text": "Large file content extracted successfully",
                "extraction_time": 2.5,
                "confidence_score": 0.85,
                "language": "en",
                "warnings": ["Large file processing took longer than expected"],
                "errors": []
            }
            mock_get_service.return_value = mock_service
            
            # Create temporary large file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
                temp_file.write(large_content)
                temp_file_path = temp_file.name
            
            try:
                # Extract text
                result = mock_service.extract_text(temp_file_path)
                
                # Assert result
                assert result.success is True
                assert result.text == "Large file content extracted successfully"
                assert result.extraction_time == 2.5
                assert result.confidence_score == 0.85
                assert result.language == "en"
                assert result.warnings == ["Large file processing took longer than expected"]
                assert result.errors == []
                
            finally:
                # Clean up
                os.unlink(temp_file_path)
    
    def test_extract_text_unicode(self):
        """Test extracting text with Unicode content."""
        # Create Unicode content
        unicode_content = "Hello 世界! 🌍 This is a test with Unicode characters."
        
        # Mock extraction service
        with patch('backend_app.file_intake.services.extraction_service.get_extraction_service') as mock_get_service:
            mock_service = Mock()
            mock_service.extract_text.return_value = {
                "success": True,
                "text": unicode_content,
                "extraction_time": 0.3,
                "confidence_score": 0.98,
                "language": "en",
                "warnings": [],
                "errors": []
            }
            mock_get_service.return_value = mock_service
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w', encoding='utf-8') as temp_file:
                temp_file.write(unicode_content)
                temp_file_path = temp_file.name
            
            try:
                # Extract text
                result = mock_service.extract_text(temp_file_path)
                
                # Assert result
                assert result.success is True
                assert result.text == unicode_content
                assert result.extraction_time == 0.3
                assert result.confidence_score == 0.98
                assert result.language == "en"
                assert result.warnings == []
                assert result.errors == []
                
            finally:
                # Clean up
                os.unlink(temp_file_path)
    
    def test_extract_text_empty_file(self):
        """Test extracting text from empty file."""
        # Mock extraction service
        with patch('backend_app.file_intake.services.extraction_service.get_extraction_service') as mock_get_service:
            mock_service = Mock()
            mock_service.extract_text.return_value = {
                "success": True,
                "text": "",
                "extraction_time": 0.1,
                "confidence_score": 0.0,
                "language": None,
                "warnings": ["Empty file detected"],
                "errors": []
            }
            mock_get_service.return_value = mock_service
            
            # Create temporary empty file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
                temp_file_path = temp_file.name
            
            try:
                # Extract text
                result = mock_service.extract_text(temp_file_path)
                
                # Assert result
                assert result.success is True
                assert result.text == ""
                assert result.extraction_time == 0.1
                assert result.confidence_score == 0.0
                assert result.language is None
                assert result.warnings == ["Empty file detected"]
                assert result.errors == []
                
            finally:
                # Clean up
                os.unlink(temp_file_path)
    
    def test_extract_text_binary_file(self):
        """Test extracting text from binary file."""
        # Create binary content
        binary_content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        
        # Mock extraction service
        with patch('backend_app.file_intake.services.extraction_service.get_extraction_service') as mock_get_service:
            mock_service = Mock()
            mock_service.extract_text.return_value = {
                "success": False,
                "text": None,
                "extraction_time": 0.2,
                "confidence_score": 0.0,
                "language": None,
                "warnings": [],
                "errors": ["File appears to be binary, no text content extracted"]
            }
            mock_get_service.return_value = mock_service
            
            # Create temporary binary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as temp_file:
                temp_file.write(binary_content)
                temp_file_path = temp_file.name
            
            try:
                # Extract text
                result = mock_service.extract_text(temp_file_path)
                
                # Assert result
                assert result.success is False
                assert result.text is None
                assert result.extraction_time == 0.2
                assert result.confidence_score == 0.0
                assert result.language is None
                assert result.warnings == []
                assert result.errors == ["File appears to be binary, no text content extracted"]
                
            finally:
                # Clean up
                os.unlink(temp_file_path)