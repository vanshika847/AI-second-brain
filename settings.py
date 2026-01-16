"""
config/settings.py

Central configuration for AI Second Brain.
Groq API version - FREE and fast!
"""

from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field
import os

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent


class Settings(BaseSettings):
    """
    Application settings with Groq integration.
    
    Environment Variables:
    - GROQ_API_KEY: Your Groq API key (free)
    - OPENAI_API_KEY: Your OpenAI API key (optional, paid)
    """
    
    # ==================== API KEYS ====================
    # Groq API key (FREE)
    GROQ_API_KEY: str = Field(
        default="",
        description="Groq API key - get free at https://console.groq.com"
    )
    
    # OpenAI API key (optional, paid)
    OPENAI_API_KEY: str = Field(
        default="",
        description="OpenAI API key (optional, paid)"
    )
    
    # ==================== PATHS ====================
    UPLOAD_DIR: Path = PROJECT_ROOT / "data" / "uploads"
    CHROMA_DB_DIR: Path = PROJECT_ROOT / "data" / "chroma_db"
    CHROMA_COLLECTION_NAME: str = "documents"
    
    # ==================== MODELS ====================
    # Embedding model - LOCAL (free, no API cost)
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-small-en-v1.5"
    EMBEDDING_DIM: int = 384
    
    # LLM Provider: True = Groq (free), False = OpenAI (paid)
    USE_GROQ: bool = True
    
    # Groq settings (FREE, fast)
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    GROQ_API_BASE: str = "https://api.groq.com/openai/v1"
    GROQ_TEMPERATURE: float = 0.1
    GROQ_MAX_TOKENS: int = 1024
    
    # OpenAI settings (paid, only used if USE_GROQ = False)
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_TEMPERATURE: float = 0.1
    OPENAI_MAX_TOKENS: int = 1000
    
    # ==================== CHUNKING ====================
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50
    
    # ==================== RETRIEVAL ====================
    TOP_K_RETRIEVAL: int = 5
    SIMILARITY_THRESHOLD: float = 0.5
    
    # ==================== CONVERSATION ====================
    MEMORY_WINDOW: int = 3
    
    # ==================== SUPPORTED FILE TYPES ====================
    SUPPORTED_EXTENSIONS: list[str] = [".pdf", ".docx", ".pptx", ".txt", ".md"]
    MAX_FILE_SIZE_MB: int = 1024  # 1 GB
    
    # ==================== UI ====================
    APP_TITLE: str = "🧠 AI Second Brain"
    PAGE_ICON: str = "🧠"
    WELCOME_MESSAGE: str = """
    👋 Welcome to your AI Second Brain!
    
    **Get started:**
    1. Upload documents (PDF, DOCX, PPTX, TXT, MD)
    2. Wait for processing (you'll see a success message)
    3. Ask questions about your documents
    
    **Features:**
    - Powered by Groq (100% FREE, lightning fast ⚡)
    - Local embeddings (privacy + no costs)
    - Source citations with page numbers
    - Conversation memory
    
    **Cost:** $0 - Completely FREE! 🎉
    """
    
    class Config:
        arbitrary_types_allowed = True
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def __init__(self, **kwargs):
        """Initialize settings and create necessary directories"""
        super().__init__(**kwargs)
        
        # Load API keys from environment
        if self.USE_GROQ:
            # Using Groq (free)
            if not self.GROQ_API_KEY:
                self.GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
            
            if not self.GROQ_API_KEY:
                raise ValueError(
                    "❌ GROQ_API_KEY not found!\n\n"
                    "Get your FREE key at: https://console.groq.com/\n"
                    "Then add to .env file: GROQ_API_KEY=gsk_...\n\n"
                    "Steps:\n"
                    "1. Visit https://console.groq.com/\n"
                    "2. Sign up (free)\n"
                    "3. Go to API Keys section\n"
                    "4. Create new key\n"
                    "5. Add to .env file"
                )
        else:
            # Using OpenAI (paid)
            if not self.OPENAI_API_KEY:
                self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
            
            if not self.OPENAI_API_KEY:
                raise ValueError(
                    "❌ OPENAI_API_KEY not found!\n\n"
                    "Set USE_GROQ = True to use FREE Groq instead.\n"
                    "Or get OpenAI key at: https://platform.openai.com/api-keys"
                )
        
        # Create directories (OneDrive safe)
        try:
            self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        except (FileExistsError, OSError):
            pass
        
        try:
            self.CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)
        except (FileExistsError, OSError):
            pass


# ==================== SINGLETON INSTANCE ====================
settings = Settings()


# ==================== HELPER FUNCTIONS ====================
def get_upload_path(filename: str) -> Path:
    """Get full path for an uploaded file."""
    return settings.UPLOAD_DIR / filename


def is_supported_file(filename: str) -> bool:
    """Check if a file extension is supported."""
    return Path(filename).suffix.lower() in settings.SUPPORTED_EXTENSIONS


def estimate_cost(num_tokens: int) -> float:
    """
    Estimate API cost for a request.
    
    For Groq: FREE (always returns 0)
    For OpenAI: Based on model pricing
    """
    if settings.USE_GROQ:
        return 0.0  # Groq is free!
    else:
        pricing = {
            "gpt-3.5-turbo": 0.002 / 1000,
            "gpt-4": 0.03 / 1000,
            "gpt-4-turbo": 0.01 / 1000,
        }
        return num_tokens * pricing.get(settings.OPENAI_MODEL, 0.002 / 1000)