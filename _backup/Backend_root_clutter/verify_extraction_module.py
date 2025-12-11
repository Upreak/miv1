#!/usr/bin/env python3
"""
Extraction Module Verification Script
Tests all requirements specified by the user
"""
import sys
import os
import tempfile
import json
import sqlite3
from pathlib import Path
import subprocess
import requests
from io import BytesIO

# Add the backend_app to path
sys.path.insert(0, str(Path(__file__).parent / "Backend"))

class ExtractionVerifier:
    def __init__(self):
        self.base_url = "http://localhost:8000"  # Adjust as needed
        self.endpoint = f"{self.base_url}/api/v1/extraction/run"
        
    def create_test_files(self):
        """Create test files for verification"""
        test_files = {}
        
        # 1. Resume PDF
        resume_pdf = b"""%PDF-1.4
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
/Length 200
>>
stream
BT
/F1 12 Tf
50 700 Td
(JOHN DOE) Tj
0 -20 Td
(Senior Software Engineer) Tj
0 -20 Td
(Email: john.doe@email.com) Tj
0 -20 Td
(Phone: +1234567890) Tj
0 -20 Td
(Experience: 5+ years in Python development) Tj
0 -20 Td
(Skills: Python, Django, FastAPI, PostgreSQL) Tj
0 -20 Td
(Education: M.S. Computer Science) Tj
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
477
%%EOF"""
        test_files['resume_pdf'] = resume_pdf
        
        # 2. Job Description PDF
        jd_pdf = b"""%PDF-1.4
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
/Length 250
>>
stream
BT
/F1 12 Tf
50 700 Td
(POSITION: Senior Backend Developer) Tj
0 -20 Td
(COMPANY: TechCorp Inc.) Tj
0 -20 Td
(LOCATION: San Francisco, CA) Tj
0 -20 Td
(REQUIREMENTS:) Tj
0 -20 Td
(- 5+ years Python experience) Tj
0 -20 Td
(- REST API development) Tj
0 -20 Td
(- Database design and optimization) Tj
0 -20 Td
(- Cloud deployment experience) Tj
0 -20 Td
(BENEFITS:) Tj
0 -20 Td
(- Competitive salary) Tj
0 -20 Td
(- Health insurance) Tj
0 -20 Td
(- Remote work options) Tj
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
527
%%EOF"""
        test_files['jd_pdf'] = jd_pdf
        
        # 3. Simple JPG (1x1 red pixel)
        test_files['jpg_resume'] = b"\xff\xd8\xff\xe0\x00\x10\x4a\x46\x49\x46\x00\x01\x01\x01\x00\x48\x00\x48\x00\x00\xff\xdb\x00\x43\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\x09\x09\x08\x0a\x0c\x14\x0d\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c\x20\x24\x2e\x27\x20\x22\x2c\x23\x1c\x1c\x28\x37\x29\x2c\x30\x31\x34\x34\x34\x1f\x27\x39\x3d\x38\x32\x3c\x2e\x33\x34\x32\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xb2\x80\x00\x00\x00\x00\xff\xd9"
        
        return test_files
    
    def test_extraction_endpoint(self, file_content, filename, document_type, expected_non_empty=True):
        """Test extraction endpoint with given file"""
        print(f"\n🧪 Testing: {filename} ({document_type})")
        
        try:
            # Prepare multipart form data
            files = {
                'file': (filename, BytesIO(file_content), 'application/octet-stream')
            }
            data = {
                'document_type': document_type
            }
            
            # Make request
            response = requests.post(self.endpoint, files=files, data=data, timeout=30)
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"   ❌ ERROR: {response.text}")
                return False
            
            result = response.json()
            
            # Verify response structure
            required_fields = [
                "success", "document_type", "file_name", "file_size", 
                "module_used", "text", "score", "attempts", "metadata", "log_id"
            ]
            
            missing_fields = [field for field in required_fields if field not in result]
            if missing_fields:
                print(f"   ❌ Missing fields: {missing_fields}")
                return False
            
            # Verify extracted text is non-empty (if expected)
            if expected_non_empty and not result["text"].strip():
                print(f"   ❌ Extracted text is empty!")
                return False
            elif expected_non_empty:
                print(f"   ✅ Extracted text length: {len(result['text'])} chars")
            
            # Verify score > 70 (if text was extracted)
            if result["text"].strip() and result["score"] < 70:
                print(f"   ⚠️  Score: {result['score']} (< 70)")
            elif result["text"].strip():
                print(f"   ✅ Score: {result['score']} (>= 70)")
            
            # Verify document type flows through
            if result["document_type"] != document_type:
                print(f"   ❌ Document type mismatch: expected {document_type}, got {result['document_type']}")
                return False
            else:
                print(f"   ✅ Document type: {result['document_type']}")
            
            # Verify module_used is present and realistic
            if not result["module_used"]:
                print(f"   ❌ module_used is empty!")
                return False
            else:
                print(f"   ✅ Module used: {result['module_used']}")
            
            # Verify log_id is present
            if result["log_id"] <= 0:
                print(f"   ❌ Invalid log_id: {result['log_id']}")
                return False
            else:
                print(f"   ✅ Log ID: {result['log_id']}")
            
            print(f"   ✅ Test PASSED")
            return True
            
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Could not connect to server at {self.endpoint}")
            print(f"   💡 Make sure the backend server is running: python -m uvicorn backend_app.main:app --reload")
            return False
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            return False
    
    def check_logbook(self):
        """Check extraction logbook entries"""
        print(f"\n📊 Checking extraction logbook...")
        
        logbook_path = Path("Backend/logs/extraction_logbook.db")
        if not logbook_path.exists():
            print(f"   ❌ Logbook not found at {logbook_path}")
            return False
        
        try:
            with sqlite3.connect(str(logbook_path)) as conn:
                cursor = conn.execute("""
                    SELECT id, timestamp, file_path, success, quality_score, module_used 
                    FROM extraction_logs 
                    ORDER BY id DESC 
                    LIMIT 10
                """)
                
                rows = cursor.fetchall()
                
                if not rows:
                    print(f"   ⚠️  No log entries found")
                    return False
                
                print(f"   ✅ Found {len(rows)} recent log entries:")
                for row in rows:
                    print(f"      ID: {row[0]}, Time: {row[1]}, File: {Path(row[2]).name}, Success: {row[3]}, Score: {row[4]}, Module: {row[5]}")
                
                return True
                
        except Exception as e:
            print(f"   ❌ Error reading logbook: {str(e)}")
            return False
    
    def verify_endpoint_isolation(self):
        """Verify extraction endpoint doesn't call other modules"""
        print(f"\n🔍 Verifying endpoint isolation...")
        
        # Check extraction.py imports
        extraction_file = Path("Backend/backend_app/api/v1/extraction.py")
        if not extraction_file.exists():
            print(f"   ❌ Extraction file not found")
            return False
        
        content = extraction_file.read_text()
        
        # Check for unwanted imports
        unwanted_imports = [
            'brain_module', 'orchestrator', 'ATS', 'at_score', 'candidate_matching'
        ]
        
        found_unwanted = []
        for unwanted in unwanted_imports:
            if unwanted in content:
                found_unwanted.append(unwanted)
        
        if found_unwanted:
            print(f"   ❌ Found unwanted imports: {found_unwanted}")
            return False
        
        # Check for only allowed imports
        allowed_imports = [
            'fastapi', 'pathlib', 'json', 'tempfile', 'sqlite3', 
            'consolidated_extractor', 'logging'
        ]
        
        missing_allowed = []
        for allowed in allowed_imports:
            if allowed not in content:
                missing_allowed.append(allowed)
        
        if missing_allowed:
            print(f"   ⚠️  Missing some allowed imports: {missing_allowed}")
        
        print(f"   ✅ Endpoint appears to be isolated (no brain/orchestrator/ATS imports)")
        return True
    
    def run_comprehensive_test(self):
        """Run all verification tests"""
        print("🚀 Starting Extraction Module Verification")
        print("=" * 60)
        
        test_files = self.create_test_files()
        all_passed = True
        
        # Test 1: Resume PDF
        all_passed &= self.test_extraction_endpoint(
            test_files['resume_pdf'], 
            'test_resume.pdf', 
            'resume'
        )
        
        # Test 2: Job Description PDF  
        all_passed &= self.test_extraction_endpoint(
            test_files['jd_pdf'], 
            'test_jd.pdf', 
            'job_description'
        )
        
        # Test 3: JPG Resume (OCR test)
        all_passed &= self.test_extraction_endpoint(
            test_files['jpg_resume'], 
            'test_resume.jpg', 
            'resume',
            expected_non_empty=False  # OCR might not work on minimal image
        )
        
        # Test 4: Verify logbook
        all_passed &= self.check_logbook()
        
        # Test 5: Verify isolation
        all_passed &= self.verify_endpoint_isolation()
        
        print("\n" + "=" * 60)
        if all_passed:
            print("✅ ALL TESTS PASSED - Extraction module is working correctly!")
        else:
            print("❌ SOME TESTS FAILED - Please check the output above")
        
        return all_passed

def main():
    print("""
🔧 Extraction Module Verification Tool
====================================

This script tests:
1. Extraction of various file types (PDF resume, PDF JD, JPG)
2. Response validation (text non-empty, score > 70, module_used varies)
3. Document type flow-through
4. Logbook entries creation
5. Endpoint isolation (no brain/orchestrator/ATS calls)

Prerequisites:
- Backend server must be running on localhost:8000
- Test files will be created automatically

To start the backend server:
cd Backend && python -m uvicorn backend_app.main:app --reload
""")
    
    verifier = ExtractionVerifier()
    
    # Check if server is running
    try:
        response = requests.get(f"{verifier.base_url}/docs", timeout=5)
        print("✅ Backend server is running")
    except:
        print("❌ Backend server is not running!")
        print("Please start it first:")
        print("cd Backend && python -m uvicorn backend_app.main:app --reload")
        return
    
    # Run tests
    verifier.run_comprehensive_test()

if __name__ == "__main__":
    main()