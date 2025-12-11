# System Architecture

## Overview
The AI Recruitment Platform is a sophisticated recruitment management system with a FastAPI Backend and React/TypeScript Frontend. It features advanced AI-powered resume processing, multi-provider LLM integration, and comprehensive authentication.

## Core Components

### 1. Backend (`Backend/backend_app`)
*   **Framework**: FastAPI 0.104.1
*   **Database**: PostgreSQL with SQLAlchemy 2.0 ORM
*   **Auth**: OTP-based (WhatsApp/Telegram), JWT, Role-based access.
*   **AI Brain**: Gateway for LLM providers (OpenAI, Gemini, Groq).
*   **File Intake**: processing pipeline for PDF/DOCX using `pdfminer.six` and virus scanning.

### 2. Frontend (`Frontend/`)
*   **Framework**: React 19.2.0, Vite
*   **Language**: TypeScript
*   **State**: Context/Hooks (Modular design)
*   **UI**: Custom Tailwind/CSS components.

## Key Modules

### Brain Module
Orchestrates AI interactions.
*   **Multi-Provider**: Circuit breaker pattern for OpenRouter, Groq, Gemini.
*   **Prompt Builder**: Template-based generation.
*   **Cost Tracking**: Usage limits and key rotation.

### File Intake System
*   **Virus Scanning**: ClamAV integration (mock/adapter).
*   **Text Extraction**: 97% accuracy target using hybrid parsers.
*   **Quarantine**: Unsafe files are isolated.

### Chatbot Module (In Progress)
*   **Skills**: Onboarding, Resume Intake, Job Creation.
*   **Channels**: WhatsApp, Telegram.
*   **Context**: Session-based conversation memory.

## Data Flow
1.  **Resume Upload** -> Virus Scan -> Quarantine/Storage -> Text Extraction -> PII Redaction -> AI Parsing -> Database.
2.  **Job Creation** -> Recruiter Input -> AI Optimization -> Database -> Vector Embedding -> Matching Engine.

## Infrastructure
*   **Containerization**: Docker (In Setup)
*   **Queues**: Celery for background tasks (Extraction, Email).
*   **Storage**: Local filesystem (dev) / S3-compatible (prod).
