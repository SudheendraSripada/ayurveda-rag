import os
import json
import logging
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# Import helper modules
from pinecone_helper import get_index_stats, search_index, init_index
from gemini_helper import generate_chat_remedy, stream_chat_remedy
import database

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ayurveda-rag")

load_dotenv()

app = FastAPI(title="Sushruta Ayurveda RAG - Doctor Chat & Auth API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class SignUpPayload(BaseModel):
    email: str
    password: str
    full_name: str

class LoginPayload(BaseModel):
    email: str
    password: str

class ChatMessage(BaseModel):
    role: str  # "user" or "model" / "assistant"
    content: str

class ChatPayload(BaseModel):
    messages: List[ChatMessage]
    session_id: Optional[str] = None
    language: Optional[str] = "English"
    rerank: Optional[bool] = True

class SessionCreatePayload(BaseModel):
    title: Optional[str] = "New Consultation"
    id: Optional[str] = None

class ConfigPayload(BaseModel):
    pinecone_api_key: Optional[str] = None
    pinecone_index_name: Optional[str] = "ayurveda-index"
    gemini_api_key: Optional[str] = None

# Helper to resolve user from Authorization header
def get_current_user_from_header(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    if not authorization:
        return None
    token = authorization.replace("Bearer ", "").strip()
    return database.get_user_by_token(token)

# =========================================================
# 1. USER AUTHENTICATION ENDPOINTS
# =========================================================
@app.post("/api/auth/signup")
def signup(payload: SignUpPayload):
    try:
        user_data = database.create_user(payload.email, payload.password, payload.full_name)
        return {
            "success": True,
            "token": user_data["token"],
            "user": {
                "id": user_data["id"],
                "email": user_data["email"],
                "full_name": user_data["full_name"]
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed. Please try again.")

@app.post("/api/auth/login")
def login(payload: LoginPayload):
    try:
        user_data = database.authenticate_user(payload.email, payload.password)
        return {
            "success": True,
            "token": user_data["token"],
            "user": {
                "id": user_data["id"],
                "email": user_data["email"],
                "full_name": user_data["full_name"]
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Authentication failed.")

@app.get("/api/auth/me")
def get_me(authorization: Optional[str] = Header(None)):
    user = get_current_user_from_header(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"user": user}

@app.post("/api/auth/logout")
def logout(authorization: Optional[str] = Header(None)):
    if authorization:
        token = authorization.replace("Bearer ", "").strip()
        database.delete_token(token)
    return {"success": True, "message": "Logged out successfully"}

# =========================================================
# 2. DATABASE CHAT SESSIONS & HISTORY
# =========================================================
@app.get("/api/chat/sessions")
def list_sessions(authorization: Optional[str] = Header(None)):
    user = get_current_user_from_header(authorization)
    if not user:
        return {"sessions": []}
    sessions = database.get_user_sessions(user["id"])
    return {"sessions": sessions}

@app.post("/api/chat/sessions")
def create_session(payload: SessionCreatePayload, authorization: Optional[str] = Header(None)):
    user = get_current_user_from_header(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Must be logged in to create saved database sessions.")
    session = database.create_chat_session(user["id"], payload.title or "New Consultation", payload.id)
    return {"session": session}

@app.get("/api/chat/sessions/{session_id}/messages")
def get_session_messages(session_id: str, authorization: Optional[str] = Header(None)):
    user = get_current_user_from_header(authorization)
    if not user:
        return {"messages": []}
    messages = database.get_session_messages(session_id, user["id"])
    return {"messages": messages}

@app.delete("/api/chat/sessions/{session_id}")
def delete_session(session_id: str, authorization: Optional[str] = Header(None)):
    user = get_current_user_from_header(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    deleted = database.delete_user_session(session_id, user["id"])
    return {"success": deleted}

# =========================================================
# 3. REAL-TIME FAST STREAMING CONSULTATION ENDPOINT (SSE)
# =========================================================
@app.post("/api/chat/stream")
async def handle_chat_stream(payload: ChatPayload, authorization: Optional[str] = Header(None)):
    """Stream token-by-token consultation in real time with Pinecone scriptures and persistent DB storage."""
    load_dotenv(override=True)
    pinecone_key = os.getenv("PINECONE_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME", "ayurveda-index")
    
    if not gemini_key:
        raise HTTPException(status_code=400, detail="Gemini API Key is not configured.")
        
    if not payload.messages:
        raise HTTPException(status_code=400, detail="No messages provided.")
        
    user = get_current_user_from_header(authorization)
    latest_user_message = payload.messages[-1].content
    selected_language = payload.language or "English"
    session_id = payload.session_id or f"ses_guest_{int(os.times().system * 1000)}"
    
    # If user logged in, persist the user message
    if user:
        try:
            database.add_chat_message(session_id, user["id"], "user", latest_user_message)
        except Exception as e:
            logger.warning(f"Failed to persist user message: {e}")
    
    # 1. Retrieve scriptural context from Pinecone
    passages = []
    if pinecone_key and index_name:
        try:
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
        except Exception as e:
            logger.warning(f"Pinecone retrieval note: {str(e)}")
            passages = []
            
    messages_dict = [{"role": m.role, "content": m.content} for m in payload.messages]
    
    def event_generator():
        # First event: Send citations so UI displays source cards immediately!
        yield f"data: {json.dumps({'type': 'sources', 'sources': passages, 'language': selected_language})}\n\n"
        
        full_response_text = ""
        try:
            for token in stream_chat_remedy(
                api_key=gemini_key,
                messages=messages_dict,
                context_passages=passages,
                language=selected_language
            ):
                full_response_text += token
                yield f"data: {json.dumps({'type': 'token', 'chunk': token})}\n\n"
                
            # If user logged in, persist doctor response in database
            if user:
                try:
                    database.add_chat_message(session_id, user["id"], "doctor", full_response_text, passages)
                except Exception as e:
                    logger.warning(f"Failed to persist doctor message: {e}")
                    
            yield f"data: {json.dumps({'type': 'done', 'reply': full_response_text})}\n\n"
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")

# Non-streaming fallback endpoint
@app.post("/api/chat")
def handle_chat(payload: ChatPayload, authorization: Optional[str] = Header(None)):
    load_dotenv(override=True)
    pinecone_key = os.getenv("PINECONE_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME", "ayurveda-index")
    
    if not gemini_key:
        raise HTTPException(status_code=400, detail="Gemini API Key is not configured.")
    if not payload.messages:
        raise HTTPException(status_code=400, detail="No messages provided.")
        
    user = get_current_user_from_header(authorization)
    latest_user_message = payload.messages[-1].content
    selected_language = payload.language or "English"
    session_id = payload.session_id or f"ses_guest_{int(os.times().system * 1000)}"
    
    if user:
        try:
            database.add_chat_message(session_id, user["id"], "user", latest_user_message)
        except Exception as e:
            logger.warning(f"DB user message store notice: {e}")
            
    passages = []
    if pinecone_key and index_name:
        try:
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
        except Exception as e:
            logger.warning(f"Pinecone retrieval notice: {e}")
            passages = []
            
    try:
        messages_dict = [{"role": m.role, "content": m.content} for m in payload.messages]
        reply_text = generate_chat_remedy(
            api_key=gemini_key,
            messages=messages_dict,
            context_passages=passages,
            language=selected_language
        )
        
        if user:
            try:
                database.add_chat_message(session_id, user["id"], "doctor", reply_text, passages)
            except Exception as e:
                logger.warning(f"DB doctor message store notice: {e}")
                
        return {
            "reply": reply_text,
            "sources": passages,
            "language": selected_language
        }
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =========================================================
# 4. CONFIG & STATS ENDPOINTS
# =========================================================
@app.get("/api/config-status")
def get_config_status():
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

@app.get("/api/index-stats")
def index_stats():
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
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/", StaticFiles(directory="static", html=True), name="root_static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
