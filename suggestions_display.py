"""
ui/suggestions_display.py

Display question suggestions in the UI.
"""

import streamlit as st
from src.question_suggestions import generate_question_suggestions


def render_question_suggestions():
    """Render question suggestion buttons."""
    
    if "show_suggestions" not in st.session_state:
        st.session_state.show_suggestions = True
    
    if not st.session_state.show_suggestions:
        return
    
    st.markdown("### 💡 Suggested Questions")
    st.caption("Click any question to ask it")
    
    