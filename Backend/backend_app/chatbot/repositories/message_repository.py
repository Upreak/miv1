"""
Message Repository for Chatbot/Co-Pilot Module

Handles database operations for chatbot messages.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from ..models.message_log_model import MessageLog, MessageType, MessageDirection


class MessageRepository:
    """
    Repository for chatbot message operations.
    
    Handles CRUD operations and message management queries.
    """
    
    def __init__(self, db: Session):
        """
        Initialize message repository.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def create(self, sid: str, message_id: Optional[str], message_type: MessageType,
               direction: MessageDirection, content: str, platform: str,
               metadata: Dict[str, Any] = None) -> MessageLog:
        """
        Create a new message log.
        
        Args:
            sid: Session ID
            message_id: Platform-specific message ID
            message_type: Message type
            direction: Message direction
            content: Message content
            platform: Platform where message was sent/received
            metadata: Additional message data
            
        Returns:
            MessageLog: Created message log
        """
        message = MessageLog(
            sid=sid,
            message_id=message_id,
            type=message_type,
            direction=direction,
            content=content,
            platform=platform,
            metadata=metadata or {}
        )
        
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        
        return message
    
    def get_by_id(self, message_id: str) -> Optional[MessageLog]:
        """
        Get message by ID.
        
        Args:
            message_id: Message ID
            
        Returns:
            Optional[MessageLog]: Message or None
        """
        return self.db.query(MessageLog).filter(MessageLog.id == message_id).first()
    
    def get_by_sid(self, sid: str, limit: int = 100) -> List[MessageLog]:
        """
        Get messages by session ID.
        
        Args:
            sid: Session ID
            limit: Maximum number of messages to return
            
        Returns:
            List[MessageLog]: List of messages
        """
        return self.db.query(MessageLog).filter(
            MessageLog.sid == sid
        ).order_by(MessageLog.timestamp.desc()).limit(limit).all()
    
    def get_by_platform(self, platform: str, limit: int = 100) -> List[MessageLog]:
        """
        Get messages by platform.
        
        Args:
            platform: Platform name
            limit: Maximum number of messages to return
            
        Returns:
            List[MessageLog]: List of messages
        """
        return self.db.query(MessageLog).filter(
            MessageLog.platform == platform
        ).order_by(MessageLog.timestamp.desc()).limit(limit).all()
    
    def get_by_type(self, message_type: MessageType, limit: int = 100) -> List[MessageLog]:
        """
        Get messages by type.
        
        Args:
            message_type: Message type
            limit: Maximum number of messages to return
            
        Returns:
            List[MessageLog]: List of messages
        """
        return self.db.query(MessageLog).filter(
            MessageLog.type == message_type
        ).order_by(MessageLog.timestamp.desc()).limit(limit).all()
    
    def get_by_direction(self, direction: MessageDirection, limit: int = 100) -> List[MessageLog]:
        """
        Get messages by direction.
        
        Args:
            direction: Message direction
            limit: Maximum number of messages to return
            
        Returns:
            List[MessageLog]: List of messages
        """
        return self.db.query(MessageLog).filter(
            MessageLog.direction == direction
        ).order_by(MessageLog.timestamp.desc()).limit(limit).all()
    
    def get_recent_messages(self, hours: int = 24, limit: int = 100) -> List[MessageLog]:
        """
        Get recent messages.
        
        Args:
            hours: Messages from the last N hours
            limit: Maximum number of messages to return
            
        Returns:
            List[MessageLog]: List of recent messages
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return self.db.query(MessageLog).filter(
            MessageLog.timestamp >= cutoff_time
        ).order_by(MessageLog.timestamp.desc()).limit(limit).all()
    
    def get_conversation_history(self, sid: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get conversation history for a session.
        
        Args:
            sid: Session ID
            limit: Maximum number of messages to return
            
        Returns:
            List[Dict[str, Any]]: Conversation history
        """
        messages = self.db.query(MessageLog).filter(
            MessageLog.sid == sid
        ).order_by(MessageLog.timestamp.asc()).limit(limit).all()
        
        history = []
        for message in messages:
            history.append({
                'id': message.id,
                'type': message.type.value,
                'direction': message.direction.value,
                'content': message.content,
                'timestamp': message.timestamp.isoformat(),
                'platform': message.platform,
                'processed': message.processed,
                'response_time': message.response_time,
                'skill_used': message.skill_used
            })
        
        return history
    
    def update_processed_status(self, message_id: str, status: str, 
                              response_time: Optional[int] = None) -> Optional[MessageLog]:
        """
        Update message processed status.
        
        Args:
            message_id: Message ID
            status: Processing status
            response_time: Response time in milliseconds
            
        Returns:
            Optional[MessageLog]: Updated message or None
        """
        message = self.get_by_id(message_id)
        if not message:
            return None
        
        message.processed = status
        if response_time is not None:
            message.response_time = response_time
        
        self.db.commit()
        self.db.refresh(message)
        
        return message
    
    def set_skill_used(self, message_id: str, skill_name: str) -> Optional[MessageLog]:
        """
        Set skill used for message processing.
        
        Args:
            message_id: Message ID
            skill_name: Name of skill used
            
        Returns:
            Optional[MessageLog]: Updated message or None
        """
        message = self.get_by_id(message_id)
        if not message:
            return None
        
        message.skill_used = skill_name
        self.db.commit()
        self.db.refresh(message)
        
        return message
    
    def get_message_stats(self) -> Dict[str, Any]:
        """
        Get message statistics.
        
        Returns:
            Dict[str, Any]: Message statistics
        """
        total_messages = self.db.query(MessageLog).count()
        
        # Count by platform
        platform_counts = {}
        for platform in ['whatsapp', 'telegram', 'web']:
            count = self.db.query(MessageLog).filter(MessageLog.platform == platform).count()
            platform_counts[platform] = count
        
        # Count by type
        type_counts = {}
        for msg_type in MessageType:
            count = self.db.query(MessageLog).filter(MessageLog.type == msg_type).count()
            type_counts[msg_type.value] = count
        
        # Count by direction
        direction_counts = {}
        for direction in MessageDirection:
            count = self.db.query(MessageLog).filter(MessageLog.direction == direction).count()
            direction_counts[direction.value] = count
        
        # Get average response time
        response_times = self.db.query(
            MessageLog.response_time
        ).filter(MessageLog.response_time.isnot(None)).all()
        
        avg_response_time = sum(rt[0] for rt in response_times) / len(response_times) if response_times else 0
        
        # Get success rate
        processed_messages = self.db.query(MessageLog).filter(
            MessageLog.processed.isnot(None)
        ).all()
        
        success_count = sum(1 for msg in processed_messages if msg.processed == 'success')
        success_rate = success_count / len(processed_messages) if processed_messages else 0
        
        return {
            'total_messages': total_messages,
            'platform_distribution': platform_counts,
            'type_distribution': type_counts,
            'direction_distribution': direction_counts,
            'average_response_time': avg_response_time,
            'success_rate': success_rate
        }
    
    def get_skill_usage_stats(self) -> Dict[str, Any]:
        """
        Get skill usage statistics.
        
        Returns:
            Dict[str, Any]: Skill usage statistics
        """
        # Get all skills used
        skills = self.db.query(
            MessageLog.skill_used,
            func.count(MessageLog.id).label('count')
        ).filter(
            MessageLog.skill_used.isnot(None)
        ).group_by(MessageLog.skill_used).all()
        
        # Get average response time by skill
        skill_response_times = self.db.query(
            MessageLog.skill_used,
            func.avg(MessageLog.response_time).label('avg_response_time')
        ).filter(
            MessageLog.skill_used.isnot(None),
            MessageLog.response_time.isnot(None)
        ).group_by(MessageLog.skill_used).all()
        
        stats = {}
        for skill, count in skills:
            avg_time = next((rt.avg_response_time for rt in skill_response_times if rt.skill_used == skill), 0)
            stats[skill] = {
                'usage_count': count,
                'average_response_time': avg_time
            }
        
        return stats
    
    def get_platform_performance(self) -> Dict[str, Any]:
        """
        Get platform performance metrics.
        
        Returns:
            Dict[str, Any]: Platform performance metrics
        """
        platforms = ['whatsapp', 'telegram', 'web']
        
        performance = {}
        for platform in platforms:
            # Get messages for this platform
            platform_messages = self.db.query(MessageLog).filter(
                MessageLog.platform == platform
            ).all()
            
            if not platform_messages:
                performance[platform] = {
                    'total_messages': 0,
                    'average_response_time': 0,
                    'success_rate': 0
                }
                continue
            
            # Calculate metrics
            total_messages = len(platform_messages)
            response_times = [msg.response_time for msg in platform_messages if msg.response_time]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            processed_messages = [msg for msg in platform_messages if msg.processed]
            success_count = sum(1 for msg in processed_messages if msg.processed == 'success')
            success_rate = success_count / len(processed_messages) if processed_messages else 0
            
            performance[platform] = {
                'total_messages': total_messages,
                'average_response_time': avg_response_time,
                'success_rate': success_rate
            }
        
        return performance
    
    def search_messages(self, query: str, limit: int = 100) -> List[MessageLog]:
        """
        Search messages by content.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List[MessageLog]: Matching messages
        """
        return self.db.query(MessageLog).filter(
            MessageLog.content.ilike(f'%{query}%')
        ).order_by(MessageLog.timestamp.desc()).limit(limit).all()
    
    def get_messages_by_skill(self, skill_name: str, limit: int = 100) -> List[MessageLog]:
        """
        Get messages processed by a specific skill.
        
        Args:
            skill_name: Skill name
            limit: Maximum number of messages to return
            
        Returns:
            List[MessageLog]: Messages processed by skill
        """
        return self.db.query(MessageLog).filter(
            MessageLog.skill_used == skill_name
        ).order_by(MessageLog.timestamp.desc()).limit(limit).all()
    
    def get_error_messages(self, limit: int = 100) -> List[MessageLog]:
        """
        Get error messages.
        
        Args:
            limit: Maximum number of messages to return
            
        Returns:
            List[MessageLog]: Error messages
        """
        return self.db.query(MessageLog).filter(
            or_(
                MessageLog.type == MessageType.ERROR,
                MessageLog.processed == 'failed'
            )
        ).order_by(MessageLog.timestamp.desc()).limit(limit).all()
    
    def cleanup_old_messages(self, days_old: int = 90) -> int:
        """
        Clean up old messages.
        
        Args:
            days_old: Messages older than this many days will be deleted
            
        Returns:
            int: Number of messages deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        messages_to_delete = self.db.query(MessageLog).filter(
            MessageLog.timestamp < cutoff_date
        ).all()
        
        count = len(messages_to_delete)
        
        for message in messages_to_delete:
            self.db.delete(message)
        
        self.db.commit()
        
        return count
    
    def get_hourly_message_stats(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get hourly message statistics.
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            List[Dict[str, Any]]: Hourly statistics
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Group by hour
        hourly_stats = self.db.query(
            func.date_trunc('hour', MessageLog.timestamp).label('hour'),
            func.count(MessageLog.id).label('count'),
            func.avg(MessageLog.response_time).label('avg_response_time')
        ).filter(
            MessageLog.timestamp >= cutoff_time
        ).group_by(
            func.date_trunc('hour', MessageLog.timestamp)
        ).order_by(
            func.date_trunc('hour', MessageLog.timestamp)
        ).all()
        
        stats = []
        for stat in hourly_stats:
            stats.append({
                'hour': stat.hour.isoformat(),
                'message_count': stat.count,
                'average_response_time': stat.avg_response_time or 0
            })
        
        return stats
    
    def get_user_message_patterns(self, sid: str, days: int = 7) -> Dict[str, Any]:
        """
        Analyze user message patterns.
        
        Args:
            sid: Session ID
            days: Number of days to analyze
            
        Returns:
            Dict[str, Any]: Message patterns
        """
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        messages = self.db.query(MessageLog).filter(
            and_(
                MessageLog.sid == sid,
                MessageLog.timestamp >= cutoff_time
            )
        ).all()
        
        if not messages:
            return {'error': 'No messages found for the specified period'}
        
        # Analyze patterns
        total_messages = len(messages)
        user_messages = [msg for msg in messages if msg.direction == MessageDirection.INBOUND]
        bot_messages = [msg for msg in messages if msg.direction == MessageDirection.OUTBOUND]
        
        # Calculate response times
        response_times = []
        for i, msg in enumerate(bot_messages):
            if i < len(user_messages):
                # Calculate time difference between user message and bot response
                time_diff = (msg.timestamp - user_messages[i].timestamp).total_seconds() * 1000
                response_times.append(time_diff)
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Message length analysis
        user_message_lengths = [len(msg.content) for msg in user_messages]
        bot_message_lengths = [len(msg.content) for msg in bot_messages]
        
        avg_user_message_length = sum(user_message_lengths) / len(user_message_lengths) if user_message_lengths else 0
        avg_bot_message_length = sum(bot_message_lengths) / len(bot_message_lengths) if bot_message_lengths else 0
        
        return {
            'total_messages': total_messages,
            'user_messages': len(user_messages),
            'bot_messages': len(bot_messages),
            'average_response_time': avg_response_time,
            'average_user_message_length': avg_user_message_length,
            'average_bot_message_length': avg_bot_message_length,
            'messages_per_day': total_messages / days
        }
    
    def export_conversation(self, sid: str, format: str = 'json') -> str:
        """
        Export conversation for a session.
        
        Args:
            sid: Session ID
            format: Export format ('json', 'csv')
            
        Returns:
            str: Exported conversation
        """
        messages = self.get_conversation_history(sid, limit=1000)
        
        if format == 'json':
            return str(messages)
        elif format == 'csv':
            # Simple CSV export
            lines = ['timestamp,type,direction,content,platform']
            for msg in messages:
                lines.append(f"{msg['timestamp']},{msg['type']},{msg['direction']},"
                           f'"{msg["content"]}",{msg["platform"]}')
            return '\n'.join(lines)
        else:
            raise ValueError(f"Unsupported export format: {format}")