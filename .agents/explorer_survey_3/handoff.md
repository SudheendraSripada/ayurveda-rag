# Survey & Technical Audit Report: Ayurvedic RAG & Scriptural Grounding Engine

**Agent**: Explorer 3 (Ayurvedic Intelligence & RAG Specialist)  
**Date**: 2026-08-23  
**Project Root**: `C:\Users\hi\ayurveda-rag`  
**Report Path**: `C:\Users\hi\ayurveda-rag\.agents\explorer_survey_3\handoff.md`  

---

## 1. Observation

Direct inspection of the codebase at `C:\Users\hi\ayurveda-rag` revealed the following technical components, configurations, and mechanics across data storage, vector retrieval, prompt design, scriptural grounding, and safety guardrails:

### 1.1 Inventory of the 31 Digitized Ayurvedic Scriptures

In `backend/ingest_books.py` (lines 16–48), the system defines an explicit corpus of 31 authentic Telugu and classical Sanskrit Ayurveda reference books retrieved from FreeGurukul CDN (`https://pdf.freegurukul.org/s/<id>`):

| Book ID | Scripture / Book Title (Original) | Transliteration / English Translation | Canonical Scope / Subject Matter | Source URL |
|---|---|---|---|---|
| **1** | అందరికి ఆయుర్వేదం-స్వదేశీ వనములికా వేదం | Andariki Ayurvedam - Swadeshi Vanamulika Vedam | Medicinal plants, herbal taxonomy, preparation of botanical remedies | `https://pdf.freegurukul.org/s/1406` |
| **2** | అందరికి ఆయుర్వేదం-స్వదేశీ ఆహార వేదం | Andariki Ayurvedam - Swadeshi Ahara Vedam | Traditional nutrition, food compatibility (*Viruddhahara*), dietary therapy | `https://pdf.freegurukul.org/s/1407` |
| **3** | అందరికి ఆయుర్వేదం-స్వదేశీ సౌందర్య వేదం | Andariki Ayurvedam - Swadeshi Soundarya Vedam | Skin, hair, ocular wellness, botanical cosmeceuticals | `https://pdf.freegurukul.org/s/1408` |
| **4** | అందరికి ఆయుర్వేదం-ఆయుర్వేద జీవన వేదం | Andariki Ayurvedam - Ayurveda Jeevana Vedam | Daily routine (*Dinacharya*), seasonal health (*Ritucharya*), preventive vitality | `https://pdf.freegurukul.org/s/1409` |
| **5** | అందరికి ఆయుర్వేదం-సంవత్సర సంచిక-1 | Andariki Ayurvedam - Samvatsara Sanchika 1 | Annual compendium of clinical case studies & herbal remedies (Vol 1) | `https://pdf.freegurukul.org/s/1410` |
| **6** | అందరికి ఆయుర్వేదం-సంవత్సర సంచిక-2 | Andariki Ayurvedam - Samvatsara Sanchika 2 | Annual compendium of clinical case studies & herbal remedies (Vol 2) | `https://pdf.freegurukul.org/s/1411` |
| **7** | అందరికి ఆయుర్వేదం-సంవత్సర సంచిక-3 | Andariki Ayurvedam - Samvatsara Sanchika 3 | Annual compendium of clinical case studies & herbal remedies (Vol 3) | `https://pdf.freegurukul.org/s/1412` |
| **8** | గృహ వైద్యం-4 | Griha Vaidyam 4 | Household first-aid, acute symptoms, kitchen remedies | `https://pdf.freegurukul.org/s/1414` |
| **9** | వ్యాసప్రోక్త వైద్య శాస్త్రము | Vyasa Prokta Vaidya Shastramu | Classical Vedic medical scripture & foundational healing verses | `https://pdf.freegurukul.org/s/1415` |
| **10** | మన్కి మిన్కి-ఆయుర్వేదం | Manki Minki - Ayurvedam | Pediatric care (*Kaumarbhritya*) and family Ayurvedic guide | `https://pdf.freegurukul.org/s/1418` |
| **11** | ఆయుర్వేదం ఆధునిక శాస్త్రీయ వికాసము | Ayurvedam Adhunika Shastriya Vikasamu | Modern scientific correlation & pharmacology of Ayurvedic formulations | `https://pdf.freegurukul.org/s/1419` |
| **12** | చరక సంహిత-విమాన స్థానము | Charaka Samhita - Vimana Sthana | Fundamental pathology, dosage measurements, Dosha assessment (*Dosa-Pramana*) | `https://pdf.freegurukul.org/s/1420` |
| **13** | చరక సంహిత-శారీర స్థానము | Charaka Samhita - Sharira Sthana | Human anatomy, embryology, physiology, mind-body constitution (*Prakriti*) | `https://pdf.freegurukul.org/s/1421` |
| **14** | చరక సంహిత-కల్ప స్థానము | Charaka Samhita - Kalpa Sthana | Pharmaceutical formulations, purification methods (*Panchakarma* preparation) | `https://pdf.freegurukul.org/s/1422` |
| **15** | చరక సంహిత-చికిత్సా స్థానము | Charaka Samhita - Chikitsa Sthana | Clinical therapeutics for internal diseases (Fever, Gulma, Prameha, Rajayakshma) | `https://pdf.freegurukul.org/s/1423` |
| **16** | అష్టాంగ హృదయము-సూత్ర స్థానము | Ashtanga Hridaya - Sutra Sthana | Fundamental principles of Tridosha, Dhatus, Agni, Ahara, and hygiene | `https://pdf.freegurukul.org/s/1425` |
| **17** | అష్టాంగ హృదయము-ఉత్తర స్థానము | Ashtanga Hridaya - Uttara Sthana | Specialized treatments: ENT (*Shalakya*), pediatrics (*Balaroga*), toxicology | `https://pdf.freegurukul.org/s/1426` |
| **18** | అష్టాంగ హృదయము-చికిత్స,కల్ప స్థానము | Ashtanga Hridaya - Chikitsa & Kalpa Sthana | Therapeutics for systemic conditions and specific compound recipes | `https://pdf.freegurukul.org/s/1427` |
| **19** | అందరికి ఆయుర్వేదం-2008 | Andariki Ayurvedam Annual 2008 | Historical monthly compendium on indigenous herbs & treatments | `https://pdf.freegurukul.org/s/3391` |
| **20** | అందరికి ఆయుర్వేదం-2009 | Andariki Ayurvedam Annual 2009 | Historical monthly compendium on indigenous herbs & treatments | `https://pdf.freegurukul.org/s/3392` |
| **21** | అందరికి ఆయుర్వేదం-2010 | Andariki Ayurvedam Annual 2010 | Historical monthly compendium on indigenous herbs & treatments | `https://pdf.freegurukul.org/s/3393` |
| **22** | అందరికి ఆయుర్వేదం-2011 | Andariki Ayurvedam Annual 2011 | Historical monthly compendium on indigenous herbs & treatments | `https://pdf.freegurukul.org/s/3394` |
| **23** | అందరికి ఆయుర్వేదం-2012 | Andariki Ayurvedam Annual 2012 | Historical monthly compendium on indigenous herbs & treatments | `https://pdf.freegurukul.org/s/3395` |
| **24** | అందరికి ఆయుర్వేదం-2013 | Andariki Ayurvedam Annual 2013 | Historical monthly compendium on indigenous herbs & treatments | `https://pdf.freegurukul.org/s/3396` |
| **25** | అందరికి ఆయుర్వేదం-2014 | Andariki Ayurvedam Annual 2014 | Historical monthly compendium on indigenous herbs & treatments | `https://pdf.freegurukul.org/s/3397` |
| **26** | అందరికి ఆయుర్వేదం-2015 | Andariki Ayurvedam Annual 2015 | Historical monthly compendium on indigenous herbs & treatments | `https://pdf.freegurukul.org/s/3398` |
| **27** | వంట ఇల్లే వైద్యశాల | Vanta Ille Vaidyashala | "Kitchen Pharmacy" — culinary spice therapeutics (Turmeric, Ginger, Cumin) | `https://pdf.freegurukul.org/s/1394` |
| **28** | ప్రకృతి వైద్యం | Prakruti Vaidyam | Naturopathic principles, hydrotherapy, earth/sun therapies aligned with Ayurveda | `https://pdf.freegurukul.org/s/1390` |
| **29** | ప్రకృతి వైద్య తత్త్వము | Prakruti Vaidya Tattvamu | Philosophy of natural therapeutics and self-healing bio-mechanisms | `https://pdf.freegurukul.org/s/1392` |
| **30** | ప్రకృతి గృహ వైద్యం | Prakruti Griha Vaidyam | Practical household nature treatments for common ailments | `https://pdf.freegurukul.org/s/1393` |
| **31** | గృహౌషద వనము | Grihaushadha Vanamu | Cultivation & clinical use of home medicinal gardens (Tulsi, Aloe, Neem) | `https://pdf.freegurukul.org/s/1396` |

---

### 1.2 Ingestion & Text Chunking Architecture

1. **Storage Format**:
   - Primary data source: Downloaded PDF files stored in directory `backend/downloaded_books/` (`ingest_books.py`, line 50).
   - Ingestion entry point: `ingest_books.py` (`ingest_all_books()`).

2. **Text Cleaning & Normalization (`backend/pdf_parser.py`, lines 5–17)**:
   ```python
   def clean_text(text: str) -> str:
       # Replaces \r\n and \r with \n
       # Collapses horizontal whitespace to single space
       # Strips leading/trailing spaces around newlines
       # Collapses 3+ consecutive newlines to \n\n
   ```

3. **Sliding-Window Chunking Algorithm (`backend/pdf_parser.py`, lines 19–63)**:
   - Chunk Size: `chunk_size = 800` characters.
   - Overlap: `overlap = 150` characters.
   - Lookback Heuristic: When reaching `start + chunk_size`, searches backward up to `min(overlap, 100, remaining_length)` for natural boundary characters (`\n`, `.`, `!`, `?`, or space).
   - Forward Progression Guarantee: `stride = max(1, chunk_size - overlap)` ensuring no infinite loops on dense passages.

4. **Chunk Metadata Specification (`backend/pdf_parser.py`, lines 84–96)**:
   ```python
   {
       "id": f"{safe_filename}_p{page_num}_c{chunk_idx}",
       "text": chunk_text_content,
       "source_book": book_title,
       "page_number": page_num,
       "chunk_index": chunk_idx
   }
   ```
   - Alphanumeric sanitize: `re.sub(r'[^a-zA-Z0-9\._-]', '_', filename)` ensures Pinecone vector ID compliance.

---

### 1.3 Vector Store, Embedding Model & Retrieval Pipeline

1. **Vector Store**: Pinecone Serverless Index (`backend/pinecone_helper.py`, lines 8–29).
   - Cloud: AWS
   - Region: `us-east-1`
   - Default Index Name: `ayurveda-index` (configured via `PINECONE_INDEX_NAME` in `.env`).
   - Namespace: `"ayurveda"` (`pinecone_helper.py`, line 113, `main.py`, line 106).

2. **Embedding Model**:
   - Model: `llama-text-embed-v2` via **Pinecone Integrated Inference** (`pinecone_helper.py`, lines 18–21).
   - Embedding Field Mapping: `{"text": "chunk_text"}`.
   - Ingestion Method: `index.upsert_records(namespace="ayurveda", records=batch)` where each record contains `_id`, `chunk_text`, `source_book`, and `page_number`. Batched in chunks of 100 records (`pinecone_helper.py`, lines 94–99).
   - Key Property: Zero local GPU/PyTorch dependencies required; Pinecone serverless handles vectorization on upsert and query.

3. **Retrieval & Neural Reranker (`backend/pinecone_helper.py`, lines 109–166)**:
   - Base Retrieval: Initial vector search fetches `top_k = 15` semantic candidates.
   - Reranker: `bge-reranker-v2-m3` applied serverless via Pinecone:
     ```python
     search_params["rerank"] = {
         "model": "bge-reranker-v2-m3",
         "rank_fields": ["chunk_text"],
         "top_n": 5
     }
     ```
   - Reranking can be toggled by user in UI (`#checkbox-rerank`) and via API payload (`rerank: bool`).
   - Output: Returns `top_n = 5` passages with `id`, `score`, `text`, `source_book`, `page_number`.

---

### 1.4 System Prompts & Ayurvedic Domain Logic

Located in `backend/gemini_helper.py` (lines 8–41):

1. **Physician Persona & Archetype**:
   - Persona: `"Sage Dhanvantari"` — expert, compassionate master Ayurvedic physician and senior wellness consultant.
   - Foundational Compendia: Explicitly instructed to synthesize *Charaka Samhita*, *Sushruta Samhita*, *Ashtanga Hridaya*, *Vanamulika Veda*, and *Swadesi Ahara Veda*.

2. **Ayurvedic Diagnostic Logic**:
   - **Tridosha**: Root-cause analysis evaluating Vata (dryness, pain, mobility, nervous impulses), Pitta (heat, inflammation, acidity, metabolism), and Kapha (congestion, heaviness, stagnation, mucus).
   - **Agni & Ama**: Assessment of digestive fire strength (Sama/Vishama/Tikshna/Manda Agni) and presence of toxic metabolic residue (*Ama*).
   - **Dhatus & Malas**: Consideration of 7 bodily tissue strata (*Rasa*, *Rakta*, *Mamsa*, *Meda*, *Asthi*, *Majja*, *Shukra*) and excretions (*Malas*).
   - **Prakriti vs Vikriti**: Differentiating inborn constitutional baseline from current pathological vitiation.
   - **Formulations**: Practical, accessible remedies utilizing kitchen herbs, spices, herbal decoctions (*Kashayams*), medicinal jams (*Lehyams*), herbal powders (*Churnas*), medicated oils (*Tailas*), and topical pastes (*Lepas*).
   - **Dosage & Anupana**: Strict requirement for exact dosages and carrier vehicles (*Anupana*: warm water, raw honey, cow's milk, rock candy, pure ghee) with chronotherapeutic timing (e.g., empty stomach, pre-meal, post-meal, bedtime).
   - **Pathya & Apathya**: Clear division into dietary/lifestyle habits to adopt (*Pathya*) vs habits to strictly avoid (*Apathya*), incorporating daily routine (*Dinacharya*) and seasonal regimen (*Ritucharya*).
   - **Interactive Consultation**: Mandates concluding each consultation with a targeted diagnostic inquiry (assessing digestion, bowel regularity, sleep, stress, duration).

3. **Multi-Language Architecture**:
   - Dynamic prompt injection (`gemini_helper.py`, lines 67–76):
     ```python
     if language and language.strip().lower() != "english":
         lang_directive = (
             f"\n=== MANDATORY LANGUAGE DIRECTIVE ===\n"
             f"You MUST generate your entire consultation and remedy response in {language}. "
             f"Write in natural, fluent {language} with traditional Ayurvedic terms, while preserving inline numerical citations like [1], [2].\n\n"
         )
     ```
   - Supported across 12 languages: English, Telugu, Hindi, Sanskrit, Tamil, Kannada, Malayalam, Marathi, Bengali, Spanish, French, German.

4. **Model Cascade & Generation Parameters**:
   - Models: Cascade through `["gemini-3.6-flash", "gemini-2.5-flash", "gemini-flash-latest"]`.
   - Temperature: `0.25` (ensuring clinical precision and minimizing creative drift).

---

### 1.5 Scriptural Citation Grounding Engine

1. **Context Construction (`backend/gemini_helper.py`, lines 54–65)**:
   Retrieved passages are formatted into structured numbered blocks:
   ```
   === SCRIPTURAL PASSAGES FROM AYURVEDIC BOOKS ===
   [1] Source Book: చరక సంహిత-చికిత్సా స్థానము
       Page Number: 142
       Excerpt: ...
   [2] Source Book: అందరికి ఆయుర్వేదం-స్వదేశీ ఆహార వేదం
       Page Number: 88
       Excerpt: ...
   =================================================
   ```

2. **Inline Citation Rules (`backend/gemini_helper.py`, lines 17–22)**:
   - Requires inline numerical citations `[1]`, `[2]`, `[3]` for every remedy, herb, formulation, dosage, or symptom mechanism extracted from the context passages.
   - Allows multi-source synthesis brackets (e.g., `[1][3]`).

3. **API Response Contract (`backend/main.py`, lines 126–130)**:
   ```json
   {
       "reply": "Warm greeting ... Triphala decoction [1] balances Pitta and Kapha ... [2]",
       "sources": [
           {
               "id": "book_15_charaka_p142_c1",
               "score": 0.892,
               "text": "Exact text chunk from scripture...",
               "source_book": "చరక సంహిత-చికిత్సా స్థానము",
               "page_number": 142
           }
       ],
       "language": "English"
   }
   ```

4. **Frontend Citation & Popover Rendering (`backend/static/app.js`, lines 840–896)**:
   - **Sources Tray**: `renderSourcesTray(sources)` renders clickable badge chips above the physician's response bubble.
   - **Inline Citation Conversion**: `formatMessageWithCitations(text, sources)` executes regex `text.replace(/\[(\d+)\]/g, ...)` converting `[N]` into `<a class="inline-citation" data-source-idx="${N - 1}">[N]</a>`.
   - **Interactive Popovers**: Clicking any `.inline-citation` or `.source-chip` triggers `showCitationPopover()`, which positions `#citation-popover` relative to the clicked element and displays:
     - Scripture Title (`popover-book-title`)
     - Scripture Page Number (`popover-page`)
     - Verbatim Passage Excerpt (`popover-excerpt`)

---

### 1.6 Guardrails, Medical Safety & Hallucination Prevention

1. **Strict Domain Guardrail (`backend/gemini_helper.py`, lines 23–26)**:
   - Explicitly restricts scope to health, wellness, symptoms, illnesses, anatomy, nutrition, herbs, Dinacharya, Ritucharya, and Ayurvedic principles.
   - Refusal formula:
     > *"I am strictly authorized to provide health consultations and remedies based on Ayurvedic scriptures and reference books. I cannot assist with unrelated queries."*

2. **Hallucination Prevention on Missing Passages (`gemini_helper.py`, line 21)**:
   - When the uploaded vector index does not contain the specific passage for a health query, the model is permitted to draw upon authentic classical Ayurvedic knowledge, but is constrained to append:
     > `"*Note: This formulation is derived from classical Ayurvedic principles as the specific uploaded volumes did not directly contain this passage.*"`

3. **Clinical Safety & Contraindications (`gemini_helper.py`, line 39)**:
   - Mandatory inclusion of precautions: pregnancy/lactation safety, pediatric considerations, hypertension cautions, herb-drug interactions, and clinical red flags requiring immediate emergency medical evaluation.

4. **Disclaimers & Legal Transparency (`backend/static/index.html`, lines 509–524, `app.js`, lines 934–965)**:
   - Input footer warning: *"Sushruta AI can make mistakes. Consider verifying important remedies. Compiled strictly for Ayurvedic reference."*
   - Dedicated modal popups for **Privacy Policy** (local-first storage, zero tracking), **Terms of Service** (educational reference only), and **Medical Disclaimer** (not a substitute for hospital emergency care or licensed diagnosis).

---

### 1.7 Discovered Bugs & Test Pipeline Discrepancies

1. **Unit Test Failure in `test_pipeline.py`**:
   - Command: `python -m unittest test_pipeline.py`
   - Failure: `test_guardrails_instruction` fails with `AssertionError: 'STRICTOR DOMAIN GUARDRAILS' not found in SYSTEM_INSTRUCTION`.
   - Root Cause: `test_pipeline.py` line 22 checks for `"STRICTOR DOMAIN GUARDRAILS"`, whereas `gemini_helper.py` line 23 has `"=== STRICT DOMAIN RESTRICTIONS ==="`.
2. **Integration Test Suite**:
   - Command: `python -m unittest test_server.py`
   - Result: 5 tests passed (100% OK).

---

## 2. Logic Chain

The following deductive chain explains how the components interact from user query to grounded remedy:

1. **User Query Input**: The user describes their physical symptoms, Prakriti questions, or health inquiry on the frontend (`app.js`), selecting their preferred consultation language and reranking preference.
2. **Pinecone Semantic Vector Retrieval**:
   - `main.py` forwards the query string to `pinecone_helper.search_index()`.
   - Pinecone serverless embedding model `llama-text-embed-v2` embeds the query on the fly without local GPU compute.
   - Pinecone retrieves top 15 candidate passages from the `"ayurveda"` namespace across the 31 indexed Ayurvedic books.
   - `bge-reranker-v2-m3` neural cross-encoder ranks the passages and isolates the top 5 most relevant excerpts.
3. **Prompt Formulation & Context Injection**:
   - `gemini_helper.py` formats these 5 passages into numbered entries `[1]`, `[2]`, ... `[5]`.
   - Dynamic language directives and the complete conversation history (`messages`) are packed into Gemini contents.
4. **Physician Synthesis (`gemini-3.6-flash`)**:
   - Gemini applies the Sage Dhanvantari persona, evaluating Tridosha root cause, Dhatus, Agni, and Ama.
   - Gemini structures the output into Dosha Analysis, Formulations with step-by-step prep, Dosage & Anupana, Pathya/Apathya, Precautions, and Follow-up diagnostic questions.
   - Gemini embeds inline bracketed citations (e.g. `[1]`, `[2]`) pointing to the indexed passages.
5. **Payload Transmission & UI Grounding**:
   - FastAPI returns the JSON response containing the generated text and the list of source passage dicts.
   - `app.js` renders the Perplexity-style Sources Tray and converts `[N]` references into clickable links.
   - User clicks citation links to inspect verbatim book names, page numbers, and original scriptural excerpts.

---

## 3. Caveats

1. **Corpus Availability**: The 31 PDF books are not pre-bundled in the git repository (to conserve repo size); they are downloaded dynamically via `ingest_books.py` to `downloaded_books/` when running the ingestion job.
2. **Sanskrit vs Telugu Titles**: While the system prompt and UI references cite classical Sanskrit compendia (*Charaka Samhita*, *Sushruta Samhita*, *Ashtanga Hridaya*), the actual FreeGurukul URLs include Charaka and Ashtanga Hridaya Sthanas translated/commentated in Telugu alongside traditional Telugu home medicine compendia. Standalone *Sushruta Samhita* (Sharira/Sutra/Chikitsa Sthana) is not yet explicitly in `BOOKS_LIST` in `ingest_books.py`.
3. **No Real-Time Streaming Yet**: The `/api/chat` endpoint is currently a standard synchronous blocking HTTP POST endpoint. Streaming tokens via Server-Sent Events (SSE) or WebSockets is not yet implemented.
4. **Client-Side Persistence Only**: Chat history and sessions are currently stored solely in the client browser's `localStorage` (`sushruta_chat_sessions_v1`). There is no backend database (SQLite/PostgreSQL) with user authentication or multi-tenant session isolation.
5. **Dense-Only Retrieval**: Current Pinecone retrieval relies entirely on dense semantic vectors (`llama-text-embed-v2`). Technical Sanskrit terms (*Srotas*, *Dhatu Agni*, *Vipaka*, *Prabhava*, specific botanical binomials) would benefit from hybrid BM25 + dense search.

---

## 4. Conclusion

The Ayurvedic RAG and scriptural grounding capabilities provide a solid foundational architecture:
- **Clean Ingestion & Chunking**: 800-char sliding window with lookback sentence boundaries and page-level metadata tracking.
- **Serverless Pinecone Retrieval**: Integrated embedding with `llama-text-embed-v2` and neural reranking with `bge-reranker-v2-m3`.
- **Rich Ayurvedic Intelligence**: Sage Dhanvantari persona systematically reasons across Tridosha, Dhatus, Agni, Ama, Anupana, and Pathya/Apathya.
- **Perplexity-Style Citations**: Seamless end-to-end integration from retrieved passages to LLM citation generation and interactive frontend popovers.
- **Safety & Guardrails**: Clear non-health query refusal, ungrounded knowledge flags, and medical disclaimers.

### Actionable Roadmap for Implementation Milestones:
1. **Fix `test_pipeline.py`**: Update line 22 from `"STRICTOR DOMAIN GUARDRAILS"` to `"STRICT DOMAIN RESTRICTIONS"` to pass unit tests.
2. **Milestone 1 (Auth & Isolation)**: Implement backend JWT/Session auth and user-specific conversation isolation.
3. **Milestone 2 (Database Persistence)**: Add SQLite/PostgreSQL schema storing users, chat sessions, messages, and citation metadata.
4. **Milestone 3 (Real-Time SSE Token Streaming)**: Convert `/api/chat` to an SSE stream endpoint that yields tokens progressively while streaming citation metadata at the start/end of generation.
5. **Milestone 4 (Enhanced Model Intelligence & Scripture Expansion)**: Expand `BOOKS_LIST` to include Sushruta Samhita, Sharangadhara Samhita, and Madhava Nidana, and add hybrid BM25 search for exact Sanskrit nomenclature.

---

## 5. Verification Method

To independently verify all findings in this report, execute the following commands in PowerShell from `C:\Users\hi\ayurveda-rag\backend`:

1. **Verify Backend Dependencies & Code Structure**:
   ```powershell
   cd C:\Users\hi\ayurveda-rag\backend
   Get-ChildItem -Path .
   ```
2. **Verify Server Integration Tests**:
   ```powershell
   python -m unittest test_server.py
   ```
   *Expected*: 5 tests run, status `OK`.
3. **Verify Pipeline Test Discrepancy**:
   ```powershell
   python -m unittest test_pipeline.py
   ```
   *Expected*: Discrepancy in `test_guardrails_instruction` due to `"STRICTOR DOMAIN GUARDRAILS"` string mismatch.
4. **Verify 31 Scriptures Definition**:
   Inspect `ingest_books.py` lines 16–48 to confirm exactly 31 items in `BOOKS_LIST`.
5. **Verify Pinecone Integrated Inference Configuration**:
   Inspect `pinecone_helper.py` lines 18–21 for model `"llama-text-embed-v2"` and lines 132–137 for reranker `"bge-reranker-v2-m3"`.
6. **Verify Citation Extraction & Popover**:
   Inspect `gemini_helper.py` lines 53–65 (passage numbering) and `static/app.js` lines 863–896 (regex `\[(\d+)\]` replacement and popover display).

### Invalidation Conditions:
- If `BOOKS_LIST` in `ingest_books.py` is modified or removed.
- If Pinecone integrated embedding model or field mapping is altered.
- If system prompt citation instructions in `gemini_helper.py` are changed.
