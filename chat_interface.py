"""
ui/chat_interface.py

Streamlit chat interface for the AI Second Brain.
"""

import streamlit as st
from typing import List
from src.rag_engine import get_rag_engine, QueryResult
from src.utils import setup_logger
from src.question_suggestions import generate_question_suggestions
from ui.voice_input import render_voice_button_inline

logger = setup_logger(__name__)


def render_chat_interface():
    """Render the main chat interface."""
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Display sources if available
            if message["role"] == "assistant" and "sources" in message:
                render_sources(message["sources"])
    
    # Show question suggestions if no messages yet
    if len(st.session_state.messages) == 0:
        render_initial_suggestions()
    
    # Add voice input button (floating)
    render_voice_button_inline()
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        handle_user_input(prompt)


def render_initial_suggestions():
    """Show suggested questions when chat is empty."""
    
    st.markdown("### 💡 Try asking:")
    
    # Generate suggestions
    suggestions = generate_question_suggestions(num_suggestions=5)
    
    # Display as clickable buttons
    cols = st.columns(2)
    for idx, suggestion in enumerate(suggestions):
        col = cols[idx % 2]
        with col:
            if st.button(
                suggestion,
                key=f"suggestion_{idx}",
                use_container_width=True,
                type="secondary"
            ):
                handle_user_input(suggestion)
                st.rerun()


def handle_user_input(prompt: str):
    """Handle user input and generate response."""
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get RAG engine
    rag_engine = get_rag_engine()
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = rag_engine.query(prompt)
            
            # Display answer
            st.markdown(result.answer)
            
            # Display sources
            if result.sources:
                render_sources(result.sources)
            
            # Add to session state
            st.session_state.messages.append({
                "role": "assistant",
                "content": result.answer,
                "sources": result.sources
            })


def render_sources(sources: List[dict]):
    """Render source citations."""
    if not sources:
        return
    
    with st.expander(f"📚 Sources ({len(sources)})"):
        for i, source in enumerate(sources, 1):
            score_color = "🟢" if source['score_percent'] > 80 else "🟡" if source['score_percent'] > 60 else "🟠"
            
            page_info = ""
            if 'page' in source:
                page_info = f" (Page {source['page']})"
            elif 'slide' in source:
                page_info = f" (Slide {source['slide']})"
            
            st.markdown(f"""
            **{score_color} Source {i}: {source['filename']}**{page_info}  
            *Relevance: {source['score_percent']}%*
            
            > {source['text_preview']}
            """)
            st.divider()


def render_sidebar_controls():
    """Render sidebar controls."""
    st.sidebar.title("💬 Chat Controls")
    
    # Clear conversation button
    if st.sidebar.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        rag_engine = get_rag_engine()
        rag_engine.clear_memory()
        st.rerun()
    
    # Show conversation count
    msg_count = len(st.session_state.messages)
    st.sidebar.metric("Messages", msg_count)
    
    # Voice tutorial
    with st.sidebar.expander("🎤 Voice Input Help"):
        st.markdown("""
        **How to use Voice Input:**
        
        1. Click the floating 🎤 button (bottom-right)
        2. Speak your question clearly
        3. Your speech appears in the chat input
        4. Press Enter to send
        
        **Keyboard Shortcut:** `Ctrl+Shift+V`
        
        **Note:** Works in Chrome/Edge only
        """)