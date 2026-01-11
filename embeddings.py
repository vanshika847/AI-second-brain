"""
src/embeddings.py

Embedding manager using FastEmbed for local, fast text embeddings.
Converts text chunks into vector representations for semantic search.
"""

from typing import List, Optional
from llama_index.core.embeddings import BaseEmbedding
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from config.settings import settings
from src.utils import setup_logger, EmbeddingError

# Setup logger
logger = setup_logger(__name__)


class EmbeddingManager:
    """
    Manages text embedding generation using FastEmbed.
    
    FastEmbed is lightweight and fast compared to sentence-transformers.
    It runs locally (no API calls) and produces high-quality embeddings.
    """
    
    def __init__(self):
        """Initialize the embedding model."""
        self._embed_model: Optional[BaseEmbedding] = None
        self._model_loaded = False
    
    @property
    def embed_model(self) -> BaseEmbedding:
        """
        Lazy-load the embedding model (only loads when first used).
        
        Returns:
            Initialized FastEmbed embedding model
            
        Raises:
            EmbeddingError: If model fails to load
        """
        if self._embed_model is None:
            try:
                logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL_NAME}")
                
                # Initialize FastEmbed with BGE model
                # BGE (BAAI General Embedding) is top-tier for retrieval
                self._embed_model = FastEmbedEmbedding(
                    model_name=settings.EMBEDDING_MODEL_NAME
                )
                
                self._model_loaded = True
                logger.info(f"✅ Embedding model loaded successfully")
                
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise EmbeddingError(f"Could not load embedding model: {e}")
        
        return self._embed_model
    
    def get_text_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text string.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats (vector representation)
            
        Example:
            >>> manager = EmbeddingManager()
            >>> vector = manager.get_text_embedding("Hello world")
            >>> len(vector)
            384  # BGE-small dimension
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            # Return zero vector for empty text
            return [0.0] * settings.EMBEDDING_DIM
        
        try:
            # Get embedding from model
            embedding = self.embed_model.get_text_embedding(text)
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise EmbeddingError(f"Failed to generate embedding: {e}")
    
    def get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batch processing).
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
            
        Note:
            Batch processing is faster than calling get_text_embedding()
            multiple times due to model optimization.
        """
        if not texts:
            logger.warning("Empty text list provided for embedding")
            return []
        
        try:
            logger.info(f"Generating embeddings for {len(texts)} texts")
            
            # Filter out empty texts
            valid_texts = [t for t in texts if t and t.strip()]
            
            if not valid_texts:
                logger.warning("All texts were empty after filtering")
                return [[0.0] * settings.EMBEDDING_DIM] * len(texts)
            
            # Get embeddings in batch
            embeddings = self.embed_model.get_text_embedding_batch(valid_texts)
            
            logger.info(f"✅ Generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise EmbeddingError(f"Failed to generate batch embeddings: {e}")
    
    def get_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for a search query.
        
        Some embedding models have separate query/document modes.
        FastEmbed handles this automatically, so this is an alias
        to get_text_embedding for consistency.
        
        Args:
            query: Search query text
            
        Returns:
            Embedding vector for the query
        """
        return self.get_text_embedding(query)
    
    @property
    def dimension(self) -> int:
        """
        Get the embedding dimension size.
        
        Returns:
            Number of dimensions in the embedding vector
        """
        return settings.EMBEDDING_DIM
    
    @property
    def model_name(self) -> str:
        """
        Get the name of the embedding model.
        
        Returns:
            Model name string
        """
        return settings.EMBEDDING_MODEL_NAME
    
    def is_loaded(self) -> bool:
        """
        Check if the embedding model is loaded.
        
        Returns:
            True if model is loaded, False otherwise
        """
        return self._model_loaded


# ==================== SINGLETON INSTANCE ====================
# Create one global embedding manager
# This ensures the model is only loaded once and reused
_embedding_manager = None


def get_embedding_manager() -> EmbeddingManager:
    """
    Get the global embedding manager instance (singleton pattern).
    
    Returns:
        Singleton EmbeddingManager instance
        
    Example:
        >>> from src.embeddings import get_embedding_manager
        >>> manager = get_embedding_manager()
        >>> vector = manager.get_text_embedding("test")
    """
    global _embedding_manager
    
    if _embedding_manager is None:
        _embedding_manager = EmbeddingManager()
        logger.info("Created global EmbeddingManager instance")
    
    return _embedding_manager


# ==================== CONVENIENCE FUNCTIONS ====================
def embed_text(text: str) -> List[float]:
    """
    Convenience function to embed a single text.
    
    Args:
        text: Text to embed
        
    Returns:
        Embedding vector
    """
    manager = get_embedding_manager()
    return manager.get_text_embedding(text)


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Convenience function to embed multiple texts.
    
    Args:
        texts: List of texts to embed
        
    Returns:
        List of embedding vectors
    """
    manager = get_embedding_manager()
    return manager.get_text_embeddings(texts)


def embed_query(query: str) -> List[float]:
    """
    Convenience function to embed a search query.
    
    Args:
        query: Search query
        
    Returns:
        Query embedding vector
    """
    manager = get_embedding_manager()
    return manager.get_query_embedding(query)
    