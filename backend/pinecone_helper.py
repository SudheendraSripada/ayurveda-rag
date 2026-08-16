import time
from pinecone import Pinecone

def get_pinecone_client(api_key: str) -> Pinecone:
    """Initialize and return a Pinecone client."""
    return Pinecone(api_key=api_key)

def init_index(api_key: str, index_name: str, cloud: str = "aws", region: str = "us-east-1") -> bool:
    """Check if the index exists, and create it using integrated inference if not."""
    pc = get_pinecone_client(api_key)
    
    if not pc.has_index(index_name):
        try:
            pc.create_index_for_model(
                name=index_name,
                cloud=cloud,
                region=region,
                embed={
                    "model": "llama-text-embed-v2",
                    "field_map": {"text": "chunk_text"}
                }
            )
            # Wait until index is ready
            while not pc.describe_index(index_name).status.ready:
                time.sleep(2)
            return True
        except Exception as e:
            raise Exception(f"Failed to create integrated inference index: {str(e)}")
    return False

def get_index_stats(api_key: str, index_name: str) -> dict:
    """Retrieve statistics about the Pinecone index."""
    pc = get_pinecone_client(api_key)
    if not pc.has_index(index_name):
        return {"exists": False, "total_vector_count": 0, "namespaces": {}}
        
    index = pc.Index(index_name)
    stats = index.describe_index_stats()
    
    total_vectors = getattr(stats, "total_vector_count", 0)
    if isinstance(stats, dict):
        total_vectors = stats.get("total_vector_count", 0)
        ns_dict = stats.get("namespaces", {})
    else:
        ns_dict = getattr(stats, "namespaces", {}) or {}
    
    namespaces_summary = {}
    if isinstance(ns_dict, dict):
        for ns, ns_obj in ns_dict.items():
            if isinstance(ns_obj, dict):
                namespaces_summary[ns] = ns_obj.get("vector_count", 0)
            else:
                namespaces_summary[ns] = getattr(ns_obj, "vector_count", 0)
                
    return {
        "exists": True,
        "total_vector_count": total_vectors,
        "namespaces": namespaces_summary
    }

def delete_pinecone_index(api_key: str, index_name: str) -> bool:
    """Delete a Pinecone index."""
    pc = get_pinecone_client(api_key)
    if pc.has_index(index_name):
        pc.delete_index(index_name)
        return True
    return False

def upsert_chunks(api_key: str, index_name: str, chunks: list[dict], namespace: str) -> int:
    """
    Upsert document chunks to Pinecone.
    Each chunk in `chunks` should be:
    {
        "id": "unique_id",
        "text": "text content",
        "source_book": "book_name.pdf",
        "page_number": 12
    }
    """
    pc = get_pinecone_client(api_key)
    index = pc.Index(index_name)
    
    # Map to Pinecone integrated inference expected format
    records = []
    for chunk in chunks:
        records.append({
            "_id": chunk["id"],
            "chunk_text": chunk["text"],
            "source_book": chunk["source_book"],
            "page_number": chunk["page_number"]
        })
        
    # Batch records in chunks of 100 for reliable upserts
    batch_size = 100
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

def search_index(
    api_key: str, 
    index_name: str, 
    query: str, 
    namespace: str, 
    top_k: int = 15, 
    reranker_model: str = None,
    top_n: int = 5
) -> list[dict]:
    """Search the integrated inference index semantically."""
    pc = get_pinecone_client(api_key)
    if not pc.has_index(index_name):
        raise ValueError(f"Index {index_name} does not exist.")
        
    index = pc.Index(index_name)
    
    search_params = {
        "namespace": namespace,
        "top_k": top_k,
        "inputs": {"text": query}
    }
    
    # Use Pinecone's serverless reranking if model is specified
    if reranker_model:
        search_params["rerank"] = {
            "model": reranker_model,
            "rank_fields": ["chunk_text"],
            "top_n": top_n
        }
        
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
        
        results.append({
            "id": hit_id,
            "score": float(hit_score) if hit_score else 0.0,
            "text": fields.get("chunk_text", ""),
            "source_book": fields.get("source_book", ""),
            "page_number": fields.get("page_number", 0)
        })
            
    return results

if __name__ == "__main__":
    print("Pinecone Helper module initialized successfully.")
