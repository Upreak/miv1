

# Production Database Schema Specification

## 1. Core Identity & Authentication
**Table: users**
*Stores login credentials and global role.*
- `id` (UUID, PK): Unique identifier
- `email` (VARCHAR, Unique): User email
- `password_hash` (VARCHAR): Bcrypt hash
- `role` (ENUM): 'ADMIN', 'RECRUITER', 'SALES', 'CANDIDATE', 'MANAGER'
- `full_name` (VARCHAR): Display name
- `avatar_url` (VARCHAR): S3 URL
- `status` (ENUM): 'Active', 'Inactive'
- `is_verified` (BOOLEAN): Email verification status
- `created_at` (TIMESTAMP)
- `last_login` (TIMESTAMP)
- `last_active` (TIMESTAMP): For tracking user presence

**Table: system_settings**
*Stores global configuration and feature flags.*
- `key` (VARCHAR, PK): e.g., 'ENABLE_AI_PARSING', 'MAINTENANCE_MODE'
- `value` (JSONB): The setting value (boolean, string, or config object)
- `description` (TEXT)
- `updated_at` (TIMESTAMP)
- `updated_by` (UUID, FK -> users.id)

---

## 2. Public Job Board & "Hot Drops"
*Stores both internal jobs and external jobs found by AI.*

**Table: external_job_postings (Hot Drops)**
*Persists the "Daily Hot Drops" found by the AI to prevent re-fetching.*
- `id` (UUID, PK)
- `source` (VARCHAR): 'AI_Scraper', 'LinkedIn', 'Indeed'
- `original_url` (TEXT): Link to the external job
- `title` (VARCHAR)
- `company_name` (VARCHAR)
- `location` (VARCHAR)
- `posted_date` (DATE)
- `summary` (TEXT)
- `salary_text` (VARCHAR): Scraped salary (e.g., "$100k - $120k" or "Not Disclosed")
- `job_type` (VARCHAR): 'Remote', 'Contract', 'Full-time'
- `fetched_at` (TIMESTAMP): When our AI found it
- `expires_at` (TIMESTAMP): TTL for cache (e.g., 24 hours)

---

## 3. Recruitment Module (ATS)
*Manages internal job postings and the hiring pipeline. Google Jobs Compliant Schema.*

**Table: jobs (Internal Postings)**
**Basic Details**
- `id` (UUID, PK)
- `client_id` (UUID, FK -> clients.id): The company hiring
- `assigned_recruiter_id` (UUID, FK -> users.id): Internal owner
- `title` (VARCHAR): job_title
- `internal_job_id` (VARCHAR): job_id
- `employment_type` (ENUM): 'FULL_TIME', 'PART_TIME', 'CONTRACTOR', 'TEMPORARY', 'INTERN'
- `work_mode` (ENUM): 'On-site', 'Remote', 'Hybrid'
- `industry` (VARCHAR)
- `functional_area` (VARCHAR)

**Location & Compensation**
- `job_locations` (JSONB): Array of strings (City, State)
- `min_salary` (BIGINT)
- `max_salary` (BIGINT)
- `currency` (VARCHAR): 'INR', 'USD'
- `salary_unit` (ENUM): 'YEAR', 'MONTH', 'HOUR'
- `benefits_perks` (JSONB): Array of strings

**Description & Requirements**
- `about_company` (TEXT)
- `job_summary` (TEXT): Full description
- `responsibilities` (JSONB): Key duties
- `experience_required` (VARCHAR): e.g. "3-5 Years"
- `education_qualification` (VARCHAR): e.g. "B.Tech"
- `required_skills` (JSONB): `["React", "Node"]`
- `preferred_skills` (JSONB)
- `tools_tech_stack` (JSONB)

**Application & Process**
- `number_of_openings` (INT)
- `application_deadline` (DATE)
- `hiring_process_rounds` (JSONB): Array of round names e.g. ["Screening", "Tech"]
- `notice_period_accepted` (VARCHAR): e.g. "Immediate to 30 Days"

**SEO & Metadata**
- `slug_url` (VARCHAR, Unique): SEO friendly URL
- `meta_title` (VARCHAR): SEO Title
- `meta_description` (VARCHAR): SEO Description

**Status**
- `status` (ENUM): 'Draft', 'Sourcing', 'Interview', 'Offer', 'Closed'
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

---

## 4. Candidate Profile (The Person)
*Stores the "Master Profile" of a user. One user = One Profile. **Independent of specific jobs.**.*

**Table: candidate_profiles**
- `user_id` (UUID, PK, FK -> users.id)
- `phone` (VARCHAR)
- `linkedin_url` (VARCHAR)
- `portfolio_url` (VARCHAR)
- `github_url` (VARCHAR)
- `resume_url` (VARCHAR): Link to the master resume file (S3)
- `resume_last_updated` (TIMESTAMP)
- `bio` (TEXT): Professional Summary
- `is_actively_searching` (BOOLEAN)

**Skills & Education (Section B)**
- `highest_education` (VARCHAR)
- `year_of_passing` (INT)
- `skills` (JSONB): `["React", "TypeScript"]`
- `certificates` (JSONB): `["AWS Certified"]`
- `projects_summary` (TEXT)
- `ai_skills_vector` (VECTOR): For semantic search matching (pgvector)

**Job Preferences (Section C)**
- `total_experience_years` (DECIMAL)
- `current_role` (VARCHAR)
- `expected_role` (VARCHAR)
- `job_type_preference` (VARCHAR): Full-time/Contract
- `current_locations` (JSONB): `["Bangalore"]`
- `preferred_locations` (JSONB): `["Remote", "Mumbai"]`
- `ready_to_relocate` (VARCHAR): 'Yes', 'No', 'Open to Discussion'
- `notice_period` (INT): Days
- `availability_date` (DATE)
- `shift_preference` (VARCHAR): Day/Night/Flex
- `work_authorization` (VARCHAR)

**Salary Info (Section D)**
- `current_ctc` (BIGINT)
- `expected_ctc` (BIGINT)
- `currency` (VARCHAR)
- `is_ctc_negotiable` (BOOLEAN)

**Personal & Broader Preferences (Section E)**
- `looking_for_jobs_abroad` (BOOLEAN)
- `sector_preference` (VARCHAR): Private/Govt
- `preferred_industries` (JSONB)
- `gender` (VARCHAR)
- `marital_status` (VARCHAR)
- `dob` (DATE)
- `languages` (JSONB)
- `reservation_category` (VARCHAR): General/OBC/SC/ST
- `disability` (VARCHAR): Text description or NULL
- `willingness_to_travel` (VARCHAR)
- `has_driving_license` (BOOLEAN)

**Contact & Availability (Section G)**
- `has_current_offers` (BOOLEAN)
- `number_of_offers` (INT)
- `best_time_to_contact` (VARCHAR)
- `preferred_contact_mode` (VARCHAR): Email/Call/WhatsApp
- `alternate_email` (VARCHAR)
- `alternate_phone` (VARCHAR)
- `time_zone` (VARCHAR)

**Table: candidate_work_history (Section F)**
- `id` (UUID, PK)
- `profile_id` (UUID, FK -> candidate_profiles.user_id)
- `company_name` (VARCHAR)
- `job_title` (VARCHAR)
- `start_date` (DATE)
- `end_date` (DATE)
- `is_current` (BOOLEAN)
- `responsibilities` (TEXT)
- `tools_used` (JSONB)
- `ctc_at_role` (VARCHAR)

---

## 5. Applications (The Pivot / Link)
*This is the MOST CRITICAL table for tracking "One Candidate, Multiple Jobs".*

**Table: applications**
- `id` (UUID, PK)
- `job_id` (UUID, FK -> jobs.id)
- `candidate_id` (UUID, FK -> users.id)
- `applied_at` (TIMESTAMP)

**Job-Specific Tracking**
- `status` (ENUM): 'New', 'Screening', 'Interview', 'Offer', 'Rejected', 'Withdrawn'
- `is_active` (BOOLEAN): True if process is ongoing. False if rejected/hired/withdrawn.
- `match_score` (INT): 0-100. *Specific to this job description*.
- `ai_custom_summary` (TEXT): "Candidate matches React requirement but is expensive for this specific budget."

**Automation & Co-Pilot State**
- `automation_status` (ENUM): 'New', 'Contacting...', 'Awaiting Reply', 'Live Chat', 'Intervention Needed', 'Completed', 'Declined'
- `is_recruiter_approved` (BOOLEAN): Manual override to boost candidate visibility.

**Manual Follow-up Tracking**
- `follow_up_status` (VARCHAR): 'Shortlisted', 'Int-scheduled', 'Offered', 'Joined', 'No Show', 'Under Follow-up', 'Rejected'
- `next_follow_up_date` (DATE): For calendar reminders.
- `follow_up_remarks` (TEXT): Recruiter's internal notes.

**Table: application_timeline**
*Logs history of status changes for a specific application.*
- `id` (UUID, PK)
- `application_id` (UUID, FK -> applications.id)
- `previous_status` (VARCHAR)
- `new_status` (VARCHAR)
- `changed_by` (UUID, FK -> users.id)
- `remarks` (TEXT)
- `created_at` (TIMESTAMP)

---

## 6. Action Queue (Notifications & Tasks)
*Manages the recruiter's "My Action Queue" panel.*

**Table: action_queue**
- `id` (UUID, PK)
- `user_id` (UUID, FK -> users.id): The recruiter who needs to see this.
- `type` (ENUM): 'NEW_MATCHES', 'CHAT_FOLLOWUP', 'NO_RESPONSE', 'PARSE_FAILURE', 'INTERVENTION_NEEDED'
- `title` (VARCHAR)
- `description` (TEXT)
- `priority` (ENUM): 'High', 'Medium', 'Low'
- `related_job_id` (UUID, FK -> jobs.id, Nullable)
- `related_candidate_id` (UUID, FK -> users.id, Nullable)
- `is_dismissed` (BOOLEAN)
- `created_at` (TIMESTAMP)

---

## 7. Sales Module (CRM)
**Table: leads**
- `id` (UUID, PK)
- `owner_id` (UUID, FK -> users.id)
- `company_name` (VARCHAR)
- `contact_person` (VARCHAR)
- `contact_email` (VARCHAR)
- `contact_phone` (VARCHAR)
- `status` (ENUM): 'New', 'Contacted', 'Qualified', 'Proposal', 'Negotiation', 'Converted', 'Lost'
- `service_type` (ENUM): 'Permanent', 'Contract', 'RPO', 'Executive Search'
- `estimated_value` (DECIMAL)
- `probability` (INT): 0-100
- `expected_close_date` (DATE)
- `next_follow_up` (TIMESTAMP)
- `source` (VARCHAR)

**Table: sales_tasks**
*Tracks tasks associated with leads.*
- `id` (UUID, PK)
- `lead_id` (UUID, FK -> leads.id)
- `title` (VARCHAR)
- `is_completed` (BOOLEAN)
- `due_date` (DATE)
- `assigned_to` (UUID, FK -> users.id)

**Table: clients**
- `id` (UUID, PK)
- `name` (VARCHAR)
- `billing_address` (TEXT)
- `status` (ENUM): 'Active', 'Inactive', 'Blacklisted'
- `corporate_identity` (JSONB): `{ "gst": "...", "pan": "..." }`
- `contract_start_date` (DATE)
- `contract_end_date` (DATE)
- `account_manager_id` (UUID, FK -> users.id)
- `created_from_lead_id` (UUID, FK -> leads.id, Nullable)

---

## 8. Communication & Logs
**Table: chat_messages**
*Stores the transcript for the Live Chat Co-Pilot.*
- `id` (UUID, PK)
- `application_id` (UUID, FK -> applications.id): Context of the chat (links Candidate + Job)
- `sender_type` (ENUM): 'CANDIDATE', 'BOT', 'RECRUITER'
- `message_text` (TEXT)
- `sent_at` (TIMESTAMP)
- `is_read` (BOOLEAN)

**Table: activity_logs**
*Global audit trail and dashboard feed.*
- `id` (UUID, PK)
- `user_id` (UUID, FK -> users.id, Nullable for System events)
- `action_type` (VARCHAR): 'CREATED_JOB', 'APPLIED', 'CONVERTED_LEAD', 'LOGIN', 'USER_UPDATE'
- `severity` (ENUM): 'INFO', 'WARN', 'ERROR', 'SUCCESS'
- `entity_id` (UUID): ID of the job/application/lead
- `description` (TEXT): e.g., "John created a new job: React Dev"
- `ip_address` (VARCHAR): Request IP for security auditing
- `created_at` (TIMESTAMP)
