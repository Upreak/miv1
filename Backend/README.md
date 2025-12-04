# OTP-Only Authentication System

A complete mobile-first authentication system with OTP verification, WhatsApp, and Telegram integration built with FastAPI and SQLAlchemy.

## 🚀 Features

### 🔐 Authentication Methods
- **Web Login**: Phone number + OTP verification
- **WhatsApp Login**: Auto-login via WhatsApp messages
- **Telegram Login**: Auto-login via Telegram messages

### 🛡️ Security Features
- JWT token-based authentication
- OTP with configurable expiration (default: 5 minutes)
- Twilio SMS integration for production
- Rate limiting support
- CORS configuration
- Comprehensive error handling

### 🧪 Testing
- Unit tests with pytest
- Integration tests
- System tests
- Code linting with flake8
- Type checking with mypy
- Coverage reporting

## 📋 Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Configuration
```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:
```env
# Database Configuration
DATABASE_URL=sqlite:///./recruitment_app.db

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-here-change-in-production

# OTP Configuration
OTP_LENGTH=6
OTP_EXPIRY_MINUTES=5
SEND_OTP_VIA_SMS=false

# Twilio Configuration (for production)
SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=your-twilio-phone-number

# WhatsApp Configuration
WHATSAPP_VERIFY_TOKEN=your-whatsapp-verify-token
WHATSAPP_WEBHOOK_SECRET=your-whatsapp-webhook-secret

# Telegram Configuration
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
```

### 5. Create Directories
```bash
mkdir -p logs uploads
```

## 🧪 Testing

### Run All Tests
```bash
python run_tests.py
```

### Run Specific Test Types
```bash
# Unit tests
python -m pytest tests/ -v

# Integration tests
python -m pytest tests/test_auth_integration.py -v

# System tests
python test_auth_system.py

# Code linting
flake8 backend_app/

# Type checking
mypy backend_app/

# Code formatting
black backend_app/
```

### Test Coverage
```bash
python -m pytest tests/ --cov=backend_app --cov-report=html --cov-report=term-missing
```

Coverage reports will be generated in `htmlcov/` directory.

## 🚀 Running the Application

### Development Mode
```bash
python -m uvicorn backend_app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
gunicorn backend_app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Access the API
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🔧 API Endpoints

### Authentication Endpoints

#### Login with Phone
```http
POST /api/auth/login
Content-Type: application/json

{
  "phone": "919876543210"
}
```

#### Verify OTP
```http
POST /api/auth/verify-otp
Content-Type: application/json

{
  "phone": "919876543210",
  "otp_code": "123456"
}
```

#### Refresh Token
```http
POST /api/auth/refresh-token
Content-Type: application/json

{
  "refresh_token": "your-refresh-token"
}
```

#### Get Current User
```http
GET /api/auth/me
Authorization: Bearer your-access-token
```

#### Logout
```http
POST /api/auth/logout
Authorization: Bearer your-access-token
```

### WhatsApp Webhook

#### Verify Webhook
```http
GET /api/whatsapp/webhook?hub.mode=subscribe&hub.challenge=123456&hub.verify_token=your_verify_token
```

#### Handle Messages
```http
POST /api/whatsapp/webhook
Content-Type: application/json
X-Hub-Signature-256: sha256=your_signature

{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "changes": [
        {
          "value": {
            "messages": [
              {
                "from": "919876543210",
                "text": {
                  "body": "Hello"
                }
              }
            ]
          }
        }
      ]
    }
  ]
}
```

### Telegram Webhook

#### Handle Updates
```http
POST /api/telegram/webhook
Content-Type: application/json

{
  "message": {
    "from": {
      "id": 123456789,
      "first_name": "John",
      "username": "john_doe"
    },
    "chat": {
      "id": 123456789,
      "type": "private"
    },
    "text": "/start"
  }
}
```

## 📱 Usage Examples

### Web Login Flow
```python
import requests

# 1. Send OTP
response = requests.post("http://localhost:8000/api/auth/login", json={"phone": "919876543210"})
otp_code = response.json()["otp_code"]

# 2. Verify OTP
response = requests.post("http://localhost:8000/api/auth/verify-otp", json={
    "phone": "919876543210",
    "otp_code": otp_code
})

# 3. Get access token
access_token = response.json()["access_token"]

# 4. Use access token
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get("http://localhost:8000/api/auth/me", headers=headers)
```

### WhatsApp Integration
```python
# Handle WhatsApp messages in your webhook
def handle_whatsapp_message(message):
    phone = message["from"]
    text = message["text"]["body"]
    
    if text.lower() == "otp":
        # Send OTP via WhatsApp
        send_whatsapp_message(phone, "Your OTP is: 123456")
    elif text.lower().startswith("verify"):
        # Verify OTP
        otp = text.split(" ")[1]
        verify_otp(phone, otp)
```

### Telegram Integration
```python
# Handle Telegram commands
def handle_telegram_command(update):
    if update.message.text == "/start":
        # Auto-login user
        user_id = update.message.from_user.id
        auto_login_telegram(user_id)
    elif update.message.text == "/otp":
        # Send OTP
        send_telegram_message(update.message.chat.id, "Your OTP is: 123456")
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./recruitment_app.db` |
| `JWT_SECRET_KEY` | JWT signing secret | Required |
| `OTP_LENGTH` | OTP code length | `6` |
| `OTP_EXPIRY_MINUTES` | OTP expiration time | `5` |
| `SEND_OTP_VIA_SMS` | Enable SMS sending | `false` |
| `SMS_PROVIDER` | SMS provider (`twilio`) | `twilio` |
| `TWILIO_ACCOUNT_SID` | Twilio account SID | Required for SMS |
| `TWILIO_AUTH_TOKEN` | Twilio auth token | Required for SMS |
| `TWILIO_PHONE_NUMBER` | Twilio phone number | Required for SMS |
| `DEBUG` | Debug mode | `false` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Database Configuration

#### SQLite (Default)
```env
DATABASE_URL=sqlite:///./recruitment_app.db
```

#### PostgreSQL
```env
DATABASE_URL=postgresql://user:password@localhost/recruitment_db
```

#### MySQL
```env
DATABASE_URL=mysql://user:password@localhost/recruitment_db
```

## 🚀 Deployment

### Docker Deployment

#### Build Docker Image
```bash
docker build -t recruitment-auth .
```

#### Run Docker Container
```bash
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:password@localhost/recruitment_db \
  -e JWT_SECRET_KEY=your-secret-key \
  recruitment-auth
```

### Docker Compose

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/recruitment_db
      - JWT_SECRET_KEY=your-secret-key
    depends_on:
      - db
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=recruitment_db
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Production Deployment

1. **Environment Setup**
   ```bash
   export ENVIRONMENT=production
   export DEBUG=false
   export LOG_LEVEL=WARNING
   ```

2. **Database Migration**
   ```bash
   alembic upgrade head
   ```

3. **Process Management**
   ```bash
   # Using systemd
   sudo systemctl start recruitment-auth
   sudo systemctl enable recruitment-auth
   ```

4. **SSL/TLS Configuration**
   ```bash
   # Using nginx
   server {
       listen 443 ssl;
       server_name your-domain.com;
       
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
       
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## 📊 Monitoring

### Logging
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
```

### Health Check
```http
GET /health
```

### Metrics
```http
GET /metrics
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Database Connection Issues
```bash
# Check database connection
python -c "from backend_app.db.base import engine; print(engine.url)"
```

#### 2. JWT Token Issues
```bash
# Verify JWT configuration
python -c "from backend_app.security.token_manager import TokenManager; tm = TokenManager(); print(tm.secret_key)"
```

#### 3. Twilio SMS Issues
```bash
# Test Twilio connection
python -c "from twilio.rest import Client; client = Client('account_sid', 'auth_token'); print(client)"
```

#### 4. Import Issues
```bash
# Check Python path
python -c "import sys; print(sys.path)"
```

### Debug Mode
```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the test examples

## 🔄 Changelog

### v1.0.0
- Initial release
- OTP-only authentication
- WhatsApp integration
- Telegram integration
- Comprehensive testing suite
- Production-ready configuration