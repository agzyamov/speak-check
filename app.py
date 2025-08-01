"""
CEFR Speaking Exam Simulator - Main Streamlit Application

This is the main entry point for the CEFR Speaking Exam Simulator.
It provides a web interface for users to practice speaking tests at different CEFR levels.
"""

import streamlit as st
from questions import get_question_by_level
from transcribe import transcribe_audio
from evaluate import evaluate_speaking_response

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
                    # Force regeneration of question by clearing cache
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
            
            # Question display area
            st.subheader("📝 Speaking Prompt")
            question_placeholder = st.container()
            with question_placeholder:
                # TODO: Replace with actual question retrieval
                question = get_question_by_level(cefr_level)
                st.info(question)
            
            # Recording area
            st.subheader("🎙️ Record Your Response")
            recording_placeholder = st.container()
            with recording_placeholder:
                # TODO: Implement audio recording widget
                st.warning("Audio recording not implemented yet")
                
                # Placeholder for recording controls
                col_rec1, col_rec2, col_rec3 = st.columns(3)
                with col_rec1:
                    st.button("🔴 Start Recording", disabled=True)
                with col_rec2:
                    st.button("⏹️ Stop Recording", disabled=True)
                with col_rec3:
                    st.button("▶️ Play Recording", disabled=True)
            
            # Transcript display area
            st.subheader("📄 Speech Transcript")
            transcript_placeholder = st.container()
            with transcript_placeholder:
                # TODO: Display real-time transcription
                st.text_area(
                    "Your speech will be transcribed here...",
                    height=150,
                    disabled=True,
                    key="transcript_display"
                )
            
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