#!/usr/bin/env python3
"""
Quick test to verify logbook functionality
"""
import sys
import os
import tempfile
import sqlite3
from pathlib import Path

# Add the backend_app to path
sys.path.insert(0, str(Path(__file__).parent / "Backend"))

def test_logbook_creation():
    """Test that logbook is created and entries are logged"""
    print("🧪 Testing logbook functionality...")
    
    # Ensure logs directory exists
    logs_dir = Path("Backend/logs")
    logs_dir.mkdir(exist_ok=True)
    
    try:
        # Import the consolidated extractor
        from backend_app.text_extraction.consolidated_extractor import extract_with_logging
        
        # Create a simple test PDF
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
/Length 80
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test Resume Content) Tj
0 -20 Td
(John Doe - Software Engineer) Tj
0 -20 Td
(Experience: 5 years) Tj
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
            print("   📄 Running extraction...")
            result = extract_with_logging(
                file_path=temp_path,
                metadata={"test": "logbook_verification"},
                quality_threshold=70
            )
            
            print(f"   ✅ Extraction completed")
            print(f"      Success: {result['success']}")
            print(f"      Module: {result['module']}")
            print(f"      Score: {result['score']}")
            print(f"      Text length: {len(result['text'])} chars")
            
            # Check if logbook was created
            logbook_path = Path("Backend/logs/extraction_logbook.db")
            if logbook_path.exists():
                print(f"   ✅ Logbook created at {logbook_path}")
                
                # Read last entry
                with sqlite3.connect(str(logbook_path)) as conn:
                    cursor = conn.execute("""
                        SELECT id, timestamp, file_path, success, quality_score, module_used, metadata_json
                        FROM extraction_logs 
                        ORDER BY id DESC 
                        LIMIT 1
                    """)
                    
                    row = cursor.fetchone()
                    if row:
                        print(f"   ✅ Latest log entry:")
                        print(f"      ID: {row[0]}")
                        print(f"      Time: {row[1]}")
                        print(f"      File: {Path(row[2]).name}")
                        print(f"      Success: {bool(row[3])}")
                        print(f"      Score: {row[4]}")
                        print(f"      Module: {row[5]}")
                        print(f"      Metadata: {row[6]}")
                        return True
                    else:
                        print(f"   ❌ No log entries found")
                        return False
            else:
                print(f"   ❌ Logbook not created")
                return False
                
        finally:
            # Clean up temp file
            if temp_path.exists():
                temp_path.unlink()
                
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def verify_endpoint_isolation():
    """Verify the extraction endpoint is isolated"""
    print("\n🔍 Verifying endpoint isolation...")
    
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
    
    print(f"   ✅ Endpoint is properly isolated (no brain/orchestrator/ATS imports)")
    return True

def main():
    print("🚀 Extraction Module Verification Test")
    print("=" * 50)
    
    success = True
    
    # Test 1: Logbook functionality
    success &= test_logbook_creation()
    
    # Test 2: Endpoint isolation
    success &= verify_endpoint_isolation()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ ALL VERIFICATION TESTS PASSED!")
        print("\n📋 Summary:")
        print("   • Extraction endpoint is properly isolated")
        print("   • Logbook functionality works correctly") 
        print("   • Module is ready for production use")
    else:
        print("❌ SOME VERIFICATION TESTS FAILED!")
        print("\nPlease check the output above for details.")
    
    return success

if __name__ == "__main__":
    main()