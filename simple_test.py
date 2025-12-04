#!/usr/bin/env python3
"""
Simple test script to verify resume processing functionality
"""

import os
import json
import uuid
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import Brain Module
from Backend.backend_app.brain_module.brain_service import BrainSvc

# Simple text extraction function to read pre-extracted text files
def extract_text_from_file(file_path: str) -> str:
    """
    Simple function to read pre-extracted text files from the text_extract directory.
    This bypasses the complex extraction process and uses existing extracted files.
    """
    try:
        # Convert the original file path to the corresponding extracted text file path
        original_path = Path(file_path)
        filename = original_path.name
        
        # Look for the extracted file in the text_extract directory
        text_extract_dir = Path("Backend/text_extract")
        extracted_file = text_extract_dir / f"{filename}_extracted.txt"
        
        if extracted_file.exists():
            with open(extracted_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"SUCCESS: Loaded pre-extracted text from: {extracted_file.name}")
                return content
        else:
            # Try alternative naming patterns
            alternative_names = [
                f"{filename.replace(' ', '_').replace('-', '_')}_extracted.txt",
                f"{filename.split('.')[0]}_extracted.txt",
                f"{filename.lower().replace(' ', '_').replace('-', '_')}_extracted.txt"
            ]
            
            for alt_name in alternative_names:
                alt_file = text_extract_dir / alt_name
                if alt_file.exists():
                    with open(alt_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        print(f"SUCCESS: Loaded pre-extracted text from: {alt_file.name}")
                        return content
            
            print(f"WARNING: No pre-extracted text file found for {filename}")
            return f"# WARNING: Could not find pre-extracted text file for {filename}"
            
    except Exception as e:
        print(f"ERROR: Failed to read pre-extracted text file: {e}")
        return f"# ERROR: Failed to read pre-extracted text: {e}"

def main():
    print("=== Simple Resume Processing Test ===")
    
    # Test with one resume file first
    resume_dir = Path("Resumes")
    if not resume_dir.exists():
        print("❌ ERROR: 'Resumes' directory not found.")
        return
    
    # Get the first resume file
    resumes = list(resume_dir.glob("*"))
    if not resumes:
        print("❌ No files found in the 'Resumes' directory.")
        return
    
    test_file = resumes[0]  # Test with first file
    print(f"Testing with file: {test_file.name}")
    
    # Extract text
    extracted_text = extract_text_from_file(str(test_file))
    if not extracted_text.strip() or extracted_text.startswith("# WARNING") or extracted_text.startswith("# ERROR"):
        print(f"FAILED: Could not extract text from {test_file.name}")
        return
    
    # Show snippet
    snippet = extracted_text[:200].replace("\n", " ")
    print(f"Text snippet (200 chars): {snippet}")
    
    # Create QID
    qid = f"test-{uuid.uuid4()}"
    
    # Prepare Brain module request
    qitem = {
        "qid": qid,
        "text": extracted_text,
        "intake_type": "resume",
        "meta": {
            "filename": test_file.name,
            "source": "simple_test"
        }
    }
    
    # Call Brain Module
    try:
        print("\nSending to Brain Module...")
        result = BrainSvc.process(qitem)
        
        print(f"SUCCESS: Brain Module success: {result.get('success')}")
        print(f"SUCCESS: Provider used: {result.get('provider')}")
        print(f"SUCCESS: Model: {result.get('model')}")
        print(f"SUCCESS: Response length: {len(result.get('response', ''))}")
        
        # Save result
        result_data = {
            "filename": test_file.name,
            "qid": qid,
            "brain_output": result
        }
        
        # Save JSON result
        with open("simple_test_result.json", "w", encoding="utf-8") as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        # Save TXT result
        with open("simple_test_result.txt", "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("RESUME PROCESSING TEST RESULT\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Filename: {test_file.name}\n")
            f.write(f"QID: {qid}\n")
            f.write(f"Provider: {result.get('provider')}\n")
            f.write(f"Model: {result.get('model')}\n")
            f.write(f"Success: {result.get('success')}\n")
            f.write(f"Response Length: {len(result.get('response', ''))} characters\n\n")
            
            f.write("=" * 60 + "\n")
            f.write("BRAIN MODULE RESPONSE\n")
            f.write("=" * 60 + "\n\n")
            f.write(result.get('response', ''))
        
        print("SUCCESS: Result saved to simple_test_result.json and simple_test_result.txt")
        
    except Exception as e:
        print(f"FAILED: Brain module error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()