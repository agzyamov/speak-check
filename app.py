"""
CEFR Speaking Exam Simulator - Main Streamlit Application

This is the main entry point for the CEFR Speaking Exam Simulator.
It provides a web interface for users to practice speaking tests at different CEFR levels.
"""

import streamlit as st
import os
from questions import get_question_by_level
from transcribe import transcribe_audio
from evaluate import evaluate_speaking_response
from tts import speak, stop_speaking, is_speaking, get_available_voices, configure_tts
from recording import start_recording, stop_recording, play_recording, is_recording, get_recording_state, get_recording_info
from transcribe import transcribe_audio_file, get_supported_languages, setup_whisper_model

# TODO: Add session state management for exam progress
# TODO: Implement audio recording functionality
# TODO: Add timer functionality for speaking responses
# TODO: Implement progress tracking and session history

def main():
    """Main Streamlit application function."""
    
    # Page configuration
    st.set_page_config(
        page_title="CEFR Speaking Exam Simulator",
        page_icon="🎤",
        layout="wide"
    )
    
    # Initialize session state
    if 'test_started' not in st.session_state:
        st.session_state.test_started = False
    if 'current_level' not in st.session_state:
        st.session_state.current_level = "B1"
    if 'test_session_id' not in st.session_state:
        st.session_state.test_session_id = None
    if 'current_question' not in st.session_state:
        st.session_state.current_question = ""
    if 'tts_enabled' not in st.session_state:
        st.session_state.tts_enabled = True
    if 'auto_play_question' not in st.session_state:
        st.session_state.auto_play_question = True
    if 'session_history' not in st.session_state:
        st.session_state.session_history = []
    if 'recording_active' not in st.session_state:
        st.session_state.recording_active = False
    if 'current_recording_file' not in st.session_state:
        st.session_state.current_recording_file = None
    if 'recording_duration' not in st.session_state:
        st.session_state.recording_duration = 0
    
    # Header
    st.title("🎤 CEFR Speaking Exam Simulator")
    st.markdown("Practice your English speaking skills with AI-powered CEFR level assessment")
    
    # Sidebar configuration
    st.sidebar.header("Exam Settings")
    
    # CEFR level selection with descriptions
    level_options = {
        "A2": "A2 - Elementary",
        "B1": "B1 - Intermediate", 
        "B2": "B2 - Upper-Intermediate",
        "C1": "C1 - Advanced"
    }
    
    selected_level_display = st.sidebar.selectbox(
        "🎯 Select CEFR Level:",
        options=list(level_options.values()),
        index=list(level_options.keys()).index(st.session_state.current_level),
        help="Choose your target CEFR level for the speaking exam"
    )
    
    # Extract the level code (A2, B1, etc.) from the display text
    cefr_level = selected_level_display.split(" - ")[0]
    
    # Update session state if level changed
    if cefr_level != st.session_state.current_level:
        st.session_state.current_level = cefr_level
        # Reset test if level changed during active test
        if st.session_state.test_started:
            st.session_state.test_started = False
            st.rerun()
    
    # Show current test status in sidebar
    if st.session_state.test_started:
        st.sidebar.success(f"🎤 **Test Active**")
        st.sidebar.write(f"**Session ID:** {st.session_state.test_session_id}")
    else:
        st.sidebar.info("⏳ **Test Not Started**")
        st.sidebar.write("Select a level and click 'Start Speaking Test' to begin")
    
    st.sidebar.markdown("---")
    
    # TTS Settings
    st.sidebar.subheader("🔊 Audio Settings")
    
    # TTS Enable/Disable
    tts_enabled = st.sidebar.checkbox(
        "Enable Text-to-Speech",
        value=st.session_state.tts_enabled,
        help="Enable automatic reading of speaking prompts"
    )
    if tts_enabled != st.session_state.tts_enabled:
        st.session_state.tts_enabled = tts_enabled
    
    if tts_enabled:
        # Auto-play setting
        auto_play = st.sidebar.checkbox(
            "Auto-play questions",
            value=st.session_state.auto_play_question,
            help="Automatically play questions when they appear"
        )
        if auto_play != st.session_state.auto_play_question:
            st.session_state.auto_play_question = auto_play
        
        # Voice selection
        from tts import get_available_voices
        voices = get_available_voices()
        if voices:
            voice_names = [f"{voice['name']}" for voice in voices]
            selected_voice_idx = st.sidebar.selectbox(
                "Voice Selection",
                range(len(voice_names)),
                format_func=lambda x: voice_names[x],
                index=0,
                help="Choose a different voice for better quality"
            )
        
        # Voice settings
        col_rate, col_vol = st.sidebar.columns(2)
        with col_rate:
            speech_rate = st.slider(
                "Speed",
                min_value=50,
                max_value=300,
                value=180,  # Updated default
                step=25,
                help="Speech rate (words per minute)"
            )
        with col_vol:
            volume = st.slider(
                "Volume",
                min_value=0.0,
                max_value=1.0,
                value=0.9,  # Updated default
                step=0.1,
                help="Audio volume level"
            )
        
        # Apply TTS settings
        if voices:
            configure_tts(rate=speech_rate, volume=volume, voice_index=selected_voice_idx)
        else:
            configure_tts(rate=speech_rate, volume=volume)
        
        # Show current TTS status
        if is_speaking():
            st.sidebar.success("🔊 Currently speaking...")
    
    st.sidebar.markdown("---")
    
    # TODO: Add exam type selection (monologue, dialogue, etc.)
    # TODO: Add difficulty settings within each level  
    # TODO: Add time limit configuration
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header(f"Speaking Test - Level {cefr_level}")
        
        # Test control buttons
        if not st.session_state.test_started:
            # Show start button when test not active
            col_btn1, col_btn2 = st.columns([3, 1])
            with col_btn1:
                if st.button("🎯 Start Speaking Test", type="primary", use_container_width=True):
                    st.session_state.test_started = True
                    st.session_state.current_level = cefr_level
                    # Add new session to session_history
                    st.session_state.session_history.append({
                        "level": cefr_level,
                        "started_at": st.session_state.get("test_started_time", None)  # Optional: add timestamp if available
                    })
                    st.session_state.test_session_id = f"session_{cefr_level}_{len(st.session_state.session_history)}"
                    st.success(f"✅ Test started for level {cefr_level}!")
                    st.rerun()
            with col_btn2:
                st.info(f"Level: **{cefr_level}**")
        else:
            # Show test controls when test is active
            col_btn1, col_btn2, col_btn3 = st.columns([2, 2, 1])
            with col_btn1:
                st.success(f"🎤 **Active Test - Level {cefr_level}**")
            with col_btn2:
                if st.button("🔄 New Question", use_container_width=True):
                    # Force regeneration of question by rerunning the app
                    st.rerun()
            with col_btn3:
                if st.button("❌ End Test", type="secondary"):
                    st.session_state.test_started = False
                    st.session_state.test_session_id = None
                    st.info("Test ended. Click 'Start Speaking Test' to begin again.")
                    st.rerun()
        
        # Test area
        if st.session_state.get('test_started', False):
            st.markdown("---")
            
            # Question display area with TTS
            st.subheader("📝 Speaking Prompt")
            question_placeholder = st.container()
            with question_placeholder:
                # Get current question
                question = get_question_by_level(cefr_level)
                
                # Check if question changed (for auto-play)
                question_changed = question != st.session_state.current_question
                if question_changed:
                    st.session_state.current_question = question
                
                # Display question
                st.info(question)
                
                # TTS Controls
                if st.session_state.tts_enabled:
                    col_tts1, col_tts2, col_tts3, col_tts4 = st.columns([1, 1, 1, 2])
                    
                    with col_tts1:
                        if st.button("▶️ Play", help="Read the question aloud"):
                            with st.spinner("🔊 Playing question..."):
                                try:
                                    st.write(f"🐛 DEBUG: About to speak: '{question[:50]}...'")
                                    result = speak(question, async_playback=False)
                                    st.write(f"🐛 DEBUG: TTS result: {result}")
                                    if result:
                                        st.success("✅ TTS completed successfully!")
                                    else:
                                        st.error("❌ TTS failed!")
                                except Exception as e:
                                    st.error(f"❌ TTS Error: {e}")
                                    import traceback
                                    st.code(traceback.format_exc())
                    
                    with col_tts2:
                        if st.button("⏹️ Stop", help="Stop audio playback"):
                            stop_speaking()
                            
                    # Add debug test button
                    col_debug = st.columns(1)[0]
                    with col_debug:
                        if st.button("🧪 Test TTS (Simple)", help="Test TTS with simple text"):
                            try:
                                import subprocess
                                st.write("🐛 Testing macOS say command...")
                                subprocess.run(['say', 'Testing from Streamlit'], check=True)
                                st.success("✅ macOS TTS completed!")
                            except Exception as e:
                                st.error(f"❌ macOS TTS Error: {e}")
                    
                    with col_tts3:
                        # TTS Status indicator
                        if is_speaking():
                            st.success("🔊 Playing")
                        else:
                            st.empty()
                    
                    with col_tts4:
                        # Auto-play indicator
                        if st.session_state.auto_play_question:
                            st.caption("🔄 Auto-play enabled")
                
                # Auto-play functionality (temporarily disabled for testing)
                # if (st.session_state.tts_enabled and 
                #     st.session_state.auto_play_question and 
                #     question_changed and 
                #     question.strip()):
                #     # Auto-play the question when it first appears
                #     speak(question, async_playback=True)
            
            # Recording area
            st.subheader("🎙️ Record Your Response")
            recording_placeholder = st.container()
            with recording_placeholder:
                # Recording status
                recording_state = get_recording_state()
                if st.session_state.recording_active:
                    st.success(f"🔴 Recording... ({st.session_state.recording_duration:.1f}s)")
                else:
                    st.info("⏸️ Ready to record")
                
                # Recording controls
                col_rec1, col_rec2, col_rec3, col_rec4 = st.columns([1, 1, 1, 2])
                
                with col_rec1:
                    if st.button("🔴 Start Recording", 
                                disabled=st.session_state.recording_active,
                                help="Start recording your spoken response"):
                        if start_recording(session_id=st.session_state.test_session_id):
                            st.session_state.recording_active = True
                            st.session_state.recording_duration = 0
                            st.success("🎙️ Recording started!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to start recording")
                
                with col_rec2:
                    if st.button("⏹️ Stop Recording", 
                                disabled=not st.session_state.recording_active,
                                help="Stop recording and save audio"):
                        recording_file = stop_recording()
                        if recording_file:
                            st.session_state.recording_active = False
                            st.session_state.current_recording_file = recording_file
                            st.success(f"✅ Recording saved: {os.path.basename(recording_file)}")
                            st.rerun()
                        else:
                            st.error("❌ Failed to stop recording")
                
                with col_rec3:
                    if st.button("▶️ Play Recording", 
                                disabled=not st.session_state.current_recording_file,
                                help="Play back your recorded response"):
                        if play_recording(st.session_state.current_recording_file):
                            st.success("🔊 Playing recording...")
                        else:
                            st.error("❌ Failed to play recording")
                
                with col_rec4:
                    # Recording info
                    if st.session_state.current_recording_file:
                        recording_info = get_recording_info(st.session_state.test_session_id)
                        st.caption(f"📁 {recording_info['total_recordings']} recording(s) in session")
                
                # Recording progress (if active)
                if st.session_state.recording_active:
                    # Simple progress indicator
                    progress_bar = st.progress(0)
                    progress_text = st.empty()
                    
                    # Update progress (this is a simplified version)
                    import time
                    start_time = time.time()
                    while st.session_state.recording_active:
                        elapsed = time.time() - start_time
                        progress = min(elapsed / 120.0, 1.0)  # 2 minutes max
                        progress_bar.progress(progress)
                        progress_text.text(f"Recording: {elapsed:.1f}s / 120s")
                        time.sleep(0.1)
                        
                        if not st.session_state.recording_active:
                            break
            
            # Transcript display area
            st.subheader("📄 Speech Transcript")
            transcript_placeholder = st.container()
            with transcript_placeholder:
                # Controls for transcription
                col_tr1, col_tr2, col_tr3 = st.columns([1, 1, 2])
                with col_tr1:
                    lang_codes = get_supported_languages()
                    selected_lang = st.selectbox(
                        "Lang",
                        options=lang_codes,
                        index=lang_codes.index("en") if "en" in lang_codes else 0,
                        help="Language hint for Whisper",
                        key="transcribe_lang",
                    )
                with col_tr2:
                    model_choice = st.selectbox(
                        "Model",
                        options=["tiny", "base", "small", "medium"],
                        index=1,
                        help="Whisper model size",
                        key="transcribe_model",
                    )
                with col_tr3:
                    do_transcribe = st.button(
                        "📝 Transcribe Recording",
                        disabled=not st.session_state.current_recording_file,
                        help="Run Whisper transcription on the latest recording",
                    )

                # Transcript area
                transcript_text = st.session_state.get("latest_transcript_text", "")
                st.text_area(
                    "Your speech will be transcribed here...",
                    value=transcript_text,
                    height=180,
                    disabled=True,
                    key="transcript_display",
                )

                # Run transcription when requested
                if do_transcribe and st.session_state.current_recording_file:
                    with st.spinner("Transcribing with Whisper... (first run may download a model)"):
                        try:
                            # Lazy init model; if not installed, surface error nicely
                            setup_whisper_model(model_choice)
                            result = transcribe_audio_file(
                                st.session_state.current_recording_file,
                                language=selected_lang,
                                model_size=model_choice,
                            )
                            if result.get("status") == "ok" and result.get("text"):
                                st.session_state.latest_transcript_text = result["text"].strip()
                                st.success(
                                    f"✅ Transcribed ({result.get('language', selected_lang)} | {result.get('model', model_choice)})"
                                )
                                # Show brief metadata
                                meta = st.columns(3)
                                meta[0].metric("Duration", f"{result.get('duration', 0.0):.1f}s")
                                meta[1].metric("Segments", f"{len(result.get('segments', []))}")
                                meta[2].metric("Model", result.get("model", model_choice))
                                st.rerun()
                            else:
                                err = result.get("error") or "No text returned"
                                st.error(f"❌ Transcription failed: {err}")
                        except Exception as e:
                            st.error(f"❌ Whisper error: {e}")
            
            # Evaluation area
            st.subheader("🤖 AI Feedback")
            evaluation_placeholder = st.container()
            with evaluation_placeholder:
                # TODO: Display AI evaluation results
                st.info("AI evaluation will appear here after you complete your response")
    
    with col2:
        st.header("📊 Session Info")
        
        # Current session stats
        st.metric("Current Level", cefr_level)
        st.metric("Test Status", "Active" if st.session_state.test_started else "Inactive")
        st.metric("Questions Completed", "0")  # TODO: Track from session state
        st.metric("Average Score", "N/A")  # TODO: Calculate from history
        
        # TODO: Add progress chart
        # TODO: Add recent scores history
        # TODO: Add tips and guidelines
        
        st.markdown("---")
        st.subheader("🎯 CEFR Level Guide")
        cefr_info = {
            "A2": "Elementary - Basic phrases and expressions",
            "B1": "Intermediate - Familiar topics and situations", 
            "B2": "Upper-Intermediate - Complex topics with fluency",
            "C1": "Advanced - Spontaneous and fluent expression"
        }
        
        for level, description in cefr_info.items():
            if level == cefr_level:
                st.success(f"**{level}**: {description} ⭐")
            else:
                st.text(f"{level}: {description}")
        
        if st.session_state.test_started:
            st.info(f"🎯 **Currently testing at {cefr_level} level**")
        else:
            st.warning("💡 **Tip**: Choose your level and start the test!")
    
    # Footer
    st.markdown("---")
    st.markdown("**CEFR Speaking Exam Simulator** | Practice makes perfect!")

if __name__ == "__main__":
    main()