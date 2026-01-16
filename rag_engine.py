"""
src/rag_engine.py

RAG (Retrieval-Augmented Generation) engine.
Combines document retrieval with Groq/OpenAI for contextual Q&A.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from openai import OpenAI
from config.settings import settings
from src.vector_store import get_vector_store
from src.embeddings import get_embedding_manager
from src.utils import setup_logger

# Setup logger
logger = setup_logger(__name__)


@dataclass
class ChatMessage:
    """Represents a single chat message."""
    role: str  # "user" or "assistant"
    content: str


@dataclass
class QueryResult:
    """Result from a RAG query."""
    answer: str
    sources: List[Dict[str, Any]]
    query: str


class RAGEngine:
    """
    RAG engine that retrieves relevant documents and generates answers.
    """
    
    def __init__(self):
        """Initialize RAG engine with LLM and vector store."""
        self.vector_store = get_vector_store()
        self.embed_manager = get_embedding_manager()
        
        # Initialize LLM client
        if settings.USE_GROQ:
            self.llm_client = OpenAI(
                api_key=settings.GROQ_API_KEY,
                base_url=settings.GROQ_API_BASE
            )
            self.model_name = settings.GROQ_MODEL
            self.temperature = settings.GROQ_TEMPERATURE
            self.max_tokens = settings.GROQ_MAX_TOKENS
            logger.info(f"✅ RAGEngine initialized with Groq: {settings.GROQ_MODEL}")
        else:
            self.llm_client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model_name = settings.OPENAI_MODEL
            self.temperature = settings.OPENAI_TEMPERATURE
            self.max_tokens = settings.OPENAI_MAX_TOKENS
            logger.info(f"✅ RAGEngine initialized with OpenAI: {settings.OPENAI_MODEL}")
        
        # Conversation memory
        self.conversation_history: List[ChatMessage] = []
    
    def query(
        self,
        question: str,
        use_memory: bool = True,
        top_k: int = None
    ) -> QueryResult:
        """
        Query the RAG system with a question.
        
        Args:
            question: User's question
            use_memory: Whether to use conversation history
            top_k: Number of documents to retrieve
            
        Returns:
            QueryResult with answer and sources
        """
        if top_k is None:
            top_k = settings.TOP_K_RETRIEVAL
        
        logger.info(f"Processing query: '{question}'")
        
        try:
            # Step 1: Retrieve relevant documents
            retrieved_docs = self.vector_store.search(question, top_k=top_k)
            
            if not retrieved_docs:
                logger.warning("No relevant documents found")
                return QueryResult(
                    answer="I couldn't find any relevant information in your documents to answer this question.",
                    sources=[],
                    query=question
                )
            
            # Step 2: Build context from retrieved documents
            context = self._build_context(retrieved_docs)
            
            # Step 3: Build prompt with memory if enabled
            prompt = self._build_prompt(question, context, use_memory)
            
            # Step 4: Generate answer using native OpenAI client
            logger.info("Generating answer...")
            response = self.llm_client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            answer = response.choices[0].message.content.strip()
            
            # Step 5: Update conversation memory
            if use_memory:
                self._update_memory(question, answer)
            
            # Step 6: Format sources
            sources = self._format_sources(retrieved_docs)
            
            logger.info(f"✅ Query completed. Retrieved {len(sources)} sources")
            
            return QueryResult(
                answer=answer,
                sources=sources,
                query=question
            )
            
        except Exception as e:
            logger.error(f"Error during query: {e}")
            return QueryResult(
                answer=f"Error processing query: {str(e)}",
                sources=[],
                query=question
            )
    
    def _build_context(self, retrieved_docs: List[Dict[str, Any]]) -> str:
        """Build context string from retrieved documents."""
        context_parts = []
        
        for i, doc in enumerate(retrieved_docs, 1):
            text = doc['text']
            metadata = doc['metadata']
            score = doc['score']
            
            source_name = metadata.get('source', 'Unknown')
            page_info = ""
            if 'page' in metadata:
                page_info = f", Page {metadata['page']}"
            elif 'slide' in metadata:
                page_info = f", Slide {metadata['slide']}"
            
            context_parts.append(
                f"[Source {i}: {source_name}{page_info}] (Relevance: {score:.2f})\n{text}\n"
            )
        
        return "\n---\n".join(context_parts)
    
    def _build_prompt(
        self,
        question: str,
        context: str,
        use_memory: bool
    ) -> str:
        """Build the prompt for LLM."""
        
        prompt = f"""You are a helpful AI assistant that answers questions based ONLY on the provided context.

IMPORTANT RULES:
1. Answer ONLY using information from the context below
2. If the context doesn't contain relevant information, say "I don't have information about that in the uploaded documents"
3. Cite sources by mentioning the source name and page/slide number when possible
4. Be concise but thorough

CONTEXT:
{context}

"""
        
        if use_memory and self.conversation_history:
            prompt += "PREVIOUS CONVERSATION:\n"
            recent_history = self.conversation_history[-settings.MEMORY_WINDOW * 2:]
            for msg in recent_history:
                prompt += f"{msg.role.upper()}: {msg.content}\n"
            prompt += "\n"
        
        prompt += f"QUESTION: {question}\n\nANSWER:"
        
        return prompt
    
    def _update_memory(self, question: str, answer: str):
        """Update conversation memory."""
        self.conversation_history.append(ChatMessage(role="user", content=question))
        self.conversation_history.append(ChatMessage(role="assistant", content=answer))
        
        max_messages = settings.MEMORY_WINDOW * 2
        if len(self.conversation_history) > max_messages:
            self.conversation_history = self.conversation_history[-max_messages:]
    
    def _format_sources(self, retrieved_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format sources for display."""
        sources = []
        
        for doc in retrieved_docs:
            metadata = doc['metadata']
            
            source_info = {
                'filename': metadata.get('source', 'Unknown'),
                'text_preview': doc['text'][:200] + "..." if len(doc['text']) > 200 else doc['text'],
                'score': round(doc['score'], 3),
                'score_percent': round(doc['score'] * 100, 1),
            }
            
            if 'page' in metadata:
                source_info['page'] = metadata['page']
            if 'slide' in metadata:
                source_info['slide'] = metadata['slide']
            
            sources.append(source_info)
        
        return sources
    
    def clear_memory(self):
        """Clear conversation history."""
        self.conversation_history = []
        logger.info("Conversation memory cleared")
    
    def get_memory(self) -> List[ChatMessage]:
        """Get current conversation history."""
        return self.conversation_history.copy()


# ==================== SINGLETON INSTANCE ====================
_rag_engine = None


def get_rag_engine() -> RAGEngine:
    """Get the global RAGEngine instance (singleton pattern)."""
    global _rag_engine
    
    if _rag_engine is None:
        _rag_engine = RAGEngine()
        logger.info("Created global RAGEngine instance")
    
    return _rag_engine


# ==================== CONVENIENCE FUNCTIONS ====================
def ask_question(question: str, use_memory: bool = True) -> QueryResult:
    """Convenience function to ask a question."""
    engine = get_rag_engine()
    return engine.query(question, use_memory=use_memory)