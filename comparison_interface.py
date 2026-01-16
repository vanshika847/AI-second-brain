"""
ui/comparison_interface.py

UI for document comparison feature.
"""

import streamlit as st
from src.document_comparison import compare_documents, get_available_documents


def render_comparison_tab():
    """Render document comparison interface."""
    
    st.header("📊 Compare Documents")
    
    st.markdown("""
    Select 2 or more documents to compare their content, findings, or methodologies.
    """)
    
    # Get available documents
    available_docs = get_available_documents()
    
    if len(available_docs) < 2:
        st.warning("⚠️ You need at least 2 documents uploaded to use comparison feature.")
        st.info("💡 Upload more documents in the sidebar to enable comparison.")
        return
    
    # Document selection
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected_docs = st.multiselect(
            "Select documents to compare",
            options=available_docs,
            default=available_docs[:2] if len(available_docs) >= 2 else [],
            help="Choose 2-5 documents for best results"
        )
    
    with col2:
        comparison_aspect = st.selectbox(
            "Compare by",
            options=["general", "methodology", "findings", "structure", "tone"],
            help="What aspect to focus on"
        )
    
    # Compare button
    if st.button("🔍 Compare Documents", type="primary", disabled=len(selected_docs) < 2):
        with st.spinner("Analyzing documents..."):
            result = compare_documents(selected_docs, comparison_aspect)
            
            if "error" in result:
                st.error(result["error"])
                if "found_docs" in result:
                    st.info(f"Found content in: {', '.join(result['found_docs'])}")
            else:
                st.markdown("### Comparison Results")
                st.markdown(result["comparison"])
                
                # Show document list
                with st.expander("📄 Compared Documents"):
                    for doc in result["documents"]:
                        st.markdown(f"- {doc}")