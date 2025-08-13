"""
OpenAI Whisper API Speech-to-Text Provider

This module provides speech-to-text functionality using OpenAI's managed Whisper API.
It offers a simple interface for transcribing audio files with high accuracy.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _ensure_openai_available() -> bool:
    """Check if OpenAI client is available and API key is set."""
    try:
        import openai
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.error("OPENAI_API_KEY environment variable not set")
            return False
        return True
    except ImportError:
        logger.error("OpenAI client not installed. Run: pip install openai")
        return False

def transcribe_audio_file(
    file_path: str,
    language: str = "en",
    model: str = "whisper-1",
    response_format: str = "verbose_json"
) -> Dict[str, Any]:
    """
    Transcribe audio file using OpenAI Whisper API.
    
    Args:
        file_path: Path to the audio file
        language: Language code (e.g., "en", "es", "fr")
        model: Whisper model to use (default: "whisper-1")
        response_format: Response format ("json", "verbose_json", "text", "srt", "vtt")
        
    Returns:
        Dict with transcription results
    """
    if not _ensure_openai_available():
        return {
            "text": "",
            "status": "error",
            "error": "OpenAI client not available or API key not set"
        }
    
    try:
        import openai
        
        # Validate file exists
        path_obj = Path(file_path)
        if not path_obj.exists():
            return {
                "text": "",
                "status": "error", 
                "error": f"File not found: {file_path}"
            }
        
        # Validate file size (OpenAI has 25MB limit)
        file_size = path_obj.stat().st_size
        if file_size > 25 * 1024 * 1024:  # 25MB
            return {
                "text": "",
                "status": "error",
                "error": f"File too large ({file_size / 1024 / 1024:.1f}MB). OpenAI limit is 25MB."
            }
        
        # Open and transcribe file
        with open(file_path, "rb") as audio_file:
            logger.info(f"Transcribing {file_path} with OpenAI Whisper API")
            
            response = openai.Audio.transcribe(
                model=model,
                file=audio_file,
                language=language,
                response_format=response_format
            )
        
        # Parse response based on format
        if response_format == "verbose_json":
            return {
                "text": response.get("text", "").strip(),
                "language": response.get("language", language),
                "duration": response.get("duration", 0.0),
                "segments": response.get("segments", []),
                "status": "ok",
                "model": model,
                "provider": "openai"
            }
        else:
            # Simple text response
            return {
                "text": response.strip() if isinstance(response, str) else "",
                "language": language,
                "duration": 0.0,
                "segments": [],
                "status": "ok", 
                "model": model,
                "provider": "openai"
            }
            
    except Exception as e:
        logger.error(f"OpenAI transcription error: {e}")
        return {
            "text": "",
            "status": "error",
            "error": f"Transcription failed: {str(e)}"
        }

def transcribe_audio_bytes(
    audio_data: bytes,
    language: str = "en", 
    model: str = "whisper-1",
    response_format: str = "verbose_json"
) -> Dict[str, Any]:
    """
    Transcribe audio bytes using OpenAI Whisper API.
    
    Args:
        audio_data: Raw audio data
        language: Language code
        model: Whisper model to use
        response_format: Response format
        
    Returns:
        Dict with transcription results
    """
    if not _ensure_openai_available():
        return {
            "text": "",
            "status": "error",
            "error": "OpenAI client not available or API key not set"
        }
    
    try:
        import openai
        import tempfile
        
        # Write bytes to temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_data)
            temp_path = tmp.name
        
        try:
            result = transcribe_audio_file(temp_path, language, model, response_format)
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except Exception:
                pass
        
        return result
        
    except Exception as e:
        logger.error(f"OpenAI transcription error: {e}")
        return {
            "text": "",
            "status": "error",
            "error": f"Transcription failed: {str(e)}"
        }

def get_supported_languages() -> List[str]:
    """
    Get list of supported language codes for OpenAI Whisper.
    
    Returns:
        List of supported language codes
    """
    # OpenAI Whisper supports 99+ languages
    # Return most common ones for UI
    return [
        "en", "es", "fr", "de", "it", "pt", "ru", "ja", "zh", "ko",
        "ar", "hi", "nl", "pl", "sv", "da", "no", "fi", "tr", "he"
    ]

def validate_audio_format(file_path: str) -> bool:
    """
    Validate if audio file format is supported by OpenAI Whisper.
    
    Args:
        file_path: Path to audio file
        
    Returns:
        True if format is supported
    """
    supported_formats = [".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".wav", ".webm"]
    return Path(file_path).suffix.lower() in supported_formats

def get_audio_duration(file_path: str) -> float:
    """
    Get audio duration in seconds (placeholder - OpenAI doesn't provide this before transcription).
    
    Args:
        file_path: Path to audio file
        
    Returns:
        Duration in seconds (0.0 if cannot determine)
    """
    try:
        import wave
        if Path(file_path).suffix.lower() == ".wav":
            with wave.open(file_path, "rb") as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                return float(frames) / float(rate) if rate else 0.0
    except Exception:
        pass
    return 0.0

def is_available() -> bool:
    """
    Check if OpenAI STT is available (client installed and API key set).
    
    Returns:
        True if available
    """
    return _ensure_openai_available()
