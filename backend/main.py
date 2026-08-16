import os
import json
import logging
from typing import Optional
from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# Import our helper modules
from pdf_parser import parse_pdf
from pinecone_helper import init_index, get_index_stats, upsert_chunks, search_index, delete_pinecone_index
from gemini_helper import generate_remedy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ayurveda-rag")

# Load environment variables
load_dotenv()

app = FastAPI(title="Ayurveda RAG API")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory status store for background uploads
# key: filename, value: {"status": "Processing/Completed/Failed", "progress": str, "chunks": int}
upload_status = {}

INDEXED_DOCS_FILE = "indexed_docs.json"

def load_indexed_docs() -> dict:
    """Load metadata of indexed documents from disk."""
    if os.path.exists(INDEXED_DOCS_FILE):
        try:
            with open(INDEXED_DOCS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_indexed_docs(docs: dict):
    """Save metadata of indexed documents to disk."""
    try:
        with open(INDEXED_DOCS_FILE, "w", encoding="utf-8") as f:
            json.dump(docs, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save indexed docs JSON: {str(e)}")

# Models for request validation
class ConfigModel(BaseModel):
    pinecone_api_key: str
    pinecone_index_name: str
    gemini_api_key: str

class QueryModel(BaseModel):
    query: str
    rerank: Optional[bool] = False

# Background task to parse PDF and upsert chunks to Pinecone
def process_pdf_background(file_path: str, filename: str, pinecone_key: str, index_name: str, namespace: str):
    try:
        upload_status[filename] = {"status": "Processing", "progress": "Parsing PDF pages...", "chunks": 0}
        logger.info(f"Background processing started for {filename}")
        
        # Parse and chunk PDF
        chunks = parse_pdf(file_path)
        chunk_count = len(chunks)
        upload_status[filename]["chunks"] = chunk_count
        upload_status[filename]["progress"] = f"Parsed {chunk_count} chunks. Initializing Pinecone index..."
        
        # Initialize index
        init_index(api_key=pinecone_key, index_name=index_name)
        
        # Ingest/Upsert chunks
        upload_status[filename]["progress"] = f"Indexing {chunk_count} chunks to Pinecone..."
        total_upserted = upsert_chunks(api_key=pinecone_key, index_name=index_name, chunks=chunks, namespace=namespace)
        
        # Save to indexed documents
        docs = load_indexed_docs()
        docs[filename] = {
            "filename": filename,
            "chunk_count": total_upserted,
            "indexed_at": time_string()
        }
        save_indexed_docs(docs)
        
        upload_status[filename] = {"status": "Completed", "progress": "Successfully indexed!", "chunks": total_upserted}
        logger.info(f"Background processing completed for {filename}")
        
        # Clean up temporary uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        logger.error(f"Error processing {filename}: {str(e)}")
        upload_status[filename] = {"status": "Failed", "progress": f"Error: {str(e)}", "chunks": 0}
        if os.path.exists(file_path):
            os.remove(file_path)

def time_string():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Endpoints
@app.post("/api/config")
def save_config(config: ConfigModel):
    """Validate credentials and write to .env file."""
    # 1. Validate Pinecone API Key
    try:
        from pinecone import Pinecone
        pc = Pinecone(api_key=config.pinecone_api_key)
        # Attempt to list indexes to check auth
        pc.list_indexes()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid Pinecone API Key: {str(e)}")
        
    # 2. Validate Gemini API Key
    try:
        from google import genai
        client = genai.Client(api_key=config.gemini_api_key)
        # Attempt to list models to check auth
        client.models.list()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid Gemini API Key: {str(e)}")
        
    # Write configuration to .env file
    try:
        with open(".env", "w", encoding="utf-8") as f:
            f.write(f"PINECONE_API_KEY={config.pinecone_api_key}\n")
            f.write(f"PINECONE_INDEX_NAME={config.pinecone_index_name}\n")
            f.write(f"GEMINI_API_KEY={config.gemini_api_key}\n")
        
        # Reload environment
        load_dotenv(override=True)
        return {"status": "success", "message": "Credentials validated and saved successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write configuration: {str(e)}")

@app.get("/api/config-status")
def get_config_status():
    """Check if API keys are configured."""
    load_dotenv(override=True)
    pinecone_configured = bool(os.getenv("PINECONE_API_KEY"))
    gemini_configured = bool(os.getenv("GEMINI_API_KEY"))
    index_name = os.getenv("PINECONE_INDEX_NAME", "ayurveda-index")
    
    return {
        "configured": pinecone_configured and gemini_configured,
        "pinecone_configured": pinecone_configured,
        "gemini_configured": gemini_configured,
        "index_name": index_name
    }

@app.post("/api/upload")
def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Upload a PDF book and trigger background parsing and indexing."""
    load_dotenv(override=True)
    pinecone_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME")
    
    if not pinecone_key or not index_name:
        raise HTTPException(status_code=400, detail="Pinecone credentials are not configured. Please go to Settings.")
        
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    # Create temp directory if it doesn't exist
    os.makedirs("temp", exist_ok=True)
    temp_file_path = os.path.join("temp", file.filename)
    
    with open(temp_file_path, "wb") as f:
        f.write(file.file.read())
        
    # Queue background processing task
    # We use 'ayurveda' as default namespace
    background_tasks.add_task(
        process_pdf_background, 
        temp_file_path, 
        file.filename, 
        pinecone_key, 
        index_name, 
        "ayurveda"
    )
    
    return {"filename": file.filename, "status": "Queued", "message": "File upload successful. Ingestion started in background."}

@app.get("/api/upload-status")
def get_upload_status():
    """Retrieve indexing status of currently processing books."""
    return upload_status

@app.get("/api/documents")
def get_documents():
    """Get the list of indexed books and their details."""
    return load_indexed_docs()

@app.delete("/api/documents/{filename}")
def delete_document(filename: str):
    """Delete a document record from metadata. (Does not delete vectors from Pinecone)."""
    docs = load_indexed_docs()
    if filename in docs:
        del docs[filename]
        save_indexed_docs(docs)
        return {"status": "success", "message": f"Deleted {filename} metadata from library."}
    raise HTTPException(status_code=404, detail="Document not found.")

@app.post("/api/query")
def run_query(payload: QueryModel):
    """Perform RAG search and answer medical remedy question."""
    load_dotenv(override=True)
    pinecone_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME")
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    if not pinecone_key or not index_name or not gemini_key:
        raise HTTPException(status_code=400, detail="System keys are not configured. Please check Settings.")
        
    try:
        # 1. Search Pinecone for context passages
        # Default namespace is 'ayurveda'
        logger.info(f"Querying Pinecone for: '{payload.query}'")
        
        # Setup optional reranker
        reranker_model = None
        if payload.rerank:
            reranker_model = "bge-reranker-v2-m3"
            
        passages = search_index(
            api_key=pinecone_key, 
            index_name=index_name, 
            query=payload.query, 
            namespace="ayurveda", 
            top_k=15,
            reranker_model=reranker_model,
            top_n=5
        )
        
        # 2. Call Gemini to synthesize a remedy response
        logger.info(f"Generating remedy from {len(passages)} passages")
        remedy_text = generate_remedy(
            api_key=gemini_key, 
            query=payload.query, 
            context_passages=passages
        )
        
        return {
            "remedy": remedy_text,
            "sources": passages
        }
    except Exception as e:
        logger.error(f"RAG query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate remedy: {str(e)}")

@app.get("/api/index-stats")
def index_stats():
    """Retrieve total vector counts and namespaces from Pinecone."""
    load_dotenv(override=True)
    pinecone_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME")
    
    if not pinecone_key or not index_name:
        return {"exists": False, "total_vector_count": 0, "namespaces": {}}
        
    try:
        stats = get_index_stats(pinecone_key, index_name)
        return stats
    except Exception as e:
        logger.error(f"Failed to get Pinecone stats: {str(e)}")
        return {"exists": False, "error": str(e), "total_vector_count": 0, "namespaces": {}}

@app.post("/api/clear-index")
def clear_index():
    """Delete the entire index to reset database."""
    load_dotenv(override=True)
    pinecone_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME")
    
    if not pinecone_key or not index_name:
        raise HTTPException(status_code=400, detail="Keys are not configured.")
        
    try:
        delete_pinecone_index(pinecone_key, index_name)
        # Clear document library
        save_indexed_docs({})
        # Clear upload status
        upload_status.clear()
        return {"status": "success", "message": "Index deleted and database reset successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset database: {str(e)}")

# Mount static frontend
# Create static directory if it doesn't exist
os.makedirs("static", exist_ok=True)

# Custom router to serve index.html at root
@app.get("/")
def read_root():
    static_index = os.path.join("static", "index.html")
    if os.path.exists(static_index):
        return FileResponse(static_index)
    return JSONResponse(content={"message": "Ayurveda RAG Server Running. static/index.html not found yet. Please create the frontend static files."})

# Mount the static folder at /static for assets (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    # Listen on localhost:8000
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
