"""
Text-to-Speech Module for CEFR Speaking Exam Simulator

This module provides text-to-speech functionality for reading speaking prompts aloud.
Supports multiple TTS engines with fallback options for cross-platform compatibility.
"""

import threading
import time
from typing import Dict, List, Optional, Any
from enum import Enum
import logging

# TTS Engine imports (with graceful fallbacks)
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    pyttsx3 = None

try:
    from gtts import gTTS
    import pygame
    import io
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    gTTS = None
    pygame = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TTSEngine(Enum):
    """Available TTS engines."""
    PYTTSX3 = "pyttsx3"
    GTTS = "gtts"
    SYSTEM = "system"

class TTSState(Enum):
    """TTS playback states."""
    IDLE = "idle"
    SPEAKING = "speaking"
    PAUSED = "paused"
    STOPPED = "stopped"

class TTSManager:
    """
    Manages text-to-speech functionality with multiple engine support.
    
    Features:
    - Multiple TTS engine support (pyttsx3, gTTS)
    - Asynchronous playback with threading
    - Voice configuration (rate, volume, voice selection)
    - Playback state management (play, pause, stop)
    - Error handling and graceful fallbacks
    """
    
    def __init__(self, engine: Optional[TTSEngine] = None):
        """
        Initialize TTS manager with specified engine.
        
        Args:
            engine: Preferred TTS engine, auto-detects if None
        """
        self.state = TTSState.IDLE
        self.current_thread: Optional[threading.Thread] = None
        self.stop_requested = False
        
        # Engine selection and initialization
        self.engine_type = engine or self._detect_best_engine()
        self.engine = self._initialize_engine()
        
        # Voice settings
        self.settings = {
            "rate": 150,  # Words per minute
            "volume": 0.8,  # Volume level (0.0 to 1.0)
            "voice_index": 0,  # Voice selection index
            "language": "en"  # Language code
        }
        
        # Apply initial settings
        self._configure_engine()
    
    def _detect_best_engine(self) -> TTSEngine:
        """
        Detect the best available TTS engine.
        
        Returns:
            TTSEngine: Best available engine
        """
        if PYTTSX3_AVAILABLE:
            logger.info("Using pyttsx3 TTS engine")
            return TTSEngine.PYTTSX3
        elif GTTS_AVAILABLE:
            logger.info("Using gTTS engine (requires internet)")
            return TTSEngine.GTTS
        else:
            logger.warning("No TTS engines available, using system fallback")
            return TTSEngine.SYSTEM
    
    def _initialize_engine(self) -> Any:
        """
        Initialize the selected TTS engine.
        
        Returns:
            Initialized TTS engine object
        """
        try:
            if self.engine_type == TTSEngine.PYTTSX3 and PYTTSX3_AVAILABLE:
                engine = pyttsx3.init()
                return engine
            elif self.engine_type == TTSEngine.GTTS and GTTS_AVAILABLE:
                # Initialize pygame for audio playback
                pygame.mixer.init()
                return True  # gTTS doesn't need persistent engine
            else:
                return None
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            return None
    
    def _configure_engine(self) -> None:
        """Configure TTS engine with current settings."""
        if not self.engine:
            return
        
        try:
            if self.engine_type == TTSEngine.PYTTSX3:
                # Configure pyttsx3 settings
                self.engine.setProperty('rate', self.settings['rate'])
                self.engine.setProperty('volume', self.settings['volume'])
                
                # Set voice if available
                voices = self.engine.getProperty('voices')
                if voices and len(voices) > self.settings['voice_index']:
                    self.engine.setProperty('voice', voices[self.settings['voice_index']].id)
                
        except Exception as e:
            logger.error(f"Failed to configure TTS engine: {e}")
    
    def get_available_voices(self) -> List[Dict[str, str]]:
        """
        Get list of available voices for current engine.
        
        Returns:
            List[Dict[str, str]]: List of voice information
        """
        voices = []
        
        try:
            if self.engine_type == TTSEngine.PYTTSX3 and self.engine:
                pyttsx3_voices = self.engine.getProperty('voices')
                for i, voice in enumerate(pyttsx3_voices or []):
                    voices.append({
                        "index": i,
                        "name": getattr(voice, 'name', f'Voice {i}'),
                        "id": getattr(voice, 'id', f'voice_{i}'),
                        "languages": getattr(voice, 'languages', ['en'])
                    })
            elif self.engine_type == TTSEngine.GTTS:
                # gTTS supports multiple languages
                voices.append({
                    "index": 0,
                    "name": "Google TTS (English)",
                    "id": "gtts_en",
                    "languages": ["en"]
                })
                
        except Exception as e:
            logger.error(f"Failed to get available voices: {e}")
        
        return voices
    
    def speak(self, text: str, async_playback: bool = True) -> bool:
        """
        Convert text to speech and play it.
        
        Args:
            text: Text to convert to speech
            async_playback: Whether to play asynchronously
            
        Returns:
            bool: True if speech started successfully
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for TTS")
            return False
        
        # Stop any current playback
        self.stop()
        
        # Reset state
        self.state = TTSState.SPEAKING
        self.stop_requested = False
        
        try:
            if async_playback:
                # Start playback in separate thread
                self.current_thread = threading.Thread(
                    target=self._speak_threaded,
                    args=(text,),
                    daemon=True
                )
                self.current_thread.start()
                return True
            else:
                # Synchronous playback
                return self._speak_synchronous(text)
                
        except Exception as e:
            logger.error(f"Failed to start TTS playback: {e}")
            self.state = TTSState.IDLE
            return False
    
    def _speak_threaded(self, text: str) -> None:
        """Thread function for asynchronous speech playback."""
        try:
            self._speak_synchronous(text)
        finally:
            self.state = TTSState.IDLE
    
    def _speak_synchronous(self, text: str) -> bool:
        """
        Synchronous speech playback implementation.
        
        Args:
            text: Text to convert to speech
            
        Returns:
            bool: True if playback completed successfully
        """
        try:
            if self.engine_type == TTSEngine.PYTTSX3 and self.engine:
                return self._speak_pyttsx3(text)
            elif self.engine_type == TTSEngine.GTTS:
                return self._speak_gtts(text)
            else:
                return self._speak_system_fallback(text)
                
        except Exception as e:
            logger.error(f"TTS playback failed: {e}")
            return False
    
    def _speak_pyttsx3(self, text: str) -> bool:
        """Speak using pyttsx3 engine."""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
            return True
        except Exception as e:
            logger.error(f"pyttsx3 playback failed: {e}")
            return False
    
    def _speak_gtts(self, text: str) -> bool:
        """Speak using Google TTS engine."""
        try:
            if not GTTS_AVAILABLE:
                return False
            
            # Generate speech
            tts = gTTS(text=text, lang=self.settings['language'], slow=False)
            
            # Save to bytes buffer
            mp3_buffer = io.BytesIO()
            tts.write_to_fp(mp3_buffer)
            mp3_buffer.seek(0)
            
            # Play using pygame
            pygame.mixer.music.load(mp3_buffer)
            pygame.mixer.music.play()
            
            # Wait for playback to complete
            while pygame.mixer.music.get_busy():
                if self.stop_requested:
                    pygame.mixer.music.stop()
                    break
                time.sleep(0.1)
            
            return True
            
        except Exception as e:
            logger.error(f"gTTS playback failed: {e}")
            return False
    
    def _speak_system_fallback(self, text: str) -> bool:
        """Fallback to system TTS commands."""
        try:
            import subprocess
            import platform
            
            system = platform.system()
            if system == "Darwin":  # macOS
                subprocess.run(["say", text], check=True)
            elif system == "Windows":
                # Use PowerShell for Windows TTS
                cmd = f'Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Speak("{text}")'
                subprocess.run(["powershell", "-Command", cmd], check=True)
            elif system == "Linux":
                # Try espeak on Linux
                subprocess.run(["espeak", text], check=True)
            else:
                logger.error(f"Unsupported system for TTS fallback: {system}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"System TTS fallback failed: {e}")
            return False
    
    def stop(self) -> None:
        """Stop current TTS playback."""
        self.stop_requested = True
        
        try:
            if self.engine_type == TTSEngine.PYTTSX3 and self.engine:
                self.engine.stop()
            elif self.engine_type == TTSEngine.GTTS and pygame:
                pygame.mixer.music.stop()
        except Exception as e:
            logger.error(f"Failed to stop TTS playback: {e}")
        
        # Wait for thread to complete
        if self.current_thread and self.current_thread.is_alive():
            self.current_thread.join(timeout=1.0)
        
        self.state = TTSState.STOPPED
    
    def pause(self) -> bool:
        """
        Pause current TTS playback.
        
        Returns:
            bool: True if pause was successful
        """
        try:
            if self.engine_type == TTSEngine.GTTS and pygame:
                pygame.mixer.music.pause()
                self.state = TTSState.PAUSED
                return True
            else:
                # pyttsx3 doesn't support pause, so we stop instead
                self.stop()
                return True
        except Exception as e:
            logger.error(f"Failed to pause TTS playback: {e}")
            return False
    
    def resume(self) -> bool:
        """
        Resume paused TTS playback.
        
        Returns:
            bool: True if resume was successful
        """
        try:
            if self.state == TTSState.PAUSED and pygame:
                pygame.mixer.music.unpause()
                self.state = TTSState.SPEAKING
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to resume TTS playback: {e}")
            return False
    
    def is_speaking(self) -> bool:
        """
        Check if TTS is currently speaking.
        
        Returns:
            bool: True if currently speaking
        """
        return self.state == TTSState.SPEAKING
    
    def update_settings(self, **kwargs) -> None:
        """
        Update TTS settings.
        
        Args:
            **kwargs: Settings to update (rate, volume, voice_index, language)
        """
        for key, value in kwargs.items():
            if key in self.settings:
                self.settings[key] = value
        
        # Reconfigure engine with new settings
        self._configure_engine()
    
    def get_engine_info(self) -> Dict[str, Any]:
        """
        Get information about current TTS engine.
        
        Returns:
            Dict[str, Any]: Engine information and capabilities
        """
        return {
            "engine": self.engine_type.value,
            "available": self.engine is not None,
            "state": self.state.value,
            "settings": self.settings.copy(),
            "voices_count": len(self.get_available_voices()),
            "supports_pause": self.engine_type == TTSEngine.GTTS
        }

# Global TTS manager instance
_tts_manager: Optional[TTSManager] = None

def get_tts_manager() -> TTSManager:
    """
    Get or create global TTS manager instance.
    
    Returns:
        TTSManager: Global TTS manager
    """
    global _tts_manager
    if _tts_manager is None:
        _tts_manager = TTSManager()
    return _tts_manager

def speak(text: str, async_playback: bool = True) -> bool:
    """
    Speak the given text using the global TTS manager.
    
    Args:
        text: Text to convert to speech
        async_playback: Whether to play asynchronously
        
    Returns:
        bool: True if speech started successfully
    """
    manager = get_tts_manager()
    return manager.speak(text, async_playback)

def stop_speaking() -> None:
    """Stop any current TTS playback."""
    manager = get_tts_manager()
    manager.stop()

def is_speaking() -> bool:
    """
    Check if TTS is currently active.
    
    Returns:
        bool: True if currently speaking
    """
    manager = get_tts_manager()
    return manager.is_speaking()

def get_available_voices() -> List[Dict[str, str]]:
    """
    Get list of available TTS voices.
    
    Returns:
        List[Dict[str, str]]: Available voices information
    """
    manager = get_tts_manager()
    return manager.get_available_voices()

def configure_tts(**kwargs) -> None:
    """
    Configure TTS settings.
    
    Args:
        **kwargs: Settings to update (rate, volume, voice_index, language)
    """
    manager = get_tts_manager()
    manager.update_settings(**kwargs)