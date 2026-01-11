"""
src/document_processor.py

Document processing module for parsing and chunking various file formats.
Supports: PDF, DOCX, PPTX, TXT, MD
"""

from pathlib import Path
from typing import List, Dict, Optional
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.readers.file import (
    PDFReader,
    DocxReader,
    PptxReader,
)
from config.settings import settings
from src.utils import (
    setup_logger,
    validate_file,
    clean_text,
    extract_metadata,
    DocumentProcessingError,
)

# Setup logger
logger = setup_logger(__name__)


class DocumentProcessor:
    """
    Processes documents: reads, parses, cleans, and chunks text.
    """
    
    def __init__(self):
        """Initialize document readers and text splitter."""
        # Initialize readers for different file types
        self.pdf_reader = PDFReader()
        self.docx_reader = DocxReader()
        self.pptx_reader = PptxReader()
        
        # Initialize text splitter (chunks documents into smaller pieces)
        self.text_splitter = SentenceSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )
        
        logger.info("DocumentProcessor initialized")
    
    def load_document(self, file_path: Path) -> List[Document]:
        """
        Load and parse a document based on its file type.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            List of Document objects with text and metadata
            
        Raises:
            DocumentProcessingError: If file cannot be processed
        """
        # Validate file first
        is_valid, error_msg = validate_file(file_path)
        if not is_valid:
            logger.error(f"File validation failed: {error_msg}")
            raise DocumentProcessingError(error_msg)
        
        logger.info(f"Loading document: {file_path.name}")
        
        try:
            # Get file extension
            ext = file_path.suffix.lower()
            
            # Route to appropriate reader
            if ext == ".pdf":
                documents = self._load_pdf(file_path)
            elif ext == ".docx":
                documents = self._load_docx(file_path)
            elif ext == ".pptx":
                documents = self._load_pptx(file_path)
            elif ext in [".txt", ".md"]:
                documents = self._load_text(file_path)
            else:
                raise DocumentProcessingError(f"Unsupported file type: {ext}")
            
            logger.info(f"✅ Loaded {len(documents)} document(s) from {file_path.name}")
            return documents
            
        except Exception as e:
            logger.error(f"Error loading document: {e}")
            raise DocumentProcessingError(f"Failed to load document: {e}")
    
    def _load_pdf(self, file_path: Path) -> List[Document]:
        """Load PDF document."""
        try:
            documents = self.pdf_reader.load_data(file=file_path)
            
            # Create new documents instead of modifying originals
            processed_docs = []
            for i, doc in enumerate(documents):
                new_doc = Document(
                    text=clean_text(doc.text),
                    metadata={
                        **doc.metadata,  # Keep original metadata
                        'source': file_path.name,
                        'file_type': 'pdf',
                        'page': i + 1,
                    }
                )
                processed_docs.append(new_doc)
            
            return processed_docs
            
        except Exception as e:
            raise DocumentProcessingError(f"PDF parsing error: {e}")
    
    def _load_docx(self, file_path: Path) -> List[Document]:
        """Load DOCX document."""
        try:
            documents = self.docx_reader.load_data(file=file_path)
            
            # Create new documents instead of modifying
            processed_docs = []
            for doc in documents:
                new_doc = Document(
                    text=clean_text(doc.text),
                    metadata={
                        **doc.metadata,
                        'source': file_path.name,
                        'file_type': 'docx',
                    }
                )
                processed_docs.append(new_doc)
            
            return processed_docs
            
        except Exception as e:
            raise DocumentProcessingError(f"DOCX parsing error: {e}")
    
    def _load_pptx(self, file_path: Path) -> List[Document]:
        """Load PPTX document."""
        try:
            documents = self.pptx_reader.load_data(file=file_path)
            
            # Create new documents
            processed_docs = []
            for i, doc in enumerate(documents):
                new_doc = Document(
                    text=clean_text(doc.text),
                    metadata={
                        **doc.metadata,
                        'source': file_path.name,
                        'file_type': 'pptx',
                        'slide': i + 1,
                    }
                )
                processed_docs.append(new_doc)
            
            return processed_docs
            
        except Exception as e:
            raise DocumentProcessingError(f"PPTX parsing error: {e}")
    
    def _load_text(self, file_path: Path) -> List[Document]:
        """Load plain text or markdown file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Create Document object
            doc = Document(
                text=clean_text(text),
                metadata={
                    'source': file_path.name,
                    'file_type': file_path.suffix.lower()[1:],  # Remove dot
                }
            )
            
            return [doc]
            
        except Exception as e:
            raise DocumentProcessingError(f"Text file reading error: {e}")
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into smaller chunks for better retrieval.
        
        Args:
            documents: List of Document objects
            
        Returns:
            List of chunked Document objects
        """
        logger.info(f"Chunking {len(documents)} documents...")
        
        try:
            # Use LlamaIndex's sentence splitter
            chunks = self.text_splitter.get_nodes_from_documents(documents)
            
            # Convert nodes back to Documents with metadata preservation
            chunked_docs = []
            for i, chunk in enumerate(chunks):
                # Create new document from chunk
                doc = Document(
                    text=chunk.get_content(),
                    metadata={
                        **chunk.metadata,  # Preserve original metadata
                        'chunk_id': i,
                        'chunk_size': len(chunk.get_content()),
                    }
                )
                chunked_docs.append(doc)
            
            logger.info(f"✅ Created {len(chunked_docs)} chunks")
            return chunked_docs
            
        except Exception as e:
            logger.error(f"Chunking error: {e}")
            raise DocumentProcessingError(f"Failed to chunk documents: {e}")
    
    def process_file(self, file_path: Path) -> List[Document]:
        """
        Complete processing pipeline: load → chunk → return.
        
        Args:
            file_path: Path to document file
            
        Returns:
            List of chunked Document objects ready for embedding
        """
        logger.info(f"Processing file: {file_path.name}")
        
        # Step 1: Load document
        documents = self.load_document(file_path)
        
        # Step 2: Chunk into smaller pieces
        chunks = self.chunk_documents(documents)
        
        logger.info(f"✅ File processed: {file_path.name} → {len(chunks)} chunks")
        return chunks


# ==================== SINGLETON INSTANCE ====================
_document_processor = None


def get_document_processor() -> DocumentProcessor:
    """
    Get the global DocumentProcessor instance (singleton pattern).
    
    Returns:
        Singleton DocumentProcessor instance
    """
    global _document_processor
    
    if _document_processor is None:
        _document_processor = DocumentProcessor()
        logger.info("Created global DocumentProcessor instance")
    
    return _document_processor


# ==================== CONVENIENCE FUNCTIONS ====================
def process_document(file_path: Path) -> List[Document]:
    """
    Convenience function to process a document.
    
    Args:
        file_path: Path to document
        
    Returns:
        List of chunked Documents
    """
    processor = get_document_processor()
    return processor.process_file(file_path)