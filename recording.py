"""
Voice Recording Module for CEFR Speaking Exam Simulator.

This module provides functionality to record user's spoken answers,
process audio, and integrate with transcription services.
"""

import os
import time
import threading
import tempfile
import wave
import pyaudio
import numpy as np
from typing import Optional, Callable, Dict, Any
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecordingState(Enum):
    """Recording states."""
    IDLE = "idle"
    RECORDING = "recording"
    PROCESSING = "processing"
    PLAYBACK = "playback"
    ERROR = "error"

class AudioQuality(Enum):
    """Audio quality settings."""
    LOW = "low"      # 8kHz, mono
    MEDIUM = "medium"  # 16kHz, mono  
    HIGH = "high"    # 44.1kHz, mono

class VoiceRecorder:
    """
    Voice recording functionality for CEFR speaking exam.
    
    Features:
    - Real-time audio recording
    - Multiple quality settings
    - Audio playback
    - Integration with transcription
    - Session management
    """
    
    def __init__(self, 
                 quality: AudioQuality = AudioQuality.HIGH,
                 max_duration: int = 120,  # 2 minutes max
                 sample_rate: int = 44100,
                 channels: int = 1,
                 chunk_size: int = 1024):
        """
        Initialize voice recorder.
        
        Args:
            quality: Audio quality setting
            max_duration: Maximum recording duration in seconds
            sample_rate: Audio sample rate
            channels: Number of audio channels (1=mono, 2=stereo)
            chunk_size: Audio chunk size for processing
        """
        self.quality = quality
        self.max_duration = max_duration
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        
        # Recording state
        self.state = RecordingState.IDLE
        self.is_recording = False
        self.recording_thread = None
        self.audio_frames = []
        
        # Audio processing
        self.pyaudio = None
        self.stream = None
        self.temp_file = None
        
        # Callbacks
        self.on_recording_start: Optional[Callable] = None
        self.on_recording_stop: Optional[Callable] = None
        self.on_recording_progress: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        
        # Session data
        self.current_session_id: Optional[str] = None
        self.recording_history: list = []
        
        # Initialize PyAudio
        self._initialize_pyaudio()
    
    def _initialize_pyaudio(self) -> None:
        """Initialize PyAudio for audio recording."""
        try:
            self.pyaudio = pyaudio.PyAudio()
            logger.info("PyAudio initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize PyAudio: {e}")
            self.state = RecordingState.ERROR
    
    def start_recording(self, session_id: Optional[str] = None) -> bool:
        """
        Start voice recording.
        
        Args:
            session_id: Optional session identifier
            
        Returns:
            bool: True if recording started successfully
        """
        if self.is_recording:
            logger.warning("Recording already in progress")
            return False
        
        try:
            # Create temporary file for recording
            self.temp_file = tempfile.NamedTemporaryFile(
                suffix='.wav', 
                delete=False
            )
            self.temp_file.close()
            
            # Initialize recording
            self.audio_frames = []
            self.is_recording = True
            self.state = RecordingState.RECORDING
            self.current_session_id = session_id or f"session_{int(time.time())}"
            
            # Start recording thread
            self.recording_thread = threading.Thread(
                target=self._record_audio,
                daemon=True
            )
            self.recording_thread.start()
            
            logger.info(f"Started recording session: {self.current_session_id}")
            
            # Call callback if provided
            if self.on_recording_start:
                self.on_recording_start(self.current_session_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            self.state = RecordingState.ERROR
            if self.on_error:
                self.on_error(str(e))
            return False
    
    def stop_recording(self) -> Optional[str]:
        """
        Stop voice recording and save audio file.
        
        Returns:
            Optional[str]: Path to saved audio file, or None if failed
        """
        if not self.is_recording:
            logger.warning("No recording in progress")
            return None
        
        try:
            # Stop recording
            self.is_recording = False
            self.state = RecordingState.PROCESSING
            
            # Wait for recording thread to finish
            if self.recording_thread:
                self.recording_thread.join(timeout=5.0)
            
            # Save audio file
            if self.audio_frames and self.temp_file:
                duration = len(self.audio_frames) * self.chunk_size / self.sample_rate
                
                # Only save if we have meaningful audio (at least 0.5 seconds)
                if duration > 0.5:
                    self._save_audio_file()
                    
                    # Add to history
                    recording_info = {
                        'session_id': self.current_session_id,
                        'file_path': self.temp_file.name,
                        'duration': duration,
                        'timestamp': time.time(),
                        'quality': self.quality.value
                    }
                    self.recording_history.append(recording_info)
                    
                    logger.info(f"Recording saved: {self.temp_file.name} (duration: {duration:.2f}s)")
                    
                    # Call callback if provided
                    if self.on_recording_stop:
                        self.on_recording_stop(recording_info)
                    
                    self.state = RecordingState.IDLE
                    return self.temp_file.name
                else:
                    logger.warning(f"Recording too short ({duration:.2f}s), not saving")
            else:
                logger.warning("No audio frames captured")
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to stop recording: {e}")
            self.state = RecordingState.ERROR
            if self.on_error:
                self.on_error(str(e))
            return None
    
    def _record_audio(self) -> None:
        """Internal method to record audio in a separate thread."""
        try:
            # Open audio stream
            self.stream = self.pyaudio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            logger.info("Audio stream opened, starting recording...")
            
            start_time = time.time()
            frames_captured = 0
            
            while self.is_recording:
                # Check max duration
                if time.time() - start_time > self.max_duration:
                    logger.info("Maximum recording duration reached")
                    break
                
                # Read audio data
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                self.audio_frames.append(data)
                frames_captured += 1
                
                # Calculate progress
                elapsed = time.time() - start_time
                if self.on_recording_progress:
                    self.on_recording_progress(elapsed, self.max_duration)
                
                # Small delay to prevent CPU overload
                time.sleep(0.01)
            
            # Close stream
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            
            logger.info(f"Recording thread finished. Captured {frames_captured} frames.")
            
        except Exception as e:
            logger.error(f"Error in recording thread: {e}")
            self.state = RecordingState.ERROR
            if self.on_error:
                self.on_error(str(e))
    
    def _save_audio_file(self) -> None:
        """Save recorded audio frames to WAV file."""
        try:
            with wave.open(self.temp_file.name, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.pyaudio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(self.sample_rate)
                wf.writeframes(b''.join(self.audio_frames))
            
            logger.info(f"Audio saved to: {self.temp_file.name}")
            
        except Exception as e:
            logger.error(f"Failed to save audio file: {e}")
            raise
    
    def play_recording(self, file_path: Optional[str] = None) -> bool:
        """
        Play back a recorded audio file.
        
        Args:
            file_path: Path to audio file (uses current recording if None)
            
        Returns:
            bool: True if playback started successfully
        """
        try:
            audio_file = file_path or (self.temp_file.name if self.temp_file else None)
            if not audio_file or not os.path.exists(audio_file):
                logger.error("No audio file to play")
                return False
            
            # Open audio file
            with wave.open(audio_file, 'rb') as wf:
                # Open playback stream
                stream = self.pyaudio.open(
                    format=self.pyaudio.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True
                )
                
                # Play audio
                data = wf.readframes(self.chunk_size)
                while data:
                    stream.write(data)
                    data = wf.readframes(self.chunk_size)
                
                # Clean up
                stream.stop_stream()
                stream.close()
            
            logger.info(f"Playback completed: {audio_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to play recording: {e}")
            return False
    
    def get_recording_info(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about recordings.
        
        Args:
            session_id: Optional session ID to filter
            
        Returns:
            Dict with recording information
        """
        if session_id:
            recordings = [r for r in self.recording_history if r['session_id'] == session_id]
        else:
            recordings = self.recording_history
        
        return {
            'total_recordings': len(recordings),
            'current_session': self.current_session_id,
            'is_recording': self.is_recording,
            'state': self.state.value,
            'recordings': recordings
        }
    
    def cleanup(self) -> None:
        """Clean up resources and temporary files."""
        try:
            # Stop any ongoing recording
            if self.is_recording:
                self.stop_recording()
            
            # Close PyAudio
            if self.pyaudio:
                self.pyaudio.terminate()
            
            # Clean up temporary files
            for recording in self.recording_history:
                try:
                    if os.path.exists(recording['file_path']):
                        os.unlink(recording['file_path'])
                except Exception as e:
                    logger.warning(f"Failed to clean up {recording['file_path']}: {e}")
            
            logger.info("Voice recorder cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        self.cleanup()

# Global recorder instance
_recorder_instance: Optional[VoiceRecorder] = None

def get_recorder() -> VoiceRecorder:
    """Get or create global voice recorder instance."""
    global _recorder_instance
    if _recorder_instance is None:
        _recorder_instance = VoiceRecorder()
    return _recorder_instance

def start_recording(session_id: Optional[str] = None) -> bool:
    """Start voice recording."""
    return get_recorder().start_recording(session_id)

def stop_recording() -> Optional[str]:
    """Stop voice recording and return file path."""
    return get_recorder().stop_recording()

def play_recording(file_path: Optional[str] = None) -> bool:
    """Play back a recording."""
    return get_recorder().play_recording(file_path)

def get_recording_info(session_id: Optional[str] = None) -> Dict[str, Any]:
    """Get recording information."""
    return get_recorder().get_recording_info(session_id)

def is_recording() -> bool:
    """Check if currently recording."""
    return get_recorder().is_recording

def get_recording_state() -> str:
    """Get current recording state."""
    return get_recorder().state.value

def cleanup_recorder() -> None:
    """Clean up recorder resources."""
    global _recorder_instance
    if _recorder_instance:
        _recorder_instance.cleanup()
        _recorder_instance = None 