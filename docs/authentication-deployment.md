# Authentication System Deployment Guide

## 🎯 Overview

This guide covers the deployment and setup of the CEFR Speaking Exam Simulator's new authentication system, implemented per GitHub Issue #24.

## 🏗️ Architecture

The authentication system consists of:

- **FastAPI Backend**: REST API with JWT authentication (`/api/auth/*`)
- **Streamlit Frontend**: Enhanced UI with login/registration integration
- **MongoDB Database**: User data, sessions, and password reset tokens
- **Security Features**: Rate limiting, input validation, secure headers

## 📋 Prerequisites

1. **Python 3.13+** with virtual environment
2. **MongoDB** running locally or accessible via URI
3. **Required Environment Variables**:
   - `JWT_SECRET`: Secret key for JWT token signing
   - `MONGODB_URI`: MongoDB connection string (optional, defaults to localhost)
   - `MONGODB_DB`: Database name (optional, defaults to "speak_check")

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Activate virtual environment
source venv/bin/activate

# Install new dependencies
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
# Generate a secure JWT secret
export JWT_SECRET=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Optional: Set MongoDB connection (defaults to localhost)
export MONGODB_URI="mongodb://localhost:27017"
export MONGODB_DB="speak_check"
```

### 3. Start the Complete System

```bash
# Use the automated startup script
./scripts/start_auth_system.sh
```

Or start services manually:

```bash
# Terminal 1: Start API server
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2: Start Streamlit app
python -m streamlit run app.py --server.port 8501
```

### 4. Access the Application

- **Streamlit App**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health

## 🔐 Authentication Features

### User Registration
- **Endpoint**: `POST /api/auth/register`
- **Features**: Email validation, password strength checking, duplicate prevention
- **Rate Limit**: 3 attempts per minute

### User Login
- **Endpoint**: `POST /api/auth/login`
- **Features**: JWT token generation, session management, last login tracking
- **Rate Limit**: 5 attempts per minute

### Session Management
- **Token Validation**: `POST /api/auth/validate-token`
- **Logout**: `POST /api/auth/logout` (single session or all sessions)
- **Session Duration**: 30 days (configurable)

### Profile Management
- **Get Profile**: `GET /api/auth/profile`
- **Update Profile**: `PUT /api/auth/profile`
- **Features**: Name updates, preferences storage

## 🛡️ Security Features

### Password Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character (`!@#$%^&*()_+-=[]{}|;:,.<>?`)

### Rate Limiting
- **Registration**: 3 attempts per minute
- **Login**: 5 attempts per minute
- **Token Validation**: 10 requests per minute

### Security Headers
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Content-Security-Policy: default-src 'self'`

### JWT Security
- Cryptographically secure secret key
- Token expiration (30 days default)
- User ID and email embedded in payload

## 🗄️ Database Schema

### Users Collection
```javascript
{
  "_id": ObjectId,
  "email": "user@example.com",      // Unique index
  "password_hash": "bcrypt_hash",
  "name": "User Name",
  "created_at": ISODate,
  "last_login": ISODate,
  "is_verified": false,
  "is_active": true,
  "preferences": {},
  "profile": {}
}
```

### User Sessions Collection
```javascript
{
  "user_id": ObjectId,
  "token": "secure_token",          // Unique index
  "created_at": ISODate,
  "expires_at": ISODate,
  "is_active": true,
  "user_agent": "browser_info",
  "ip_address": "127.0.0.1"
}
```

### Password Reset Tokens Collection
```javascript
{
  "user_id": ObjectId,
  "token": "reset_token",           // Unique index
  "created_at": ISODate,
  "expires_at": ISODate,
  "used": false
}
```

## 🧪 Testing

### Run Authentication Tests
```bash
# Run all authentication tests
python -m pytest tests/test_auth.py -v

# Run specific test categories
python -m pytest tests/test_auth.py::TestAuthService -v
python -m pytest tests/test_auth.py::TestAPIEndpoints -v
```

### Manual API Testing
```bash
# Test registration
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "confirm_password": "TestPass123!",
    "name": "Test User"
  }'

# Test login
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'
```

## 🚀 Production Deployment

### Environment Configuration
```bash
# Production environment variables
export JWT_SECRET="your-super-secure-secret-key-here"
export MONGODB_URI="mongodb://user:password@mongodb-host:27017/dbname"
export API_HOST="0.0.0.0"
export API_PORT="8000"
export CORS_ORIGINS="https://yourdomain.com,https://api.yourdomain.com"
export TRUSTED_HOSTS="yourdomain.com,api.yourdomain.com"
```

### Production Considerations
1. **Use HTTPS**: Configure SSL/TLS certificates
2. **Reverse Proxy**: Use nginx or similar for the Streamlit app
3. **Process Manager**: Use systemd, supervisor, or PM2
4. **Database Security**: Enable MongoDB authentication
5. **Monitoring**: Set up logging and health checks
6. **Backup**: Regular database backups

### Docker Deployment (Optional)
```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000 8501

CMD ["./scripts/start_auth_system.sh"]
```

## 🔧 Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   - Ensure MongoDB is running
   - Check `MONGODB_URI` environment variable
   - Verify database permissions

2. **JWT Token Errors**
   - Verify `JWT_SECRET` is set and consistent
   - Check token expiration settings
   - Ensure no spaces in secret key

3. **Rate Limiting Issues**
   - Check if requests are coming from expected IP
   - Adjust rate limits in `api/auth_routes.py`
   - Clear any cached rate limit data

4. **CORS Errors**
   - Update `CORS_ORIGINS` environment variable
   - Check browser developer tools for specific errors
   - Ensure both origins (API and Streamlit) are included

### Debug Mode
```bash
# Enable API debug logging
export API_RELOAD="true"
export PYTHONPATH="."

# Start with debug info
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload --log-level debug
```

## 📊 Monitoring

### Health Checks
- **API Health**: `GET /health`
- **Auth Health**: `GET /api/auth/health`

### Database Monitoring
```python
from db_mongo.crud import get_user_count, get_session_count

print(f"Active users: {get_user_count()}")
print(f"Active sessions: {get_session_count()}")
```

### Session Cleanup
```python
from db_mongo.crud import cleanup_expired_sessions, cleanup_expired_reset_tokens

# Run periodically (e.g., daily cron job)
expired_sessions = cleanup_expired_sessions()
expired_tokens = cleanup_expired_reset_tokens()
print(f"Cleaned up {expired_sessions} sessions and {expired_tokens} reset tokens")
```

## 🔄 Migration from Previous Version

If upgrading from a version without authentication:

1. **Backup existing data**: Export current session data
2. **Run database indexes**: They'll be created automatically on first startup
3. **Update session creation**: Existing sessions will work but won't have user association
4. **User migration**: Existing users will need to register accounts

## 📚 API Documentation

Once running, visit http://localhost:8000/docs for interactive API documentation with:
- Request/response schemas
- Try-it-out functionality  
- Authentication flow examples
- Error response formats

## 🎯 Next Steps

Future enhancements could include:
- Email verification system
- Password reset via email
- OAuth integration (Google, GitHub)
- Two-factor authentication
- User roles and permissions
- Advanced session management
- Audit logging

---

For issues or questions, please refer to the GitHub issue: https://github.com/agzyamov/speak-check/issues/24