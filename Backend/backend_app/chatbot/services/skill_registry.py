"""
Skill Registry for Chatbot/Co-Pilot Module

Manages registration and retrieval of AI skills for the chatbot system.
Skills are registered in priority order and selected based on their ability
to handle the current conversation state and user message.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..models.conversation_state import ConversationState
from ..utils.skill_context import SkillContext

logger = logging.getLogger(__name__)


class SkillRegistry:
    """
    Skill Registry for managing AI skills.
    
    This registry is responsible for:
    - Registering skills with priority ordering
    - Selecting appropriate skills for messages
    - Managing skill execution context
    - Providing skill metadata and information
    """
    
    def __init__(self):
        """
        Initialize Skill Registry.
        """
        self.skills = []
        self.skill_metadata = {}
        self.execution_stats = {}
    
    def register(self, skill, priority: int = 10) -> None:
        """
        Register a skill with the registry.
        
        Args:
            skill: Skill instance
            priority: Skill priority (higher = more important)
        """
        try:
            # Create skill entry with priority
            skill_entry = {
                'skill': skill,
                'priority': priority,
                'name': skill.name,
                'description': skill.description,
                'class': skill.__class__.__name__,
                'registered_at': datetime.utcnow()
            }
            
            # Insert skill in priority order (higher priority first)
            inserted = False
            for i, existing_entry in enumerate(self.skills):
                if priority > existing_entry['priority']:
                    self.skills.insert(i, skill_entry)
                    inserted = True
                    break
            
            if not inserted:
                self.skills.append(skill_entry)
            
            # Store metadata
            self.skill_metadata[skill.name] = skill.get_skill_info()
            
            # Initialize execution stats
            self.execution_stats[skill.name] = {
                'executions': 0,
                'successful_executions': 0,
                'failed_executions': 0,
                'average_execution_time': 0.0,
                'last_execution': None,
                'total_execution_time': 0.0
            }
            
            logger.info(f"Registered skill: {skill.name} with priority {priority}")
            
        except Exception as e:
            logger.error(f"Error registering skill {skill.name}: {e}")
            raise
    
    def unregister(self, skill_name: str) -> bool:
        """
        Unregister a skill from the registry.
        
        Args:
            skill_name: Name of skill to unregister
            
        Returns:
            bool: True if skill was unregistered, False if not found
        """
        try:
            for i, skill_entry in enumerate(self.skills):
                if skill_entry['name'] == skill_name:
                    del self.skills[i]
                    if skill_name in self.skill_metadata:
                        del self.skill_metadata[skill_name]
                    if skill_name in self.execution_stats:
                        del self.execution_stats[skill_name]
                    logger.info(f"Unregistered skill: {skill_name}")
                    return True
            return False
        except Exception as e:
            logger.error(f"Error unregistering skill {skill_name}: {e}")
            return False
    
    def get_all(self) -> List[Any]:
        """
        Get all registered skills in priority order.
        
        Returns:
            List[Any]: List of skill instances
        """
        return [entry['skill'] for entry in self.skills]
    
    def get_by_name(self, skill_name: str) -> Optional[Any]:
        """
        Get skill by name.
        
        Args:
            skill_name: Name of skill to retrieve
            
        Returns:
            Optional[Any]: Skill instance or None
        """
        for entry in self.skills:
            if entry['name'] == skill_name:
                return entry['skill']
        return None
    
    def get_by_priority(self, min_priority: int = 0, max_priority: int = 100) -> List[Any]:
        """
        Get skills by priority range.
        
        Args:
            min_priority: Minimum priority
            max_priority: Maximum priority
            
        Returns:
            List[Any]: List of skill instances
        """
        return [
            entry['skill'] for entry in self.skills
            if min_priority <= entry['priority'] <= max_priority
        ]
    
    def get_skills_for_state(self, state: ConversationState) -> List[Any]:
        """
        Get skills that can handle a specific state.
        
        Args:
            state: Conversation state
            
        Returns:
            List[Any]: List of skill instances
        """
        return [
            entry['skill'] for entry in self.skills
            if entry['skill'].can_handle(state, "")
        ]
    
    def select_skill(self, state: ConversationState, message: str, 
                    context: Dict[str, Any] = None) -> Optional[Any]:
        """
        Select the most appropriate skill for the current state and message.
        
        Args:
            state: Current conversation state
            message: User message
            context: Additional context
            
        Returns:
            Optional[Any]: Selected skill or None
        """
        try:
            # Get skills that can handle this state
            candidate_skills = []
            
            for entry in self.skills:
                skill = entry['skill']
                if skill.can_handle(state, message, context):
                    candidate_skills.append((skill, entry['priority']))
            
            if not candidate_skills:
                logger.warning(f"No skills found for state {state} and message: {message}")
                return None
            
            # Sort by priority (highest first)
            candidate_skills.sort(key=lambda x: x[1], reverse=True)
            
            # Return highest priority skill
            selected_skill = candidate_skills[0][0]
            logger.info(f"Selected skill: {selected_skill.name} for state {state}")
            
            return selected_skill
            
        except Exception as e:
            logger.error(f"Error selecting skill: {e}")
            return None
    
    def get_skill_info(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """
        Get skill information.
        
        Args:
            skill_name: Name of skill
            
        Returns:
            Optional[Dict[str, Any]]: Skill information or None
        """
        return self.skill_metadata.get(skill_name)
    
    def get_all_skill_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information for all registered skills.
        
        Returns:
            Dict[str, Dict[str, Any]]: All skill information
        """
        return self.skill_metadata.copy()
    
    def get_execution_stats(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """
        Get execution statistics for a skill.
        
        Args:
            skill_name: Name of skill
            
        Returns:
            Optional[Dict[str, Any]]: Execution statistics or None
        """
        return self.execution_stats.get(skill_name)
    
    def get_all_execution_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get execution statistics for all skills.
        
        Returns:
            Dict[str, Dict[str, Any]]: All execution statistics
        """
        return self.execution_stats.copy()
    
    def update_execution_stats(self, skill_name: str, success: bool, 
                             execution_time: float) -> None:
        """
        Update execution statistics for a skill.
        
        Args:
            skill_name: Name of skill
            success: Whether execution was successful
            execution_time: Execution time in seconds
        """
        try:
            if skill_name not in self.execution_stats:
                self.execution_stats[skill_name] = {
                    'executions': 0,
                    'successful_executions': 0,
                    'failed_executions': 0,
                    'average_execution_time': 0.0,
                    'last_execution': None,
                    'total_execution_time': 0.0
                }
            
            stats = self.execution_stats[skill_name]
            stats['executions'] += 1
            stats['total_execution_time'] += execution_time
            
            if success:
                stats['successful_executions'] += 1
            else:
                stats['failed_executions'] += 1
            
            stats['average_execution_time'] = stats['total_execution_time'] / stats['executions']
            stats['last_execution'] = {
                'timestamp': datetime.utcnow().isoformat(),
                'success': success,
                'execution_time': execution_time
            }
            
        except Exception as e:
            logger.error(f"Error updating execution stats for {skill_name}: {e}")
    
    def get_skill_capabilities(self) -> Dict[str, List[str]]:
        """
        Get capabilities of all registered skills.
        
        Returns:
            Dict[str, List[str]]: Skill capabilities
        """
        capabilities = {}
        
        for entry in self.skills:
            skill = entry['skill']
            skill_info = self.skill_metadata[skill.name]
            
            capabilities[skill.name] = {
                'can_handle_states': skill_info.get('can_handle_states', []),
                'required_context': skill_info.get('required_context', []),
                'priority': entry['priority'],
                'description': skill_info.get('description', '')
            }
        
        return capabilities
    
    def validate_skill_context(self, skill_name: str, context: Dict[str, Any]) -> bool:
        """
        Validate that required context is available for a skill.
        
        Args:
            skill_name: Name of skill
            context: Context to validate
            
        Returns:
            bool: True if context is valid, False otherwise
        """
        try:
            skill = self.get_by_name(skill_name)
            if skill:
                return skill.validate_context(context)
            return False
        except Exception as e:
            logger.error(f"Error validating context for skill {skill_name}: {e}")
            return False
    
    def get_skill_dependencies(self) -> Dict[str, List[str]]:
        """
        Get skill dependencies (which skills depend on others).
        
        Returns:
            Dict[str, List[str]]: Skill dependencies
        """
        # This would be implemented if skills had dependencies
        # For now, return empty dict
        return {}
    
    def reorder_skills(self, skill_name: str, new_priority: int) -> bool:
        """
        Reorder a skill by changing its priority.
        
        Args:
            skill_name: Name of skill to reorder
            new_priority: New priority value
            
        Returns:
            bool: True if reordered successfully
        """
        try:
            # Remove skill from current position
            skill_entry = None
            for i, entry in enumerate(self.skills):
                if entry['name'] == skill_name:
                    skill_entry = self.skills.pop(i)
                    break
            
            if not skill_entry:
                return False
            
            # Update priority
            skill_entry['priority'] = new_priority
            
            # Reinsert in correct position
            inserted = False
            for i, existing_entry in enumerate(self.skills):
                if new_priority > existing_entry['priority']:
                    self.skills.insert(i, skill_entry)
                    inserted = True
                    break
            
            if not inserted:
                self.skills.append(skill_entry)
            
            logger.info(f"Reordered skill {skill_name} to priority {new_priority}")
            return True
            
        except Exception as e:
            logger.error(f"Error reordering skill {skill_name}: {e}")
            return False
    
    def get_skill_execution_history(self, skill_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get execution history for a skill.
        
        Args:
            skill_name: Name of skill
            limit: Maximum number of entries to return
            
        Returns:
            List[Dict[str, Any]]: Execution history
        """
        try:
            # This would typically query a database or log storage
            # For now, return empty list
            return []
        except Exception as e:
            logger.error(f"Error getting execution history for {skill_name}: {e}")
            return []
    
    def export_registry(self) -> Dict[str, Any]:
        """
        Export registry configuration.
        
        Returns:
            Dict[str, Any]: Exported registry data
        """
        return {
            'skills': [
                {
                    'name': entry['name'],
                    'priority': entry['priority'],
                    'description': entry['description'],
                    'class': entry['class'],
                    'registered_at': entry['registered_at'].isoformat()
                }
                for entry in self.skills
            ],
            'metadata': self.skill_metadata,
            'exported_at': datetime.utcnow().isoformat()
        }
    
    def import_registry(self, registry_data: Dict[str, Any]) -> bool:
        """
        Import registry configuration.
        
        Args:
            registry_data: Registry data to import
            
        Returns:
            bool: True if imported successfully
        """
        try:
            # Clear existing skills
            self.skills = []
            self.skill_metadata = {}
            self.execution_stats = {}
            
            # Import skills
            for skill_data in registry_data.get('skills', []):
                # This would need to reconstruct skill instances
                # For now, just log the import
                logger.info(f"Importing skill: {skill_data['name']}")
            
            logger.info("Registry imported successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error importing registry: {e}")
            return False
    
    def get_skill_performance_report(self) -> Dict[str, Any]:
        """
        Get performance report for all skills.
        
        Returns:
            Dict[str, Any]: Performance report
        """
        try:
            report = {
                'total_skills': len(self.skills),
                'total_executions': sum(stats['executions'] for stats in self.execution_stats.values()),
                'successful_executions': sum(stats['successful_executions'] for stats in self.execution_stats.values()),
                'failed_executions': sum(stats['failed_executions'] for stats in self.execution_stats.values()),
                'average_execution_time': sum(stats['average_execution_time'] for stats in self.execution_stats.values()) / len(self.execution_stats) if self.execution_stats else 0,
                'skills': []
            }
            
            for entry in self.skills:
                skill_name = entry['name']
                stats = self.execution_stats.get(skill_name, {})
                
                skill_report = {
                    'name': skill_name,
                    'priority': entry['priority'],
                    'executions': stats.get('executions', 0),
                    'successful_executions': stats.get('successful_executions', 0),
                    'failed_executions': stats.get('failed_executions', 0),
                    'success_rate': (stats.get('successful_executions', 0) / stats.get('executions', 1)) * 100,
                    'average_execution_time': stats.get('average_execution_time', 0),
                    'last_execution': stats.get('last_execution')
                }
                
                report['skills'].append(skill_report)
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
            return {}