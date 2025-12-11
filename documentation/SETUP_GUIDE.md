# System Setup & Configuration Guide

## 1. Prerequisites
*   **Python**: 3.10+
*   **Node.js**: 18+ (for Frontend)
*   **PostgreSQL**: 13+ (Local or Cloud)
*   **Git**

## 2. Installation

### Backend Setup
1.  Navigate to `Backend/backend_app`:
    ```bash
    cd Backend/backend_app
    ```
2.  Create virtual environment:
    ```bash
    python -m venv .venv
    .venv\Scripts\activate  # Windows
    # source .venv/bin/activate  # Linux/Mac
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Frontend Setup
1.  Navigate to `Frontend`:
    ```bash
    cd Frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    # or
    yarn install
    ```

## 3. Environment Configuration
The project uses a **single unified `.env` file** in the root directory.

### Copy Template
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### Configure Keys
Fill in the following sections in `.env`:

#### Application
*   `DEBUG`: `True` for development.
*   `SECRET_KEY`: Generate a strong random string.
*   `DATABASE_URL`: `postgresql://user:pass@localhost:5432/db_name`

#### AI Providers
You need API keys for at least one provider.
*   **OpenRouter**: `OPENROUTER_API_KEY`
*   **Groq**: `GROQ_API_KEY`
*   **Gemini**: `GEMINI_API_KEY`

#### Telegram Bot (Optional)
*   `TELEGRAM_BOT_TOKEN`: Get from @BotFather
*   `TELEGRAM_WEBHOOK_URL`: Your simplified ngrok URL

## 4. Database Setup
1.  Ensure PostgreSQL is running.
2.  Create database `recruitment_db`.
3.  Run migrations (if Alembic is configured) or initialization scripts in `Backend/backend_app/db`.

## 5. Running the Application

### Start Backend
```bash
cd Backend/backend_app
uvicorn main:app --reload --port 8000
```
API Docs will be at: `http://localhost:8000/docs`

### Start Frontend
```bash
cd Frontend
npm run dev
```
App will be at: `http://localhost:5173`

## 6. Testing
Run tests from the backend directory:
```bash
pytest
```
