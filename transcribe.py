"""
Speech Transcription Module

This module handles speech-to-text functionality for the CEFR Speaking Exam Simulator.
It provides interfaces for recording audio and converting speech to text using Whisper.
"""

from __future__ import annotations

import io
import os
import tempfile
import wave
from typing import Optional, Dict, Any, List
from pathlib import Path

# Lazy import to avoid heavy startup cost in Streamlit
_whisper_model_cache: Dict[str, Any] = {}

# TODO: Implement actual Whisper integration
# TODO: Add support for multiple speech recognition engines
# TODO: Implement real-time transcription
# TODO: Add noise reduction and audio preprocessing
# TODO: Handle multiple languages and accents
# TODO: Implement confidence scoring for transcriptions


def _ensure_whisper_installed() -> None:
    """Ensure the openai-whisper package is available, raise helpful error if not."""
    try:
        import whisper  # noqa: F401
    except Exception as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "openai-whisper is not installed. Install dependencies and ensure ffmpeg is available."
        ) from exc


def setup_whisper_model(model_size: str = "base") -> bool:
    """
    Initialize and cache the Whisper model for transcription.

    Args:
        model_size (str): "tiny", "base", "small", "medium", or "large"

    Returns:
        bool: True if setup successful, False otherwise
    """
    valid_sizes = ["tiny", "base", "small", "medium", "large"]
    if model_size not in valid_sizes:
        print(f"Invalid model size. Choose from: {valid_sizes}")
        return False

    try:
        _ensure_whisper_installed()
        import whisper

        if model_size in _whisper_model_cache:
            return True

        # fp16 is auto-managed at transcribe call; model is shared
        model = whisper.load_model(model_size)
        _whisper_model_cache[model_size] = model
        return True
    except Exception as exc:  # pragma: no cover - download/env dependent
        print(f"Failed to initialize Whisper model '{model_size}': {exc}")
        return False


def _get_model(model_size: str = "base") -> Any:
    if model_size not in _whisper_model_cache:
        ok = setup_whisper_model(model_size)
        if not ok:
            raise RuntimeError("Failed to set up Whisper model")
    return _whisper_model_cache[model_size]


def _estimate_duration_from_wav(file_path: str) -> float:
    try:
        with wave.open(file_path, "rb") as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            return float(frames) / float(rate) if rate else 0.0
    except Exception:
        return 0.0


def transcribe_audio(audio_data: bytes, language: str = "en", model_size: str = "base") -> Dict[str, Any]:
    """
    Transcribe in-memory audio bytes by writing to a temp file and using Whisper.

    Args:
        audio_data: Raw audio data (wav/mp3/m4a/ogg/flac)
        language: Language code hint for transcription
        model_size: Whisper model size

    Returns:
        Dict with transcription text, language, segments and metadata
    """
    try:
        # Write to a temporary file with a generic extension; Whisper + ffmpeg can detect
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_data)
            temp_path = tmp.name
        try:
            result = transcribe_audio_file(temp_path, language=language, model_size=model_size)
        finally:
            try:
                os.unlink(temp_path)
            except Exception:
                pass
        return result
    except Exception as exc:
        return {
            "text": "",
            "confidence": 0.0,
            "language": language,
            "duration": 0.0,
            "words": [],
            "status": "error",
            "error": f"Transcription error: {exc}",
        }


def transcribe_audio_file(
    file_path: str,
    language: str = "en",
    model_size: str = "base",
    task: str = "transcribe",
) -> Dict[str, Any]:
    """
    Transcribe audio from a file path using Whisper.

    Args:
        file_path: Path to the audio file
        language: Optional language hint (e.g., "en"); if empty/None, Whisper will detect
        model_size: Whisper model size to use
        task: "transcribe" or "translate"

    Returns:
        Dict with transcription results
    """
    try:
        path_obj = Path(file_path)
        if not path_obj.exists():
            return {"text": "", "confidence": 0.0, "status": "error", "error": f"File not found: {file_path}"}

        _ensure_whisper_installed()
        model = _get_model(model_size)

        # Run transcription. fp16=False ensures CPU compatibility
        result = model.transcribe(
            str(path_obj),
            language=language if language else None,
            task=task,
            fp16=False,
            verbose=False,
            temperature=0.0,
        )

        text: str = (result or {}).get("text", "").strip()
        segments: List[Dict[str, Any]] = (result or {}).get("segments", [])
        detected_language: Optional[str] = (result or {}).get("language")

        # Best-effort duration estimation
        duration = 0.0
        if segments:
            try:
                duration = float(segments[-1].get("end", 0.0))
            except Exception:
                duration = 0.0
        if duration == 0.0 and path_obj.suffix.lower() == ".wav":
            duration = _estimate_duration_from_wav(str(path_obj))

        # Whisper does not provide confidence by default. Leave None.
        return {
            "text": text,
            "confidence": None,
            "language": detected_language or language,
            "duration": duration,
            "segments": segments,
            "status": "ok",
            "model": model_size,
        }
    except Exception as exc:
        return {
            "text": "",
            "confidence": 0.0,
            "language": language,
            "duration": 0.0,
            "words": [],
            "status": "error",
            "error": f"Transcription error: {exc}",
        }


def get_supported_languages() -> List[str]:
    """
    Get a list of supported languages for transcription.

    Returns:
        A list of language codes supported by Whisper, if available, else a common subset
    """
    try:
        _ensure_whisper_installed()
        from whisper.tokenizer import LANGUAGES

        # LANGUAGES is a dict name->code. Return codes.
        # Some callers expect codes like 'en', 'es', etc.
        return sorted(list(LANGUAGES.values()))
    except Exception:
        # Fallback common set
        return [
            "en",
            "es",
            "fr",
            "de",
            "it",
            "pt",
            "ru",
            "ja",
            "zh",
            "ko",
        ]


def validate_audio_format(file_path: str) -> bool:
    """
    Validate if the audio file format is supported by Whisper/ffmpeg.

    Returns:
        True if extension is commonly supported
    """
    supported_formats = [".wav", ".mp3", ".m4a", ".ogg", ".flac", ".webm", ".aac"]
    return Path(file_path).suffix.lower() in supported_formats


def get_audio_duration(file_path: str) -> float:
    """Get approximate duration of an audio file in seconds (WAV only fast-path)."""
    if Path(file_path).suffix.lower() == ".wav":
        return _estimate_duration_from_wav(file_path)
    return 0.0


def preprocess_audio(audio_data: bytes) -> bytes:
    """
    Placeholder for audio preprocessing pipeline (noise reduction, normalization, etc.).
    Currently returns the input unmodified.
    """
    return audio_data


class AudioRecorder:
    """
    Class for handling real-time audio recording.

    Note: A full real-time recorder is out of scope for this module since
    recording is handled by `recording.py`. This class remains as a placeholder.
    """

    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.is_recording = False
        self.audio_buffer = io.BytesIO()

    def start_recording(self) -> bool:
        self.is_recording = True
        print("[Placeholder] Audio recording started")
        return True

    def stop_recording(self) -> bytes:
        self.is_recording = False
        print("[Placeholder] Audio recording stopped")
        return b""

    def get_recording_status(self) -> Dict[str, Any]:
        return {
            "is_recording": self.is_recording,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "buffer_size": len(self.audio_buffer.getvalue()),
            "duration": 0.0,
        }