"""
CEFR Speaking Exam Simulator - Main Streamlit Application

This is the main entry point for the CEFR Speaking Exam Simulator.
It provides a web interface for users to practice speaking tests at different CEFR levels.
Now includes user authentication and session management.
"""

import streamlit as st
import os
import json
import random
from pathlib import Path
from questions import get_question_by_level
from evaluate import evaluate_speaking_response
from tts import speak, stop_speaking, is_speaking, get_available_voices, configure_tts
from recording import start_recording, stop_recording, play_recording, is_recording, get_recording_state, get_recording_info
from stt_openai import transcribe_audio_file, get_supported_languages, is_available as stt_available
from db_mongo.crud import (
    create_session as mongo_create_session,
    end_session as mongo_end_session,
    add_recording as mongo_add_recording,
    add_transcript as mongo_add_transcript,
    add_evaluation as mongo_add_evaluation,
    list_sessions as mongo_list_sessions,
    get_session_detail as mongo_get_session_detail,
)
import db_mongo.client as mongo_client
from streamlit_auth import streamlit_auth

# TODO: Add session state management for exam progress
# TODO: Implement audio recording functionality
# TODO: Add timer functionality for speaking responses
# TODO: Implement progress tracking and session history


@st.cache_data(ttl=60 * 60 * 24)
def load_population_data() -> list[dict]:
    p = Path("data/scraped/population.json")
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text())
        # keep only valid rows with country and population
        return [r for r in data if r.get("country") and isinstance(r.get("population"), int)]
    except Exception:
        return []


def generate_population_prompt(level: str, data: list[dict]) -> str:
    if not data:
        return "Talk about population trends in your country."
    # choose countries
    pick = lambda: random.choice([r for r in data if r["country"].lower() not in {"world", "europe", "asia"}])
    a = pick()
    if level in {"A2", "B1"}:
        return f"Describe life in {a['country']}. Mention how population size ({a['population']:,}) might affect daily life (transport, housing, jobs)."
    # B2/C1 compare
    b = pick()
    tries = 0
    while b["country"] == a["country"] and tries < 5:
        b = pick(); tries += 1
    return (
        f"Compare {a['country']} (population {a['population']:,}) and {b['country']} (population {b['population']:,}). "
        f"Discuss reasons for differences, and implications for economy, infrastructure, and environment."
    )


def main():
    """Main Streamlit application function."""
    
    # Page configuration
    st.set_page_config(
        page_title="CEFR Speaking Exam Simulator",
        page_icon="🎤",
        layout="wide"
    )
    
    # Require authentication - this will show login/register form if not authenticated
    streamlit_auth.require_auth()
    
    # Render user menu in sidebar for authenticated users
    streamlit_auth.render_user_menu()
    
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
    if 'stt_enabled' not in st.session_state:
        st.session_state.stt_enabled = False
    if 'latest_transcript_text' not in st.session_state:
        st.session_state.latest_transcript_text = ""
    if 'evaluation_enabled' not in st.session_state:
        st.session_state.evaluation_enabled = False
    if 'latest_evaluation' not in st.session_state:
        st.session_state.latest_evaluation = None
    
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
        selected_voice_idx = None  # ensure defined for linters
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
        if voices and selected_voice_idx is not None:
            configure_tts(rate=speech_rate, volume=volume, voice_index=selected_voice_idx)
        else:
            configure_tts(rate=speech_rate, volume=volume)
        
        # Show current TTS status
        if is_speaking():
            st.sidebar.success("🔊 Currently speaking...")
    
    st.sidebar.markdown("---")
    
    # STT Settings
    st.sidebar.subheader("📝 Speech-to-Text")
    
    # Check if STT is available
    if stt_available():
        stt_enabled = st.sidebar.checkbox(
            "Enable Speech-to-Text",
            value=st.session_state.stt_enabled,
            help="Enable OpenAI Whisper API transcription of recordings"
        )
        if stt_enabled != st.session_state.stt_enabled:
            st.session_state.stt_enabled = stt_enabled
    else:
        st.sidebar.warning("⚠️ STT not available")
        st.sidebar.info("Set OPENAI_API_KEY environment variable to enable transcription")
        st.session_state.stt_enabled = False
    
    st.sidebar.markdown("---")
    
    # Evaluation Settings
    st.sidebar.subheader("🤖 AI Assessment")
    
    # Check if evaluation is available (same as STT availability)
    if stt_available():
        evaluation_enabled = st.sidebar.checkbox(
            "Enable AI Assessment",
            value=st.session_state.evaluation_enabled,
            help="Enable OpenAI GPT-based CEFR level assessment"
        )
        if evaluation_enabled != st.session_state.evaluation_enabled:
            st.session_state.evaluation_enabled = evaluation_enabled
    else:
        st.sidebar.warning("⚠️ AI Assessment not available")
        st.sidebar.info("Set OPENAI_API_KEY environment variable to enable assessment")
        st.session_state.evaluation_enabled = False
    
    st.sidebar.markdown("---")
    
    # Data-driven prompts
    st.sidebar.subheader("📊 Data-driven Prompts")
    use_population_prompts = st.sidebar.checkbox(
        "Use population dataset",
        value=st.session_state.get("use_population_prompts", False),
        help="Generate prompts from real population data (Wikipedia).",
    )
    st.session_state.use_population_prompts = use_population_prompts
    if use_population_prompts:
        data_status = "loaded" if load_population_data() else "missing"
        st.sidebar.caption(f"Population data: {data_status}")
    
    # Weather Context
    st.sidebar.subheader("🌦️ Weather Context")
    use_weather = st.sidebar.checkbox(
        "Use weather context",
        value=st.session_state.get("use_weather", False),
        help="Augment prompts with current weather in a city.",
    )
    st.session_state.use_weather = use_weather
    weather_city = st.sidebar.text_input("City", value=st.session_state.get("weather_city", "London"))
    st.session_state.weather_city = weather_city
    wx_summary = None
    if use_weather:
        try:
            from weather_client import get_weather
            wx = get_weather(weather_city)
            if wx:
                wx_summary = wx.get("summary")
                st.sidebar.caption(f"{wx_summary}")
                # stash in session for persistence
                st.session_state.latest_weather = wx
            else:
                st.sidebar.caption("No weather data (stub or MCP unavailable)")
        except Exception:
            st.sidebar.caption("Weather fetch failed")

    st.sidebar.markdown("---")
    
    # TODO: Add exam type selection (monologue, dialogue, etc.)
    # TODO: Add difficulty settings within each level  
    # TODO: Add time limit configuration
    
    # History - recent sessions
    with st.sidebar.expander("📜 History", expanded=False):
        def render_local_history():
            local = st.session_state.get("session_history", [])
            if not local:
                st.caption("No local sessions yet.")
                return
            for idx, sess in enumerate(reversed(local[-10:])):
                label = f"{sess.get('level','?')} • local • {sess.get('started_at','')}"
                if st.button(label, key=f"local_sess_{idx}"):
                    st.session_state.test_session_id = sess.get("id") or f"local_{idx}"
                    st.session_state.current_level = sess.get("level", st.session_state.current_level)
                    st.session_state.test_started = False
                    st.rerun()
        try:
            sessions = mongo_list_sessions(limit=10)
            if sessions:
                for s in sessions:
                    sid = str(s.get("_id"))
                    label = f"{s.get('level', '?')} • {s.get('status', '')} • {s.get('started_at', '')}"
                    if st.button(label, key=f"sess_{sid}"):
                        st.session_state.test_session_id = sid
                        st.session_state.current_level = s.get("level", st.session_state.current_level)
                        st.session_state.test_started = s.get("status") == "active"
                        st.rerun()
            else:
                st.caption("No DB sessions yet. Showing local history:")
                render_local_history()
        except Exception:
            st.caption("History not available from DB. Showing local history:")
            render_local_history()

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
                    # Persist session in Mongo
                    try:
                        # Get current user ID from authentication
                        user_data = streamlit_auth.get_user_data()
                        user_id = user_data.get("user_id") if user_data else None
                        sid = mongo_create_session(level=cefr_level, user_id=user_id)
                        st.session_state.test_session_id = sid
                    except Exception:
                        # Fallback to ephemeral session id if DB is unavailable
                        st.session_state.test_session_id = f"session_{cefr_level}_{len(st.session_state.session_history)+1}"
                    # Add new session to session_history (UI only)
                    st.session_state.session_history.append({
                        "level": cefr_level,
                        "started_at": st.session_state.get("test_started_time", None)
                    })
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
                    if st.session_state.get("use_population_prompts"):
                        pop = load_population_data()
                        st.session_state.current_question = generate_population_prompt(cefr_level, pop)
                    else:
                        # default path: just reset so a new random question will be generated below
                        st.session_state.current_question = ""
                    st.rerun()
            with col_btn3:
                if st.button("❌ End Test", type="secondary"):
                    # Persist session end
                    try:
                        if st.session_state.test_session_id:
                            mongo_end_session(st.session_state.test_session_id, status="completed")
                    except Exception:
                        pass
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
                if st.session_state.get("use_population_prompts"):
                    base_q = generate_population_prompt(cefr_level, load_population_data())
                else:
                    base_q = get_question_by_level(cefr_level)
                # Weather augmentation
                if st.session_state.get("use_weather") and st.session_state.get("latest_weather"):
                    from weather_client import weather_prompt
                    wx = st.session_state.latest_weather
                    aug = weather_prompt(cefr_level, wx)
                    question = f"{base_q}\n\nContext: {wx.get('summary')}\n{aug}"
                else:
                    question = base_q
                
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
                            # Save recording metadata to Mongo
                            try:
                                if st.session_state.test_session_id:
                                    mongo_add_recording(
                                        session_id=st.session_state.test_session_id,
                                        file_url=recording_file,
                                        duration_s=st.session_state.get("recording_duration", None),
                                    )
                            except Exception:
                                pass
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
            
            # Transcript section
            if st.session_state.stt_enabled:
                st.subheader("📄 Speech Transcript")
                transcript_placeholder = st.container()
                with transcript_placeholder:
                    # Controls for transcription
                    col_tr1, col_tr2, col_tr3 = st.columns([1, 1, 2])
                    with col_tr1:
                        lang_codes = get_supported_languages()
                        selected_lang = st.selectbox(
                            "Language",
                            options=lang_codes,
                            index=lang_codes.index("en") if "en" in lang_codes else 0,
                            help="Language hint for transcription",
                            key="transcribe_lang",
                        )
                    with col_tr2:
                        model_choice = st.selectbox(
                            "Model",
                            options=["whisper-1"],
                            index=0,
                            help="OpenAI Whisper model",
                            key="transcribe_model",
                        )
                    with col_tr3:
                        do_transcribe = st.button(
                            "📝 Transcribe Recording",
                            disabled=not st.session_state.current_recording_file,
                            help="Run OpenAI Whisper transcription on the latest recording",
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
                        with st.spinner("Transcribing with OpenAI Whisper..."):
                            try:
                                result = transcribe_audio_file(
                                    st.session_state.current_recording_file,
                                    language=selected_lang,
                                    model=model_choice,
                                )
                                if result.get("status") == "ok" and result.get("text"):
                                    st.session_state.latest_transcript_text = result["text"].strip()
                                    # Persist transcript to Mongo (attach to latest recording if any)
                                    try:
                                        detail = mongo_get_session_detail(st.session_state.test_session_id)
                                        recs = detail.get("recordings", [])
                                        last_rec = recs[0] if recs else None
                                        if last_rec:
                                            mongo_add_transcript(
                                                recording_id=str(last_rec.get("_id")),
                                                text=st.session_state.latest_transcript_text,
                                                language=result.get("language"),
                                                provider=result.get("provider", "openai"),
                                                model=result.get("model", "whisper-1"),
                                                segments=result.get("segments"),
                                            )
                                    except Exception:
                                        pass
                                    st.success(
                                        f"✅ Transcribed ({result.get('language', selected_lang)} | {result.get('provider', 'OpenAI')})"
                                    )
                                    # Show brief metadata
                                    meta = st.columns(3)
                                    meta[0].metric("Duration", f"{result.get('duration', 0.0):.1f}s")
                                    meta[1].metric("Segments", f"{len(result.get('segments', []))}")
                                    meta[2].metric("Provider", result.get("provider", "OpenAI"))
                                    st.rerun()
                                else:
                                    err = result.get("error") or "No text returned"
                                    st.error(f"❌ Transcription failed: {err}")
                            except Exception as e:
                                st.error(f"❌ OpenAI Whisper error: {e}")
            
            # Evaluation area
            if st.session_state.evaluation_enabled:
                st.subheader("🤖 AI Feedback")
                evaluation_placeholder = st.container()
                with evaluation_placeholder:
                    # Evaluation controls
                    col_eval1, col_eval2 = st.columns([1, 2])
                    with col_eval1:
                        do_evaluate = st.button(
                            "🎯 Evaluate Response",
                            disabled=not st.session_state.latest_transcript_text,
                            help="Run AI assessment on your transcribed response",
                        )
                    
                    # Evaluation results area
                    if st.session_state.latest_evaluation:
                        eval_result = st.session_state.latest_evaluation
                        
                        # Overall assessment
                        col_overall1, col_overall2, col_overall3 = st.columns(3)
                        with col_overall1:
                            st.metric("Overall Level", eval_result.predicted_level.value)
                        with col_overall2:
                            st.metric("Confidence", f"{eval_result.confidence:.1%}")
                        with col_overall3:
                            st.metric("Word Count", eval_result.word_count)
                        
                        # Detailed scores
                        st.subheader("📊 Detailed Scores")
                        col_scores1, col_scores2 = st.columns(2)
                        
                        with col_scores1:
                            st.metric("Fluency", f"{eval_result.criteria_scores.fluency:.1f}/10")
                            st.metric("Accuracy", f"{eval_result.criteria_scores.accuracy:.1f}/10")
                            st.metric("Grammar", f"{eval_result.criteria_scores.grammatical_range:.1f}/10")
                        
                        with col_scores2:
                            st.metric("Vocabulary", f"{eval_result.criteria_scores.lexical_range:.1f}/10")
                            st.metric("Coherence", f"{eval_result.criteria_scores.task_achievement:.1f}/10")
                            st.metric("Overall Score", f"{eval_result.overall_score:.1f}/10")
                        
                        # Detailed feedback
                        st.subheader("📝 Detailed Feedback")
                        st.markdown(eval_result.detailed_feedback)
                        
                        # Recommendations
                        if eval_result.recommendations:
                            st.subheader("💡 Recommendations")
                            for i, rec in enumerate(eval_result.recommendations, 1):
                                st.write(f"{i}. {rec}")
                    
                    # Run evaluation when requested
                    elif do_evaluate and st.session_state.latest_transcript_text:
                        with st.spinner("Assessing with AI..."):
                            try:
                                eval_result = evaluate_speaking_response(
                                    transcript=st.session_state.latest_transcript_text,
                                    target_level=cefr_level,
                                    question=st.session_state.current_question,
                                    audio_duration=0.0
                                )
                                st.session_state.latest_evaluation = eval_result
                                # Persist evaluation to Mongo (attach to latest transcript if any)
                                try:
                                    detail = mongo_get_session_detail(st.session_state.test_session_id)
                                    recs = detail.get("recordings", [])
                                    last_rec = recs[0] if recs else None
                                    if last_rec:
                                        # find transcript for last_rec (latest)
                                        transcripts = list(mongo_client.db.transcripts.find({"recording_id": last_rec["_id"]}).sort("created_at", -1))  # noqa: E501
                                        last_tr = transcripts[0] if transcripts else None
                                        if last_tr:
                                            mongo_add_evaluation(
                                                transcript_id=str(last_tr.get("_id")),
                                                overall_level=eval_result.predicted_level.value,
                                                confidence=eval_result.confidence,
                                                scores={
                                                    "fluency": eval_result.criteria_scores.fluency,
                                                    "accuracy": eval_result.criteria_scores.accuracy,
                                                    "grammar": eval_result.criteria_scores.grammatical_range,
                                                    "vocabulary": eval_result.criteria_scores.lexical_range,
                                                    "coherence": eval_result.criteria_scores.task_achievement,
                                                },
                                                rationale=eval_result.detailed_feedback,
                                                tips=eval_result.recommendations,
                                            )
                                except Exception:
                                    pass
                                st.success("✅ Assessment completed!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Assessment failed: {e}")
            else:
                st.subheader("🤖 AI Feedback")
                st.info("Enable 'AI Assessment' in the sidebar to get detailed feedback")
    
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