#!/usr/bin/env python3
"""
test_resumes.py
Standalone script to test resume parsing via Brain Module.
"""

import os
import json
import uuid
import getpass
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import Brain Module
from Backend.backend_app.brain_module.brain_service import BrainSvc

# Import your existing text extractor (adjust import if needed)
# from Backend.backend_app.text_extraction.consolidated_extractor import extract_with_logging as extract_text_from_file

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
                print(f"✅ Successfully loaded pre-extracted text from: {extracted_file.name}")
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
                        print(f"✅ Successfully loaded pre-extracted text from: {alt_file.name}")
                        return content
            
            print(f"⚠ WARNING: No pre-extracted text file found for {filename}")
            return f"# WARNING: Could not find pre-extracted text file for {filename}"
            
    except Exception as e:
        print(f"❌ Error reading pre-extracted text file: {e}")
        return f"# ERROR: Failed to read pre-extracted text: {e}"


# -------------------------------
# 1. LOGIN SYSTEM
# -------------------------------
def authenticate():
    print("=== Resume Processing Test Tool ===")
    user = input("Username: ").strip()
    pwd = getpass.getpass("Password: ").strip()

    if user == "admin" and pwd == "admin123":
        print("Login successful.\n")
        return True
    else:
        print("Invalid credentials. Exiting...")
        return False


# -------------------------------
# 2. PROCESS RESUMES
# -------------------------------
def process_resumes():
    resume_dir = Path("Resumes")
    if not resume_dir.exists():
        print("❌ ERROR: 'Resumes' directory not found in project root.")
        return

    resumes = list(resume_dir.glob("*"))
    if not resumes:
        print("❌ No files found in the 'Resumes' directory.")
        return

    print(f"Found {len(resumes)} resumes to process.\n")

    results_json = []
    results_txt_lines = []

    for file_path in resumes:
        print("------------------------------------------------------")
        print(f"Processing file: {file_path.name}")

        # Extract text
        try:
            extracted_text = extract_text_from_file(str(file_path))
        except Exception as e:
            print(f"❌ Extraction error for {file_path.name}: {e}")
            continue

        if not extracted_text.strip():
            print(f"⚠ WARNING: No text extracted from {file_path.name}")
            continue

        # Debugging snippet
        snippet = extracted_text[:200].replace("\n", " ")
        print(f"Text snippet (200 chars): {snippet}")
        print("Sending text to Brain Module using RESUME prompt...\n")

        # Create QID automatically
        qid = f"resume-test-{uuid.uuid4()}"

        # Prepare Brain module request
        qitem = {
            "qid": qid,
            "text": extracted_text,
            "intake_type": "resume",   # forces resume prompt
            "meta": {
                "filename": file_path.name,
                "source": "test_resumes_script"
            }
        }

        # Call Brain Module
        try:
            result = BrainSvc.process(qitem)
        except Exception as e:
            print(f"❌ Brain module error for {file_path.name}: {e}")
            continue

        # Display result summary
        print(f"Brain Module success: {result.get('success')}")
        print(f"Provider used: {result.get('provider')}")
        print(f"Model: {result.get('model')}\n")

        # Save to memory
        results_json.append({
            "filename": file_path.name,
            "qid": qid,
            "full_text": extracted_text,
            "brain_output": result
        })

        results_txt_lines.append(
            f"\n==== {file_path.name} ====\n"
            f"QID: {qid}\n"
            f"Provider: {result.get('provider')}\n"
            f"Model: {result.get('model')}\n"
            f"Success: {result.get('success')}\n"
            f"Response:\n{result.get('response')}\n"
        )

    # -------------------------------
    # 3. SAVE OUTPUT FILES
    # -------------------------------
    print("\nSaving results...")

    with open("results.json", "w", encoding="utf-8") as jf:
        json.dump(results_json, jf, ensure_ascii=False, indent=2)

    with open("results.txt", "w", encoding="utf-8") as tf:
        tf.write("\n".join(results_txt_lines))

    print("✔ results.json and results.txt saved successfully.")
    print("Done. Exiting.")


# -------------------------------
# MAIN EXECUTION
# -------------------------------
if __name__ == "__main__":
    if authenticate():
        process_resumes()