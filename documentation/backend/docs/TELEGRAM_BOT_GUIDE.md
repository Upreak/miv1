# Telegram Bot Integration Guide

## Overview

This document provides comprehensive setup instructions, deployment guidelines, and troubleshooting documentation for the production-ready Telegram bot integration with your recruitment chatbot system.

## Table of Contents

1. [Features](#features)
2. [Prerequisites](#prerequisites)
3. [Setup Instructions](#setup-instructions)
4. [Configuration](#configuration)
5. [Deployment](#deployment)
6. [Testing](#testing)
7. [Monitoring and Logging](#monitoring-and-logging)
8. [Troubleshooting](#troubleshooting)
9. [Security Best Practices](#security-best-practices)
10. [API Reference](#api-reference)

## Features

### ✅ **Production-Ready Features**

- **Secure Token Management**: Environment-based configuration with validation
- **Intelligent Response System**: Context-aware responses for recruitment queries
- **Rate Limiting**: Protection against spam and abuse
- **Error Handling**: Comprehensive error handling and graceful degradation
- **Health Monitoring**: Built-in health check endpoints
- **Webhook Management**: Automatic webhook setup and validation
- **Security Validation**: Request validation and input sanitization
- **Comprehensive Testing**: Unit tests, integration tests, and mock testing
- **Production Logging**: Structured logging for monitoring and debugging
- **Graceful Startup/Shutdown**: Proper service lifecycle management

### 🤖 **Bot Functionality**

- **Command Support**:
  - `/start` - Welcome message and introduction
  - `/help` - Help and available commands
  - `/high` - Special greeting response
- **Message Types**: Text, photos, documents, voice, video, location, contact
- **Intelligent Responses**: Job search, resume analysis, company info, greetings
- **State Management**: Conversation state tracking (extensible)

## Prerequisites

### Required Software

- Python 3.10+
- PostgreSQL (for database)
- Redis (for caching and sessions)
- FastAPI application server

### Telegram Requirements

- Telegram Bot Token (from @BotFather)
- Publicly accessible webhook URL (for production)
- HTTPS certificate (for webhook URL)

### Environment Setup

```bash
# Clone and navigate to project
git clone <your-repo>
cd Backend

# Install dependencies
pip install -r requirements.txt
pip install -r backend_app/requirements.txt
```

## Setup Instructions

### Step 1: Create Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Copy the bot token (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxYZ123abc456`)

### Step 2: Configure Environment

#### Option A: Interactive Setup (Recommended)

```bash
python scripts/deploy_telegram_bot.py
```

This will guide you through:
- Bot token configuration
- Webhook URL setup
- Security secret generation
- Debug mode configuration

#### Option B: Manual Configuration

Create `.env` file with the following variables:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_WEBHOOK_SECRET=your_generated_secret_here
TELEGRAM_WEBHOOK_URL=https://your-domain.com/api/v1/telegram/webhooks/telegram

# Optional Settings
TELEGRAM_DEBUG_MODE=false
TELEGRAM_MOCK_MODE=false
TELEGRAM_RATE_LIMIT_REQUESTS=30
TELEGRAM_RATE_LIMIT_WINDOW=60
TELEGRAM_TIMEOUT=30
```

### Step 3: Set Webhook

```bash
# Using the deployment script
python scripts/deploy_telegram_bot.py

# Or manually via API
curl -X POST "https://api.telegram.org/bot{TOKEN}/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-domain.com/api/v1/telegram/webhooks/telegram",
    "secret_token": "your_secret_token"
  }'
```

### Step 4: Start Application

```bash
# Start FastAPI application
uvicorn backend_app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Docker (if available)
docker-compose up -d
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | ✅ | - | Telegram Bot API token |
| `TELEGRAM_WEBHOOK_SECRET` | ✅ | - | Secret token for webhook validation |
| `TELEGRAM_WEBHOOK_URL` | ✅ | - | Full webhook URL |
| `TELEGRAM_DEBUG_MODE` | ❌ | false | Enable debug logging |
| `TELEGRAM_MOCK_MODE` | ❌ | false | Enable mock mode for testing |
| `TELEGRAM_RATE_LIMIT_REQUESTS` | ❌ | 30 | Max requests per minute per user |
| `TELEGRAM_RATE_LIMIT_WINDOW` | ❌ | 60 | Rate limit window in seconds |
| `TELEGRAM_TIMEOUT` | ❌ | 30 | API request timeout in seconds |

### Configuration Validation

```python
from backend_app.config.telegram_config import telegram_settings

# Validate configuration
issues = telegram_settings.validate_configuration()
if issues:
    print("Configuration issues:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("Configuration is valid!")
```

## Deployment

### Production Deployment

#### 1. Environment Setup

```bash
# Set production environment
export TELEGRAM_DEBUG_MODE=false
export TELEGRAM_MOCK_MODE=false

# Configure production webhook URL
export TELEGRAM_WEBHOOK_URL=https://your-production-domain.com/api/v1/telegram/webhooks/telegram
```

#### 2. Security Configuration

```bash
# Generate secure webhook secret
python -c "import secrets; print(''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(32)))"
```

#### 3. Deploy Application

```bash
# Using Docker
docker build -t recruitment-bot .
docker run -d -p 8000:8000 --env-file .env recruitment-bot

# Using Kubernetes
kubectl apply -f k8s/deployment.yaml

# Using Heroku
git push heroku main
heroku config:set $(cat .env | xargs)
```

#### 4. Verify Deployment

```bash
# Check health status
curl https://your-domain.com/api/v1/telegram/health

# Test webhook
curl https://your-domain.com/api/v1/telegram/test-integration
```

### Docker Deployment

#### Dockerfile

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "backend_app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - TELEGRAM_WEBHOOK_SECRET=${TELEGRAM_WEBHOOK_SECRET}
      - TELEGRAM_WEBHOOK_URL=${TELEGRAM_WEBHOOK_URL}
    depends_on:
      - postgres
      - redis
  
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: recruitment_db
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## Testing

### Unit Tests

```bash
# Run all Telegram bot tests
pytest tests/test_telegram_bot.py -v

# Run specific test categories
pytest tests/test_telegram_bot.py::TestTelegramSettings -v
pytest tests/test_telegram_bot.py::TestTelegramSecurityManager -v
pytest tests/test_telegram_bot.py::TestTelegramBotService -v
```

### Integration Tests

```bash
# Run integration tests
pytest tests/test_telegram_bot.py::TestTelegramIntegration -v -m integration

# Run with mock mode
TELEGRAM_MOCK_MODE=true pytest tests/test_telegram_bot.py -v
```

### Manual Testing

#### 1. Test Bot Connection

```bash
# Test bot info
curl -X GET "https://api.telegram.org/bot{TOKEN}/getMe"

# Expected response:
# {"ok":true,"result":{"id":123456789,"is_bot":true,"first_name":"YourBot","username":"YourBot"}}
```

#### 2. Test Webhook

```bash
# Send test message to your bot on Telegram
# Check application logs for webhook processing
```

#### 3. Test API Endpoints

```bash
# Health check
curl https://your-domain.com/api/v1/telegram/health

# Configuration check
curl https://your-domain.com/api/v1/telegram/configuration

# Webhook info
curl https://your-domain.com/api/v1/telegram/get-webhook-info
```

### Mock Testing

For development without real Telegram API calls:

```bash
# Enable mock mode
export TELEGRAM_MOCK_MODE=true

# Run tests or application
pytest tests/test_telegram_bot.py -v
```

## Monitoring and Logging

### Health Check Endpoints

```bash
# General health check
GET /api/v1/telegram/health

# Configuration status
GET /api/v1/telegram/configuration

# Integration test
GET /api/v1/telegram/test-integration
```

### Log Monitoring

```python
# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Monitor specific loggers
logger = logging.getLogger('backend_app.services.telegram_service')
```

### Metrics to Monitor

- **Request Rate**: Messages per minute
- **Error Rate**: Failed webhook processing
- **Response Time**: Message processing latency
- **Rate Limiting**: Blocked requests count
- **Webhook Status**: Active webhook information

### Alerting

Set up alerts for:

```yaml
# Example Prometheus alerts
- alert: TelegramBotDown
  expr: up{job="telegram-bot"} == 0
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: "Telegram bot is down"

- alert: HighErrorRate
  expr: rate(telegram_errors_total[5m]) > 0.1
  for: 2m
  labels:
    severity: warning
  annotations:
    summary: "High error rate in Telegram bot"
```

## Troubleshooting

### Common Issues

#### 1. Bot Token Issues

**Problem**: "Invalid bot token format"

**Solution**:
```bash
# Verify token format (should be: 123456789:ABCdefGHIjklMNOpqrsTUVwxYZ123abc456)
echo $TELEGRAM_BOT_TOKEN | grep -E '^[0-9]+:[A-Za-z0-9_-]{35}$'

# Get new token from @BotFather if needed
```

#### 2. Webhook Issues

**Problem**: Webhook not receiving messages

**Diagnosis**:
```bash
# Check webhook info
curl -X GET "https://api.telegram.org/bot{TOKEN}/getWebhookInfo"

# Check for errors in response
# Look for "last_error_message" field
```

**Solutions**:
- Ensure HTTPS certificate is valid
- Check firewall settings
- Verify webhook URL is accessible
- Check application logs for errors

#### 3. Rate Limiting

**Problem**: Messages being blocked

**Solution**:
```bash
# Check current rate limit settings
curl https://your-domain.com/api/v1/telegram/configuration

# Adjust rate limits if needed
export TELEGRAM_RATE_LIMIT_REQUESTS=50
export TELEGRAM_RATE_LIMIT_WINDOW=60
```

#### 4. Database Connection

**Problem**: Database errors during message processing

**Solution**:
```bash
# Check database connection
python -c "from backend_app.db.connection import init_db; import asyncio; asyncio.run(init_db())"

# Verify database URL
echo $DATABASE_URL
```

### Debug Mode

Enable debug logging:

```bash
export TELEGRAM_DEBUG_MODE=true
# Restart application
```

Check logs for detailed information:

```bash
# View application logs
tail -f logs/app.log | grep telegram

# Look for specific error patterns
grep -i "telegram.*error" logs/app.log
```

### Webhook Secret Issues

**Problem**: "Invalid webhook secret"

**Solution**:
```bash
# Verify secret is set correctly
echo $TELEGRAM_WEBHOOK_SECRET

# Check webhook secret in Telegram
curl -X GET "https://api.telegram.org/bot{TOKEN}/getWebhookInfo" | grep "secret"

# Regenerate secret if needed
python -c "import secrets; print(''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(32)))"
```

### Network Issues

**Problem**: Cannot reach webhook URL

**Diagnosis**:
```bash
# Test webhook URL accessibility
curl -I https://your-domain.com/api/v1/telegram/webhooks/telegram

# Check for SSL issues
openssl s_client -connect your-domain.com:443
```

**Solutions**:
- Verify SSL certificate
- Check reverse proxy configuration
- Ensure port 443 is open
- Check CDN settings

## Security Best Practices

### 1. Token Security

- **Never commit tokens to version control**
- **Use environment variables**
- **Rotate tokens regularly**
- **Limit bot permissions**

### 2. Webhook Security

- **Always use HTTPS**
- **Validate webhook secrets**
- **Implement rate limiting**
- **Sanitize all inputs**

### 3. Input Validation

```python
# Example: Validate chat ID
if not TelegramSecurityManager.validate_chat_id(chat_id):
    logger.warning(f"Invalid chat ID: {chat_id}")
    return

# Example: Sanitize message content
sanitized_text = TelegramSecurityManager.sanitize_telegram_input(text)
```

### 4. Rate Limiting

```python
# Built-in rate limiting
if not self.rate_limiter.is_allowed(f"user:{user_id}"):
    await self._send_rate_limit_message(chat_id)
    return
```

### 5. Secret Management

```bash
# Use secure secret generation
export TELEGRAM_WEBHOOK_SECRET=$(python -c "import secrets; import string; print(''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(64)))")

# Store secrets securely
# - Use AWS Secrets Manager
# - Use HashiCorp Vault
# - Use Kubernetes secrets
```

## API Reference

### Webhook Endpoint

```http
POST /api/v1/telegram/webhooks/telegram
Content-Type: application/json

{
  "update_id": 123456789,
  "message": {
    "message_id": 123,
    "from": {
      "id": 456,
      "username": "testuser"
    },
    "chat": {
      "id": 789
    },
    "text": "Hello bot!",
    "date": 1234567890
  }
}
```

**Headers**:
- `X-Telegram-Bot-Api-Secret-Token`: Webhook secret (if configured)

**Response**:
```json
{
  "status": "received",
  "timestamp": 123456789,
  "message_type": "webhook"
}
```

### Health Check Endpoint

```http
GET /api/v1/telegram/health
```

**Response**:
```json
{
  "status": "healthy",
  "service": "telegram_bot",
  "timestamp": "2024-01-01T12:00:00",
  "details": {
    "initialized": true,
    "config_valid": true,
    "mock_mode": false,
    "rate_limiter_stats": {
      "active_users": 10,
      "max_requests": 30,
      "window_seconds": 60
    }
  }
}
```

### Configuration Endpoint

```http
GET /api/v1/telegram/configuration
```

**Response**:
```json
{
  "configuration": {
    "bot_token_set": true,
    "webhook_url": "https://example.com/webhook",
    "webhook_secret_set": true,
    "mock_mode": false,
    "debug_mode": false,
    "rate_limit": {
      "requests": 30,
      "window": 60
    },
    "timeout": 30,
    "retry_attempts": 3
  },
  "validation_issues": [],
  "is_configured": true
}
```

### Send Message Endpoint

```http
POST /api/v1/telegram/send-message
Content-Type: application/json

{
  "chat_id": 123456789,
  "text": "Hello from bot!",
  "parse_mode": "Markdown"
}
```

**Response**:
```json
{
  "status": "success",
  "message_id": 123,
  "chat_id": 123456789
}
```

### Webhook Management

#### Set Webhook

```http
POST /api/v1/telegram/set-webhook
Content-Type: application/json

{
  "webhook_url": "https://your-domain.com/api/v1/telegram/webhooks/telegram",
  "secret_token": "your-secret-token"
}
```

#### Get Webhook Info

```http
GET /api/v1/telegram/get-webhook-info
```

#### Delete Webhook

```http
DELETE /api/v1/telegram/delete-webhook
Content-Type: application/json

{
  "drop_pending_updates": true
}
```

## Support and Maintenance

### Regular Maintenance

1. **Monitor logs daily**
2. **Check webhook status weekly**
3. **Rotate secrets monthly**
4. **Update dependencies regularly**

### Getting Help

1. **Check logs**: `tail -f logs/app.log`
2. **Run health check**: `curl /api/v1/telegram/health`
3. **Check configuration**: `curl /api/v1/telegram/configuration`
4. **Review this guide**: For common issues and solutions

### Contributing

To contribute improvements to the Telegram bot:

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Submit a pull request

### License

This Telegram bot integration is part of the recruitment chatbot system.