"""
src/question_suggestions.py

Generate smart question suggestions based on document content.
"""

from typing import List
from src.vector_store import get_vector_store
from src.rag_engine import get_rag_engine
from src.utils import setup_logger

logger = setup_logger(__name__)


def generate_question_suggestions(
    filename: str = None,
    num_suggestions: int = 5
) -> List[str]:
    """
    Generate relevant question suggestions.
    
    Args:
        filename: Specific document (or None for all docs)
        num_suggestions: Number of questions
        
    Returns:
        List of suggested questions
    """
    logger.info(f"Generating suggestions for {filename or 'all documents'}")
    
    try:
        vector_store = get_vector_store()
        
        if filename:
            query = f"content from {filename}"
        else:
            query = "main topics and key information"
        
        results = vector_store.search(query, top_k=5)
        
        if not results:
            return _get_default_suggestions()
        
        if filename:
            results = [r for r in results if r['metadata'].get('source') == filename]
        
        if not results:
            return _get_default_suggestions()
        
        context = "\n\n".join([r['text'][:500] for r in results[:3]])
        suggestions = _generate_with_llm(context, filename, num_suggestions)
        
        return suggestions
    
    except Exception as e:
        logger.error(f"Error generating suggestions: {e}")
        return _get_default_suggestions()


def _generate_with_llm(context: str, filename: str, num: int) -> List[str]:
    """Use LLM to generate contextual questions."""
    
    rag_engine = get_rag_engine()
    doc_ref = f"the document '{filename}'" if filename else "the uploaded documents"
    
    prompt = f"""Based on this content from {doc_ref}, generate {num} insightful questions.

CONTENT:
{context}

Generate {num} diverse questions that:
1. Are directly answerable from the content
2. Cover different aspects
3. Are natural and conversational

Format: Return ONLY the questions, one per line.
"""
    
    try:
        response = rag_engine.llm_client.chat.completions.create(
            model=rag_engine.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300
        )
        
        questions_text = response.choices[0].message.content.strip()
        questions = [
            q.strip().lstrip('123456789.-•* ')
            for q in questions_text.split('\n')
            if q.strip() and '?' in q
        ]
        
        return questions[:num] if questions else _get_default_suggestions()
    
    except Exception as e:
        logger.error(f"LLM suggestion error: {e}")
        return _get_default_suggestions()


def _get_default_suggestions() -> List[str]:
    """Fallback generic suggestions."""
    return [
        "What are the main topics covered?",
        "Can you summarize the key points?",
        "What are the most important findings?",
        "Are there any dates or statistics mentioned?",
        "Who are the key people mentioned?"
    ]