import os
import json
import time
import logging
from typing import Optional, Dict, Any
from pinecone import Pinecone

logger = logging.getLogger("pinecone-helper")

def resolve_pinecone_api_key(provided_key: Optional[str] = None) -> str:
    """
    Resolves the Pinecone API key in priority order:
    1. Explicitly passed argument
    2. PINECONE_API_KEY environment variable
    3. Project .env or backend/.env file
    4. ~/.gemini/config/mcp_config.json
    """
    if provided_key and provided_key.strip():
        return provided_key.strip()
        
    env_key = os.getenv("PINECONE_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()
        
    # Check .env files
    env_locations = [
        os.path.join(os.path.dirname(__file__), ".env"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    ]
    for p in env_locations:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("PINECONE_API_KEY="):
                            val = line.split("=", 1)[1].strip()
                            if val:
                                return val
            except Exception:
                pass
                
    # Check MCP configuration
    mcp_config_path = os.path.expanduser("~/.gemini/config/mcp_config.json")
    if os.path.exists(mcp_config_path):
        try:
            with open(mcp_config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                pinecone_cfg = data.get("mcpServers", {}).get("pinecone-mcp-server", {})
                mcp_key = pinecone_cfg.get("env", {}).get("PINECONE_API_KEY")
                if mcp_key and mcp_key.strip():
                    return mcp_key.strip()
        except Exception:
            pass
            
    return ""

_pinecone_client_cache: Dict[str, Pinecone] = {}
_pinecone_index_cache: Dict[str, Any] = {}

def get_pinecone_client(api_key: Optional[str] = None) -> Pinecone:
    """Initialize and return a cached singleton Pinecone client."""
    resolved_key = resolve_pinecone_api_key(api_key)
    if not resolved_key:
        raise ValueError("PINECONE_API_KEY could not be resolved from environment or configuration.")
    if resolved_key not in _pinecone_client_cache:
        _pinecone_client_cache[resolved_key] = Pinecone(api_key=resolved_key)
    return _pinecone_client_cache[resolved_key]

def get_pinecone_index(api_key: Optional[str] = None, index_name: str = "ayurveda-index"):
    """Retrieve and cache Pinecone Index instance to reuse connection pools and prevent SSL leaks."""
    resolved_key = resolve_pinecone_api_key(api_key)
    cache_key = f"{resolved_key}:{index_name}"
    if cache_key not in _pinecone_index_cache:
        pc = get_pinecone_client(resolved_key)
        _pinecone_index_cache[cache_key] = pc.Index(index_name)
    return _pinecone_index_cache[cache_key]

def init_index(api_key: Optional[str] = None, index_name: str = "ayurveda-index", cloud: str = "aws", region: str = "us-east-1") -> bool:
    """Check if the index exists, and create it using integrated inference if not."""
    resolved_key = resolve_pinecone_api_key(api_key)
    pc = get_pinecone_client(resolved_key)
    
    if not pc.has_index(index_name):
        try:
            logger.info(f"Creating integrated inference index '{index_name}' on {cloud}:{region}...")
            pc.create_index_for_model(
                name=index_name,
                cloud=cloud,
                region=region,
                embed={
                    "model": "llama-text-embed-v2",
                    "field_map": {"text": "chunk_text"}
                }
            )
            while not pc.describe_index(index_name).status.ready:
                time.sleep(2)
            logger.info(f"Index '{index_name}' is ready.")
            return True
        except Exception as e:
            raise Exception(f"Failed to create integrated inference index: {str(e)}")
    return False

def get_index_stats(api_key: Optional[str] = None, index_name: str = "ayurveda-index") -> dict:
    """Retrieve statistics about the Pinecone index."""
    try:
        resolved_key = resolve_pinecone_api_key(api_key)
        if not resolved_key:
            return {"exists": False, "total_vector_count": 0, "namespaces": {}}
            
        cache_key = f"{resolved_key}:{index_name}"
        if cache_key not in _pinecone_index_cache:
            pc = get_pinecone_client(resolved_key)
            if not pc.has_index(index_name):
                return {"exists": False, "total_vector_count": 0, "namespaces": {}}
            
        index = get_pinecone_index(resolved_key, index_name)
        stats = index.describe_index_stats()
        
        total_vectors = getattr(stats, "total_vector_count", 0)
        if isinstance(stats, dict):
            total_vectors = stats.get("total_vector_count", 0) or stats.get("totalRecordCount", 0)
            ns_dict = stats.get("namespaces", {})
        else:
            ns_dict = getattr(stats, "namespaces", {}) or {}
            if hasattr(stats, "total_record_count"):
                total_vectors = stats.total_record_count
        
        namespaces_summary = {}
        if isinstance(ns_dict, dict):
            for ns, ns_obj in ns_dict.items():
                if isinstance(ns_obj, dict):
                    namespaces_summary[ns] = ns_obj.get("vector_count", 0) or ns_obj.get("record_count", 0)
                else:
                    namespaces_summary[ns] = getattr(ns_obj, "vector_count", 0) or getattr(ns_obj, "record_count", 0)
                    
        return {
            "exists": True,
            "total_vector_count": total_vectors,
            "namespaces": namespaces_summary
        }
    except Exception as e:
        logger.warning(f"Error fetching Pinecone index stats: {e}")
        return {"exists": False, "error": str(e), "total_vector_count": 0, "namespaces": {}}

def delete_pinecone_index(api_key: Optional[str] = None, index_name: str = "ayurveda-index") -> bool:
    """Delete a Pinecone index."""
    resolved_key = resolve_pinecone_api_key(api_key)
    pc = get_pinecone_client(resolved_key)
    cache_key = f"{resolved_key}:{index_name}"
    _pinecone_index_cache.pop(cache_key, None)
    if pc.has_index(index_name):
        pc.delete_index(index_name)
        return True
    return False

def upsert_chunks(api_key: Optional[str] = None, index_name: str = "ayurveda-index", chunks: list[dict] = None, namespace: str = "ayurveda") -> int:
    """
    Upsert document chunks to Pinecone integrated inference index.
    """
    if not chunks:
        return 0
    resolved_key = resolve_pinecone_api_key(api_key)
    index = get_pinecone_index(resolved_key, index_name)
    
    records = []
    for chunk in chunks:
        rec = {
            "_id": str(chunk["id"]),
            "chunk_text": chunk["text"],
            "source_book": chunk.get("source_book", "Ayurvedic Treatise"),
            "page_number": chunk.get("page_number", 0)
        }
        if "category" in chunk:
            rec["category"] = chunk["category"]
        if "download_url" in chunk:
            rec["download_url"] = chunk["download_url"]
        if "is_ayurveda" in chunk:
            rec["is_ayurveda"] = bool(chunk["is_ayurveda"])
        records.append(rec)
        
    batch_size = 96
    total_upserted = 0
    
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        res = index.upsert_records(namespace=namespace, records=batch)
        if hasattr(res, "record_count"):
            total_upserted += res.record_count
        elif isinstance(res, dict) and "record_count" in res:
            total_upserted += res["record_count"]
        else:
            total_upserted += len(batch)
        
    return total_upserted

def upsert_catalog_books(
    api_key: Optional[str] = None, 
    index_name: str = "ayurveda-index", 
    books: list[dict] = None, 
    namespace: str = "ayurveda",
    batch_size: int = 64,
    start_offset: int = 0,
    delay_between_batches: float = 2.0
) -> int:
    """
    Transform and upsert the 3500 FreeGurukul Telugu books catalog into Pinecone.
    Creates rich, semantically searchable representations embedded via llama-text-embed-v2.
    """
    if not books:
        return 0
        
    resolved_key = resolve_pinecone_api_key(api_key)
    index = get_pinecone_index(resolved_key, index_name)
    
    records = []
    for b in books:
        book_id = b.get("book_id", b.get("id", 0))
        unique_id = f"b_{book_id}_{b.get('id', 0)}"
        
        tel_title = (b.get("title_telugu") or "").strip()
        en_title = (b.get("title_english") or "").strip()
        cat = (b.get("category") or "General").strip()
        topics = b.get("topics") or []
        is_ayur = bool(b.get("is_ayurveda", False))
        pages = b.get("pages", 0)
        size_mb = b.get("size_mb", 0)
        url = (b.get("url") or "").strip()
        src_page = b.get("source_pdf_page", 0)
        
        topics_str = ", ".join(topics) if topics else "Scriptural Knowledge"
        classif = "Authentic Ayurveda, Medicine & Health Science" if is_ayur else "Classical Telugu Cultural Literature"
        
        # Dense, descriptive text representation optimized for semantic vector retrieval
        chunk_text = (
            f"Treatise: {tel_title} ({en_title})\n"
            f"Category: {cat}\n"
            f"Domain Classification: {classif}\n"
            f"Clinical & Botanical Topics: {topics_str}\n"
            f"Volume Details: {pages} Pages, File Size: {size_mb} MB\n"
            f"FreeGurukul Archive Reference: Catalog Entry #{book_id} (Catalog Page {src_page})\n"
            f"Direct Digital Reading URL: {url}\n"
            f"Summary: Official FreeGurukul Telugu archive #{book_id}. Title: {tel_title} ({en_title}). "
            f"Domain: {cat}. Preserved for clinical study, herbal medicine formulations, and heritage research."
        )
        
        records.append({
            "_id": unique_id,
            "chunk_text": chunk_text,
            "source_book": en_title or tel_title or f"Book #{book_id}",
            "page_number": src_page,
            "category": cat,
            "download_url": url,
            "is_ayurveda": is_ayur
        })
        
    logger.info(f"Prepared {len(records)} catalog records for upserting into Pinecone '{index_name}'...")
    total_upserted = 0
    
    for i in range(start_offset, len(records), batch_size):
        batch = records[i:i + batch_size]
        max_retries = 6
        for attempt in range(max_retries):
            try:
                res = index.upsert_records(namespace=namespace, records=batch)
                if hasattr(res, "record_count"):
                    total_upserted += res.record_count
                elif isinstance(res, dict) and "record_count" in res:
                    total_upserted += res["record_count"]
                else:
                    total_upserted += len(batch)
                
                logger.info(f"Upsert progress: {min(i + batch_size, len(records))}/{len(records)} records...")
                if delay_between_batches > 0:
                    time.sleep(delay_between_batches)
                break
            except Exception as e:
                err_str = str(e).lower()
                if "429" in err_str or "resource_exhausted" in err_str or "rate" in err_str:
                    wait_time = 15 * (attempt + 1)
                    logger.warning(f"Pinecone rate limit encountered on batch {i}-{i+len(batch)}. Backing off for {wait_time}s (attempt {attempt+1}/{max_retries})...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Error upserting batch {i} to {i + len(batch)}: {e}")
                    if attempt == max_retries - 1:
                        raise e
                    time.sleep(5)
            
    logger.info(f"Successfully upserted {total_upserted} records into Pinecone namespace '{namespace}'.")
    return total_upserted

def clear_namespace(api_key: Optional[str] = None, index_name: str = "ayurveda-index", namespace: str = "ayurveda") -> bool:
    """Clear all records from a Pinecone namespace."""
    try:
        resolved_key = resolve_pinecone_api_key(api_key)
        index = get_pinecone_index(resolved_key, index_name)
        index.delete(delete_all=True, namespace=namespace)
        logger.info(f"Cleared namespace '{namespace}' in Pinecone index '{index_name}'.")
        return True
    except Exception as e:
        logger.warning(f"Notice clearing namespace '{namespace}': {e}")
        return False

def search_index(
    api_key: Optional[str] = None, 
    index_name: str = "ayurveda-index", 
    query: str = "", 
    namespace: str = "ayurveda", 
    top_k: int = 25, 
    reranker_model: Optional[str] = "bge-reranker-v2-m3",
    top_n: int = 6,
    min_score: float = 0.0,
    filter: Optional[dict] = None
) -> list[dict]:
    """
    Search the integrated inference index semantically with optional metadata filtering and cross-encoder reranking.
    Returns rich metadata including category, download_url, is_ayurveda, and topics.
    """
    resolved_key = resolve_pinecone_api_key(api_key)
    cache_key = f"{resolved_key}:{index_name}"
    if cache_key not in _pinecone_index_cache:
        pc = get_pinecone_client(resolved_key)
        if not pc.has_index(index_name):
            raise ValueError(f"Index {index_name} does not exist.")
        
    index = get_pinecone_index(resolved_key, index_name)
    
    search_params = {
        "namespace": namespace,
        "top_k": top_k,
        "inputs": {"text": query}
    }
    
    if filter:
        search_params["filter"] = filter
        
    if reranker_model:
        search_params["rerank"] = {
            "model": reranker_model,
            "rank_fields": ["chunk_text"],
            "top_n": top_n
        }
        
    try:
        response = index.search(**search_params)
    except Exception as e:
        logger.warning(f"Reranker search failed or model unavailable ({e}). Retrying standard dense search...")
        search_params.pop("rerank", None)
        search_params["top_k"] = top_n
        response = index.search(**search_params)
    
    results = []
    hits = []
    if response:
        if hasattr(response, "result") and hasattr(response.result, "hits"):
            hits = response.result.hits
        elif isinstance(response, dict) and "result" in response and "hits" in response["result"]:
            hits = response["result"]["hits"]
        elif hasattr(response, "hits"):
            hits = response.hits
        elif isinstance(response, dict) and "hits" in response:
            hits = response["hits"]
            
    for hit in hits:
        hit_id = getattr(hit, "id", None) or (hit.get("_id") or hit.get("id") if isinstance(hit, dict) else "")
        hit_score = getattr(hit, "score", 0.0) or (hit.get("_score") or hit.get("score", 0.0) if isinstance(hit, dict) else 0.0)
        fields = getattr(hit, "fields", {}) or (hit.get("fields", {}) if isinstance(hit, dict) else {})
        
        score_val = float(hit_score) if hit_score is not None else 0.0
        if score_val < min_score:
            continue
            
        results.append({
            "id": str(hit_id),
            "score": score_val,
            "text": fields.get("chunk_text", ""),
            "source_book": fields.get("source_book", ""),
            "page_number": fields.get("page_number", 0),
            "category": fields.get("category", ""),
            "download_url": fields.get("download_url", ""),
            "is_ayurveda": bool(fields.get("is_ayurveda", False))
        })
            
    return results

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Pinecone Helper Module initialized.")
