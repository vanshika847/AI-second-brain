"""
src/document_comparison.py

Document comparison functionality.
"""

from typing import List, Dict, Any
from src.vector_store import get_vector_store
from src.rag_engine import get_rag_engine
from src.utils import setup_logger

logger = setup_logger(__name__)


def compare_documents(
    doc_names: List[str],
    comparison_aspect: str = "general"
) -> Dict[str, Any]:
    """
    Compare multiple documents.
    
    Args:
        doc_names: List of document filenames to compare
        comparison_aspect: What to compare (general, methodology, findings, etc.)
        
    Returns:
        Comparison result with similarities and differences
    """
    logger.info(f"Comparing documents: {doc_names}")
    
    if len(doc_names) < 2:
        return {
            "error": "Please select at least 2 documents to compare"
        }
    
    # Get vector store
    vector_store = get_vector_store()
    
    # Retrieve chunks from each document
    doc_contexts = {}
    for doc_name in doc_names:
        # Search for content from this specific document
        query = f"content from document {doc_name}"
        results = vector_store.search(query, top_k=20)
        
        # Filter results to only this document
        doc_chunks = [
            r for r in results 
            if r['metadata'].get('source', '') == doc_name
        ]
        
        if doc_chunks:
            # Combine top chunks into context
            context = "\n\n".join([chunk['text'] for chunk in doc_chunks[:5]])
            doc_contexts[doc_name] = context
        else:
            logger.warning(f"No content found for {doc_name}")
    
    if len(doc_contexts) < 2:
        return {
            "error": f"Could not find enough content. Found: {list(doc_contexts.keys())}",
            "found_docs": list(doc_contexts.keys())
        }
    
    # Build comparison prompt
    prompt = _build_comparison_prompt(doc_contexts, comparison_aspect)
    
    # Get RAG engine and generate comparison
    rag_engine = get_rag_engine()
    
    try:
        # Use LLM directly for comparison
        response = rag_engine.llm_client.chat.completions.create(
            model=rag_engine.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1500
        )
        
        comparison_text = response.choices[0].message.content.strip()
        
        return {
            "comparison": comparison_text,
            "documents": list(doc_contexts.keys()),
            "aspect": comparison_aspect
        }
    
    except Exception as e:
        logger.error(f"Comparison error: {e}")
        return {
            "error": f"Failed to generate comparison: {str(e)}"
        }


def _build_comparison_prompt(
    doc_contexts: Dict[str, str],
    aspect: str
) -> str:
    """Build comparison prompt."""
    
    aspect_instructions = {
        "general": "Compare the overall content, themes, and main points",
        "methodology": "Compare the methodologies, approaches, and techniques used",
        "findings": "Compare the key findings, results, and conclusions",
        "structure": "Compare the structure, organization, and format",
        "tone": "Compare the writing style, tone, and intended audience",
        "timeline": "Compare any dates, timelines, or chronological aspects",
        "authors": "Compare authorship, credentials, and perspectives"
    }
    
    instruction = aspect_instructions.get(aspect, aspect_instructions["general"])
    
    prompt = f"""You are comparing multiple documents. {instruction}.

Provide your comparison in this clear format:

**📊 SIMILARITIES:**
- List all key similarities between the documents

**🔍 DIFFERENCES:**
- List all notable differences

**📄 UNIQUE TO EACH DOCUMENT:**
"""
    
    for doc_name, context in doc_contexts.items():
        prompt += f"\n**{doc_name}:**\n- Unique aspects or content\n"
    
    prompt += "\n\n---\n\n**DOCUMENT CONTENTS:**\n\n"
    
    for doc_name, context in doc_contexts.items():
        prompt += f"### Document: {doc_name}\n{context[:1500]}\n\n---\n\n"
    
    prompt += "\nProvide a detailed, structured comparison following the format above:"
    
    return prompt


def get_available_documents() -> List[str]:
    """
    Get list of all documents in the vector store.
    
    Returns:
        List of unique document filenames
    """
    try:
        vector_store = get_vector_store()
        
        # Get sample of documents
        all_results = vector_store.search("", top_k=1000)
        
        # Extract unique filenames
        filenames = set()
        for result in all_results:
            filename = result['metadata'].get('source', '')
            if filename:
                filenames.add(filename)
        
        return sorted(list(filenames))
    
    except Exception as e:
        logger.error(f"Error getting documents: {e}")
        return []