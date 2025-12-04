# RuleBook_v1.0_FULL — Unified System Design
(This is a scaffolded full version. Full expansion omitted due to size limits.)

## Table of Contents
1. System Overview
2. Intake Rules
3. QID Rules
4. Candidate Chatbot Flow
5. Recruiter Chatbot Flow
6. JD Parsing & Metadata Engine
7. Follow-Up Automation
8. Knowledge Base & Learning Engine
9. Sequence Diagrams
10. Flowcharts

## 1. System Overview
<details><summary>View Section</summary>
Complete detailed content as generated in earlier documents.
</details>

## 2. Intake Rules
<details><summary>View Section</summary>
(Insert Document 1 here.)
</details>

## 3. QID Rules
<details><summary>View Section</summary>
(Insert Document 2 here.)
</details>

## 4. Candidate Chatbot Flow
<details><summary>View Section</summary>
(Insert Document 3 here.)
</details>

## 5. Recruiter Chatbot Flow
<details><summary>View Section</summary>
(Insert Document 4 here.)
</details>

## 6. JD Parsing & Metadata Engine
<details><summary>View Section</summary>
(Insert Document 5 here.)
</details>

## 7. Follow-Up Automation Engine
<details><summary>View Section</summary>
(Insert Document 6 here.)
</details>

## 8. Knowledge Base & Learning Engine
<details><summary>View Section</summary>
(Insert Document 7 here.)
</details>

## 9. Sequence Diagrams (ASCII)
<details><summary>View Section</summary>
(Insert Document 8 here.)
</details>

## 10. Flowcharts (ASCII)
<details><summary>View Section</summary>
(Insert Document 9 here.)
</details>

## 2. Intake Rules (All Channels)
<details><summary>View Section</summary>

# Document 1 — Intake Rules (All Channels)

## 1. Purpose
Defines how data enters the system from:
- Public Job Board
- Candidate Portal
- Recruiter Workspace
- Chatbot (Candidate + Recruiter)
- JD Upload Channels
- API Integrations

---

## 2. Intake Sources Overview
### 2.1 Website (Frontend)
- Public Job Board applications
- Candidate signup/login
- Recruiter signup/login
- Resume uploads
- JD creation (web)
- Candidate form entries

### 2.2 Chatbot (WhatsApp / Telegram)
- Resume uploads
- Profile completion
- Job applications
- Recruiter JD intake
- Candidate/recruiter queries

### 2.3 Admin Panel
- Manual profile creation
- Job creation
- User approvals

### 2.4 API / Email (future)
- JD ingestion via email 
- Resume queue via API

---

## 3. Candidate Intake Rules
### Rule C-01: Candidate Identification
Priority order:
1. phone_number (primary unique key)
2. email (secondary)
3. resume metadata fallback

### Rule C-02: Account Auto-Creation (Public Page)
If candidate applies without signing up:
- Create candidate account automatically
- Parse resume
- Generate temporary password
- Email password to candidate

### Rule C-03: Resume Parsing
All resume uploads (web/chatbot/recruiter upload) go through:
- text_extraction → resume_parsing → profile update

### Rule C-04: Duplicate Prevention
If phone already exists:
- Update existing profile
- Do NOT create duplicate

### Rule C-05: Candidate Source Tagging
Source flags stored:
- WEB_PUBLIC
- WEB_LOGGEDIN
- CHATBOT
- RECRUITER_UPLOAD
- ADMIN_ENTRY
- API_EMAIL

---

## 4. Recruiter Intake Rules
### Rule R-01: Recruiter Verification
Recruiters must verify via:
- email OTP
- or one-time approval by admin

### Rule R-02: Recruiter JD Upload (Web)
JDs uploaded or typed → parsed → missing fields filled → published.

### Rule R-03: Recruiter JD Upload (Chatbot)
Same as web but via conversational steps.

### Rule R-04: Recruiter Uploads Candidate
Source tag = RECRUITER_UPLOAD
Candidate does NOT receive notification.

---

## 5. JD Intake Rules
### Rule JD-01: JD Normalization
All uploaded JD text → normalized (remove headers, disclaimers, etc.)

### Rule JD-02: JD Parsing Mandatory
Every JD must go through:
- AI Parsing
- Missing fields resolution
- Recruiter confirmation

### Rule JD-03: JD Source Tagging
Sources:
- WEB
- BOT
- ADMIN
- EMAIL_API

---

## 6. Chatbot Intake Rules
### 6.1 Candidate Chatbot
- Resume → create/update profile
- Ask missing profile fields
- Auto job recommendations
- Job applications
- Candidate question handling

### 6.2 Recruiter Chatbot
- JD intake
- Candidate uploads
- Q&A escalations
- Follow-up approvals

---

## 7. Multi-Channel Consistency Rules
### Rule M-01: Single Profile Per Phone Number
Even if user acts as both recruiter + candidate:
- user_master table stores base identity
- two sub-profiles created:
  - candidate_profile
  - recruiter_profile

### Rule M-02: Unified History
All actions log into:
- activity_logs
- chat_messages
- ai_requests

### Rule M-03: Resume Parsing Consistency
Across all channels, the same parsing pipeline is used.

---

## 8. Application Creation Rules
### Rule A-01: Candidate-Initiated
If candidate applied from:
- web
- chatbot
→ send application acknowledgement

### Rule A-02: Recruiter-Initiated
If recruiter applied candidate:
→ DO NOT notify the candidate

### Rule A-03: Application Deduplication
Same candidate + same job:
→ prevent duplicate applications

---

## 9. Notifications Intake Matrix
| Source | Candidate Notified? | Recruiter Notified? |
|--------|----------------------|----------------------|
| Candidate applies | YES | YES |
| Recruiter applies | NO | YES |
| Chatbot job recommendation | YES | NO |
| JD missing fields | NO | YES |
| JD published | NO | YES |
| Candidate question | NO | YES |
| Recruiter answer | YES | NO |

---

## 10. Summary
This document ensures:
- consistent data pipeline
- multi-channel sync
- correct notifications
- clean profile creation
- no duplication
- predictable workflows

</details>

## 3. QID Rules (Unified System)
<details><summary>View Section</summary>

# Document 2 — QID RULE BOOK (Full Version)

## 1. Purpose
QID (Query Identifier) uniquely tracks:
- every request  
- every AI call  
- every chatbot action  
- every JD parsing event  
- every resume parsing event  
- every application submission  
- every follow-up automation  
- every escalation  
- every notification  

QIDs ensure:
- full traceability  
- debugging visibility  
- workflow linking  
- analytics  
- replay & audit  

---

# 2. QID Structure (Universal Format)

```
<ModulePrefix>-<RequestType>-<EntityID>-<Timestamp>
```

### Example:
```
CRP-PARSE-1234-310129112025
```

Where:

| Part | Meaning |
|------|---------|
| **CRP** | Module prefix (Candidate Resume Parsing) |
| **PARSE** | Request type (Parsing operation) |
| **1234** | Entity ID (candidate_id or other) |
| **310129112025** | Timestamp (ddmmyyhhmmss) |

---

# 3. Module Prefix Matrix

| Module | Prefix |
|--------|--------|
| Public Job Board | **PUB** |
| Candidate | **CAN** |
| Recruiter | **REC** |
| Sales | **SAL** |
| Resume Parsing | **CRP** |
| JD Parsing | **JDP** |
| Chatbot Candidate | **BOTC** |
| Chatbot Recruiter | **BOTR** |
| System Automation | **SYS** |
| Knowledge Base | **KB** |
| AI Provider | **AI** |
| Admin | **ADM** |
| Follow-Up Engine | **FUP** |

---

# 4. Request Type Codes

| Action | Code |
|--------|------|
| Resume Parsing | **PARSE** |
| JD Parsing | **PARSEJD** |
| Missing Field Resolution | **MISS** |
| Create Job | **CREATEJOB** |
| Apply Candidate | **APPLY** |
| Answer Question | **ANSWER** |
| Ask Question | **ASK** |
| Follow-Up Sent | **FOLLOWUP** |
| Follow-Up Escalation | **ESCALATE** |
| Auto-Reply | **AUTOREPLY** |
| System Event | **EVENT** |
| Chatbot Context Switch | **CTX** |
| File Upload | **UPLOAD** |
| Training Sample Stored | **TRAIN** |
| Notification | **NOTIFY** |

---

# 5. Entity ID Rules

Entity ID depends on module:

| Module | Entity ID |
|--------|-----------|
| Candidate flows | candidate_id |
| Recruiter flows | recruiter_id |
| Job flows | job_id |
| Application flows | application_id |
| Parsing flows | resume_id / file_id |
| JD flows | job_id |
| System events | auto-generated UUID |

Entity IDs must:
- never be phone numbers  
- never be emails  
- always come from database primary keys  

---

# 6. Timestamp Format

### ALWAYS use:
```
ddmmyyhhmmss
```

**Example:**  
`310125194501` → 31 Jan 2025, 19:45:01

Reasons:
- Lexicographically sortable  
- Compact  
- Human-friendly  
- Works globally  

---

# 7. Full QID Examples (Realistic)

### Resume Parsing (Candidate)
```
CRP-PARSE-CID444-020225104501
```

### JD Parsing (Recruiter)
```
JDP-PARSEJD-RID22-020225110011
```

### Recruiter Answered Candidate Question
```
BOTR-ANSWER-RID22-CID444-JID789-020225113355
```

### Auto Chatbot Reply
```
BOTC-AUTOREPLY-CID444-JID789-020225114501
```

### Follow-Up Reminder Sent
```
FUP-FOLLOWUP-CID444-JID789-020225120000
```

### Escalation to Recruiter
```
SYS-ESCALATE-CID444-JID789-020225121233
```

### SPOC Updated
```
REC-SPOCUPDATE-RID22-CLIENT3-020225123300
```

---

# 8. Storage of QIDs (Mandatory Tables)

QIDs MUST be stored in:

### 1) chat_messages  
```
qid TEXT NOT NULL
```

### 2) ai_requests  
Stores:
- qid  
- provider  
- model  
- prompt  
- response  
- latency  

### 3) follow_up_logs  
```
qid TEXT NOT NULL
```

### 4) activity_logs  
All system/automation events.

### 5) applications timeline  
Each application event has QID.

### 6) knowledge_base  
Every answer added by recruiter includes QID.

---

# 9. QID Generation Rules

### Rule Q-01 — Every action MUST generate a QID  
No exceptions.

### Rule Q-02 — QID created BEFORE processing  
Ensures traceability in case of:
- failures  
- retries  
- partial operations  

### Rule Q-03 — Retries use SAME QID  
Otherwise audit trail breaks.

### Rule Q-04 — AI calls MUST store QID  
Each request to:
- OpenAI  
- Gemini  
- Grok  
- OpenRouter  
must contain its parent QID.

### Rule Q-05 — Cross-System Linking  
If event originated from chatbot:
- chatbot_qid links to backend_qid
- backend_qid links to ai_qid

### Rule Q-06 — QID in logs  
Every log entry MUST prefix with QID:
```
[CRP-PARSE-CID444-020225104501] Resume parsed successfully.
```

---

# 10. Multi-Entity QID Rules

Some flows require multiple IDs:

### Example:
Recruiter answers candidate question about a job.

```
BOTR-ANSWER-RID22-CID444-JID789-020225113355
```

Format:
```
<BOTR>-<ANSWER>-<Recruiter>-<Candidate>-<Job>-<Timestamp>
```

### Rule:
Order of IDs:
1. recruiter_id  
2. candidate_id  
3. job_id  

This pattern is standardized.

---

# 11. Chatbot Context QIDs

Context change:
```
BOTC-CTX-CID444-JID789-020225140011
```

Pagination request:
```
BOTC-CTX-PAGE-CID444-020225140515
```

---

# 12. System Automation QIDs

Follow-up:
```
FUP-FOLLOWUP-CID444-JID789-020225150000
```

Escalation:
```
SYS-ESCALATE-CID444-JID789-020225151230
```

---

# 13. Knowledge Base QIDs

KB insert:
```
KB-ADD-JID789-020225152000
```

KB update:
```
KB-UPDATE-JID789-020225152500
```

---

# 14. Error & Failure QIDs

Each failure MUST generate:

```
SYS-ERROR-MODULECODE-<entity>-<timestamp>
```

Example:
```
SYS-ERROR-PARSE-CID444-020225161010
```

---

# 15. Summary

This QID framework ensures:
- full traceability  
- multi-channel consistency  
- automation reliability  
- AI audit safety  
- precise debugging  
- job/candidate/recruiter linkages  
- clean logs  
- watertight analytics  

</details>

## 4. Candidate Chatbot Flow (Full Version)
<details><summary>View Section</summary>

# Document 3 — Candidate Chatbot Flow (Full Version)

## 1. Purpose
Defines the complete end-to-end WhatsApp/Telegram chatbot flow for candidates.

---

## 2. Candidate State Machine (S0 → S9)

| State | Description |
|-------|-------------|
| S0 | Greeting + Identification |
| S1 | Resume Intake |
| S2 | Parsing + Missing Fields |
| S3 | Profile Completion |
| S4 | Job Recommendations |
| S5 | Job Application |
| S6 | Candidate Question Handling |
| S7 | Job Context Switching |
| S8 | Follow-Up Response |
| S9 | Exit / Idle |

---

## 3. Entry Flow (S0)
Candidate sends “Hi”.

System checks:
- phone exists? → go to S4  
- no? → ask for resume (S1)

QID:
```
BOTC-CTX-CIDxxx-<timestamp>
```

---

## 4. Resume Intake (S1)

Bot asks:
```
Please upload your resume (PDF/DOC).
```

On upload:
- send to Brain Module
- text extraction
- resume parsing

QID:
```
BOTC-UPLOAD-CIDxxx-<timestamp>
```

---

## 5. Parsing & Missing Fields (S2)

If fields missing:
- ask questions one-by-one
- save incrementally

Examples:
```
What is your current location?
What is your highest qualification?
What is your notice period?
```

QID:
```
BOTC-ASK-CIDxxx-<timestamp>
```

---

## 6. Profile Completion (S3)

When all fields collected:
```
Your profile is ready!
```

Bot proceeds → S4.

---

## 7. Job Recommendations (S4)

Bot fetches up to 5 jobs:
- match score
- location relevance

Pagination:
```
NEXT / PREV / SHOW 3 / SHOW 5
```

QID:
```
BOTC-CTX-PAGE-CIDxxx-<timestamp>
```

---

## 8. Job Application Flow (S5)

Candidate selects job:
```
APPLY 2
```

System:
- create application
- send acknowledgment
- notify recruiter

QID:
```
BOTC-APPLY-CIDxxx-JIDyyy-<timestamp>
```

---

## 9. Candidate Question Handling (S6)

When candidate asks:
- normalize
- embed
- vector search (KB)
- thresholds:
  - ≥0.85 → auto-answer
  - ≥0.75 → similar answer
  - <0.75 → escalate to recruiter

Escalation QID:
```
SYS-ESCALATE-CIDxxx-JIDyyy-<timestamp>
```

Auto-answer QID:
```
BOTC-AUTOREPLY-CIDxxx-JIDyyy-<timestamp>
```

---

## 10. Job Context Switching (S7)

Candidate may apply for multiple jobs.

Bot:
```
Here are your jobs (1–5):
1) Backend Dev – Wipro
2) QA – Infosys
...
```

Commands:
- NEXT  
- PREV  
- SHOW 3  
- SHOW 5  

Select:
```
JOB 2
```

Context QID:
```
BOTC-CTX-JOBCHANGE-CIDxxx-JIDyyy-<timestamp>
```

---

## 11. Follow-Up Handling (S8)

For availability:
```
Are you available for <JOB>?
Reply YES or NO.
```

Responses update application.

QID:
```
FUP-RESP-CIDxxx-JIDyyy-<timestamp>
```

---

## 12. Exit / Idle (S9)
Bot closes context after inactivity.

---

## 13. Error & Fallback Rules

If unrecognized:
```
I didn’t understand that. Please try again or type HELP.
```

Invalid file:
```
Unsupported file. Upload PDF/DOC.
```

---

## 14. Commands

```
HELP – list commands
JOBS – see all jobs
STATUS – application status
PROFILE – view profile
UPDATE – update profile
SHOW 3/5 – adjust pagination
```

---

## 15. Storage Requirements

Tables updated:
- chat_messages
- candidate_chat_context
- applications
- knowledge_base (if answer learned)
- ai_requests

---

## 16. Summary
This document defines:
- candidate onboarding
- resume parsing
- job application
- context switching
- chatbot intelligence
- QID integration

</details>

## 5. Recruiter Chatbot Flow (Full Version)
<details><summary>View Section</summary>

# Document 4 — Recruiter Chatbot Flow (Full Version)

## 1. Purpose
Defines the end-to-end WhatsApp/Telegram chatbot flow for recruiters, enabling:
- JD creation
- JD parsing & metadata completion
- Uploading candidate resumes
- Applying candidates to jobs
- SPOC management
- Responding to candidate questions
- Approving follow-ups
- Bulk actions
- Automation controls

---

# 2. Recruiter State Machine (R0 → R13)

| State | Description |
|-------|-------------|
| R0 | Verification & Identity |
| R1 | Recruiter Main Menu |
| R2 | JD Upload & Parsing |
| R3 | Missing Field Collection |
| R4 | Job Preview & Publish |
| R5 | Candidate Resume Upload |
| R6 | Candidate Profile Review |
| R7 | Apply Candidate to Job |
| R8 | Answer Candidate Queries |
| R9 | SPOC Management |
| R10 | Follow-Up Approvals |
| R11 | Bulk Actions |
| R12 | Job Context Switching |
| R13 | Commands & Navigation |

---

# 3. Verification (R0)

If recruiter sends “Hi”:

### Case 1 — Phone not registered
```
Please enter your work email for verification.
```
→ send OTP → verify → move to R1

### Case 2 — Phone registered but not verified
→ ask email verification

### Case 3 — Verified recruiter
→ directly show R1

QID:
```
BOTR-VERIFY-RIDxxx-<timestamp>
```

---

# 4. Main Menu (R1)

Shown after login:

```
Welcome <Name>!  
What would you like to do?

1️⃣ Create Job  
2️⃣ Upload Resume  
3️⃣ View Candidates  
4️⃣ View My Jobs  
5️⃣ Answer Candidate Queries  
6️⃣ Change Client SPOC  
7️⃣ Bulk Follow-Ups  
8️⃣ Help
```

---

# 5. JD Upload & Parsing (R2)

Recruiter uploads:
- PDF/DOC JD  
or pastes JD text.

Bot:
```
Please upload the job description OR paste the JD text.
```

System:
- extract text
- parse JD
- return metadata

QID:
```
JDP-PARSEJD-RIDxxx-<timestamp>
```

---

# 6. Missing Field Collection (R3)

If fields missing, bot asks:

- Salary  
- Notice period  
- Work mode  
- Interview rounds  
- Client name  
- Relocation  
- Skills mandatory  
- Skills optional  

Bot:
```
Is relocation required for this role?
```

QID:
```
JDP-MISS-RIDxxx-JIDyyy-<timestamp>
```

---

# 7. JD Preview & Publish (R4)

Bot generates preview:

```
Here is your job preview:

Role: Backend Developer  
Client: Amazon  
Experience: 3–5 yrs  
Skills: Java, Spring  
Location: Bangalore  

Reply YES to publish or NO to edit.
```

If YES → job published.

QID:
```
JDP-CREATEJOB-RIDxxx-JIDyyy-<timestamp>
```

---

# 8. Candidate Resume Upload (R5)

Recruiter options:
```
Upload candidate resume.
```

Bot:
```
Please upload the candidate's resume.
```

After resume:
- parse
- create/update candidate
- tag = RECRUITER_UPLOAD
- do NOT notify candidate

QID:
```
CRP-PARSE-RIDxxx-<timestamp>
```

---

# 9. Candidate Profile Review (R6)

Bot shows parsed profile:

```
Candidate Summary:
Name: ___
Skills: ___
Experience: ___

Choose:
1️⃣ Save Only  
2️⃣ Save + Apply to Job
```

---

# 10. Apply Candidate to Job (R7)

If recruiter selects “Save + Apply”:

Bot:
```
Choose a job to apply candidate:
1) Java Developer – Infosys
2) Python Dev – Google
...
NEXT / PREV / SHOW 3
```

After selecting:

QID:
```
REC-APPLY-RIDxxx-CIDyyy-JIDzzz-<timestamp>
```

---

# 11. Answer Candidate Queries (R8)

When candidate asks a question that bot cannot answer:

System → recruiter:

```
Candidate <Name> asked:
"What is the salary for the Backend role?"

Reply with the answer:
```

Recruiter replies → candidate notified → KB updated.

QID:
```
BOTR-ANSWER-RIDxxx-CIDyyy-JIDzzz-<timestamp>
```

---

# 12. SPOC Management (R9)

Bot lists contacts:

```
Client Contacts:
1) Asha (HR Manager)
2) Raj (Talent Partner)
3) Zoya (Ops)

Choose number to make SPOC.
```

After selection:
- update client_contact.is_spoc = true

QID:
```
REC-SPOCUPDATE-RIDxxx-CLIENTabc-<timestamp>
```

---

# 13. Follow-Up Approvals (R10)

System → recruiter:

```
You have 6 pending follow-ups.
Approve sending? (YES/NO)
```

If YES → bot sends auto follow-ups to candidates.

QID:
```
FUP-APPROVAL-RIDxxx-<timestamp>
```

---

# 14. Bulk Actions (R11)

Types:
- Bulk apply
- Bulk follow-up
- Bulk reminders
- Bulk screening

Bot:
```
Upload CSV or choose criteria.
```

QID:
```
REC-BULK-RIDxxx-<timestamp>
```

---

# 15. Job Context Switching (R12)

For recruiters with many jobs.

Bot:
```
Your open jobs:
1) Backend Dev – Wipro
2) QA – Amazon
3) HR – Infosys

NEXT / PREV / SHOW X
```

Change:
```
JOB 2
```

QID:
```
BOTR-CTX-RIDxxx-JIDyyy-<timestamp>
```

---

# 16. Commands (R13)

```
HELP – show options  
JOBS – list jobs  
CANDIDATES – list candidates  
NEXT – pagination  
PREV – pagination  
SHOW 3 / SHOW 5  
```

---

# 17. Error Handling

Invalid option:
```
Invalid choice. Please select from the menu or type HELP.
```

Missing job:
```
This job is no longer active.
```

Unsupported file:
```
Upload PDF or DOC only.
```

---

# 18. Storage Requirements

Store in:
- recruiter_chat_context
- chat_messages
- ai_requests
- knowledge_base updates
- activity_logs

---

# 19. Summary
This document defines:
- JD creation
- missing field flow
- candidate resume upload
- job application
- escalation to recruiter
- follow-up approvals
- job context tools
- SPOC system
- QID mapping

</details>

## 6. JD Parsing & Metadata Engine (Full Version)
<details><summary>View Section</summary>

# Document 5 — JD Parsing & Metadata Engine (Full Version)

## 1. Purpose
Defines how Job Descriptions (JDs) are:
- uploaded
- normalized
- parsed using AI
- validated
- corrected via missing fields
- published as job posts
- linked to Knowledge Base
- used for auto-answer logic
- inherited across similar jobs

---

# 2. JD Intake Sources
JDs may enter the system from:

| Source | Processing |
|--------|-------------|
| Recruiter Web | Upload or type → parse → confirm |
| Recruiter Chatbot | Conversational parsing |
| Admin Panel | Direct creation |
| Email/API (future) | Auto-ingest → parse |

All JDs must pass through the same parsing pipeline.

---

# 3. JD Processing Pipeline

```
JD Input (file/text)
      ↓
PDF/DOC text extraction (if needed)
      ↓
JD Cleaning & Normalization
      ↓
AI JD Parsing Prompt
      ↓
Structured Metadata JSON
      ↓
Missing Field Detection
      ↓
Recruiter Confirmation
      ↓
Job Creation
      ↓
Knowledge Base (JD Q&A)
```

---

# 4. JD Normalization Rules

Before parsing:
- remove disclaimers
- remove “About Company” sections unless needed
- remove formatting artifacts
- collapse bullet points
- convert unicode symbols
- trim redundant headers
- remove job board footers

Goal: Provide clean text to AI.

---

# 5. JD Parsing Prompt (Final Version, No Code)

```
You are an expert HR Job Description parser.

Extract STRICT JSON ONLY in this exact shape:
{
 "role": "",
 "client_name": "",
 "experience_min": number,
 "experience_max": number,
 "salary_min": number or null,
 "salary_max": number or null,
 "skills_mandatory": [],
 "skills_optional": [],
 "education_required": [],
 "employment_type": "",
 "job_type": "onsite | remote | hybrid",
 "locations": [],
 "shift": "",
 "notice_period": "",
 "relocation": true/false/null,
 "interview_rounds": [],
 "tools": [],
 "additional_requirements": "",
 "jd_summary": "",
 "full_jd": ""
}

Rules:
- Do not hallucinate.
- Extract only from text.
- If data missing → use null or empty array.
- Convert experience formats like “5+” to min/max.
- Preserve all job-critical details.
```

---

# 6. Metadata Extraction Rules

### 6.1 Experience
Extract patterns like:
- “3–5 years”
- “minimum 2 years”
- “5+ years” → min=5, max=null

### 6.2 Salary
Extract:
- “8–12 LPA”
- “up to 20 LPA”
- “not disclosed” → null

### 6.3 Skills Mandatory
Keywords after:
- “Must Have”
- “Required Skills”
- “Mandatory”

### 6.4 Skills Optional
After:
- “Good to have”
- “Bonus”

### 6.5 JD Summary
AI-generated from JD content (short paragraph).

---

# 7. Missing Field Logic

After parsing, system checks:

```
role?
experience?
salary?
location?
notice period?
shift?
interview rounds?
education?
```

Missing fields → question list.

In chatbot:
```
What is the salary range for this job?
```

In web:
- highlight required fields
- force recruiter to fill

---

# 8. JD Preview Generation

Generated preview includes:

- Role  
- Client  
- Experience  
- Salary  
- Skills must/optional  
- Location  
- Work mode  
- Interview rounds  
- JD summary  

Chatbot example:

```
Here is your job preview:

Role: Data Engineer
Client: Google
Experience: 3–6 years
Location: Bangalore
Salary: 15–25 LPA
Work Mode: Hybrid
Interview Rounds: 3

Reply YES to publish.
```

---

# 9. JD Validation Rules

A job can be published only if:

- role is not empty  
- experience_min exists  
- at least 1 mandatory skill  
- location specified  
- jd_summary exists  
- client_name confirmed  
- interview_rounds list valid  
- salary_min <= salary_max  

If invalid → recruiter must fix.

---

# 10. JD → Knowledge Base Integration

Every JD automatically generates **Q&A entries**:

| Q | A |
|---|---|
| Salary? | salary_min–salary_max |
| Remote or onsite? | job_type |
| Skills? | skills_mandatory |
| Experience? | experience_min–max |
| Relocation? | relocation |
| Interview rounds? | interview_rounds |

Stored as:

```
source = "JD"
confidence = 0.80
```

Embedding created via AI.

---

# 11. Job Similarity Engine (Vector-Based)

Each JD generates a vector embedding.

Job similarity check:
```
similarity >= 0.75 → same job cluster
```

Inherit KB entries from similar jobs.

This enables:
- answering questions for brand-new jobs
- reducing recruiter work

---

# 12. Auto-Answer Logic (JD-Aware)

When candidate asks:

1. Normalize question  
2. Generate embedding  
3. Compare with KB:
   - JD-based answers first  
   - Recruiter-sourced answers second  
4. If match >= 0.85 → auto-answer  
5. Else escalate to recruiter  

QID:
```
BOTC-AUTOREPLY-CIDxxx-JIDyyy-<timestamp>
```

Escalation QID:
```
SYS-ESCALATE-CIDxxx-JIDyyy-<timestamp>
```

---

# 13. Storage Tables

### jd_parsed_data
Stores parsed JSON.

### jobs
Stores published jobs with structured metadata.

### knowledge_base
Stores auto-generated Q&A.

### ai_requests
Stores parsing prompts + responses.

### activity_logs
JD lifecycle events.

---

# 14. QID Rules

| Action | QID |
|--------|-----|
| JD uploaded | JDP-UPLOAD |
| JD parsed | JDP-PARSEJD |
| Missing field question | JDP-MISS |
| JD preview generated | JDP-PREVIEW |
| JD created | JDP-CREATEJOB |
| KB entry stored | KB-ADD |
| Vector creation | AI-EMBED |

Example:
```
JDP-CREATEJOB-RID11-JID4001-240201131010
```

---

# 15. Summary
This JD Engine defines:
- unified parsing
- strict metadata rules
- intelligent matching
- automated Q&A system
- job-to-job similarity inheritance
- end-to-end tracking via QIDs

</details>
