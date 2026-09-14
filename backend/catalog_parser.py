import os
import re
import json
import logging
import sqlite3
from typing import List, Dict, Any, Optional
from pypdf import PdfReader

logger = logging.getLogger("catalog-parser")

DEFAULT_PDF_PATH = "/home/codespace/.gemini/antigravity/brain/82daf026-db94-4963-872a-63247e685df5/.user_uploaded/media_1789351461017.pdf"
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CATALOG_JSON_PATH = os.path.join(DATA_DIR, "books_catalog.json")
DB_PATH = os.getenv("AYURVEDA_DB_PATH", os.path.join(os.path.dirname(__file__), "ayurveda.db"))

CATEGORY_VARIANTS = {
    "భక్తి యోగం": ["భక్తి యోగం", "భక్తు యోగెం", "భక్తి యోగము"],
    "కర్మ యోగం": ["కర్మ యోగం", "కర్మ యోగెం", "కరమ యోగిం", "కరమ యోగం"],
    "రాజ యోగం": ["రాజ యోగం", "రాజ్జ యోగెం", "రాజ యోగెం", "రాజ యోగిం"],
    "జ్ఞాన యోగం": ["జ్ఞాన యోగం", "జ్ఞాన యోగెం", "జ్ఞాన యోగిం"],
    "రామాయణం": ["రామాయణం", "రామాయణెం", "రామాయణిం"],
    "మహాభారతం": ["మహాభారతం", "మహాభార్తెం", "మహాభారతిం"],
    "భగవద్గీత": ["భగవద్గీత", "భగవ్ద్గగత", "భగవద్గీతలు"],
    "పురాణములు": ["పురాణములు", "పురాణాలు", "పురాణము"],
    "భాగవతము": ["భాగవతము", "భాగవ్తము", "భాగవతం"],
    "వేదములు": ["వేదములు", "వేద్ములు", "వేదాలు"],
    "ఉప వేదాలు": ["ఉప వేదాలు", "ఉప వేద్యలు"],
    "వేదాంగాలు": ["వేదాంగాలు", "వేదాెంగాలు", "వేద్యింగాలు"],
    "ఉప వేదాంగాలు": ["ఉప వేదాంగాలు", "ఉప వేదాెంగాలు", "ఉప వేద్యింగాలు"],
    "ఉపనిషత్తులు": ["ఉపనిషత్తులు", "ఉపన్నషత్తతలు", "ఉపనిషత్"],
    "గీతలు": ["గీతలు", "గ్లతలు"],
    "ధర్మము": ["ధర్మము", "ధరమము"],
    "కథలు": ["కథలు"],
    "శతకాలు": ["శతకాలు"],
    "సూక్తులు": ["సూక్తులు", "సూకుతలు"],
    "కావ్యాలు": ["కావ్యాలు", "కావాాలు"],
    "నాటకాలు": ["నాటకాలు", "నా కాలు"],
    "కీర్తనలు": ["కీర్తనలు", "కీరతనలు", "కీర్ునలు"],
    "గేయాలు": ["గేయాలు", "గ్వయాలు"],
    "దేవిదేవతలు": ["దేవిదేవతలు", "దేవిదేవ్తలు"],
    "గురువులు": ["గురువులు"],
    "భక్తులు": ["భక్తులు", "భకుతలు"],
    "కవులు": ["కవులు"],
    "జీవిత చరిత్ర": ["జీవిత చరిత్ర"],
    "మహిళలు": ["మహిళలు", "మహిళ్లు"],
    "పిల్లలు": ["పిల్లలు", "పిలేలు"],
    "చరిత్ర": ["చరిత్ర"],
    "విజ్ఞానము": ["విజ్ఞానము"],
    "వ్యక్తిత్వ వికాసం": ["వ్యక్తిత్వ వికాసం", "వ్ాకితతవ వికాస్ిం", "వాక్తుతవ వికాస్ిం", "వాక్తుతవ వికాసం", "వాక్తుతవ వికాస్ెం"],
    "సామాజిక అవగాహన": ["సామాజిక అవగాహన", "సామాజిక అవ్గాహన"]
}

HEADER_PATTERNS = [
    r"^No\s+Category", r"^\(MB\)", r"^Download$", r"^Link$", r"Go To Top", r"^Donate eBook",
    r"support@freegurukul\.org", r"Submit eBook", r"మీరు ఏదైనా పుస్తకిం", r"ఈ క్రింది లింక్స",
    r"ఉచిత గురుకుల విదా", r"Helpline/Whatsapp", r"Android ఆప్:", r"iOS ఆప్:", r"Website:",
    r"వీడియో ప్రవ్చనాలు", r"ఆడియో ప్రవ్చనాలు", r"మైిండ్ మేనేజ్", r"ఇింపాక్స్", r"ఇవి కావ్యలింటే",
    r"మొబైల్ అప్", r"ననుి నేను తెలుసుకవటెం", r"భార్ా భర్ు అన్యానాెంగా", r"^\d+\)\s+"
]

CATEGORY_LOOKUP = []
for canon, variants in CATEGORY_VARIANTS.items():
    for v in variants:
        CATEGORY_LOOKUP.append((v, canon))
CATEGORY_LOOKUP.sort(key=lambda x: -len(x[0]))

TOPIC_MAPPINGS = {
    "digestion_agni": ["జీర్ణం", "అజీర్ణం", "కడుపు", "Jeernam", "ఆహార", "Aahara", "Anna", "Agni", "Ama", "గ్యాస్", "కడుపుబ్బరం", "మంట"],
    "fevers_jwara": ["జ్వరం", "జ్జవరాలు", "చలిజ్వరం", "Jwaralu", "తాపం", "Pitta", "Sudarshana"],
    "diabetes_prameha": ["మధుమేహం", "డయాబెటీస్", "రక్తపోటు", "Madhumeham", "Daibeties", "Sugar", "Prameha"],
    "respiratory_kasa": ["ఊపిరితిత్తులు", "దగ్గు", "ఆయాసం", "పడిశం", "కఫం", "UpiriTittulu", "Kasa", "Swasa", "Kapha", "Asthama", "ఉబ్బసం", "జలుబు"],
    "joints_sandhivata": ["కీళ్లు", "కీలునొప్పులు", "కండరాలు", "వాతం", "సంధివాతం", "Keellu", "Sandhivata", "Vata", "నొప్పులు"],
    "cardiovascular_hridaya": ["గుండె", "హృదయం", "రక్తపోటు", "Gunde", "Hrudayam", "Heart"],
    "kidney_ashmari": ["మూత్రపిండాలు", "మూత్ర", "Mootrapindam", "Ashmari", "Mutrakrichra"],
    "herbs_vanamulika": ["వనమూలిక", "వనమూలికా", "ఔషధ", "మొక్కలు", "మూలికలు", "తులసి", "పసుపు", "అశ్వగంధ", "Vanamulika", "Oshadulu", "Mokkala", "Tulasi", "Gruhoushada"],
    "kitchen_remedies": ["వంట ఇల్లు", "వంటిల్లు", "గృహ వైద్యం", "పోపుల పెట్టె", "VantileVaidhyasala", "GruhaVaidyam", "చిట్కా వైద్యం", "ChitkaVaidyam"],
    "nature_cure": ["ప్రకృతి వైద్యం", "నీటి చికిత్స", "సహజ వైద్యం", "Prakruthi", "Upavasa", "ఉపవాస", "సూర్యకిరణ"],
    "classical_samhita": ["చరక సంహిత", "చర్క స్ెంహిత", "అష్టాంగ హృదయము", "అష్ణసెంగ హృద్యము", "కాశ్యప సంహిత", "కాశాప స్ెంహిత", "సుశ్రుత", "Charaka", "Ashtanga", "Sushruta", "Kasyapa", "SahasraYoga"]
}

def extract_topics(text: str) -> List[str]:
    """Tag book with relevant clinical, botanical, or philosophical topics."""
    text_lower = text.lower()
    matched = []
    for topic, kws in TOPIC_MAPPINGS.items():
        for kw in kws:
            if kw.lower() in text_lower:
                matched.append(topic)
                break
    return matched

def is_ayurveda_treatise(cat: str, tel_title: str, en_title: str, book_id: int) -> bool:
    """
    Accurately identifies authentic Ayurveda, traditional medicine, and health treatises.
    Prevents false positives from Arthashastra, Gandharvaveda, dance, literature, etc.
    """
    en_lower = en_title.lower()
    
    non_ayur_exclusions_en = [
        "arthasastra", "ardhasastram", "chanakya", "kowtilya", "dhanurveda", 
        "gandharva", "sangeetha", "sangeeta", "natya", "nrutya", "nrutta", 
        "chitra", "shilpa", "sculpture", "painting", "journalis", "magic", 
        "chess", "drama", "katha", "hasya", "vyasa", "sampradaya", "abhinaya",
        "brahmasutra", "nyaya", "mimamsa", "tarka", "vaisheshika", "rachanalu",
        "appulu", "sabhalu", "nirvahana", "avadhana", "lekhaa"
    ]
    non_ayur_exclusions_tel = [
        "అర్థశాస్త్ర", "అర్ధ శాస్త్ర", "అర్ాశాస్త్ర", "చాణక్య", "చాణక్త", "కౌటిల",
        "గాంధర్వ", "గాెంధర్వ", "సంగీత", "స్ెంగ్లత", "నాట్య", "నాటా", "నృత్య", "నృతా",
        "నృత్త", "నృతు", "శిల్ప", "శిల్ు", "చిత్ర కళ", "మేధ మాజిక్", "మేధ మాాజిక్",
        "జర్నలిస్ట్", "జ్జర్ిలస్ట్", "బ్రహ్మ సూత్ర", "బ్రహమ సూత్ర", "మీమాంస", "మీమాెంస",
        "న్యాయ", "నాాయ", "వైశేషిక", "వైశేష్టక", "హాస్య", "హాస్", "శృంగార", "శృెంగార్",
        "రసభావ", "ర్స్భావ", "వివాహ", "పెళ్లి", "పళిల", "రచనలు", "సభలు", "అప్పులు"
    ]
    
    if any(re.search(r"\b" + ex + r"\b", en_lower) or ex in en_lower for ex in non_ayur_exclusions_en):
        return False
    if any(ex in tel_title for ex in non_ayur_exclusions_tel):
        return False
        
    # FreeGurukul Upa Vedalu health section
    if cat == "ఉప వేదాలు" and 1328 <= book_id <= 1434:
        return True
        
    ayur_explicit_kws_tel = [
        "ఆయుర్వేద", "ఆయుర్వవద్", "వైద్య", "వైద్ా", "చికిత్స", "చిక్తతస", 
        "వనమూలిక", "ఔషధ", "ఓషదు", "చర్క", "చరక", "అష్టాంగ", "అష్ణసెంగ", 
        "కాశ్యప", "కాశాప", "సుశ్రుత", "హోమియో", "ప్రకృతి వైద్య", 
        "రోగము", "రోగాలు", "వ్యాధి", "వాాధి", "వాాదులు", "జ్వర", "జ్జవర", 
        "ఆరోగ్య", "ఆరోగా", "పథ్య", "పథా", "అనుపాన", "నిఘంటు", 
        "వృక్షశాస్త్ర", "మధుమేహ", "రక్తపోటు"
    ]
    ayur_explicit_kws_en = [
        r"\bayurved", r"\bvaidya", r"\bchikitsa", r"\bcharaka\b", r"\bashtanga\b", 
        r"\bkasyapa\b", r"\bsushruta\b", r"\bhealth\b", r"\bmedicine\b", 
        r"\bvanamulika\b", r"\bjwar", r"\baahar", r"\bpathya\b", r"\banupana\b",
        r"\bherb", r"\bhomeopathy\b", r"\bhomiyo", r"\bdoctor\b", r"\bhospital\b",
        r"\bdisease\b", r"\bdiabetes\b", r"\bdaibeties\b", r"\bswadesi\b"
    ]
    
    if any(k in tel_title for k in ayur_explicit_kws_tel):
        return True
    if any(re.search(p, en_lower) for p in ayur_explicit_kws_en):
        return True
        
    return False

def parse_catalog_from_pdf(pdf_path: str = DEFAULT_PDF_PATH) -> List[Dict[str, Any]]:
    """
    Parse the FreeGurukul Telugu books catalog PDF (pages 4 to 103) into structured entries.
    Employs robust multiline row accumulation ending at 'Download' to eliminate wrapped-line fragmentation.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found at {pdf_path}")
        
    reader = PdfReader(pdf_path)
    logger.info(f"Loaded PDF with {len(reader.pages)} pages from {pdf_path}.")
    
    books = []
    
    for p_idx in range(3, min(103, len(reader.pages))):
        page = reader.pages[p_idx]
        annots = page.get('/Annots') or []
        
        drive_links = []
        for a in annots:
            obj = a.get_object()
            act = obj.get('/A')
            uri = act.get('/URI') if act else None
            if uri and "drive.google.com" in str(uri):
                rect = [float(x) for x in obj.get('/Rect', [0, 0, 0, 0])]
                drive_links.append({'y': rect[1], 'uri': str(uri).strip()})
        # Order top to bottom
        drive_links.sort(key=lambda x: -x['y'])
        link_urls = [l['uri'] for l in drive_links]
        
        txt = page.extract_text() or ''
        lines = [l.strip() for l in txt.split('\n') if l.strip()]
        clean_lines = [l for l in lines if not any(re.search(p, l) for p in HEADER_PATTERNS)]
        
        entries = []
        curr = []
        for l in clean_lines:
            curr.append(l)
            if re.search(r"Download\s*$", l, re.IGNORECASE):
                combined = " ".join(curr)
                # Strip any preceding section header text before the leading digits
                combined = re.sub(r"^[^\d]+(?=\d+\s+)", "", combined)
                if re.match(r"^\d+\s+", combined):
                    entries.append(combined)
                curr = []
                
        for i, e in enumerate(entries):
            m_start = re.match(r"^(\d+)\s+(.*)$", e)
            if not m_start:
                continue
                
            book_id = int(m_start.group(1))
            rem = m_start.group(2).strip()
            
            cat = "ఇతరాలు"
            for v, canon in CATEGORY_LOOKUP:
                if rem.startswith(v):
                    cat = canon
                    rem = rem[len(v):].strip()
                    break
                    
            url = link_urls[i] if i < len(link_urls) else ""
            
            m_end = re.search(r"(?:([A-Za-z0-9_\-\.]+)\s+)?(\d+)\s+(\d+)\s+Download.*$", rem, re.IGNORECASE)
            if m_end:
                en_title = (m_end.group(1) or "").strip()
                pages = int(m_end.group(2))
                size_mb = int(m_end.group(3))
                tel_title = rem[:m_end.start()].strip()
            else:
                en_title = ""
                pages = 0
                size_mb = 0
                tel_title = rem
                
            tel_title = tel_title or en_title or f"Book {book_id}"
            combined_txt = f"{cat} {tel_title} {en_title}"
            topics = extract_topics(combined_txt)
            is_ayur = is_ayurveda_treatise(cat, tel_title, en_title, book_id)
            
            books.append({
                'id': len(books) + 1,
                'book_id': book_id,
                'category': cat,
                'title_telugu': tel_title,
                'title_english': en_title,
                'pages': pages,
                'size_mb': size_mb,
                'url': url,
                'is_ayurveda': is_ayur,
                'topics': topics,
                'source_pdf_page': p_idx + 1
            })
            
    logger.info(f"Extracted {len(books)} clean books ({sum(1 for b in books if b['is_ayurveda'])} Ayurveda treatises).")
    return books

def save_catalog_to_json(books: List[Dict[str, Any]], output_path: str = CATALOG_JSON_PATH):
    """Save parsed books catalog to JSON."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(books, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved {len(books)} books to {output_path}")

def load_catalog_from_json(path: str = CATALOG_JSON_PATH) -> List[Dict[str, Any]]:
    """Load cached books catalog from JSON."""
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def populate_database_catalog(books: List[Dict[str, Any]], db_path: str = DB_PATH):
    """Store all 3400+ books in SQLite database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS books;")
    cursor.execute("""
    CREATE TABLE books (
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
    
    for b in books:
        cursor.execute("""
        INSERT INTO books (
            id, book_id, category, title_telugu, title_english, pages, size_mb, 
            download_url, is_ayurveda, topics, source_pdf_page
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            b['id'],
            b['book_id'],
            b['category'],
            b['title_telugu'],
            b['title_english'],
            b['pages'],
            b['size_mb'],
            b['url'],
            1 if b['is_ayurveda'] else 0,
            json.dumps(b.get('topics', [])),
            b.get('source_pdf_page', 0)
        ))
        
    conn.commit()
    conn.close()
    logger.info(f"Successfully populated {len(books)} books in SQLite DB: {db_path}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    books = parse_catalog_from_pdf()
    save_catalog_to_json(books)
    populate_database_catalog(books)
    print(f"Catalog parsing complete: {len(books)} books.")
