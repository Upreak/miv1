# prompts/resume_prompt.py
from typing import Dict, Any
from jinja2 import Template
import json

class ResumePromptRenderer:
    """Renders prompts for resume parsing"""
    
    def __init__(self):
        self.template = self._get_resume_template()
    
    def _get_resume_template(self) -> str:
        """Get the resume parsing template"""
        return """Resume parsing prompt
Task: Extract all information explicitly mentioned in the resume(structured/unstructured text) and structure it according to the Candidate Portfolio format. Do NOT infer, guess, or generate missing details. If a field is not present, leave it blank.

General Rules:
- Use only the content found in the resume.
- Maintain exact wording for skills, certificates, responsibilities, tools, etc.
- Dates must follow DD/MMM/YYYY format when possible.
- For multiple values, return them as arrays.
- Output strictly in JSON.

Fields to Extract (Output):
Identity Basics:
  Full Name:
  Email Address:
  Mobile Number:
  Professional Summary:
  LinkedIn URL:
  Portfolio URL
 
Education & Skills:
  Highest Education (PhD/Doctorate):
  Second Highest Education (Masters):
  Third Highest Education (Bachelor):
  DIPLOMA:
  ITI:
  PUC:
  SSLC:
  Certificates:
  Skills:
  Field of Study:
  Projects / Profile:
  GitHub / Behance / Kaggle URL:

Job Preferences:
  Total Experience (Years):
  Current Role:
  Expected Role:
  Job Type:
  Current Locations:
  Ready to Relocate:
  Notice Period:
  Work Authorization / Visa:

Salary Info:
  Current CTC (LPA):
  Expected CTC (LPA):

Broader Preferences & Personal Details:
  Preferred Industries:
  Gender:
  Marital Status:
  Date of Birth:
  Languages Known:

Work History (repeat for each job):
  Job Title/Role:
  Company Name:
  Start Date:
  End Date:
  Key Responsibilities:
  Tools Used:

Processing Guidelines:
- Include degree, institution, year, and score if available.
- List certificates individually.
- Extract every skill exactly as written.
- Create separate entries for each job in work history.
- Keep responsibilities true to the resume text.
- Leave blank fields empty.
- Do NOT assume or interpret any information not stated.

Output:
Return ONLY the final JSON.

Resume Text:
{{ resume_text }}
"""
    
    def render_prompt(self, text: str, source_type: str = "text", filename: str = None) -> str:
        """Render the resume parsing prompt"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info("=== RESUME PROMPT RENDERING SYSTEM DEBUG ===")
        logger.info(f"System: Python Class (ResumePromptRenderer)")
        logger.info(f"Template source: Hardcoded string in Python class")
        logger.info(f"Text length: {len(text)}")
        logger.info(f"Source type: {source_type}")
        logger.info(f"Filename: {filename or 'unknown'}")
        
        logger.debug(f"DEBUG: Resume text preview: {text[:200]}...")
        
        context = {
            'resume_text': text,
            'source_type': source_type,
            'filename': filename or 'unknown'
        }
        
        logger.debug(f"DEBUG: Resume prompt context: {context}")
        
        template = Template(self.template)
        rendered_prompt = template.render(**context)
        
        logger.info(f"DEBUG: Resume prompt rendered successfully")
        logger.info(f"Final prompt length: {len(rendered_prompt)}")
        logger.debug(f"DEBUG: Rendered resume prompt preview: {rendered_prompt[:300]}...")
        
        # Check for template variable issues
        if '{{' in rendered_prompt:
            logger.warning("WARNING: Template variables not properly rendered!")
        else:
            logger.info("SUCCESS: Template variables properly rendered")
        
        return rendered_prompt