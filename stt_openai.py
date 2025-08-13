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
        from openai import OpenAI  # noqa: F401
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.error("OPENAI_API_KEY environment variable not set")
            return False
        return True
    except Exception:
        logger.error("OpenAI client not installed. Run: pip install openai")
        return False


def _response_to_dict(response: Any) -> Dict[str, Any]:
    """Best-effort conversion of OpenAI response objects to a dict."""
    if isinstance(response, dict):
        return response
    for attr in ("model_dump", "to_dict"):
        fn = getattr(response, attr, None)
        if callable(fn):
            try:
                return fn()
            except Exception:
                pass
    # Fallback minimal mapping
    text = getattr(response, "text", "")
    return {"text": text}


def transcribe_audio_file(
    file_path: str,
    language: str = "en",
    model: str = "whisper-1",
    response_format: str = "verbose_json"
) -> Dict[str, Any]:
    """
    Transcribe audio file using OpenAI Whisper API (new client interface).
    """
    if not _ensure_openai_available():
        return {
            "text": "",
            "status": "error",
            "error": "OpenAI client not available or API key not set"
        }

    try:
        from openai import OpenAI

        # Validate file exists
        path_obj = Path(file_path)
        if not path_obj.exists():
            return {"text": "", "status": "error", "error": f"File not found: {file_path}"}

        # Validate file size (OpenAI has ~25MB limit for many audio formats)
        file_size = path_obj.stat().st_size
        if file_size > 25 * 1024 * 1024:  # 25MB
            return {
                "text": "",
                "status": "error",
                "error": f"File too large ({file_size / 1024 / 1024:.1f}MB). Limit is 25MB."
            }

        client = OpenAI()

        with open(file_path, "rb") as audio_file:
            logger.info(f"Transcribing {file_path} with OpenAI (model={model})")
            response = client.audio.transcriptions.create(
                model=model,
                file=audio_file,
                language=language,
                response_format=response_format,
            )

        data = _response_to_dict(response)
        text = data.get("text") or getattr(response, "text", "")
        detected_language = data.get("language", language)
        duration = data.get("duration", 0.0)
        segments = data.get("segments", [])

        return {
            "text": (text or "").strip(),
            "language": detected_language,
            "duration": duration,
            "segments": segments,
            "status": "ok",
            "model": model,
            "provider": "openai",
        }

    except Exception as e:
        logger.error(f"OpenAI transcription error: {e}")
        return {"text": "", "status": "error", "error": f"Transcription failed: {str(e)}"}


def transcribe_audio_bytes(
    audio_data: bytes,
    language: str = "en",
    model: str = "whisper-1",
    response_format: str = "verbose_json"
) -> Dict[str, Any]:
    """Transcribe audio bytes using OpenAI Whisper API."""
    if not _ensure_openai_available():
        return {"text": "", "status": "error", "error": "OpenAI client not available or API key not set"}

    try:
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_data)
            temp_path = tmp.name
        try:
            return transcribe_audio_file(temp_path, language, model, response_format)
        finally:
            try:
                os.unlink(temp_path)
            except Exception:
                pass
    except Exception as e:
        logger.error(f"OpenAI transcription error: {e}")
        return {"text": "", "status": "error", "error": f"Transcription failed: {str(e)}"}


def get_supported_languages() -> List[str]:
    """Common language codes for UI selection."""
    return [
        "en", "es", "fr", "de", "it", "pt", "ru", "ja", "zh", "ko",
        "ar", "hi", "nl", "pl", "sv", "da", "no", "fi", "tr", "he",
    ]


def validate_audio_format(file_path: str) -> bool:
    supported_formats = [".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".wav", ".webm"]
    return Path(file_path).suffix.lower() in supported_formats


def get_audio_duration(file_path: str) -> float:
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
    return _ensure_openai_available()
