"""
Message Engine for Chatbot/Co-Pilot Module

Handles conversation history persistence, transcript management, and message
tracking across different platforms (WhatsApp, Telegram, Web).
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Union
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.message_log_model import MessageLog, MessageType, MessageDirection
from ..repositories.message_repository import MessageRepository

logger = logging.getLogger(__name__)


class MessageEngine:
    """
    Message Engine for managing conversation history and transcripts.
    
    This engine provides:
    - Message persistence across platforms
    - Conversation transcript retrieval
    - Message validation and sanitization
    - Transcript export capabilities
    - Message analytics and statistics
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        Initialize Message Engine.
        
        Args:
            db_session: Database session
        """
        self.db_session = db_session
        self.repository = MessageRepository(db_session)
        self.max_message_length = 10000  # Maximum message length
        self.max_transcript_length = 100  # Maximum messages in transcript
    
    async def save_bot_message(
        self,
        session_id: str,
        message_id: Optional[str],
        content: str,
        platform: str,
        metadata: Optional[Dict[str, Any]] = None,
        response_time: Optional[int] = None,
        skill_used: Optional[str] = None
    ) -> Optional[MessageLog]:
        """
        Save a bot-generated message.
        
        Args:
            session_id: Session identifier
            message_id: Platform-specific message ID
            content: Message content
            platform: Platform (whatsapp/telegram/web)
            metadata: Additional message metadata
            response_time: Response time in milliseconds
            skill_used: Skill that generated this message
            
        Returns:
            Optional[MessageLog]: Saved message or None
        """
        try:
            # Sanitize content
            sanitized_content = self._sanitize_content(content)
            
            # Validate content
            if not self._validate_message_content(sanitized_content):
                logger.warning(f"Invalid message content for session {session_id}")
                return None
            
            # Create message log
            message = await self.repository.create(
                sid=session_id,
                message_id=message_id,
                message_type=MessageType.BOT,
                direction=MessageDirection.OUTBOUND,
                content=sanitized_content,
                platform=platform,
                metadata={
                    **(metadata or {}),
                    'response_time': response_time,
                    'skill_used': skill_used,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
            logger.debug(f"Saved bot message {message.id} for session {session_id}")
            return message
            
        except SQLAlchemyError as e:
            logger.error(f"Database error saving bot message: {e}")
            return None
        except Exception as e:
            logger.error(f"Error saving bot message: {e}")
            return None
    
    async def save_candidate_message(
        self,
        session_id: str,
        message_id: Optional[str],
        content: str,
        platform: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[MessageLog]:
        """
        Save a candidate/user message.
        
        Args:
            session_id: Session identifier
            message_id: Platform-specific message ID
            content: Message content
            platform: Platform (whatsapp/telegram/web)
            metadata: Additional message metadata
            
        Returns:
            Optional[MessageLog]: Saved message or None
        """
        try:
            # Sanitize content
            sanitized_content = self._sanitize_content(content)
            
            # Validate content
            if not self._validate_message_content(sanitized_content):
                logger.warning(f"Invalid message content for session {session_id}")
                return None
            
            # Create message log
            message = await self.repository.create(
                sid=session_id,
                message_id=message_id,
                message_type=MessageType.USER,
                direction=MessageDirection.INBOUND,
                content=sanitized_content,
                platform=platform,
                metadata={
                    **(metadata or {}),
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
            logger.debug(f"Saved candidate message {message.id} for session {session_id}")
            return message
            
        except SQLAlchemyError as e:
            logger.error(f"Database error saving candidate message: {e}")
            return None
        except Exception as e:
            logger.error(f"Error saving candidate message: {e}")
            return None
    
    async def load_transcript(
        self,
        session_id: str,
        limit: int = 50,
        include_metadata: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Load conversation transcript for a session.
        
        Args:
            session_id: Session identifier
            limit: Maximum number of messages to retrieve
            include_metadata: Whether to include metadata in results
            
        Returns:
            List[Dict[str, Any]]: Conversation transcript
        """
        try:
            # Get messages from repository
            messages = await self.repository.get_conversation_history(
                session_id, limit
            )
            
            # Format transcript
            transcript = []
            for msg in messages:
                message_data = {
                    'id': msg['id'],
                    'type': msg['type'],
                    'direction': msg['direction'],
                    'content': msg['content'],
                    'timestamp': msg['timestamp'],
                    'platform': msg['platform']
                }
                
                if include_metadata:
                    message_data['metadata'] = msg.get('metadata', {})
                
                transcript.append(message_data)
            
            logger.debug(f"Loaded transcript with {len(transcript)} messages for session {session_id}")
            return transcript
            
        except SQLAlchemyError as e:
            logger.error(f"Database error loading transcript: {e}")
            return []
        except Exception as e:
            logger.error(f"Error loading transcript: {e}")
            return []
    
    async def get_message_stats(
        self,
        session_id: Optional[str] = None,
        platform: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get message statistics.
        
        Args:
            session_id: Optional session identifier
            platform: Optional platform filter
            days: Number of days to analyze
            
        Returns:
            Dict[str, Any]: Message statistics
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=days)
            
            # Build query
            query = select(MessageLog)
            if session_id:
                query = query.where(MessageLog.sid == session_id)
            if platform:
                query = query.where(MessageLog.platform == platform)
            query = query.where(MessageLog.timestamp >= cutoff_time)
            
            # Execute query
            result = await self.db_session.execute(query)
            messages = result.scalars().all()
            
            # Calculate stats
            total_messages = len(messages)
            bot_messages = len([m for m in messages if m.type == MessageType.BOT])
            user_messages = len([m for m in messages if m.type == MessageType.USER])
            
            # Calculate average response time
            response_times = [m.metadata.get('response_time') for m in messages 
                            if m.metadata and m.metadata.get('response_time')]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            # Calculate success rate
            processed_messages = [m for m in messages if m.processed]
            success_rate = len([m for m in processed_messages if m.processed == 'success']) / len(processed_messages) if processed_messages else 0
            
            stats = {
                'total_messages': total_messages,
                'bot_messages': bot_messages,
                'user_messages': user_messages,
                'average_response_time': avg_response_time,
                'success_rate': success_rate,
                'platform_distribution': self._get_platform_distribution(messages),
                'hourly_activity': self._get_hourly_activity(messages),
                'skill_usage': self._get_skill_usage(messages)
            }
            
            return stats
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting message stats: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error getting message stats: {e}")
            return {}
    
    async def export_transcript(
        self,
        session_id: str,
        format: str = 'json',
        include_metadata: bool = False
    ) -> Optional[str]:
        """
        Export conversation transcript.
        
        Args:
            session_id: Session identifier
            format: Export format ('json', 'csv', 'txt')
            include_metadata: Whether to include metadata
            
        Returns:
            Optional[str]: Exported transcript or None
        """
        try:
            transcript = await self.load_transcript(
                session_id, 
                limit=1000,  # Large limit for export
                include_metadata=include_metadata
            )
            
            if format == 'json':
                import json
                return json.dumps(transcript, indent=2, ensure_ascii=False)
            
            elif format == 'csv':
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.writer(output)
                
                # Write header
                header = ['timestamp', 'type', 'direction', 'content', 'platform']
                if include_metadata:
                    header.append('metadata')
                writer.writerow(header)
                
                # Write data
                for msg in transcript:
                    row = [
                        msg['timestamp'],
                        msg['type'],
                        msg['direction'],
                        msg['content'],
                        msg['platform']
                    ]
                    if include_metadata:
                        row.append(str(msg.get('metadata', {})))
                    writer.writerow(row)
                
                return output.getvalue()
            
            elif format == 'txt':
                lines = []
                for msg in transcript:
                    timestamp = msg['timestamp']
                    sender = 'Bot' if msg['direction'] == 'outbound' else 'User'
                    content = msg['content']
                    lines.append(f"[{timestamp}] {sender}: {content}")
                return '\n'.join(lines)
            
            else:
                logger.error(f"Unsupported export format: {format}")
                return None
                
        except Exception as e:
            logger.error(f"Error exporting transcript: {e}")
            return None
    
    async def cleanup_old_messages(
        self,
        days_old: int = 90,
        session_id: Optional[str] = None
    ) -> int:
        """
        Clean up old messages.
        
        Args:
            days_old: Messages older than this many days will be deleted
            session_id: Optional session to clean (if None, clean all)
            
        Returns:
            int: Number of messages deleted
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            # Build query
            query = delete(MessageLog).where(MessageLog.timestamp < cutoff_date)
            if session_id:
                query = query.where(MessageLog.sid == session_id)
            
            # Execute deletion
            result = await self.db_session.execute(query)
            await self.db_session.commit()
            
            deleted_count = result.rowcount
            logger.info(f"Cleaned up {deleted_count} old messages")
            return deleted_count
            
        except SQLAlchemyError as e:
            logger.error(f"Database error cleaning up messages: {e}")
            await self.db_session.rollback()
            return 0
        except Exception as e:
            logger.error(f"Error cleaning up messages: {e}")
            return 0
    
    async def get_session_activity(
        self,
        session_id: str,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get activity metrics for a session.
        
        Args:
            session_id: Session identifier
            hours: Number of hours to analyze
            
        Returns:
            Dict[str, Any]: Activity metrics
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            # Get messages for session
            query = select(MessageLog).where(
                and_(
                    MessageLog.sid == session_id,
                    MessageLog.timestamp >= cutoff_time
                )
            ).order_by(desc(MessageLog.timestamp))
            
            result = await self.db_session.execute(query)
            messages = result.scalars().all()
            
            if not messages:
                return {
                    'session_id': session_id,
                    'active': False,
                    'last_activity': None,
                    'message_count': 0,
                    'bot_messages': 0,
                    'user_messages': 0
                }
            
            # Calculate metrics
            last_activity = messages[0].timestamp
            message_count = len(messages)
            bot_messages = len([m for m in messages if m.type == MessageType.BOT])
            user_messages = len([m for m in messages if m.type == MessageType.USER])
            
            return {
                'session_id': session_id,
                'active': True,
                'last_activity': last_activity.isoformat(),
                'message_count': message_count,
                'bot_messages': bot_messages,
                'user_messages': user_messages,
                'avg_response_time': self._calculate_avg_response_time(messages)
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting session activity: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error getting session activity: {e}")
            return {}
    
    def _sanitize_content(self, content: str) -> str:
        """
        Sanitize message content.
        
        Args:
            content: Raw message content
            
        Returns:
            str: Sanitized content
        """
        if not content:
            return ""
        
        # Remove excessive whitespace
        content = ' '.join(content.split())
        
        # Truncate if too long
        if len(content) > self.max_message_length:
            content = content[:self.max_message_length - 3] + "..."
        
        return content
    
    def _validate_message_content(self, content: str) -> bool:
        """
        Validate message content.
        
        Args:
            content: Message content to validate
            
        Returns:
            bool: True if content is valid
        """
        if not content or not content.strip():
            return False
        
        # Check for excessive length
        if len(content) > self.max_message_length:
            return False
        
        # Check for potentially harmful content
        harmful_patterns = [
            '<script',  # XSS prevention
            'javascript:',  # XSS prevention
            'data:',  # Data URI prevention
        ]
        
        content_lower = content.lower()
        for pattern in harmful_patterns:
            if pattern in content_lower:
                return False
        
        return True
    
    def _get_platform_distribution(self, messages: List[MessageLog]) -> Dict[str, int]:
        """
        Get platform distribution statistics.
        
        Args:
            messages: List of messages
            
        Returns:
            Dict[str, int]: Platform distribution
        """
        distribution = {}
        for msg in messages:
            platform = msg.platform
            distribution[platform] = distribution.get(platform, 0) + 1
        return distribution
    
    def _get_hourly_activity(self, messages: List[MessageLog]) -> Dict[str, int]:
        """
        Get hourly activity statistics.
        
        Args:
            messages: List of messages
            
        Returns:
            Dict[str, int]: Hourly activity
        """
        hourly_activity = {}
        for msg in messages:
            hour = msg.timestamp.hour
            hourly_activity[hour] = hourly_activity.get(hour, 0) + 1
        return hourly_activity
    
    def _get_skill_usage(self, messages: List[MessageLog]) -> Dict[str, int]:
        """
        Get skill usage statistics.
        
        Args:
            messages: List of messages
            
        Returns:
            Dict[str, int]: Skill usage
        """
        skill_usage = {}
        for msg in messages:
            if msg.skill_used:
                skill_usage[msg.skill_used] = skill_usage.get(msg.skill_used, 0) + 1
        return skill_usage
    
    def _calculate_avg_response_time(self, messages: List[MessageLog]) -> float:
        """
        Calculate average response time.
        
        Args:
            messages: List of messages
            
        Returns:
            float: Average response time
        """
        response_times = []
        user_msg_time = None
        
        for msg in reversed(messages):
            if msg.direction == MessageDirection.INBOUND:
                user_msg_time = msg.timestamp
            elif msg.direction == MessageDirection.OUTBOUND and user_msg_time:
                if msg.metadata and msg.metadata.get('response_time'):
                    response_times.append(msg.metadata['response_time'])
                elif user_msg_time:
                    # Calculate from timestamp difference
                    time_diff = (msg.timestamp - user_msg_time).total_seconds() * 1000
                    response_times.append(time_diff)
                    user_msg_time = None
        
        return sum(response_times) / len(response_times) if response_times else 0.0
    
    async def mark_message_processed(
        self,
        message_id: str,
        status: str,
        response_time: Optional[int] = None
    ) -> bool:
        """
        Mark a message as processed.
        
        Args:
            message_id: Message identifier
            status: Processing status ('success', 'failed', 'pending')
            response_time: Response time in milliseconds
            
        Returns:
            bool: True if successful
        """
        try:
            message = await self.repository.get_by_id(message_id)
            if not message:
                return False
            
            await self.repository.update_processed_status(
                message_id, status, response_time
            )
            
            logger.debug(f"Marked message {message_id} as {status}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Database error marking message as processed: {e}")
            return False
        except Exception as e:
            logger.error(f"Error marking message as processed: {e}")
            return False
    
    async def get_message_by_platform_message_id(
        self,
        platform: str,
        platform_message_id: str
    ) -> Optional[MessageLog]:
        """
        Get message by platform-specific message ID.
        
        Args:
            platform: Platform name
            platform_message_id: Platform-specific message ID
            
        Returns:
            Optional[MessageLog]: Message or None
        """
        try:
            query = select(MessageLog).where(
                and_(
                    MessageLog.platform == platform,
                    MessageLog.message_id == platform_message_id
                )
            )
            
            result = await self.db_session.execute(query)
            return result.scalar_one_or_none()
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting message by platform ID: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting message by platform ID: {e}")
            return None