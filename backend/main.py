import os
import json
import logging
from typing import Optional, List
from pydantic import BaseModel
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# Import helper modules
from pinecone_helper import get_index_stats, search_index, init_index
from gemini_helper import generate_chat_remedy

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ayurveda-rag")

load_dotenv()

app = FastAPI(title="Sushruta Ayurveda RAG - Doctor Chat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    role: str  # "user" or "model" / "assistant"
    content: str

class ChatPayload(BaseModel):
    messages: List[ChatMessage]
    rerank: Optional[bool] = True

class ConfigPayload(BaseModel):
    pinecone_api_key: Optional[str] = None
    pinecone_index_name: Optional[str] = "ayurveda-index"
    gemini_api_key: Optional[str] = None

@app.get("/api/config-status")
def get_config_status():
    """Return whether API keys are loaded."""
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

@app.post("/api/config")
def update_config(payload: ConfigPayload):
    """Save or update API configuration in .env."""
    load_dotenv(override=True)
    
    pinecone_key = payload.pinecone_api_key or os.getenv("PINECONE_API_KEY", "")
    gemini_key = payload.gemini_api_key or os.getenv("GEMINI_API_KEY", "")
    index_name = payload.pinecone_index_name or os.getenv("PINECONE_INDEX_NAME", "ayurveda-index")
    
    with open(".env", "w", encoding="utf-8") as f:
        f.write(f"PINECONE_API_KEY={pinecone_key}\n")
        f.write(f"PINECONE_INDEX_NAME={index_name}\n")
        f.write(f"GEMINI_API_KEY={gemini_key}\n")
        
    load_dotenv(override=True)
    return {"status": "success", "message": "Configuration updated successfully."}

@app.post("/api/chat")
def handle_chat(payload: ChatPayload):
    """Multi-turn RAG chat with scriptural retrieval & Perplexity-style citations."""
    load_dotenv(override=True)
    pinecone_key = os.getenv("PINECONE_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME", "ayurveda-index")
    
    if not gemini_key:
        raise HTTPException(status_code=400, detail="Gemini API Key is not configured.")
        
    if not payload.messages:
        raise HTTPException(status_code=400, detail="No messages provided.")
        
    latest_user_message = payload.messages[-1].content
    
    # 1. Retrieve scriptural context from Pinecone if configured
    passages = []
    if pinecone_key and index_name:
        try:
            logger.info(f"Retrieving scriptures from Pinecone for query: '{latest_user_message[:60]}...'")
            reranker = "bge-reranker-v2-m3" if payload.rerank else None
            
            passages = search_index(
                api_key=pinecone_key,
                index_name=index_name,
                query=latest_user_message,
                namespace="ayurveda",
                top_k=15,
                reranker_model=reranker,
                top_n=5
            )
            logger.info(f"Retrieved {len(passages)} scriptural passages.")
        except Exception as e:
            logger.warning(f"Pinecone retrieval note: {str(e)}")
            passages = []
            
    # 2. Call Gemini Ayurvedic Physician Model
    try:
        messages_dict = [{"role": m.role, "content": m.content} for m in payload.messages]
        reply_text = generate_chat_remedy(
            api_key=gemini_key,
            messages=messages_dict,
            context_passages=passages
        )
        
        return {
            "reply": reply_text,
            "sources": passages
        }
    except Exception as e:
        logger.error(f"Chat generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate consultation response: {str(e)}")

@app.get("/api/index-stats")
def index_stats():
    """Retrieve total vector counts and namespaces from Pinecone."""
    load_dotenv(override=True)
    pinecone_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME", "ayurveda-index")
    
    if not pinecone_key or not index_name:
        return {"exists": False, "total_vector_count": 0, "namespaces": {}}
        
    try:
        stats = get_index_stats(pinecone_key, index_name)
        return stats
    except Exception as e:
        return {"exists": False, "error": str(e), "total_vector_count": 0, "namespaces": {}}

# Static files mounting
os.makedirs("static", exist_ok=True)

@app.get("/")
def read_root():
    static_index = os.path.join("static", "index.html")
    if os.path.exists(static_index):
        return FileResponse(static_index)
    return JSONResponse(content={"message": "Sushruta Ayurveda RAG running. Frontend static/index.html not found."})

app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
