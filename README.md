# 🌿 Sushruta Ayurveda RAG - Intelligent Remedy Assistant

An authentic, domain-restricted **Retrieval-Augmented Generation (RAG)** web application designed for Ayurvedic health consultations. Built with **FastAPI**, **Pinecone Integrated Inference (`llama-text-embed-v2`)**, **Google Gemini 2.5 Flash**, and a responsive botanical frontend.

---

## 📸 System Overview

- **User Remedy Search**: Direct symptom analysis yielding structured formulations, herbal ingredients, dosages, preparation instructions, diet/lifestyle (*Pathya/Apathya*) advice, precautions, and book citations.
- **Strict Domain Guardrails**: Automatically detects and rejects non-health/non-Ayurvedic queries with standardized responses.
- **Admin Control Center** (Passcode: `admin123`): Password-protected panel for managing API credentials, uploading reference PDFs with background chunking, viewing index statistics, and resetting database vectors.
- **Serverless Integrated Inference**: Pinecone auto-embeds text using `llama-text-embed-v2` and optionally applies `bge-reranker-v2-m3` for high-precision document reranking.

---

## 📁 Repository Structure

```
ayurveda-rag/
├── .gitignore
├── README.md
└── backend/
    ├── main.py               # FastAPI application with REST endpoints & background tasks
    ├── pdf_parser.py         # PDF text extractor with sliding-window chunking
    ├── pinecone_helper.py    # Pinecone SDK client, index lifecycle, batch upsert & search
    ├── gemini_helper.py      # Gemini 2.5 Flash client with system prompt & guardrails
    ├── requirements.txt      # Python dependencies
    ├── test_pipeline.py      # Pipeline unit test suite
    ├── test_server.py        # Server integration test suite
    └── static/
        ├── index.html        # Single-page interface (Remedy Finder + Admin Console)
        ├── style.css         # Custom botanical theme styling
        └── app.js            # Reactive frontend logic & markdown rendering
```

---

## ⚡ Quick Start

### 1. Prerequisites
- Python 3.10+ (Tested up to Python 3.14)
- Pinecone API Key ([pinecone.io](https://www.pinecone.io/))
- Google Gemini API Key ([aistudio.google.com](https://aistudio.google.com/))

### 2. Installation
```powershell
cd ayurveda-rag/backend
pip install -r requirements.txt
```

### 3. Start the Application
```powershell
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser at `http://127.0.0.1:8000`.

### 4. Admin Setup
1. Click **Admin Panel** in the top navigation bar.
2. Enter the admin passcode: `admin123`.
3. Input your **Pinecone API Key**, **Pinecone Index Name** (default: `ayurveda-index`), and **Gemini API Key**, then click **Validate & Save Keys**.
4. Drag and drop your Ayurveda reference book PDFs (e.g. *Charaka Samhita*, *Sushruta Samhita*, *Ashtanga Hridayam*) into the upload box.
5. Once indexing finishes, return to the **Remedy Finder** tab and query any symptom!

---

## 🧪 Testing

Run the automated test suites:
```powershell
# Pipeline tests
python -m unittest test_pipeline.py

# Server integration tests
python -m unittest test_server.py
```

---

## 📜 License
MIT License. Traditional Ayurvedic formulations compiled for educational & wellness reference.
