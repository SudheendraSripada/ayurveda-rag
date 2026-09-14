"""
Automated Pipeline: Ingest the ~3500 FreeGurukul Telugu Books Catalog into Pinecone
Populates 'ayurveda-index' with rich semantic treatise embeddings for high-precision RAG.
"""

import os
import sys
import json
import logging
from dotenv import load_dotenv

from catalog_parser import parse_catalog_from_pdf, save_catalog_to_json, load_catalog_from_json, populate_database_catalog, CATALOG_JSON_PATH, DB_PATH
from pinecone_helper import resolve_pinecone_api_key, init_index, upsert_catalog_books, get_index_stats, clear_namespace

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ingest-catalog")

load_dotenv()

def run_ingest_pipeline(limit: int = None, offset: int = None, namespace: str = "ayurveda", index_name: str = "ayurveda-index", reset_namespace: bool = False) -> dict:
    """
    Main ingestion orchestrator:
    1. Ensures books are parsed from PDF and saved to JSON & SQLite.
    2. Resolves Pinecone credentials and index readiness.
    3. Transforms and upserts catalog records into Pinecone vector index with rate-limit resiliency.
    4. Validates final vector stats.
    """
    # 1. Check or generate catalog JSON
    if not os.path.exists(CATALOG_JSON_PATH):
        logger.info(f"Catalog JSON not found at {CATALOG_JSON_PATH}. Parsing from uploaded PDF...")
        books = parse_catalog_from_pdf()
        save_catalog_to_json(books, CATALOG_JSON_PATH)
        populate_database_catalog(books, DB_PATH)
    else:
        logger.info(f"Loading existing catalog from {CATALOG_JSON_PATH}...")
        books = load_catalog_from_json(CATALOG_JSON_PATH)

    logger.info(f"Loaded {len(books)} books from catalog.")
    populate_database_catalog(books, DB_PATH)

    # 2. Check Pinecone credentials
    api_key = resolve_pinecone_api_key()
    if not api_key:
        logger.error("PINECONE_API_KEY could not be found in environment, .env, or MCP config.")
        return {"success": False, "error": "Missing PINECONE_API_KEY"}

    # 3. Ensure index exists
    logger.info(f"Ensuring Pinecone index '{index_name}' is initialized...")
    init_index(api_key=api_key, index_name=index_name)

    if reset_namespace:
        logger.info(f"Resetting Pinecone namespace '{namespace}' prior to clean upsert...")
        clear_namespace(api_key=api_key, index_name=index_name, namespace=namespace)
        start_idx = 0
    else:
        # Check current vector count for auto-resume
        existing_stats = get_index_stats(api_key=api_key, index_name=index_name)
        existing_records = existing_stats.get("namespaces", {}).get(namespace, 0)
        start_idx = offset if offset is not None else (existing_records if existing_records < len(books) else 0)

    books_to_upsert = books[:limit] if limit else books
    
    logger.info(f"Beginning upsert of catalog records (start_offset={start_idx}, total={len(books_to_upsert)}) to Pinecone (namespace='{namespace}')...")
    
    upserted_count = upsert_catalog_books(
        api_key=api_key,
        index_name=index_name,
        books=books_to_upsert,
        namespace=namespace,
        batch_size=64,
        start_offset=start_idx,
        delay_between_batches=2.0
    )

    # 5. Fetch updated stats
    stats = get_index_stats(api_key=api_key, index_name=index_name)
    logger.info(f"Ingestion complete! Total upserted in this run: {upserted_count}. Pinecone stats: {stats}")

    return {
        "success": True,
        "total_catalog_books": len(books),
        "upserted_count": upserted_count,
        "pinecone_stats": stats
    }

if __name__ == "__main__":
    limit_val = None
    offset_val = None
    for arg in sys.argv[1:]:
        if arg.startswith("--limit="):
            limit_val = int(arg.split("=")[1])
        elif arg.startswith("--offset="):
            offset_val = int(arg.split("=")[1])
        elif arg.isdigit() and limit_val is None:
            limit_val = int(arg)
    result = run_ingest_pipeline(limit=limit_val, offset=offset_val)
    print("Ingestion Result:", json.dumps(result, indent=2))
