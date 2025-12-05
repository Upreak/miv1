#!/usr/bin/env python3
"""
Batch Resume Extraction Script
Extracts text from all resume files in the Resumes folder and saves as txt files.
Uses the consolidated_extractor module for extraction.
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

# Import the consolidated extractor (frozen module)
from backend_app.text_extraction.consolidated_extractor import extract_with_logging

def setup_logging():
    """Setup basic logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/batch_extraction.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def extract_single_resume(file_path: Path, metadata: dict = None) -> dict:
    """
    Extract text from a single resume file using frozen extraction API
    
    Args:
        file_path: Path to the resume file (Path object)
        metadata: Optional metadata to include
    
    Returns:
        dict: Extraction result with text and metadata
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Processing file: {file_path}")
        
        # Prepare metadata for batch processing
        extraction_metadata = metadata or {}
        extraction_metadata.update({
            "source": "batch_extractor",
            "batch_id": "local_test",
            "extraction_timestamp": datetime.now().isoformat(),
            "source_file": str(file_path)
        })
        
        # Use frozen extraction API contract
        result = extract_with_logging(
            file_path=Path(file_path),
            metadata=extraction_metadata
        )
        
        logger.info(f"Successfully extracted text from {file_path.name}")
        
        return {
            "success": True,
            "file_path": file_path,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error extracting text from {file_path}: {str(e)}")
        return {
            "success": False,
            "file_path": file_path,
            "error": str(e)
        }

def save_extracted_text(text: str, output_path: Path) -> bool:
    """
    Save extracted text to a txt file
    
    Args:
        text: Extracted text content
        output_path: Path where to save the text file
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding="utf-8", errors="ignore")
        return True
    except Exception as e:
        logging.getLogger(__name__).error(f"Error saving text to {output_path}: {str(e)}")
        return False

def process_all_resumes():
    """
    Process all resume files in the Resumes folder using frozen extraction module
    """
    logger = setup_logging()
    
    # Define paths - fix path to Resumes directory
    resumes_dir = Path("../Resumes")
    output_dir = Path("extracted_resumes")
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all resume files
    if not resumes_dir.exists():
        logger.error(f"Resumes directory not found: {resumes_dir}")
        logger.info(f"Looking for resumes in: {resumes_dir.absolute()}")
        return
    
    # Supported file extensions
    supported_extensions = {'.pdf', '.docx', '.doc', '.txt', '.jpg', '.jpeg', '.png'}
    
    resume_files = []
    for file_path in resumes_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            resume_files.append(file_path)
    
    if not resume_files:
        logger.warning("No supported resume files found in the directory")
        return
    
    logger.info(f"Found {len(resume_files)} resume files to process:")
    for file_path in resume_files:
        logger.info(f"  - {file_path.name}")
    
    # Process each file using frozen extraction contract
    results = []
    successful_extractions = 0
    
    for file_path in resume_files:
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing: {file_path.name}")
        logger.info(f"{'='*60}")
        
        # Extract text using frozen API contract
        extraction_result = extract_single_resume(
            file_path=file_path,
            metadata={"batch_processing": True}
        )
        
        if extraction_result["success"]:
            successful_extractions += 1
            
            # Get result from frozen extraction module
            result = extraction_result["result"]
            
            # Update variable assignments according to frozen spec
            text = result.get("text", "")
            module_used = result.get("module", "unknown")
            score = result.get("score", 0)
            
            # Safety check for empty text
            if not text.strip():
                logger.warning(f"WARNING: No text extracted for {file_path.name}")
                continue
            
            # Generate output filename
            base_name = file_path.stem
            output_file = output_dir / f"{base_name}_extracted.txt"
            
            # Save extracted text using frozen API
            if save_extracted_text(text, output_file):
                logger.info(f"SUCCESS - Text saved to: {output_file}")
            else:
                logger.error(f"FAILED - Failed to save text to: {output_file}")
            
            # Validate output according to frozen spec
            logger.info(f"Text length: {len(text)} characters")
            logger.info(f"Module used: {module_used}")
            logger.info(f"Quality score: {score}")
            
        else:
            logger.error(f"FAILED - Failed to extract text: {extraction_result['error']}")
        
        results.append(extraction_result)
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("BATCH EXTRACTION SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"Total files processed: {len(resume_files)}")
    logger.info(f"Successful extractions: {successful_extractions}")
    logger.info(f"Failed extractions: {len(resume_files) - successful_extractions}")
    logger.info(f"Output directory: {output_dir}")
    
    if successful_extractions > 0:
        logger.info("\nSUCCESS - Successfully extracted resume texts saved to:")
        for result in results:
            if result["success"]:
                base_name = result["file_path"].stem
                output_file = output_dir / f"{base_name}_extracted.txt"
                logger.info(f"  - {output_file}")
    
    return results

if __name__ == "__main__":
    print("Starting Batch Resume Extraction...")
    print("Using frozen extraction module for optimal text extraction")
    print("-" * 60)
    
    # Run the extraction
    results = process_all_resumes()
    
    print("\n" + "=" * 60)
    print("Batch extraction completed!")
    print("Check 'extracted_resumes/' directory for output files")
    print("Check 'logs/batch_extraction.log' for detailed logs")