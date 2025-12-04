"""
LLM Service for Chatbot/Co-Pilot Module

Provides a thin wrapper around Brain / LLM providers for generating
AI responses, extracting intent, and handling chat completions.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Union

from ...brain_module.brain_service import BrainService
from ...brain_module.providers.provider_factory import create_provider_from_env
from datetime import timedelta

logger = logging.getLogger(__name__)


class LLMService:
    """
    LLM Service for AI-powered chatbot responses.
    
    This service is responsible for:
    - Generating contextual replies based on conversation history
    - Extracting user intent from messages
    - Handling chat completions with context
    - Managing different LLM providers
    - Caching responses for performance
    """
    
    def __init__(self, provider_name: str = "openrouter", model_name: str = "gpt-3.5-turbo"):
        """
        Initialize LLM Service.
        
        Args:
            provider_name: Name of LLM provider
            model_name: Name of model to use
        """
        self.provider_name = provider_name
        self.model_name = model_name
        self.brain_service = BrainService()
        self.provider = create_provider_from_env(0)  # Use slot 0 for default provider
        self.response_cache = {}
        self.cache_ttl = 300  # 5 minutes cache
        
        # Initialize conversation templates
        self.conversation_templates = {
            'greeting': [
                "Hello! How can I help you today?",
                "Hi there! What can I do for you?",
                "Welcome! I'm here to assist you."
            ],
            'help': [
                "I can help you with job searching, resume management, and career guidance.",
                "Here's what I can do:\n• Find jobs that match your profile\n• Help you create a great resume\n• Guide you through the application process\n• Provide career advice",
                "I'm your AI career assistant! I can help with job matching, resume building, and career planning."
            ],
            'goodbye': [
                "Goodbye! Feel free to come back anytime if you need help.",
                "Take care! I'll be here whenever you need assistance.",
                "Have a great day! Reach out anytime for career help."
            ],
            'error': [
                "I apologize, but I encountered an error. Please try again.",
                "Something went wrong. Let me try that again for you.",
                "I'm having trouble processing your request. Please try once more."
            ]
        }
    
    def generate_reply(self, context: Dict[str, Any], message: str = None) -> str:
        """
        Generate contextual reply based on conversation context.
        
        Args:
            context: Conversation context
            message: Optional user message for context
            
        Returns:
            str: Generated reply
        """
        try:
            # Check cache first
            cache_key = self._generate_cache_key(context, message)
            cached_response = self._get_from_cache(cache_key)
            if cached_response:
                return cached_response
            
            # Prepare prompt
            prompt = self._prepare_contextual_prompt(context, message)
            
            # Generate response
            response = self.brain_service.generate_response(
                prompt=prompt,
                provider=self.provider_name,
                model=self.model_name
            )
            
            # Cache response
            self._cache_response(cache_key, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating reply: {e}")
            return self._get_fallback_response('error')
    
    def extract_intent(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Extract user intent from text.
        
        Args:
            text: User text to analyze
            context: Additional context
            
        Returns:
            Dict[str, Any]: Intent analysis result
        """
        try:
            # Prepare intent extraction prompt
            prompt = self._prepare_intent_prompt(text, context)
            
            # Extract intent
            intent_response = self.brain_service.generate_response(
                prompt=prompt,
                provider=self.provider_name,
                model=self.model_name
            )
            
            # Parse intent response
            intent = self._parse_intent_response(intent_response, text)
            
            return intent
            
        except Exception as e:
            logger.error(f"Error extracting intent: {e}")
            return {
                'intent': 'unknown',
                'confidence': 0.0,
                'entities': [],
                'text': text
            }
    
    def chat_completion(self, history: List[Dict[str, str]], 
                       system_prompt: str = None) -> str:
        """
        Generate chat completion based on conversation history.
        
        Args:
            history: Conversation history
            system_prompt: Optional system prompt
            
        Returns:
            str: Chat completion response
        """
        try:
            # Check cache first
            cache_key = self._generate_chat_cache_key(history, system_prompt)
            cached_response = self._get_from_cache(cache_key)
            if cached_response:
                return cached_response
            
            # Prepare chat completion
            response = self.brain_service.chat_completion(
                history=history,
                system_prompt=system_prompt,
                provider=self.provider_name,
                model=self.model_name
            )
            
            # Cache response
            self._cache_response(cache_key, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            return self._get_fallback_response('error')
    
    def summarize_conversation(self, history: List[Dict[str, str]]) -> str:
        """
        Summarize conversation history.
        
        Args:
            history: Conversation history
            
        Returns:
            str: Conversation summary
        """
        try:
            # Prepare summary prompt
            prompt = self._prepare_summary_prompt(history)
            
            # Generate summary
            summary = self.brain_service.generate_response(
                prompt=prompt,
                provider=self.provider_name,
                model=self.model_name
            )
            
            return summary
            
        except Exception as e:
            logger.error(f"Error summarizing conversation: {e}")
            return "Unable to generate summary at this time."
    
    def generate_job_description(self, title: str, company: str, 
                               requirements: Dict[str, Any]) -> str:
        """
        Generate job description.
        
        Args:
            title: Job title
            company: Company name
            requirements: Job requirements
            
        Returns:
            str: Generated job description
        """
        try:
            # Prepare job description prompt
            prompt = self._prepare_job_description_prompt(title, company, requirements)
            
            # Generate job description
            job_description = self.brain_service.generate_response(
                prompt=prompt,
                provider=self.provider_name,
                model=self.model_name
            )
            
            return job_description
            
        except Exception as e:
            logger.error(f"Error generating job description: {e}")
            return f"**{title}** at {company}\n\nWe are looking for a qualified professional to join our team."
    
    def generate_resume_summary(self, resume_data: Dict[str, Any]) -> str:
        """
        Generate resume summary.
        
        Args:
            resume_data: Resume data
            
        Returns:
            str: Generated resume summary
        """
        try:
            # Prepare resume summary prompt
            prompt = self._prepare_resume_summary_prompt(resume_data)
            
            # Generate summary
            summary = self.brain_service.generate_response(
                prompt=prompt,
                provider=self.provider_name,
                model=self.model_name
            )
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating resume summary: {e}")
            return "Unable to generate resume summary at this time."
    
    def generate_interview_questions(self, job_title: str, 
                                   experience_level: str) -> List[str]:
        """
        Generate interview questions.
        
        Args:
            job_title: Job title
            experience_level: Experience level
            
        Returns:
            List[str]: List of interview questions
        """
        try:
            # Prepare interview questions prompt
            prompt = self._prepare_interview_questions_prompt(job_title, experience_level)
            
            # Generate questions
            questions_response = self.brain_service.generate_response(
                prompt=prompt,
                provider=self.provider_name,
                model=self.model_name
            )
            
            # Parse questions
            questions = self._parse_interview_questions(questions_response)
            
            return questions
            
        except Exception as e:
            logger.error(f"Error generating interview questions: {e}")
            return [
                "Tell me about yourself.",
                "Why are you interested in this position?",
                "What are your strengths and weaknesses?"
            ]
    
    def _prepare_contextual_prompt(self, context: Dict[str, Any], 
                                 message: str = None) -> str:
        """
        Prepare contextual prompt for reply generation.
        
        Args:
            context: Conversation context
            message: Optional user message
            
        Returns:
            str: Prepared prompt
        """
        # Build context string
        context_parts = []
        
        # Add user role
        user_role = context.get('user_role', 'unknown')
        context_parts.append(f"User Role: {user_role}")
        
        # Add conversation state
        session_state = context.get('session_state', 'unknown')
        context_parts.append(f"Conversation State: {session_state}")
        
        # Add channel
        channel = context.get('channel', 'unknown')
        context_parts.append(f"Channel: {channel}")
        
        # Add recent conversation history
        if 'history' in context:
            context_parts.append("Recent Conversation:")
            for entry in context['history'][-3:]:  # Last 3 entries
                context_parts.append(f"  {entry.get('sender', 'Unknown')}: {entry.get('content', '')}")
        
        # Add current message
        if message:
            context_parts.append(f"Current Message: {message}")
        
        # Add context data
        if 'session_context' in context:
            context_parts.append("Context Data:")
            for key, value in context['session_context'].items():
                context_parts.append(f"  {key}: {value}")
        
        # Build final prompt
        prompt = f"""
You are an AI career assistant for a recruitment platform. Your role is to help users with job searching, career guidance, and recruitment processes.

Context:
{chr(10).join(context_parts)}

Please provide a helpful, professional, and engaging response that:
1. Acknowledges the user's message
2. Provides relevant information based on their role and context
3. Guides them toward their goals
4. Maintains a friendly and professional tone

Response:
"""
        
        return prompt
    
    def _prepare_intent_prompt(self, text: str, context: Dict[str, Any] = None) -> str:
        """
        Prepare intent extraction prompt.
        
        Args:
            text: User text
            context: Additional context
            
        Returns:
            str: Prepared prompt
        """
        prompt = f"""
Analyze the following user message and extract the intent and entities.

Message: "{text}"

Context: {context or 'None'}

Please respond with a JSON object containing:
- intent: The primary intent (e.g., 'greeting', 'help', 'job_search', 'resume_upload', 'goodbye', 'unknown')
- confidence: Confidence score (0.0 to 1.0)
- entities: List of extracted entities (e.g., ['job_title', 'location', 'experience_level'])

Example response:
{{
  "intent": "job_search",
  "confidence": 0.9,
  "entities": ["software_engineer", "remote", "senior"]
}}
"""
        
        return prompt
    
    def _prepare_summary_prompt(self, history: List[Dict[str, str]]) -> str:
        """
        Prepare conversation summary prompt.
        
        Args:
            history: Conversation history
            
        Returns:
            str: Prepared prompt
        """
        # Format history
        history_text = ""
        for entry in history:
            sender = entry.get('sender', 'Unknown')
            content = entry.get('content', '')
            history_text += f"{sender}: {content}\n"
        
        prompt = f"""
Summarize the following conversation in 2-3 sentences:

{history_text}

Summary:
"""
        
        return prompt
    
    def _prepare_job_description_prompt(self, title: str, company: str, 
                                      requirements: Dict[str, Any]) -> str:
        """
        Prepare job description generation prompt.
        
        Args:
            title: Job title
            company: Company name
            requirements: Job requirements
            
        Returns:
            str: Prepared prompt
        """
        prompt = f"""
Generate a professional job description for a {title} position at {company}.

Requirements:
{chr(10).join(f"- {key}: {value}" for key, value in requirements.items())}

Please include:
1. Job summary
2. Key responsibilities
3. Required qualifications
4. Preferred qualifications (if any)
5. What we offer

Job Description:
"""
        
        return prompt
    
    def _prepare_resume_summary_prompt(self, resume_data: Dict[str, Any]) -> str:
        """
        Prepare resume summary generation prompt.
        
        Args:
            resume_data: Resume data
            
        Returns:
            str: Prepared prompt
        """
        prompt = f"""
Generate a professional resume summary based on the following information:

{chr(10).join(f"{key}: {value}" for key, value in resume_data.items())}

Please create a compelling 2-3 sentence summary that highlights:
1. Key skills and experience
2. Career achievements
3. Professional strengths

Summary:
"""
        
        return prompt
    
    def _prepare_interview_questions_prompt(self, job_title: str, 
                                         experience_level: str) -> str:
        """
        Prepare interview questions generation prompt.
        
        Args:
            job_title: Job title
            experience_level: Experience level
            
        Returns:
            str: Prepared prompt
        """
        prompt = f"""
Generate 5 relevant interview questions for a {job_title} position with {experience_level} experience level.

Questions should cover:
1. Technical skills and knowledge
2. Problem-solving abilities
3. Team collaboration
4. Industry-specific knowledge
5. Career goals and motivation

Please provide the questions as a numbered list:
"""
        
        return prompt
    
    def _parse_intent_response(self, response: str, original_text: str) -> Dict[str, Any]:
        """
        Parse intent extraction response.
        
        Args:
            response: LLM response
            original_text: Original user text
            
        Returns:
            Dict[str, Any]: Parsed intent
        """
        try:
            # Try to parse JSON response
            import json
            intent_data = json.loads(response)
            
            return {
                'intent': intent_data.get('intent', 'unknown'),
                'confidence': float(intent_data.get('confidence', 0.0)),
                'entities': intent_data.get('entities', []),
                'text': original_text
            }
            
        except (json.JSONDecodeError, ValueError):
            # Fallback to simple intent detection
            return self._simple_intent_detection(original_text)
    
    def _parse_interview_questions(self, response: str) -> List[str]:
        """
        Parse interview questions from response.
        
        Args:
            response: LLM response
            
        Returns:
            List[str]: List of questions
        """
        try:
            # Split by numbered questions
            questions = []
            lines = response.split('\n')
            current_question = ""
            
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith(('Q', 'Question'))):
                    if current_question:
                        questions.append(current_question)
                    current_question = line
                elif line:
                    current_question += " " + line
            
            if current_question:
                questions.append(current_question)
            
            return questions[:5]  # Return max 5 questions
            
        except Exception as e:
            logger.error(f"Error parsing interview questions: {e}")
            return []
    
    def _simple_intent_detection(self, text: str) -> Dict[str, Any]:
        """
        Simple intent detection as fallback.
        
        Args:
            text: User text
            
        Returns:
            Dict[str, Any]: Detected intent
        """
        text_lower = text.lower()
        
        # Greeting patterns
        if any(word in text_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
            return {'intent': 'greeting', 'confidence': 0.8, 'entities': [], 'text': text}
        
        # Help patterns
        if any(word in text_lower for word in ['help', 'assist', 'guide', 'how to']):
            return {'intent': 'help', 'confidence': 0.8, 'entities': [], 'text': text}
        
        # Goodbye patterns
        if any(word in text_lower for word in ['bye', 'goodbye', 'see you', 'later']):
            return {'intent': 'goodbye', 'confidence': 0.8, 'entities': [], 'text': text}
        
        # Job search patterns
        if any(word in text_lower for word in ['job', 'work', 'position', 'career', 'employment']):
            return {'intent': 'job_search', 'confidence': 0.7, 'entities': [], 'text': text}
        
        # Resume patterns
        if any(word in text_lower for word in ['resume', 'cv', 'curriculum', 'profile']):
            return {'intent': 'resume_upload', 'confidence': 0.7, 'entities': [], 'text': text}
        
        # Default
        return {'intent': 'unknown', 'confidence': 0.1, 'entities': [], 'text': text}
    
    def _generate_cache_key(self, context: Dict[str, Any], message: str = None) -> str:
        """
        Generate cache key for response.
        
        Args:
            context: Context dictionary
            message: Optional message
            
        Returns:
            str: Cache key
        """
        import hashlib
        
        # Create hashable string
        context_str = str(sorted(context.items()))
        message_str = str(message) if message else ""
        
        hash_input = f"{context_str}{message_str}"
        return hashlib.md5(hash_input.encode()).hexdigest()
    
    def _generate_chat_cache_key(self, history: List[Dict[str, str]], 
                               system_prompt: str = None) -> str:
        """
        Generate cache key for chat completion.
        
        Args:
            history: Conversation history
            system_prompt: System prompt
            
        Returns:
            str: Cache key
        """
        import hashlib
        
        # Create hashable string
        history_str = str(sorted(history))
        prompt_str = str(system_prompt) if system_prompt else ""
        
        hash_input = f"{history_str}{prompt_str}"
        return hashlib.md5(hash_input.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[str]:
        """
        Get response from cache.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Optional[str]: Cached response or None
        """
        if cache_key in self.response_cache:
            cached_data = self.response_cache[cache_key]
            if datetime.utcnow() - cached_data['timestamp'] < timedelta(seconds=self.cache_ttl):
                return cached_data['response']
            else:
                # Remove expired cache
                del self.response_cache[cache_key]
        
        return None
    
    def _cache_response(self, cache_key: str, response: str) -> None:
        """
        Cache response.
        
        Args:
            cache_key: Cache key
            response: Response to cache
        """
        self.response_cache[cache_key] = {
            'response': response,
            'timestamp': datetime.utcnow()
        }
        
        # Clean old cache entries
        self._clean_cache()
    
    def _clean_cache(self) -> None:
        """
        Clean expired cache entries.
        """
        current_time = datetime.utcnow()
        expired_keys = []
        
        for key, cached_data in self.response_cache.items():
            if current_time - cached_data['timestamp'] > timedelta(seconds=self.cache_ttl):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.response_cache[key]
    
    def _get_fallback_response(self, intent: str) -> str:
        """
        Get fallback response for intent.
        
        Args:
            intent: Intent type
            
        Returns:
            str: Fallback response
        """
        return self.conversation_templates.get(intent, [self.conversation_templates['error'][0]])[0]
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dict[str, Any]: Cache statistics
        """
        return {
            'cache_size': len(self.response_cache),
            'cache_ttl': self.cache_ttl,
            'provider': self.provider_name,
            'model': self.model_name
        }
    
    def clear_cache(self) -> None:
        """
        Clear response cache.
        """
        self.response_cache.clear()
        logger.info("LLM response cache cleared")
    
    def update_cache_ttl(self, ttl: int) -> None:
        """
        Update cache TTL.
        
        Args:
            ttl: New TTL in seconds
        """
        self.cache_ttl = ttl
        logger.info(f"LLM cache TTL updated to {ttl} seconds")
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get provider information.
        
        Returns:
            Dict[str, Any]: Provider information
        """
        return {
            'provider': self.provider_name,
            'model': self.model_name,
            'available': self.provider is not None,
            'cache_stats': self.get_cache_stats()
        }