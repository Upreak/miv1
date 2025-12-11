-- Migration B: Extend applications and candidate_profiles with timestamp fields
-- This migration adds timestamp fields for prescreening and freshness tracking

-- Add fields to applications table
ALTER TABLE applications 
ADD COLUMN IF NOT EXISTS pre_screening_completed BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS pre_screening_summary TEXT,
ADD COLUMN IF NOT EXISTS jd_match_score INTEGER,
ADD COLUMN IF NOT EXISTS must_have_failed BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS last_prescreening_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS submitted_to_client BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS submitted_to_client_at TIMESTAMP WITH TIME ZONE;

-- Add fields to candidate_profiles table
ALTER TABLE candidate_profiles 
ADD COLUMN IF NOT EXISTS current_ctc_last_updated TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS expected_ctc_last_updated TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS notice_period_last_updated TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS current_location_last_updated TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS skills_last_updated TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS preferred_location_last_updated TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS last_prescreening_at TIMESTAMP WITH TIME ZONE;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_applications_pre_screening_completed ON applications(pre_screening_completed);
CREATE INDEX IF NOT EXISTS idx_applications_submitted_to_client ON applications(submitted_to_client);
CREATE INDEX IF NOT EXISTS idx_applications_last_prescreening_at ON applications(last_prescreening_at);
CREATE INDEX IF NOT EXISTS idx_candidate_profiles_last_prescreening_at ON candidate_profiles(last_prescreening_at);

-- Add comments for documentation
COMMENT ON COLUMN applications.pre_screening_completed IS 'Whether prescreening questions have been completed for this application';
COMMENT ON COLUMN applications.pre_screening_summary IS 'JSON summary of prescreening answers and scores';
COMMENT ON COLUMN applications.jd_match_score IS 'Job description match score (0-100) based on prescreening answers';
COMMENT ON COLUMN applications.must_have_failed IS 'Whether candidate failed any must-have criteria';
COMMENT ON COLUMN applications.last_prescreening_at IS 'Timestamp of last prescreening completion';
COMMENT ON COLUMN applications.submitted_to_client IS 'Whether application has been submitted to client';
COMMENT ON COLUMN applications.submitted_to_client_at IS 'Timestamp when application was submitted to client';
COMMENT ON COLUMN candidate_profiles.current_ctc_last_updated IS 'Last update timestamp for current CTC field';
COMMENT ON COLUMN candidate_profiles.expected_ctc_last_updated IS 'Last update timestamp for expected CTC field';
COMMENT ON COLUMN candidate_profiles.notice_period_last_updated IS 'Last update timestamp for notice period field';
COMMENT ON COLUMN candidate_profiles.current_location_last_updated IS 'Last update timestamp for current location field';
COMMENT ON COLUMN candidate_profiles.skills_last_updated IS 'Last update timestamp for skills field';
COMMENT ON COLUMN candidate_profiles.preferred_location_last_updated IS 'Last update timestamp for preferred location field';
COMMENT ON COLUMN candidate_profiles.last_prescreening_at IS 'Timestamp of last prescreening for this candidate';