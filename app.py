"""
app.py

Main Streamlit application for AI Second Brain.
Entry point: streamlit run app.py
"""

import streamlit as st
from config.settings import settings
from ui.chat_interface import render_chat_interface, render_sidebar_controls
from ui.upload_interface import render_upload_interface
from ui.comparison_interface import render_comparison_tab
from src.utils import setup_logger

logger = setup_logger(__name__)


def main():
    """Main application entry point."""
    
    # Page configuration
    st.set_page_config(
        page_title=settings.APP_TITLE,
        page_icon=settings.PAGE_ICON,
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Title
    st.title(settings.APP_TITLE)
    
    # Sidebar - Upload interface
    render_upload_interface()
    
    # Sidebar - Chat controls
    render_sidebar_controls()
    
    # Main area - Tabs for Chat and Comparison
    tab1, tab2 = st.tabs(["💬 Chat", "📊 Compare Documents"])
    
    with tab1:
        # Show welcome or chat
        if len(st.session_state.messages) == 0:
            st.markdown(settings.WELCOME_MESSAGE)
            
            from src.vector_store import get_vector_store
            vector_store = get_vector_store()
            doc_count = vector_store.get_document_count()
            
            if doc_count > 0:
                st.info(f"✅ **{doc_count} document chunks** indexed and ready to query!")
            else:
                st.warning("⚠️ No documents uploaded yet. Upload some documents in the sidebar to get started!")
        
        # Chat interface
        render_chat_interface()
    
    with tab2:
        # Document comparison
        render_comparison_tab()
    
    # Footer
    st.sidebar.divider()
    
    # Feature info
    st.sidebar.caption("**✨ Features:**")
    st.sidebar.caption("• 💬 Chat with documents")
    st.sidebar.caption("• 🎤 Voice input (Chrome/Edge)")
    st.sidebar.caption("• 📊 Compare documents")
    st.sidebar.caption("• 💡 Smart suggestions")
    
    st.sidebar.divider()
    st.sidebar.caption(
        f"Powered by {settings.GROQ_MODEL if settings.USE_GROQ else settings.OPENAI_MODEL} • "
        f"Local embeddings • 100% FREE"
    )


if __name__ == "__main__":
    logger.info("🚀 Starting AI Second Brain application")
    main()