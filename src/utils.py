"""
src/utils.py

Utility functions for file handling, validation, and logging.
These are reusable helpers used by other modules.
"""

import logging
from pathlib import Path
from typing import Optional
from config.settings import settings, is_supported_file


# ==================== LOGGING SETUP ====================
def setup_logger(name: str) -> logging.Logger:
    """
    Create a consistent logger across all modules.
    
    Args:
        name: Logger name (usually __name__ from calling module)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Console handler with formatting
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


# Create module logger
logger = setup_logger(__name__)


# ==================== FILE VALIDATION ====================
def validate_file(file_path: Path) -> tuple[bool, Optional[str]]:
    """
    Validate if a file exists, is supported, and within size limits.
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if file exists
    if not file_path.exists():
        return False, f"File not found: {file_path}"
    
    # Check if it's a file (not a directory)
    if not file_path.is_file():
        return False, f"Path is not a file: {file_path}"
    
    # Check if extension is supported
    if not is_supported_file(file_path.name):
        supported = ", ".join(settings.SUPPORTED_EXTENSIONS)
        return False, f"Unsupported file type. Supported: {supported}"
    
    # Check file size
    file_size_mb = file_path.stat().st_size / (1024 * 1024)
    if file_size_mb > settings.MAX_FILE_SIZE_MB:
        return False, f"File too large: {file_size_mb:.1f}MB (max: {settings.MAX_FILE_SIZE_MB}MB)"
    
    return True, None


# ==================== FILE OPERATIONS ====================
def safe_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal attacks."""
    return Path(filename).name


def get_file_extension(filename: str) -> str:
    """Extract file extension in lowercase."""
    return Path(filename).suffix.lower()


def format_file_size(size_bytes: int) -> str:
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


# ==================== TEXT PROCESSING ====================
def clean_text(text: str) -> str:
    """
    Clean extracted text from documents.
    Removes extra whitespace, null characters, etc.
    """
    if not text:
        return ""
    
    # Remove null bytes and form feeds
    text = text.replace('\x00', '').replace('\f', '\n')
    
    # Replace multiple spaces with single space
    text = ' '.join(text.split())
    
    # Replace multiple newlines with max 2 newlines
    while '\n\n\n' in text:
        text = text.replace('\n\n\n', '\n\n')
    
    return text.strip()


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


# ==================== METADATA HELPERS ====================
def extract_metadata(file_path: Path) -> dict:
    """Extract basic metadata from a file."""
    stat = file_path.stat()
    
    return {
        'filename': file_path.name,
        'file_type': get_file_extension(file_path.name),
        'file_size': stat.st_size,
        'file_size_formatted': format_file_size(stat.st_size),
        'modified_time': stat.st_mtime,
    }


# ==================== ERROR HANDLING ====================
class DocumentProcessingError(Exception):
    """Custom exception for document processing errors."""
    pass


class EmbeddingError(Exception):
    """Custom exception for embedding generation errors."""
    pass


class RetrievalError(Exception):
    """Custom exception for vector retrieval errors."""
    pass