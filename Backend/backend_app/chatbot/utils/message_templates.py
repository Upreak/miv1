"""
Message Templates for Chatbot/Co-Pilot Module

Provides pre-defined message templates for different scenarios and user interactions.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
import json


class TemplateCategory(Enum):
    """Categories of message templates"""
    ONBOARDING = "onboarding"
    RESUME_INTAKE = "resume_intake"
    JOB_MATCHING = "job_matching"
    JOB_CREATION = "job_creation"
    APPLICATION = "application"
    PROFILE = "profile"
    HELP = "help"
    ERROR = "error"
    SUCCESS = "success"
    CONFIRMATION = "confirmation"
    NOTIFICATION = "notification"


class MessageTemplates:
    """
    Collection of message templates for the chatbot system.
    
    Provides structured templates for different scenarios and user interactions.
    """
    
    # Onboarding Templates
    ONBOARDING_WELCOME = {
        'category': TemplateCategory.ONBOARDING,
        'template': "Welcome to our recruitment platform! I'm here to help you with your job search or hiring needs. Are you a Candidate looking for jobs or a Recruiter looking to hire?",
        'buttons': [
            {'text': 'Candidate', 'payload': 'candidate'},
            {'text': 'Recruiter', 'payload': 'recruiter'}
        ]
    }
    
    ONBOARDING_ROLE_SELECTED = {
        'category': TemplateCategory.ONBOARDING,
        'template': "Great! I'll help you as a {role}. Let me get started with setting up your profile.",
        'variables': ['role']
    }
    
    ONBOARDING_CANDIDATE_GUIDE = {
        'category': TemplateCategory.ONBOARDING,
        'template': "As a candidate, I can help you:\n\n• Upload your resume\n• Find job matches\n• Apply to positions\n• Track your applications\n\nWhat would you like to do first?",
        'buttons': [
            {'text': 'Upload Resume', 'payload': 'upload_resume'},
            {'text': 'Find Jobs', 'payload': 'find_jobs'},
            {'text': 'View Profile', 'payload': 'view_profile'}
        ]
    }
    
    ONBOARDING_RECRUITER_GUIDE = {
        'category': TemplateCategory.ONBOARDING,
        'template': "As a recruiter, I can help you:\n\n• Create job postings\n• Find candidates\n• Review applications\n• Manage hiring pipeline\n\nWhat would you like to do first?",
        'buttons': [
            {'text': 'Create Job', 'payload': 'create_job'},
            {'text': 'Find Candidates', 'payload': 'find_candidates'},
            {'text': 'View Jobs', 'payload': 'view_jobs'}
        ]
    }
    
    # Resume Intake Templates
    RESUME_UPLOAD_REQUEST = {
        'category': TemplateCategory.RESUME_INTAKE,
        'template': "Please upload your resume file. I can accept PDF, DOC, or DOCX files up to 10MB.",
        'buttons': [
            {'text': 'Upload File', 'payload': 'upload_file'},
            {'text': 'Skip', 'payload': 'skip_resume'}
        ]
    }
    
    RESUME_UPLOAD_SUCCESS = {
        'category': TemplateCategory.RESUME_INTAKE,
        'template': "Great! I've received your resume. Processing it now... This may take a few moments.",
        'variables': ['processing_time']
    }
    
    RESUME_UPLOAD_FAILED = {
        'category': TemplateCategory.ERROR,
        'template': "I'm sorry, I couldn't process your resume. Please try uploading a different file or contact support.",
        'buttons': [
            {'text': 'Try Again', 'payload': 'upload_resume'},
            {'text': 'Skip', 'payload': 'skip_resume'}
        ]
    }
    
    RESUME_PROCESSING_COMPLETE = {
        'category': TemplateCategory.SUCCESS,
        'template': "Perfect! I've processed your resume and created your profile. You can now search for jobs that match your skills and experience.",
        'buttons': [
            {'text': 'Find Jobs', 'payload': 'find_jobs'},
            {'text': 'View Profile', 'payload': 'view_profile'}
        ]
    }
    
    # Job Matching Templates
    JOB_SEARCH_REQUEST = {
        'category': TemplateCategory.JOB_MATCHING,
        'template': "What type of position are you looking for? You can search by job title, keywords, or location.",
        'buttons': [
            {'text': 'By Title', 'payload': 'search_by_title'},
            {'text': 'By Keywords', 'payload': 'search_by_keywords'},
            {'text': 'By Location', 'payload': 'search_by_location'}
        ]
    }
    
    JOB_SEARCH_RESULTS = {
        'category': TemplateCategory.JOB_MATCHING,
        'template': "I found {count} jobs that match your criteria:\n\n{job_list}",
        'variables': ['count', 'job_list'],
        'buttons': [
            {'text': 'View Details', 'payload': 'view_job_details'},
            {'text': 'Apply Now', 'payload': 'apply_job'},
            {'text': 'Search Again', 'payload': 'search_jobs'}
        ]
    }
    
    JOB_MATCH_SCORE = {
        'category': TemplateCategory.JOB_MATCHING,
        'template': "This job matches your profile with {score}% compatibility.\n\n{match_reasoning}",
        'variables': ['score', 'match_reasoning']
    }
    
    # Job Creation Templates
    JOB_CREATION_START = {
        'category': TemplateCategory.JOB_CREATION,
        'template': "Let's create a job posting! I'll guide you through the process step by step.",
        'buttons': [
            {'text': 'Start Creating', 'payload': 'start_job_creation'},
            {'text': 'View Templates', 'payload': 'view_job_templates'}
        ]
    }
    
    JOB_TITLE_REQUEST = {
        'category': TemplateCategory.JOB_CREATION,
        'template': "What's the job title? (e.g., Software Engineer, Marketing Manager, Sales Representative)",
        'buttons': [
            {'text': 'Use Template', 'payload': 'use_job_template'},
            {'text': 'Skip', 'payload': 'skip_job_title'}
        ]
    }
    
    JOB_DESCRIPTION_REQUEST = {
        'category': TemplateCategory.JOB_CREATION,
        'template': "Please provide a job description. Include key responsibilities, requirements, and qualifications.",
        'buttons': [
            {'text': 'Generate AI Description', 'payload': 'generate_ai_description'},
            {'text': 'Use Template', 'payload': 'use_job_template'}
        ]
    }
    
    JOB_CREATION_SUCCESS = {
        'category': TemplateCategory.SUCCESS,
        'template': "Excellent! Your job '{job_title}' has been created and posted. Candidates can now apply for this position.",
        'variables': ['job_title'],
        'buttons': [
            {'text': 'View Job', 'payload': 'view_job'},
            {'text': 'Create Another', 'payload': 'create_another_job'},
            {'text': 'Find Candidates', 'payload': 'find_candidates'}
        ]
    }
    
    # Application Templates
    APPLICATION_START = {
        'category': TemplateCategory.APPLICATION,
        'template': "Ready to apply for '{job_title}'? I'll help you submit your application.",
        'variables': ['job_title'],
        'buttons': [
            {'text': 'Apply Now', 'payload': 'confirm_application'},
            {'text': 'View Requirements', 'payload': 'view_job_requirements'},
            {'text': 'Cancel', 'payload': 'cancel_application'}
        ]
    }
    
    APPLICATION_SUBMITTED = {
        'category': TemplateCategory.SUCCESS,
        'template': "Great! Your application for '{job_title}' has been submitted successfully. You'll receive updates on your application status.",
        'variables': ['job_title'],
        'buttons': [
            {'text': 'View Application', 'payload': 'view_application'},
            {'text': 'Find More Jobs', 'payload': 'find_jobs'},
            {'text': 'View Profile', 'payload': 'view_profile'}
        ]
    }
    
    # Profile Templates
    PROFILE_VIEW = {
        'category': TemplateCategory.PROFILE,
        'template': "Here's your profile:\n\n{profile_summary}\n\n{skills}\n\n{experience}",
        'variables': ['profile_summary', 'skills', 'experience'],
        'buttons': [
            {'text': 'Edit Profile', 'payload': 'edit_profile'},
            {'text': 'Update Skills', 'payload': 'update_skills'},
            {'text': 'Add Experience', 'payload': 'add_experience'}
        ]
    }
    
    PROFILE_UPDATE_REQUEST = {
        'category': TemplateCategory.PROFILE,
        'template': "What would you like to update in your profile?",
        'buttons': [
            {'text': 'Personal Info', 'payload': 'update_personal_info'},
            {'text': 'Skills', 'payload': 'update_skills'},
            {'text': 'Experience', 'payload': 'update_experience'},
            {'text': 'Education', 'payload': 'update_education'}
        ]
    }
    
    # Help Templates
    HELP_GENERAL = {
        'category': TemplateCategory.HELP,
        'template': "I'm here to help! Here's what I can do:\n\n• Upload and process your resume\n• Find job matches based on your profile\n• Apply to jobs\n• Create job postings\n• Find candidates\n• Track applications\n\nWhat would you like help with?",
        'buttons': [
            {'text': 'Resume Help', 'payload': 'help_resume'},
            {'text': 'Job Search Help', 'payload': 'help_job_search'},
            {'text': 'Application Help', 'payload': 'help_application'},
            {'text': 'Recruiter Help', 'payload': 'help_recruiter'}
        ]
    }
    
    HELP_CANDIDATE = {
        'category': TemplateCategory.HELP,
        'template': "As a candidate, I can help you:\n\n• Upload your resume for processing\n• Search for jobs that match your skills\n• Apply to positions with one click\n• Track your application status\n• Update your profile\n\nWhat specific help do you need?",
        'buttons': [
            {'text': 'Upload Resume', 'payload': 'upload_resume'},
            {'text': 'Find Jobs', 'payload': 'find_jobs'},
            {'text': 'View Profile', 'payload': 'view_profile'},
            {'text': 'General Help', 'payload': 'general_help'}
        ]
    }
    
    HELP_RECRUITER = {
        'category': TemplateCategory.HELP,
        'template': "As a recruiter, I can help you:\n\n• Create detailed job postings\n• Find qualified candidates\n• Review applications\n• Manage your hiring pipeline\n• Track candidate progress\n\nWhat specific help do you need?",
        'buttons': [
            {'text': 'Create Job', 'payload': 'create_job'},
            {'text': 'Find Candidates', 'payload': 'find_candidates'},
            {'text': 'View Jobs', 'payload': 'view_jobs'},
            {'text': 'General Help', 'payload': 'general_help'}
        ]
    }
    
    # Error Templates
    ERROR_GENERAL = {
        'category': TemplateCategory.ERROR,
        'template': "I'm sorry, I encountered an error. Please try again or contact support if the problem persists.",
        'buttons': [
            {'text': 'Try Again', 'payload': 'retry'},
            {'text': 'Contact Support', 'payload': 'contact_support'},
            {'text': 'Go Back', 'payload': 'go_back'}
        ]
    }
    
    ERROR_INVALID_INPUT = {
        'category': TemplateCategory.ERROR,
        'template': "I'm sorry, I didn't understand that. Please try again or type 'help' for assistance.",
        'buttons': [
            {'text': 'Try Again', 'payload': 'retry'},
            {'text': 'Help', 'payload': 'help'}
        ]
    }
    
    ERROR_FILE_TOO_LARGE = {
        'category': TemplateCategory.ERROR,
        'template': "The file is too large. Please upload a file smaller than 10MB.",
        'buttons': [
            {'text': 'Try Again', 'payload': 'upload_resume'},
            {'text': 'Skip', 'payload': 'skip_resume'}
        ]
    }
    
    ERROR_FILE_INVALID = {
        'category': TemplateCategory.ERROR,
        'template': "Invalid file format. Please upload a PDF, DOC, or DOCX file.",
        'buttons': [
            {'text': 'Try Again', 'payload': 'upload_resume'},
            {'text': 'Skip', 'payload': 'skip_resume'}
        ]
    }
    
    # Success Templates
    SUCCESS_GENERAL = {
        'category': TemplateCategory.SUCCESS,
        'template': "Perfect! I've completed that task successfully.",
        'buttons': [
            {'text': 'Great!', 'payload': 'success_acknowledgment'},
            {'text': 'What\'s Next?', 'payload': 'what_next'}
        ]
    }
    
    SUCCESS_PROFILE_UPDATE = {
        'category': TemplateCategory.SUCCESS,
        'template': "Your profile has been updated successfully!",
        'buttons': [
            {'text': 'View Profile', 'payload': 'view_profile'},
            {'text': 'Find Jobs', 'payload': 'find_jobs'},
            {'text': 'Update More', 'payload': 'update_profile'}
        ]
    }
    
    # Confirmation Templates
    CONFIRMATION_GENERAL = {
        'category': TemplateCategory.CONFIRMATION,
        'template': "Are you sure you want to {action}?",
        'variables': ['action'],
        'buttons': [
            {'text': 'Yes', 'payload': 'confirm_yes'},
            {'text': 'No', 'payload': 'confirm_no'}
        ]
    }
    
    CONFIRMATION_APPLICATION = {
        'category': TemplateCategory.CONFIRMATION,
        'template': "Are you sure you want to apply for '{job_title}'? This will submit your application and resume.",
        'variables': ['job_title'],
        'buttons': [
            {'text': 'Yes, Apply', 'payload': 'confirm_application'},
            {'text': 'No, Cancel', 'payload': 'cancel_application'}
        ]
    }
    
    # Notification Templates
    NOTIFICATION_NEW_JOB = {
        'category': TemplateCategory.NOTIFICATION,
        'template': "New job alert! I found {count} new jobs that match your profile.",
        'variables': ['count'],
        'buttons': [
            {'text': 'View Jobs', 'payload': 'view_new_jobs'},
            {'text': 'Later', 'payload': 'notification_later'}
        ]
    }
    
    NOTIFICATION_APPLICATION_STATUS = {
        'category': TemplateCategory.NOTIFICATION,
        'template': "Update on your application for '{job_title}': {status}",
        'variables': ['job_title', 'status'],
        'buttons': [
            {'text': 'View Details', 'payload': 'view_application_details'},
            {'text': 'View All Applications', 'payload': 'view_all_applications'}
        ]
    }
    
    @classmethod
    def get_template(cls, category: TemplateCategory, template_name: str, variables: Dict[str, Any] = None) -> str:
        """
        Get a specific template with optional variable substitution.
        
        Args:
            category: Template category
            template_name: Template name
            variables: Dictionary of variables to substitute
            
        Returns:
            str: Formatted template string
        """
        # Get all templates for the category
        category_templates = []
        
        # Search through all class attributes for templates in the specified category
        for attr_name in dir(cls):
            attr_value = getattr(cls, attr_name)
            if isinstance(attr_value, dict) and attr_value.get('category') == category:
                category_templates.append(attr_value)
        
        # Find the specific template
        for template in category_templates:
            if template_name.lower() in attr_name.lower():
                template_text = template.get('template', '')
                
                # Substitute variables
                if variables:
                    for key, value in variables.items():
                        template_text = template_text.replace(f'{{{key}}}', str(value))
                
                return template_text
        
        # Return default template if not found
        return cls.get_template(TemplateCategory.ERROR, 'general')
    
    @classmethod
    def get_category_templates(cls, category: TemplateCategory) -> List[Dict[str, Any]]:
        """
        Get all templates for a specific category.
        
        Args:
            category: Template category
            
        Returns:
            List[Dict[str, Any]]: List of templates in the category
        """
        templates = []
        
        for attr_name in dir(cls):
            attr_value = getattr(cls, attr_name)
            if isinstance(attr_value, dict) and attr_value.get('category') == category:
                templates.append(attr_value)
        
        return templates
    
    @classmethod
    def get_template_with_buttons(cls, category: TemplateCategory, template_name: str, 
                                variables: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get a template with buttons and variables.
        
        Args:
            category: Template category
            template_name: Template name
            variables: Dictionary of variables to substitute
            
        Returns:
            Dict[str, Any]: Template with buttons and variables
        """
        # Get the template
        template_text = cls.get_template(category, template_name, variables)
        
        # Find the full template object
        for attr_name in dir(cls):
            attr_value = getattr(cls, attr_name)
            if isinstance(attr_value, dict) and attr_value.get('category') == category:
                if template_name.lower() in attr_name.lower():
                    result = attr_value.copy()
                    result['template'] = template_text
                    return result
        
        # Return default template
        return {
            'category': TemplateCategory.ERROR,
            'template': cls.get_template(TemplateCategory.ERROR, 'general'),
            'buttons': []
        }
    
    @classmethod
    def generate_custom_message(cls, category: TemplateCategory, message: str, 
                               buttons: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Generate a custom message template.
        
        Args:
            category: Template category
            message: Custom message text
            buttons: Optional list of buttons
            
        Returns:
            Dict[str, Any]: Custom template
        """
        return {
            'category': category,
            'template': message,
            'buttons': buttons or []
        }
    
    @classmethod
    def get_onboarding_flow(cls) -> List[Dict[str, Any]]:
        """
        Get the complete onboarding flow templates.
        
        Returns:
            List[Dict[str, Any]]: Onboarding flow templates
        """
        return [
            cls.ONBOARDING_WELCOME,
            cls.ONBOARDING_CANDIDATE_GUIDE,
            cls.ONBOARDING_RECRUITER_GUIDE
        ]
    
    @classmethod
    def get_resume_intake_flow(cls) -> List[Dict[str, Any]]:
        """
        Get the complete resume intake flow templates.
        
        Returns:
            List[Dict[str, Any]]: Resume intake flow templates
        """
        return [
            cls.RESUME_UPLOAD_REQUEST,
            cls.RESUME_UPLOAD_SUCCESS,
            cls.RESUME_PROCESSING_COMPLETE
        ]
    
    @classmethod
    def get_job_search_flow(cls) -> List[Dict[str, Any]]:
        """
        Get the complete job search flow templates.
        
        Returns:
            List[Dict[str, Any]]: Job search flow templates
        """
        return [
            cls.JOB_SEARCH_REQUEST,
            cls.JOB_SEARCH_RESULTS,
            cls.JOB_MATCH_SCORE
        ]
    
    @classmethod
    def get_job_creation_flow(cls) -> List[Dict[str, Any]]:
        """
        Get the complete job creation flow templates.
        
        Returns:
            List[Dict[str, Any]]: Job creation flow templates
        """
        return [
            cls.JOB_CREATION_START,
            cls.JOB_TITLE_REQUEST,
            cls.JOB_DESCRIPTION_REQUEST,
            cls.JOB_CREATION_SUCCESS
        ]
    
    @classmethod
    def get_application_flow(cls) -> List[Dict[str, Any]]:
        """
        Get the complete application flow templates.
        
        Returns:
            List[Dict[str, Any]]: Application flow templates
        """
        return [
            cls.APPLICATION_START,
            cls.APPLICATION_SUBMITTED
        ]
    
    @classmethod
    def get_help_flow(cls) -> List[Dict[str, Any]]:
        """
        Get the complete help flow templates.
        
        Returns:
            List[Dict[str, Any]]: Help flow templates
        """
        return [
            cls.HELP_GENERAL,
            cls.HELP_CANDIDATE,
            cls.HELP_RECRUITER
        ]
    
    @classmethod
    def export_templates(cls, category: TemplateCategory = None) -> Dict[str, Any]:
        """
        Export templates to JSON format.
        
        Args:
            category: Optional category to export
            
        Returns:
            Dict[str, Any]: Exported templates
        """
        export_data = {}
        
        if category:
            templates = cls.get_category_templates(category)
            export_data[category.value] = templates
        else:
            for cat in TemplateCategory:
                templates = cls.get_category_templates(cat)
                export_data[cat.value] = templates
        
        return export_data
    
    @classmethod
    def import_templates(cls, json_data: str) -> bool:
        """
        Import templates from JSON format.
        
        Args:
            json_data: JSON string containing templates
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            data = json.loads(json_data)
            
            # This would dynamically add templates to the class
            # For now, we'll just validate the format
            for category_name, templates in data.items():
                if not isinstance(templates, list):
                    return False
                
                for template in templates:
                    if not isinstance(template, dict):
                        return False
                    
                    if 'category' not in template or 'template' not in template:
                        return False
            
            return True
            
        except json.JSONDecodeError:
            return False