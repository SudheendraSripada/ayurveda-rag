import logging
from typing import Generator, Optional
from google import genai
from google.genai import types

logger = logging.getLogger("gemini-helper")

DEFAULT_CANDIDATE_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite"
]

def resolve_candidate_models(model_name: Optional[str] = None) -> list[str]:
    """Return an ordered list of candidate models with the requested model first."""
    models = list(DEFAULT_CANDIDATE_MODELS)
    if model_name and model_name.strip():
        m = model_name.strip()
        if m in models:
            models.remove(m)
        models.insert(0, m)
    return models

SYSTEM_INSTRUCTION = """You are "Sage Dhanvantari", an expert, compassionate Ayurvedic physician and senior wellness consultant. 

Your mission is to guide patients and users toward vibrant health, vitality, and root-cause healing by synthesizing traditional Ayurvedic scriptures, classical compendia (Charaka Samhita, Sushruta Samhita, Ashtanga Hridaya, Vanamulika Veda, Swadesi Ahara Veda), and verified health principles.

=== CORE PERSONA & TONE ===
- **Empathetic, Wise, and Encouraging**: Communicate like a master Ayurvedic physician who deeply understands human physiology, Prakriti (body constitution), and the interconnectedness of mind, body, and spirit.
- **Root-Cause Focus**: Always analyze symptoms through the lens of Tridosha imbalances (Vata, Pitta, Kapha), Dhatus (tissues), Agni (digestive fire), and Ama (metabolic toxins).
- **Practical & Actionable**: Provide clear, accessible home remedies using everyday kitchen spices, herbal decoctions (Kashayams), lehyams, pastes, and lifestyle adjustments.

=== PERPLEXITY-STYLE CITATIONS & GROUNDING ===
1. **Primary Grounding**: Ground your advice strictly in the provided "SCRIPTURAL PASSAGES FROM AYURVEDIC BOOKS".
2. **Inline Numerical Citations**: Whenever you state a remedy, medicinal plant, formulation, dosage, or symptom mechanism from the context, include an inline citation `[1]`, `[2]`, `[3]` corresponding to the passage index.
3. **Multi-Source Synthesis**: If a remedy appears across multiple texts or pages, cite them together (e.g. `[1][3]`).
4. **General Knowledge Supplementation**: If the uploaded books do not contain the specific remedy for a health question, you may provide authentic classical Ayurvedic knowledge, but explicitly note: "*Note: This formulation is derived from classical Ayurvedic principles as the specific uploaded volumes did not directly contain this passage.*"

=== STRICT DOMAIN RESTRICTIONS ===
1. You MUST ONLY assist with queries related to health, wellness, symptoms, illnesses, anatomy, nutrition, herbs, daily routines (Dinacharya), seasonal routines (Ritucharya), and Ayurvedic principles.
2. If the user asks about anything outside health/Ayurveda (e.g., coding, computer science, math, finance, sports, politics, mechanics, pop culture, non-health cooking), you MUST refuse politely using this exact response:
"I am strictly authorized to provide health consultations and remedies based on Ayurvedic scriptures and reference books. I cannot assist with unrelated queries."

=== RESPONSE FORMAT ===
Organize your consultation in clean, engaging Markdown:
- **Greeting & Dosha Analysis**: Warm greeting and assessment of the likely Dosha imbalance (Vata / Pitta / Kapha) and root cause.
- **Herbal Formulations & Home Remedies**: 
  - List of raw herbs / kitchen ingredients with inline citations `[1]`, `[2]`.
  - Numbered, step-by-step preparation (decoction, paste, infused oil, powder).
- **Dosage & Anupana (Carrier)**: Exact dosage, timing (before/after meals, bedtime), and carrier vehicle (warm water, honey, cow's milk, ghee).
- **Pathya & Apathya (Diet & Lifestyle)**:
  - Foods & habits to embrace (Pathya).
  - Foods & habits to strictly avoid (Apathya).
  - Relevant daily routine advice (Dinacharya).
- **Precautions & Medical Disclaimer**: When to consult a clinic and specific contraindications (pregnancy, children, high BP).
- **Follow-Up Question**: Conclude with a helpful diagnostic question (e.g. asking about digestion, sleep, duration) to maintain an interactive consultation.
"""

def prepare_prompt_contents(messages: list[dict], context_passages: list[dict], language: str = "English") -> list[str]:
    # Construct context string with passage numbers for citations
    context_str = ""
    if context_passages:
        context_str = "=== SCRIPTURAL PASSAGES FROM AYURVEDIC BOOKS ===\n\n"
        for i, p in enumerate(context_passages):
            idx = i + 1
            source_book = p.get('source_book', 'Ayurvedic Scripture')
            page_no = p.get('page_number', 'N/A')
            category = p.get('category', 'General')
            download_url = p.get('download_url', '')
            excerpt = p.get('text', '').strip()
            
            context_str += f"[{idx}] Source Treatise: {source_book}\n"
            context_str += f"    Category: {category} | Reference Page: {page_no}\n"
            if download_url:
                context_str += f"    Digital Volume Archive: {download_url}\n"
            context_str += f"    Scriptural Text & Remedy Excerpt:\n    {excerpt}\n\n"
        context_str += "=================================================\n\n"
    else:
        context_str = "=== SCRIPTURAL PASSAGES FROM AYURVEDIC BOOKS ===\nNo direct passages found in the uploaded index.\n\n"
        
    # Language instruction directive
    lang_directive = ""
    if language and language.strip().lower() != "english":
        lang_directive = (
            f"\n=== MANDATORY LANGUAGE DIRECTIVE ===\n"
            f"You MUST generate your entire consultation and remedy response in {language}. "
            f"Write in natural, fluent {language} with traditional Ayurvedic terms, while preserving inline numerical citations like [1], [2].\n\n"
        )
    else:
        lang_directive = "\n=== MANDATORY LANGUAGE DIRECTIVE ===\nRespond in fluent English while preserving inline citations like [1], [2].\n\n"
        
    formatted_contents = []
    for i, msg in enumerate(messages):
        role = msg.get("role", "user")
        content = msg.get("content", "")
        
        if i == len(messages) - 1 and role == "user":
            user_content = f"{context_str}{lang_directive}Patient Query / Message:\n{content}"
            formatted_contents.append(user_content)
        else:
            formatted_contents.append(content)
            
    return formatted_contents

def generate_chat_remedy(
    api_key: str, 
    messages: list[dict], 
    context_passages: list[dict], 
    language: str = "English",
    model_name: Optional[str] = None
) -> str:
    """Generate multi-turn Ayurvedic consultation response in selected language using Gemini with retrieved context."""
    client = genai.Client(api_key=api_key)
    formatted_contents = prepare_prompt_contents(messages, context_passages, language)
            
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION + (f"\nIMPORTANT: The patient has requested this consultation strictly in {language} language." if language else ""),
        temperature=0.25
    )
    
    candidate_models = resolve_candidate_models(model_name)
    
    last_err = None
    for model in candidate_models:
        try:
            response = client.models.generate_content(
                model=model,
                contents=formatted_contents,
                config=config
            )
            return response.text
        except Exception as e:
            logger.warning(f"Model {model} failed: {str(e)}. Attempting next candidate...")
            last_err = e
            
    raise last_err or Exception("All Gemini model generation attempts failed.")

def stream_chat_remedy(
    api_key: str,
    messages: list[dict],
    context_passages: list[dict],
    language: str = "English",
    model_name: Optional[str] = None
) -> Generator[str, None, None]:
    """Stream multi-turn Ayurvedic consultation tokens in real-time."""
    client = genai.Client(api_key=api_key)
    formatted_contents = prepare_prompt_contents(messages, context_passages, language)
    
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION + (f"\nIMPORTANT: The patient has requested this consultation strictly in {language} language." if language else ""),
        temperature=0.25
    )
    
    candidate_models = resolve_candidate_models(model_name)
    
    for model in candidate_models:
        try:
            response_stream = client.models.generate_content_stream(
                model=model,
                contents=formatted_contents,
                config=config
            )
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
            return
        except Exception as e:
            logger.warning(f"Stream model {model} failed: {str(e)}. Attempting fallback...")
            continue
            
    raise Exception("Streaming failed across all candidate models.")
