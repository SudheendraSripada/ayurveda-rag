import os
import re
import time
import urllib.request
import logging
from dotenv import load_dotenv
from pdf_parser import parse_pdf
from pinecone_helper import init_index, upsert_chunks

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ingest-books")

load_dotenv()

# Complete list of 31 authentic Telugu and classical Sanskrit Ayurveda reference books
BOOKS_LIST = [
    {"id": 1, "title": "అందరికి ఆయుర్వేదం-స్వదేశీ వనములికా వేదం", "url": "https://pdf.freegurukul.org/s/1406"},
    {"id": 2, "title": "అందరికి ఆయుర్వేదం-స్వదేశీ ఆహార వేదం", "url": "https://pdf.freegurukul.org/s/1407"},
    {"id": 3, "title": "అందరికి ఆయుర్వేదం-స్వదేశీ సౌందర్య వేదం", "url": "https://pdf.freegurukul.org/s/1408"},
    {"id": 4, "title": "అందరికి ఆయుర్వేదం-ఆయుర్వేద జీవన వేదం", "url": "https://pdf.freegurukul.org/s/1409"},
    {"id": 5, "title": "అందరికి ఆయుర్వేదం-సంవత్సర సంచిక-1", "url": "https://pdf.freegurukul.org/s/1410"},
    {"id": 6, "title": "అందరికి ఆయుర్వేదం-సంవత్సర సంచిక-2", "url": "https://pdf.freegurukul.org/s/1411"},
    {"id": 7, "title": "అందరికి ఆయుర్వేదం-సంవత్సర సంచిక-3", "url": "https://pdf.freegurukul.org/s/1412"},
    {"id": 8, "title": "గృహ వైద్యం-4", "url": "https://pdf.freegurukul.org/s/1414"},
    {"id": 9, "title": "వ్యాసప్రోక్త వైద్య శాస్త్రము", "url": "https://pdf.freegurukul.org/s/1415"},
    {"id": 10, "title": "మన్కి మిన్కి-ఆయుర్వేదం", "url": "https://pdf.freegurukul.org/s/1418"},
    {"id": 11, "title": "ఆయుర్వేదం ఆధునిక శాస్త్రీయ వికాసము", "url": "https://pdf.freegurukul.org/s/1419"},
    {"id": 12, "title": "చరక సంహిత-విమాన స్థానము", "url": "https://pdf.freegurukul.org/s/1420"},
    {"id": 13, "title": "చరక సంహిత-శారీర స్థానము", "url": "https://pdf.freegurukul.org/s/1421"},
    {"id": 14, "title": "చరక సంహిత-కల్ప స్థానము", "url": "https://pdf.freegurukul.org/s/1422"},
    {"id": 15, "title": "చరక సంహిత-చికిత్సా స్థానము", "url": "https://pdf.freegurukul.org/s/1423"},
    {"id": 16, "title": "అష్టాంగ హృదయము-సూత్ర స్థానము", "url": "https://pdf.freegurukul.org/s/1425"},
    {"id": 17, "title": "అష్టాంగ హృదయము-ఉత్తర స్థానము", "url": "https://pdf.freegurukul.org/s/1426"},
    {"id": 18, "title": "అష్టాంగ హృదయము-చికిత్స,కల్ప స్థానము", "url": "https://pdf.freegurukul.org/s/1427"},
    {"id": 19, "title": "అందరికి ఆయుర్వేదం-2008", "url": "https://pdf.freegurukul.org/s/3391"},
    {"id": 20, "title": "అందరికి ఆయుర్వేదం-2009", "url": "https://pdf.freegurukul.org/s/3392"},
    {"id": 21, "title": "అందరికి ఆయుర్వేదం-2010", "url": "https://pdf.freegurukul.org/s/3393"},
    {"id": 22, "title": "అందరికి ఆయుర్వేదం-2011", "url": "https://pdf.freegurukul.org/s/3394"},
    {"id": 23, "title": "అందరికి ఆయుర్వేదం-2012", "url": "https://pdf.freegurukul.org/s/3395"},
    {"id": 24, "title": "అందరికి ఆయుర్వేదం-2013", "url": "https://pdf.freegurukul.org/s/3396"},
    {"id": 25, "title": "అందరికి ఆయుర్వేదం-2014", "url": "https://pdf.freegurukul.org/s/3397"},
    {"id": 26, "title": "అందరికి ఆయుర్వేదం-2015", "url": "https://pdf.freegurukul.org/s/3398"},
    {"id": 27, "title": "వంట ఇల్లే వైద్యశాల", "url": "https://pdf.freegurukul.org/s/1394"},
    {"id": 28, "title": "ప్రకృతి వైద్యం", "url": "https://pdf.freegurukul.org/s/1390"},
    {"id": 29, "title": "ప్రకృతి వైద్య తత్త్వము", "url": "https://pdf.freegurukul.org/s/1392"},
    {"id": 30, "title": "ప్రకృతి గృహ వైద్యం", "url": "https://pdf.freegurukul.org/s/1393"},
    {"id": 31, "title": "గృహౌషద వనము", "url": "https://pdf.freegurukul.org/s/1396"}
]

DOWNLOAD_DIR = "downloaded_books"

def download_pdf(url: str, output_path: str) -> bool:
    """Download PDF file with User-Agent header and increased timeout for large volumes."""
    try:
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=120) as response, open(output_path, "wb") as out_file:
            out_file.write(response.read())
        return True
    except Exception as e:
        logger.error(f"Failed to download {url}: {str(e)}")
        return False

def ingest_all_books(limit: int = None, include_catalog: bool = True):
    """Download, parse, and ingest books to Pinecone."""
    from pinecone_helper import resolve_pinecone_api_key
    pinecone_key = resolve_pinecone_api_key()
    index_name = os.getenv("PINECONE_INDEX_NAME", "ayurveda-index")
    
    if not pinecone_key:
        logger.error("PINECONE_API_KEY is not set in environment, .env, or MCP config!")
        return
        
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    logger.info(f"Initializing Pinecone index '{index_name}'...")
    init_index(api_key=pinecone_key, index_name=index_name)
    
    if include_catalog:
        try:
            from ingest_catalog import run_ingest_pipeline
            logger.info("Triggering 3500 books catalog ingestion into Pinecone...")
            run_ingest_pipeline(limit=limit, namespace="ayurveda", index_name=index_name)
        except Exception as e:
            logger.warning(f"Catalog ingestion notice: {e}")
            
    books_to_process = BOOKS_LIST[:limit] if limit else BOOKS_LIST
    logger.info(f"Starting treatise text ingestion for {len(books_to_process)} reference books...")
    
    total_books_indexed = 0
    total_chunks_indexed = 0
    
    for book in books_to_process:
        book_id = book["id"]
        book_title = book["title"]
        url = book["url"]
        
        filename = f"book_{book_id}_{re.sub(r'[^a-zA-Z0-9]', '_', book_title)}.pdf"
        file_path = os.path.join(DOWNLOAD_DIR, filename)
        
        logger.info(f"[{book_id}/{len(books_to_process)}] Processing: {book_title}...")
        
        if not os.path.exists(file_path):
            logger.info(f"Downloading from {url}...")
            if not download_pdf(url, file_path):
                logger.warning(f"Skipping {book_title} due to download failure.")
                continue
                
        try:
            logger.info(f"Extracting & chunking {filename}...")
            chunks = parse_pdf(file_path, chunk_size=800, overlap=150)
            
            for c in chunks:
                c["source_book"] = book_title
                c["is_ayurveda"] = True
                
            logger.info(f"Generated {len(chunks)} text chunks for '{book_title}'. Upserting to Pinecone...")
            upserted = upsert_chunks(api_key=pinecone_key, index_name=index_name, chunks=chunks, namespace="ayurveda")
            
            total_books_indexed += 1
            total_chunks_indexed += upserted
            logger.info(f"Successfully indexed {upserted} chunks for '{book_title}'.")
        except Exception as e:
            logger.error(f"Failed to process '{book_title}': {str(e)}")
            
    logger.info(f"Ingestion completed! Total Books: {total_books_indexed}, Total Chunks: {total_chunks_indexed}")

if __name__ == "__main__":
    import sys
    limit_count = None
    catalog_flag = True
    for arg in sys.argv[1:]:
        if arg.isdigit():
            limit_count = int(arg)
        elif arg == "--no-catalog":
            catalog_flag = False
    ingest_all_books(limit=limit_count, include_catalog=catalog_flag)
