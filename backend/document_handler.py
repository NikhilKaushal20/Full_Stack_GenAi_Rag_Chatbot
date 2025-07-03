import os
import logging
import pickle
from pathlib import Path
from typing import Dict, List, Any

from dotenv import load_dotenv
from utils.pdf_loader import PDFLoader
from g_chain import RAGChain

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure vectorstore directory exists
os.makedirs("vectorstore", exist_ok=True)


class DocumentHandler:
    def __init__(self):
        """Initialize the document handler."""
        self.pdf_loader = PDFLoader()
        self.rag_chain = RAGChain()
        self.processed_docs: Dict[str, Dict[str, Any]] = {}  # Tracks all processed documents

    async def process_document(self, file_path: str, filename: str) -> bool:
        """Process a PDF document, create a vectorstore, and save metadata."""
        try:
            logger.info(f"Starting document processing for: {filename}")

            # Extract and chunk text from PDF
            text_chunks = self.pdf_loader.load_and_split(file_path)
            if not text_chunks:
                logger.error(f"No text extracted from {filename}")
                return False

            logger.info(f"Extracted {len(text_chunks)} text chunks from {filename}")

            # Create vectorstore
            vectorstore_path = f"vectorstore/{filename}_vectorstore.pkl"
            success = await self.rag_chain.create_vectorstore(text_chunks, vectorstore_path)

            if success:
                self.processed_docs[filename] = {
                    "file_path": file_path,
                    "vectorstore_path": vectorstore_path,
                    "chunks_count": len(text_chunks),
                    "status": "processed"
                }
                self._save_metadata()
                logger.info(f"Successfully processed document: {filename}")
                return True
            else:
                logger.error(f"Failed to create vectorstore for {filename}")
                return False

        except ValueError as e:
            # Handle OpenAI-specific errors (propagate them up)
            logger.error(f"OpenAI error processing document {filename}: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Error processing document {filename}: {str(e)}")
            return False

    async def query_document(self, question: str, filename: str = None) -> Dict[str, Any]:
        """Query a previously processed document."""
        try:
            if not self.processed_docs:
                self._load_metadata()

            if not filename and self.processed_docs:
                filename = list(self.processed_docs.keys())[-1]
                logger.info(f"No filename specified, using most recent: {filename}")

            if not filename or filename not in self.processed_docs:
                raise ValueError(f"Document not found. Available: {list(self.processed_docs.keys())}")

            vectorstore_path = self.processed_docs[filename]["vectorstore_path"]
            if not os.path.exists(vectorstore_path):
                raise FileNotFoundError(f"Vectorstore missing for document: {filename}")

            logger.info(f"Querying document: {filename} with question: {question}")
            response = await self.rag_chain.query(question, vectorstore_path)

            return {
                "answer": response["answer"],
                "sources": response.get("sources", []),
                "document": filename
            }

        except Exception as e:
            logger.error(f"Error querying document: {str(e)}")
            raise

    def get_processed_documents(self) -> List[str]:
        """Return list of all processed document names."""
        if not self.processed_docs:
            self._load_metadata()
        return list(self.processed_docs.keys())

    def _save_metadata(self):
        """Persist metadata about processed documents."""
        try:
            metadata_path = "vectorstore/processed_docs_metadata.pkl"
            with open(metadata_path, 'wb') as f:
                pickle.dump(self.processed_docs, f)
            logger.info("Saved processed documents metadata.")
        except Exception as e:
            logger.error(f"Error saving metadata: {str(e)}")

    def _load_metadata(self):
        """Load metadata about previously processed documents."""
        try:
            metadata_path = "vectorstore/processed_docs_metadata.pkl"
            if os.path.exists(metadata_path):
                with open(metadata_path, 'rb') as f:
                    self.processed_docs = pickle.load(f)
                logger.info(f"Loaded metadata for {len(self.processed_docs)} documents.")
            else:
                logger.info("No metadata found; starting fresh.")
        except Exception as e:
            logger.error(f"Error loading metadata: {str(e)}")
            self.processed_docs = {}

    def delete_document(self, filename: str) -> bool:
        """Delete a document and its vectorstore from disk and memory."""
        try:
            if filename not in self.processed_docs:
                logger.warning(f"Document {filename} not found for deletion.")
                return False

            doc_info = self.processed_docs[filename]

            # Remove vectorstore and original file
            if os.path.exists(doc_info["vectorstore_path"]):
                os.remove(doc_info["vectorstore_path"])
            if os.path.exists(doc_info["file_path"]):
                os.remove(doc_info["file_path"])

            del self.processed_docs[filename]
            self._save_metadata()

            logger.info(f"Successfully deleted document: {filename}")
            return True

        except Exception as e:
            logger.error(f"Error deleting document {filename}: {str(e)}")
            return False
