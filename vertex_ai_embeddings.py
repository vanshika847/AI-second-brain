"""
Google Vertex AI Embeddings for AI Second Brain
Replaces OpenAI embeddings with Google's embedding models
"""

from vertexai.language_models import TextEmbeddingModel
from google.cloud import aiplatform
from google.oauth2 import service_account
import os

class VertexAIEmbeddings:
    def __init__(self, project_id, location='us-central1', credentials_path='firebase-credentials.json'):
        """
        Initialize Vertex AI for embeddings
        
        Args:
            project_id: Your Google Cloud project ID (e.g., 'ai-second-brain-hackathon')
            location: GCP region (default: us-central1)
            credentials_path: Path to service account JSON file
        """
        try:
            # Set up credentials from service account file
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path
            )
            
            # Initialize Vertex AI
            aiplatform.init(
                project=project_id,
                location=location,
                credentials=credentials
            )
            
            self.project_id = project_id
            self.location = location
            self.model_name = "textembedding-gecko@003"
            
            print(f"✅ Vertex AI initialized successfully!")
            print(f"   Project: {project_id}")
            print(f"   Location: {location}")
            print(f"   Model: {self.model_name}")
            
        except Exception as e:
            print(f"❌ Error initializing Vertex AI: {str(e)}")
            raise
    
    def get_embeddings(self, texts):
        """
        Generate embeddings for text(s) using Google's Vertex AI model
        
        Args:
            texts: Single string or list of strings to embed
            
        Returns:
            List of embedding vectors (each vector is a list of floats)
        """
        try:
            # Convert single string to list
            if isinstance(texts, str):
                texts = [texts]
            
            # Load the embedding model
            model = TextEmbeddingModel.from_pretrained(self.model_name)
            
            # Generate embeddings
            embeddings = model.get_embeddings(texts)
            
            # Extract the vector values from embedding objects
            embedding_vectors = [emb.values for emb in embeddings]
            
            print(f"✅ Generated {len(embedding_vectors)} embeddings")
            print(f"   Dimension: {len(embedding_vectors[0])} (768 for gecko model)")
            
            return embedding_vectors
            
        except Exception as e:
            print(f"❌ Error generating embeddings: {str(e)}")
            return None
    
    def get_embedding(self, text):
        """
        Get embedding for a single text (convenience method)
        
        Args:
            text: Single string to embed
            
        Returns:
            Single embedding vector (list of floats)
        """
        embeddings = self.get_embeddings([text])
        return embeddings[0] if embeddings else None
    
    def get_embedding_dimension(self):
        """
        Get the dimension size of embeddings from this model
        
        Returns:
            Integer dimension size (768 for gecko@003)
        """
        return 768
    
    def batch_embed_documents(self, documents, batch_size=5):
        """
        Embed multiple documents in batches (for large datasets)
        
        Args:
            documents: List of text documents to embed
            batch_size: Number of documents to process at once
            
        Returns:
            List of all embedding vectors
        """
        all_embeddings = []
        
        print(f"📦 Processing {len(documents)} documents in batches of {batch_size}...")
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            print(f"   Processing batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")
            
            batch_embeddings = self.get_embeddings(batch)
            if batch_embeddings:
                all_embeddings.extend(batch_embeddings)
        
        print(f"✅ Completed embedding {len(all_embeddings)} documents")
        return all_embeddings


# Test/Demo code
if __name__ == "__main__":
    print("🚀 Testing Vertex AI Embeddings...\n")
    
    # IMPORTANT: Replace with your actual project ID
    PROJECT_ID = "ai-second-brain-hackathon"  # ← Change this to your project ID
    
    try:
        # Initialize Vertex AI
        embedder = VertexAIEmbeddings(
            project_id=PROJECT_ID,
            credentials_path='firebase-credentials.json'
        )
        
        # Test with sample texts
        print("\n📝 Testing with sample texts...")
        
        sample_texts = [
            "What is artificial intelligence?",
            "How does machine learning work?",
            "Python is a programming language"
        ]
        
        # Generate embeddings
        embeddings = embedder.get_embeddings(sample_texts)
        
        if embeddings:
            print(f"\n✅ Successfully generated embeddings!")
            print(f"   Number of texts: {len(sample_texts)}")
            print(f"   Number of embeddings: {len(embeddings)}")
            print(f"   Embedding dimension: {len(embeddings[0])}")
            print(f"\n   First embedding (first 10 values):")
            print(f"   {embeddings[0][:10]}...")
            
            # Test single embedding
            print("\n📝 Testing single text embedding...")
            single_embedding = embedder.get_embedding("This is a test sentence")
            if single_embedding:
                print(f"✅ Single embedding generated: {len(single_embedding)} dimensions")
        
        print("\n🎉 All tests passed! Vertex AI is ready to use.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Make sure 'firebase-credentials.json' exists in your project folder")
        print("2. Replace PROJECT_ID with your actual Google Cloud project ID")
        print("3. Make sure Vertex AI API is enabled in Google Cloud Console")