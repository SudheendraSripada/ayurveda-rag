import sqlite3
import hashlib
import secrets
import json
import os
from typing import Optional, List, Dict, Any
from datetime import datetime

DB_PATH = os.getenv("AYURVEDA_DB_PATH", os.path.join(os.path.dirname(__file__), "ayurveda.db"))

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
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
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)
    
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
    
    conn.commit()
    conn.close()

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
    now = datetime.utcnow().isoformat()
    
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (id, email, password_hash, salt, full_name, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, email, pwd_hash, salt, full_name, now)
        )
        token = "tok_" + secrets.token_hex(24)
        cursor.execute("INSERT INTO auth_tokens (token, user_id, created_at) VALUES (?, ?, ?)", (token, user_id, now))
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
    now = datetime.utcnow().isoformat()
    cursor.execute("INSERT INTO auth_tokens (token, user_id, created_at) VALUES (?, ?, ?)", (token, user["id"], now))
    conn.commit()
    conn.close()
    
    return {"id": user["id"], "email": user["email"], "full_name": user["full_name"], "token": token}

def get_user_by_token(token: str) -> Optional[Dict[str, Any]]:
    if not token:
        return None
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT u.id, u.email, u.full_name, u.created_at
    FROM auth_tokens t
    JOIN users u ON t.user_id = u.id
    WHERE t.token = ?
    """, (token,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return {"id": user["id"], "email": user["email"], "full_name": user["full_name"]}
    return None

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
    now = datetime.utcnow().isoformat()
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
    now = datetime.utcnow().isoformat()
    
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
    cursor.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
    cursor.execute("DELETE FROM chat_sessions WHERE id = ? AND user_id = ?", (session_id, user_id))
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected

# Initialize database tables on import
init_db()
