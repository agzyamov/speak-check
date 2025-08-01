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
    
    # Header
    st.title("🎤 CEFR Speaking Exam Simulator")
    st.markdown("Practice your English speaking skills with AI-powered CEFR level assessment")
    
    # Sidebar configuration
    st.sidebar.header("Exam Settings")
    
    # CEFR level selection
    cefr_level = st.sidebar.selectbox(
        "Select CEFR Level:",
        options=["A2", "B1", "B2", "C1"],
        index=1,  # Default to B1
        help="Choose your target CEFR level for the speaking exam"
    )
    
    # TODO: Add exam type selection (monologue, dialogue, etc.)
    # TODO: Add difficulty settings within each level
    # TODO: Add time limit configuration
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header(f"Speaking Test - Level {cefr_level}")
        
        # Start test button
        if st.button("🎯 Start Speaking Test", type="primary", use_container_width=True):
            st.session_state.test_started = True
            st.session_state.current_level = cefr_level
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
                st.success(f"**{level}**: {description}")
            else:
                st.text(f"{level}: {description}")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <small>CEFR Speaking Exam Simulator | Practice makes perfect! 🎯</small>
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()