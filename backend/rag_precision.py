"""
Ayurvedic Clinical Knowledge Base & RAG Precision Engine
Enhances retrieval precision via Ayurvedic entity extraction, bilingual query expansion,
hybrid candidate scoring, and scriptural treatise linking.
"""

import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger("rag-precision")

# Comprehensive Ayurvedic Clinical & Botanical Knowledge Base
AYURVEDIC_KNOWLEDGE_BASE = {
    "digestion_acidity": {
        "symptoms": ["digestion", "digestive", "acidity", "acid reflux", "gerd", "heartburn", "burning sensation", "indigestion", "bloating", "gas", "belching", "gastritis", "ulcer", "stomach burn"],
        "telugu_terms": ["ఆమ్లపిత్తం", "కడుపులో మంట", "అజీర్ణం", "గ్యాస్", "కడుపుబ్బరం", "తేన్పులు", "జీర్ణశక్తి", "మంట"],
        "sanskrit_terms": ["Amlapitta", "Agnimandya", "Vidagdha Jirna", "Adhmana", "Pitta Shamana"],
        "dosha": "Pitta aggravating Agni (Vidagdhajeerna / Amlapitta)",
        "classical_texts": ["Charaka Samhita Chikitsasthana", "Ashtanga Hridaya Sutrasthana", "Swadesi Ahara Veda", "Vantile Vaidhyasala"],
        "key_herbs": ["Shatavari", "Yashtimadhu (Licorice)", "Amalaki (Amla)", "Dhanyaka (Coriander)", "Jeeraka (Cumin)", "Ghee", "Cow Milk"]
    },
    "fevers_infections": {
        "symptoms": ["fever", "fevers", "high temperature", "chills", "body ache", "viral fever", "flu", "dengue", "malaria", "typhoid", "shivering"],
        "telugu_terms": ["జ్వరం", "జ్జవరాలు", "చలిజ్వరం", "తాపం", "ఒంటి నొప్పులు"],
        "sanskrit_terms": ["Jwara", "Santapa", "Vata-Pitta Jwara", "Taruna Jwara", "Langhana"],
        "dosha": "Pitta-Vata imbalance causing Ama blockage of Rasavaha Srotas",
        "classical_texts": ["Charaka Samhita Jwara Chikitsa", "Ashtanga Hridaya", "Gruha Vaidyam"],
        "key_herbs": ["Guduchi (Amrutha/Tinospora)", "Sudarshana Churna", "Tulsi", "Shunti (Dry Ginger)", "Maricha (Black Pepper)", "Musta"]
    },
    "respiratory_cough": {
        "symptoms": ["cough", "coughs", "coughing", "cold", "dry cough", "wet cough", "phlegm", "mucus", "asthma", "wheezing", "bronchitis", "throat irritation", "sinusitis", "congestion", "breathlessness"],
        "telugu_terms": ["దగ్గు", "పడిశం", "ఆయాసం", "ఊపిరితిత్తులు", "కఫం", "శ్వాస", "గొంతు నొప్పి", "జలుబు", "ఉబ్బసం"],
        "sanskrit_terms": ["Kasa", "Swasa", "Pratishyaya", "Kapha Rogam", "Tamaka Swasa"],
        "dosha": "Kapha-Vata obstruction in Pranavaha Srotas",
        "classical_texts": ["Charaka Samhita Kasa Chikitsa", "Ashtanga Hridaya", "Vanamulika Veda"],
        "key_herbs": ["Vasa (Adhatoda)", "Kantakari", "Tulsi", "Trikatu (Shunti, Maricha, Pippali)", "Yashtimadhu", "Talisadi Churna", "Sitopaladi Churna"]
    },
    "joints_arthritis": {
        "symptoms": ["joint", "joints", "joint pain", "knee pain", "arthritis", "osteoarthritis", "rheumatoid", "back pain", "sciatica", "stiffness", "joint swelling", "uric acid", "gout", "knee stiffness"],
        "telugu_terms": ["కీళ్ల నొప్పులు", "మోకాళ్ల నొప్పులు", "వాతం", "సంధివాతం", "నడుము నొప్పి", "కీలు వాపు"],
        "sanskrit_terms": ["Sandhivata", "Amavata", "Vatarakta", "Kati Shoola", "Gridhrasi"],
        "dosha": "Aggravated Vata in Asthi and Majja Dhatus / Ama deposition",
        "classical_texts": ["Charaka Samhita Vatavyadhi Chikitsa", "Sushruta Samhita", "Vanamulika Veda", "Ashtanga Hridaya"],
        "key_herbs": ["Shallaki (Boswellia)", "Guggulu (Yogaraja / Kaishore)", "Ashwagandha", "Nirgundi", "Rasna", "Bala", "Mahanarayana Taila"]
    },
    "edema_swelling": {
        "symptoms": ["fluid retention", "water retention", "swelling", "edema", "dropsy", "puffiness", "bloated feet"],
        "telugu_terms": ["వాపు", "శోఫ", "నీరు పట్టడం", "శరీర వాపు"],
        "sanskrit_terms": ["Shotha", "Shopha", "Kaphaja Shotha", "Vataja Shopha"],
        "dosha": "Kapha-Vata obstruction in Udakavaha Srotas",
        "classical_texts": ["Charaka Samhita Shotha Chikitsa", "Ashtanga Hridaya", "Gruhoushada Vanamu"],
        "key_herbs": ["Punarnava (Boerhavia Diffusa)", "Gokshura", "Dashamoola", "Varuna", "Kulatta"]
    },
    "headache_migraine": {
        "symptoms": ["headache", "migraine", "head pain", "cluster headache", "temple pain", "throbbing head"],
        "telugu_terms": ["తలనెప్పి", "తల నొప్పి", "పార్శ్వపు నొప్పి", "శిరో వేదన"],
        "sanskrit_terms": ["Shirashoola", "Ardhavabhedaka", "Suryavarta", "Vataja Shirashoola"],
        "dosha": "Vata-Pitta vitiation in Uttamanga (head)",
        "classical_texts": ["Charaka Samhita Siddhisthana", "Ashtanga Hridaya", "Vanamulika Veda"],
        "key_herbs": ["Pathyadi Kwatha", "Brahmi", "Shankhapushpi", "Nasya with Anu Taila", "Chandanadi Lepa"]
    },
    "diabetes_metabolism": {
        "symptoms": ["diabetes", "sugar", "frequent urination", "high blood sugar", "fatigue", "excessive thirst", "weight loss"],
        "telugu_terms": ["మధుమేహం", "చక్కెర వ్యాధి", "డయాబెటీస్", "అధిక మూత్రం"],
        "sanskrit_terms": ["Prameha", "Madhumeha", "Medo Dhatu Dushti", "Kapha-Vata Prameha"],
        "dosha": "Kaphaja Prameha progressing to Vataja Madhumeha with Medas impairment",
        "classical_texts": ["Charaka Samhita Prameha Chikitsa", "Sushruta Samhita", "Swadesi Ahara Veda"],
        "key_herbs": ["Meshashringi (Gymnema Sylvestre)", "Vijaysar", "Haridra (Turmeric)", "Amalaki", "Jambu (Jamun seed)", "Karela (Bitter Gourd)", "Nisha Amalaki"]
    },
    "skin_allergies": {
        "symptoms": ["skin allergy", "itching", "skin rash", "eczema", "psoriasis", "hives", "allergy", "pimples", "acne", "fungal infection", "ringworm", "dry skin"],
        "telugu_terms": ["చర్మ వ్యాధులు", "గజ్జి", "దురద", "తామర", "మొటిమలు", "కుష్ఠు"],
        "sanskrit_terms": ["Kushta", "Kandu", "Sheetapitta", "Mukhadushika", "Raktapitta"],
        "dosha": "Pitta and Rakta Dhatu vitiation with Kapha association",
        "classical_texts": ["Charaka Samhita Kushta Chikitsa", "Sushruta Samhita", "Swadesi Soundarya Veda", "Vanamulika Veda"],
        "key_herbs": ["Neem (Nimba)", "Manjistha", "Khadira", "Haridra", "Bakuchi", "Aloe Vera (Kumari)", "Gandhaka Rasayana"]
    },
    "cardiovascular_hypertension": {
        "symptoms": ["blood pressure", "hypertension", "high bp", "cholesterol", "palpitations", "heart disease", "chest tightness"],
        "telugu_terms": ["రక్తపోటు", "గుండె", "హృదయం", "కొలెస్ట్రాల్"],
        "sanskrit_terms": ["Raktagatha Vata", "Hridroga", "Dhamani Pratichaya"],
        "dosha": "Vata-Pitta vitiation in Rasa and Raktavaha Srotas",
        "classical_texts": ["Charaka Samhita Hridroga", "Ashtanga Hridaya", "Swadesi Ahara Veda"],
        "key_herbs": ["Arjuna Bark (Terminalia Arjuna)", "Sarpagandha", "Pushkarmool", "Guggulu", "Garlic (Lashuna)", "Brahmi"]
    },
    "insomnia_stress": {
        "symptoms": ["insomnia", "sleeplessness", "poor sleep", "stress", "anxiety", "depression", "memory loss", "mental fatigue"],
        "telugu_terms": ["నిద్రలేమి", "నిద్ర", "ఒత్తిడి", "ఆందోళన", "జ్ఞాపకశక్తి"],
        "sanskrit_terms": ["Anidra", "Nidranasha", "Manasika Dosha (Rajas/Tamas)", "Smriti Mandya"],
        "dosha": "Vata vitiation affecting Manovaha Srotas and Tarpaka Kapha depletion",
        "classical_texts": ["Charaka Samhita Sutrasthana", "Ashtanga Hridaya", "Ayurveda Jeevana Vedam"],
        "key_herbs": ["Ashwagandha", "Brahmi (Bacopa)", "Shankhapushpi", "Jatamansi", "Tagara", "Warm Nutmeg Milk (Jatiphala)", "Shirodhara"]
    },
    "kidney_urinary": {
        "symptoms": ["kidney", "kidney stone", "urinary tract", "uti", "burning urination", "painful urination", "creatinine", "renal"],
        "telugu_terms": ["మూత్రపిండాలు", "మూత్రంలో మంట", "మూత్రపిండ రాళ్లు", "మూత్ర రోగాలు"],
        "sanskrit_terms": ["Ashmari", "Mutrakrichra", "Mutraghata", "Vrukka Roga"],
        "dosha": "Vata-Pitta crystallization forming Ashmari (stones)",
        "classical_texts": ["Sushruta Samhita Ashmari Chikitsa", "Charaka Samhita", "Vanamulika Veda"],
        "key_herbs": ["Pashanabheda", "Gokshura", "Punarnava", "Varuna", "Kulatta (Horsegram Kashayam)", "Chandraprabha Vati"]
    },
    "hair_care": {
        "symptoms": ["hair fall", "hair loss", "baldness", "dandruff", "premature graying", "split ends"],
        "telugu_terms": ["జుట్టు రాలడం", "వెంట్రుకలు", "చుండ్రు", "నెరవడం", "కేశ సౌందర్యం"],
        "sanskrit_terms": ["Khalitya", "Palitya", "Darunaka", "Kesha Rogam"],
        "dosha": "Pitta aggravating Asthi Dhatu and Bhrajaka Pitta",
        "classical_texts": ["Swadesi Soundarya Veda", "Ashtanga Hridaya", "Vanamulika Veda"],
        "key_herbs": ["Bhringraj", "Amalaki", "Brahmi", "Neelibhringadi Taila", "Methi (Fenugreek)", "Hibiscus (Japa)", "Triphala"]
    },
    "liver_jaundice": {
        "symptoms": ["liver", "jaundice", "fatty liver", "hepatitis", "yellow eyes", "loss of appetite"],
        "telugu_terms": ["కాలేయ రోగాలు", "కామెర్లు", "ఆకలి లేకపోవడం"],
        "sanskrit_terms": ["Yakrit Roga", "Kamila", "Pandu", "Arochaka"],
        "dosha": "Ranjaka Pitta vitiation leading to Yakrit-Pliha obstruction",
        "classical_texts": ["Charaka Samhita Pandu-Kamila Chikitsa", "Ashtanga Hridaya", "Vanamulika Veda"],
        "key_herbs": ["Bhumi Amalaki (Phyllanthus Niruri)", "Katuki", "Punarnava", "Kalmegh (Andrographis)", "Arogyavardhini Vati"]
    },
    "bowel_constipation": {
        "symptoms": ["constipation", "irregular bowel", "piles", "hemorrhoids", "fissure", "hard stools", "straining"],
        "telugu_terms": ["మలబద్ధకం", "మూలశంక", "పైల్స్", "మల విసర్జన"],
        "sanskrit_terms": ["Vibandha", "Arshas", "Apana Vayu Dushti", "Purishavaha Srotas"],
        "dosha": "Apana Vata dryness and sluggishness",
        "classical_texts": ["Charaka Samhita Chikitsasthana", "Ashtanga Hridaya", "Swadesi Ahara Veda"],
        "key_herbs": ["Triphala Churna", "Haritaki", "Isabgol", "Castor Oil (Eranda Taila)", "Senna", "Warm water with Ghee"]
    }
}

def expand_ayurvedic_query(query: str) -> Dict[str, Any]:
    """
    Analyzes user query, detects Ayurvedic clinical entities using regex word boundaries,
    and produces an enriched query for vector and hybrid search.
    """
    q_lower = query.lower()
    matched_domains = []
    clinical_keywords = []
    telugu_keywords = []
    sanskrit_keywords = []
    treatises = []
    herbs = []

    for domain_key, info in AYURVEDIC_KNOWLEDGE_BASE.items():
        domain_matched = False
        # Check English symptoms with strict word boundaries
        for s in info["symptoms"]:
            if re.search(r"\b" + re.escape(s) + r"\b", q_lower):
                domain_matched = True
                clinical_keywords.append(s)
                break
        # Check Telugu terms
        for t in info["telugu_terms"]:
            if t in query:
                domain_matched = True
                telugu_keywords.append(t)
                break

        if domain_matched:
            matched_domains.append(domain_key)
            telugu_keywords.extend(info["telugu_terms"][:3])
            sanskrit_keywords.extend(info["sanskrit_terms"][:2])
            treatises.extend(info["classical_texts"][:2])
            herbs.extend(info["key_herbs"][:3])

    # Deduplicate while preserving order
    telugu_keywords = list(dict.fromkeys(telugu_keywords))
    sanskrit_keywords = list(dict.fromkeys(sanskrit_keywords))
    treatises = list(dict.fromkeys(treatises))
    herbs = list(dict.fromkeys(herbs))

    # Build semantic search expansion query
    expansion_parts = [query]
    if telugu_keywords:
        expansion_parts.append(" ".join(telugu_keywords[:4]))
    if sanskrit_keywords:
        expansion_parts.append(" ".join(sanskrit_keywords[:3]))
    if treatises:
        expansion_parts.append(" ".join(treatises[:2]))

    expanded_query_str = " | ".join(expansion_parts)

    return {
        "original_query": query,
        "expanded_query": expanded_query_str,
        "matched_domains": matched_domains,
        "telugu_keywords": telugu_keywords,
        "sanskrit_keywords": sanskrit_keywords,
        "treatises": treatises,
        "herbs": herbs
    }

def calculate_precision_relevance_score(hit: Dict[str, Any], clinical_context: Dict[str, Any]) -> float:
    """
    Computes a composite relevance score for a retrieved hit
    based on vector score, Ayurveda status, topic matches, and treatise match.
    """
    base_score = float(hit.get("score", 0.0))
    boost = 0.0

    # Boost verified Ayurveda treatises
    if hit.get("is_ayurveda"):
        boost += 0.15

    source_book = (hit.get("source_book") or "").lower()
    text = (hit.get("text") or "").lower()

    for treatise in clinical_context.get("treatises", []):
        t_clean = treatise.lower().split()[0]
        if t_clean in source_book or t_clean in text:
            boost += 0.12
            break

    for herb in clinical_context.get("herbs", []):
        h_clean = herb.lower().split()[0]
        if h_clean in text:
            boost += 0.08
            break

    for tel_k in clinical_context.get("telugu_keywords", []):
        if tel_k in text:
            boost += 0.10
            break

    return min(1.0, base_score + boost)

def format_scriptural_context(passages: List[Dict[str, Any]]) -> str:
    """
    Formats retrieved scripture passages into a Perplexity-style prompt section
    with full metadata, direct FreeGurukul links, and passage numbers.
    """
    if not passages:
        return "=== SCRIPTURAL PASSAGES FROM AYURVEDIC BOOKS ===\nNo direct passages retrieved from the catalog index.\n\n"

    lines = ["=== SCRIPTURAL PASSAGES FROM AYURVEDIC BOOKS ===", ""]
    for i, p in enumerate(passages):
        idx = i + 1
        book_title = p.get("source_book") or "Ayurvedic Scripture"
        page_no = p.get("page_number", "N/A")
        category = p.get("category", "General")
        download_url = p.get("download_url", "")
        excerpt = (p.get("text") or "").strip()

        lines.append(f"[{idx}] Source Treatise: {book_title}")
        lines.append(f"    Category: {category} | Reference Page: {page_no}")
        if download_url:
            lines.append(f"    Digital Archive URL: {download_url}")
        lines.append(f"    Scriptural Text & Scope: {excerpt}")
        lines.append("")

    lines.append("=================================================")
    lines.append("")
    return "\n".join(lines)
