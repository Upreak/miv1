

# Business Logic & Backend Rules

## 1. Job Board Domain

### A. Job Creation & Validation Rules
1.  **Salary Validation:** `max_salary` must be greater than or equal to `min_salary`. Negative values are rejected.
2.  **Location formatting:** Job Locations must be validated against a standard ISO city/country list to ensure searchability.
3.  **Expiry Logic:**
    - Jobs status 'Sourcing' auto-expires to 'Closed' after 45 days unless renewed.
    - 'Draft' jobs are deleted after 90 days of inactivity.
4.  **Slug Generation:** 
    - `slug_url` must be unique. Pattern: `[job-title]-[client-name]-[random-4-char]`.
    - If a duplicate exists, append a numeric suffix.
    - AI-generated slugs must be sanitized to remove special characters (only alphanumeric and hyphens).

### B. Application Constraints
1.  **Duplicate Application Prevention:**
    - A Candidate cannot apply to the *same* `job_id` twice within 6 months.
    - Check composite key: `(candidate_email, job_id)`.
    - **Error:** Return `409 Conflict` - "You have already applied for this position."
2.  **Internal Candidate Check:**
    - If `candidate_email` exists in the system but for a different job, link the existing profile to the new application instead of creating a duplicate record.
3.  **Cooldown Period:**
    - If a candidate was `Rejected` by a Client, they cannot apply to *other* roles for the same Client for 30 days (optional config per client).

---

## 2. Recruitment Process (ATS)

### A. Multi-Job Candidate Tracking
*A single candidate can be in process for multiple jobs simultaneously.*

1.  **Profile Independence:** 
    - Editing a candidate's Phone Number in one application MUST update it for ALL active applications (because it's the same person).
    - Editing `match_score` or `status` MUST only affect the specific Job Application context.
2.  **Conflict Resolution:**
    - If a candidate moves to status `Joined` for Job A, the system should trigger a warning: "Candidate is active in Job B (Interview). Withdraw from Job B?"
    - Do not auto-withdraw without Recruiter confirmation.
3.  **AI Parsing Context:**
    - When AI parses a resume, it matches against the **Profile** first.
    - Then, it runs the **Match Logic** against the specific **Job Description** to create an entry in the `applications` table with a unique score.

### B. Co-Pilot & Automation Logic
*Rules governing the AI Agent's interaction with candidates.*

1.  **Automation State Machine:**
    - `New`: Default state upon parsing/application.
    - `Contacting...`: System is sending initial outreach (email/SMS).
    - `Awaiting Reply`: Outreach sent, no response yet.
    - `Live Chat`: Candidate responded, session is active.
    - `Intervention Needed`: AI confidence low OR candidate requested human.
    - `Completed`: Bot finished screening successfully.
    - `Declined`: Candidate not interested.
2.  **Intervention Rules:**
    - If a Recruiter clicks "Intervene & Take Over", the `sender_type` switches from 'BOT' to 'RECRUITER'.
    - The AI agent must strictly **PAUSE** generation while Recruiter mode is active.
    - Only clicking "Resume Automation" returns control to the Bot.
3.  **Triggering Alerts:**
    - If a sentiment analysis of a candidate reply is negative or confused, auto-switch `automation_status` to `Intervention Needed` and create an **Action Queue** item.

### C. Candidate Management & Approval
1.  **Recruiter Approved Override:**
    - Toggling `is_recruiter_approved` to TRUE should visually highlight the candidate card (e.g., Purple badge).
    - It does **not** change the AI Match Score, but it should prioritize the candidate in sort order (always show Approved on top).
2.  **Follow-up Constraints:**
    - Setting a `next_follow_up_date` must auto-create a hidden Calendar event or Action Queue reminder.
    - `follow_up_status` is independent of the main ATS `status` (allows granular tracking like "No Show" without rejecting the application immediately).

---

## 3. Search & Matching Logic

### A. Search Query Processing
1.  **Keyword Normalization:** "ReactJS", "React.js", "React" -> treated as single token "REACT".
2.  **Location Radius:**
    - Exact match gets 100% weight.
    - Within 50km gets 80% weight.
    - Different location but `ready_to_relocate=true` gets 50% weight.

### B. AI Match Scoring
1.  **Weighted Formula:**
    - Skills Match: 60%
    - Experience Match: 20% (Target +/- 2 years is ideal).
    - Location/Relocation: 10%
    - Budget Fit: 10%
2.  **Threshold:**
    - Candidates with score < 40 are auto-tagged `Low Relevance` but NOT rejected automatically (Human in loop).

---

## 4. Action Queue Generation Rules
*Logic for populating the Recruiter's "My Action Queue".*

1.  **New High Match:**
    - **Trigger:** A new candidate applies/is sourced with Match Score > 85%.
    - **Action Item:** Type `NEW_MATCHES`, Priority `High`.
2.  **Chat Intervention:**
    - **Trigger:** `automation_status` becomes `Intervention Needed`.
    - **Action Item:** Type `INTERVENTION_NEEDED`, Priority `High`.
3.  **Stalled Workflow:**
    - **Trigger:** Candidate in `Screening` stage for > 5 days with no activity.
    - **Action Item:** Type `NO_RESPONSE`, Priority `Medium`.

---

## 5. Sales CRM Logic

### A. Lead Management
1.  **Mandatory Fields:** `company_name` is the minimum requirement to create a Lead.
2.  **Contact Info:** While not mandatory for creation, `contact_person`, `email`, and `phone` should be populated as early as possible.
3.  **State Persistence:**
    - Notes and Activity Logs are immutable (cannot be deleted, only appended).

### B. Lead to Client Conversion
1.  **Data Propagation:**
    - When converting, the Lead's `company_name` becomes the Client's `name`.
    - Lead's `contact_person`, `email`, `phone` become the Client's **Primary Contact (SPOC)**.
2.  **Enrichment Requirement:**
    - A Lead cannot become a 'Active' Client without a valid `billing_address`.
    - The conversion process must prompt the user to input the Address and optional Corporate Details (GST/PAN).
3.  **Status Handling:**
    - Upon successful conversion, Lead status updates to `Converted`.
    - The Lead record is preserved for reporting (Win Rate analysis).

---

## 6. Standardized Error Handling

### HTTP Status Codes
| Code | Meaning | Use Case |
|:---|:---|:---|
| `400` | Bad Request | Validation failure (e.g., Missing email, Salary min > max). |
| `401` | Unauthorized | Missing or invalid JWT token. |
| `403` | Forbidden | Authenticated, but role doesn't permit action (e.g., Recruiter trying to delete Client). |
| `404` | Not Found | Resource ID does not exist. |
| `409` | Conflict | Duplicate Entry (Email exists, Application exists). |
| `422` | Unprocessable | Logical error (e.g., Moving candidate from 'New' directly to 'Joined'). |
| `429` | Rate Limited | Too many AI calls or API requests. |
| `500` | Server Error | Unhandled exception or Database connection failure. |

---

## 7. Admin & Security

### A. User Management
1.  **Admin Protection:**
    - A user with `role='ADMIN'` cannot delete their own account.
    - There must always be at least one Active Admin in the system.
2.  **User Lifecycle:**
    - Users are created with `status='Active'` by default.
    - Setting `status='Inactive'` immediately revokes API access (middleware check).
    - Password Reset: Admins can trigger a reset link, but cannot view old passwords (hashing).
3.  **Email Uniqueness:**
    - `email` must be unique across the `users` table.

### B. Audit Logging
1.  **Critical Events:** The following events MUST generate an entry in `activity_logs` with `severity='WARN'` or `severity='ERROR'`:
    - Failed Login Attempts (Brute force detection).
    - User Role Changes (Privilege escalation).
    - Bulk Data Export (Data exfiltration risk).
2.  **Log Retention:**
    - Audit logs are immutable and retained for a minimum of 90 days.

### C. System Settings (Feature Flags)
1.  **Dynamic Toggling:**
    - Changing a setting in `system_settings` (e.g., `ENABLE_AI_PARSING` = `false`) must take effect immediately without server restart.
    - This allows Admins to degrade performance gracefully during outages (e.g., disable AI if API rate limit hits).
