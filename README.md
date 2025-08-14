# CEFR Speaking Exam Simulator 🎤

A web-based application that simulates the speaking component of CEFR (Common European Framework of Reference) English language exams. This tool helps learners practice and assess their speaking skills at levels A2 through C1 using AI-powered evaluation.

## 🎯 Purpose

The CEFR Speaking Exam Simulator provides:

- **Authentic Practice**: Realistic speaking prompts aligned with CEFR standards
- **AI Assessment**: Automated evaluation of speaking performance using advanced language models
- **Instant Feedback**: Immediate scoring and detailed recommendations for improvement
- **Level Progression**: Structured practice from A2 (Elementary) to C1 (Advanced)
- **Accessibility**: Web-based interface accessible from any modern browser

## 🚀 Usage

### Prerequisites

- Python 3.8 or higher
- Microphone access for audio recording
- Modern web browser

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd speak-check
```

2. Create and activate virtual environment:
```bash
python -m venv venv
./venv/bin/Activate.ps1  # On Windows PowerShell
# or source venv/bin/activate  # On Unix/macOS bash
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. **Start the server (Tremlett command):**
```bash
./venv/bin/Activate.ps1 && python -m streamlit run app.py --server.port 8501 --server.headless true
```

5. Open your browser and navigate to `http://localhost:8501`

### How to Use

1. **Select CEFR Level**: Choose your target level (A2, B1, B2, or C1) from the dropdown
2. **Start Test**: Click "Start Speaking Test" to begin
3. **Read Prompt**: Review the speaking question displayed
4. **Record Response**: Use the recording controls to capture your spoken answer
5. **Get Feedback**: Receive AI-generated evaluation and recommendations

## 📁 File Structure

```
speak-check/
├── app.py              # Main Streamlit application entry point
├── questions.py        # CEFR-level speaking prompts and question management
├── tts.py              # Text-to-Speech functionality (Microsoft Edge TTS)
├── recording.py        # Voice recording functionality (PyAudio)
├── stt_openai.py       # Speech-to-text functionality (OpenAI Whisper API)
├── eval_openai.py      # AI-based CEFR assessment (OpenAI GPT)
├── evaluate.py         # AI-based CEFR scoring and evaluation
├── test_recording.py   # Voice recording test script
├── requirements.txt    # Python dependencies
├── TECH_PRACTICES.md   # Technical practices and conventions
└── README.md          # Project documentation
```

### File Descriptions

#### `app.py`
The main Streamlit application providing the web interface. Features:
- CEFR level selection dropdown
- Speaking test interface with recording controls
- Real-time transcript display
- AI evaluation results presentation
- Session progress tracking

#### `questions.py`
Manages speaking prompts organized by CEFR levels:
- Database of level-appropriate questions (A2-C1)
- Random question selection
- Question metadata and categorization
- Extensible structure for adding new prompts

#### `tts.py`
Text-to-Speech functionality with premium voice quality:
- Microsoft Edge TTS integration (8 high-quality neural voices)
- Thread-safe async operations for Streamlit compatibility
- Voice selection, speed, and volume controls
- Graceful fallback chain (Edge TTS → pyttsx3 → gTTS → System)
- Temporary file management with automatic cleanup

#### `recording.py`
Professional voice recording capabilities:
- PyAudio integration for cross-platform audio capture
- Multiple quality settings (Low/Medium/High)
- Session-based recording management
- Audio playback functionality
- Thread-safe operations with progress tracking
- WAV file generation with configurable parameters

#### `stt_openai.py`
Handles speech-to-text conversion using OpenAI Whisper API:
- Managed transcription service (no local model downloads)
- Support for multiple audio formats (WAV, MP3, M4A, etc.)
- Language detection and selection
- High accuracy transcription with confidence scoring
- Cloud-based processing for scalability
- Automatic error handling and retry logic

#### `eval_openai.py`
Provides AI-powered CEFR assessment (OpenAI GPT):
- Multi-criteria assessment (fluency, accuracy, lexical range, etc.)
- CEFR level prediction based on linguistic analysis
- Detailed feedback generation
- Personalized improvement recommendations
- Benchmark comparison against CEFR standards

#### `evaluate.py`
Provides AI-powered CEFR evaluation:
 - Multi-criteria assessment (fluency, accuracy, lexical range, etc.)
 - CEFR level prediction based on linguistic analysis
 - Detailed feedback generation
 - Personalized improvement recommendations
 - Benchmark comparison against CEFR standards

## 🛠️ Current Status

**🎉 Core functionality implemented - Full speaking exam simulation available!**

### ✅ Implemented Features
- ✅ **Complete Streamlit interface** with modern UI design
- ✅ **CEFR level selection** (A2, B1, B2, C1) with descriptions
- ✅ **Premium Text-to-Speech** using Microsoft Edge TTS (8 high-quality voices)
- ✅ **Voice Recording** with PyAudio integration (up to 2 minutes)
- ✅ **Audio Playback** of recorded responses
- ✅ **Speech-to-Text** using OpenAI Whisper API (managed service)
- ✅ **Session Management** with unique session IDs
- ✅ **Question Database** with level-appropriate prompts
- ✅ **Real-time Status** indicators and progress tracking
- ✅ **Audio Quality Controls** (speed, volume, voice selection)
- ✅ **Thread-safe Operations** with robust error handling
- ✅ **Modular Architecture** with clean separation of concerns
- ✅ **AI Assessment** using OpenAI GPT for detailed feedback

### 🔄 TODO: Advanced Features to Implement
- 🔄 **AI evaluation** using language models (OpenAI/Claude)
- 🔄 **CEFR scoring algorithm** with detailed feedback
- 🔄 **Pronunciation analysis** and fluency assessment
- 🔄 **Recording history** and progress analytics

### TODO: Advanced Features
- 🔄 Pronunciation analysis
- 🔄 Multi-language support
- 🔄 Detailed linguistic analysis
- 🔄 Custom evaluation criteria
- 🔄 Export functionality for results
- 🔄 User authentication and profiles
- 🔄 Performance analytics and trends

## 🎓 CEFR Levels Supported

### A2 (Elementary)
- Basic personal information and familiar topics
- Simple descriptions of people, places, and activities
- 50+ words typical response length

### B1 (Intermediate)
- Connected speech on familiar topics
- Personal experiences and future plans
- 100+ words typical response length

### B2 (Upper-Intermediate)
- Complex topics with spontaneous interaction
- Abstract concepts and detailed explanations
- 150+ words typical response length

### C1 (Advanced)
- Sophisticated language use with flexibility
- Complex argumentation and subtle meaning
- 200+ words typical response length

## 🔧 Technical Architecture

### Dependencies
- **Streamlit**: Web interface framework
- **Microsoft Edge TTS**: Premium text-to-speech synthesis
- **PyAudio**: Cross-platform audio recording and playback
- **NumPy**: Audio processing and data manipulation
- **Pygame**: Audio file playback for TTS
- **OpenAI**: Whisper API for speech-to-text transcription
- **SpaCy/NLTK**: Natural language processing (planned)
- **OpenAI/Anthropic APIs**: AI evaluation (planned)

### Design Principles
- **Modular Architecture**: Separated concerns for UI, transcription, and evaluation
- **Extensible**: Easy to add new question types, evaluation criteria, and languages
- **User-Friendly**: Intuitive interface suitable for language learners
- **Scalable**: Architecture supports future enhancements and features

## 🤝 Contributing

This project is in early development. Key areas for contribution:
- Audio processing and recording implementation
- AI evaluation algorithm development
- Question database expansion
- UI/UX improvements
- Testing and validation

## 📝 License

[Add license information here]

## 🆘 Support

For questions, issues, or feature requests, please [create an issue](../../issues) in the repository.

---

**Note**: This application is designed for educational purposes and speaking practice. It does not replace official CEFR certification exams.

## 🗣️ Speech-to-Text (OpenAI Whisper API)

The app now supports managed speech transcription using OpenAI's Whisper API:

### Setup Requirements
- **OpenAI API Key**: Set the `OPENAI_API_KEY` environment variable
- **Internet Connection**: Required for API calls to OpenAI
- **Audio Format**: Supports WAV, MP3, M4A, MPEG, MPGA, WebM (up to 25MB)

### How to Use
1. Set your OpenAI API key: `export OPENAI_API_KEY="your-api-key-here"`
2. Enable "Speech-to-Text" in the sidebar settings
3. Record your response using the recording controls
4. Click "Transcribe Recording" to get your speech converted to text
5. The transcript will appear in the text area with metadata

### Features
- **High Accuracy**: Uses OpenAI's latest Whisper model
- **Language Support**: 99+ languages with automatic detection
- **Cloud Processing**: No local model downloads or GPU requirements
- **Error Handling**: Graceful fallbacks and user-friendly error messages
- **Metadata**: Shows duration, segments, and detected language

### Cost Considerations
- OpenAI Whisper API charges per minute of audio processed
- Current pricing: ~$0.006 per minute (very affordable for practice)
- No charges for failed transcriptions or API errors

## 🤖 AI Assessment (OpenAI GPT)

The app now provides AI-powered CEFR level assessment using OpenAI's GPT models:

### Setup Requirements
- **OpenAI API Key**: Same key used for STT (set `OPENAI_API_KEY` in `.env`)
- **Internet Connection**: Required for API calls to OpenAI
- **Transcript**: Requires a transcribed speech response

### How to Use
1. Enable "AI Assessment" in the sidebar settings
2. Complete a recording and transcription (see STT section above)
3. Click "Evaluate Response" to get detailed AI feedback
4. Review your CEFR level, scores, and personalized recommendations

### Assessment Criteria
- **Fluency**: Natural flow, hesitations, speech rate
- **Accuracy**: Grammatical correctness, vocabulary precision
- **Grammar**: Sentence structure complexity, error patterns
- **Vocabulary**: Word choice, lexical range, sophistication
- **Coherence**: Logical organization, topic relevance, completeness

### Features
- **CEFR Level Prediction**: AI-determined proficiency level (A2-C1)
- **Detailed Scoring**: 0-10 scale for each assessment criterion
- **Personalized Feedback**: Strengths, areas for improvement, and actionable tips
- **Confidence Scoring**: Assessment reliability indicator
- **Fallback Mode**: Basic assessment when API is unavailable

### Cost Considerations
- OpenAI GPT API charges per token processed
- Current pricing: ~$0.0001 per 1K tokens (very affordable)
- Typical assessment: 500-1000 tokens per evaluation