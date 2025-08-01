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

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

4. Open your browser and navigate to `http://localhost:8501`

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
├── transcribe.py       # Speech-to-text functionality using Whisper
├── evaluate.py         # AI-based CEFR scoring and evaluation
├── requirements.txt    # Python dependencies
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

#### `transcribe.py`
Handles speech-to-text conversion:
- Audio recording from microphone
- Integration with OpenAI Whisper for transcription
- Audio preprocessing and quality enhancement
- Support for multiple audio formats
- Real-time transcription capabilities

#### `evaluate.py`
Provides AI-powered CEFR evaluation:
- Multi-criteria assessment (fluency, accuracy, lexical range, etc.)
- CEFR level prediction based on linguistic analysis
- Detailed feedback generation
- Personalized improvement recommendations
- Benchmark comparison against CEFR standards

## 🛠️ Current Status

**⚠️ This is a scaffold implementation - core functionality is not yet implemented.**

### Implemented Features
- ✅ Basic Streamlit interface structure
- ✅ CEFR level selection
- ✅ Question database with sample prompts
- ✅ Placeholder UI components
- ✅ Modular architecture

### TODO: Core Features to Implement
- 🔄 Audio recording functionality
- 🔄 Whisper integration for speech-to-text
- 🔄 AI evaluation using language models (OpenAI/Claude)
- 🔄 Real-time transcription display
- 🔄 Scoring algorithm implementation
- 🔄 Session state management
- 🔄 Progress tracking and history
- 🔄 Audio preprocessing and enhancement

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
- **OpenAI Whisper**: Speech recognition engine
- **Pandas/NumPy**: Data processing
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