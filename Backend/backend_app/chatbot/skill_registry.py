"""
Chatbot Skill Registry - Auto-registration system for all skills
"""
from backend_app.chatbot.services.skill_registry import SkillRegistry
from backend_app.chatbot.services.message_router import MessageRouter
from backend_app.chatbot.services.sid_service import SIDService
from backend_app.chatbot.services.llm_service import LLMService
from backend_app.chatbot.services.skills.onboarding_skill import OnboardingSkill
from backend_app.chatbot.services.skills.resume_intake_skill import ResumeIntakeSkill
from backend_app.chatbot.services.skills.candidate_matching_skill import CandidateMatchingSkill
from backend_app.chatbot.services.skills.job_creation_skill import JobCreationSkill
from backend_app.chatbot.services.skills.onboarding_skill import OnboardingSkill
# from backend_app.chatbot.services.skills.profile_update_skill import ProfileUpdateSkill  # Commented out - not available
from backend_app.chatbot.services.skills.base_skill import BaseSkill
from backend_app.chatbot.services.jdkb_service import JDKBService
from backend_app.repositories.jobs_repo import JobsRepository
from backend_app.services.profile_writer import ProfileWriter
import logging

logger = logging.getLogger(__name__)

# Global skill registry instance
skill_registry = SkillRegistry()

# Global message router instance
message_router = None

# Global services
llm_service = None
sid_service = None
jdkb_service = None
profile_writer = None
jobs_repo = None


def initialize_chatbot_system(db_session=None):
    """
    Initialize the chatbot system with all skills and services
    """
    global skill_registry, message_router, llm_service, sid_service, jobs_repo
    
    try:
        # Initialize services
        if db_session:
            sid_service = SIDService(db_session)
            jobs_repo = JobsRepository(db_session)
            jdkb_service = JDKBService(jobs_repo)
            profile_writer = ProfileWriter(db_session)
        else:
            # Create a mock SID service for now
            class MockSIDService:
                def get_or_create(self, channel, channel_user_id, user_id=None):
                    return MockSession(channel, channel_user_id, user_id)
            
            class MockSession:
                def __init__(self, channel, channel_user_id, user_id):
                    self.sid = f"mock_{channel}_{channel_user_id}"
                    self.channel = channel
                    self.channel_user_id = channel_user_id
                    self.user_id = user_id
            
            sid_service = MockSIDService()
            # jdkb_service remains None or we could mock it
        
        llm_service = LLMService()
        message_router = MessageRouter(skill_registry, sid_service)
        
        # Register all skills
        register_all_skills()
        
        logger.info("Chatbot system initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing chatbot system: {e}")
        return False


def register_all_skills():
    """Register all available skills with the skill registry"""
    global skill_registry
    
    try:
        # List of skills to register with their priorities
        skills_to_register = [
            (OnboardingSkill(), 20),  # Highest priority for onboarding
            (ResumeIntakeSkill(profile_writer), 15),  # High priority for resume intake
            (CandidateMatchingSkill(jdkb_service), 12),  # Medium-high priority for matching
            (JobCreationSkill(jobs_repo), 10),  # Medium priority for job creation
            # (ProfileUpdateSkill(), 8),  # Commented out - not available
        ]
        
        # Register each skill
        for skill, priority in skills_to_register:
            try:
                skill_registry.register(skill, priority)
                logger.info(f"Registered skill: {skill.name} with priority {priority}")
            except Exception as e:
                logger.error(f"Failed to register skill {skill.name}: {e}")
                continue
        
        logger.info(f"Successfully registered {len(skills_to_register)} skills")
        return True
        
    except Exception as e:
        logger.error(f"Error registering skills: {e}")
        return False


def get_skill_registry():
    """Get the global skill registry instance"""
    return skill_registry


def get_message_router():
    """Get the global message router instance"""
    return message_router


def get_llm_service():
    """Get the global LLM service instance"""
    return llm_service


def get_sid_service():
    """Get the global SID service instance"""
    return sid_service


def get_skill_stats():
    """Get statistics about registered skills"""
    try:
        stats = skill_registry.get_all_execution_stats()
        registry_stats = skill_registry.get_skill_performance_report()
        
        return {
            "total_skills": len(stats),
            "skills": stats,
            "performance_report": registry_stats
        }
    except Exception as e:
        logger.error(f"Error getting skill stats: {e}")
        return {"error": str(e)}


def validate_skill_registration():
    """Validate that all expected skills are registered"""
    try:
        expected_skills = [
            "onboarding_skill",
            "resume_intake_skill", 
            "candidate_matching_skill",
            "job_creation_skill",
            "profile_update_skill"
        ]
        
        registered_skills = [skill.name for skill in skill_registry.get_all()]
        missing_skills = [skill for skill in expected_skills if skill not in registered_skills]
        
        if missing_skills:
            logger.warning(f"Missing skills: {missing_skills}")
            return False, missing_skills
        else:
            logger.info("All expected skills are registered")
            return True, []
            
    except Exception as e:
        logger.error(f"Error validating skill registration: {e}")
        return False, [str(e)]


def reset_skill_registry():
    """Reset the skill registry (for testing/debugging)"""
    global skill_registry, message_router
    
    try:
        skill_registry = SkillRegistry()
        if message_router:
            message_router.skill_registry = skill_registry
        logger.info("Skill registry reset successfully")
        return True
    except Exception as e:
        logger.error(f"Error resetting skill registry: {e}")
        return False


# Auto-initialize when module is imported
if __name__ == "__main__":
    # This allows the module to be tested independently
    success = initialize_chatbot_system()
    if success:
        print("Chatbot system initialized successfully")
        stats = get_skill_stats()
        print(f"Registered skills: {stats.get('total_skills', 0)}")
    else:
        print("Failed to initialize chatbot system")
