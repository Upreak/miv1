#!/usr/bin/env python3
"""
Comprehensive Resume Processing Workflow Test Script

This script validates the entire resume processing pipeline from intake to storage.
It processes all resumes from the 'Resumes' folder, extracts text, parses with the brain module,
and stores results with proper error handling and logging.

Features:
- Complete folder map generation
- Processing of all resumes from Resumes folder
- Text extraction from each resume
- Brain module parsing
- Results storage in designated folder
- Comprehensive error handling and logging
- Summary report generation
"""

import os
import sys
import json
import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import time

# Configure logging with UTF-8 encoding to handle emojis
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_workflow.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ResumeProcessingTest:
    """Comprehensive test suite for resume processing workflow"""
    
    def __init__(self):
        self.test_start_time = datetime.now()
        self.results = {
            'test_info': {
                'start_time': self.test_start_time.isoformat(),
                'test_type': 'Resume Processing Workflow Test',
                'version': '1.0'
            },
            'folder_map': {},
            'resume_files': [],
            'processing_results': [],
            'summary': {
                'total_resumes': 0,
                'successful': 0,
                'failed': 0,
                'success_rate': 0.0,
                'total_processing_time': 0.0
            }
        }
        
        # Define paths
        self.base_path = Path.cwd()
        self.resumes_path = self.base_path / "Resumes"
        self.output_path = self.base_path / "test_results"
        self.output_path.mkdir(exist_ok=True)
        
        logger.info(f"Test initialized at {self.test_start_time}")
        logger.info(f"Base path: {self.base_path}")
        logger.info(f"Resumes path: {self.resumes_path}")
        logger.info(f"Output path: {self.output_path}")
    
    def generate_folder_map(self) -> Dict[str, Any]:
        """Generate complete folder map and file structure"""
        logger.info("Generating complete folder map...")
        
        def scan_directory(path: Path, max_depth: int = 3, current_depth: int = 0) -> Dict[str, Any]:
            """Recursively scan directory structure"""
            if current_depth >= max_depth:
                return {"type": "directory", "files": [], "subdirectories": []}
            
            structure = {
                "type": "directory",
                "path": str(path),
                "files": [],
                "subdirectories": {}
            }
            
            try:
                if path.exists() and path.is_dir():
                    for item in sorted(path.iterdir()):
                        if item.name.startswith('.') or item.name == '__pycache__':
                            continue
                        
                        if item.is_file():
                            structure["files"].append({
                                "name": item.name,
                                "size": item.stat().st_size if item.exists() else 0,
                                "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat() if item.exists() else None
                            })
                        elif item.is_dir():
                            structure["subdirectories"][item.name] = scan_directory(item, max_depth, current_depth + 1)
            except Exception as e:
                logger.warning(f"Error scanning directory {path}: {e}")
            
            return structure
        
        folder_map = scan_directory(self.base_path, max_depth=3)
        self.results['folder_map'] = folder_map
        
        # Save folder map to file
        folder_map_file = self.output_path / "folder_map.json"
        with open(folder_map_file, 'w', encoding='utf-8') as f:
            json.dump(folder_map, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Folder map generated and saved to {folder_map_file}")
        return folder_map
    
    def discover_resume_files(self) -> List[Path]:
        """Discover all resume files in the Resumes folder"""
        logger.info(f"Discovering resume files in {self.resumes_path}...")
        
        if not self.resumes_path.exists():
            logger.warning(f"Resumes folder does not exist: {self.resumes_path}")
            return []
        
        # Supported file extensions
        supported_extensions = {'.pdf', '.docx', '.doc', '.txt'}
        
        resume_files = []
        for file_path in self.resumes_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                resume_files.append(file_path)
        
        resume_files.sort()
        self.results['resume_files'] = [str(f) for f in resume_files]
        
        logger.info(f"Found {len(resume_files)} resume files:")
        for file_path in resume_files:
            logger.info(f"  - {file_path.name}")
        
        return resume_files
    
    def extract_text_from_resume(self, resume_path: Path) -> Tuple[bool, str, Optional[str]]:
        """Extract text content from a resume file"""
        logger.info(f"Extracting text from {resume_path.name}...")
        
        try:
            # Try to import text extraction module
            backend_path = self.base_path / "Backend" / "backend_app"
            if backend_path.exists():
                sys.path.insert(0, str(backend_path))
                from text_extraction.consolidated_extractor import extract_text_from_file
                
                # Extract text
                extracted_text = extract_text_from_file(str(resume_path))
                
                if extracted_text and len(extracted_text.strip()) > 0:
                    logger.info(f"Successfully extracted {len(extracted_text)} characters from {resume_path.name}")
                    return True, extracted_text, None
                else:
                    error_msg = f"No text extracted from {resume_path.name}"
                    logger.warning(error_msg)
                    return False, "", error_msg
            else:
                error_msg = f"Backend path does not exist: {backend_path}"
                logger.error(error_msg)
                return False, "", error_msg
                
        except ImportError as e:
            error_msg = f"Failed to import text extraction module: {e}"
            logger.error(error_msg)
            return False, "", error_msg
        except Exception as e:
            error_msg = f"Error extracting text from {resume_path.name}: {str(e)}"
            logger.error(error_msg)
            return False, "", error_msg
    
    def parse_with_brain_module(self, extracted_text: str, resume_name: str) -> Tuple[bool, Dict[str, Any], Optional[str]]:
        """Use brain module to parse extracted text"""
        logger.info(f"Parsing extracted text with brain module for {resume_name}...")
        
        try:
            # Try to import brain module
            backend_path = self.base_path / "Backend" / "backend_app"
            if backend_path.exists():
                sys.path.insert(0, str(backend_path))
                from brain_module.brain_core import BrainCore
                
                # Initialize brain core
                brain_core = BrainCore()
                
                # Parse the text
                result = brain_core.process_resume(extracted_text)
                
                if result and 'success' in result and result['success']:
                    logger.info(f"Successfully parsed {resume_name} with brain module")
                    return True, result, None
                else:
                    error_msg = f"Brain module parsing failed for {resume_name}: {result.get('error', 'Unknown error')}"
                    logger.warning(error_msg)
                    return False, {}, error_msg
            else:
                error_msg = f"Backend path does not exist: {backend_path}"
                logger.error(error_msg)
                return False, {}, error_msg
                
        except ImportError as e:
            error_msg = f"Failed to import brain module: {e}"
            logger.error(error_msg)
            return False, {}, error_msg
        except Exception as e:
            error_msg = f"Error parsing with brain module for {resume_name}: {str(e)}"
            logger.error(error_msg)
            return False, {}, error_msg
    
    def store_processed_result(self, resume_name: str, extracted_text: str, parsed_result: Dict[str, Any]) -> bool:
        """Store processed results in designated folder"""
        logger.info(f"Storing processed result for {resume_name}...")
        
        try:
            # Create resume-specific output directory
            resume_output_dir = self.output_path / "processed_resumes" / resume_name.replace(' ', '_').replace('.', '_')
            resume_output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save extracted text
            text_file = resume_output_dir / "extracted_text.txt"
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(extracted_text)
            
            # Save parsed result
            result_file = resume_output_dir / "parsed_result.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(parsed_result, f, indent=2, ensure_ascii=False)
            
            # Create summary file
            summary_file = resume_output_dir / "processing_summary.json"
            summary = {
                'resume_name': resume_name,
                'extraction_status': 'success',
                'parsing_status': 'success' if parsed_result.get('success', False) else 'failed',
                'extraction_time': datetime.now().isoformat(),
                'text_length': len(extracted_text),
                'parsed_fields': list(parsed_result.keys()) if parsed_result else []
            }
            
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2)
            
            logger.info(f"Successfully stored results for {resume_name} in {resume_output_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing results for {resume_name}: {str(e)}")
            return False
    
    def process_single_resume(self, resume_path: Path) -> Dict[str, Any]:
        """Process a single resume through the entire workflow"""
        resume_name = resume_path.name
        logger.info(f"Processing resume: {resume_name}")
        
        processing_result = {
            'resume_name': resume_name,
            'resume_path': str(resume_path),
            'extraction': {
                'success': False,
                'text_length': 0,
                'error': None,
                'processing_time': 0.0
            },
            'parsing': {
                'success': False,
                'error': None,
                'processing_time': 0.0
            },
            'storage': {
                'success': False,
                'error': None
            },
            'overall_success': False,
            'total_processing_time': 0.0
        }
        
        start_time = time.time()
        
        try:
            # Step 1: Extract text
            extract_start = time.time()
            extract_success, extracted_text, extract_error = self.extract_text_from_resume(resume_path)
            extract_time = time.time() - extract_start
            
            processing_result['extraction']['success'] = extract_success
            processing_result['extraction']['error'] = extract_error
            processing_result['extraction']['processing_time'] = extract_time
            
            if not extract_success:
                logger.error(f"Text extraction failed for {resume_name}: {extract_error}")
                processing_result['overall_success'] = False
                return processing_result
            
            processing_result['extraction']['text_length'] = len(extracted_text)
            
            # Step 2: Parse with brain module
            parse_start = time.time()
            parse_success, parsed_result, parse_error = self.parse_with_brain_module(extracted_text, resume_name)
            parse_time = time.time() - parse_start
            
            processing_result['parsing']['success'] = parse_success
            processing_result['parsing']['error'] = parse_error
            processing_result['parsing']['processing_time'] = parse_time
            
            if not parse_success:
                logger.error(f"Brain module parsing failed for {resume_name}: {parse_error}")
                processing_result['overall_success'] = False
                return processing_result
            
            # Step 3: Store results
            storage_success = self.store_processed_result(resume_name, extracted_text, parsed_result)
            processing_result['storage']['success'] = storage_success
            processing_result['storage']['error'] = None if storage_success else "Storage failed"
            
            if not storage_success:
                logger.error(f"Result storage failed for {resume_name}")
                processing_result['overall_success'] = False
                return processing_result
            
            # Success!
            processing_result['overall_success'] = True
            processing_result['total_processing_time'] = time.time() - start_time
            
            logger.info(f"Successfully processed {resume_name} in {processing_result['total_processing_time']:.2f} seconds")
            
        except Exception as e:
            processing_result['overall_success'] = False
            processing_result['error'] = str(e)
            logger.error(f"Unexpected error processing {resume_name}: {str(e)}")
            logger.error(traceback.format_exc())
        
        return processing_result
    
    def run_workflow_test(self):
        """Run the complete workflow test"""
        logger.info("Starting comprehensive resume processing workflow test...")
        
        # Step 1: Generate folder map
        self.generate_folder_map()
        
        # Step 2: Discover resume files
        resume_files = self.discover_resume_files()
        
        if not resume_files:
            logger.warning("No resume files found. Test cannot proceed.")
            return
        
        # Step 3: Process each resume
        logger.info(f"Processing {len(resume_files)} resumes...")
        
        for i, resume_path in enumerate(resume_files, 1):
            logger.info(f"Processing resume {i}/{len(resume_files)}: {resume_path.name}")
            
            try:
                result = self.process_single_resume(resume_path)
                self.results['processing_results'].append(result)
                
                if result['overall_success']:
                    logger.info(f"SUCCESS {resume_path.name} - SUCCESS")
                else:
                    logger.info(f"FAILED {resume_path.name} - FAILED")
                    
            except Exception as e:
                logger.error(f"Critical error processing {resume_path.name}: {str(e)}")
                logger.error(traceback.format_exc())
        
        # Step 4: Generate summary
        self.generate_summary()
        
        # Step 5: Save all results
        self.save_results()
        
        logger.info("Resume processing workflow test completed!")
    
    def generate_summary(self):
        """Generate test execution summary"""
        total_resumes = len(self.results['processing_results'])
        successful = sum(1 for r in self.results['processing_results'] if r['overall_success'])
        failed = total_resumes - successful
        success_rate = (successful / total_resumes * 100) if total_resumes > 0 else 0
        
        total_time = sum(r['total_processing_time'] for r in self.results['processing_results'])
        
        self.results['summary'] = {
            'total_resumes': total_resumes,
            'successful': successful,
            'failed': failed,
            'success_rate': round(success_rate, 2),
            'total_processing_time': round(total_time, 2),
            'average_processing_time': round(total_time / total_resumes, 2) if total_resumes > 0 else 0
        }
        
        logger.info("=" * 60)
        logger.info("TEST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Resumes: {total_resumes}")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Success Rate: {success_rate:.2f}%")
        logger.info(f"Total Processing Time: {total_time:.2f} seconds")
        logger.info(f"Average Processing Time: {total_time / total_resumes:.2f} seconds" if total_resumes > 0 else "Average Processing Time: N/A")
        logger.info("=" * 60)
    
    def save_results(self):
        """Save all test results to files"""
        # Save complete results
        results_file = self.output_path / "test_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        # Save summary report
        summary_file = self.output_path / "test_summary_report.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("Resume Processing Workflow Test Summary Report\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Test Type: {self.results['test_info']['test_type']}\n")
            f.write(f"Start Time: {self.results['test_info']['start_time']}\n")
            f.write(f"Version: {self.results['test_info']['version']}\n\n")
            
            summary = self.results['summary']
            f.write("EXECUTIVE SUMMARY\n")
            f.write("-" * 30 + "\n")
            f.write(f"Total Resumes Processed: {summary['total_resumes']}\n")
            f.write(f"Successful: {summary['successful']}\n")
            f.write(f"Failed: {summary['failed']}\n")
            f.write(f"Success Rate: {summary['success_rate']}%\n")
            f.write(f"Total Processing Time: {summary['total_processing_time']} seconds\n")
            f.write(f"Average Processing Time: {summary['average_processing_time']} seconds\n\n")
            
            f.write("DETAILED RESULTS\n")
            f.write("-" * 30 + "\n")
            for result in self.results['processing_results']:
                status = "SUCCESS" if result['overall_success'] else "FAILED"
                f.write(f"{result['resume_name']}: {status}\n")
                if not result['overall_success']:
                    if result['extraction']['error']:
                        f.write(f"  - Extraction Error: {result['extraction']['error']}\n")
                    if result['parsing']['error']:
                        f.write(f"  - Parsing Error: {result['parsing']['error']}\n")
                    if result['storage']['error']:
                        f.write(f"  - Storage Error: {result['storage']['error']}\n")
                else:
                    f.write(f"  - Processing Time: {result['total_processing_time']:.2f} seconds\n")
                    f.write(f"  - Text Length: {result['extraction']['text_length']} characters\n")
        
        logger.info(f"Test results saved to:")
        logger.info(f"  - {results_file}")
        logger.info(f"  - {summary_file}")
    
    def print_final_report(self):
        """Print final test report"""
        print("\n" + "=" * 80)
        print("RESUME PROCESSING WORKFLOW TEST - FINAL REPORT")
        print("=" * 80)
        
        summary = self.results['summary']
        print(f"\nTest Statistics:")
        print(f"   Total Resumes: {summary['total_resumes']}")
        print(f"   Successful: {summary['successful']}")
        print(f"   Failed: {summary['failed']}")
        print(f"   Success Rate: {summary['success_rate']}%")
        
        print(f"\nPerformance Metrics:")
        print(f"   Total Processing Time: {summary['total_processing_time']} seconds")
        print(f"   Average Processing Time: {summary['average_processing_time']} seconds")
        
        print(f"\nOutput Files:")
        print(f"   Test Results: {self.output_path / 'test_results.json'}")
        print(f"   Summary Report: {self.output_path / 'test_summary_report.txt'}")
        print(f"   Folder Map: {self.output_path / 'folder_map.json'}")
        
        print(f"\n📂 Processed Resumes:")
        for result in self.results['processing_results']:
            status = "SUCCESS" if result['overall_success'] else "FAILED"
            print(f"   {status} {result['resume_name']}")
        
        print("\n" + "=" * 80)


def main():
    """Main test execution"""
    print("Starting Comprehensive Resume Processing Workflow Test")
    print("=" * 80)
    
    try:
        # Initialize test
        test = ResumeProcessingTest()
        
        # Run the complete workflow test
        test.run_workflow_test()
        
        # Print final report
        test.print_final_report()
        
        # Exit with appropriate code
        successful = test.results['summary']['successful']
        total = test.results['summary']['total_resumes']
        
        if successful == total and total > 0:
            print("\nAll tests passed successfully!")
            sys.exit(0)
        elif successful > 0:
            print(f"\n{total - successful} out of {total} tests failed.")
            sys.exit(1)
        else:
            print(f"\nAll {total} tests failed.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nCritical error during test execution: {str(e)}")
        logger.error(f"Critical error: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()