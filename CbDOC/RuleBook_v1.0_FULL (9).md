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

## 7. Follow-Up Automation Engine (Full Version)
<details><summary>View Section</summary>

# Document 6 — Follow-Up Automation Engine (Full Version)

## 1. Purpose
This engine handles all automated communication with candidates and recruiters:
- availability checks  
- follow-up reminders  
- interview reminders  
- recruiter approval workflows  
- escalation rules  
- no-response handling  
- status-driven messaging  
- quiet-hour controls  
- anti-spam enforcement  

It operates independently but is triggered by QID-based events.

---

# 2. Follow-Up Categories

### 2.1 Candidate Follow-Ups
- Availability confirmation  
- Missing details  
- Interview reminders  
- Offer acceptance  
- Document submission  
- Joining reminders  

### 2.2 Recruiter Follow-Ups
- Candidate availability updates  
- Escalations (unanswered questions)  
- Approval requests  
- Job status changes  

### 2.3 System Follow-Ups
- Timed checks  
- Retry rules  
- Escalate to SPOC  
- Activity log updates  

---

# 3. Trigger Types

### T1 — Time-based
- every 24 hours for pending follow-ups  
- configurable intervals  

### T2 — Event-based
Examples:
- candidate applied  
- recruiter answered  
- candidate updated profile  

### T3 — Escalation-based
If unanswered after X retries.

---

# 4. Follow-Up Timing Matrix

| Follow-Up Type | First Attempt | Second | Third | Escalation |
|----------------|---------------|--------|--------|------------|
| Availability Check | Immediate | +6 hours | +24 hours | Recruiter |
| Interview Reminder | -24 hours | -3 hours | — | — |
| Offer Acceptance | Immediate | +24 hours | +48 hours | Recruiter + SPOC |
| Document Submission | Immediate | +24 hours | +72 hours | Recruiter |
| General Query | Immediate | +6 hours | +24 hours | Recruiter |

---

# 5. Candidate Communication Templates

### Availability:
```
Are you available for the <Role> position with <Client>?  
Reply YES or NO.
```

### Interview Reminder:
```
Reminder: Your interview for <Role> is scheduled at <Time>.  
Good luck!
```

### Offer Acceptance:
```
You have received an offer for <Role> at <Client>.  
Please reply ACCEPT or REJECT.
```

---

# 6. Recruiter Communication Templates

### Escalation:
```
Candidate <Name> has not responded for <Role>.  
Please check manually.
```

### Approval Request:
```
We are ready to send follow-up messages to <X> candidates.  
Reply APPROVE or SKIP.
```

---

# 7. Retry Rules

### Rule R-01 — Max 3 attempts
Candidate follow-ups do not retry beyond 3.

### Rule R-02 — Recruiter approvals do not retry
If not answered → logged as skipped.

### Rule R-03 — Escalation after final attempt
Escalated to:
- recruiter → candidate queries  
- SPOC → offer or joining issues  

---

# 8. Quiet Hour Rules

Follow-ups MUST NOT be sent:
- between 9:00 PM and 9:00 AM (configurable)  
- except interview reminders within 3 hours  

Queue messages and deliver after quiet hours.

---

# 9. Anti-Spam Logic

Prevent:
- duplicate reminders  
- continuous nagging  
- loops  

Rules:
- one message per category at a time  
- wait period enforced  
- escalation handled only once  

---

# 10. Follow-Up State Machine

```
          ┌──────────────┐
          │   Pending     │
          └───────┬──────┘
                  ▼
            First Attempt
                  │
                  ▼
            Second Attempt
                  │
                  ▼
            Third Attempt
                  │
         ┌────────┴─────────┐
         ▼                  ▼
     Responded          Not Responded
                          │
                          ▼
                    Escalated
```

---

# 11. Application Status-Driven Messages

### Status → Message

| Status | Message |
|--------|---------|
| Shortlisted | “You are shortlisted.” |
| Interview Scheduled | “Interview set for <time>.” |
| Offered | “You have received an offer.” |
| Rejected | “Thank you for applying.” |

---

# 12. Follow-Up Logs

Table: **follow_up_logs**

Stores:
- qid  
- candidate_id  
- job_id  
- attempt_count  
- next_follow_up_at  
- status  
- escalation_flag  

---

# 13. QID Mapping

| Event | QID |
|--------|------|
| Follow-up sent | FUP-FOLLOWUP |
| Follow-up response | FUP-RESP |
| Escalation | FUP-ESCALATE |
| Recruiter approval | FUP-APPROVAL |
| System retry | FUP-RETRY |

Examples:
```
FUP-FOLLOWUP-CID444-JID22-020225090000
FUP-ESCALATE-CID444-JID22-020225180000
```

---

# 14. Completion Rules

A follow-up cycle ends when:
- candidate responds  
- recruiter intervenes  
- 3 retries complete  
- job closed  
- candidate withdrawn  

---

# 15. Summary

This engine:
- automates all follow-ups  
- reduces recruiter workload  
- ensures timely responses  
- handles escalation safely  
- maintains anti-spam and quiet-hour rules  
- ties everything together using QIDs  

</details>

## 8. Knowledge Base & Learning Engine (Full Version)
<details><summary>View Section</summary>

# Document 7 — Knowledge Base & Learning Engine (Full Version)

## 1. Purpose
This module powers intelligent Q&A handling across:
- Candidate chatbot  
- Recruiter chatbot  
- JD-based question answering  
- System auto-replies  
- Escalations  
- Learning from recruiter corrections  

It enables your platform to get smarter over time.

---

# 2. Knowledge Base Architecture

The KB has 3 layers:

### Layer 1 — JD-Derived Knowledge  
Generated automatically from the JD metadata.

### Layer 2 — Recruiter-Sourced Knowledge  
Created when recruiter answers questions.

### Layer 3 — Historical Knowledge (Learning Engine)  
Generated from repeated patterns in conversations.

Each entry contains:
- question  
- answer  
- job_id (optional)  
- recruiter_id (optional)  
- confidence_score  
- source (`JD`, `RECRUITER`, `LEARNING`)  
- embedding vector  
- timestamp  
- QID of origin  

---

# 3. When Knowledge is Added

### A) At JD Creation  
System adds answers to standard questions:
- salary  
- experience  
- location  
- skills  
- remote/onsite  
- interview rounds  
- relocation  
- education  

Example entry:
```
Q: What is the salary?
A: 12–18 LPA
source: JD
confidence: 0.80
```

### B) When Recruiter Answers Candidate  
Bot stores new knowledge:

```
Q: Is relocation mandatory?
A: Yes, it is mandatory for this role.
source: RECRUITER
confidence: 0.95
```

### C) When Similar Q&A Appears Repeatedly  
If a pattern appears:
- same question appears 3+ times  
- similar recruiter answers  
→ promote to “LEARNING” knowledge

---

# 4. Knowledge Base Table Structure

### Table: `knowledge_base`

| Field | Type |
|--------|---------|
| id | UUID |
| job_id | nullable UUID |
| recruiter_id | nullable UUID |
| question | TEXT |
| answer | TEXT |
| source | ENUM(JD, RECRUITER, LEARNING) |
| confidence | FLOAT |
| embedding | VECTOR(1536) |
| created_at | TIMESTAMP |
| updated_at | TIMESTAMP |
| qid | TEXT |

### Table: `knowledge_history`
Stores change tracking for corrections.

### Table: `kb_embeddings`
Stores reusable raw vector data.

---

# 5. Question Normalization Pipeline

Before matching:

```
lowercase
remove punctuation
lemmatize
remove stopwords
semantic normalization
```

Example:
```
"How much salary they will pay?"
→ "salary range"
```

---

# 6. Answer Retrieval Algorithm

### Step 1 — Normalize question  
### Step 2 — Generate embedding  
### Step 3 — Compare with KB entries  
### Step 4 — Similarity scoring  
### Step 5 — Apply thresholds:

| Condition | Action |
|-----------|--------|
| sim ≥ 0.85 | Auto-answer |
| 0.75–0.84 | Suggest closest match |
| sim < 0.75 | Escalate to recruiter |

QID for auto-answer:
```
BOTC-AUTOREPLY-CIDxxx-JIDyyy-<timestamp>
```

QID for escalation:
```
SYS-ESCALATE-CIDxxx-JIDyyy-<timestamp>
```

---

# 7. Multi-Job Learning & Inheritance

### Rule LJ-01 — Clustered Jobs Share Knowledge  
If jobs have similarity ≥ 0.75:
- share JD-based Q&A  
- share recruiter Q&A  
- improve with each new answer  

### Rule LJ-02 — Recruiter-Added Q&A Inherits to Cluster  
If recruiter answers once → future similar roles also get answer.

### Rule LJ-03 — Brand Consistency  
Questions about:
- company  
- hiring process  
- culture  
inherit across ALL jobs under the same client.

---

# 8. Recruiter Override Rules

Recruiter answer ALWAYS overrides:
- JD knowledge  
- System knowledge  
- Learning knowledge  

KB updated with:
- `source = RECRUITER`
- `confidence = 0.95`

---

# 9. Correction Flow

If recruiter says:
```
“Salary is actually 10–14 LPA.”
```

System:
- updates KB
- stores old in history
- recalculates embedding
- spreads correction across similar jobs

QID:
```
KB-UPDATE-RIDxxx-JIDyyy-<timestamp>
```

---

# 10. Learning Engine Rules

### LE-01 — Pattern Detection  
If similar answers appear repeatedly:
- cluster  
- weigh  
- promote to learning entry  

### LE-02 — Model Improvement  
Chat history becomes training dataset for local embedding tuning.

### LE-03 — Time Decay  
Old answers slowly lose weight unless reconfirmed.

### LE-04 — Invalidation  
If recruiter corrects → learning reset.

---

# 11. Safety Guardrails

### SG-01 — No Hallucinations  
If no KB match → escalate, never guess.

### SG-02 — Sensitive Questions Blocked  
Examples:
- salary negotiations  
- complaints  
- internal feedback  
→ routed to recruiter only.

### SG-03 — Answer Length Limit  
Max 400 chars in chatbot.

---

# 12. QID Rules for KB Engine

| Event | QID |
|--------|------|
| KB added | KB-ADD |
| KB updated | KB-UPDATE |
| KB auto-learning | KB-LEARN |
| Embedding generation | AI-EMBED |
| Retraining event | KB-TRAIN |

Example:
```
KB-ADD-JID455-020225133000
```

---

# 13. Storage & Consistency Requirements

- all KB updates stored with QIDs  
- KB entries versioned  
- all embeddings stored for audit  
- AI requests stored in ai_requests  
- recruiter corrections logged in activity_logs  

---

# 14. Knowledge Answer Lifecycle

```
JD created
   ↓
JD Q&A generated
   ↓
Candidate asks question
   ↓
Match with KB
   ↓
Auto-answer OR escalate
   ↓
Recruiter responds
   ↓
KB updated
   ↓
Learning Engine retrains
   ↓
Better answers in future
```

---

# 15. Summary

This engine ensures:
- Accurate auto-answering  
- Continuous learning  
- JD-aware responses  
- Recruiter override control  
- High relevance answers  
- Full traceability via QIDs  

It is the intelligence core of the chatbot.

</details>

## 9. Sequence Diagrams (ASCII — Full Version)
<details><summary>View Section</summary>

# Document 8 — Sequence Diagrams (Full ASCII Edition)

Below are complete ASCII-based sequence diagrams for Candidate, Recruiter, JD, Parsing, KB, and Follow-Up automation flows.

All diagrams are designed to be readable in:
- GitHub
- VSCode
- Notion
- Markdown renderers

---

# 1. Candidate Onboarding Flow (S0 → S4)

```
Candidate        Chatbot         Backend        Brain Module       DB
    |              |                |                |             |
    |---"Hi"------>|                |                |             |
    |              |--check phone-->|
    |              |                |--lookup------->|--query----->|
    |              |                |<--result-------|<--data------|
    |              |<--ask resume---|
    |---upload resume-------------->|                |             |
    |              |                |--store resume->|
    |              |                |--parse req---->|--extract-->|
    |              |                |                |--parse---->|
    |              |                |<--parsed-------|             |
    |              |<--missing Qs---|                |             |
    |---answers-------------------->|                |             |
    |              |                |--update------->|
    |              |<--Profile Ready|
```

---

# 2. Resume Parsing Flow

```
Frontend/Chatbot
      |
      v
File Upload ---------> Backend
                         |
                         v
                  PDF/DOC Extractor
                         |
                         v
                    Parsed Text
                         |
                         v
                 Resume Parsing AI
                         |
                         v
                Structured Candidate JSON
                         |
                         v
                Save to candidate_profile
```

---

# 3. Candidate Job Recommendation Flow

```
Candidate -> Chatbot -> Backend -> Matching Engine -> DB
    |           |          |            |              |
    |--"Jobs?"->|          |            |              |
    |           |--fetch-> |            |--top 5------>|
    |           |<--list---|            |<--jobs-------|
    |<--jobs----|          |            |              |
```

Pagination:

```
Candidate --"NEXT"--> Chatbot --CTX UPDATE--> Backend
```

---

# 4. Candidate Job Apply Flow

```
Candidate       Chatbot        Backend         DB
    |              |              |              |
    |--"APPLY 2"-->|
    |              |--verify job->|
    |              |              |--create app->|
    |              |<--success----|
    |<--Applied----|
```

---

# 5. Candidate Question → Auto-Answer or Escalation

```
Candidate        Chatbot       Backend      KB Engine     Recruiter
    |               |             |             |             |
    |--question---->|             |             |             |
    |               |--normalize->|             |             |
    |               |             |--embed----->|             |
    |               |             |<--match------|            |
    |               |             |             |             |
if match >= 0.85:
    |               |<--auto-answer--------------             |
else:
    |               |--escalate----------------------------->|
    |               |                                        |
    |               |<-------------recruiter answer----------|
    |<----------------auto-notify----------------------------|
```

---

# 6. Recruiter JD Creation (Web + Chatbot)

```
Recruiter    Chatbot/Web     Backend      Brain JD Parser       DB
    |            |              |                |               |
    |--Upload---->|            |                |               |
    |            |--store----->|                |               |
    |            |              |--parse JD---->|--LLM--------->|
    |            |              |<--parsed-------|               |
    |            |<--Missing fields--------------               |
    |--answers----------------->|                |               |
    |            |              |--update------->|               |
    |            |<--Preview----|                |               |
    |--"YES"---->|             |                |               |
    |            |              |--Create Job-->|--insert------>|
    |            |<--Success----|                |               |
```

---

# 7. Recruiter Resume Upload → Save + Apply

```
Recruiter     Chatbot       Backend       Brain Parser       DB
    |            |              |                |            |
    |--upload--->|              |                |            |
    |            |--store------>|                |            |
    |            |              |--parse resume->|--LLM------>|
    |            |              |<--parsed--------|            |
    |            |<--Summary----|                |            |
    |--"2.Save+Apply"---------->|                |            |
    |            |              |--fetch jobs--->|--jobs----->|
    |            |<--jobs-------|                |            |
    |--"JOB 2"----------------->|                |            |
    |            |              |--apply-------->|--insert--->|
    |            |<--Success----|                |            |
```

---

# 8. SPOC Assignment Flow

```
Recruiter -> Chatbot -> Backend -> DB
    |          |          |        |
    |--"SPOC"->|          |        |
    |          |--list--->|        |
    |          |<--names--|        |
    |--pick---->|          |        |
    |          |--update->|--save->|
    |<--done----|          |        |
```

---

# 9. Follow-Up Engine (Automation)

```
Scheduler -----> Follow-Up Engine -----> Backend -----> Chatbot -----> Candidate
    |                    |                   |              |              |
    |--tick------------->|                   |              |              |
                         |--pull pending---->|              |              |
                         |<--list------------|              |              |
                         |--send FUP-------->|--send------>|              |
                         |                   |             |--deliver---->|
                         |--retry logic---------------------------------->|
                         |--escalate (if needed)------------------------->Recruiter
```

---

# 10. QID Propagation Diagram

```
Action ---> Chatbot ---> Backend ---> AI Provider ---> DB Logs
   |           |            |             |             |
   |--QID----->|--carry---->|--store----->|--store----->|
                metadata       ai_requests   audit_logs
```

---

# 11. Multi-Channel Sync Diagram

```
 Web UI       Chatbot       Backend        DB
   |            |              |            |
   |--event---->|              |            |
   |            |--event------>|            |
   |            |              |--update--->|
   |<--sync-----|<--sync-------|            |
```

---

# 12. Application Lifecycle

```
Apply → Screening → Shortlist → Interview → Offer → Join → Close
```

Detailed:

```
Candidate → Apply
Backend → Screening Engine
Recruiter → Shortlist
Bot → Interview Confirmation
Recruiter → Finalize Offer
Bot → Offer Acceptance
Recruiter → Joining Confirmation
System → Close Application
```

---

# 13. Summary

These diagrams provide:
- complete end-to-end clarity  
- multi-module visibility  
- AI + automation understanding  
- QID propagation view  
- channel interactions  

All diagrams are ASCII-safe and compatible with all documentation systems.

</details>

## 10. Flowcharts (ASCII — Full Version)
<details><summary>View Section</summary>

# Document 9 — Flowcharts (Full ASCII Edition)

This section includes all major flowcharts for:
- Candidate onboarding
- Resume parsing
- JD creation
- Recruiter workflows
- AI engines
- Knowledge Base learning
- Follow-up automation
- Chatbot routing logic
- Account creation

All diagrams are pure ASCII and markdown-friendly.

---

# 1. Candidate Resume Intake Flowchart

```
      ┌─────────────┐
      │ Candidate Hi │
      └───────┬─────┘
              ▼
     ┌──────────────────┐
     │ Phone in system? │
     └───────┬──────────┘
        Yes   │    No
              │
     ▼        ▼
Existing   Ask Resume
Profile     Upload
              │
              ▼
        Resume Uploaded
              │
              ▼
        Parse Resume
              │
              ▼
     Missing Fields?
         │     │
        No     Yes
         │       │
         ▼       ▼
  Profile Ready  Ask Questions
                    │
                    ▼
               Save Answers
                    │
                    ▼
              Profile Ready
```

---

# 2. Candidate Job Recommendation Flow

```
     ┌──────────────────┐
     │ Profile Complete │
     └───────┬──────────┘
             ▼
      Fetch Matches
             │
             ▼
      Top 5 Jobs Found?
         │        │
        Yes       No
         │         │
         ▼         ▼
     Show Jobs   Inform "No Jobs"
         │
         ▼
   NEXT / PREV / SHOW X
```

---

# 3. Candidate Application Flow

```
      ┌────────────┐
      │ APPLY <n>  │
      └──────┬─────┘
             ▼
     Validate Job ID
             │
             ▼
   Create Application
             │
             ▼
 Notify Recruiter + Candidate
             │
             ▼
         Completed
```

---

# 4. Candidate Question Answering Flow

```
     ┌──────────────────────┐
     │ Candidate Question?  │
     └──────────┬───────────┘
                ▼
        Normalize Text
                │
                ▼
       Generate Embedding
                │
                ▼
         KB Similarity
                │
     ┌──────────┼───────────┐
     ▼          ▼           ▼
Auto-Answer   Suggest     Escalate
(sim>=0.85) (0.75–0.84)  (sim<0.75)
```

---

# 5. Recruiter JD Creation Flowchart

```
     ┌──────────────┐
     │ Upload JD    │
     └──────┬───────┘
            ▼
  Extract & Normalize JD
            │
            ▼
      AI JD Parsing
            │
            ▼
   Any Missing Fields?
         │     │
        Yes    No
         │       │
         ▼       ▼
   Ask Recruiter Fill
         │       │
         ▼       ▼
     Update JD Metadata
            │
            ▼
      Generate Preview
            │
            ▼
    Recruiter Approves?
         │       │
        Yes      No
         │        │
         ▼        ▼
    Publish Job   Edit JD
```

---

# 6. Recruiter Resume Upload → Save or Save+Apply

```
     ┌────────────────┐
     │ Upload Resume  │
     └───────┬────────┘
             ▼
        Parse Resume
             │
             ▼
     Show Candidate Summary
             │
   ┌─────────┼─────────┐
   ▼         ▼         ▼
Save Only  Save+Apply  Cancel
             │
             ▼
       List Recruiter Jobs
             │
             ▼
         Apply to Job
```

---

# 7. SPOC Assignment Flow

```
       ┌───────────┐
       │ SPOC Menu │
       └─────┬─────┘
             ▼
     List Client Contacts
             │
             ▼
    Recruiter Selects SPOC
             │
             ▼
     Update is_spoc = true
```

---

# 8. Follow-Up Automation Flow

```
         ┌──────────────┐
         │ Scheduler Tick│
         └──────┬───────┘
                ▼
         Load Pending FUPs
                │
                ▼
       Attempt Follow-Up #n
                │
                ▼
    ┌───────────┼────────────┐
    ▼           ▼            ▼
Responded   Retry Allowed   Escalate
              (n < 3)
```

---

# 9. Knowledge Base Update Flow

```
   Candidate Question
           │
           ▼
         Match KB
           │
   ┌───────┼─────────┐
   ▼       ▼         ▼
 Auto     Suggest   Escalate
           │          │
           ▼          ▼
      Recruiter Answer
           │
           ▼
      Store in KB
           │
           ▼
    Update Embeddings
```

---

# 10. AI Fallback Flow (Multi-Provider)

```
           ┌───────────────┐
           │ AI Call Start │
           └──────┬────────┘
                  ▼
         Provider #1 (Primary)
                  │
     ┌────────────┼────────────┐
     ▼             ▼            ▼
 Success     Provider Error   Timeout
     │            │             │
     ▼            ▼             ▼
Return OK   Switch Provider   Switch Provider
                  │
                  ▼
        Provider #2 Attempt
```

---

# 11. Account Creation Logic (Public vs Logged-In)

```
      ┌──────────────┐
      │ Apply for Job │
      └──────┬────────┘
             ▼
  Logged-In Candidate?
        │       │
       Yes      No
        │        │
        ▼        ▼
 Use Existing  Create New
 Candidate     Candidate
   Profile       Profile
```

---

# 12. Chatbot Routing Engine Flow

```
     ┌───────────────┐
     │ Incoming Msg  │
     └───────┬───────┘
             ▼
      Identify User
             │
       Candidate? Recruiter?
       │          │
       ▼          ▼
Candidate Bot   Recruiter Bot
       │          │
       ▼          ▼
Route to Respective State Machine
```

---

# 13. System-Wide QID Generation Flow

```
    ┌────────────────────┐
    │ Any System Action? │
    └─────────┬──────────┘
              ▼
       Generate QID
              │
              ▼
 Store QID in Logs + DB
              │
              ▼
 Process Action
```

---

# 14. Summary

These flowcharts visually represent:
- core system logic  
- decision trees  
- user journeys  
- AI & automation flows  
- routing logic  
- parsing pipelines  
- follow-up sequences  
- multi-channel behaviors  

They serve as the visual backbone of the entire RuleBook.

</details>
