#!/usr/bin/env python3
"""
Quick TTS diagnostic tool to test different audio methods
"""

import time
import subprocess
import sys

def test_system_tts():
    """Test macOS system TTS"""
    print("🔊 Testing macOS system TTS...")
    try:
        result = subprocess.run(
            ['say', '-v', 'Alex', 'Testing system text to speech'], 
            check=True, 
            capture_output=True,
            text=True
        )
        print("✅ System TTS command executed successfully")
        return True
    except Exception as e:
        print(f"❌ System TTS failed: {e}")
        return False

def test_pyttsx3():
    """Test pyttsx3 TTS engine"""
    print("🔊 Testing pyttsx3 TTS...")
    try:
        import pyttsx3
        engine = pyttsx3.init()
        
        # Get and show available voices
        voices = engine.getProperty('voices')
        print(f"📢 Found {len(voices)} voices")
        
        # Try different voice settings
        engine.setProperty('rate', 200)    # Faster speech
        engine.setProperty('volume', 1.0)  # Max volume
        
        # Test with first available voice
        if voices:
            engine.setProperty('voice', voices[0].id)
            print(f"🎭 Using voice: {voices[0].name}")
        
        engine.say("Testing Python T T S with maximum volume")
        engine.runAndWait()
        print("✅ pyttsx3 TTS completed")
        return True
    except Exception as e:
        print(f"❌ pyttsx3 failed: {e}")
        return False

def test_gtts():
    """Test Google TTS with pygame"""
    print("🔊 Testing Google TTS...")
    try:
        from gtts import gTTS
        import pygame
        import io
        
        # Generate speech
        tts = gTTS(text="Testing Google text to speech", lang='en', slow=False)
        mp3_buffer = io.BytesIO()
        tts.write_to_fp(mp3_buffer)
        mp3_buffer.seek(0)
        
        # Play with pygame
        pygame.mixer.init()
        pygame.mixer.music.load(mp3_buffer)
        pygame.mixer.music.play()
        
        # Wait for playback
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        
        print("✅ Google TTS completed")
        return True
    except Exception as e:
        print(f"❌ Google TTS failed: {e}")
        return False

def main():
    """Run comprehensive TTS tests"""
    print("🎵 TTS Audio Diagnostic Tool")
    print("=" * 40)
    
    print("\n💡 BEFORE TESTING:")
    print("1. Turn up your Mac volume (F12)")
    print("2. Check System Preferences > Sound > Output")
    print("3. Make sure correct speakers/headphones selected")
    print("4. Close other audio apps if needed")
    
    input("\nPress Enter when ready to test audio...")
    
    tests = [
        ("macOS System TTS", test_system_tts),
        ("pyttsx3 Engine", test_pyttsx3), 
        ("Google TTS", test_gtts)
    ]
    
    results = {}
    for name, test_func in tests:
        print(f"\n{'=' * 40}")
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"❌ {name} crashed: {e}")
            results[name] = False
        
        time.sleep(2)  # Pause between tests
    
    # Summary
    print(f"\n{'=' * 40}")
    print("📊 TEST RESULTS:")
    for name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {name}: {status}")
    
    if not any(results.values()):
        print("\n⚠️  NO AUDIO DETECTED!")
        print("Try these solutions:")
        print("1. Check if headphones are plugged in but sound going to speakers")
        print("2. Restart Terminal/Python")
        print("3. Check macOS privacy settings for Terminal audio access")
        print("4. Try running: sudo chmod +x /usr/bin/say")

if __name__ == "__main__":
    main()