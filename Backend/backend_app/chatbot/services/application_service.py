"""
Application Service for Chatbot/Co-Pilot Module

Handles integration with the applications system, including:
- Updating application status and prescreen results
- Managing application timelines
- Creating action queue entries
- Updating candidate profiles with fresh data
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class ApplicationService:
    """
    Service for managing application-related operations in the chatbot system.
    
    This service handles:
    - Application status updates
    - Prescreen result processing
    - Application timeline management
    - Action queue integration
    - Candidate profile updates
    """
    
    def __init__(self, db_session: AsyncSession):
        """
        Initialize Application Service.
        
        Args:
            db_session: Database session
        """
        self.db_session = db_session
        self.application_repo = ApplicationRepository(db_session)
        self.candidate_repo = CandidateRepository(db_session)
    
    async def update_prescreen_completion(
        self,
        application_id: str,
        prescreen_summary: Dict[str, Any],
        match_score: float,
        must_have_failed: bool = False
    ) -> bool:
        """
        Update application with prescreen completion results.
        
        Args:
            application_id: Application identifier
            prescreen_summary: JSON summary of prescreen answers and scores
            match_score: Job description match score (0-100)
            must_have_failed: Whether candidate failed any must-have criteria
            
        Returns:
            bool: True if update successful
        """
        try:
            # Get application
            application = await self.application_repo.get_by_id(application_id)
            if not application:
                logger.warning(f"Application {application_id} not found")
                return False
            
            # Update application fields
            update_data = {
                'pre_screening_completed': True,
                'pre_screening_summary': prescreen_summary,
                'jd_match_score': match_score,
                'must_have_failed': must_have_failed,
                'last_prescreening_at': datetime.utcnow()
            }
            
            # Update application
            await self.application_repo.update(application_id, **update_data)
            
            # Add timeline entry
            await self._add_timeline_entry(
                application_id,
                "Prescreening Completed",
                f"Match score: {match_score}%, Must-haves: {'Passed' if not must_have_failed else 'Failed'}"
            )
            
            # Create action queue entry if needed
            if must_have_failed:
                await self._create_action_queue_entry(
                    application_id,
                    "PRESREENING_FAILED",
                    f"Candidate failed must-have criteria (score: {match_score}%)"
                )
            else:
                await self._create_action_queue_entry(
                    application_id,
                    "PRESREENING_COMPLETE",
                    f"Candidate completed prescreening (score: {match_score}%)"
                )
            
            logger.info(f"Updated prescreen completion for application {application_id}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Database error updating prescreen completion: {e}")
            return False
        except Exception as e:
            logger.error(f"Error updating prescreen completion: {e}")
            return False
    
    async def mark_application_submitted(
        self,
        application_id: str,
        client_submission_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Mark application as submitted to client.
        
        Args:
            application_id: Application identifier
            client_submission_data: Additional client submission data
            
        Returns:
            bool: True if update successful
        """
        try:
            # Get application
            application = await self.application_repo.get_by_id(application_id)
            if not application:
                logger.warning(f"Application {application_id} not found")
                return False
            
            # Update application
            update_data = {
                'submitted_to_client': True,
                'submitted_to_client_at': datetime.utcnow()
            }
            
            if client_submission_data:
                update_data['client_submission_data'] = client_submission_data
            
            await self.application_repo.update(application_id, **update_data)
            
            # Add timeline entry
            await self._add_timeline_entry(
                application_id,
                "Submitted to Client",
                "Application submitted to client for review"
            )
            
            # Create action queue entry
            await self._create_action_queue_entry(
                application_id,
                "CLIENT_SUBMISSION",
                "Application submitted to client"
            )
            
            logger.info(f"Marked application {application_id} as submitted to client")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Database error marking application as submitted: {e}")
            return False
        except Exception as e:
            logger.error(f"Error marking application as submitted: {e}")
            return False
    
    async def update_candidate_profile_freshness(
        self,
        candidate_id: str,
        updated_fields: List[str],
        prescreen_answers: Dict[str, Any]
    ) -> bool:
        """
        Update candidate profile with fresh data from prescreening.
        
        Args:
            candidate_id: Candidate identifier
            updated_fields: List of fields that were updated
            prescreen_answers: Prescreen answers to update profile with
            
        Returns:
            bool: True if update successful
        """
        try:
            # Get candidate profile
            candidate = await self.candidate_repo.get_by_id(candidate_id)
            if not candidate:
                logger.warning(f"Candidate {candidate_id} not found")
                return False
            
            # Map prescreen answers to profile fields
            profile_updates = self._map_prescreen_to_profile(prescreen_answers)
            
            # Update profile fields
            if profile_updates:
                await self.candidate_repo.update(candidate_id, **profile_updates)
                
                # Update freshness timestamps
                freshness_updates = {
                    f"{field}_last_updated": datetime.utcnow() 
                    for field in updated_fields if field in profile_updates
                }
                
                if freshness_updates:
                    await self.candidate_repo.update(candidate_id, **freshness_updates)
            
            # Update last prescreening timestamp
            await self.candidate_repo.update(
                candidate_id,
                last_prescreening_at=datetime.utcnow()
            )
            
            logger.info(f"Updated candidate {candidate_id} profile freshness")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Database error updating candidate profile: {e}")
            return False
        except Exception as e:
            logger.error(f"Error updating candidate profile: {e}")
            return False
    
    async def get_application_status(self, application_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current application status and prescreen results.
        
        Args:
            application_id: Application identifier
            
        Returns:
            Optional[Dict[str, Any]]: Application status or None
        """
        try:
            application = await self.application_repo.get_by_id(application_id)
            if not application:
                return None
            
            return {
                'application_id': application.id,
                'job_id': application.job_id,
                'candidate_id': application.candidate_id,
                'pre_screening_completed': application.pre_screening_completed,
                'pre_screening_summary': application.pre_screening_summary,
                'jd_match_score': application.jd_match_score,
                'must_have_failed': application.must_have_failed,
                'submitted_to_client': application.submitted_to_client,
                'submitted_to_client_at': application.submitted_to_client_at,
                'last_updated': application.updated_at
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting application status: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting application status: {e}")
            return None
    
    async def create_application(
        self,
        job_id: str,
        candidate_id: str,
        source: str = "chatbot"
    ) -> Optional[str]:
        """
        Create new application through chatbot.
        
        Args:
            job_id: Job identifier
            candidate_id: Candidate identifier
            source: Application source
            
        Returns:
            Optional[str]: Application ID or None
        """
        try:
            # Check if application already exists
            existing_app = await self.application_repo.get_by_candidate_job(
                candidate_id, job_id
            )
            if existing_app:
                logger.warning(f"Application already exists for candidate {candidate_id} and job {job_id}")
                return existing_app.id
            
            # Create new application
            application_data = {
                'job_id': job_id,
                'candidate_id': candidate_id,
                'application_status': 'New',
                'source': source,
                'automation_status': 'New'
            }
            
            new_application = await self.application_repo.create(**application_data)
            
            # Add timeline entry
            await self._add_timeline_entry(
                new_application.id,
                "Application Created",
                f"Application created via {source}"
            )
            
            # Create action queue entry
            await self._create_action_queue_entry(
                new_application.id,
                "NEW_APPLICATION",
                f"New application created via {source}"
            )
            
            logger.info(f"Created application {new_application.id} for candidate {candidate_id}")
            return new_application.id
            
        except SQLAlchemyError as e:
            logger.error(f"Database error creating application: {e}")
            return None
        except Exception as e:
            logger.error(f"Error creating application: {e}")
            return None
    
    async def get_application_timeline(self, application_id: str) -> List[Dict[str, Any]]:
        """
        Get application timeline entries.
        
        Args:
            application_id: Application identifier
            
        Returns:
            List[Dict[str, Any]]: Timeline entries
        """
        try:
            # This would query the application_timeline table
            # For now, return empty list
            return []
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting application timeline: {e}")
            return []
        except Exception as e:
            logger.error(f"Error getting application timeline: {e}")
            return []
    
    def _map_prescreen_to_profile(self, prescreen_answers: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map prescreen answers to candidate profile fields.
        
        Args:
            prescreen_answers: Prescreen answers
            
        Returns:
            Dict[str, Any]: Profile field updates
        """
        profile_updates = {}
        
        # Map common prescreen fields to profile fields
        field_mappings = {
            'current_ctc': 'current_ctc',
            'expected_ctc': 'expected_ctc',
            'notice_period': 'notice_period',
            'current_location': 'current_location',
            'skills': 'skills',
            'preferred_location': 'preferred_location'
        }
        
        for prescreen_field, profile_field in field_mappings.items():
            if prescreen_field in prescreen_answers:
                profile_updates[profile_field] = prescreen_answers[prescreen_field]
        
        return profile_updates
    
    async def _add_timeline_entry(
        self,
        application_id: str,
        action: str,
        details: str
    ) -> bool:
        """
        Add entry to application timeline.
        
        Args:
            application_id: Application identifier
            action: Action description
            details: Action details
            
        Returns:
            bool: True if successful
        """
        try:
            timeline_entry = ApplicationTimeline(
                application_id=application_id,
                action=action,
                details=details,
                timestamp=datetime.utcnow()
            )
            
            self.db_session.add(timeline_entry)
            await self.db_session.commit()
            
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Database error adding timeline entry: {e}")
            await self.db_session.rollback()
            return False
        except Exception as e:
            logger.error(f"Error adding timeline entry: {e}")
            return False
    
    async def _create_action_queue_entry(
        self,
        application_id: str,
        action_type: str,
        details: str
    ) -> bool:
        """
        Create action queue entry.
        
        Args:
            application_id: Application identifier
            action_type: Type of action
            details: Action details
            
        Returns:
            bool: True if successful
        """
        try:
            action_entry = ActionQueue(
                application_id=application_id,
                action_type=action_type,
                details=details,
                status='pending',
                created_at=datetime.utcnow(),
                priority='medium'
            )
            
            self.db_session.add(action_entry)
            await self.db_session.commit()
            
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Database error creating action queue entry: {e}")
            await self.db_session.rollback()
            return False
        except Exception as e:
            logger.error(f"Error creating action queue entry: {e}")
            return False
    
    async def bulk_update_applications_status(
        self,
        application_ids: List[str],
        status: str,
        details: Optional[str] = None
    ) -> bool:
        """
        Bulk update application statuses.
        
        Args:
            application_ids: List of application identifiers
            status: New status
            details: Additional details
            
        Returns:
            bool: True if successful
        """
        try:
            # Update applications
            await self.application_repo.bulk_update_status(application_ids, status)
            
            # Add timeline entries
            for app_id in application_ids:
                await self._add_timeline_entry(
                    app_id,
                    f"Bulk Status Update: {status}",
                    details or f"Status updated to {status}"
                )
            
            logger.info(f"Bulk updated {len(application_ids)} applications to status {status}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Database error in bulk update: {e}")
            return False
        except Exception as e:
            logger.error(f"Error in bulk update: {e}")
            return False
    
    async def get_pending_applications(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get applications pending prescreening.
        
        Args:
            limit: Maximum number of applications to return
            
        Returns:
            List[Dict[str, Any]]: Pending applications
        """
        try:
            applications = await self.application_repo.get_pending_prescreening(limit)
            
            result = []
            for app in applications:
                result.append({
                    'application_id': app.id,
                    'job_id': app.job_id,
                    'candidate_id': app.candidate_id,
                    'application_status': app.application_status,
                    'created_at': app.created_at,
                    'source': app.source
                })
            
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting pending applications: {e}")
            return []
        except Exception as e:
            logger.error(f"Error getting pending applications: {e}")
            return []