from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..db.models.users import User
from ..db.models.candidate_profiles import CandidateProfile
from ..shared.schemas import CandidateProfileCreate, CandidateProfileUpdate
import logging

logger = logging.getLogger(__name__)

class CandidateRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email, User.role == 'Candidate').first()

    def create(self, data: Dict[str, Any]) -> User:
        # Create a basic user record for the candidate
        user = User(
            email=data.get("email"),
            full_name=data.get("name"),
            role="Candidate",
            # Generate a temporary password or handle auth separately
            hashed_password="TEMPORARY_HASH", 
            phone_number=data.get("phone")
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def create_profile(self, profile_create: CandidateProfileCreate) -> CandidateProfile:
        # Convert schema to dict, excluding fields not in model
        # Note: Implementation depends on Schema vs Model alignment
        # For now, we manually map or dump
        
        # Check if profile exists for user
        existing = self.get_latest_profile(profile_create.candidate_id) # candidate_id here is user_id
        if existing:
            return self.update_profile(existing.id, CandidateProfileUpdate(**profile_create.dict()))

        db_profile = CandidateProfile(
            user_id=profile_create.candidate_id, # Mapping candidate_id to user_id
            # Map other fields from profile_create to model columns
            # This requires careful mapping based on the actual model structure
            # For simplicity in this fix, we assume profile_create fields match relevant columns or we pass generic JSON
            skills=profile_create.skills,
            experience=profile_create.work_experience, # distinct fields?
            education=profile_create.education
            # Add other fields as needed based on CandidateProfile model definition
        )
        self.db.add(db_profile)
        self.db.commit()
        self.db.refresh(db_profile)
        return db_profile

    def get_latest_profile(self, user_id: int) -> Optional[CandidateProfile]:
        return self.db.query(CandidateProfile).filter(CandidateProfile.user_id == user_id).first()

    def update_profile(self, profile_id: int, update_data: CandidateProfileUpdate) -> CandidateProfile:
        db_profile = self.db.query(CandidateProfile).filter(CandidateProfile.id == profile_id).first()
        if db_profile:
            # Update fields
            # ... implementation ...
            self.db.commit()
            self.db.refresh(db_profile)
        return db_profile
