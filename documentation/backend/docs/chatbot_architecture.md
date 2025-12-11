# Chatbot Module Architecture

## Overview

The Chatbot Module is a comprehensive AI-powered conversational system designed to handle candidate onboarding, prescreening, recruiter workflows, and job matching across multiple platforms (WhatsApp, Telegram, Web).

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Clients                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   WhatsApp UI   │  │  Telegram UI    │  │   Web UI     │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────┬─────────────────┬─────────────────┬───────────┘
              │                 │                 │
              ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway / Router                     │
└─────────────┬─────────────────┬─────────────────┬───────────┘
              │                 │                 │
              ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    Chatbot Module                           │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                Controller Layer                       │  │
│  │  ┌─────────────────┐  ┌─────────────────┐            │  │
│  │  │   Chat Router   │  │   Controllers   │            │  │
│  │  └─────────────────┘  └─────────────────┘            │  │
│  └─────────────┬─────────────────┬───────────────────────┘  │
│                │                 │                          │
│  ┌─────────────▼─────────────────▼───────────────────────┐  │
│  │              Service Layer                            │  │
│  │  ┌─────────────────┐  ┌─────────────────┐            │  │
│  │  │   Workflow      │  │   Session       │            │  │
│  │  │   Engine        │  │   Manager       │            │  │
│  │  └─────────────────┘  └─────────────────┘            │  │
│  │  ┌─────────────────┐  ┌─────────────────┐            │  │
│  │  │   Prescreening  │  │   Profile       │            │  │
│  │  │   Service       │  │   Update        │            │  │
│  │  └─────────────────┘  └─────────────────┘            │  │
│  │  ┌─────────────────┐  ┌─────────────────┐            │  │
│  │  │   JD KB         │  │   Export        │            │  │
│  │  │   Service       │  │   Service       │            │  │
│  │  └─────────────────┘  └─────────────────┘            │  │
│  │  ┌─────────────────┐  ┌─────────────────┐            │  │
│  │  │   Recruiter     │  │   Rules         │            │  │
│  │  │   Outreach      │  │   Engine        │            │  │
│  │  └─────────────────┘  └─────────────────┘            │  │
│  └─────────────┬─────────────────┬───────────────────────┘  │
│                │                 │                          │
│  ┌─────────────▼─────────────────▼───────────────────────┐  │
│  │              Repository Layer                         │  │
│  │  ┌─────────────────┐  ┌─────────────────┐            │  │
│  │  │   Session       │  │   Message       │            │  │
│  │  │   Repository    │  │   Repository    │            │  │
│  │  └─────────────────┘  └─────────────────┘            │  │
│  └─────────────┬─────────────────┬───────────────────────┘  │
│                │                 │                          │
└────────────────▼─────────────────▼───────────────────────────┘
              │                 │
              ▼                 ▼
┌─────────────────────────────────────────────────────────────┐
│                      Database Layer                         │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │ chatbot_sessions│  │chatbot_messages │                  │
│  └─────────────────┘  └─────────────────┘                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │job_prescreen_   │  │prescreen_answers│  │   job_faq    │ │
│  │  questions      │  └─────────────────┘  └──────────────┘ │
│  └─────────────────┘                                         │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Controller Layer

#### Chat Router (`chat_router.py`)
- **Purpose**: Handles all incoming HTTP requests and routes them to appropriate controllers
- **Endpoints**:
  - `POST /chatbot/start-session` - Start a new chatbot session
  - `POST /chatbot/message` - Process incoming messages
  - `GET /chatbot/session/{session_id}` - Get session details
  - `PUT /chatbot/session/{session_id}/state` - Update session state
  - `POST /applications/{application_id}/prescreen-answers` - Submit prescreen answers
  - `POST /jobs/{job_id}/prescreen-questions` - Create prescreen questions
  - `GET /jobs/{job_id}/prescreen-questions` - Get prescreen questions
  - `POST /jobs/{job_id}/suggest-questions` - Suggest questions via AI
  - `POST /jobs/{job_id}/outreach` - Trigger candidate outreach
  - `POST /jobs/{job_id}/export-candidates` - Export candidate data

#### Controller (`controller.py`)
- **Purpose**: High-level orchestration of chatbot operations
- **Responsibilities**:
  - Session management coordination
  - Message processing coordination
  - Response formatting and error handling

### 2. Service Layer

#### Workflow Engine (`workflow_engine.py`)
- **Purpose**: Main dispatcher and state transitions for conversations
- **States**: INITIALIZED, ONBOARDING, COLLECTING_INFO, PROCESSING, WAITING_FOR_INPUT, COMPLETED, ERROR
- **Responsibilities**:
  - State management and transitions
  - Intent analysis
  - Step-by-step processing
  - Context management

#### Session Manager (`state_manager.py`)
- **Purpose**: Manages conversation state and session storage
- **Features**:
  - In-memory session storage with TTL
  - Thread-safe operations
  - Redis backend support
  - Session persistence and cleanup

#### Prescreening Service (`prescreening_service.py`)
- **Purpose**: Handles prescreen question processing and scoring
- **Responsibilities**:
  - Validate prescreen answers
  - Compute match scores
  - Update application records
  - Manage prescreen answer storage

#### Profile Update Service (`profile_update_service.py`)
- **Purpose**: Manages candidate profile updates with freshness tracking
- **Features**:
  - Freshness checking (configurable days)
  - Selective profile updates
  - Timestamp management
  - Audit logging

#### JD KB Service (`jd_kb_service.py`)
- **Purpose**: Job knowledge base for answering candidate questions
- **Features**:
  - FAQ storage and retrieval
  - Keyword-based question matching
  - Fuzzy matching for similar questions
  - Escalation to recruiters

#### Export Service (`export_service.py`)
- **Purpose**: Generates Excel exports and ZIP files for client submissions
- **Features**:
  - Excel file generation with predefined headers
  - Resume collection and bundling
  - JSON summary generation
  - Email notifications

#### Recruiter Outreach Service (`recruiter_outreach_service.py`)
- **Purpose**: Manages recruiter-candidate communication
- **Features**:
  - Candidate outreach automation
  - Response relay to candidates
  - WhatsApp webhook integration
  - Template-based messaging

#### Rules Engine (`rules_engine.py`)
- **Purpose**: Validation and normalization of user inputs
- **Validators**:
  - Email validation
  - Phone number normalization
  - Number range validation
  - Choice validation
  - Skill normalization
  - Match score computation

### 3. Repository Layer

#### Session Repository (`session_repository.py`)
- **Purpose**: Data access for session management
- **Operations**: Create, Read, Update, Delete sessions

#### Message Repository (`message_repository.py`)
- **Purpose**: Data access for message logging
- **Operations**: Log messages, retrieve conversation history

### 4. Database Models

#### Core Tables

1. **chatbot_sessions**
   - Session state management
   - User identification across platforms
   - Context storage

2. **chatbot_message_logs**
   - Conversation history
   - Message metadata
   - Performance tracking

3. **job_prescreen_questions**
   - Prescreen question definitions
   - Validation rules
   - Question weights

4. **prescreen_answers**
   - Candidate responses
   - Answer validation results
   - Scoring data

5. **job_faq**
   - Job-specific knowledge base
   - Question-answer pairs
   - Keyword matching

## Configuration

### Environment Variables

```bash
# Chatbot settings
FRESHNESS_DAYS=30
EXPORT_TMP_PATH=/data/exports
QUARANTINE_BASE_PATH=/data/quarantine
WHATSAPP_OUTBOUND_WEBHOOK_URL=
EMAIL_SENDER_SMTP_HOST=
EMAIL_SENDER_SMTP_PORT=587
EMAIL_SENDER_SMTP_USERNAME=
EMAIL_SENDER_SMTP_PASSWORD=
EMAIL_SENDER_SMTP_USE_TLS=true
```

### Default QIDs

The system includes 20 default prescreen questions:

1. `ps_current_ctc` - Current CTC
2. `ps_expected_ctc` - Expected CTC
3. `ps_notice_period` - Notice period
4. `ps_total_experience` - Total experience
5. `ps_key_skills` - Key technical skills
6. `ps_has_offers` - Other job offers
7. `ps_preferred_location` - Preferred work locations
8. `ps_current_location` - Current location
9. `ps_availability` - Interview availability
10. `ps_best_time_to_contact` - Best contact time
11. `ps_work_mode` - Work mode preference
12. `ps_relocate` - Relocation willingness
13. `ps_shift_preference` - Shift preference
14. `ps_visa_status` - Work authorization
15. `ps_certifications` - Relevant certifications
16. `ps_education` - Education level
17. `ps_industry_experience` - Industry experience
18. `ps_management_experience` - Management experience
19. `ps_salary_negotiable` - Salary negotiability
20. `ps_reason_for_change` - Job change reason

## Excel Export Format

The export service generates Excel files with the following header:

```
["Application ID","Candidate Name","Email","Phone","Total Experience","Current CTC (LPA)","Expected CTC (LPA)","Notice Period","Current Location","Preferred Location","Skills","JD Match Score","Must-Have-Failed","PreScreen_Summary_JSON","Recruiter Notes","Submitted At"]
```

## State Machine

```
INITIALIZED → ONBOARDING → COLLECTING_INFO → PROCESSING → COMPLETED
    ↓           ↓              ↓                ↓
    └───────────┴──────────────┴────────────────┘
                                    ↓
                                 ERROR → INITIALIZED
```

## Integration Points

### External Services

1. **WhatsApp Business API**
   - Outbound webhook for notifications
   - Message delivery tracking

2. **Email Service (SMTP)**
   - Export notifications
   - Outreach communications

3. **AI Providers (OpenRouter, Gemini, Groq)**
   - Question suggestions
   - Response generation
   - Match analysis

### Database Integration

1. **Existing Tables Extended**
   - `applications` - Added prescreening fields
   - `candidate_profiles` - Added freshness tracking

2. **New Tables**
   - Chatbot-specific session and message storage
   - Prescreening question and answer storage
   - Job knowledge base storage

## Security Considerations

1. **Session Security**
   - UUID-based session identifiers
   - TTL-based session expiration
   - Secure context storage

2. **Data Validation**
   - Input sanitization via Rules Engine
   - SQL injection prevention
   - XSS protection for web interfaces

3. **Access Control**
   - Role-based access (Candidate/Recruiter)
   - API authentication
   - Sensitive data encryption

## Performance Considerations

1. **Caching**
   - Redis for session storage
   - Question cache for frequently asked questions
   - Match score caching

2. **Database Optimization**
   - Indexes on frequently queried fields
   - Partitioning for large message logs
   - Connection pooling

3. **Async Processing**
   - Background tasks for exports
   - Async message processing
   - Non-blocking I/O operations

## Monitoring and Logging

1. **Application Metrics**
   - Response times
   - Error rates
   - Session duration
   - User engagement

2. **Business Metrics**
   - Prescreen completion rates
   - Match score distributions
   - Export frequencies
   - Outreach effectiveness

3. **Log Levels**
   - DEBUG: Detailed execution flow
   - INFO: Business events and state changes
   - WARNING: Validation failures and edge cases
   - ERROR: System failures and exceptions

## Deployment Considerations

1. **Environment Setup**
   - Database migrations
   - Redis configuration
   - SMTP setup
   - WhatsApp API integration

2. **Scaling**
   - Horizontal scaling for chatbot services
   - Database read replicas
   - CDN for static assets

3. **Backup and Recovery**
   - Session data backup
   - Message log archival
   - Configuration backup

## Future Enhancements

1. **AI Improvements**
   - Advanced NLP for better intent recognition
   - Sentiment analysis for user experience
   - Personalized response generation

2. **Integration Expansion**
   - Additional messaging platforms
   - Video interview integration
   - Assessment platform integration

3. **Analytics Enhancement**
   - Predictive analytics for candidate success
   - Advanced reporting dashboards
   - A/B testing for conversation flows