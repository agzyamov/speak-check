# 📚 feat(docs): Add Postman collections for API documentation and testing

## 🎯 **Feature Request: Postman Collections for API Documentation**

### **Overview**
Create comprehensive Postman collections to document and test the CEFR Speaking Exam Simulator's API endpoints, external dependencies, and database operations.

### **Background**
Currently, the application lacks formal API documentation. While it's a Streamlit web app (not traditional REST API), we can still benefit from documenting:
- Streamlit internal endpoints (health checks)
- External API dependencies (OpenAI Whisper, weather APIs)
- Database operations (MongoDB)
- Development and testing utilities

### **Proposed Collections**

#### **1. Health & Monitoring Collection**
```json
{
  "name": "speak-check - Health & Monitoring",
  "endpoints": [
    "GET /_stcore/health - Streamlit health check",
    "GET / - Main application page",
    "GET /_stcore/config - Streamlit configuration",
    "GET /k8s/_stcore/health - Kubernetes health check"
  ]
}
```

#### **2. External APIs Collection**
```json
{
  "name": "speak-check - External APIs", 
  "endpoints": [
    "POST /openai/audio/transcriptions - Whisper STT",
    "POST /openai/chat/completions - GPT evaluation",
    "GET /weather - Weather context API"
  ]
}
```

#### **3. Database Operations Collection**
```json
{
  "name": "speak-check - Database Operations",
  "operations": [
    "MongoDB health check",
    "List sessions",
    "Database statistics",
    "Collection queries"
  ]
}
```

#### **4. Development & Testing Collection**
```json
{
  "name": "speak-check - Development & Testing",
  "features": [
    "Docker health checks",
    "Production health checks", 
    "Load testing endpoints",
    "Environment validation"
  ]
}
```

### **Implementation Plan**

#### **Phase 1: Collection Creation**
- [ ] Create 4 Postman collection JSON files
- [ ] Add comprehensive test scripts for each endpoint
- [ ] Include environment variables for different deployments
- [ ] Add pre-request scripts for authentication

#### **Phase 2: Environment Setup**
- [ ] Create environment files for:
  - Local development
  - Docker deployment  
  - Kubernetes deployment
  - Production
- [ ] Configure API keys and secrets
- [ ] Set up variable substitution

#### **Phase 3: Integration & Testing**
- [ ] Add Newman CLI integration for CI/CD
- [ ] Create GitHub Actions workflow for API testing
- [ ] Set up automated health checks
- [ ] Add monitoring and alerting

#### **Phase 4: Documentation**
- [ ] Create README for Postman collections
- [ ] Add usage examples and best practices
- [ ] Document environment setup process
- [ ] Create troubleshooting guide

### **File Structure**
```
postman/
├── collections/
│   ├── health-monitoring.json
│   ├── external-apis.json
│   ├── database-operations.json
│   └── development-testing.json
├── environments/
│   ├── local.json
│   ├── docker.json
│   ├── k8s.json
│   └── production.json
├── data/
│   └── sample-audio.wav
├── scripts/
│   ├── run-tests.sh
│   └── setup-environments.sh
└── README.md
```

### **Benefits**

#### **For Development**
- ✅ **Standardized Testing**: Consistent API testing across environments
- ✅ **Debugging**: Easy way to test individual components
- ✅ **Documentation**: Living documentation of application endpoints
- ✅ **Collaboration**: Team can easily test and validate changes

#### **For Operations**
- ✅ **Health Monitoring**: Automated health checks for all deployments
- ✅ **Integration Testing**: Validate external API dependencies
- ✅ **Database Validation**: Direct MongoDB operations for troubleshooting
- ✅ **CI/CD Integration**: Automated testing in deployment pipelines

#### **For Quality Assurance**
- ✅ **Regression Testing**: Ensure endpoints work after changes
- ✅ **Load Testing**: Validate application performance
- ✅ **Environment Validation**: Test across dev/staging/prod
- ✅ **Error Handling**: Test error scenarios and edge cases

### **Technical Requirements**

#### **Dependencies**
- Postman Desktop App or Newman CLI
- GitHub Personal Access Token (for MCP integration)
- OpenAI API Key (for external API testing)
- MongoDB connection (for database operations)

#### **Environment Variables**
```bash
# Required
OPENAI_API_KEY=sk-...
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_...

# Optional  
WEATHER_API_KEY=your_key
MONGODB_URI=mongodb://localhost:27017
BASE_URL=http://localhost:8501
```

#### **CI/CD Integration**
```yaml
# .github/workflows/api-testing.yml
name: API Testing
on: [push, pull_request]
jobs:
  api-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run API Tests
        run: |
          npm install -g newman
          newman run postman/collections/health-monitoring.json
```

### **Success Criteria**
- [ ] All 4 Postman collections created and functional
- [ ] Environment configurations for all deployment scenarios
- [ ] Automated testing integrated into CI/CD pipeline
- [ ] Documentation complete with usage examples
- [ ] Team can successfully use collections for testing

### **Acceptance Criteria**
- [ ] **AC-001**: Health check endpoints return 200 status
- [ ] **AC-002**: External API tests validate OpenAI integration
- [ ] **AC-003**: Database operations can query MongoDB collections
- [ ] **AC-004**: Development tests work across all environments
- [ ] **AC-005**: Newman CLI integration works in CI/CD
- [ ] **AC-006**: Documentation is clear and comprehensive

### **Estimated Effort**
- **Collection Creation**: 2-3 hours
- **Environment Setup**: 1-2 hours  
- **CI/CD Integration**: 1-2 hours
- **Documentation**: 1-2 hours
- **Testing & Validation**: 1-2 hours

**Total**: 6-11 hours

### **Priority**
**Medium** - This will improve development workflow and operational monitoring, but isn't blocking core functionality.

### **Labels**
- `enhancement`
- `documentation` 
- `testing`
- `api`
- `postman`

### **Assignees**
- [ ] @agzyamov (or appropriate team member)

### **Related Issues**
- Related to #15 (Playwright testing) - complements UI testing with API testing
- Related to #19 (K8s deployment) - will help validate K8s health checks

---

**Note**: This issue was created to improve the development experience and operational monitoring of the CEFR Speaking Exam Simulator. The Postman collections will serve as both documentation and testing tools for the application's various endpoints and integrations.


