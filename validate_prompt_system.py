#!/usr/bin/env python3
"""
Comprehensive validation script for the prompt system with detailed logging
"""

import sys
import os
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('validate_prompt_system.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def test_prompt_systems():
    """Test all prompt rendering systems"""
    logger.info("=== COMPREHENSIVE PROMPT SYSTEM VALIDATION ===")
    
    # Test data
    sample_resume = """
    John Doe
    Email: john.doe@email.com
    Phone: +1-555-0123
    
    Experience:
    Software Engineer at Tech Corp (2020-2023)
    - Developed web applications using Python and React
    - Led a team of 5 developers
    
    Education:
    Bachelor of Science in Computer Science
    University of Technology (2016-2020)
    """
    
    sample_jd = """
    Senior Software Engineer
    
    We are looking for a Senior Software Engineer with experience in:
    - Python and React
    - Team leadership
    - Web development
    
    Requirements:
    - 5+ years of experience
    - Bachelor's degree in Computer Science
    - Strong communication skills
    """
    
    logger.info("\n--- Testing Python Class Systems ---")
    
    # Test ResumePromptRenderer
    try:
        sys.path.insert(0, str(Path(__file__).parent / "Backend" / "backend_app"))
        from brain_module.prompts.resume_prompt import ResumePromptRenderer
        
        logger.info("Testing ResumePromptRenderer...")
        resume_renderer = ResumePromptRenderer()
        resume_prompt = resume_renderer.render_prompt(sample_resume, "text", "test_resume.txt")
        
        logger.info(f"Resume prompt length: {len(resume_prompt)}")
        logger.info(f"Contains expected content: {'John Doe' in resume_prompt}")
        logger.info(f"Template variables rendered: {'{{' not in resume_prompt}")
        
    except Exception as e:
        logger.error(f"Error testing ResumePromptRenderer: {e}")
    
    # Test JDPromptRenderer
    try:
        from brain_module.prompts.jd_prompt import JDPromptRenderer
        
        logger.info("Testing JDPromptRenderer...")
        jd_renderer = JDPromptRenderer()
        jd_prompt = jd_renderer.render_prompt(sample_jd, "text", "test_jd.txt")
        
        logger.info(f"JD prompt length: {len(jd_prompt)}")
        logger.info(f"Contains expected content: {'Senior Software Engineer' in jd_prompt}")
        logger.info(f"Template variables rendered: {'{{' not in jd_prompt}")
        
    except Exception as e:
        logger.error(f"Error testing JDPromptRenderer: {e}")
    
    logger.info("\n--- Testing YAML Template System ---")
    
    # Test YAML PromptRenderer
    try:
        from brain_module.prompt_renderer import PromptRenderer
        
        logger.info("Testing YAML PromptRenderer...")
        yaml_renderer = PromptRenderer()
        
        # Test resume parsing with YAML
        resume_context = {
            'resume_text': sample_resume,
            'source_type': 'text',
            'filename': 'test_resume.txt'
        }
        
        yaml_resume_prompt = yaml_renderer.render('resume_parse', resume_context)
        logger.info(f"YAML resume prompt length: {len(yaml_resume_prompt)}")
        logger.info(f"Contains expected content: {'John Doe' in yaml_resume_prompt}")
        logger.info(f"Template variables rendered: {'{{' not in yaml_resume_prompt}")
        
        # Test JD parsing with YAML
        jd_context = {
            'jd_text': sample_jd,
            'source_type': 'text',
            'filename': 'test_jd.txt'
        }
        
        yaml_jd_prompt = yaml_renderer.render('jd_parse', jd_context)
        logger.info(f"YAML JD prompt length: {len(yaml_jd_prompt)}")
        logger.info(f"Contains expected content: {'Senior Software Engineer' in yaml_jd_prompt}")
        logger.info(f"Template variables rendered: {'{{' not in yaml_jd_prompt}")
        
    except Exception as e:
        logger.error(f"Error testing YAML PromptRenderer: {e}")
    
    logger.info("\n--- Testing BrainCore Integration ---")
    
    # Test BrainCore prompt building
    try:
        from brain_module.brain_core import BrainCore
        
        logger.info("Testing BrainCore prompt building...")
        brain_core = BrainCore()
        
        # Test resume prompt building
        resume_prompt = brain_core._build_prompt(sample_resume, "resume_parsing")
        logger.info(f"BrainCore resume prompt length: {len(resume_prompt)}")
        logger.info(f"Contains expected content: {'John Doe' in resume_prompt}")
        
        # Test JD prompt building
        jd_prompt = brain_core._build_prompt(sample_jd, "jd_parsing")
        logger.info(f"BrainCore JD prompt length: {len(jd_prompt)}")
        logger.info(f"Contains expected content: {'Senior Software Engineer' in jd_prompt}")
        
    except Exception as e:
        logger.error(f"Error testing BrainCore: {e}")

def check_mock_data_usage():
    """Check for mock data usage in the system"""
    logger.info("\n=== CHECKING FOR MOCK DATA USAGE ===")
    
    # Check the mock function
    try:
        sys.path.insert(0, str(Path(__file__).parent / "Backend" / "backend_app"))
        from brain_module.brain_core import parse_resume
        
        logger.info("Testing parse_resume function...")
        mock_result = parse_resume("test resume text")
        logger.info(f"Mock result: {mock_result}")
        
        if mock_result == {"status": "parsed"}:
            logger.warning("WARNING: Mock function returns hardcoded response!")
            logger.warning("This indicates the system may be using mock data instead of real LLM calls")
        
    except Exception as e:
        logger.error(f"Error testing mock function: {e}")

def analyze_test_files():
    """Analyze test files for hardcoded prompts"""
    logger.info("\n=== ANALYZING TEST FILES ===")
    
    test_files = ["test_all_apis.py", "test_all_apis1.py", "test_refactored_providers.py"]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            try:
                with open(test_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Check for hardcoded prompts
                if 'RESUME_PROMPT = """' in content:
                    logger.info(f"Found hardcoded resume prompt in {test_file}")
                    
                    # Extract prompt length
                    start_idx = content.find('RESUME_PROMPT = """') + len('RESUME_PROMPT = """')
                    end_idx = content.find('"""', start_idx)
                    hardcoded_prompt = content[start_idx:end_idx]
                    
                    logger.info(f"Hardcoded prompt length: {len(hardcoded_prompt)}")
                    logger.info(f"Contains personal data: {'@' in hardcoded_prompt}")
                    logger.info(f"Contains phone numbers: {'-' in hardcoded_prompt}")
                    
                    if len(hardcoded_prompt) > 2000:
                        logger.warning(f"WARNING: Very long hardcoded prompt in {test_file}!")
                
            except Exception as e:
                logger.error(f"Error analyzing {test_file}: {e}")
        else:
            logger.warning(f"Test file {test_file} not found")

def main():
    """Main validation function"""
    logger.info("Starting comprehensive prompt system validation...")
    
    test_prompt_systems()
    check_mock_data_usage()
    analyze_test_files()
    
    logger.info("\n=== VALIDATION SUMMARY ===")
    logger.info("Check validate_prompt_system.log for detailed logs")
    logger.info("Key validation points:")
    logger.info("1. Which prompt rendering systems are being used")
    logger.info("2. Whether template variables are properly rendered")
    logger.info("3. If mock data is being used instead of real LLM calls")
    logger.info("4. The consistency between different prompt systems")
    logger.info("5. Issues with hardcoded prompts in test files")

if __name__ == "__main__":
    main()