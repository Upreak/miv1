# Chatbot API Documentation

## Overview

This document describes all the API endpoints for the Chatbot Module, including request/response formats and examples.

## Base URL

```
https://your-domain.com/api/v1
```

## Authentication

All endpoints require authentication via JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Candidate Endpoints

### 1. Start Session

Start a new chatbot session for a user.

**Endpoint:** `POST /chatbot/start-session`

**Request Body:**
```json
{
  "user_id": "user-123",
  "platform": "whatsapp",
  "platform_user_id": "whatsapp-user-123",
  "user_role": "candidate"
}
```

**Response (200 OK):**
```json
{
  "session_id": "session-123",
  "user_id": "user-123",
  "platform": "whatsapp",
  "user_role": "candidate",
  "created_at": "2025-01-01T00:00:00"
}
```

**Error Response (400 Bad Request):**
```json
{
  "detail": "Invalid platform specified"
}
```

### 2. Process Message

Send a message to the chatbot and receive a response.

**Endpoint:** `POST /chatbot/message`

**Request Body:**
```json
{
  "session_id": "session-123",
  "message": "Hello, I want to apply for a job",
  "message_type": "text"
}
```

**Response (200 OK):**
```json
{
  "session_id": "session-123",
  "response": "Hello! I'd be happy to help you apply for a job. Let me start by collecting some information about you.",
  "next_action": "collect_basic_info",
  "timestamp": "2025-01-01T00:00:00"
}
```

### 3. Get Session

Retrieve session details.

**Endpoint:** `GET /chatbot/session/{session_id}`

**Response (200 OK):**
```json
{
  "session_id": "session-123",
  "user_id": "user-123",
  "platform": "whatsapp",
  "user_role": "candidate",
  "state": "onboarding",
  "context": {
    "current_skill": "onboarding",
    "step": 1,
    "collected_data": {}
  },
  "created_at": "2025-01-01T00:00:00",
  "updated_at": "2025-01-01T00:00:00"
}
```

### 4. Update Session State

Update the state and context of a session.

**Endpoint:** `PUT /chatbot/session/{session_id}/state`

**Request Body:**
```json
{
  "state": "onboarding_completed",
  "context": {
    "current_skill": "resume_intake",
    "step": 1,
    "collected_data": {
      "name": "John Doe",
      "email": "john@example.com"
    }
  }
}
```

**Response (200 OK):**
```json
{
  "session_id": "session-123",
  "state": "onboarding_completed",
  "context": {
    "current_skill": "resume_intake",
    "step": 1,
    "collected_data": {
      "name": "John Doe",
      "email": "john@example.com"
    }
  },
  "updated_at": "2025-01-01T00:00:00"
}
```

### 5. Submit Prescreen Answers

Submit answers to prescreen questions for an application.

**Endpoint:** `POST /applications/{application_id}/prescreen-answers`

**Request Body:**
```json
{
  "answers": {
    "ps_current_ctc": "10.5",
    "ps_expected_ctc": "15.0",
    "ps_notice_period": "60",
    "ps_total_experience": "5",
    "ps_key_skills": ["Python", "FastAPI", "SQLAlchemy"]
  },
  "update_global_profile": true
}
```

**Response (200 OK):**
```json
{
  "application_id": "app-123",
  "jd_match_score": 85,
  "must_have_failed": false,
  "answers_processed": 5,
  "global_profile_updated": true,
  "timestamp": "2025-01-01T00:00:00"
}
```

## Recruiter Endpoints

### 1. Create Prescreen Questions

Create prescreen questions for a job.

**Endpoint:** `POST /jobs/{job_id}/prescreen-questions`

**Request Body:**
```json
[
  {
    "qid": "ps_current_ctc",
    "question_text": "What is your current CTC?",
    "type": "number",
    "required": true,
    "must_have": true,
    "weight": 10,
    "validation_rule": "min:0,max:100"
  }
]
```

**Response (200 OK):**
```json
{
  "job_id": "job-123",
  "questions_created": 1,
  "timestamp": "2025-01-01T00:00:00"
}
```

### 2. Get Prescreen Questions

Retrieve prescreen questions for a job.

**Endpoint:** `GET /jobs/{job_id}/prescreen-questions`

**Response (200 OK):**
```json
[
  {
    "qid": "ps_current_ctc",
    "question_text": "What is your current CTC (LPA)?",
    "type": "number",
    "required": true,
    "must_have": true,
    "weight": 10,
    "validation_rule": "min:0,max:100"
  },
  {
    "qid": "ps_expected_ctc",
    "question_text": "What is your expected CTC (LPA)?",
    "type": "number",
    "required": true,
    "must_have": true,
    "weight": 10,
    "validation_rule": "min:0,max:100"
  }
]
```

### 3. Suggest Prescreen Questions

Get AI-suggested prescreen questions based on job description.

**Endpoint:** `POST /jobs/{job_id}/suggest-questions`

**Response (200 OK):**
```json
{
  "job_id": "job-123",
  "suggested_questions": [
    {
      "qid": "ps_current_ctc",
      "question_text": "What is your current CTC (LPA)?",
      "type": "number",
      "required": true,
      "must_have": true,
      "weight": 10
    }
  ],
  "timestamp": "2025-01-01T00:00:00"
}
```

### 4. Trigger Candidate Outreach

Send outreach messages to candidates for a job.

**Endpoint:** `POST /jobs/{job_id}/outreach`

**Request Body:**
```json
{
  "candidate_ids": ["candidate-123", "candidate-456"]
}
```

**Response (200 OK):**
```json
{
  "job_id": "job-123",
  "candidates_contacted": 2,
  "outreach_initiated": true,
  "timestamp": "2025-01-01T00:00:00"
}
```

### 5. Export Candidates

Create an export job for candidates matching a job.

**Endpoint:** `POST /jobs/{job_id}/export-candidates`

**Request Body:**
```json
{
  "application_ids": ["app-123", "app-456"],
  "client_spoc_id": "spoc-123",
  "include_resumes": true,
  "include_json": true
}
```

**Response (200 OK):**
```json
{
  "export_job_id": "export-123",
  "job_id": "job-123",
  "applications_included": 2,
  "status": "queued",
  "download_url": null,
  "created_at": "2025-01-01T00:00:00"
}
```

### 6. Get Export Status

Check the status of an export job.

**Endpoint:** `GET /exports/{export_job_id}`

**Response (200 OK):**
```json
{
  "export_job_id": "export-123",
  "job_id": "job-123",
  "applications_included": 2,
  "status": "completed",
  "download_url": "https://your-domain.com/downloads/export-123.zip",
  "created_at": "2025-01-01T00:00:00",
  "completed_at": "2025-01-01T00:05:00"
}
```

## Error Responses

All endpoints can return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication required"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "An internal server error occurred"
}
```

## Data Types

### UserRole
```json
"candidate" | "recruiter"
```

### ConversationState
```json
"initialized" | "onboarding" | "collecting_info" | "processing" | "waiting_for_input" | "completed" | "error"
```

### MessageType
```json
"text" | "image" | "document" | "location" | "quick_reply"
```

### QuestionType
```json
"text" | "number" | "select" | "multi_select" | "date" | "boolean"
```

### Platform
```json
"whatsapp" | "telegram" | "web"
```

## Rate Limiting

All endpoints are subject to rate limiting:
- **Limit**: 100 requests per minute per user
- **Headers**: 
  - `X-RateLimit-Limit`: Request limit per minute
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Time when the rate limit resets

## Webhook Callbacks

### WhatsApp Outbound Webhook

When sending messages via WhatsApp, the system will call your configured webhook:

**URL**: Configured via `WHATSAPP_OUTBOUND_WEBHOOK_URL` environment variable

**Request Body:**
```json
{
  "message_id": "msg-123",
  "to": "+1234567890",
  "status": "sent" | "delivered" | "read" | "failed",
  "timestamp": "2025-01-01T00:00:00",
  "error": "Error message if status is failed"
}
```

## Excel Export Format

The export service generates Excel files with the following columns:

| Column Name | Description | Example |
|-------------|-------------|---------|
| Application ID | Unique application identifier | app-123 |
| Candidate Name | Full name of candidate | John Doe |
| Email | Candidate email address | john@example.com |
| Phone | Candidate phone number | +1234567890 |
| Total Experience | Years of experience | 5.5 |
| Current CTC (LPA) | Current salary in LPA | 10.5 |
| Expected CTC (LPA) | Expected salary in LPA | 15.0 |
| Notice Period | Notice period in days | 60 |
| Current Location | Current city/location | Bangalore |
| Preferred Location | Preferred work locations | Remote, Bangalore |
| Skills | Comma-separated skills | Python, FastAPI, SQL |
| JD Match Score | Match score (0-100) | 85 |
| Must-Have-Failed | Whether must-have criteria failed | false |
| PreScreen_Summary_JSON | JSON with prescreen details | {"scores": {...}} |
| Recruiter Notes | Additional notes from recruiter | Strong candidate |
| Submitted At | When submitted to client | 2025-01-01T00:00:00 |

## SDK Examples

### JavaScript/Node.js

```javascript
const axios = require('axios');

const api = axios.create({
  baseURL: 'https://your-domain.com/api/v1',
  headers: {
    'Authorization': 'Bearer your-jwt-token',
    'Content-Type': 'application/json'
  }
});

// Start session
const startSession = async (userData) => {
  const response = await api.post('/chatbot/start-session', userData);
  return response.data;
};

// Send message
const sendMessage = async (sessionData) => {
  const response = await api.post('/chatbot/message', sessionData);
  return response.data;
};

// Submit prescreen answers
const submitAnswers = async (applicationId, answers) => {
  const response = await api.post(`/applications/${applicationId}/prescreen-answers`, answers);
  return response.data;
};
```

### Python

```python
import requests
import json

class ChatbotAPI:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    
    def start_session(self, user_data):
        response = requests.post(
            f'{self.base_url}/api/v1/chatbot/start-session',
            headers=self.headers,
            json=user_data
        )
        return response.json()
    
    def send_message(self, session_data):
        response = requests.post(
            f'{self.base_url}/api/v1/chatbot/message',
            headers=self.headers,
            json=session_data
        )
        return response.json()
    
    def submit_prescreen_answers(self, application_id, answers):
        response = requests.post(
            f'{self.base_url}/api/v1/applications/{application_id}/prescreen-answers',
            headers=self.headers,
            json=answers
        )
        return response.json()
```

## Testing

### Using curl

```bash
# Start session
curl -X POST https://your-domain.com/api/v1/chatbot/start-session \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "platform": "whatsapp",
    "platform_user_id": "whatsapp-user-123",
    "user_role": "candidate"
  }'

# Send message
curl -X POST https://your-domain.com/api/v1/chatbot/message \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-123",
    "message": "Hello, I want to apply for a job",
    "message_type": "text"
  }'

# Submit prescreen answers
curl -X POST https://your-domain.com/api/v1/applications/app-123/prescreen-answers \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "answers": {
      "ps_current_ctc": "10.5",
      "ps_expected_ctc": "15.0",
      "ps_notice_period": "60",
      "ps_total_experience": "5",
      "ps_key_skills": ["Python", "FastAPI", "SQLAlchemy"]
    },
    "update_global_profile": true
  }'
```

## Versioning

The API uses semantic versioning in the URL path:
- **Current Version**: `/api/v1/`
- **Future Versions**: `/api/v2/`, etc.

Breaking changes will require a new version. Non-breaking changes (additions) will be added to the current version.