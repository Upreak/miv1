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
