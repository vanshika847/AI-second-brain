"""
src/vector_store.py

Vector store management using ChromaDB for persistent storage.
Handles document indexing and similarity search.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
import chromadb
from chromadb.config import Settings as ChromaSettings
from llama_index.core import Document, VectorStoreIndex, StorageContext
from llama_index.core.vector_stores import VectorStoreQuery
from llama_index.vector_stores.chroma import ChromaVectorStore
from config.settings import settings
from src.embeddings import get_embedding_manager
from src.utils import setup_logger, RetrievalError

# Setup logger
logger = setup_logger(__name__)


class VectorStoreManager:
    """
    Manages ChromaDB vector store for document embeddings.
    Provides indexing and retrieval operations.
    """
    
    def __init__(self):
        """Initialize ChromaDB client and collection."""
        self._index: Optional[VectorStoreIndex] = None
        self._chroma_client = None
        self._collection = None
        self._initialize_chroma()
    
    def _initialize_chroma(self):
        """Initialize ChromaDB client and collection."""
        try:
            logger.info(f"Initializing ChromaDB at {settings.CHROMA_DB_DIR}")
            
            # Create persistent ChromaDB client
            self._chroma_client = chromadb.PersistentClient(
                path=str(settings.CHROMA_DB_DIR),
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                )
            )
            
            # Get or create collection
            self._collection = self._chroma_client.get_or_create_collection(
                name=settings.CHROMA_COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}  # Use cosine similarity
            )
            
            logger.info(f"✅ ChromaDB initialized with collection: {settings.CHROMA_COLLECTION_NAME}")
            logger.info(f"Collection contains {self._collection.count()} documents")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise RetrievalError(f"ChromaDB initialization failed: {e}")
    
    def index_documents(self, documents: List[Document]) -> bool:
        """
        Index documents into the vector store.
        
        Args:
            documents: List of Document objects to index
            
        Returns:
            True if successful
        """
        if not documents:
            logger.warning("No documents provided for indexing")
            return False
        
        try:
            logger.info(f"Indexing {len(documents)} documents...")
            
            # Get embedding manager
            embed_manager = get_embedding_manager()
            
            # Create ChromaVectorStore
            vector_store = ChromaVectorStore(chroma_collection=self._collection)
            
            # Create storage context
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            # Create index from documents with custom embeddings
            self._index = VectorStoreIndex.from_documents(
                documents,
                storage_context=storage_context,
                embed_model=embed_manager.embed_model,
                show_progress=True,
            )
            
            logger.info(f"✅ Successfully indexed {len(documents)} documents")
            logger.info(f"Total documents in collection: {self._collection.count()}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error indexing documents: {e}")
            raise RetrievalError(f"Failed to index documents: {e}")
    
    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using semantic similarity.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            filters: Optional metadata filters
            
        Returns:
            List of dictionaries with text, metadata, and score
        """
        if top_k is None:
            top_k = settings.TOP_K_RETRIEVAL
        
        try:
            logger.info(f"Searching for: '{query}' (top_k={top_k})")
            
            # Check if index exists
            if self._index is None:
                self._load_index()
                
                if self._index is None:
                    logger.warning("No documents indexed yet")
                    return []
            
            # Get embedding manager
            embed_manager = get_embedding_manager()
            
            # Create retriever
            retriever = self._index.as_retriever(
                similarity_top_k=top_k,
                embed_model=embed_manager.embed_model,
            )
            
            # Retrieve documents
            nodes = retriever.retrieve(query)
            
            # Format results with safe score handling
            results = []
            for node in nodes:
                # Get score safely (default to 1.0 if None)
                score = getattr(node, 'score', None)
                if score is None:
                    score = 1.0
                
                result = {
                    'text': node.get_content(),
                    'metadata': node.metadata,
                    'score': float(score),
                }
                results.append(result)
            
            # Filter by similarity threshold (safe comparison)
            filtered_results = []
            for r in results:
                try:
                    if r['score'] >= settings.SIMILARITY_THRESHOLD:
                        filtered_results.append(r)
                except (TypeError, ValueError):
                    # If comparison fails, include result anyway
                    filtered_results.append(r)
            
            logger.info(f"✅ Found {len(filtered_results)} relevant documents")
            return filtered_results
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            raise RetrievalError(f"Failed to search documents: {e}")
    
    def _load_index(self):
        """Load existing index from ChromaDB."""
        try:
            if self._collection.count() == 0:
                logger.info("No existing documents in collection")
                return
            
            logger.info("Loading existing index...")
            
            # Get embedding manager
            embed_manager = get_embedding_manager()
            
            # Create vector store from existing collection
            vector_store = ChromaVectorStore(chroma_collection=self._collection)
            
            # Load index
            self._index = VectorStoreIndex.from_vector_store(
                vector_store,
                embed_model=embed_manager.embed_model,
            )
            
            logger.info("✅ Loaded existing index")
            
        except Exception as e:
            logger.error(f"Error loading index: {e}")
    
    def clear_all(self) -> bool:
        """Clear all documents from the vector store."""
        try:
            logger.warning("Clearing all documents from vector store...")
            
            # Delete collection
            self._chroma_client.delete_collection(settings.CHROMA_COLLECTION_NAME)
            
            # Recreate empty collection
            self._collection = self._chroma_client.get_or_create_collection(
                name=settings.CHROMA_COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
            
            # Reset index
            self._index = None
            
            logger.info("✅ Vector store cleared")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing vector store: {e}")
            return False
    
    def get_document_count(self) -> int:
        """Get total number of documents in the vector store."""
        return self._collection.count()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        return {
            'total_documents': self.get_document_count(),
            'collection_name': settings.CHROMA_COLLECTION_NAME,
            'embedding_model': settings.EMBEDDING_MODEL_NAME,
            'embedding_dimension': settings.EMBEDDING_DIM,
        }


# ==================== SINGLETON INSTANCE ====================
_vector_store = None


def get_vector_store() -> VectorStoreManager:
    """Get the global VectorStoreManager instance (singleton pattern)."""
    global _vector_store
    
    if _vector_store is None:
        _vector_store = VectorStoreManager()
        logger.info("Created global VectorStoreManager instance")
    
    return _vector_store


# ==================== CONVENIENCE FUNCTIONS ====================
def index_documents(documents: List[Document]) -> bool:
    """Convenience function to index documents."""
    store = get_vector_store()
    return store.index_documents(documents)


def search_documents(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Convenience function to search documents."""
    store = get_vector_store()
    return store.search(query, top_k=top_k)