"""
ui/upload_interface.py

Document upload interface for the AI Second Brain.
"""

import streamlit as st
from pathlib import Path
from config.settings import settings, get_upload_path
from src.document_processor import get_document_processor
from src.vector_store import get_vector_store
from src.utils import setup_logger, format_file_size

logger = setup_logger(__name__)


def render_upload_interface():
    """Render the document upload interface."""
    
    st.sidebar.title("📤 Upload Documents")
    
    # File uploader
    uploaded_files = st.sidebar.file_uploader(
        "Choose files",
        type=[ext[1:] for ext in settings.SUPPORTED_EXTENSIONS],  # Remove dots
        accept_multiple_files=True,
        help=f"Supported: {', '.join(settings.SUPPORTED_EXTENSIONS)}"
    )
    
    if uploaded_files:
        if st.sidebar.button("🚀 Process Documents", use_container_width=True, type="primary"):
            process_uploaded_files(uploaded_files)
    
    # Show current stats
    render_document_stats()


def process_uploaded_files(uploaded_files):
    """Process uploaded files."""
    
    progress_bar = st.sidebar.progress(0)
    status_text = st.sidebar.empty()
    
    total_files = len(uploaded_files)
    processor = get_document_processor()
    vector_store = get_vector_store()
    
    all_chunks = []
    
    for i, uploaded_file in enumerate(uploaded_files):
        try:
            # Update progress
            progress = (i + 1) / total_files
            progress_bar.progress(progress)
            status_text.text(f"Processing {uploaded_file.name}...")
            
            # Save file temporarily
            file_path = get_upload_path(uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            logger.info(f"Processing file: {uploaded_file.name}")
            
            # Process document
            chunks = processor.process_file(file_path)
            all_chunks.extend(chunks)
            
            logger.info(f"✅ Processed {uploaded_file.name}: {len(chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Error processing {uploaded_file.name}: {e}")
            st.sidebar.error(f"❌ Error: {uploaded_file.name} - {str(e)}")
    
    # Index all chunks
    if all_chunks:
        status_text.text("Indexing documents...")
        try:
            vector_store.index_documents(all_chunks)
            
            progress_bar.progress(1.0)
            status_text.empty()
            progress_bar.empty()
            
            st.sidebar.success(f"✅ Successfully processed {total_files} file(s)! ({len(all_chunks)} chunks)")
            st.rerun()
            
        except Exception as e:
            logger.error(f"Error indexing documents: {e}")
            st.sidebar.error(f"❌ Indexing error: {str(e)}")
    else:
        status_text.empty()
        progress_bar.empty()
        st.sidebar.warning("⚠️ No valid documents to process")


def render_document_stats():
    """Render document statistics."""
    
    st.sidebar.divider()
    st.sidebar.subheader("📊 Document Stats")
    
    vector_store = get_vector_store()
    stats = vector_store.get_stats()
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Total Chunks", stats['total_documents'])
    with col2:
        st.metric("Dimension", stats['embedding_dimension'])
    
    st.sidebar.caption(f"Model: {stats['embedding_model'].split('/')[-1]}")
    
    # Clear all button
    if stats['total_documents'] > 0:
        st.sidebar.divider()
        if st.sidebar.button("🗑️ Clear All Documents", use_container_width=True, type="secondary"):
            if st.sidebar.checkbox("⚠️ Confirm deletion"):
                vector_store.clear_all()
                st.sidebar.success("✅ All documents cleared")
                st.rerun()