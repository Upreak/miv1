"""
State Machine Framework for Chatbot/Co-Pilot Module

Implements a robust state machine for managing conversation flows across
different user roles (candidate/recruiter) and platforms (WhatsApp/Telegram/Web).
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable, Tuple
from enum import Enum as PyEnum
from dataclasses import dataclass, field

from ..models.session_model import Session, UserRole, ConversationState
from ..services.session_service import SessionService
from ..utils.skill_context import SkillContext

logger = logging.getLogger(__name__)


class TransitionResult(PyEnum):
    """Result of a state transition"""
    SUCCESS = "success"
    INVALID_TRANSITION = "invalid_transition"
    VALIDATION_FAILED = "validation_failed"
    ERROR = "error"


@dataclass
class Transition:
    """Represents a state transition"""
    from_state: ConversationState
    to_state: ConversationState
    condition: Optional[Callable] = None
    action: Optional[Callable] = None
    validation_rules: List[str] = field(default_factory=list)


@dataclass
class StateTransitionResult:
    """Result of a state transition attempt"""
    result: TransitionResult
    new_state: Optional[ConversationState]
    context_updates: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class StateMachine:
    """
    State Machine for managing chatbot conversation flows.
    
    This state machine handles:
    - State transitions based on user input and context
    - Validation of transitions
    - Context management across states
    - Error handling and recovery
    - State persistence
    """
    
    def __init__(self, session_service: SessionService):
        """
        Initialize State Machine.
        
        Args:
            session_service: Session service for persistence
        """
        self.session_service = session_service
        self.transitions: List[Transition] = []
        self.state_handlers: Dict[ConversationState, Callable] = {}
        self._build_state_transitions()
        self._build_state_handlers()
    
    def _build_state_transitions(self):
        """Define valid state transitions"""
        # Candidate flow transitions
        candidate_transitions = [
            # Onboarding flow
            Transition(
                from_state=ConversationState.ONBOARDING,
                to_state=ConversationState.AWAITING_RESUME,
                condition=self._is_resume_required,
                validation_rules=["user_authenticated"]
            ),
            Transition(
                from_state=ConversationState.ONBOARDING,
                to_state=ConversationState.PROFILE_READY,
                condition=self._is_profile_complete,
                validation_rules=["user_authenticated"]
            ),
            
            # Resume processing flow
            Transition(
                from_state=ConversationState.AWAITING_RESUME,
                to_state=ConversationState.PROFILE_READY,
                condition=self._is_resume_processed,
                validation_rules=["resume_received", "profile_extracted"]
            ),
            
            # Application flow
            Transition(
                from_state=ConversationState.PROFILE_READY,
                to_state=ConversationState.APPLICATION,
                condition=self._has_job_match,
                validation_rules=["job_selected"]
            ),
            
            # Matching flow
            Transition(
                from_state=ConversationState.PROFILE_READY,
                to_state=ConversationState.MATCHING,
                condition=self._wants_matching,
                validation_rules=["profile_ready"]
            ),
            
            # Idle transitions
            Transition(
                from_state=ConversationState.PROFILE_READY,
                to_state=ConversationState.IDLE,
                condition=self._user_idle,
            ),
            Transition(
                from_state=ConversationState.APPLICATION,
                to_state=ConversationState.IDLE,
                condition=self._application_complete,
            ),
        ]
        
        # Recruiter flow transitions
        recruiter_transitions = [
            # Recruiter onboarding
            Transition(
                from_state=ConversationState.ONBOARDING,
                to_state=ConversationState.RECRUITER_FLOW,
                condition=self._is_recruiter_authenticated,
                validation_rules=["recruiter_authenticated"]
            ),
            
            # Job creation flow
            Transition(
                from_state=ConversationState.RECRUITER_FLOW,
                to_state=ConversationState.JOB_CREATION,
                condition=self._wants_create_job,
                validation_rules=["recruiter_authenticated"]
            ),
            
            # Matching flow for recruiters
            Transition(
                from_state=ConversationState.RECRUITER_FLOW,
                to_state=ConversationState.MATCHING,
                condition=self._wants_candidate_matching,
                validation_rules=["job_selected"]
            ),
            
            # Idle transitions
            Transition(
                from_state=ConversationState.RECRUITER_FLOW,
                to_state=ConversationState.IDLE,
                condition=self._recruiter_idle,
            ),
        ]
        
        # Universal transitions
        universal_transitions = [
            # Any state can go to onboarding if user starts over
            Transition(
                from_state=ConversationState.IDLE,
                to_state=ConversationState.ONBOARDING,
                condition=self._wants_restart,
            ),
            
            # Help transitions from any state
            Transition(
                from_state=ConversationState.ONBOARDING,
                to_state=ConversationState.ONBOARDING,
                condition=self._requests_help,
            ),
            Transition(
                from_state=ConversationState.AWAITING_RESUME,
                to_state=ConversationState.AWAITING_RESUME,
                condition=self._requests_help,
            ),
            Transition(
                from_state=ConversationState.PROFILE_READY,
                to_state=ConversationState.PROFILE_READY,
                condition=self._requests_help,
            ),
            Transition(
                from_state=ConversationState.RECRUITER_FLOW,
                to_state=ConversationState.RECRUITER_FLOW,
                condition=self._requests_help,
            ),
            Transition(
                from_state=ConversationState.JOB_CREATION,
                to_state=ConversationState.JOB_CREATION,
                condition=self._requests_help,
            ),
            Transition(
                from_state=ConversationState.MATCHING,
                to_state=ConversationState.MATCHING,
                condition=self._requests_help,
            ),
            Transition(
                from_state=ConversationState.APPLICATION,
                to_state=ConversationState.APPLICATION,
                condition=self._requests_help,
            ),
        ]
        
        self.transitions = candidate_transitions + recruiter_transitions + universal_transitions
    
    def _build_state_handlers(self):
        """Build state-specific handlers"""
        self.state_handlers = {
            ConversationState.ONBOARDING: self._handle_onboarding,
            ConversationState.AWAITING_RESUME: self._handle_awaiting_resume,
            ConversationState.PROFILE_READY: self._handle_profile_ready,
            ConversationState.RECRUITER_FLOW: self._handle_recruiter_flow,
            ConversationState.JOB_CREATION: self._handle_job_creation,
            ConversationState.MATCHING: self._handle_matching,
            ConversationState.APPLICATION: self._handle_application,
            ConversationState.IDLE: self._handle_idle,
        }
    
    async def transition_state(
        self,
        session_id: str,
        intent: str,
        context: Dict[str, Any],
        user_message: Optional[str] = None
    ) -> StateTransitionResult:
        """
        Attempt to transition to a new state based on intent and context.
        
        Args:
            session_id: Session identifier
            intent: User intent
            context: Current context
            user_message: Optional user message
            
        Returns:
            StateTransitionResult: Result of transition attempt
        """
        try:
            # Get current session
            session = await self.session_service.get_session(session_id)
            if not session:
                return StateTransitionResult(
                    result=TransitionResult.ERROR,
                    new_state=None,
                    error_message="Session not found"
                )
            
            current_state = session.state
            user_role = session.role
            
            # Find valid transition
            transition = self._find_valid_transition(
                current_state, intent, context, user_role
            )
            
            if not transition:
                return StateTransitionResult(
                    result=TransitionResult.INVALID_TRANSITION,
                    new_state=current_state,
                    error_message=f"No valid transition from {current_state.value} for intent {intent}"
                )
            
            # Validate transition
            validation_result = await self._validate_transition(
                transition, session, context, user_message
            )
            
            if not validation_result["valid"]:
                return StateTransitionResult(
                    result=TransitionResult.VALIDATION_FAILED,
                    new_state=current_state,
                    error_message=validation_result["error"],
                    context_updates=validation_result.get("context_updates", {})
                )
            
            # Execute transition
            new_state = transition.to_state
            
            # Execute transition action if exists
            if transition.action:
                try:
                    action_result = await transition.action(session, context, user_message)
                    if action_result:
                        context.update(action_result)
                except Exception as e:
                    logger.error(f"Error executing transition action: {e}")
                    return StateTransitionResult(
                        result=TransitionResult.ERROR,
                        new_state=current_state,
                        error_message=f"Action execution failed: {str(e)}"
                    )
            
            # Update session state
            updated_session = await self.session_service.update_session_state(
                session_id, new_state
            )
            
            if not updated_session:
                return StateTransitionResult(
                    result=TransitionResult.ERROR,
                    new_state=current_state,
                    error_message="Failed to update session state"
                )
            
            # Get state handler response
            handler_response = await self._execute_state_handler(
                new_state, session, context, user_message
            )
            
            logger.info(f"State transition: {current_state.value} -> {new_state.value} for session {session_id}")
            
            return StateTransitionResult(
                result=TransitionResult.SUCCESS,
                new_state=new_state,
                context_updates=handler_response.get("context_updates", {}),
                metadata={
                    "previous_state": current_state.value,
                    "transition_time": datetime.utcnow().isoformat(),
                    "intent": intent,
                    "handler_response": handler_response.get("message", "")
                }
            )
            
        except Exception as e:
            logger.error(f"Error in state transition: {e}")
            return StateTransitionResult(
                result=TransitionResult.ERROR,
                new_state=session.state if session else None,
                error_message=str(e)
            )
    
    def _find_valid_transition(
        self,
        current_state: ConversationState,
        intent: str,
        context: Dict[str, Any],
        user_role: UserRole
    ) -> Optional[Transition]:
        """Find a valid transition for the current state and intent"""
        for transition in self.transitions:
            if transition.from_state != current_state:
                continue
            
            # Check if transition is valid for user role
            if not self._is_transition_valid_for_role(transition, user_role):
                continue
            
            # Check condition if exists
            if transition.condition and not transition.condition(context, intent):
                continue
            
            # Check if intent matches transition trigger
            if not self._is_intent_matching(transition, intent, context):
                continue
            
            return transition
        
        return None
    
    def _is_transition_valid_for_role(self, transition: Transition, user_role: UserRole) -> bool:
        """Check if transition is valid for the user role"""
        # Some transitions are role-specific
        recruiter_only_states = [
            ConversationState.RECRUITER_FLOW,
            ConversationState.JOB_CREATION
        ]
        
        if transition.to_state in recruiter_only_states and user_role != UserRole.RECRUITER:
            return False
        
        return True
    
    def _is_intent_matching(self, transition: Transition, intent: str, context: Dict[str, Any]) -> bool:
        """Check if intent matches transition requirements"""
        # Define intent mappings for common transitions
        intent_mappings = {
            # Onboarding triggers
            "resume_upload": [ConversationState.AWAITING_RESUME],
            "profile_complete": [ConversationState.PROFILE_READY],
            "start_over": [ConversationState.ONBOARDING],
            "help": [ConversationState.ONBOARDING, ConversationState.AWAITING_RESUME, 
                    ConversationState.PROFILE_READY, ConversationState.RECRUITER_FLOW,
                    ConversationState.JOB_CREATION, ConversationState.MATCHING,
                    ConversationState.APPLICATION],
            
            # Recruiter triggers
            "create_job": [ConversationState.JOB_CREATION],
            "find_candidates": [ConversationState.MATCHING],
            "recruiter_dashboard": [ConversationState.RECRUITER_FLOW],
            
            # Candidate triggers
            "find_jobs": [ConversationState.MATCHING],
            "apply_job": [ConversationState.APPLICATION],
            "view_profile": [ConversationState.PROFILE_READY],
        }
        
        target_states = intent_mappings.get(intent, [])
        return transition.to_state in target_states
    
    async def _validate_transition(
        self,
        transition: Transition,
        session: Session,
        context: Dict[str, Any],
        user_message: Optional[str]
    ) -> Dict[str, Any]:
        """Validate transition requirements"""
        validation_result = {
            "valid": True,
            "error": None,
            "context_updates": {}
        }
        
        # Check validation rules
        for rule in transition.validation_rules:
            if rule == "user_authenticated":
                if not session.user_id:
                    validation_result["valid"] = False
                    validation_result["error"] = "User must be authenticated"
                    return validation_result
            
            elif rule == "resume_received":
                if not context.get("resume_received"):
                    validation_result["valid"] = False
                    validation_result["error"] = "Resume must be uploaded"
                    return validation_result
            
            elif rule == "profile_extracted":
                if not context.get("profile_extracted"):
                    validation_result["valid"] = False
                    validation_result["error"] = "Profile must be extracted from resume"
                    return validation_result
        
        return validation_result
    
    async def _execute_state_handler(
        self,
        state: ConversationState,
        session: Session,
        context: Dict[str, Any],
        user_message: Optional[str]
    ) -> Dict[str, Any]:
        """Execute state-specific handler"""
        handler = self.state_handlers.get(state)
        if handler:
            try:
                return await handler(session, context, user_message)
            except Exception as e:
                logger.error(f"Error executing state handler for {state}: {e}")
                return {"message": "Error in state handler", "context_updates": {}}
        
        return {"message": f"State: {state.value}", "context_updates": {}}
    
    # State condition methods
    def _is_resume_required(self, context: Dict[str, Any], intent: str) -> bool:
        """Check if resume is required"""
        return intent == "resume_upload" or not context.get("profile_extracted")
    
    def _is_profile_complete(self, context: Dict[str, Any], intent: str) -> bool:
        """Check if profile is complete"""
        return context.get("profile_extracted", False) and intent != "resume_upload"
    
    def _is_resume_processed(self, context: Dict[str, Any], intent: str) -> bool:
        """Check if resume is processed"""
        return context.get("profile_extracted", False)
    
    def _has_job_match(self, context: Dict[str, Any], intent: str) -> bool:
        """Check if there are job matches"""
        return intent == "apply_job" and context.get("job_selected")
    
    def _wants_matching(self, context: Dict[str, Any], intent: str) -> bool:
        """Check if user wants job matching"""
        return intent == "find_jobs"
    
    def _user_idle(self, context: Dict[str, Any], intent: str) -> bool:
        """Check if user is idle"""
        return intent == "idle"
    
    def _application_complete(self, context: Dict[str, Any], intent: str) -> bool:
        """Check if application is complete"""
        return context.get("application_submitted", False)
    
    def _is_recruiter_authenticated(self, context: Dict[str, Any], intent: str) -> bool:
        """Check if recruiter is authenticated"""
        return context.get("user_role") == "recruiter"
    
    def _wants_create_job(self, context: Dict[str, Any], intent: str) -> bool:
        """Check if recruiter wants to create job"""
        return intent == "create_job"
    
    def _wants_candidate_matching(self, context: Dict[str, Any], intent: str) -> bool:
        """Check if recruiter wants candidate matching"""
        return intent == "find_candidates"
    
    def _recruiter_idle(self, context: Dict[str, Any], intent: str) -> bool:
        """Check if recruiter is idle"""
        return intent == "idle"
    
    def _wants_restart(self, context: Dict[str, Any], intent: str) -> bool:
        """Check if user wants to restart"""
        return intent == "start_over"
    
    def _requests_help(self, context: Dict[str, Any], intent: str) -> bool:
        """Check if user requests help"""
        return intent == "help"
    
    # State handler methods
    async def _handle_onboarding(
        self,
        session: Session,
        context: Dict[str, Any],
        user_message: Optional[str]
    ) -> Dict[str, Any]:
        """Handle onboarding state"""
        return {
            "message": "Welcome! Please upload your resume or let me know how I can help.",
            "context_updates": {"onboarding_step": "started"}
        }
    
    async def _handle_awaiting_resume(
        self,
        session: Session,
        context: Dict[str, Any],
        user_message: Optional[str]
    ) -> Dict[str, Any]:
        """Handle resume upload state"""
        return {
            "message": "Please upload your resume (PDF/DOCX) so I can extract your profile information.",
            "context_updates": {"awaiting_resume": True}
        }
    
    async def _handle_profile_ready(
        self,
        session: Session,
        context: Dict[str, Any],
        user_message: Optional[str]
    ) -> Dict[str, Any]:
        """Handle profile ready state"""
        return {
            "message": "Great! Your profile is ready. You can now search for jobs or I can help you find matches.",
            "context_updates": {"profile_ready": True}
        }
    
    async def _handle_recruiter_flow(
        self,
        session: Session,
        context: Dict[str, Any],
        user_message: Optional[str]
    ) -> Dict[str, Any]:
        """Handle recruiter main flow"""
        return {
            "message": "Welcome Recruiter! What would you like to do? Create a job post or find candidates?",
            "context_updates": {"recruiter_mode": True}
        }
    
    async def _handle_job_creation(
        self,
        session: Session,
        context: Dict[str, Any],
        user_message: Optional[str]
    ) -> Dict[str, Any]:
        """Handle job creation state"""
        return {
            "message": "Let's create a job post. Please provide the job title.",
            "context_updates": {"creating_job": True}
        }
    
    async def _handle_matching(
        self,
        session: Session,
        context: Dict[str, Any],
        user_message: Optional[str]
    ) -> Dict[str, Any]:
        """Handle candidate/job matching state"""
        return {
            "message": "Searching for matches based on your profile...",
            "context_updates": {"matching_in_progress": True}
        }
    
    async def _handle_application(
        self,
        session: Session,
        context: Dict[str, Any],
        user_message: Optional[str]
    ) -> Dict[str, Any]:
        """Handle job application state"""
        return {
            "message": "Preparing your application. Please review the details.",
            "context_updates": {"application_in_progress": True}
        }
    
    async def _handle_idle(
        self,
        session: Session,
        context: Dict[str, Any],
        user_message: Optional[str]
    ) -> Dict[str, Any]:
        """Handle idle state"""
        return {
            "message": "I'm here to help! What would you like to do?",
            "context_updates": {"idle": True}
        }
    
    async def get_state_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get state transition history for a session.
        
        Args:
            session_id: Session identifier
            limit: Number of transitions to return
            
        Returns:
            List[Dict[str, Any]]: State transition history
        """
        # This would typically query a state transition log table
        # For now, return empty list
        return []
    
    async def reset_session_state(
        self,
        session_id: str,
        target_state: ConversationState = ConversationState.ONBOARDING
    ) -> bool:
        """
        Reset session to a specific state.
        
        Args:
            session_id: Session identifier
            target_state: Target state
            
        Returns:
            bool: True if reset successful
        """
        try:
            session = await self.session_service.get_session(session_id)
            if not session:
                return False
            
            # Clear state-specific context
            context = session.context or {}
            state_keys = [
                "onboarding_step", "awaiting_resume", "profile_ready",
                "recruiter_mode", "creating_job", "matching_in_progress",
                "application_in_progress", "idle"
            ]
            
            for key in state_keys:
                context.pop(key, None)
            
            # Update session
            await self.session_service.update_session_context(session_id, context)
            await self.session_service.update_session_state(session_id, target_state)
            
            logger.info(f"Reset session {session_id} to state {target_state.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting session state: {e}")
            return False