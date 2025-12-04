"""
Skill Context for Chatbot/Co-Pilot Module

Provides context management for individual skills and skill execution tracking.
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import uuid
import json
import logging

logger = logging.getLogger(__name__)


class SkillContext:
    """
    Context data for individual skill execution.
    
    Tracks skill execution parameters, results, and metadata.
    """
    
    def __init__(self, skill_name: str, trigger_message: str, parameters: Dict[str, Any] = None):
        """
        Initialize skill context.
        
        Args:
            skill_name: Name of the skill being executed
            trigger_message: Message that triggered this skill
            parameters: Parameters for skill execution
        """
        self.skill_id = str(uuid.uuid4())
        self.skill_name = skill_name
        self.trigger_message = trigger_message
        self.parameters = parameters or {}
        self.execution_start = datetime.utcnow()
        self.execution_end = None
        self.result = None
        self.error = None
        self.metadata = {}
        self.intermediate_steps = []
        self.performance_metrics = {}
    
    def start_execution(self) -> None:
        """Mark the start of skill execution."""
        self.execution_start = datetime.utcnow()
        self.metadata['execution_started'] = True
    
    def end_execution(self, result: Any = None, error: str = None) -> None:
        """
        Mark the end of skill execution.
        
        Args:
            result: Execution result
            error: Error message if execution failed
        """
        self.execution_end = datetime.utcnow()
        self.result = result
        self.error = error
        
        if error:
            self.metadata['execution_failed'] = True
            self.metadata['error_message'] = error
        else:
            self.metadata['execution_success'] = True
    
    def add_intermediate_step(self, step_name: str, step_data: Dict[str, Any]) -> None:
        """
        Add an intermediate execution step.
        
        Args:
            step_name: Name of the step
            step_data: Step data
        """
        step = {
            'step_name': step_name,
            'timestamp': datetime.utcnow().isoformat(),
            'data': step_data
        }
        self.intermediate_steps.append(step)
    
    def set_performance_metric(self, metric_name: str, value: Union[int, float, str]) -> None:
        """
        Set a performance metric.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
        """
        self.performance_metrics[metric_name] = {
            'value': value,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def get_execution_time(self) -> Optional[float]:
        """
        Get execution time in seconds.
        
        Returns:
            Optional[float]: Execution time in seconds, or None if not completed
        """
        if not self.execution_start:
            return None
        
        end_time = self.execution_end or datetime.utcnow()
        return (end_time - self.execution_start).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert skill context to dictionary."""
        return {
            'skill_id': self.skill_id,
            'skill_name': self.skill_name,
            'trigger_message': self.trigger_message,
            'parameters': self.parameters,
            'execution_start': self.execution_start.isoformat() if self.execution_start else None,
            'execution_end': self.execution_end.isoformat() if self.execution_end else None,
            'execution_time': self.get_execution_time(),
            'result': self.result,
            'error': self.error,
            'metadata': self.metadata,
            'intermediate_steps': self.intermediate_steps,
            'performance_metrics': self.performance_metrics
        }
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the context."""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value."""
        return self.metadata.get(key, default)
    
    def is_successful(self) -> bool:
        """Check if skill execution was successful."""
        return self.error is None and self.metadata.get('execution_success', False)
    
    def has_error(self) -> bool:
        """Check if skill execution had an error."""
        return self.error is not None or self.metadata.get('execution_failed', False)


class SkillExecutionContextManager:
    """
    Manager for skill execution contexts.
    
    Handles creation, tracking, and cleanup of skill contexts.
    """
    
    def __init__(self):
        self.active_contexts = {}
        self.completed_contexts = []
        self.max_active_contexts = 100
        self.max_completed_contexts = 1000
    
    def create_context(self, skill_name: str, trigger_message: str, 
                      parameters: Dict[str, Any] = None) -> SkillContext:
        """
        Create a new skill context.
        
        Args:
            skill_name: Name of the skill
            trigger_message: Trigger message
            parameters: Skill parameters
            
        Returns:
            SkillContext: New skill context
        """
        # Clean up old contexts if needed
        self._cleanup_old_contexts()
        
        # Create new context
        context = SkillContext(skill_name, trigger_message, parameters)
        context.start_execution()
        
        # Store active context
        self.active_contexts[context.skill_id] = context
        
        return context
    
    def get_active_context(self, skill_id: str) -> Optional[SkillContext]:
        """
        Get an active skill context.
        
        Args:
            skill_id: Skill ID
            
        Returns:
            Optional[SkillContext]: Active context or None
        """
        return self.active_contexts.get(skill_id)
    
    def complete_context(self, skill_id: str, result: Any = None, error: str = None) -> bool:
        """
        Complete a skill context.
        
        Args:
            skill_id: Skill ID
            result: Execution result
            error: Error message if failed
            
        Returns:
            bool: True if successful, False if context not found
        """
        context = self.active_contexts.get(skill_id)
        if not context:
            return False
        
        # Complete the context
        context.end_execution(result, error)
        
        # Move to completed contexts
        self.completed_contexts.append(context)
        
        # Remove from active contexts
        del self.active_contexts[skill_id]
        
        # Clean up completed contexts if needed
        self._cleanup_completed_contexts()
        
        return True
    
    def get_context_history(self, skill_name: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get context execution history.
        
        Args:
            skill_name: Optional skill name filter
            limit: Maximum number of contexts to return
            
        Returns:
            List[Dict[str, Any]]: Context history
        """
        history = []
        
        # Filter by skill name if specified
        contexts = self.completed_contexts
        if skill_name:
            contexts = [ctx for ctx in contexts if ctx.skill_name == skill_name]
        
        # Get most recent contexts
        for context in contexts[-limit:]:
            history.append(context.to_dict())
        
        return history
    
    def get_active_contexts_count(self) -> int:
        """Get number of active contexts."""
        return len(self.active_contexts)
    
    def get_completed_contexts_count(self) -> int:
        """Get number of completed contexts."""
        return len(self.completed_contexts)
    
    def get_skill_execution_stats(self, skill_name: str) -> Dict[str, Any]:
        """
        Get execution statistics for a specific skill.
        
        Args:
            skill_name: Skill name
            
        Returns:
            Dict[str, Any]: Execution statistics
        """
        skill_contexts = [ctx for ctx in self.completed_contexts if ctx.skill_name == skill_name]
        
        if not skill_contexts:
            return {
                'skill_name': skill_name,
                'total_executions': 0,
                'successful_executions': 0,
                'failed_executions': 0,
                'average_execution_time': 0,
                'success_rate': 0
            }
        
        successful = sum(1 for ctx in skill_contexts if ctx.is_successful())
        failed = sum(1 for ctx in skill_contexts if ctx.has_error())
        
        execution_times = [ctx.get_execution_time() for ctx in skill_contexts if ctx.get_execution_time()]
        avg_time = sum(execution_times) / len(execution_times) if execution_times else 0
        
        return {
            'skill_name': skill_name,
            'total_executions': len(skill_contexts),
            'successful_executions': successful,
            'failed_executions': failed,
            'average_execution_time': avg_time,
            'success_rate': successful / len(skill_contexts) if skill_contexts else 0
        }
    
    def get_all_skills_stats(self) -> Dict[str, Any]:
        """
        Get execution statistics for all skills.
        
        Returns:
            Dict[str, Any]: All skills statistics
        """
        skills = set(ctx.skill_name for ctx in self.completed_contexts)
        stats = {}
        
        for skill in skills:
            stats[skill] = self.get_skill_execution_stats(skill)
        
        return stats
    
    def _cleanup_old_contexts(self) -> None:
        """Clean up old active contexts if limit exceeded."""
        if len(self.active_contexts) > self.max_active_contexts:
            # Remove oldest contexts
            sorted_contexts = sorted(
                self.active_contexts.values(),
                key=lambda x: x.execution_start or datetime.utcnow()
            )
            
            for context in sorted_contexts[:len(self.active_contexts) - self.max_active_contexts]:
                del self.active_contexts[context.skill_id]
    
    def _cleanup_completed_contexts(self) -> None:
        """Clean up old completed contexts if limit exceeded."""
        if len(self.completed_contexts) > self.max_completed_contexts:
            # Remove oldest contexts
            self.completed_contexts = self.completed_contexts[-self.max_completed_contexts:]
    
    def export_contexts(self, skill_name: str = None, format: str = 'json') -> str:
        """
        Export contexts to a specific format.
        
        Args:
            skill_name: Optional skill name filter
            format: Export format ('json', 'csv')
            
        Returns:
            str: Exported contexts
        """
        contexts = self.completed_contexts
        if skill_name:
            contexts = [ctx for ctx in contexts if ctx.skill_name == skill_name]
        
        if format == 'json':
            return json.dumps([ctx.to_dict() for ctx in contexts], indent=2)
        elif format == 'csv':
            # Simple CSV export
            lines = ['skill_id,skill_name,trigger_message,execution_time,success,error']
            for ctx in contexts:
                lines.append(f"{ctx.skill_id},{ctx.skill_name},{ctx.trigger_message},"
                           f"{ctx.get_execution_time() or 0},{ctx.is_successful()},{ctx.error or ''}")
            return '\n'.join(lines)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def import_contexts(self, data: str, format: str = 'json') -> bool:
        """
        Import contexts from a specific format.
        
        Args:
            data: Data to import
            format: Import format ('json', 'csv')
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if format == 'json':
                contexts_data = json.loads(data)
                for ctx_data in contexts_data:
                    context = SkillContext(
                        ctx_data['skill_name'],
                        ctx_data['trigger_message'],
                        ctx_data.get('parameters', {})
                    )
                    context.execution_start = datetime.fromisoformat(ctx_data['execution_start'])
                    context.execution_end = datetime.fromisoformat(ctx_data['execution_end']) if ctx_data.get('execution_end') else None
                    context.result = ctx_data.get('result')
                    context.error = ctx_data.get('error')
                    context.metadata = ctx_data.get('metadata', {})
                    context.intermediate_steps = ctx_data.get('intermediate_steps', [])
                    context.performance_metrics = ctx_data.get('performance_metrics', {})
                    
                    self.completed_contexts.append(context)
            
            elif format == 'csv':
                # Simple CSV import
                lines = data.strip().split('\n')
                for line in lines[1:]:  # Skip header
                    parts = line.split(',')
                    if len(parts) >= 6:
                        context = SkillContext(parts[1], parts[2])
                        context.execution_start = datetime.utcnow()  # Approximate
                        context.execution_end = datetime.utcnow()  # Approximate
                        context.result = "Imported"
                        context.error = parts[5] if parts[5] else None
                        
                        self.completed_contexts.append(context)
            
            return True
            
        except Exception as e:
            logger.error(f"Error importing contexts: {e}")
            return False
    
    def clear_contexts(self, skill_name: str = None) -> int:
        """
        Clear contexts.
        
        Args:
            skill_name: Optional skill name to clear, or None to clear all
            
        Returns:
            int: Number of contexts cleared
        """
        if skill_name:
            # Clear specific skill contexts
            cleared = len([ctx for ctx in self.completed_contexts if ctx.skill_name == skill_name])
            self.completed_contexts = [ctx for ctx in self.completed_contexts if ctx.skill_name != skill_name]
            return cleared
        else:
            # Clear all contexts
            cleared = len(self.completed_contexts) + len(self.active_contexts)
            self.completed_contexts = []
            self.active_contexts = {}
            return cleared
    
    def get_context_by_skill_name(self, skill_name: str, limit: int = 10) -> List[SkillContext]:
        """
        Get contexts by skill name.
        
        Args:
            skill_name: Skill name
            limit: Maximum number of contexts to return
            
        Returns:
            List[SkillContext]: Contexts for the skill
        """
        contexts = [ctx for ctx in self.completed_contexts if ctx.skill_name == skill_name]
        return contexts[-limit:]


# Global skill context manager instance
skill_context_manager = SkillExecutionContextManager()