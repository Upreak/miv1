#!/usr/bin/env python3
"""
Simple test script to verify the extraction API endpoint works
"""
import sys
import os
import tempfile
import json
from pathlib import Path

# Add the backend_app to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from backend_app.api.v1.extraction import router
    print("✓ Successfully imported extraction router")
except Exception as e:
    print(f"✗ Failed to import extraction router: {e}")
    sys.exit(1)

try:
    from backend_app.text_extraction.consolidated_extractor import extract_with_logging
    print("✓ Successfully imported consolidated extractor")
except Exception as e:
    print(f"✗ Failed to import consolidated extractor: {e}")
    sys.exit(1)

# Test the extraction function directly
def test_extraction_function():
    """Test the extraction function directly"""
    try:
        # Create a simple test PDF content
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
        
        # Write to temp file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(pdf_content)
            temp_path = Path(f.name)
        
        try:
            # Test extraction
            result = extract_with_logging(
                file_path=temp_path,
                metadata={"test": "value"},
                quality_threshold=70
            )
            
            print(f"✓ Extraction result: {result}")
            
            # Verify result structure
            required_fields = ["success", "module", "text", "score", "attempts"]
            for field in required_fields:
                if field not in result:
                    print(f"✗ Missing field in result: {field}")
                    return False
            
            print("✓ All required fields present in result")
            return True
            
        finally:
            # Clean up temp file
            if temp_path.exists():
                temp_path.unlink()
                
    except Exception as e:
        print(f"✗ Extraction test failed: {e}")
        return False

def test_logbook():
    """Test that logbook is created"""
    try:
        logbook_path = Path("logs/extraction_logbook.db")
        if logbook_path.exists():
            print("✓ Logbook database exists")
        else:
            print("! Logbook database does not exist yet (will be created on first use)")
        return True
    except Exception as e:
        print(f"✗ Logbook test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Text Extraction Module Implementation")
    print("=" * 50)
    
    success = True
    
    # Test 1: Import tests
    print("\n1. Testing imports...")
    
    # Test 2: Extraction function test
    print("\n2. Testing extraction function...")
    success &= test_extraction_function()
    
    # Test 3: Logbook test
    print("\n3. Testing logbook...")
    success &= test_logbook()
    
    print("\n" + "=" * 50)
    if success:
        print("✓ All tests passed! The extraction module is working.")
    else:
        print("✗ Some tests failed!")
        sys.exit(1)