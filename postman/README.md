# CEFR Speaking Exam Simulator - Postman Collections

Comprehensive API testing and monitoring collections for the CEFR Speaking Exam Simulator application. This implementation addresses GitHub issue #21 with complete testing coverage for external APIs, health monitoring, and development utilities.

## 📋 Overview

This Postman collections suite provides:
- **Health Monitoring** - System availability and dependency checks
- **External API Testing** - OpenAI, GitHub, and weather service integration
- **Database Operations** - MongoDB CRUD testing (requires API endpoints)
- **Development Tools** - Configuration validation and debugging utilities

## 🚀 Quick Start

### Prerequisites

```bash
# Install Newman globally
npm install -g newman

# Verify installation
newman --version
```

### Environment Variables

Set these environment variables before running tests:

```bash
export openai_api_key="your-openai-api-key"
export github_token="your-github-token"
```

### Running Tests

```bash
# Run all collections with local environment
./scripts/run-tests.sh

# Run specific collection with docker environment
./scripts/run-tests.sh docker health-monitoring

# Run with Kubernetes environment
./scripts/run-tests.sh k8s
```

### Generate Reports

```bash
# Generate HTML report for local environment
./scripts/generate-report.sh

# Generate JSON report for docker environment
./scripts/generate-report.sh docker json

# Generate both formats
./scripts/generate-report.sh k8s both
```

### Cleanup

```bash
# Clean up test data and reports
./scripts/cleanup.sh
```

## 📁 Directory Structure

```
postman/
├── collections/                    # Postman collection files
│   ├── health-monitoring.postman_collection.json
│   ├── external-apis.postman_collection.json
│   ├── database-operations.postman_collection.json
│   └── development-testing.postman_collection.json
├── environments/                   # Environment configurations
│   ├── local.postman_environment.json
│   ├── docker.postman_environment.json
│   └── k8s.postman_environment.json
├── scripts/                       # Automation scripts
│   ├── run-tests.sh               # Newman test runner
│   ├── generate-report.sh         # Report generator
│   └── cleanup.sh                 # Cleanup utility
├── test-data/                     # Sample test data
│   ├── sample-transcript.json
│   └── sample-evaluation.json
├── reports/                       # Generated reports (auto-created)
└── README.md                      # This file
```

## 📊 Collections Overview

### 1. Health & Monitoring

**File:** `health-monitoring.postman_collection.json`

Tests system availability and dependency health:
- Application availability check
- OpenAI API connectivity
- GitHub API connectivity
- File system health validation
- Environment configuration verification

**Key Features:**
- Automated health status detection
- Response time monitoring
- Dependency chain validation
- Environment-specific health checks

### 2. External APIs

**File:** `external-apis.postman_collection.json`

Tests integration with external services:
- **OpenAI Whisper STT** - Speech-to-text conversion testing
- **OpenAI GPT Assessment** - CEFR evaluation testing
- **GitHub Repository** - Repository information retrieval
- **Weather Service** - Third-party API integration example

**Key Features:**
- API key validation
- Response format verification
- Error handling testing
- Rate limiting awareness

### 3. Database Operations

**File:** `database-operations.postman_collection.json`

Tests MongoDB operations (requires API endpoints):
- Session management (CRUD)
- Recording operations
- Transcript storage and retrieval
- Evaluation data management

**Note:** Returns 404 as expected since the Streamlit app doesn't expose REST API endpoints for database operations.

### 4. Development & Testing

**File:** `development-testing.postman_collection.json`

Development utilities and debugging tools:
- Configuration validation
- Test data generation
- Performance monitoring
- Debug information collection

## 🌍 Environment Configurations

### Local Environment
- **App URL:** `http://localhost:8501`
- **MongoDB:** `mongodb://localhost:27017`
- **Usage:** Development and local testing

### Docker Environment
- **App URL:** `http://app:8501`
- **MongoDB:** `mongodb://mongo:27017`
- **Usage:** Containerized testing

### Kubernetes Environment
- **App URL:** `http://localhost:30080`
- **MongoDB:** `mongodb://mongo:27017`
- **Usage:** K8s cluster testing (k3d)

## 🛠 Scripts Usage

### run-tests.sh

```bash
# Usage: ./scripts/run-tests.sh [environment] [collection] [output_format]

# Examples:
./scripts/run-tests.sh                           # All collections, local env
./scripts/run-tests.sh docker                   # All collections, docker env
./scripts/run-tests.sh local health-monitoring  # Specific collection
./scripts/run-tests.sh k8s all json             # JSON output only
```

### generate-report.sh

```bash
# Usage: ./scripts/generate-report.sh [environment] [format]

# Examples:
./scripts/generate-report.sh                    # HTML report, local env
./scripts/generate-report.sh docker json       # JSON report, docker env
./scripts/generate-report.sh k8s both          # Both formats
```

### cleanup.sh

```bash
# Usage: ./scripts/cleanup.sh [environment]

# Examples:
./scripts/cleanup.sh           # Clean local environment data
./scripts/cleanup.sh docker    # Clean docker environment data
```

## 📈 Reports

### HTML Reports
- Comprehensive visual reports with metrics
- Collection status overview
- Configuration details
- Usage instructions

### JSON Reports
- Machine-readable summaries
- API integration friendly
- CI/CD pipeline compatible

Reports are generated in the `reports/` directory with timestamps.

## 🔧 Customization

### Adding New Tests

1. **Modify Collections**: Edit the relevant `.postman_collection.json` file
2. **Update Environment**: Add new variables to environment files
3. **Test Scripts**: Update the `run-tests.sh` script if needed
4. **Documentation**: Update this README with new test details

### Environment Variables

Collections support these environment variables:
- `openai_api_key` - OpenAI API authentication
- `github_token` - GitHub API authentication
- `base_url` - Application base URL
- `mongodb_url` - MongoDB connection string

## ⚠️ Important Notes

1. **API Endpoints**: Database operations return 404 as expected since the Streamlit app doesn't expose REST endpoints
2. **API Keys**: Ensure valid OpenAI and GitHub tokens are configured
3. **Network Access**: External API tests require internet connectivity
4. **Environment Setup**: Match environment configuration with your deployment

## 🐛 Troubleshooting

### Newman Not Found
```bash
npm install -g newman
```

### Permission Denied
```bash
chmod +x scripts/*.sh
```

### Environment File Missing
Check that the environment file exists in `environments/` directory.

### API Key Issues
Verify environment variables are set:
```bash
echo $openai_api_key
echo $github_token
```

## 📚 References

- [Newman CLI Documentation](https://www.npmjs.com/package/newman)
- [Postman Documentation](https://learning.postman.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [GitHub API Documentation](https://docs.github.com/en/rest)

## 🔗 Related Issues

- **GitHub Issue #21**: Postman collections implementation
- **Main Repository**: [speak-check](https://github.com/agzyamov/speak-check)

---

**Generated as part of GitHub issue #21 implementation**