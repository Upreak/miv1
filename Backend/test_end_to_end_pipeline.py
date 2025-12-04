#!/usr/bin/env python3
"""
End-to-End Resume Processing Pipeline Test

This script tests the complete pipeline:
1. Document ingestion
2. Text extraction and saving to text_extract folder
3. LLM processing with prompts
4. Response storage

Usage:
    python test_end_to_end_pipeline.py
"""

import os
import sys
import logging
import traceback
import json
from pathlib import Path
from datetime import datetime

# Setup logging with UTF-8 encoding to handle Unicode characters
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('end_to_end_test.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Custom formatter to handle Unicode encoding issues on Windows
class UnicodeSafeFormatter(logging.Formatter):
    def format(self, record):
        try:
            return super().format(record)
        except UnicodeEncodeError:
            # Replace problematic Unicode characters
            record.msg = str(record.msg).replace('✓', 'SUCCESS').replace('✗', 'ERROR').replace('→', '->')
            return super().format(record)

# Apply custom formatter
for handler in logging.getLogger().handlers:
    handler.setFormatter(UnicodeSafeFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logger = logging.getLogger(__name__)

# Add Backend to path
sys.path.insert(0, str(Path(__file__).parent))

def setup_directories():
    """Create necessary directories"""
    directories = [
        "text_extract",
        "llm_responses",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        logger.info(f"Created directory: {directory}")

def find_resume_files():
    """Find resume files in the Resumes directory"""
    resume_dir = Path("C:/Users/maheshpattar/Desktop/test2/Resumes")
    
    if not resume_dir.exists():
        logger.error(f"Resumes directory not found: {resume_dir}")
        return []
    
    # Supported file types
    supported_extensions = {'.pdf', '.doc', '.docx', '.txt'}
    
    resume_files = []
    for file_path in resume_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            resume_files.append(file_path)
    
    logger.info(f"Found {len(resume_files)} resume files:")
    for file_path in resume_files:
        logger.info(f"  - {file_path}")
    
    return resume_files

def test_text_extraction():
    """Test text extraction from resume files"""
    logger.info("=" * 60)
    logger.info("STEP 1: TESTING TEXT EXTRACTION")
    logger.info("=" * 60)
    
    try:
        from backend_app.text_extraction.consolidated_extractor import extract_with_logging
        logger.info("✓ Successfully imported consolidated_extractor")
    except ImportError as e:
        logger.error(f"✗ Failed to import consolidated_extractor: {e}")
        return False
    
    resume_files = find_resume_files()
    if not resume_files:
        logger.error("✗ No resume files found")
        return False
    
    extraction_results = []
    
    for file_path in resume_files:
        logger.info(f"\nProcessing: {file_path.name}")
        
        try:
            # Extract text using consolidated extractor
            result = extract_with_logging(
                file_path=file_path,
                metadata={"source": "end_to_end_test", "filename": file_path.name},
                quality_threshold=70.0
            )
            
            if result["success"]:
                logger.info(f"✓ Extraction successful using {result['module']}")
                logger.info(f"  Quality score: {result['score']:.1f}")
                logger.info(f"  Text length: {len(result['text'])}")
                
                # Save extracted text
                text_extract_path = Path("text_extract") / f"{file_path.stem}_extracted.txt"
                with open(text_extract_path, 'w', encoding='utf-8') as f:
                    f.write(result['text'])
                
                logger.info(f"✓ Saved extracted text to: {text_extract_path}")
                
                extraction_results.append({
                    'file_path': file_path,
                    'text_path': text_extract_path,
                    'success': True,
                    'module': result['module'],
                    'score': result['score'],
                    'length': len(result['text'])
                })
                
            else:
                logger.error(f"✗ Extraction failed for {file_path.name}")
                logger.error(f"  Error: {result.get('error_message', 'Unknown error')}")
                
                extraction_results.append({
                    'file_path': file_path,
                    'text_path': None,
                    'success': False,
                    'error': result.get('error_message', 'Unknown error')
                })
                
        except Exception as e:
            logger.error(f"✗ Exception during extraction of {file_path.name}: {e}")
            logger.error(traceback.format_exc())
            
            extraction_results.append({
                'file_path': file_path,
                'text_path': None,
                'success': False,
                'error': str(e)
            })
    
    # Summary
    successful = sum(1 for r in extraction_results if r['success'])
    logger.info(f"\nExtraction Summary: {successful}/{len(extraction_results)} successful")
    
    return successful > 0, extraction_results

def test_llm_processing(extraction_results):
    """Test LLM processing with prompts"""
    logger.info("=" * 60)
    logger.info("STEP 2: TESTING LLM PROCESSING")
    logger.info("=" * 60)
    
    try:
        from backend_app.services.brain_service import parse_resume_from_path
        logger.info("✓ Successfully imported brain_service")
    except ImportError as e:
        logger.error(f"✗ Failed to import brain_service: {e}")
        return False
    
    llm_results = []
    
    for result in extraction_results:
        if not result['success']:
            continue
            
        logger.info(f"\nProcessing: {result['file_path'].name}")
        
        try:
            # Parse resume using brain service
            brain_output = parse_resume_from_path(
                result['text_path'],  # Pass the extracted text file
                strategy="fast"
            )
            
            if brain_output.get('success', False):
                logger.info(f"✓ LLM processing successful")
                logger.info(f"  Provider: {brain_output.get('provider', 'unknown')}")
                logger.info(f"  Model: {brain_output.get('model', 'unknown')}")
                logger.info(f"  Response time: {brain_output.get('response_time', 0):.2f}s")
                
                # Save LLM response
                response_filename = f"{result['file_path'].stem}_response.txt"
                response_path = Path("llm_responses") / response_filename
                
                with open(response_path, 'w', encoding='utf-8') as f:
                    f.write(brain_output.get('response', ''))
                
                # Save metadata
                metadata_path = Path("llm_responses") / f"{result['file_path'].stem}_metadata.json"
                import json
                metadata = {
                    'timestamp': datetime.now().isoformat(),
                    'provider': brain_output.get('provider'),
                    'model': brain_output.get('model'),
                    'response_time': brain_output.get('response_time'),
                    'success': True,
                    'input_file': str(result['file_path']),
                    'extracted_text_file': str(result['text_path'])
                }
                
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2)
                
                logger.info(f"✓ Saved LLM response to: {response_path}")
                logger.info(f"✓ Saved metadata to: {metadata_path}")
                
                llm_results.append({
                    'file_path': result['file_path'],
                    'response_path': response_path,
                    'metadata_path': metadata_path,
                    'success': True,
                    'provider': brain_output.get('provider'),
                    'model': brain_output.get('model'),
                    'response_time': brain_output.get('response_time')
                })
                
            else:
                logger.error(f"✗ LLM processing failed for {result['file_path'].name}")
                logger.error(f"  Error: {brain_output.get('error_message', 'Unknown error')}")
                
                llm_results.append({
                    'file_path': result['file_path'],
                    'response_path': None,
                    'metadata_path': None,
                    'success': False,
                    'error': brain_output.get('error_message', 'Unknown error')
                })
                
        except Exception as e:
            logger.error(f"✗ Exception during LLM processing of {result['file_path'].name}: {e}")
            logger.error(traceback.format_exc())
            
            llm_results.append({
                'file_path': result['file_path'],
                'response_path': None,
                'metadata_path': None,
                'success': False,
                'error': str(e)
            })
    
    # Summary
    successful = sum(1 for r in llm_results if r['success'])
    logger.info(f"\nLLM Processing Summary: {successful}/{len(llm_results)} successful")
    
    return successful > 0, llm_results

def test_candidate_creation(extraction_results):
    """Test candidate profile creation"""
    logger.info("=" * 60)
    logger.info("STEP 3: TESTING CANDIDATE CREATION")
    logger.info("=" * 60)
    
    try:
        from backend_app.services.candidate_creation_service import create_candidate_profile
        logger.info("✓ Successfully imported candidate_creation_service")
    except ImportError as e:
        logger.error(f"✗ Failed to import candidate_creation_service: {e}")
        return False
    
    candidate_results = []
    
    for result in extraction_results:
        if not result['success']:
            continue
            
        logger.info(f"\nCreating candidate profile: {result['file_path'].name}")
        
        try:
            # Read extracted text
            with open(result['text_path'], 'r', encoding='utf-8') as f:
                extracted_text = f.read()
            
            # Create candidate profile
            candidate_id = create_candidate_profile(
                raw_text=extracted_text,
                source="end_to_end_test",
                filename=result['file_path'].name,
                file_type=result['file_path'].suffix
            )
            
            logger.info(f"✓ Candidate profile created: ID = {candidate_id}")
            
            candidate_results.append({
                'file_path': result['file_path'],
                'candidate_id': candidate_id,
                'success': True
            })
            
        except Exception as e:
            logger.error(f"✗ Exception during candidate creation for {result['file_path'].name}: {e}")
            logger.error(traceback.format_exc())
            
            candidate_results.append({
                'file_path': result['file_path'],
                'candidate_id': None,
                'success': False,
                'error': str(e)
            })
    
    # Summary
    successful = sum(1 for r in candidate_results if r['success'])
    logger.info(f"\nCandidate Creation Summary: {successful}/{len(candidate_results)} successful")
    
    return successful > 0, candidate_results

def generate_final_report(extraction_results, llm_results, candidate_results):
    """Generate final test report"""
    logger.info("=" * 60)
    logger.info("FINAL TEST REPORT")
    logger.info("=" * 60)
    
    total_files = len(extraction_results)
    extraction_success = sum(1 for r in extraction_results if r['success'])
    llm_success = sum(1 for r in llm_results if r['success'])
    candidate_success = sum(1 for r in candidate_results if r['success'])
    
    logger.info(f"Total files processed: {total_files}")
    logger.info(f"Text extraction: {extraction_success}/{total_files} successful")
    logger.info(f"LLM processing: {llm_success}/{len(llm_results)} successful")
    logger.info(f"Candidate creation: {candidate_success}/{len(candidate_results)} successful")
    
    # Overall success rate
    overall_success = extraction_success > 0 and llm_success > 0 and candidate_success > 0
    logger.info(f"Overall pipeline success: {'✓ PASS' if overall_success else '✗ FAIL'}")
    
    # Save detailed report
    report_path = Path("logs/end_to_end_test_report.json")
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_files': total_files,
            'extraction_success': extraction_success,
            'llm_success': llm_success,
            'candidate_success': candidate_success,
            'overall_success': overall_success
        },
        'extraction_results': extraction_results,
        'llm_results': llm_results,
        'candidate_results': candidate_results
    }
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, default=str)
    
    logger.info(f"Detailed report saved to: {report_path}")
    
    return overall_success

def main():
    """Main test execution"""
    logger.info("Starting End-to-End Resume Processing Pipeline Test")
    logger.info("=" * 60)
    
    try:
        # Setup
        setup_directories()
        
        # Step 1: Test text extraction
        extraction_success, extraction_results = test_text_extraction()
        if not extraction_success:
            logger.error("✗ Text extraction failed - stopping test")
            return False
        
        # Step 2: Test LLM processing
        llm_success, llm_results = test_llm_processing(extraction_results)
        if not llm_success:
            logger.error("✗ LLM processing failed - continuing to see other results")
        
        # Step 3: Test candidate creation
        candidate_success, candidate_results = test_candidate_creation(extraction_results)
        if not candidate_success:
            logger.error("✗ Candidate creation failed - continuing to see other results")
        
        # Generate final report
        overall_success = generate_final_report(extraction_results, llm_results, candidate_results)
        
        if overall_success:
            logger.info("✓ End-to-End Test COMPLETED SUCCESSFULLY")
            logger.info("All pipeline components are working correctly!")
        else:
            logger.warning("⚠ End-to-End Test completed with some issues")
            logger.info("Check the logs for details on failed components")
        
        return overall_success
        
    except Exception as e:
        logger.error(f"✗ Test failed with exception: {e}")
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)