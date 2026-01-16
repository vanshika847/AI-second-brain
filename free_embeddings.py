"""
FREE Embeddings using Sentence Transformers (No Google billing needed)
"""

from sentence_transformers import SentenceTransformer
import numpy as np

class FreeEmbeddings:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initialize free embedding model
        
        Args:
            model_name: Model to use (default is fast and small)
        """
        print(f"📦 Loading model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        print(f"✅ Model loaded! Embedding dimension: {self.model.get_sentence_embedding_dimension()}")
    
    def get_embeddings(self, texts):
        """
        Generate embeddings for texts
        
        Args:
            texts: Single string or list of strings
            
        Returns:
            List of embedding vectors
        """
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = self.model.encode(texts, show_progress_bar=True)
        
        print(f"✅ Generated {len(embeddings)} embeddings")
        return embeddings.tolist()
    
    def get_embedding(self, text):
        """Get single embedding"""
        return self.get_embeddings([text])[0]


# Test code
if __name__ == "__main__":
    print("🚀 Testing FREE Embeddings...\n")
    
    embedder = FreeEmbeddings()
    
    # Test
    texts = [
        "What is artificial intelligence?",
        "How does machine learning work?"
    ]
    
    embeddings = embedder.get_embeddings(texts)
    print(f"\n✅ Success! Generated {len(embeddings)} embeddings")
    print(f"   Dimension: {len(embeddings[0])}")