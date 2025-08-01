#!/usr/bin/env python3
"""
Test script for voice recording functionality.
"""

import time
import os
from recording import start_recording, stop_recording, play_recording, is_recording, get_recording_state

def test_voice_recording():
    """Test the voice recording functionality."""
    print("🎙️ Testing Voice Recording Functionality")
    print("=" * 50)
    
    # Test 1: Check initial state
    print("\n1. Initial State Check:")
    print(f"   Recording state: {get_recording_state()}")
    print(f"   Is recording: {is_recording()}")
    
    # Test 2: Start recording
    print("\n2. Starting Recording:")
    session_id = f"test_session_{int(time.time())}"
    start_result = start_recording(session_id)
    print(f"   Start result: {start_result}")
    print(f"   Is recording: {is_recording()}")
    print(f"   Session ID: {session_id}")
    
    if start_result:
        # Test 3: Record for a few seconds
        print("\n3. Recording Audio (5 seconds):")
        print("   🎤 Please speak for 5 seconds...")
        
        for i in range(5, 0, -1):
            print(f"   Recording... {i} seconds left")
            time.sleep(1)
        
        # Test 4: Stop recording
        print("\n4. Stopping Recording:")
        recording_file = stop_recording()
        print(f"   Stop result: {recording_file}")
        print(f"   Is recording: {is_recording()}")
        
        if recording_file:
            # Test 5: Check file exists
            print("\n5. File Check:")
            if os.path.exists(recording_file):
                file_size = os.path.getsize(recording_file)
                print(f"   ✅ File exists: {recording_file}")
                print(f"   📁 File size: {file_size} bytes")
                
                # Test 6: Play recording
                print("\n6. Playing Recording:")
                print("   🔊 Playing back your recording...")
                play_result = play_recording(recording_file)
                print(f"   Play result: {play_result}")
                
                # Test 7: Get recording info
                print("\n7. Recording Information:")
                from recording import get_recording_info
                info = get_recording_info(session_id)
                print(f"   Total recordings: {info['total_recordings']}")
                print(f"   Current session: {info['current_session']}")
                print(f"   State: {info['state']}")
                
            else:
                print(f"   ❌ File not found: {recording_file}")
        else:
            print("   ❌ No recording file returned")
    
    print("\n" + "=" * 50)
    print("🎤 Voice Recording Test Completed!")
    
    # Cleanup
    print("\n🧹 Cleaning up...")
    from recording import cleanup_recorder
    cleanup_recorder()
    print("✅ Cleanup completed")

if __name__ == "__main__":
    test_voice_recording() 