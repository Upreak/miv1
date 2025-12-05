"""
Test Extraction API - Comprehensive Test Suite

Tests the POST /api/v1/extraction/run endpoint according to specification.
"""
import pytest
import json
import tempfile
import os
import sqlite3
from pathlib import Path
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Import the extraction router and app
from backend_app.api.v1.extraction import router
from backend_app.main import app

# Create test client with the extraction router
client = TestClient(app)
app.include_router(router, prefix="/api/v1/extraction")

class TestExtractionAPI:
    """Comprehensive test suite for extraction API endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for tests"""
        # Ensure test files directory exists
        self.test_files_dir = Path("Backend/backend_app/tests/extraction/files")
        self.test_files_dir.mkdir(parents=True, exist_ok=True)
        
        # Ensure logs directory exists for logbook tests
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        
        yield
        
        # Cleanup: remove any temp files created during tests
        temp_dir = Path("temp_extractions")
        if temp_dir.exists():
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def create_test_file(self, filename: str, content: bytes, content_type: str):
        """Helper to create test files"""
        file_path = self.test_files_dir / filename
        file_path.write_bytes(content)
        return file_path
    
    # Functional Tests
    def test_pdf_text_resume_extraction(self):
        """Test extraction of text from PDF resume"""
        # Create a minimal PDF with text content
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
/Resources <<
/Font <<
/F1 5 0 R
>>
>>
>>
endobj

4 0 obj
<<
/Length 120
>>
stream
BT
/F1 12 Tf
50 700 Td
(John Doe) Tj
0 -20 Td
(Senior Software Engineer) Tj
0 -20 Td
(Email: john.doe@email.com) Tj
0 -20 Td
(Experience: 5 years in Python development) Tj
ET
endstream
endobj

5 0 obj
<<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
endobj

xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000264 00000 n 
0000000469 00000 n 
trailer
<<
/Size 6
/Root 1 0 R
>>
startxref
577
%%EOF"""
        
        test_file = self.create_test_file("sample_text_pdf.pdf", pdf_content, "application/pdf")
        
        with open(test_file, "rb") as f:
            response = client.post(
                "/api/v1/extraction/run",
                files={"file": f},
                data={"document_type": "resume"}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "success" in data
        assert "document_type" in data
        assert "file_name" in data
        assert "file_size" in data
        assert "module_used" in data
        assert "text" in data
        assert "score" in data
        assert "attempts" in data
        assert "metadata" in data
        assert "log_id" in data
        
        # Validate specific values
        assert data["document_type"] == "resume"
        assert data["file_name"] == "sample_text_pdf.pdf"
        assert isinstance(data["file_size"], int)
        assert data["file_size"] > 0
        assert isinstance(data["success"], bool)
        assert isinstance(data["score"], (int, float))
        assert isinstance(data["attempts"], list)
        assert data["metadata"] == {}
        assert isinstance(data["log_id"], int)
    
    def test_scanned_pdf_ocr_extraction(self):
        """Test extraction from scanned PDF using OCR"""
        # Create a minimal PDF that should trigger OCR
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Scanned Document) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000264 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
377
%%EOF"""
        
        test_file = self.create_test_file("sample_scanned_pdf.pdf", pdf_content, "application/pdf")
        
        with open(test_file, "rb") as f:
            response = client.post(
                "/api/v1/extraction/run",
                files={"file": f},
                data={"document_type": "resume"}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        # Basic validation
        assert "success" in data
        assert data["document_type"] == "resume"
        assert data["file_name"] == "sample_scanned_pdf.pdf"
    
    def test_jpg_resume_extraction(self):
        """Test extraction from JPG image"""
        # Create minimal JPG content (1x1 pixel red image)
        jpg_content = b"\xff\xd8\xff\xe0\x00\x10\x4a\x46\x49\x46\x00\x01\x01\x01\x00\x48\x00\x48\x00\x00\xff\xdb\x00\x43\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\x09\x09\x08\x0a\x0c\x14\x0d\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c\x20\x24\x2e\x27\x20\x22\x2c\x23\x1c\x1c\x28\x37\x29\x2c\x30\x31\x34\x34\x34\x1f\x27\x39\x3d\x38\x32\x3c\x2e\x33\x34\x32\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xb2\x80\x00\x00\x00\x00\xff\xd9"
        
        test_file = self.create_test_file("sample_resume.jpg", jpg_content, "image/jpeg")
        
        with open(test_file, "rb") as f:
            response = client.post(
                "/api/v1/extraction/run",
                files={"file": f},
                data={"document_type": "resume"}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        # Basic validation
        assert "success" in data
        assert data["document_type"] == "resume"
        assert data["file_name"] == "sample_resume.jpg"
    
    def test_multipage_pdf_extraction(self):
        """Test extraction from multi-page PDF"""
        # Create a minimal multi-page PDF
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R 4 0 R]
/Count 2
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 5 0 R
>>
endobj

4 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 6 0 R
>>
endobj

5 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Page 1 Content) Tj
ET
endstream
endobj

6 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Page 2 Content) Tj
ET
endstream
endobj

xref
0 7
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000101 00000 n 
0000000164 00000 n 
0000000227 00000 n 
0000000330 00000 n 
trailer
<<
/Size 7
/Root 1 0 R
>>
startxref
433
%%EOF"""
        
        test_file = self.create_test_file("multipage_test.pdf", pdf_content, "application/pdf")
        
        with open(test_file, "rb") as f:
            response = client.post(
                "/api/v1/extraction/run",
                files={"file": f},
                data={"document_type": "resume"}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        # Basic validation
        assert "success" in data
        assert data["document_type"] == "resume"
        assert data["file_name"] == "multipage_test.pdf"
    
    # Document Type Tests
    def test_document_type_resume_vs_job_description(self):
        """Test that only document_type field changes between same file"""
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test Document) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000264 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
377
%%EOF"""
        
        test_file = self.create_test_file("test_document.pdf", pdf_content, "application/pdf")
        
        # Test with document_type=resume
        with open(test_file, "rb") as f:
            response1 = client.post(
                "/api/v1/extraction/run",
                files={"file": f},
                data={"document_type": "resume"}
            )
        
        assert response1.status_code == 200
        data1 = response1.json()
        
        # Test with document_type=job_description
        with open(test_file, "rb") as f:
            response2 = client.post(
                "/api/v1/extraction/run",
                files={"file": f},
                data={"document_type": "job_description"}
            )
        
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Verify only document_type changed
        assert data1["file_name"] == data2["file_name"]
        assert data1["file_size"] == data2["file_size"]
        assert data1["text"] == data2["text"]
        assert data1["success"] == data2["success"]
        assert data1["module_used"] == data2["module_used"]
        assert data1["score"] == data2["score"]
        
        # Verify document_type changed
        assert data1["document_type"] == "resume"
        assert data2["document_type"] == "job_description"
    
    # Error Tests
    def test_no_file_provided(self):
        """Test error when no file is provided"""
        response = client.post(
            "/api/v1/extraction/run",
            data={"document_type": "resume"}
        )
        
        assert response.status_code == 422  # Validation error for missing file
    
    def test_invalid_document_type(self):
        """Test error when invalid document_type is provided"""
        # Create minimal test file
        test_content = b"test content"
        test_file = self.create_test_file("test.txt", test_content, "text/plain")
        
        with open(test_file, "rb") as f:
            response = client.post(
                "/api/v1/extraction/run",
                files={"file": f},
                data={"document_type": "invalid_type"}
            )
        
        assert response.status_code == 400
        data = response.json()
        assert "Invalid document_type" in data["detail"]
    
    def test_unsupported_file_type(self):
        """Test error when unsupported file type is provided"""
        # Create a text file (unsupported type)
        test_content = b"This is a text file content"
        test_file = self.create_test_file("test.txt", test_content, "text/plain")
        
        with open(test_file, "rb") as f:
            response = client.post(
                "/api/v1/extraction/run",
                files={"file": f},
                data={"document_type": "resume"}
            )
        
        assert response.status_code == 400
        data = response.json()
        assert "Unsupported file type" in data["detail"]
    
    def test_invalid_metadata_json(self):
        """Test error when invalid metadata JSON is provided"""
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000264 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
377
%%EOF"""
        
        test_file = self.create_test_file("test.pdf", pdf_content, "application/pdf")
        
        with open(test_file, "rb") as f:
            response = client.post(
                "/api/v1/extraction/run",
                files={"file": f},
                data={
                    "document_type": "resume",
                    "metadata": "invalid json"
                }
            )
        
        assert response.status_code == 400
        data = response.json()
        assert "Invalid metadata JSON" in data["detail"]
    
    def test_file_too_large(self):
        """Test error when file exceeds size limit"""
        # Create a file larger than 10MB limit (11MB)
        large_content = b"x" * (11 * 1024 * 1024)
        test_file = self.create_test_file("large_file.pdf", large_content, "application/pdf")
        
        with open(test_file, "rb") as f:
            response = client.post(
                "/api/v1/extraction/run",
                files={"file": f},
                data={"document_type": "resume"}
            )
        
        assert response.status_code == 400
        data = response.json()
        assert "File too large" in data["detail"]
    
    # Logbook Test
    def test_extraction_logbook_entry(self):
        """Test that extraction creates logbook entry"""
        # Clean up any existing logbook for this test
        logbook_path = Path("logs/extraction_logbook.db")
        if logbook_path.exists():
            logbook_path.unlink()
        
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test Log) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000264 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
377
%%EOF"""
        
        test_file = self.create_test_file("log_test.pdf", pdf_content, "application/pdf")
        
        with open(test_file, "rb") as f:
            response = client.post(
                "/api/v1/extraction/run",
                files={"file": f},
                data={"document_type": "resume"}
            )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify logbook entry was created
        assert logbook_path.exists()
        
        # Verify logbook entry contains expected fields
        with sqlite3.connect(str(logbook_path)) as conn:
            cursor = conn.execute(
                "SELECT attempts_json, quality_score, module_used FROM extraction_logs WHERE id = ?",
                (data["log_id"],)
            )
            row = cursor.fetchone()
            assert row is not None
            
            attempts_json, quality_score, module_used = row
            assert attempts_json is not None
            assert quality_score is not None
            assert module_used is not None
    
    # Output Contract Test
    def test_output_contract_validation(self):
        """Test that output matches exact specification contract"""
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Contract Test) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000264 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
377
%%EOF"""
        
        test_file = self.create_test_file("contract_test.pdf", pdf_content, "application/pdf")
        
        with open(test_file, "rb") as f:
            response = client.post(
                "/api/v1/extraction/run",
                files={"file": f},
                data={
                    "document_type": "resume",
                    "metadata": json.dumps({"test": "value"})
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate all required fields are present and of correct types
        assert isinstance(data["success"], bool)
        assert isinstance(data["document_type"], str)
        assert isinstance(data["file_name"], str)
        assert isinstance(data["file_size"], int)
        assert isinstance(data["module_used"], str)
        assert isinstance(data["text"], str)
        assert isinstance(data["score"], (int, float))
        assert isinstance(data["attempts"], list)
        assert isinstance(data["metadata"], dict)
        assert isinstance(data["log_id"], int)
        
        # Validate specific values
        assert data["document_type"] == "resume"
        assert data["file_name"] == "contract_test.pdf"
        assert data["metadata"] == {"test": "value"}
        assert data["log_id"] > 0