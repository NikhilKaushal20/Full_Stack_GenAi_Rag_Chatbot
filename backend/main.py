from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import shutil
from pathlib import Path
from document_handler import DocumentHandler

import logging

# Load environment variables
load_dotenv()

# Ensure required directories exist
Path("uploaded_files").mkdir(parents=True, exist_ok=True)
Path("vectorstore").mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="GenAI RAG Chatbot API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize document handler
doc_handler = DocumentHandler()

# Pydantic model for query
class QueryRequest(BaseModel):
    question: str
    filename: str = None

@app.get("/")
async def root():
    return {"message": "GenAI RAG Chatbot API is running!"}

@app.post("/process-pdf")
async def process_pdf(file: UploadFile = File(...)):
    """Upload and process a PDF file"""
    try:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        file_path = f"uploaded_files/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"Processing PDF: {file.filename}")
        success = await doc_handler.process_document(file_path, file.filename)

        if success:
            return {
                "message": f"PDF '{file.filename}' processed successfully",
                "filename": file.filename,
                "status": "ready"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to process PDF")

    except ValueError as e:
        # Handle OpenAI-specific errors
        error_msg = str(e)
        if "quota exceeded" in error_msg.lower():
            raise HTTPException(status_code=429, detail=error_msg)
        elif "authentication" in error_msg.lower():
            raise HTTPException(status_code=401, detail=error_msg)
        else:
            raise HTTPException(status_code=503, detail=error_msg)
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@app.post("/query")
async def query_document(query_request: QueryRequest):
    """Query the processed document"""
    try:
        if not query_request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")

        logger.info(f"Processing query: {query_request.question}")
        response = await doc_handler.query_document(
            query_request.question,
            query_request.filename
        )

        return {
            "question": query_request.question,
            "answer": response["answer"],
            "sources": response.get("sources", []),
            "filename": query_request.filename
        }

    except ValueError as e:
        # Handle OpenAI-specific errors
        error_dict = eval(str(e)) if str(e).startswith('{') else {"error": str(e)}
        if "quota exceeded" in error_dict.get("error", "").lower():
            raise HTTPException(status_code=429, detail=error_dict["error"])
        elif "authentication" in error_dict.get("error", "").lower():
            raise HTTPException(status_code=401, detail=error_dict["error"])
        else:
            raise HTTPException(status_code=503, detail=error_dict["error"])
    except Exception as e:
        logger.error(f"Error querying document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error querying document: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "GenAI RAG Chatbot API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
