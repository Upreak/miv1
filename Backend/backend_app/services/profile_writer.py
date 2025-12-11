from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
import logging
import json

from ..db.models.candidate_profiles import CandidateProfile
from ..db.models.users import User
from ..repositories.candidate_repo import CandidateRepository
from ..repositories.user_repo import UserRepository
from ..shared.schemas import CandidateProfileCreate, CandidateProfileUpdate

logger = logging.getLogger(__name__)

class ProfileWriter:
    """
    Service for writing and managing candidate profiles.
    Handles the conversion of parsed resume data into structured candidate profiles.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.candidate_repo = CandidateRepository(db)
        self.user_repo = UserRepository(db)
    
    def create_profile_from_parsed_data(
        self, 
        parsed_data: Dict[str, Any], 
        user_id: Optional[int] = None,
        source: str = "manual"
    ) -> CandidateProfile:
        """
        Create a candidate profile from parsed resume data.
        
        Args:
            parsed_data: Dictionary containing parsed resume information
            user_id: Optional user ID who uploaded the resume
            source: Source of the profile (manual, whatsapp, telegram, email, etc.)
            
        Returns:
            CandidateProfile: The created profile
        """
        try:
            # Extract structured data from parsed resume
            profile_data = self._extract_profile_data(parsed_data)
            
            # Create or get candidate
            candidate = self._create_or_get_candidate(profile_data, user_id)
            
            # Create profile
            profile = self._create_profile(candidate, profile_data, source)
            
            logger.info(f"Successfully created profile for candidate: {candidate.name}")
            return profile
            
        except Exception as e:
            logger.error(f"Error creating profile from parsed data: {str(e)}")
            raise
    
    def update_profile_from_parsed_data(
        self, 
        profile_id: int, 
        parsed_data: Dict[str, Any]
    ) -> CandidateProfile:
        """
        Update an existing candidate profile with new parsed data.
        
        Args:
            profile_id: ID of the profile to update
            parsed_data: Dictionary containing updated parsed resume information
            
        Returns:
            CandidateProfile: The updated profile
        """
        try:
            # Get existing profile
            profile = self.candidate_repo.get_profile_by_id(profile_id)
            if not profile:
                raise ValueError(f"Profile with ID {profile_id} not found")
            
            # Extract structured data
            profile_data = self._extract_profile_data(parsed_data)
            
            # Update profile
            updated_profile = self._update_profile(profile, profile_data)
            
            logger.info(f"Successfully updated profile ID: {profile_id}")
            return updated_profile
            
        except Exception as e:
            logger.error(f"Error updating profile from parsed data: {str(e)}")
            raise
    
    def bulk_create_profiles(
        self, 
        profiles_data: List[Dict[str, Any]], 
        user_id: Optional[int] = None
    ) -> List[CandidateProfile]:
        """
        Create multiple candidate profiles in bulk.
        
        Args:
            profiles_data: List of dictionaries containing parsed resume data
            user_id: Optional user ID who uploaded the resumes
            
        Returns:
            List[CandidateProfile]: List of created profiles
        """
        created_profiles = []
        
        try:
            for profile_data in profiles_data:
                profile = self.create_profile_from_parsed_data(
                    parsed_data=profile_data,
                    user_id=user_id,
                    source="bulk"
                )
                created_profiles.append(profile)
            
            logger.info(f"Successfully created {len(created_profiles)} profiles in bulk")
            return created_profiles
            
        except Exception as e:
            logger.error(f"Error in bulk profile creation: {str(e)}")
            raise
    
    def _extract_profile_data(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured profile data from parsed resume.
        
        Args:
            parsed_data: Raw parsed resume data
            
        Returns:
            Dict[str, Any]: Structured profile data
        """
        # This should match the structure expected by the brain module
        profile_data = {
            "personal_info": {
                "name": parsed_data.get("name", ""),
                "email": parsed_data.get("email", ""),
                "phone": parsed_data.get("phone", ""),
                "location": parsed_data.get("location", ""),
                "linkedin_url": parsed_data.get("linkedin_url", ""),
                "website_url": parsed_data.get("website_url", ""),
                "summary": parsed_data.get("summary", "")
            },
            "work_experience": parsed_data.get("work_experience", []),
            "education": parsed_data.get("education", []),
            "skills": parsed_data.get("skills", []),
            "certifications": parsed_data.get("certifications", []),
            "languages": parsed_data.get("languages", []),
            "projects": parsed_data.get("projects", []),
            "achievements": parsed_data.get("achievements", []),
            "metadata": {
                "extraction_date": datetime.utcnow().isoformat(),
                "extraction_confidence": parsed_data.get("confidence", 0.0),
                "raw_data": json.dumps(parsed_data)
            }
        }
        
        return profile_data
    
    def _create_or_get_candidate(self, profile_data: Dict[str, Any], user_id: Optional[int]) -> User:
        """
        Create a new candidate (User) or get existing one based on email.
        
        Args:
            profile_data: Structured profile data
            user_id: Optional user ID
            
        Returns:
            User: The candidate user record
        """
        email = profile_data["personal_info"].get("email")
        
        if email:
            # Try to find existing candidate by email
            candidate = self.candidate_repo.get_by_email(email)
            if candidate:
                logger.info(f"Found existing candidate user: {candidate.full_name}")
                return candidate
        
        # Create new candidate user (Note: Password handling needs improvement)
        candidate_data = {
            "name": profile_data["personal_info"].get("name", ""),
            "email": email or "",
            "phone": profile_data["personal_info"].get("phone", ""),
            "location": profile_data["personal_info"].get("location", ""),
            "user_id": user_id
        }
        
        candidate = self.candidate_repo.create(candidate_data)
        logger.info(f"Created new candidate user: {candidate.full_name}")
        return candidate
    
    def _create_profile(self, candidate: User, profile_data: Dict[str, Any], source: str) -> CandidateProfile:
        """
        Create a candidate profile.
        
        Args:
            candidate: Candidate User record
            profile_data: Structured profile data
            source: Source of the profile
            
        Returns:
            CandidateProfile: The created profile
        """
        profile_create = CandidateProfileCreate(
            candidate_id=candidate.id,
            personal_info=profile_data["personal_info"],
            work_experience=profile_data["work_experience"],
            education=profile_data["education"],
            skills=profile_data["skills"],
            certifications=profile_data["certifications"],
            languages=profile_data["languages"],
            projects=profile_data["projects"],
            achievements=profile_data["achievements"],
            metadata=profile_data["metadata"],
            source=source
        )
        
        profile = self.candidate_repo.create_profile(profile_create)
        logger.info(f"Created profile for candidate {candidate.full_name}")
        return profile
    
    def _update_profile(self, profile: CandidateProfile, profile_data: Dict[str, Any]) -> CandidateProfile:
        """
        Update an existing candidate profile.
        
        Args:
            profile: Existing profile to update
            profile_data: Updated profile data
            
        Returns:
            CandidateProfile: The updated profile
        """
        profile_update = CandidateProfileUpdate(
            personal_info=profile_data["personal_info"],
            work_experience=profile_data["work_experience"],
            education=profile_data["education"],
            skills=profile_data["skills"],
            certifications=profile_data["certifications"],
            languages=profile_data["languages"],
            projects=profile_data["projects"],
            achievements=profile_data["achievements"],
            metadata=profile_data["metadata"]
        )
        
        updated_profile = self.candidate_repo.update_profile(profile.id, profile_update)
        logger.info(f"Updated profile ID: {profile.id}")
        return updated_profile
    
    def get_profile_by_candidate_id(self, candidate_id: int) -> Optional[CandidateProfile]:
        """
        Get the latest profile for a candidate.
        
        Args:
            candidate_id: Candidate ID
            
        Returns:
            CandidateProfile: The candidate profile or None
        """
        return self.candidate_repo.get_latest_profile(candidate_id)
    
    def get_profiles_by_user_id(self, user_id: int) -> List[CandidateProfile]:
        """
        Get all profiles created by a specific user.
        
        Args:
            user_id: User ID
            
        Returns:
            List[CandidateProfile]: List of profiles
        """
        return self.candidate_repo.get_profiles_by_user_id(user_id)
    
    def search_profiles(self, query: str, limit: int = 10) -> List[CandidateProfile]:
        """
        Search for candidate profiles by name, email, or skills.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List[CandidateProfile]: Matching profiles
        """
        return self.candidate_repo.search_profiles(query, limit)
    
    def get_profile_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about candidate profiles.
        
        Returns:
            Dict[str, Any]: Profile statistics
        """
        total_profiles = self.candidate_repo.count_profiles()
        profiles_by_source = self.candidate_repo.count_profiles_by_source()
        profiles_by_month = self.candidate_repo.count_profiles_by_month()
        
        return {
            "total_profiles": total_profiles,
            "profiles_by_source": profiles_by_source,
            "profiles_by_month": profiles_by_month,
            "average_confidence": self.candidate_repo.get_average_confidence()
        }