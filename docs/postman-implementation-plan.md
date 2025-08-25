# Postman Collections Implementation Plan

## Overview

This document outlines the implementation plan for comprehensive Postman collections for the CEFR Speaking Exam Simulator, as specified in GitHub issue #21.

## Current Architecture Analysis

The CEFR Speaking Exam Simulator is a **Streamlit-based web application** with the following key components:

### Application Type
- **Frontend**: Streamlit web interface (port 8501)
- **Backend**: Python modules with direct function calls (not REST API)
- **Database**: MongoDB for session/recording/transcript storage
- **External APIs**: OpenAI (Whisper STT + GPT assessment), Weather API, GitHub API

### Key Modules
- `app.py` - Main Streamlit application
- `stt_openai.py` - OpenAI Whisper speech-to-text
- `eval_openai.py` - OpenAI GPT CEFR assessment
- `db_mongo/crud.py` - MongoDB operations
- `weather_client.py` - Weather API integration
- `recording.py` - Audio recording functionality
- `tts.py` - Text-to-speech functionality

## Implementation Strategy

Since this is a **Streamlit application** (not a traditional REST API), the Postman collections will focus on:

1. **External API Testing** - Testing integrations with third-party services
2. **Health Monitoring** - Application health checks and monitoring
3. **Database Operations** - MongoDB connection and query testing
4. **Development Tools** - Utility endpoints for development workflow

## Collection Structure

### 1. Health & Monitoring Collection
**Purpose**: Application health checks and system monitoring

**Endpoints**:
- **Streamlit Health Check**
  - `GET http://localhost:8501/health` (if implemented)
  - `GET http://localhost:8501` (main page availability)
- **MongoDB Health Check**
  - Custom script to test MongoDB connection
- **File System Health**
  - Check for required directories (`data/`, `logs/`)
  - Check for population data file
- **Environment Variables**
  - Validate required environment variables
  - Test API key presence (without exposing values)

### 2. External APIs Collection
**Purpose**: Test and validate third-party service integrations

#### OpenAI Integration
- **Whisper STT Test**
  - `POST https://api.openai.com/v1/audio/transcriptions`
  - Test with sample audio file
  - Validate response format
- **GPT Assessment Test**
  - `POST https://api.openai.com/v1/chat/completions`
  - Test CEFR assessment prompt
  - Validate structured response

#### Weather API Integration
- **Weather Data Fetch**
  - Test weather API endpoints
  - Validate response structure
  - Test error handling

#### GitHub API Integration
- **Repository Information**
  - `GET https://api.github.com/repos/agzyamov/speak-check`
  - Test authentication
  - Validate repository access

### 3. Database Operations Collection
**Purpose**: MongoDB connection and CRUD operation testing

**Operations**:
- **Connection Test**
  - Test MongoDB connection string
  - Validate database and collection access
- **Session Management**
  - Create test session
  - Update session status
  - Query sessions
- **Recording Operations**
  - Insert test recording metadata
  - Query recordings by session
- **Transcript Operations**
  - Insert test transcript
  - Query transcripts by recording
- **Evaluation Operations**
  - Insert test evaluation
  - Query evaluations by transcript

### 4. Development & Testing Collection
**Purpose**: Development utilities and testing helpers

**Utilities**:
- **Data Generation**
  - Generate test audio files
  - Create sample transcripts
  - Generate mock evaluation data
- **Cleanup Operations**
  - Clean test data from database
  - Remove temporary files
- **Configuration Validation**
  - Test environment setup
  - Validate file permissions
  - Check directory structure

## Environment Configuration

### Environment Files

#### `.postman_env_local.json`
```json
{
  "name": "CEFR Local Development",
  "values": [
    {"key": "base_url", "value": "http://localhost:8501"},
    {"key": "mongodb_url", "value": "mongodb://localhost:27017"},
    {"key": "mongodb_db", "value": "speak_check"},
    {"key": "openai_api_url", "value": "https://api.openai.com/v1"},
    {"key": "github_api_url", "value": "https://api.github.com"},
    {"key": "weather_api_url", "value": "{{weather_service_url}}"}
  ]
}
```

#### `.postman_env_docker.json`
```json
{
  "name": "CEFR Docker Environment",
  "values": [
    {"key": "base_url", "value": "http://app:8501"},
    {"key": "mongodb_url", "value": "mongodb://mongo:27017"},
    {"key": "mongodb_db", "value": "speak_check"}
  ]
}
```

#### `.postman_env_k8s.json`
```json
{
  "name": "CEFR Kubernetes Environment",
  "values": [
    {"key": "base_url", "value": "http://localhost:30080"},
    {"key": "mongodb_url", "value": "mongodb://mongo:27017"}
  ]
}
```

### Secret Variables
- `OPENAI_API_KEY`
- `GITHUB_PERSONAL_ACCESS_TOKEN`
- `MONGODB_CONNECTION_STRING` (for cloud deployments)

## Implementation Phases

### Phase 1: Core Infrastructure (2-3 hours)
- [x] Create implementation plan
- [ ] Set up collection structure
- [ ] Create environment templates
- [ ] Implement basic health checks

### Phase 2: External API Testing (2-3 hours)
- [ ] OpenAI Whisper integration tests
- [ ] OpenAI GPT assessment tests
- [ ] Weather API integration tests
- [ ] GitHub API tests

### Phase 3: Database Operations (1-2 hours)
- [ ] MongoDB connection tests
- [ ] CRUD operation tests for all collections
- [ ] Data validation tests

### Phase 4: Development Tools (1-2 hours)
- [ ] Test data generation utilities
- [ ] Cleanup and maintenance scripts
- [ ] Configuration validation tools

### Phase 5: CI/CD Integration (1 hour)
- [ ] Newman CLI setup
- [ ] GitHub Actions integration
- [ ] Automated test reporting

## File Structure

```
postman/
├── collections/
│   ├── health-monitoring.postman_collection.json
│   ├── external-apis.postman_collection.json
│   ├── database-operations.postman_collection.json
│   └── development-testing.postman_collection.json
├── environments/
│   ├── local.postman_environment.json
│   ├── docker.postman_environment.json
│   └── k8s.postman_environment.json
├── scripts/
│   ├── run-tests.sh
│   ├── cleanup.sh
│   └── generate-report.sh
├── test-data/
│   ├── sample-audio.wav
│   ├── sample-transcript.json
│   └── sample-evaluation.json
└── README.md
```

## Benefits

1. **Standardized Testing**: Consistent API testing across environments
2. **Health Monitoring**: Automated health checks for all components
3. **Development Efficiency**: Quick validation of integrations
4. **Documentation**: Living documentation of system interactions
5. **CI/CD Integration**: Automated testing in deployment pipelines
6. **Debugging Support**: Structured approach to troubleshooting issues

## Success Criteria

- [ ] All external API integrations tested and validated
- [ ] MongoDB operations fully covered
- [ ] Health checks for all system components
- [ ] Newman CLI integration working
- [ ] Documentation complete and comprehensive
- [ ] Collections executable in all environments (local, Docker, K8s)

## Next Steps

1. Create basic collection structure
2. Implement health monitoring endpoints
3. Test external API integrations
4. Set up database operation tests
5. Integrate with CI/CD pipeline

This implementation will provide a comprehensive testing framework that supports both development and operational needs of the CEFR Speaking Exam Simulator.