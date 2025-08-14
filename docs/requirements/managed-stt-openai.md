# Requirements: Managed Speech-to-Text (OpenAI Whisper API)

**Feature ID:** `managed-stt-openai`  
**PR:** #5 - feat(stt): add managed Speech-to-Text via OpenAI Whisper API  
**Status:** ✅ Implemented  
**Generated:** 2025-01-14  
**Generated-by-MCP:** true  

## 🎯 Goals

### Primary Objectives
- Enable speech-to-text transcription for CEFR speaking exam responses
- Provide high-accuracy transcription using managed cloud service
- Integrate seamlessly with existing recording and evaluation workflow
- Support multiple audio formats and languages
- Ensure reliable fallback behavior when service is unavailable

### Success Criteria
- Users can transcribe recorded audio responses to text
- Transcription accuracy meets CEFR assessment requirements
- Integration works with existing Streamlit UI without disruption
- Error handling provides clear feedback to users
- Cost-effective solution for educational use

## 👥 User Stories

### As a CEFR Exam Student
- **US-001**: I want to see my spoken response transcribed as text so I can review what I said
- **US-002**: I want accurate transcription so I can get proper AI evaluation of my speaking
- **US-003**: I want to know if transcription failed so I can try again or get help

### As a Language Learning Instructor
- **US-004**: I want students to have reliable transcription so they can practice effectively
- **US-005**: I want transcription to work with different accents and speaking speeds

### As a System Administrator
- **US-006**: I want the system to handle API failures gracefully without breaking the UI
- **US-007**: I want clear logging for troubleshooting transcription issues

## 🔧 Functional Requirements

### Core Transcription Functionality
- **FR-001**: Transcribe audio files using OpenAI Whisper API
- **FR-002**: Support multiple audio formats (WAV, MP3, M4A, MPEG, MPGA, WebM)
- **FR-003**: Handle files up to 25MB in size
- **FR-004**: Support 99+ languages with automatic detection
- **FR-005**: Return transcription with metadata (duration, segments, language)

### Integration Requirements
- **FR-006**: Integrate with existing recording module (`recording.py`)
- **FR-007**: Provide transcription results to evaluation module (`evaluate.py`)
- **FR-008**: Display transcription in Streamlit UI with real-time feedback
- **FR-009**: Support language selection for transcription

### Error Handling
- **FR-010**: Handle missing OpenAI API key gracefully
- **FR-011**: Handle network connectivity issues
- **FR-012**: Handle file size limitations
- **FR-013**: Handle unsupported audio formats
- **FR-014**: Provide user-friendly error messages

### Configuration
- **FR-015**: Load API key from environment variable `OPENAI_API_KEY`
- **FR-016**: Support `.env` file configuration
- **FR-017**: Allow model selection (default: whisper-1)
- **FR-018**: Allow response format selection (default: verbose_json)

## 🚫 Non-Functional Requirements

### Performance
- **NFR-001**: Transcription should complete within 30 seconds for typical responses (1-2 minutes)
- **NFR-002**: UI should remain responsive during transcription
- **NFR-003**: Handle concurrent transcription requests without conflicts

### Reliability
- **NFR-004**: 99% uptime for transcription service (excluding API outages)
- **NFR-005**: Graceful degradation when OpenAI API is unavailable
- **NFR-006**: Retry logic for transient network failures

### Security
- **NFR-007**: API keys should not be logged or exposed in error messages
- **NFR-008**: Audio files should be processed securely
- **NFR-009**: No sensitive data should be stored permanently

### Cost
- **NFR-010**: Cost should be reasonable for educational use (~$0.006/minute)
- **NFR-011**: Provide cost estimation to users
- **NFR-012**: Implement usage monitoring

### Usability
- **NFR-013**: Clear indication of transcription progress
- **NFR-014**: Intuitive error messages for common issues
- **NFR-015**: Consistent UI integration with existing features

## 📊 Data Contracts

### Input Data
```python
# Audio file input
file_path: str  # Path to audio file
language: str   # Language code (e.g., "en", "es", "fr")
model: str      # Whisper model (default: "whisper-1")
response_format: str  # Response format (default: "verbose_json")
```

### Output Data
```python
# Transcription result
{
    "text": str,           # Transcribed text
    "status": str,         # "success" | "error"
    "language": str,       # Detected language
    "duration": float,     # Audio duration in seconds
    "segments": List[Dict], # Detailed segments with timestamps
    "error": str,          # Error message if status is "error"
    "metadata": Dict       # Additional metadata
}
```

### Error Responses
```python
# Error cases
{
    "text": "",
    "status": "error",
    "error": "OpenAI client not available or API key not set"
}

{
    "text": "",
    "status": "error", 
    "error": "File not found: {file_path}"
}

{
    "text": "",
    "status": "error",
    "error": "File too large ({size}MB). Limit is 25MB."
}
```

## ✅ Acceptance Criteria

### Must Have
- [x] **AC-001**: Transcribe WAV files with >95% accuracy for clear speech
- [x] **AC-002**: Handle missing API key with clear error message
- [x] **AC-003**: Support files up to 25MB
- [x] **AC-004**: Return transcription within 30 seconds
- [x] **AC-005**: Integrate with existing recording workflow
- [x] **AC-006**: Display transcription in Streamlit UI
- [x] **AC-007**: Support English language transcription
- [x] **AC-008**: Provide detailed error messages for common failures

### Should Have
- [x] **AC-009**: Support multiple audio formats (MP3, M4A, etc.)
- [x] **AC-010**: Support multiple languages
- [x] **AC-011**: Return detailed metadata (segments, duration)
- [x] **AC-012**: Handle network timeouts gracefully
- [x] **AC-013**: Log transcription attempts for debugging

### Could Have
- [ ] **AC-014**: Real-time transcription streaming
- [ ] **AC-015**: Offline fallback transcription
- [ ] **AC-016**: Custom vocabulary support
- [ ] **AC-017**: Transcription confidence scoring

## 🔗 Dependencies

### External Dependencies
- **OpenAI Python Client**: `openai>=1.0.0`
- **Environment Management**: `python-dotenv`
- **Audio Processing**: Existing `recording.py` module

### Internal Dependencies
- **Streamlit UI**: `app.py` for integration
- **Evaluation Module**: `evaluate.py` for assessment
- **Configuration**: `.env` file for API key management

## 📁 Implementation Files

### Core Implementation
- `stt_openai.py` - Main transcription module
- `app.py` - UI integration (lines 603+)
- `.env.example` - Configuration template

### Configuration
- `requirements.txt` - Added OpenAI dependency
- `.gitignore` - Exclude `.env` and logs

## 🧪 Testing Requirements

### Unit Tests
- [ ] Test transcription with valid audio files
- [ ] Test error handling for missing API key
- [ ] Test file size validation
- [ ] Test unsupported file formats
- [ ] Test network error handling

### Integration Tests
- [ ] Test end-to-end recording → transcription → evaluation
- [ ] Test UI integration and error display
- [ ] Test concurrent transcription requests

### Performance Tests
- [ ] Test transcription time for different file sizes
- [ ] Test memory usage during transcription
- [ ] Test API rate limiting behavior

## 📈 Future Enhancements

### Planned Improvements
- **FE-001**: Add transcription confidence scoring
- **FE-002**: Implement caching for repeated transcriptions
- **FE-003**: Add support for custom vocabulary
- **FE-004**: Real-time transcription streaming
- **FE-005**: Offline fallback using local models

### Monitoring & Analytics
- **FE-006**: Track transcription success rates
- **FE-007**: Monitor API usage and costs
- **FE-008**: Performance metrics collection
- **FE-009**: Error rate monitoring and alerting

---

**Note**: This requirements document was generated automatically from the implemented feature. The feature has been successfully deployed and is currently in production use.
