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
