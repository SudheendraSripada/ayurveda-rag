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
from pinecone_helper import get_index_stats, search_index, init_index, resolve_pinecone_api_key
from gemini_helper import generate_chat_remedy, stream_chat_remedy
import database
import rag_precision

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
# 3. RAG PRECISION CONTEXT RETRIEVAL & CHAT ENDPOINTS
# =========================================================
def retrieve_ayurvedic_context(query: str, rerank: bool = True) -> List[Dict[str, Any]]:
    """
    Precision Ayurvedic Context Retriever:
    1. Extracts clinical conditions & performs bilingual query expansion (Telugu + Sanskrit + English).
    2. Dense vector search in Pinecone with llama-text-embed-v2 + bge-reranker-v2-m3 cross-encoder.
    3. Re-scores hits using clinical relevance boost.
    4. Augments with direct SQLite treatise metadata and FreeGurukul archive links.
    """
    pinecone_key = resolve_pinecone_api_key()
    index_name = os.getenv("PINECONE_INDEX_NAME", "ayurveda-index")
    
    clinical_analysis = rag_precision.expand_ayurvedic_query(query)
    search_query = clinical_analysis["expanded_query"]
    logger.info(f"RAG Precision: Expanding query '{query}' -> '{search_query}'")
    
    passages: List[Dict[str, Any]] = []
    if pinecone_key and index_name:
        try:
            reranker = "bge-reranker-v2-m3" if rerank else None
            # Retrieve verified Ayurvedic treatises first
            raw_passages = search_index(
                api_key=pinecone_key,
                index_name=index_name,
                query=search_query,
                namespace="ayurveda",
                top_k=25,
                reranker_model=reranker,
                top_n=8,
                filter={"is_ayurveda": {"$eq": True}}
            )
            # If strictly filtered search returned < 3 results, relax filter
            if len(raw_passages) < 3:
                fallback_passages = search_index(
                    api_key=pinecone_key,
                    index_name=index_name,
                    query=search_query,
                    namespace="ayurveda",
                    top_k=15,
                    reranker_model=reranker,
                    top_n=6
                )
                seen_ids = {p["id"] for p in raw_passages}
                for fp in fallback_passages:
                    if fp["id"] not in seen_ids:
                        raw_passages.append(fp)
                        
            for p in raw_passages:
                p["precision_score"] = rag_precision.calculate_precision_relevance_score(p, clinical_analysis)
            raw_passages.sort(key=lambda x: -x.get("precision_score", 0.0))
            passages = raw_passages[:6]
        except Exception as e:
            logger.warning(f"Pinecone precision retrieval note: {e}")
            passages = []
            
    # Hybrid SQLite Augmentation if few vector passages found
    if len(passages) < 3:
        try:
            search_terms = clinical_analysis.get("telugu_keywords", [])
            primary_term = search_terms[0] if search_terms else query
            db_candidates = database.search_books(
                query=primary_term,
                is_ayurveda=True,
                limit=3
            ).get("books", [])
            
            for b in db_candidates:
                if not any(p.get("download_url") == b["download_url"] for p in passages):
                    topics_str = ", ".join(b.get("topics", [])) if b.get("topics") else "Ayurvedic Treatment"
                    passages.append({
                        "id": f"db_{b['id']}",
                        "score": 0.88,
                        "text": f"Classical Treatise: {b['title_telugu']} ({b['title_english']}). Category: {b['category']}. Focus Topics: {topics_str}. FreeGurukul Archive #{b['book_id']}.",
                        "source_book": b["title_english"] or b["title_telugu"],
                        "page_number": b["source_pdf_page"],
                        "category": b["category"],
                        "download_url": b["download_url"],
                        "is_ayurveda": True
                    })
        except Exception as e:
            logger.warning(f"SQLite hybrid retrieval notice: {e}")
            
    return passages

@app.post("/api/chat/stream")
async def handle_chat_stream(payload: ChatPayload, authorization: Optional[str] = Header(None)):
    """Stream token-by-token consultation in real time with Pinecone scriptures and persistent DB storage."""
    load_dotenv(override=True)
    gemini_key = os.getenv("GEMINI_API_KEY")
    
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
            logger.warning(f"Failed to persist user message: {e}")
    
    # Retrieve scriptural passages with high precision
    passages = retrieve_ayurvedic_context(latest_user_message, payload.rerank)
    messages_dict = [{"role": m.role, "content": m.content} for m in payload.messages]
    
    def event_generator():
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

@app.post("/api/chat")
def handle_chat(payload: ChatPayload, authorization: Optional[str] = Header(None)):
    load_dotenv(override=True)
    gemini_key = os.getenv("GEMINI_API_KEY")
    
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
            
    passages = retrieve_ayurvedic_context(latest_user_message, payload.rerank)
            
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
    pinecone_key = resolve_pinecone_api_key()
    pinecone_configured = bool(pinecone_key)
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
    pinecone_key = payload.pinecone_api_key or resolve_pinecone_api_key()
    gemini_key = payload.gemini_api_key or os.getenv("GEMINI_API_KEY", "")
    index_name = payload.pinecone_index_name or os.getenv("PINECONE_INDEX_NAME", "ayurveda-index")
    
    env_paths = [
        os.path.join(os.path.dirname(__file__), ".env"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    ]
    for env_path in env_paths:
        try:
            with open(env_path, "w", encoding="utf-8") as f:
                f.write(f"PINECONE_API_KEY={pinecone_key}\n")
                f.write(f"PINECONE_INDEX_NAME={index_name}\n")
                f.write(f"GEMINI_API_KEY={gemini_key}\n")
        except Exception:
            pass
        
    load_dotenv(override=True)
    return {"status": "success", "message": "Configuration updated successfully."}

@app.get("/api/index-stats")
def index_stats():
    load_dotenv(override=True)
    pinecone_key = resolve_pinecone_api_key()
    index_name = os.getenv("PINECONE_INDEX_NAME", "ayurveda-index")
    
    if not pinecone_key or not index_name:
        return {"exists": False, "total_vector_count": 0, "namespaces": {}}
        
    try:
        stats = get_index_stats(pinecone_key, index_name)
        return stats
    except Exception as e:
        return {"exists": False, "error": str(e), "total_vector_count": 0, "namespaces": {}}

# =========================================================
# 5. FREEGURUKUL 3500 TELUGU BOOKS CATALOG API
# =========================================================
@app.get("/api/books")
def list_books(
    query: Optional[str] = None,
    category: Optional[str] = None,
    is_ayurveda: Optional[bool] = None,
    limit: int = 20,
    offset: int = 0
):
    """Browse and search the ~3500 FreeGurukul Telugu catalog with topic and category filters."""
    try:
        results = database.search_books(
            query=query,
            category=category,
            is_ayurveda=is_ayurveda,
            limit=min(100, max(1, limit)),
            offset=max(0, offset)
        )
        return results
    except Exception as e:
        logger.error(f"Books search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/books/stats")
def catalog_stats():
    """Retrieve aggregate statistics about the 3500 books catalog."""
    try:
        return database.get_catalog_stats()
    except Exception as e:
        logger.error(f"Catalog stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/books/categories")
def catalog_categories():
    """Retrieve all catalog categories with book counts."""
    try:
        return {"categories": database.get_categories()}
    except Exception as e:
        logger.error(f"Catalog categories error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/books/{book_id}")
def get_book_details(book_id: int):
    """Retrieve details and download link for a specific catalog book."""
    book = database.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail=f"Book #{book_id} not found in catalog")
    return {"book": book}

# Static files mounting
static_candidates = [
    os.path.join(os.path.dirname(__file__), "static"),
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend", "static"),
    "static"
]
static_dir = next((d for d in static_candidates if os.path.exists(d)), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="root_static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
