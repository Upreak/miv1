#!/usr/bin/env python3
"""
Simple test runner to validate the resume processing workflow test script.
This script performs basic validation before running the full test.
"""

import sys
import os
from pathlib import Path

def validate_environment():
    """Validate the environment before running tests"""
    print("🔍 Validating environment...")
    
    # Check if we're in the right directory
    base_path = Path.cwd()
    print(f"   Base path: {base_path}")
    
    # Check if Backend directory exists
    backend_path = base_path / "Backend" / "backend_app"
    if backend_path.exists():
        print(f"   ✅ Backend path exists: {backend_path}")
    else:
        print(f"   ❌ Backend path missing: {backend_path}")
        return False
    
    # Check if Resumes directory exists
    resumes_path = base_path / "Resumes"
    if resumes_path.exists():
        print(f"   ✅ Resumes path exists: {resumes_path}")
        resume_files = list(resumes_path.glob("*.{pdf,docx,doc,txt}"))
        print(f"   📄 Found {len(resume_files)} resume files")
    else:
        print(f"   ❌ Resumes path missing: {resumes_path}")
        return False
    
    # Check if test script exists
    test_script = base_path / "test_resume_processing_workflow.py"
    if test_script.exists():
        print(f"   ✅ Test script exists: {test_script}")
    else:
        print(f"   ❌ Test script missing: {test_script}")
        return False
    
    print("   ✅ Environment validation passed!")
    return True

def run_basic_import_test():
    """Test basic imports to ensure modules are accessible"""
    print("\n🔍 Testing basic imports...")
    
    try:
        # Test sys.path manipulation
        base_path = Path.cwd()
        backend_path = base_path / "Backend" / "backend_app"
        sys.path.insert(0, str(backend_path))
        
        # Test text extraction import
        try:
            from text_extraction.consolidated_extractor import extract_text_from_file
            print("   ✅ Text extraction module imported successfully")
        except ImportError as e:
            print(f"   ⚠️  Text extraction import failed: {e}")
            print("      This is expected if dependencies are not installed")
        
        # Test brain module import
        try:
            from brain_module.brain_core import BrainCore
            print("   ✅ Brain module imported successfully")
        except ImportError as e:
            print(f"   ⚠️  Brain module import failed: {e}")
            print("      This is expected if dependencies are not installed")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Import test failed: {e}")
        return False

def main():
    """Main test runner"""
    print("🧪 Resume Processing Workflow Test Runner")
    print("=" * 60)
    
    # Step 1: Validate environment
    if not validate_environment():
        print("\n❌ Environment validation failed. Please check the setup.")
        sys.exit(1)
    
    # Step 2: Test basic imports
    run_basic_import_test()
    
    print("\n✅ Basic validation completed successfully!")
    print("\n🚀 You can now run the full test with:")
    print("   python test_resume_processing_workflow.py")
    
    print("\n📝 Notes:")
    print("   - Import failures are expected if dependencies are not installed")
    print("   - The test will still run and generate folder maps")
    print("   - Processing failures will be logged and reported")

if __name__ == "__main__":
    main()