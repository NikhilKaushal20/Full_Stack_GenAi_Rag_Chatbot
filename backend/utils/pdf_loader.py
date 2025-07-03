import logging
from typing import List
import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
import re

logger = logging.getLogger(__name__)

class PDFLoader:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """Initialize PDF loader with chunking parameters"""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len
        )
        
        logger.info(f"PDF Loader initialized with chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF using PyMuPDF"""
        try:
            doc = fitz.open(file_path)
            text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                
                # Clean up the text
                page_text = self._clean_text(page_text)
                
                if page_text.strip():  # Only add non-empty pages
                    text += f"\n--- Page {page_num + 1} ---\n"
                    text += page_text + "\n"
            
            doc.close()
            
            logger.info(f"Successfully extracted text from PDF: {file_path}")
            logger.info(f"Total text length: {len(text)} characters")
            
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {str(e)}")
            raise e
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might interfere
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', text)
        
        # Fix common PDF extraction issues
        text = text.replace('\n-', '\n• ')  # Fix bullet points
        text = text.replace('  ', ' ')  # Remove double spaces
        
        return text.strip()
    
    def split_text_into_chunks(self, text: str) -> List[str]:
        """Split text into chunks using LangChain text splitter"""
        try:
            chunks = self.text_splitter.split_text(text)
            
            # Filter out very short chunks
            chunks = [chunk for chunk in chunks if len(chunk.strip()) > 50]
            
            logger.info(f"Split text into {len(chunks)} chunks")
            
            # Log chunk statistics
            if chunks:
                avg_length = sum(len(chunk) for chunk in chunks) / len(chunks)
                max_length = max(len(chunk) for chunk in chunks)
                min_length = min(len(chunk) for chunk in chunks)
                
                logger.info(f"Chunk statistics - Avg: {avg_length:.0f}, Max: {max_length}, Min: {min_length}")
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error splitting text into chunks: {str(e)}")
            raise e
    
    def load_and_split(self, file_path: str) -> List[str]:
        """Load PDF and split into chunks - main method"""
        try:
            logger.info(f"Processing PDF file: {file_path}")
            
            # Extract text from PDF
            text = self.extract_text_from_pdf(file_path)
            
            if not text.strip():
                logger.warning(f"No text extracted from PDF: {file_path}")
                return []
            
            # Split into chunks
            chunks = self.split_text_into_chunks(text)
            
            if not chunks:
                logger.warning(f"No chunks created from PDF: {file_path}")
                return []
            
            logger.info(f"Successfully processed PDF: {file_path} into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error loading and splitting PDF {file_path}: {str(e)}")
            raise e
    
    def get_pdf_metadata(self, file_path: str) -> dict:
        """Extract metadata from PDF"""
        try:
            doc = fitz.open(file_path)
            metadata = doc.metadata
            
            # Add additional info
            metadata['page_count'] = len(doc)
            metadata['file_path'] = file_path
            
            doc.close()
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting PDF metadata: {str(e)}")
            return {}
    
    def extract_text_by_page(self, file_path: str) -> List[str]:
        """Extract text page by page - useful for page-specific queries"""
        try:
            doc = fitz.open(file_path)
            pages = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_text = page.get_text()
                page_text = self._clean_text(page_text)
                
                if page_text.strip():
                    pages.append({
                        'page_number': page_num + 1,
                        'text': page_text
                    })
            
            doc.close()
            
            logger.info(f"Extracted text from {len(pages)} pages")
            return pages
            
        except Exception as e:
            logger.error(f"Error extracting text by page: {str(e)}")
            return []