"""
Conversation State Model for Chatbot/Co-Pilot Module

Defines the conversation state management system for tracking
user interactions and maintaining context across conversations.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum

class UserRole(Enum):
    """User roles in the chatbot system"""
    CANDIDATE = "candidate"
    RECRUITER = "recruiter"
    UNKNOWN = "unknown"

class ConversationState(Enum):
    """Conversation states for different workflows"""
    ONBOARDING = "onboarding"
    AWAITING_ROLE = "awaiting_role"
    AWAITING_RESUME = "awaiting_resume"
    PROFILE_READY = "profile_ready"
    RECRUITER_FLOW = "recruiter_flow"
    CANDIDATE_FLOW = "candidate_flow"
    JOB_CREATION = "job_creation"
    MATCHING = "matching"
    APPLICATION = "application"
    IDLE = "idle"
    ERROR = "error"

@dataclass
class SkillContext:
    """
    Context data for individual skills
    """
    skill_name: str
    trigger_message: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    execution_time: Optional[float] = None
    result: Optional[Any] = None
    error: Optional[str] = None

@dataclass
class ConversationContext:
    """
    Complete conversation context for a session
    """
    sid: str
    user_id: Optional[str] = None
    role: UserRole = UserRole.UNKNOWN
    current_state: ConversationState = ConversationState.ONBOARDING
    history: List[Dict[str, Any]] = field(default_factory=list)
    skill_contexts: List[SkillContext] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def update_state(self, new_state: ConversationState) -> None:
        """Update conversation state"""
        self.current_state = new_state
        self.updated_at = datetime.utcnow()
        
        # Add state transition to history
        self.history.append({
            'type': 'state_transition',
            'from_state': self.current_state.value,
            'to_state': new_state.value,
            'timestamp': self.updated_at.isoformat()
        })
    
    def add_message(self, message: str, sender: str = "user") -> None:
        """Add message to conversation history"""
        self.history.append({
            'type': 'message',
            'sender': sender,
            'content': message,
            'timestamp': datetime.utcnow().isoformat()
        })
        self.updated_at = datetime.utcnow()
    
    def add_skill_context(self, skill_context: SkillContext) -> None:
        """Add skill execution context"""
        self.skill_contexts.append(skill_context)
        self.updated_at = datetime.utcnow()
    
    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata value"""
        self.metadata[key] = value
        self.updated_at = datetime.utcnow()
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value"""
        return self.metadata.get(key, default)
    
    def get_last_message(self) -> Optional[Dict[str, Any]]:
        """Get the last message from history"""
        for item in reversed(self.history):
            if item.get('type') == 'message':
                return item
        return None
    
    def get_skill_results(self, skill_name: str) -> List[SkillContext]:
        """Get results from specific skill"""
        return [ctx for ctx in self.skill_contexts if ctx.skill_name == skill_name]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary"""
        return {
            'sid': self.sid,
            'user_id': self.user_id,
            'role': self.role.value,
            'current_state': self.current_state.value,
            'history': self.history,
            'skill_contexts': [
                {
                    'skill_name': ctx.skill_name,
                    'trigger_message': ctx.trigger_message,
                    'parameters': ctx.parameters,
                    'execution_time': ctx.execution_time,
                    'result': ctx.result,
                    'error': ctx.error
                }
                for ctx in self.skill_contexts
            ],
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class ConversationStateManager:
    """
    Manager for conversation state operations
    """
    
    @staticmethod
    def create_initial_context(sid: str, user_id: Optional[str] = None) -> ConversationContext:
        """Create initial conversation context"""
        return ConversationContext(
            sid=sid,
            user_id=user_id,
            role=UserRole.UNKNOWN,
            current_state=ConversationState.ONBOARDING
        )
    
    @staticmethod
    def transition_to_candidate_flow(context: ConversationContext) -> None:
        """Transition to candidate flow"""
        context.update_state(ConversationState.CANDIDATE_FLOW)
        context.set_metadata('flow_type', 'candidate')
    
    @staticmethod
    def transition_to_recruiter_flow(context: ConversationContext) -> None:
        """Transition to recruiter flow"""
        context.update_state(ConversationState.RECRUITER_FLOW)
        context.set_metadata('flow_type', 'recruiter')
    
    @staticmethod
    def transition_to_awaiting_resume(context: ConversationContext) -> None:
        """Transition to awaiting resume state"""
        context.update_state(ConversationState.AWAITING_RESUME)
        context.set_metadata('awaiting_document', 'resume')
    
    @staticmethod
    def transition_to_job_creation(context: ConversationContext) -> None:
        """Transition to job creation state"""
        context.update_state(ConversationState.JOB_CREATION)
        context.set_metadata('creation_type', 'job')
    
    @staticmethod
    def transition_to_matching(context: ConversationContext) -> None:
        """Transition to matching state"""
        context.update_state(ConversationState.MATCHING)
        context.set_metadata('matching_type', 'jobs')
    
    @staticmethod
    def is_in_state(context: ConversationContext, *states: ConversationState) -> bool:
        """Check if context is in any of the specified states"""
        return context.current_state in states
    
    @staticmethod
    def can_handle_skill(context: ConversationContext, skill_name: str) -> bool:
        """Check if skill can handle current context"""
        # Define skill-state mappings
        skill_state_mappings = {
            'onboarding_skill': [ConversationState.ONBOARDING, ConversationState.AWAITING_ROLE],
            'resume_intake_skill': [ConversationState.AWAITING_RESUME],
            'candidate_matching_skill': [ConversationState.CANDIDATE_FLOW, ConversationState.MATCHING],
            'job_creation_skill': [ConversationState.RECRUITER_FLOW, ConversationState.JOB_CREATION],
            'application_status_skill': [ConversationState.APPLICATION],
            'profile_update_skill': [ConversationState.PROFILE_READY]
        }
        
        allowed_states = skill_state_mappings.get(skill_name, [])
        return context.current_state in allowed_states