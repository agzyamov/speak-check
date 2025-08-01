# Technical Practices Guide

## CEFR Speaking Exam Simulator - Development Standards & Conventions

### 📋 Table of Contents
- [Project Overview](#project-overview)
- [Development Environment](#development-environment)
- [Code Style & Conventions](#code-style--conventions)
- [Project Structure](#project-structure)
- [Git Workflow](#git-workflow)
- [UI/UX Patterns](#uiux-patterns)
- [Architecture Decisions](#architecture-decisions)
- [Testing Strategy](#testing-strategy)
- [Dependencies](#dependencies)
- [Documentation Standards](#documentation-standards)

---

## 🎯 Project Overview

**Tech Stack:**
- **Frontend**: Streamlit (Python web framework)
- **Backend**: Python modules (questions, transcribe, evaluate)
- **Environment**: Python 3.13 + Virtual Environment
- **IDE**: VS Code with Python/Pylance extensions
- **Version Control**: Git with feature branch workflow

**Core Principles:**
- Modular architecture with clear separation of concerns
- User-centric design focused on language learning
- Progressive enhancement (start simple, add features incrementally)
- Accessibility and multilingual support

---

## 🛠️ Development Environment

### **Python Environment Setup**
```bash
# Virtual Environment (Required)
python3 -m venv venv
./venv/bin/Activate.ps1  # PowerShell
# OR
source venv/bin/activate  # Bash/Zsh

# Dependencies Installation
pip install -r requirements.txt
```

### **VS Code Configuration**
```json
{
    "python.pythonPath": "./venv/bin/python",
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true
}
```

### **Required Extensions**
- Python (Microsoft)
- Pylance (Microsoft)
- Python Docstring Generator
- GitLens
- Streamlit Snippets (optional)

---

## 📝 Code Style & Conventions

### **Python Code Style**
- **PEP 8** compliance with 88-character line limit
- **Type hints** for all function parameters and return values
- **Docstrings** for all modules, classes, and functions (Google style)
- **F-strings** for string formatting
- **Descriptive variable names** (no abbreviations)

### **Example Function Structure**
```python
def evaluate_speaking_response(
    transcript: str,
    target_level: str,
    question: str,
    audio_duration: float = 0.0
) -> EvaluationResult:
    """
    Evaluate a speaking response according to CEFR standards.
    
    Args:
        transcript: Transcribed text of the speaking response
        target_level: Target CEFR level (A2, B1, B2, C1)
        question: The original speaking prompt/question
        audio_duration: Duration of the audio response in seconds
        
    Returns:
        EvaluationResult: Comprehensive evaluation results
    """
    # Implementation here
    pass
```

### **Naming Conventions**
- **Functions**: `snake_case` (e.g., `get_question_by_level`)
- **Classes**: `PascalCase` (e.g., `EvaluationResult`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `QUESTIONS_DB`)
- **Variables**: `snake_case` (e.g., `cefr_level`)
- **Private methods**: `_leading_underscore` (e.g., `_calculate_score`)

### **Import Organization**
```python
# Standard library imports
import io
from typing import Dict, List, Any, Optional
from pathlib import Path

# Third-party imports
import streamlit as st
import pandas as pd

# Local application imports
from questions import get_question_by_level
from transcribe import transcribe_audio
```

---

## 📁 Project Structure

```
speak-check/
├── app.py                  # Main Streamlit application
├── questions.py            # Question management & CEFR prompts
├── transcribe.py          # Speech-to-text functionality
├── evaluate.py            # AI-based CEFR evaluation
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── TECH_PRACTICES.md     # This file
├── .vscode/
│   └── settings.json     # VS Code workspace settings
├── venv/                 # Virtual environment (gitignored)
└── .gitignore           # Git ignore patterns
```

### **Module Responsibilities**
- **`app.py`**: UI layer, session state, Streamlit components
- **`questions.py`**: Question database, CEFR-level content management
- **`transcribe.py`**: Audio processing, speech recognition, Whisper integration
- **`evaluate.py`**: Language assessment, CEFR scoring, AI evaluation

---

## 🌿 Git Workflow

### **Branch Strategy**
- **`main`**: Production-ready code, tagged releases
- **`basic-streamlit-app`**: Core UI features (completed)
- **`tts-question-playback`**: TTS functionality (current)
- **Feature branches**: `feature-name` or `component-name`

### **Commit Message Format**
```
type(scope): description

feat(ui): add CEFR level dropdown with descriptions
fix(tts): resolve audio playback state management
docs(readme): update installation instructions
refactor(evaluate): simplify scoring algorithm
test(questions): add unit tests for question retrieval
```

### **Pull Request Process**
1. Create feature branch from latest `main`
2. Implement feature with tests and documentation
3. Ensure all linting passes
4. Create PR with detailed description
5. Code review and approval
6. Merge to `main` with squash commits

---

## 🎨 UI/UX Patterns

### **Streamlit Component Guidelines**

#### **Layout Structure**
```python
# Consistent page configuration
st.set_page_config(
    page_title="CEFR Speaking Exam Simulator",
    page_icon="🎤",
    layout="wide"
)

# Two-column layout pattern
col1, col2 = st.columns([2, 1])  # Main content : Sidebar info
```

#### **Component Naming**
- **Buttons**: Action-oriented with emoji prefix (`🎯 Start Speaking Test`)
- **Headers**: Clear hierarchy with emoji indicators (`📝 Speaking Prompt`)
- **Status indicators**: Color-coded with emoji (`✅ Test Active`, `⏳ Test Not Started`)

#### **State Management**
```python
# Session state initialization pattern
if 'test_started' not in st.session_state:
    st.session_state.test_started = False

# State updates with rerun
if st.button("Start Test"):
    st.session_state.test_started = True
    st.rerun()
```

#### **Visual Feedback**
- **Success**: `st.success()` with green checkmark
- **Warning**: `st.warning()` with yellow caution
- **Info**: `st.info()` with blue information
- **Error**: `st.error()` with red X

### **Accessibility Standards**
- Clear visual hierarchy with proper heading levels
- High contrast color schemes
- Keyboard navigation support
- Screen reader friendly text alternatives
- Multi-language support for international users

---

## 🏗️ Architecture Decisions

### **Design Patterns**

#### **Module Architecture**
- **Separation of Concerns**: UI, business logic, data access clearly separated
- **Dependency Injection**: Functions accept dependencies as parameters
- **Stateless Functions**: Pure functions where possible, state managed at UI layer

#### **Data Flow**
```
User Input → Streamlit UI → Python Modules → Processing → UI Update
```

#### **Error Handling**
```python
def safe_operation(data: str) -> Dict[str, Any]:
    """Standard error handling pattern."""
    try:
        result = process_data(data)
        return {"success": True, "data": result}
    except SpecificException as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}
```

### **Performance Considerations**
- **Caching**: Use `@st.cache_data` for expensive operations
- **Lazy Loading**: Load components only when needed
- **Session State**: Minimize state storage, prefer computation over storage
- **Memory Management**: Clean up resources after use

---

## 🧪 Testing Strategy

### **Testing Pyramid**
1. **Unit Tests**: Individual function testing
2. **Integration Tests**: Module interaction testing
3. **UI Tests**: Streamlit component testing
4. **End-to-End Tests**: Full workflow testing

### **Test Organization**
```
tests/
├── unit/
│   ├── test_questions.py
│   ├── test_transcribe.py
│   └── test_evaluate.py
├── integration/
│   └── test_app_integration.py
└── e2e/
    └── test_user_workflows.py
```

### **Test Conventions**
```python
def test_get_question_by_level_returns_appropriate_question():
    """Test function names describe behavior, not implementation."""
    # Arrange
    level = "B1"
    
    # Act
    question = get_question_by_level(level)
    
    # Assert
    assert isinstance(question, str)
    assert len(question) > 10  # Reasonable question length
```

---

## 📦 Dependencies

### **Core Dependencies**
```python
# Web Framework
streamlit>=1.47.0

# Data Processing
pandas>=2.1.0
numpy>=2.3.0

# Audio Processing (Future)
# openai-whisper>=20231117
# pyaudio>=0.2.11

# Development
# pytest>=7.4.0
# black>=23.0.0
# flake8>=6.0.0
```

### **Dependency Management**
- **Pin major versions** to avoid breaking changes
- **Regular updates** with testing before deployment
- **Virtual environment isolation** for all development
- **Minimal dependencies** - only add what's necessary

---

## 📚 Documentation Standards

### **Code Documentation**
- **Docstrings**: Google style for all public functions
- **Inline comments**: For complex logic explanation
- **Type hints**: For all function signatures
- **README updates**: For new features and setup changes

### **File Headers**
```python
"""
Module Name - Brief Description

Detailed description of module purpose and functionality.
Used for CEFR Speaking Exam Simulator project.
"""
```

### **TODO Comments**
```python
# TODO: Implement actual Whisper integration
# TODO: Add error handling for network issues
# FIXME: Handle edge case when audio file is corrupted
# NOTE: This requires API key configuration
```

### **Configuration Documentation**
- Environment setup instructions
- API key configuration steps
- Deployment procedures
- Troubleshooting common issues

---

## 🔧 Development Commands

### **Common Commands**
```bash
# Start development server
./venv/bin/Activate.ps1
python -m streamlit run app.py

# Code quality checks
flake8 .
black --check .
mypy .

# Testing
pytest tests/
pytest --cov=. tests/

# Dependencies
pip freeze > requirements.txt
pip install -r requirements.txt
```

### **Git Commands**
```bash
# Feature development
git checkout -b feature-name
git add .
git commit -m "feat(scope): description"
git push origin feature-name

# Branch management
git checkout main
git pull origin main
git branch -d feature-name
```

---

## 🎯 Best Practices Summary

1. **Code Quality**: Write clean, readable, well-documented code
2. **Testing**: Test early and often, aim for high coverage
3. **Version Control**: Use meaningful commits and branch names
4. **User Experience**: Prioritize accessibility and usability
5. **Performance**: Profile and optimize when necessary
6. **Security**: Validate inputs, handle errors gracefully
7. **Documentation**: Keep docs up-to-date with code changes
8. **Collaboration**: Use consistent patterns and conventions

---

## 🔄 Continuous Improvement

This document should be updated as the project evolves. When adding new patterns, tools, or conventions:

1. Document the decision rationale
2. Update relevant sections
3. Communicate changes to the team
4. Ensure backward compatibility when possible
5. Provide migration guides for breaking changes

---

*Last Updated: August 2025*
*Version: 1.0*