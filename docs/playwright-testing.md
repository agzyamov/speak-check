# Playwright UI Automation Testing

## Overview

Playwright MCP integration for automated UI testing of the CEFR Speaking Exam Simulator.

## Setup

### Prerequisites
- Node.js 18+
- Streamlit app running on `http://localhost:8501`

### Installation
```bash
npm install
npm run install-browsers
```

### MCP Configuration

Configured in `.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp"]
    }
  }
}
```

## Running Tests

```bash
npm test              # Run all tests
npm run test:smoke    # Run basic smoke tests
npm run test:headed   # Run with browser UI visible
npm run show-report   # View test results
```

## Implementation

- ✅ Playwright MCP server configured
- ✅ Basic smoke tests implemented
- ✅ Cross-browser testing setup
- ✅ Screenshot capture on failures
- ✅ CI-ready configuration

Implements GitHub issue #15.