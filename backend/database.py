import sqlite3
import hashlib
import secrets
import json
import os
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta

import shutil

DEFAULT_TOKEN_TTL_DAYS = 30

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def calculate_token_expiry(days: int = DEFAULT_TOKEN_TTL_DAYS) -> str:
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()

def _resolve_db_path() -> str:
    env_path = os.getenv("AYURVEDA_DB_PATH")
    if env_path:
        return env_path
    
    default_dir = os.path.dirname(os.path.abspath(__file__))
    default_db = os.path.join(default_dir, "ayurveda.db")
    
    is_serverless = bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME") or os.getenv("NOW_REGION"))
    is_readonly = not os.access(default_dir, os.W_OK)
    
    if is_serverless or is_readonly:
        tmp_dir = os.getenv("TMPDIR", "/tmp")
        tmp_db = os.path.join(tmp_dir, "ayurveda.db")
        if not os.path.exists(tmp_db) and os.path.exists(default_db):
            try:
                shutil.copyfile(default_db, tmp_db)
            except Exception:
                pass
        return tmp_db
    
    return default_db

DB_PATH = _resolve_db_path()

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
    except sqlite3.OperationalError:
        pass
    return conn

def init_db():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            full_name TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """)
        
        # Auth tokens table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS auth_tokens (
            token TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)
        
        # Migration: ensure expires_at exists if auth_tokens was created without it
        cursor.execute("PRAGMA table_info(auth_tokens);")
        token_cols = [col[1] for col in cursor.fetchall()]
        if "expires_at" not in token_cols:
            cursor.execute("ALTER TABLE auth_tokens ADD COLUMN expires_at TEXT;")
            
        # Cleanup expired tokens on initialization
        cursor.execute("""
        DELETE FROM auth_tokens 
        WHERE (expires_at IS NOT NULL AND expires_at < ?)
           OR (expires_at IS NULL AND datetime(created_at, '+30 days') < datetime('now'))
        """, (now_iso(),))
        
        # Chat sessions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)
        
        # Chat messages table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            sources_json TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
        );
        """)
        
        # Books table for 3500 catalog
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY,
            book_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            title_telugu TEXT NOT NULL,
            title_english TEXT NOT NULL,
            pages INTEGER,
            size_mb INTEGER,
            download_url TEXT,
            is_ayurveda BOOLEAN DEFAULT 0,
            topics TEXT,
            source_pdf_page INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_books_cat ON books(category);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_books_ayur ON books(is_ayurveda);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_books_en ON books(title_english);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_books_book_id ON books(book_id);")
        
        conn.commit()
        conn.close()
    except sqlite3.OperationalError:
        pass

# Password hashing
def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    if not salt:
        salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000).hex()
    return pwd_hash, salt

def verify_password(password: str, password_hash: str, salt: str) -> bool:
    new_hash, _ = hash_password(password, salt)
    return secrets.compare_digest(new_hash, password_hash)

# User operations
def create_user(email: str, password: str, full_name: str) -> Dict[str, Any]:
    email = email.strip().lower()
    full_name = full_name.strip()
    if not email or not password or not full_name:
        raise ValueError("All fields are required")
    
    pwd_hash, salt = hash_password(password)
    user_id = "usr_" + secrets.token_hex(8)
    now = now_iso()
    
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (id, email, password_hash, salt, full_name, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, email, pwd_hash, salt, full_name, now)
        )
        token = "tok_" + secrets.token_hex(24)
        expires_at = calculate_token_expiry(DEFAULT_TOKEN_TTL_DAYS)
        cursor.execute(
            "INSERT INTO auth_tokens (token, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
            (token, user_id, now, expires_at)
        )
        conn.commit()
        return {"id": user_id, "email": email, "full_name": full_name, "token": token}
    except sqlite3.IntegrityError:
        raise ValueError("An account with this email already exists")
    finally:
        conn.close()

def authenticate_user(email: str, password: str) -> Dict[str, Any]:
    email = email.strip().lower()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, password_hash, salt, full_name FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        raise ValueError("Invalid email or password")
    
    if not verify_password(password, user["password_hash"], user["salt"]):
        conn.close()
        raise ValueError("Invalid email or password")
    
    token = "tok_" + secrets.token_hex(24)
    now = now_iso()
    expires_at = calculate_token_expiry(DEFAULT_TOKEN_TTL_DAYS)
    cursor.execute(
        "INSERT INTO auth_tokens (token, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
        (token, user["id"], now, expires_at)
    )
    conn.commit()
    conn.close()
    
    return {"id": user["id"], "email": user["email"], "full_name": user["full_name"], "token": token}

def get_user_by_token(token: str) -> Optional[Dict[str, Any]]:
    if not token:
        return None
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT u.id, u.email, u.full_name, u.created_at, t.created_at AS token_created_at, t.expires_at
    FROM auth_tokens t
    JOIN users u ON t.user_id = u.id
    WHERE t.token = ?
    """, (token,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    
    # Check token expiration
    expires_at = row["expires_at"]
    if not expires_at:
        token_created_at = row["token_created_at"]
        if token_created_at:
            try:
                c_dt = datetime.fromisoformat(token_created_at)
                if c_dt.tzinfo is None:
                    c_dt = c_dt.replace(tzinfo=timezone.utc)
                if datetime.now(timezone.utc) > c_dt + timedelta(days=DEFAULT_TOKEN_TTL_DAYS):
                    cursor.execute("DELETE FROM auth_tokens WHERE token = ?", (token,))
                    conn.commit()
                    conn.close()
                    return None
            except Exception:
                cursor.execute("DELETE FROM auth_tokens WHERE token = ?", (token,))
                conn.commit()
                conn.close()
                return None
    else:
        try:
            exp_dt = datetime.fromisoformat(expires_at)
            if exp_dt.tzinfo is None:
                exp_dt = exp_dt.replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) > exp_dt:
                cursor.execute("DELETE FROM auth_tokens WHERE token = ?", (token,))
                conn.commit()
                conn.close()
                return None
        except Exception:
            cursor.execute("DELETE FROM auth_tokens WHERE token = ?", (token,))
            conn.commit()
            conn.close()
            return None

    conn.close()
    return {"id": row["id"], "email": row["email"], "full_name": row["full_name"]}

def cleanup_expired_tokens() -> int:
    """Deletes all expired tokens from auth_tokens and returns the number of deleted rows."""
    now = now_iso()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    DELETE FROM auth_tokens 
    WHERE (expires_at IS NOT NULL AND expires_at < ?)
       OR (expires_at IS NULL AND datetime(created_at, '+30 days') < datetime('now'))
    """, (now,))
    count = cursor.rowcount
    conn.commit()
    conn.close()
    return count

def delete_token(token: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM auth_tokens WHERE token = ?", (token,))
    conn.commit()
    conn.close()

# Session operations
def get_user_sessions(user_id: str) -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, created_at, updated_at FROM chat_sessions WHERE user_id = ? ORDER BY updated_at DESC", (user_id,))
    rows = cursor.fetchall()
    sessions = [{"id": r["id"], "title": r["title"], "created_at": r["created_at"], "updated_at": r["updated_at"]} for r in rows]
    conn.close()
    return sessions

def create_chat_session(user_id: str, title: str = "New Consultation", session_id: Optional[str] = None) -> Dict[str, Any]:
    if not session_id:
        session_id = "ses_" + secrets.token_hex(8)
    now = now_iso()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_sessions (id, user_id, title, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
        (session_id, user_id, title, now, now)
    )
    conn.commit()
    conn.close()
    return {"id": session_id, "title": title, "created_at": now, "updated_at": now}

def get_session_messages(session_id: str, user_id: str) -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    # Verify ownership
    cursor.execute("SELECT user_id FROM chat_sessions WHERE id = ?", (session_id,))
    session = cursor.fetchone()
    if not session or session["user_id"] != user_id:
        conn.close()
        return []
    
    cursor.execute("SELECT id, role, content, sources_json, created_at FROM chat_messages WHERE session_id = ? ORDER BY created_at ASC", (session_id,))
    rows = cursor.fetchall()
    messages = []
    for r in rows:
        sources = json.loads(r["sources_json"]) if r["sources_json"] else []
        messages.append({
            "id": r["id"],
            "role": r["role"],
            "content": r["content"],
            "sources": sources,
            "created_at": r["created_at"]
        })
    conn.close()
    return messages

def add_chat_message(session_id: str, user_id: str, role: str, content: str, sources: Optional[List[Dict]] = None) -> Dict[str, Any]:
    conn = get_db()
    cursor = conn.cursor()
    # Verify session or create if not exists
    cursor.execute("SELECT id, user_id, title FROM chat_sessions WHERE id = ?", (session_id,))
    session = cursor.fetchone()
    now = now_iso()
    
    if not session:
        title = content[:28] + "..." if len(content) > 30 else content
        cursor.execute("INSERT INTO chat_sessions (id, user_id, title, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                       (session_id, user_id, title, now, now))
    elif session["user_id"] != user_id:
        conn.close()
        raise PermissionError("Unauthorized access to session")
    else:
        cursor.execute("UPDATE chat_sessions SET updated_at = ? WHERE id = ?", (now, session_id))
    
    msg_id = "msg_" + secrets.token_hex(8)
    sources_json = json.dumps(sources) if sources else None
    cursor.execute(
        "INSERT INTO chat_messages (id, session_id, role, content, sources_json, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (msg_id, session_id, role, content, sources_json, now)
    )
    conn.commit()
    conn.close()
    return {"id": msg_id, "session_id": session_id, "role": role, "content": content, "sources": sources or [], "created_at": now}

def delete_user_session(session_id: str, user_id: str) -> bool:
    conn = get_db()
    cursor = conn.cursor()
    # Verify session ownership first to prevent IDOR message deletion
    cursor.execute("SELECT id FROM chat_sessions WHERE id = ? AND user_id = ?", (session_id, user_id))
    session = cursor.fetchone()
    if not session:
        conn.close()
        return False

    cursor.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
    cursor.execute("DELETE FROM chat_sessions WHERE id = ? AND user_id = ?", (session_id, user_id))
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected

# =========================================================
# Books Catalog Queries (3500 FreeGurukul Books)
# =========================================================
def search_books(
    query: Optional[str] = None, 
    category: Optional[str] = None, 
    is_ayurveda: Optional[bool] = None, 
    limit: int = 20, 
    offset: int = 0
) -> Dict[str, Any]:
    conn = get_db()
    cursor = conn.cursor()
    
    where_clauses = []
    params: List[Any] = []
    
    if query and query.strip():
        q = f"%{query.strip()}%"
        where_clauses.append("(title_telugu LIKE ? OR title_english LIKE ? OR topics LIKE ?)")
        params.extend([q, q, q])
        
    if category and category.strip() and category.strip() != "All":
        where_clauses.append("category = ?")
        params.append(category.strip())
        
    if is_ayurveda is not None:
        where_clauses.append("is_ayurveda = ?")
        params.append(1 if is_ayurveda else 0)
        
    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
    
    count_query = f"SELECT COUNT(*) FROM books {where_sql}"
    cursor.execute(count_query, params)
    total = cursor.fetchone()[0]
    
    fetch_query = f"""
    SELECT id, book_id, category, title_telugu, title_english, pages, size_mb, download_url, is_ayurveda, topics, source_pdf_page
    FROM books {where_sql}
    ORDER BY is_ayurveda DESC, id ASC
    LIMIT ? OFFSET ?
    """
    cursor.execute(fetch_query, params + [limit, offset])
    rows = cursor.fetchall()
    
    books = []
    for r in rows:
        topics = json.loads(r["topics"]) if r["topics"] else []
        books.append({
            "id": r["id"],
            "book_id": r["book_id"],
            "category": r["category"],
            "title_telugu": r["title_telugu"],
            "title_english": r["title_english"],
            "pages": r["pages"],
            "size_mb": r["size_mb"],
            "download_url": r["download_url"],
            "is_ayurveda": bool(r["is_ayurveda"]),
            "topics": topics,
            "source_pdf_page": r["source_pdf_page"]
        })
        
    conn.close()
    return {
        "books": books,
        "total": total,
        "limit": limit,
        "offset": offset
    }

def get_book_by_id(book_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, book_id, category, title_telugu, title_english, pages, size_mb, download_url, is_ayurveda, topics, source_pdf_page
    FROM books WHERE book_id = ? OR id = ? LIMIT 1
    """, (book_id, book_id))
    r = cursor.fetchone()
    conn.close()
    if not r:
        return None
    topics = json.loads(r["topics"]) if r["topics"] else []
    return {
        "id": r["id"],
        "book_id": r["book_id"],
        "category": r["category"],
        "title_telugu": r["title_telugu"],
        "title_english": r["title_english"],
        "pages": r["pages"],
        "size_mb": r["size_mb"],
        "download_url": r["download_url"],
        "is_ayurveda": bool(r["is_ayurveda"]),
        "topics": topics,
        "source_pdf_page": r["source_pdf_page"]
    }

def get_catalog_stats() -> Dict[str, Any]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), SUM(CASE WHEN is_ayurveda = 1 THEN 1 ELSE 0 END), COUNT(DISTINCT category), SUM(pages) FROM books")
    row = cursor.fetchone()
    total_books = row[0] or 0
    total_ayurveda = row[1] or 0
    total_categories = row[2] or 0
    total_pages = row[3] or 0
    
    cursor.execute("SELECT category, COUNT(*) as cnt FROM books GROUP BY category ORDER BY cnt DESC LIMIT 15")
    top_categories = [{"category": r[0], "count": r[1]} for r in cursor.fetchall()]
    
    conn.close()
    return {
        "total_books": total_books,
        "ayurveda_books": total_ayurveda,
        "total_categories": total_categories,
        "total_pages": total_pages,
        "top_categories": top_categories
    }

def get_categories() -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT category, COUNT(*) as cnt FROM books GROUP BY category ORDER BY cnt DESC")
    cats = [{"category": r[0], "count": r[1]} for r in cursor.fetchall()]
    conn.close()
    return cats

def ensure_catalog_populated():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM books")
    count = cursor.fetchone()[0]
    conn.close()
    
    if count == 0:
        catalog_path = os.path.join(os.path.dirname(__file__), "data", "books_catalog.json")
        if os.path.exists(catalog_path):
            with open(catalog_path, "r", encoding="utf-8") as f:
                books = json.load(f)
            from catalog_parser import populate_database_catalog
            populate_database_catalog(books, DB_PATH)

# Initialize database tables on import
init_db()
ensure_catalog_populated()
