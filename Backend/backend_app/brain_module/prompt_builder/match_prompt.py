# prompts/match_prompt.py
from typing import Dict, Any
from jinja2 import Template
import json

class MatchPromptRenderer:
    """Renders prompts for candidate-job matching"""
    
    def __init__(self):
        self.template = self._get_match_template()
    
    def _get_match_template(self) -> str:
        """Get the candidate-job matching template"""
        return """Task:
Analyze the candidate profile and job description to provide a comprehensive matching score and detailed analysis. Compare skills, experience, education, and other relevant factors.

General Rules:
- Score from 0-100 based on overall fit
- Provide detailed justification for the score
- Identify strengths and gaps
- Consider experience level match
- Focus on practical skills alignment
- Output strictly in JSON

Output Fields:
{
  "match_score": <number between 0-100>,
  "overall_assessment": "<summary of the match>",
  "strengths": ["<list of candidate strengths for this role>"],
  "gaps": ["<list of potential gaps or concerns>"],
  "skill_match": {
    "matched_skills": ["<skills candidate has that match job requirements>"],
    "missing_skills": ["<skills required but candidate lacks>"],
    "partial_matches": ["<skills with some relevance but not exact match>"]
  },
  "experience_analysis": {
    "years_required": "<years required in job>",
    "candidate_experience": "<candidate's total experience>",
    "relevant_experience": "<years in relevant domain/role>",
    "experience_fit": "<assessment of experience level match>"
  },
  "education_analysis": {
    "required_education": "<education requirements from job>",
    "candidate_education": "<candidate's education level>",
    "education_match": "<assessment of education fit>"
  },
  "recommendations": {
    "next_steps": ["<suggested actions for hiring process>"],
    "training_needed": ["<areas where candidate might need training>"],
    "interview_focus": ["<topics to focus on during interview>"]
  },
  "risk_factors": ["<potential red flags or concerns>"],
  "cultural_fit_indicators": ["<factors suggesting good cultural fit>"]
}

Candidate Profile:
{{ candidate_data }}

Job Description:
{{ job_data }}
"""
    
    def render_prompt(self, candidate_data: str, job_data: str) -> str:
        """Render the matching prompt"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info("=== MATCH PROMPT RENDERING SYSTEM DEBUG ===")
        logger.info(f"System: Python Class (MatchPromptRenderer)")
        logger.info(f"Template source: Hardcoded string in Python class")
        logger.info(f"Candidate data length: {len(candidate_data)}")
        logger.info(f"Job data length: {len(job_data)}")
        
        logger.debug(f"DEBUG: Candidate data preview: {candidate_data[:200]}...")
        logger.debug(f"DEBUG: Job data preview: {job_data[:200]}...")
        
        context = {
            'candidate_data': candidate_data,
            'job_data': job_data
        }
        
        logger.debug(f"DEBUG: Match prompt context: {context}")
        
        template = Template(self.template)
        rendered_prompt = template.render(**context)
        
        logger.info(f"DEBUG: Match prompt rendered successfully")
        logger.info(f"Final prompt length: {len(rendered_prompt)}")
        logger.debug(f"DEBUG: Rendered match prompt preview: {rendered_prompt[:300]}...")
        
        # Check for template variable issues
        if '{{' in rendered_prompt:
            logger.warning("WARNING: Template variables not properly rendered!")
        else:
            logger.info("SUCCESS: Template variables properly rendered")
        
        return rendered_prompt