// State Management
let currentSessionId = null;
let chatSessions = [];
let isGenerating = false;
let currentSources = [];
let currentUser = null;

// Storage Keys
const SESSIONS_STORAGE_KEY = "sushruta_chat_sessions_v1";
const SITE_LANG_STORAGE_KEY = "sushruta_site_language_v1";
const RESPONSE_LANG_STORAGE_KEY = "sushruta_response_language_v1";
const AUTH_TOKEN_KEY = "sushruta_auth_token_v1";
const API_BASE_STORAGE_KEY = "sushruta_api_base_url_v1";
const LOCAL_USER_STORAGE_KEY = "sushruta_local_user_v1";

function getApiBaseUrl() {
    const saved = localStorage.getItem(API_BASE_STORAGE_KEY);
    if (saved && saved.trim()) return saved.trim().replace(/\/+$/, "");
    return "";
}

// =========================================================
// I18N TRANSLATION DICTIONARIES (Website UI Language)
// =========================================================
const I18N_DICTIONARY = {
    "English": {
        "tagline": "Ayurvedic Physician RAG",
        "nav_how_it_works": "How It Works",
        "nav_pillars": "Clinical Pillars",
        "nav_scriptures": "31 Scriptures",
        "nav_faq": "FAQ",
        "site_lang_label": "Site:",
        "nav_start_btn": "Start Consultation",
        "nav_login": "Sign In",
        "hero_badge": "<i class=\"fa-solid fa-sparkles\"></i> 5,000 Years of Vedic Wisdom &bull; Grounded in 31 Scriptures",
        "hero_title_1": "Ancient Ayurvedic Healing,",
        "hero_title_2": "Prescribed by Neural Intelligence.",
        "hero_subtitle": "Consult <strong>Sage Dhanvantari</strong> — an AI Ayurvedic physician grounded in classical digitized treatises (Charaka Samhita, Sushruta Samhita, Ashtanga Hridaya, and traditional Telugu Veda Granthas). Receive root-cause Tridosha diagnoses and verified home remedies with Perplexity-style scriptural citations.",
        "hero_btn_consult": "Start Free Consultation",
        "hero_btn_rag": "How RAG Works",
        "popular_inquiries": "Popular Inquiries (Click to ask Sage Dhanvantari):",
        "prompt_sinus_title": "Sinusitis & Headache",
        "prompt_sinus_desc": "Steam inhalation, Anu Taila & Kapha relief",
        "prompt_reflux_title": "Acid Reflux & Pitta",
        "prompt_reflux_desc": "Cooling herbs, Amla & Agni balance",
        "prompt_joint_title": "Joint Pain & Vata",
        "prompt_joint_desc": "Mahanarayana oil & Guggulu decoctions",
        "prompt_hair_title": "Hair & Scalp Health",
        "prompt_hair_desc": "Bhringraj, Brahmi & herbal hair tonics",
        "stats_scriptures": "Classical Scriptures Digitized",
        "stats_citations": "Grounded & Verified Citations",
        "stats_languages": "Languages Supported",
        "stats_free": "Free & Privacy-First",
        "arch_badge": "Architecture",
        "arch_title": "How Sushruta AI Works",
        "arch_sub": "A 3-step neural pipeline combining vector semantic retrieval with clinical physician synthesis.",
        "step_1_num": "Step 1",
        "step_1_title": "Classical Scripture Corpus",
        "step_1_desc": "31 volumes of Sanskrit and Telugu Ayurvedic treatises are indexed into semantic, searchable passages.",
        "step_2_num": "Step 2",
        "step_2_title": "Pinecone Neural RAG",
        "step_2_desc": "When you describe your symptoms, vector search and neural reranking (bge-reranker) retrieve the most relevant classical passages.",
        "step_3_num": "Step 3",
        "step_3_title": "Physician Synthesis",
        "step_3_desc": "Sage Dhanvantari synthesizes a structured remedy with Dosha analysis, kitchen ingredients, dosages, and verifiable Perplexity-style citations.",
        "pillars_badge": "Principles",
        "pillars_title": "Core Clinical Principles",
        "pillars_sub": "Root-cause healing that treats the person, not just the symptom.",
        "pillar_1_title": "Tridosha Root-Cause Diagnosis",
        "pillar_1_desc": "Assesses Vata (movement/nervous system), Pitta (metabolism/digestion), and Kapha (structure/immunity) imbalances.",
        "pillar_2_title": "Accessible Kitchen Formulations",
        "pillar_2_desc": "Prescribes safe, authentic home remedies using turmeric, ginger, black pepper, cumin, ghee, and herbal decoctions.",
        "pillar_3_title": "Verifiable Page Citations",
        "pillar_3_desc": "Every single herb and dosage is linked to its source book and page number with clickable excerpt popovers.",
        "pillar_4_title": "Zero-Tracking Privacy",
        "pillar_4_desc": "Your health questions and chat history are saved in your browser local storage with zero cloud profiling or data selling.",
        "scriptures_badge": "Knowledge Base",
        "scriptures_title": "31 Digitized Classical Treatises",
        "scriptures_sub": "Comprehensive compendia spanning centuries of traditional medical wisdom.",
        "faq_badge": "FAQ",
        "faq_title": "Frequently Asked Questions",
        "faq_q1": "Is Sushruta AI a replacement for a doctor?",
        "faq_a1": "No. Sushruta AI is an educational RAG reference tool grounded in authentic Ayurvedic literature. For emergency symptoms, acute conditions, or prescription medicines, always consult a licensed medical professional.",
        "faq_q2": "How do citations work?",
        "faq_a2": "Whenever Sage Dhanvantari recommends a formulation or herb from the 31 books, a numbered badge like [1] or [2] appears. Clicking it displays the original book title and page excerpt.",
        "faq_q3": "Is my consultation data private?",
        "faq_a3": "Yes. Your conversation history is saved securely in your private user database or browser localStorage. No personal consultation logs are sold or monetized.",
        "cta_banner_title": "Ready to Begin Your Healing Journey?",
        "cta_banner_sub": "Experience authentic, root-cause Ayurvedic consultations in your preferred language.",
        "cta_banner_btn": "Start Consultation Now",
        "footer_privacy": "Privacy Policy",
        "footer_terms": "Terms of Service",
        "footer_disclaimer": "Medical Disclaimer",
        "footer_copy": "© 2026 Sushruta AI. Grounded in traditional classical scriptures for wellness & longevity.",
        "sidebar_home": "Home & About",
        "sidebar_new_chat": "New Consultation",
        "sidebar_history_title": "Consultations",
        "sidebar_clear_btn": "Clear",
        "sidebar_quick_inquiries": "Quick Inquiries",
        "doc_name": "Sage Dhanvantari",
        "doc_grounded": "Grounded in 31 Ayurvedic Scriptures",
        "header_home": "Home",
        "welcome_title": "Ayurvedic Health Consultation",
        "welcome_subtitle": "Ask any question regarding your health, symptoms, or vitality. I synthesize classical Ayurvedic scriptures (Charaka Samhita, Sushruta Samhita, Ashtanga Hridaya, Vanamulika Veda, Swadesi Ahara Veda) to prescribe authentic, root-cause home remedies with verifiable citations.",
        "welcome_card1_title": "Digestive Agni & Ama",
        "welcome_card1_desc": "Discover natural carminative herbs & dietary rules for sluggish digestion.",
        "welcome_card2_title": "Immunity & Allergies",
        "welcome_card2_desc": "Traditional herbal decoctions (Kashayam) to balance Kapha and soothe airways.",
        "welcome_card3_title": "Mental Wellness (Manasa)",
        "welcome_card3_desc": "Medhya Rasayanas & herbs to calm the central nervous system.",
        "welcome_card4_title": "Skin & Blood Purifiers",
        "welcome_card4_desc": "Neem, Manjistha, and herbal pastes for radiant, clear skin.",
        "input_warning": "Sushruta AI can make mistakes. Consider verifying important remedies. Compiled strictly for Ayurvedic reference."
    },
    "Telugu": {
        "tagline": "ఆయుర్వేద వైద్య ఆర్.ఏ.జి (RAG)",
        "nav_how_it_works": "పనిచేసే విధానం",
        "nav_pillars": "వైద్య సూత్రాలు",
        "nav_scriptures": "31 గ్రంథాలు",
        "nav_faq": "సందేహాలు (FAQ)",
        "site_lang_label": "భాష:",
        "nav_start_btn": "వైద్య సలహా పొందండి",
        "nav_login": "లాగిన్",
        "hero_badge": "<i class=\"fa-solid fa-sparkles\"></i> 5000 ఏళ్ళ ప్రాచీన వేద విజ్ఞానం &bull; 31 ప్రామాణిక గ్రంథాలు",
        "hero_title_1": "ప్రాచీన ఆయుర్వేద చికిత్స,",
        "hero_title_2": "కృత్రిమ మేధస్సు (AI) సహకారంతో.",
        "hero_subtitle": "<strong>శ్రీ ధన్వంతరి</strong> వైద్యుని సంప్రదించండి — చరక, సుశ్రుత, అష్టాంగ హృదయము మరియు స్వదేశీ వనమూలికా వేదం వంటి 31 ప్రామాణిక గ్రంథాల ఆధారంగా మూల కారణాన్ని సరిచేసే త్రిదోష చికిత్సలను, వంటింటి ఔషధాలను పుస్తక రిఫరెన్స్‌లతో తెలుసుకోండి.",
        "hero_btn_consult": "ఉచిత వైద్య సలహా ప్రారంభించండి",
        "hero_btn_rag": "పనిచేసే విధానం",
        "popular_inquiries": "ముఖ్యమైన ఆరోగ్య సమస్యలు (ధన్వంతరి గారిని అడగడానికి క్లిక్ చేయండి):",
        "prompt_sinus_title": "సైనసైటిస్ & తలనొప్పి",
        "prompt_sinus_desc": "ఆవిరి పట్టడం, అణు తైలం & కఫ నివారణ",
        "prompt_reflux_title": "ఎసిడిటీ & పిత్త దోషం",
        "prompt_reflux_desc": "చలువ చేసే మూలికలు, ఉసిరి & జీర్ణశక్తి",
        "prompt_joint_title": "కీళ్ల నొప్పులు & వాతం",
        "prompt_joint_desc": "మహానారాయణ తైలం & గుగ్గులు కషాయాలు",
        "prompt_hair_title": "జుట్టు & చర్మ సంరక్షణ",
        "prompt_hair_desc": "భృంగరాజ తైలం, బ్రాహ్మి & జుట్టు పెరుగుదల",
        "stats_scriptures": "డిజిటలైజ్ చేసిన గ్రంథాలు",
        "stats_citations": "ఖచ్చితమైన పుస్తక ఆధారాలు",
        "stats_languages": "అందుబాటులో ఉన్న భాషలు",
        "stats_free": "పూర్తిగా ఉచితం & గోప్యత",
        "arch_badge": "సాంకేతిక విధానం",
        "arch_title": "సుశ్రుత AI ఎలా పనిచేస్తుంది?",
        "arch_sub": "ప్రాచీన గ్రంథాల సమాచార శోధన మరియు న్యూరల్ AI వైద్య విశ్లేషణల సమన్వయం.",
        "step_1_num": "దశ 1",
        "step_1_title": "31 ప్రాచీన గ్రంథాలు",
        "step_1_desc": "సంస్కృత మరియు తెలుగు ఆయుర్వేద గ్రంథాలు సులభంగా శోధించగలిగే భాగాలుగా అమర్చబడ్డాయి.",
        "step_2_num": "దశ 2",
        "step_2_title": "పైన్‌కోన్ న్యూరల్ RAG",
        "step_2_desc": "మీ ఆరోగ్య సమస్యను బట్టి సరియైన వైద్య శ్లోకాలను, పేజీలను క్షణాల్లో వెలికితీస్తుంది.",
        "step_3_num": "దశ 3",
        "step_3_title": "ధన్వంతరి వైద్య విశ్లేషణ",
        "step_3_desc": "త్రిదోష విశ్లేషణ, వంటింటి పదార్థాలు, మోతాదు మరియు పుస్తక రిఫరెన్స్‌లతో సమగ్ర పరిష్కారం అందిస్తుంది.",
        "pillars_badge": "వైద్య సూత్రాలు",
        "pillars_title": "ముఖ్యమైన ఆయుర్వేద మూలస్తంభాలు",
        "pillars_sub": "లక్షణాలను దాచడం కాదు, మూల కారణాన్ని తొలగించే సహజ వైద్యం.",
        "pillar_1_title": "త్రిదోష మూలకారణ నిర్ధారణ",
        "pillar_1_desc": "వాత, పిత్త, కఫ దోషాల హెచ్చుతగ్గులను పరిశీలించి చికిత్స సూచిస్తుంది.",
        "pillar_2_title": "సులభమైన వంటింటి ఔషధాలు",
        "pillar_2_desc": "పసుపు, అల్లం, మిరియాలు, జీలకర్ర, నెయ్యి మరియు కషాయాలతో సురక్షిత వైద్యం.",
        "pillar_3_title": "స్పష్టమైన పేజీ రిఫరెన్స్‌లు",
        "pillar_3_desc": "ప్రతి మూలిక మరియు చిట్కాకు మూల గ్రంథం మరియు పేజీ నంబర్ అందించబడుతుంది.",
        "pillar_4_title": "పూర్తి డేటా గోప్యత",
        "pillar_4_desc": "మీ సంభాషణలు మీ ఖాతా లేదా బ్రౌజర్‌లోనే సురక్షితంగా ఉంటాయి.",
        "scriptures_badge": "జ్ఞాన భాండాగారం",
        "scriptures_title": "31 ప్రాచీన గ్రంథాల సమగ్ర సమాహారం",
        "scriptures_sub": "వందల సంవత్సరాల ప్రాచీన భారతీయ వైద్య విజ్ఞానం.",
        "faq_badge": "ప్రశ్నోత్తరాలు",
        "faq_title": "తరచుగా అడిగే ప్రశ్నలు",
        "faq_q1": "సుశ్రుత AI పూర్తిస్థాయి డాక్టర్‌కు ప్రత్యామ్నాయమా?",
        "faq_a1": "కాదు. ఇది ప్రామాణిక ఆయుర్వేద గ్రంథాల ఆధారిత సమాచార వేదిక. అత్యవసర పరిస్థితుల్లో అర్హత కలిగిన వైద్యులను సంప్రదించండి.",
        "faq_q2": "పుస్తక ఆధారాలు (Citations) ఎలా పనిచేస్తాయి?",
        "faq_a2": "సలహాలలో [1], [2] పై క్లిక్ చేసినప్పుడు సంబంధిత పుస్తకం పేరు మరియు శ్లోకం కనిపిస్తాయి.",
        "faq_q3": "నా ఆరోగ్య సమాచారం సురక్షితమేనా?",
        "faq_a3": "అవును. మీ చాట్ డేటా మీ ఖాతాలో మాత్రమే ప్రైవేట్‌గా నిల్వ చేయబడుతుంది.",
        "cta_banner_title": "ఆరోగ్యవంతమైన జీవనానికి సిద్ధమా?",
        "cta_banner_sub": "మీకు నచ్చిన భాషలో ప్రాచీన ఆయుర్వేద సలహాలను పొందండి.",
        "cta_banner_btn": "ఇప్పుడే సంప్రదించండి",
        "footer_privacy": "గోప్యతా విధానం",
        "footer_terms": "నిబంధనలు",
        "footer_disclaimer": "వైద్య నిరాకరణ",
        "footer_copy": "© 2026 సుశ్రుత AI. ప్రాచీన ఆయుర్వేద గ్రంథాల ఆధారిత విజ్ఞాన వేదిక.",
        "sidebar_home": "హోమ్ & సమాచారం",
        "sidebar_new_chat": "కొత్త సంప్రదింపు",
        "sidebar_history_title": "గత సంభాషణలు",
        "sidebar_clear_btn": "క్లియర్",
        "sidebar_quick_inquiries": "ముఖ్య అంశాలు",
        "doc_name": "శ్రీ ధన్వంతరి స్వామి",
        "doc_grounded": "31 ప్రాచీన ఆయుర్వేద గ్రంథాల ఆధారంగా",
        "header_home": "హోమ్",
        "welcome_title": "ఆయుర్వేద ఆరోగ్య సలహా కేంద్రం",
        "welcome_subtitle": "మీ ఆరోగ్య సమస్యలు, లక్షణాలు లేదా సందేహాలను ఇక్కడ అడగండి. చరక సంహిత, సుశ్రుత సంహిత, వనమూలికా వేదం ఆధారంగా మూల కారణాన్ని సరిచేసే చికిత్సలను అందిస్తాము.",
        "welcome_card1_title": "జీర్ణశక్తి & ఆమ దోషం",
        "welcome_card1_desc": "గ్యాస్, మలబద్ధకం మరియు అజీర్తికి సహజ సిద్ధమైన వంటింటి చిట్కాలు.",
        "welcome_card2_title": "రోగనిరోధక శక్తి & అలెర్జీలు",
        "welcome_card2_desc": "కఫ నివారణకు మరియు శ్వాస సంబంధిత సమస్యలకు మూలికా కషాయాలు.",
        "welcome_card3_title": "మానసిక ప్రశాంతత (మనస్సు)",
        "welcome_card3_desc": "ఒత్తిడి మరియు ఆందోళనను తగ్గించే మేధ్య రసాయనాలు & బ్రాహ్మి.",
        "welcome_card4_title": "చర్మ సౌందర్యం & రక్తం శుద్ధి",
        "welcome_card4_desc": "వేప, మంజిష్ట మరియు సుగంధ లేపనాలతో సహజ చర్మ కాంతి.",
        "input_warning": "సుశ్రుత AI ప్రాచీన ఆయుర్వేద గ్రంథాల సమాచార వేదిక. ముఖ్యమైన విషయాలను సరిచూసుకోగలరు."
    },
    "Hindi": {
        "tagline": "आयुर्वेदिक चिकित्सक आर.ए.जी (RAG)",
        "nav_how_it_works": "कार्यप्रणाली",
        "nav_pillars": "चिकित्सा सिद्धांत",
        "nav_scriptures": "31 ग्रंथ",
        "nav_faq": "अक्सर पूछे जाने वाले प्रश्न",
        "site_lang_label": "भाषा:",
        "nav_start_btn": "परामर्श शुरू करें",
        "nav_login": "साइन इन",
        "hero_badge": "<i class=\"fa-solid fa-sparkles\"></i> 5000 वर्षों का वैदिक ज्ञान &bull; 31 शास्त्रीय ग्रंथों पर आधारित",
        "hero_title_1": "प्राचीन आयुर्वेदिक चिकित्सा,",
        "hero_title_2": "न्यूरल आर्टिफिशियल इंटेलिजेंस द्वारा।",
        "hero_subtitle": "<strong>धन्वंतरि वैद्य</strong> से परामर्श लें — चरक, सुश्रुत, अष्टांग हृदय और पारंपरिक वेद ग्रंथों पर आधारित त्रिदोष निदान एवं घरेलू उपचार सटीक पुस्तक संदर्भों के साथ प्राप्त करें।",
        "hero_btn_consult": "निःशुल्क परामर्श शुरू करें",
        "hero_btn_rag": "कार्यप्रणाली जानें",
        "popular_inquiries": "लोकप्रिय स्वास्थ्य विषय (पूछने के लिए क्लिक करें):",
        "prompt_sinus_title": "साइनस और सिरदर्द",
        "prompt_sinus_desc": "भाप लेना, अणु तैल और कफ निवारण",
        "prompt_reflux_title": "एसिडिटी और पित्त दोष",
        "prompt_reflux_desc": "शीतल जड़ी-बूटियां, आंवला और अग्नि संतुलन",
        "prompt_joint_title": "जोड़ों का दर्द और वात",
        "prompt_joint_desc": "महानारायण तेल और गुग्गुलु काढ़ा",
        "prompt_hair_title": "बाल और त्वचा स्वास्थ्य",
        "prompt_hair_desc": "भृंगराज, ब्राह्मी और हर्बल हेयर टॉनिक",
        "stats_scriptures": "डिजिटल शास्त्रीय ग्रंथ",
        "stats_citations": "सटीक पुस्तक संदर्भ",
        "stats_languages": "समर्थित भाषाएँ",
        "stats_free": "निःशुल्क एवं सुरक्षित",
        "arch_badge": "आर्किटेक्चर",
        "arch_title": "सुश्रुत AI कैसे कार्य करता है?",
        "arch_sub": "वेक्टर सिमेंटिक खोज और न्यूरल AI चिकित्सक विश्लेषण का सटीक समन्वय।",
        "step_1_num": "चरण 1",
        "step_1_title": "31 शास्त्रीय ग्रंथ",
        "step_1_desc": "संस्कृत और तेलुगु आयुर्वेदिक ग्रंथों को खोज योग्य रूप में व्यवस्थित किया गया है।",
        "step_2_num": "चरण 2",
        "step_2_title": "पाइनकोन न्यूरल RAG",
        "step_2_desc": "आपके लक्षणों के आधार पर सबसे सटीक श्लोक और पृष्ठ तुरंत खोजे जाते हैं।",
        "step_3_num": "चरण 3",
        "step_3_title": "वैद्यकीय विश्लेषण",
        "step_3_desc": "दोष विश्लेषण, घरेलू सामग्री, मात्रा और सटीक संदर्भों के साथ समाधान दिया जाता है।",
        "pillars_badge": "सिद्धांत",
        "pillars_title": "मूल आयुर्वेदिक सिद्धांत",
        "pillars_sub": "लक्षणों को दबाना नहीं, बल्कि मूल कारण को दूर करना।",
        "pillar_1_title": "त्रिदोष मूल कारण निदान",
        "pillar_1_desc": "वात, पित्त और कफ के असंतुलन का परीक्षण कर सटीक उपचार।",
        "pillar_2_title": "सुलभ घरेलू औषधियां",
        "pillar_2_desc": "हल्दी, सोंठ, काली मिर्च, जीरा, घी और काढ़े से सुरक्षित उपचार।",
        "pillar_3_title": "सत्यापनीय पुस्तक संदर्भ",
        "pillar_3_desc": "प्रत्येक औषधि और नुस्खे के साथ मूल ग्रंथ और पृष्ठ संख्या उपलब्ध है।",
        "pillar_4_title": "पूर्ण डेटा गोपनीयता",
        "pillar_4_desc": "आपकी स्वास्थ्य चर्चा केवल आपके खाते में सुरक्षित रहती है।",
        "scriptures_badge": "ज्ञानकोष",
        "scriptures_title": "31 डिजिटल प्राचीन ग्रंथ",
        "scriptures_sub": "शताब्दियों की पारंपरिक भारतीय चिकित्सा धरोहर।",
        "faq_badge": "FAQ",
        "faq_title": "अक्सर पूछे जाने वाले प्रश्न",
        "faq_q1": "क्या सुश्रुत AI चिकित्सक का विकल्प है?",
        "faq_a1": "नहीं, यह एक शैक्षिक संदर्भ उपकरण है। आपातकालीन स्थिति में चिकित्सक से संपर्क करें।",
        "faq_q2": "पुस्तक संदर्भ (Citations) कैसे देखें?",
        "faq_a2": "[1], [2] पर क्लिक करके मूल पुस्तक का नाम और श्लोक देख सकते हैं।",
        "faq_q3": "क्या मेरा डेटा सुरक्षित है?",
        "faq_a3": "हाँ, आपकी बातचीत सुरक्षित रूप से एन्क्रिप्टेड रहती है।",
        "cta_banner_title": "आरोग्य जीवन की शुरुआत करें",
        "cta_banner_sub": "अपनी पसंदीदा भाषा में आयुर्वेदिक मार्गदर्शन प्राप्त करें।",
        "cta_banner_btn": "अभी परामर्श लें",
        "footer_privacy": "गोपनीयता नीति",
        "footer_terms": "सेवा शर्तें",
        "footer_disclaimer": "चिकित्सा अस्वीकरण",
        "footer_copy": "© 2026 सुश्रुत AI. पारंपरिक आयुर्वेदिक ज्ञान पर आधारित।",
        "sidebar_home": "होम और विवरण",
        "sidebar_new_chat": "नया परामर्श",
        "sidebar_history_title": "परामर्श इतिहास",
        "sidebar_clear_btn": "साफ़ करें",
        "sidebar_quick_inquiries": "त्वरित विषय",
        "doc_name": "धन्वंतरि वैद्य",
        "doc_grounded": "31 आयुर्वेदिक ग्रंथों पर आधारित",
        "header_home": "होम",
        "welcome_title": "आयुर्वेदिक स्वास्थ्य परामर्श",
        "welcome_subtitle": "अपने स्वास्थ्य लक्षणों या प्रश्नों को यहाँ पूछें। चरक, सुश्रुत और प्राचीन संहिताओं के आधार पर सटीक उपचार पाएं।",
        "welcome_card1_title": "पाचन अग्नि और आम दोष",
        "welcome_card1_desc": "गैस, कब्ज और अपच के लिए प्राकृतिक घरेलू उपाय।",
        "welcome_card2_title": "प्रतिरोधक क्षमता और एलर्जी",
        "welcome_card2_desc": "कफ निवारण और श्वसन तंत्र के लिए हर्बल काढ़ा।",
        "welcome_card3_title": "मानसिक शांति (मानस)",
        "welcome_card3_desc": "तनाव और अनिद्रा कम करने वाली मेध्य औषधियां।",
        "welcome_card4_title": "त्वचा और रक्त शोधक",
        "welcome_card4_desc": "नीम, मंजिष्ठा और प्राकृतिक उबटन से त्वचा की चमक।",
        "input_warning": "सुश्रुत AI प्राचीन आयुर्वेदिक संहिताओं पर आधारित है। महत्वपूर्ण नुस्खों को सत्यापित करें।"
    },
    "Sanskrit": {
        "tagline": "आयुर्वेद वैद्यक RAG तन्त्रम्",
        "nav_how_it_works": "कार्यविधिः",
        "nav_pillars": "चिकित्सा सूत्राणि",
        "nav_scriptures": "३१ ग्रन्थाः",
        "nav_faq": "प्रश्नोत्तराणि",
        "site_lang_label": "भाषा:",
        "nav_start_btn": "परामर्शं प्रारभताम्",
        "nav_login": "प्रवेशः",
        "hero_badge": "<i class=\"fa-solid fa-sparkles\"></i> ५००० वर्षाणां वैदिक ज्ञानम् &bull; ३१ शास्त्रीय ग्रन्थाः",
        "hero_title_1": "पुरातन आयुर्वेद चिकित्सा,",
        "hero_title_2": "कृत्रिम प्रज्ञा (AI) साहाय्येन।",
        "hero_subtitle": "<strong>भगवान् धन्वन्तरिः</strong> प्रति परामर्शं प्राप्नुवन्तु — चरक-सुश्रुत-अष्टाङ्गहृदयादि ग्रन्थैः सह त्रिदोष शान्ति उपायं ग्रन्थ संदर्भैः सह प्राप्नुवन्तु।",
        "hero_btn_consult": "निःशुल्क परामर्शं प्रारभताम्",
        "hero_btn_rag": "कार्यविधिं पश्यन्तु",
        "popular_inquiries": "मुख्याः विषयाः:",
        "prompt_sinus_title": "प्रतिश्यायः शिरोरोगश्च",
        "prompt_sinus_desc": "वाष्पसेदः, अणुतैलं कफप्रशमनं च",
        "prompt_reflux_title": "अम्लपित्तं पित्तदोषश्च",
        "prompt_reflux_desc": "शीतल द्रव्याणि, आमलकी दीपनीय गणाः",
        "prompt_joint_title": "सन्धिवातम्",
        "prompt_joint_desc": "महानारायण तैलं गुग्गुलु क्वाथश्च",
        "prompt_hair_title": "केश केशाग्र स्वास्थ्यम्",
        "prompt_hair_desc": "भृङ्गराजः, ब्राह्मी रसायनं च",
        "stats_scriptures": "शास्त्रीय ग्रन्थाः",
        "stats_citations": "सत्य ग्रन्थ प्रमाणानि",
        "stats_languages": "उपलब्ध भाषाः",
        "stats_free": "निःशुल्कं सुरक्षितं च",
        "arch_badge": "संरचना",
        "arch_title": "सुश्रुत AI कार्यपद्धतिः",
        "arch_sub": "शास्त्रोक्त श्लोकानां अन्वेषणं वैद्यकीय परामर्शश्च।",
        "step_1_num": "सोपानम् १",
        "step_1_title": "३१ ग्रन्थाः",
        "step_1_desc": "संस्कृत-तेलुगु आयुर्वेद संहितानां डिजिटलीकरणम्।",
        "step_2_num": "सोपानम् २",
        "step_2_title": "पाइनकोन న్యూరల్ RAG",
        "step_2_desc": "लक्षणानुसारेण श्लोक अन्वेषणम्।",
        "step_3_num": "सोपानम् ३",
        "step_3_title": "धन्वन्तरि विश्लेषणम्",
        "step_3_desc": "दोष विश्लेषणम्, औषध मात्रा, संदर्भसहित चिकित्सा।",
        "pillars_badge": "सूत्राणि",
        "pillars_title": "आयुर्वेद मूल सूत्राणि",
        "pillars_sub": "दोष धातुमला मूलं हि शरीरम्।",
        "pillar_1_title": "त्रिदोष निदानम्",
        "pillar_1_desc": "वात पित्त कफ वैषम्य परीक्षणम्।",
        "pillar_2_title": "सुलभ गृहोपचाराः",
        "pillar_2_desc": "हरिद्रा, शुण्ठी, मरीचं, घृतं क्वाथाश्च।",
        "pillar_3_title": "प्रमाणानि",
        "pillar_3_desc": "सर्वोपचाराणां ग्रन्थ पृष्ठ संख्या निर्देशः।",
        "pillar_4_title": "गोपनीयता",
        "pillar_4_desc": "भवतां विवरणं भवत्सु एव सुरक्षितम्।",
        "scriptures_badge": "ज्ञानकोषः",
        "scriptures_title": "३१ पुरातन ग्रन्थाः",
        "scriptures_sub": "परम्परागत भारतीय चिकित्सा विद्या।",
        "faq_badge": "FAQ",
        "faq_title": "प्रश्नोत्तराणि",
        "faq_q1": "किं सुश्रुत AI साक्षात् वैद्यः?",
        "faq_a1": "न, एतत् ज्ञानवर्धनाय शास्त्रोक्त साधनम्।",
        "faq_q2": "प्रमाणानि कथं द्रष्टव्यानि?",
        "faq_a2": "[1], [2] उपरि क्लिष्ट्वा मूल श्लोकान् पश्यन्तु।",
        "faq_q3": "किं मम विवरणं सुरक्षितम्?",
        "faq_a3": "आम्, सर्वं भवतां ब्राउजर् मध्ये एव वर्तते।",
        "cta_banner_title": "आरोग्य जीवनं कामयेत",
        "cta_banner_sub": "स्वभाषायां आयुर्वेद परामर्शं स्वीकुर्वन्तु।",
        "cta_banner_btn": "परामर्शं स्वीकुर्वन्तु",
        "footer_privacy": "गोपनीयता नीतिः",
        "footer_terms": "नियमाः",
        "footer_disclaimer": "चिकित्सा अस्वीकरणम्",
        "footer_copy": "© २०२६ सुश्रुत AI. सर्वे भवन्तु सुखिनः सर्वे सन्तु निरामयाः।",
        "sidebar_home": "गृहम्",
        "sidebar_new_chat": "नवीन परामर्शः",
        "sidebar_history_title": "इतिहासः",
        "sidebar_clear_btn": "निष्कासयतु",
        "sidebar_quick_inquiries": "मुख्याः विषयाः",
        "doc_name": "भगवान् धन्वन्तरिः",
        "doc_grounded": "३१ आयुर्वेद ग्रन्थेषु प्रतिष्ठितः",
        "header_home": "गृहम्",
        "welcome_title": "आयुर्वेद स्वास्थ्य परामर्शः",
        "welcome_subtitle": "भवतां लक्षणानि अत्र पृच्छन्तु। संहिताधारेण समाधानं प्राप्स्यथ।",
        "welcome_card1_title": "जठराग्निः आमदोषश्च",
        "welcome_card1_desc": "अजीर्ण-विबन्ध निवारणाय गृहोपचाराः।",
        "welcome_card2_title": "व्याधिक्षमत्वम्",
        "welcome_card2_desc": "कफ प्रशमनाय क्वाथ द्रव्याणि।",
        "welcome_card3_title": "मानसिक स्वास्थ्यम्",
        "welcome_card3_desc": "मेध्य रसायनानि ब्राह्मी च।",
        "welcome_card4_title": "त्वचा रक्त विशुद्धिः",
        "welcome_card4_desc": "निम्ब-मञ्जिष्ठा लेपाः।",
        "input_warning": "सुश्रुत AI शास्त्रोक्त संदर्भ साधनम्।"
    }
};

// Main Views
const landingView = document.getElementById("landing-view");
const chatAppView = document.getElementById("chat-app-view");

// Navigation & Trigger Buttons
const btnLandingStart = document.getElementById("btn-landing-start");
const btnHeroConsult = document.getElementById("btn-hero-consult");
const btnBottomStart = document.getElementById("btn-bottom-start");
const btnReturnHome = document.getElementById("btn-return-home");
const btnHeaderHome = document.getElementById("btn-header-home");

// Header Website UI Language Dropdowns
const landingSiteLang = document.getElementById("landing-site-language");
const chatSiteLang = document.getElementById("chat-site-language");

// In-Chatbox Response Language Dropdown
const chatResponseLang = document.getElementById("chat-response-language");

// Sidebar & Chat Elements
const sidebar = document.getElementById("sidebar");
const sidebarBackdrop = document.getElementById("sidebar-backdrop");
const btnToggleSidebar = document.getElementById("btn-toggle-sidebar");
const btnCollapseSidebar = document.getElementById("btn-collapse-sidebar");

const chatMessages = document.getElementById("chat-messages");
const welcomeScreen = document.getElementById("welcome-screen");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const btnSend = document.getElementById("btn-send");
const checkboxRerank = document.getElementById("checkbox-rerank");
const btnNewChat = document.getElementById("btn-new-chat");
const btnClearChat = document.getElementById("btn-clear-chat");
const historyList = document.getElementById("history-list");
const btnClearAllHistory = document.getElementById("btn-clear-all-history");
const corpusBadge = document.getElementById("corpus-status-badge");

// Auth Elements
const authModal = document.getElementById("auth-modal");
const btnCloseAuth = document.getElementById("btn-close-auth");
const tabLogin = document.getElementById("tab-login");
const tabSignup = document.getElementById("tab-signup");
const loginForm = document.getElementById("login-form");
const signupForm = document.getElementById("signup-form");
const loginError = document.getElementById("login-error");
const signupError = document.getElementById("signup-error");
const btnLandingLogin = document.getElementById("btn-landing-login");
const btnChatLogin = document.getElementById("btn-chat-login");
const landingAuthContainer = document.getElementById("landing-auth-container");
const chatAuthContainer = document.getElementById("chat-auth-container");

// Settings Modal Elements
const btnSettingsModal = document.getElementById("btn-settings-modal");
const settingsModal = document.getElementById("settings-modal");
const btnCloseSettings = document.getElementById("btn-close-settings");
const btnCancelSettings = document.getElementById("btn-cancel-settings");
const settingsForm = document.getElementById("settings-form");
const apiBaseUrlInput = document.getElementById("api-base-url");
const pineconeKeyInput = document.getElementById("pinecone-api-key");
const pineconeIndexInput = document.getElementById("pinecone-index-name");
const geminiKeyInput = document.getElementById("gemini-api-key");

// Legal Modal Elements
const legalModal = document.getElementById("legal-modal");
const legalModalTitle = document.getElementById("legal-modal-title");
const legalModalContent = document.getElementById("legal-modal-content");
const btnCloseLegal = document.getElementById("btn-close-legal");
const btnDismissLegal = document.getElementById("btn-dismiss-legal");
const btnFooterPrivacy = document.getElementById("btn-footer-privacy");
const btnFooterTerms = document.getElementById("btn-footer-terms");
const btnFooterDisclaimer = document.getElementById("btn-footer-disclaimer");

// Popover Elements
const citationPopover = document.getElementById("citation-popover");
const popoverBookTitle = document.getElementById("popover-book-title");
const popoverPage = document.getElementById("popover-page");
const popoverExcerpt = document.getElementById("popover-excerpt");

// Initialize on DOM Ready
document.addEventListener("DOMContentLoaded", async () => {
    marked.setOptions({ breaks: true, gfm: true });
    
    // 1. Restore & Apply Website UI Language
    const savedSiteLang = localStorage.getItem(SITE_LANG_STORAGE_KEY) || "English";
    if (landingSiteLang) landingSiteLang.value = savedSiteLang;
    if (chatSiteLang) chatSiteLang.value = savedSiteLang;
    applySiteLanguage(savedSiteLang);

    // 2. Restore Chat Response Language in Chatbox
    const savedResponseLang = localStorage.getItem(RESPONSE_LANG_STORAGE_KEY) || "English";
    if (chatResponseLang) chatResponseLang.value = savedResponseLang;
    
    // 3. Initialize Auth State
    await checkAuthState();

    // 4. Load Chat Sessions
    await loadChatSessions();
    setupEventListeners();
    checkBackendConfig();
});

// Event Listeners
function setupEventListeners() {
    // 1. Website UI Language Change (Header Dropdowns)
    if (landingSiteLang) {
        landingSiteLang.addEventListener("change", () => {
            const lang = landingSiteLang.value;
            localStorage.setItem(SITE_LANG_STORAGE_KEY, lang);
            if (chatSiteLang) chatSiteLang.value = lang;
            applySiteLanguage(lang);
        });
    }

    if (chatSiteLang) {
        chatSiteLang.addEventListener("change", () => {
            const lang = chatSiteLang.value;
            localStorage.setItem(SITE_LANG_STORAGE_KEY, lang);
            if (landingSiteLang) landingSiteLang.value = lang;
            applySiteLanguage(lang);
        });
    }

    // 2. Chatbox Response Language Change
    if (chatResponseLang) {
        chatResponseLang.addEventListener("change", () => {
            localStorage.setItem(RESPONSE_LANG_STORAGE_KEY, chatResponseLang.value);
        });
    }

    // 3. Landing Page to Chat View Transitions
    const startConsultationButtons = [btnLandingStart, btnHeroConsult, btnBottomStart];
    startConsultationButtons.forEach(btn => {
        if (btn) {
            btn.addEventListener("click", () => openChatView());
        }
    });

    // 4. Return to Landing Page
    if (btnReturnHome) btnReturnHome.addEventListener("click", () => openLandingView());
    if (btnHeaderHome) btnHeaderHome.addEventListener("click", () => openLandingView());

    // 5. Sidebar Collapse / Expand (mobile drawer + desktop + backdrop)
    const isMobile = () => window.matchMedia("(max-width: 768px)").matches;

    function openSidebar() {
        if (isMobile()) {
            sidebar.classList.add("mobile-open");
        } else {
            sidebar.classList.remove("collapsed");
        }
        sidebarBackdrop?.classList.remove("hidden");
    }

    function closeSidebar() {
        if (isMobile()) {
            sidebar.classList.remove("mobile-open");
        } else {
            sidebar.classList.add("collapsed");
        }
        sidebarBackdrop?.classList.add("hidden");
    }

    if (btnToggleSidebar) {
        btnToggleSidebar.addEventListener("click", () => {
            const isOpen = isMobile()
                ? sidebar.classList.contains("mobile-open")
                : !sidebar.classList.contains("collapsed");
            isOpen ? closeSidebar() : openSidebar();
        });
    }

    if (btnCollapseSidebar) {
        btnCollapseSidebar.addEventListener("click", closeSidebar);
    }

    if (sidebarBackdrop) {
        sidebarBackdrop.addEventListener("click", closeSidebar);
    }

    // 6. Chat Form Submission
    chatForm.addEventListener("submit", handleSubmit);

    // 7. Textarea Auto-expand & Enter to Send
    chatInput.addEventListener("input", () => {
        chatInput.style.height = "auto";
        chatInput.style.height = Math.min(chatInput.scrollHeight, 180) + "px";
    });

    chatInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            if (!isGenerating && chatInput.value.trim().length > 0) {
                chatForm.dispatchEvent(new Event("submit"));
            }
        }
    });

    // 8. New Chat & Clear Current
    btnNewChat.addEventListener("click", () => startNewSession());
    btnClearChat.addEventListener("click", () => clearCurrentSession());
    btnClearAllHistory.addEventListener("click", clearAllHistory);

    // 9. Quick Prompt Cards
    document.querySelectorAll("[data-prompt]").forEach(el => {
        el.addEventListener("click", () => {
            const promptText = el.getAttribute("data-prompt");
            if (promptText) {
                openChatView();
                chatInput.value = promptText;
                chatInput.dispatchEvent(new Event("input"));
                chatForm.dispatchEvent(new Event("submit"));
            }
        });
    });

    // 10. Auth Modal Listeners
    if (btnLandingLogin) btnLandingLogin.addEventListener("click", () => openAuthModal());
    if (btnChatLogin) btnChatLogin.addEventListener("click", () => openAuthModal());
    if (btnCloseAuth) btnCloseAuth.addEventListener("click", () => authModal.classList.add("hidden"));

    if (tabLogin && tabSignup) {
        tabLogin.addEventListener("click", () => {
            tabLogin.classList.add("active");
            tabSignup.classList.remove("active");
            loginForm.classList.remove("hidden");
            signupForm.classList.add("hidden");
        });
        tabSignup.addEventListener("click", () => {
            tabSignup.classList.add("active");
            tabLogin.classList.remove("active");
            signupForm.classList.remove("hidden");
            loginForm.classList.add("hidden");
        });
    }

    if (loginForm) loginForm.addEventListener("submit", handleLogin);
    if (signupForm) signupForm.addEventListener("submit", handleSignup);

    // 11. Settings Modal
    btnSettingsModal.addEventListener("click", () => settingsModal.classList.remove("hidden"));
    btnCloseSettings.addEventListener("click", () => settingsModal.classList.add("hidden"));
    btnCancelSettings.addEventListener("click", () => settingsModal.classList.add("hidden"));
    settingsForm.addEventListener("submit", saveSettings);

    // 12. Legal Modals from Footer
    if (btnFooterPrivacy) btnFooterPrivacy.addEventListener("click", () => openLegalModal("privacy"));
    if (btnFooterTerms) btnFooterTerms.addEventListener("click", () => openLegalModal("terms"));
    if (btnFooterDisclaimer) btnFooterDisclaimer.addEventListener("click", () => openLegalModal("disclaimer"));
    btnCloseLegal.addEventListener("click", () => legalModal.classList.add("hidden"));
    btnDismissLegal.addEventListener("click", () => legalModal.classList.add("hidden"));

    // 13. Global Click to close Popovers
    document.addEventListener("click", (e) => {
        if (!e.target.closest(".inline-citation") && !e.target.closest(".source-chip")) {
            citationPopover.classList.add("hidden");
        }
    });
}

// =========================================================
// AUTHENTICATION & USER MANAGEMENT
// =========================================================
async function checkAuthState() {
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    if (!token) {
        currentUser = null;
        renderAuthUI();
        return;
    }

    try {
        const apiBase = getApiBaseUrl();
        const res = await fetch(apiBase + "/api/auth/me", {
            headers: { "Authorization": `Bearer ${token}` }
        });
        if (res.ok) {
            const data = await res.json();
            currentUser = data.user;
            localStorage.setItem(LOCAL_USER_STORAGE_KEY, JSON.stringify(currentUser));
        } else if (res.status === 401 || res.status === 403) {
            localStorage.removeItem(AUTH_TOKEN_KEY);
            localStorage.removeItem(LOCAL_USER_STORAGE_KEY);
            currentUser = null;
        } else {
            // Restore from local user cache if server responded with non-auth error (e.g. 404 on static deploy)
            const cached = localStorage.getItem(LOCAL_USER_STORAGE_KEY);
            if (cached) currentUser = JSON.parse(cached);
        }
    } catch (e) {
        // Offline / Netlify static fallback
        const cached = localStorage.getItem(LOCAL_USER_STORAGE_KEY);
        if (cached) {
            try {
                currentUser = JSON.parse(cached);
            } catch (err) {
                currentUser = null;
            }
        }
        console.warn("Auth check using offline/local profile state:", e);
    }
    renderAuthUI();
}

function renderAuthUI() {
    const containers = [landingAuthContainer, chatAuthContainer];
    containers.forEach(c => {
        if (!c) return;
        if (currentUser) {
            c.innerHTML = `
                <div class="auth-user-pill">
                    <i class="fa-solid fa-user-circle"></i>
                    <span class="auth-user-name" title="${escapeHTML(currentUser.full_name)}">${escapeHTML(currentUser.full_name)}</span>
                    <button class="btn-auth-logout" title="Log Out"><i class="fa-solid fa-right-from-bracket"></i></button>
                </div>
            `;
            c.querySelector(".btn-auth-logout").addEventListener("click", handleLogout);
        } else {
            c.innerHTML = `
                <button class="btn-auth-outline" title="Login to save consultations">
                    <i class="fa-solid fa-user"></i>
                    <span>Sign In</span>
                </button>
            `;
            c.querySelector(".btn-auth-outline").addEventListener("click", openAuthModal);
        }
    });
}

function openAuthModal() {
    authModal.classList.remove("hidden");
    loginError.classList.add("hidden");
    signupError.classList.add("hidden");
}

async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById("login-email").value.trim();
    const password = document.getElementById("login-password").value.trim();
    loginError.classList.add("hidden");

    const apiBase = getApiBaseUrl();

    try {
        const res = await fetch(apiBase + "/api/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });
        
        if (res.ok) {
            const data = await res.json();
            localStorage.setItem(AUTH_TOKEN_KEY, data.token);
            currentUser = data.user;
            localStorage.setItem(LOCAL_USER_STORAGE_KEY, JSON.stringify(currentUser));
            authModal.classList.add("hidden");
            renderAuthUI();
            await loadChatSessions();
            return;
        } else if (res.status === 400 || res.status === 401 || res.status === 403 || res.status === 422) {
            const data = await res.json().catch(() => ({}));
            loginError.textContent = data.detail || "Invalid email or password.";
            loginError.classList.remove("hidden");
            return;
        }
    } catch (err) {
        console.warn("Backend auth unreachable, activating client session:", err);
    }

    // Client-side / Offline fallback for Netlify static preview
    const fallbackUser = {
        email: email,
        full_name: email.split("@")[0].replace(/[._-]/g, " ").replace(/\b\w/g, l => l.toUpperCase()) || "Patient"
    };
    currentUser = fallbackUser;
    localStorage.setItem(AUTH_TOKEN_KEY, "local_auth_" + Date.now());
    localStorage.setItem(LOCAL_USER_STORAGE_KEY, JSON.stringify(currentUser));
    authModal.classList.add("hidden");
    renderAuthUI();
    await loadChatSessions();
}

async function handleSignup(e) {
    e.preventDefault();
    const full_name = document.getElementById("signup-name").value.trim();
    const email = document.getElementById("signup-email").value.trim();
    const password = document.getElementById("signup-password").value.trim();
    signupError.classList.add("hidden");

    const apiBase = getApiBaseUrl();

    try {
        const res = await fetch(apiBase + "/api/auth/signup", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ full_name, email, password })
        });

        if (res.ok) {
            const data = await res.json();
            localStorage.setItem(AUTH_TOKEN_KEY, data.token);
            currentUser = data.user;
            localStorage.setItem(LOCAL_USER_STORAGE_KEY, JSON.stringify(currentUser));
            authModal.classList.add("hidden");
            renderAuthUI();
            await loadChatSessions();
            return;
        } else if (res.status === 400 || res.status === 409 || res.status === 422) {
            const data = await res.json().catch(() => ({}));
            signupError.textContent = data.detail || "Registration failed. Email may already be registered.";
            signupError.classList.remove("hidden");
            return;
        }
    } catch (err) {
        console.warn("Backend signup unreachable, activating client session:", err);
    }

    // Client-side / Offline fallback for Netlify static preview
    const fallbackUser = {
        email: email,
        full_name: full_name || "Patient"
    };
    currentUser = fallbackUser;
    localStorage.setItem(AUTH_TOKEN_KEY, "local_auth_" + Date.now());
    localStorage.setItem(LOCAL_USER_STORAGE_KEY, JSON.stringify(currentUser));
    authModal.classList.add("hidden");
    renderAuthUI();
    await loadChatSessions();
}

async function handleLogout() {
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    const apiBase = getApiBaseUrl();
    if (token) {
        try {
            await fetch(apiBase + "/api/auth/logout", {
                method: "POST",
                headers: { "Authorization": `Bearer ${token}` }
            });
        } catch (e) {}
    }
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(LOCAL_USER_STORAGE_KEY);
    currentUser = null;
    renderAuthUI();
    loadChatSessions();
}

// =========================================================
// I18N WEBSITE UI LANGUAGE
// =========================================================
function applySiteLanguage(lang) {
    const dict = I18N_DICTIONARY[lang] || I18N_DICTIONARY["English"];
    document.querySelectorAll("[data-i18n]").forEach(el => {
        const key = el.getAttribute("data-i18n");
        if (dict[key]) {
            el.innerHTML = dict[key];
        }
    });
}

function openChatView() {
    landingView.classList.add("hidden");
    chatAppView.classList.remove("hidden");
    window.scrollTo({ top: 0, behavior: 'instant' });
    chatInput.focus();
}

function openLandingView() {
    chatAppView.classList.add("hidden");
    landingView.classList.remove("hidden");
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// =========================================================
// CHAT SESSION & DATABASE HISTORY MANAGEMENT
// =========================================================
async function loadChatSessions() {
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    const apiBase = getApiBaseUrl();

    if (currentUser && token) {
        // Load sessions from database
        try {
            const res = await fetch(apiBase + "/api/chat/sessions", {
                headers: { "Authorization": `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                chatSessions = data.sessions.map(s => ({
                    id: s.id,
                    title: s.title,
                    messages: [],
                    timestamp: s.created_at
                }));
            }
        } catch (e) {
            console.warn("DB session fetch error, using local:", e);
            // Fallback to local storage
            try {
                const stored = localStorage.getItem(SESSIONS_STORAGE_KEY);
                chatSessions = stored ? JSON.parse(stored) : [];
            } catch (err) {
                chatSessions = [];
            }
        }
    } else {
        // Load sessions from local storage
        try {
            const stored = localStorage.getItem(SESSIONS_STORAGE_KEY);
            chatSessions = stored ? JSON.parse(stored) : [];
        } catch (e) {
            chatSessions = [];
        }
    }

    if (chatSessions.length > 0) {
        await loadSession(chatSessions[0].id);
    } else {
        await startNewSession();
    }
    renderHistorySidebar();
}

function saveChatSessions() {
    try {
        localStorage.setItem(SESSIONS_STORAGE_KEY, JSON.stringify(chatSessions));
    } catch (e) {
        console.error("Storage error:", e);
    }
    renderHistorySidebar();
}

async function startNewSession() {
    currentSessionId = "ses_" + Date.now();
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    const apiBase = getApiBaseUrl();

    if (currentUser && token) {
        try {
            const res = await fetch(apiBase + "/api/chat/sessions", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({ id: currentSessionId, title: "New Consultation" })
            });
            if (res.ok) {
                const data = await res.json();
                currentSessionId = data.session.id;
            }
        } catch (e) {}
    }

    const newSession = {
        id: currentSessionId,
        title: "New Consultation",
        messages: [],
        timestamp: new Date().toISOString()
    };
    chatSessions.unshift(newSession);
    saveChatSessions();
    await loadSession(currentSessionId);
}

async function loadSession(sessionId) {
    currentSessionId = sessionId;
    let session = chatSessions.find(s => s.id === sessionId);
    if (!session) return;

    chatMessages.innerHTML = "";
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    const apiBase = getApiBaseUrl();

    // If logged in and messages not yet fetched, fetch from DB
    if (currentUser && token && session.messages.length === 0) {
        try {
            const res = await fetch(`${apiBase}/api/chat/sessions/${sessionId}/messages`, {
                headers: { "Authorization": `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                session.messages = data.messages || [];
            }
        } catch (e) {}
    }

    if (session.messages.length === 0) {
        chatMessages.appendChild(welcomeScreen);
        welcomeScreen.classList.remove("hidden");
    } else {
        welcomeScreen.classList.add("hidden");
        session.messages.forEach(msg => {
            appendMessage(msg.role === "user" ? "user" : "doctor", msg.content, msg.sources || [], false);
        });
    }
    renderHistorySidebar();
    scrollToBottom();
}

function clearCurrentSession() {
    const session = chatSessions.find(s => s.id === currentSessionId);
    if (session) {
        session.messages = [];
        session.title = "New Consultation";
        saveChatSessions();
        loadSession(currentSessionId);
    }
}

async function clearAllHistory() {
    if (confirm("Are you sure you want to clear consultation history?")) {
        const token = localStorage.getItem(AUTH_TOKEN_KEY);
        const apiBase = getApiBaseUrl();
        if (currentUser && token) {
            for (const s of chatSessions) {
                try {
                    await fetch(`${apiBase}/api/chat/sessions/${s.id}`, {
                        method: "DELETE",
                        headers: { "Authorization": `Bearer ${token}` }
                    });
                } catch (e) {}
            }
        }
        chatSessions = [];
        localStorage.removeItem(SESSIONS_STORAGE_KEY);
        await startNewSession();
    }
}

function renderHistorySidebar() {
    historyList.innerHTML = "";
    chatSessions.forEach(session => {
        const item = document.createElement("div");
        item.className = `history-item ${session.id === currentSessionId ? 'active' : ''}`;
        item.innerHTML = `
            <span class="history-title" title="${escapeHTML(session.title)}"><i class="fa-regular fa-message"></i> ${escapeHTML(session.title)}</span>
            <button class="btn-delete-session" title="Delete consultation"><i class="fa-solid fa-trash-can"></i></button>
        `;

        item.querySelector(".history-title").addEventListener("click", () => {
            openChatView();
            loadSession(session.id);
        });

        item.querySelector(".btn-delete-session").addEventListener("click", async (e) => {
            e.stopPropagation();
            const token = localStorage.getItem(AUTH_TOKEN_KEY);
            const apiBase = getApiBaseUrl();
            if (currentUser && token) {
                try {
                    await fetch(`${apiBase}/api/chat/sessions/${session.id}`, {
                        method: "DELETE",
                        headers: { "Authorization": `Bearer ${token}` }
                    });
                } catch (err) {}
            }
            chatSessions = chatSessions.filter(s => s.id !== session.id);
            saveChatSessions();
            if (currentSessionId === session.id) {
                if (chatSessions.length > 0) loadSession(chatSessions[0].id);
                else startNewSession();
            }
        });

        historyList.appendChild(item);
    });
}

// Backend Configuration Check
async function checkBackendConfig() {
    if (apiBaseUrlInput) {
        apiBaseUrlInput.value = localStorage.getItem(API_BASE_STORAGE_KEY) || "";
    }
    const apiBase = getApiBaseUrl();
    try {
        const res = await fetch(apiBase + "/api/config-status");
        const data = await res.json();
        if (data.configured) {
            pineconeKeyInput.placeholder = "••••••••••••••••••••••••••••••••";
            geminiKeyInput.placeholder = "••••••••••••••••••••••••••••••••";
            pineconeIndexInput.value = data.index_name || "ayurveda-index";
        }
        
        const statsRes = await fetch(apiBase + "/api/index-stats");
        const statsData = await statsRes.json();
        if (statsData.exists && statsData.total_vector_count > 0) {
            corpusBadge.innerHTML = `<i class="fa-solid fa-check"></i> <span>${statsData.total_vector_count.toLocaleString()} Chunks Active</span>`;
        }
    } catch (err) {
        console.warn("Config check notice:", err);
    }
}

// Save Settings
async function saveSettings(e) {
    e.preventDefault();
    if (apiBaseUrlInput) {
        const baseVal = apiBaseUrlInput.value.trim();
        if (baseVal) {
            localStorage.setItem(API_BASE_STORAGE_KEY, baseVal);
        } else {
            localStorage.removeItem(API_BASE_STORAGE_KEY);
        }
    }

    const payload = {
        pinecone_api_key: pineconeKeyInput.value.trim() || undefined,
        pinecone_index_name: pineconeIndexInput.value.trim() || "ayurveda-index",
        gemini_api_key: geminiKeyInput.value.trim() || undefined
    };

    const apiBase = getApiBaseUrl();
    try {
        const res = await fetch(apiBase + "/api/config", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            alert("Settings saved successfully.");
            settingsModal.classList.add("hidden");
            checkBackendConfig();
        } else {
            const err = await res.json().catch(() => ({}));
            alert("Error: " + (err.detail || "Server error"));
        }
    } catch (err) {
        alert("Configuration saved locally in browser.");
        settingsModal.classList.add("hidden");
    }
}

// =========================================================
// REAL-TIME STREAMING CONSULTATION HANDLER
// =========================================================
async function handleSubmit(e) {
    e.preventDefault();
    const userText = chatInput.value.trim();
    if (!userText || isGenerating) return;

    welcomeScreen.classList.add("hidden");

    let session = chatSessions.find(s => s.id === currentSessionId);
    if (!session) {
        await startNewSession();
        session = chatSessions.find(s => s.id === currentSessionId);
    }

    if (session.messages.length === 0) {
        session.title = userText.length > 26 ? userText.substring(0, 24) + "..." : userText;
    }

    session.messages.push({ role: "user", content: userText });
    appendMessage("user", userText);
    saveChatSessions();

    chatInput.value = "";
    chatInput.style.height = "auto";
    isGenerating = true;
    btnSend.disabled = true;

    // Create live doctor bubble with cursor
    const doctorRow = document.createElement("div");
    doctorRow.className = "message-row doctor";
    doctorRow.innerHTML = `
        <div class="message-avatar" title="Sage Dhanvantari">
            <i class="fa-solid fa-leaf"></i>
        </div>
        <div class="message-bubble">
            <div class="sources-placeholder"></div>
            <div class="markdown-body">
                <span class="streaming-text"></span><span class="streaming-cursor"></span>
            </div>
        </div>
    `;
    chatMessages.appendChild(doctorRow);
    scrollToBottom();

    const sourcesPlaceholder = doctorRow.querySelector(".sources-placeholder");
    const streamingTextEl = doctorRow.querySelector(".streaming-text");
    const cursorEl = doctorRow.querySelector(".streaming-cursor");
    const markdownBodyEl = doctorRow.querySelector(".markdown-body");

    const chosenResponseLang = chatResponseLang ? chatResponseLang.value : "English";
    const token = localStorage.getItem(AUTH_TOKEN_KEY);

    const headers = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;

    let accumulatedText = "";
    let streamSources = [];

    const apiBase = getApiBaseUrl();
    try {
        const response = await fetch(apiBase + "/api/chat/stream", {
            method: "POST",
            headers: headers,
            body: JSON.stringify({
                messages: session.messages,
                session_id: session.id,
                language: chosenResponseLang,
                rerank: checkboxRerank.checked
            })
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.detail || "Failed to start streaming consultation.");
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let buffer = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split("\n\n");
            buffer = lines.pop() || "";

            for (const line of lines) {
                if (line.startsWith("data: ")) {
                    try {
                        const event = JSON.parse(line.substring(6));
                        
                        if (event.type === "sources" && event.sources) {
                            streamSources = event.sources;
                            if (streamSources.length > 0) {
                                sourcesPlaceholder.innerHTML = renderSourcesTray(streamSources);
                                attachCitationListeners(doctorRow, streamSources);
                            }
                        } else if (event.type === "token" && event.chunk) {
                            accumulatedText += event.chunk;
                            streamingTextEl.innerHTML = formatMessageWithCitations(accumulatedText, streamSources);
                            attachCitationListeners(doctorRow, streamSources);
                            scrollToBottom();
                        } else if (event.type === "done") {
                            accumulatedText = event.reply || accumulatedText;
                        } else if (event.type === "error") {
                            throw new Error(event.error);
                        }
                    } catch (parseErr) {
                        console.warn("SSE parse error:", parseErr);
                    }
                }
            }
        }

        // Finalize message rendering
        cursorEl.remove();
        markdownBodyEl.innerHTML = formatMessageWithCitations(accumulatedText, streamSources);
        attachCitationListeners(doctorRow, streamSources);

        session.messages.push({ role: "model", content: accumulatedText, sources: streamSources });
        saveChatSessions();

    } catch (err) {
        cursorEl.remove();
        streamingTextEl.innerHTML = `<span style="color: #fca5a5;"><strong>Consultation Notice:</strong> ${escapeHTML(err.message || "Connection error during consultation stream.")}</span>`;
    } finally {
        isGenerating = false;
        btnSend.disabled = false;
        scrollToBottom();
    }
}

// Append Static Message Bubble (used during session restoration)
function appendMessage(sender, text, sources = [], shouldScroll = true) {
    const row = document.createElement("div");
    row.className = `message-row ${sender}`;

    if (sender === "doctor") {
        row.innerHTML = `
            <div class="message-avatar" title="Sage Dhanvantari">
                <i class="fa-solid fa-leaf"></i>
            </div>
            <div class="message-bubble">
                ${sources && sources.length > 0 ? renderSourcesTray(sources) : ''}
                <div class="markdown-body">
                    ${formatMessageWithCitations(text, sources)}
                </div>
            </div>
        `;
        attachCitationListeners(row, sources);
    } else {
        row.innerHTML = `
            <div class="message-bubble">
                ${escapeHTML(text)}
            </div>
        `;
    }

    chatMessages.appendChild(row);
    if (shouldScroll) scrollToBottom();
}

// Render Perplexity Style Sources Tray
function renderSourcesTray(sources) {
    const chipsHtml = sources.map((s, idx) => {
        const num = idx + 1;
        const shortTitle = s.source_book.length > 28 ? s.source_book.substring(0, 26) + '...' : s.source_book;
        return `
            <button class="source-chip" data-idx="${idx}" title="${escapeHTML(s.source_book)} - Page ${s.page_number}">
                <span class="chip-num">${num}</span>
                <span>${escapeHTML(shortTitle)}</span>
            </button>
        `;
    }).join('');

    return `
        <div class="sources-tray">
            <div class="sources-label"><i class="fa-solid fa-book-bookmark"></i> Scriptural Citations (${sources.length})</div>
            <div class="sources-chips">
                ${chipsHtml}
            </div>
        </div>
    `;
}

// Convert [1], [2] into clickable citation pills
function formatMessageWithCitations(text, sources) {
    let processed = text.replace(/\[(\d+)\]/g, (match, p1) => {
        const idx = parseInt(p1, 10);
        return `<a class="inline-citation" data-source-idx="${idx - 1}" href="javascript:void(0);">[${idx}]</a>`;
    });
    return marked.parse(processed);
}

// Citation Popovers
function attachCitationListeners(container, sources) {
    if (!sources || sources.length === 0) return;

    container.querySelectorAll(".inline-citation, .source-chip").forEach(el => {
        el.addEventListener("click", (e) => {
            e.stopPropagation();
            const idx = parseInt(el.getAttribute("data-source-idx") || el.getAttribute("data-idx"), 10);
            if (sources[idx]) {
                showCitationPopover(sources[idx], el);
            }
        });
    });
}

function showCitationPopover(source, anchorEl) {
    popoverBookTitle.textContent = source.source_book || "Ayurvedic Scripture";
    popoverPage.textContent = `Page ${source.page_number || 'N/A'}`;
    popoverExcerpt.textContent = `"${(source.text || '').trim()}"`;

    let downloadLink = citationPopover.querySelector(".popover-download-link");
    if (!downloadLink) {
        downloadLink = document.createElement("a");
        downloadLink.className = "popover-download-link";
        downloadLink.target = "_blank";
        downloadLink.rel = "noopener noreferrer";
        downloadLink.style.cssText = "display: block; margin-top: 0.6rem; font-size: 0.8rem; color: #10b981; font-weight: 600; text-decoration: none;";
        citationPopover.appendChild(downloadLink);
    }
    if (source.download_url) {
        downloadLink.href = source.download_url;
        downloadLink.innerHTML = '<i class="fa-solid fa-cloud-arrow-down"></i> Read / Download PDF (FreeGurukul Archive)';
        downloadLink.style.display = "block";
    } else {
        downloadLink.style.display = "none";
    }

    const rect = anchorEl.getBoundingClientRect();
    citationPopover.style.left = Math.min(rect.left, window.innerWidth - 380) + "px";
    citationPopover.style.top = (rect.bottom + 8) + "px";

    citationPopover.classList.remove("hidden");
}

function openLegalModal(type) {
    if (type === "privacy") {
        legalModalTitle.innerHTML = '<i class="fa-solid fa-user-shield"></i> Privacy Policy';
        legalModalContent.innerHTML = `
            <p><strong>Last Updated: 2026</strong></p>
            <p>Sushruta AI is committed to protecting your personal health privacy:</p>
            <ul style="margin-left: 1.25rem; margin-top: 0.5rem;">
                <li><strong>Database Isolation</strong>: Your consultation history is stored in an isolated user account. We do not sell or monetize personal health data.</li>
                <li><strong>API Processing</strong>: Queries are processed securely via encrypted TLS connections to Google Gemini and Pinecone vector databases solely to generate your Ayurvedic remedy.</li>
                <li><strong>Anonymous Guest Mode</strong>: You can consult freely without creating an account using browser-only local storage.</li>
            </ul>
        `;
    } else if (type === "terms") {
        legalModalTitle.innerHTML = '<i class="fa-solid fa-file-contract"></i> Terms of Service';
        legalModalContent.innerHTML = `
            <p><strong>Educational & Wellness Purpose</strong></p>
            <p>By using Sushruta AI, you acknowledge and agree to the following terms:</p>
            <ul style="margin-left: 1.25rem; margin-top: 0.5rem;">
                <li>The advice provided is compiled from traditional, historical Ayurvedic scriptures and reference compendia.</li>
                <li>This platform is intended for informational and wellness exploration only and does not establish a formal physician-patient relationship.</li>
                <li>Users are responsible for verifying any herb, spice, or formulation with their local certified health practitioner before intake.</li>
            </ul>
        `;
    } else {
        legalModalTitle.innerHTML = '<i class="fa-solid fa-notes-medical"></i> Medical Disclaimer';
        legalModalContent.innerHTML = `
            <p><strong>Important Health & Safety Notice:</strong></p>
            <p>Sushruta AI is an AI-powered conversational reference tool grounded in Ayurvedic literature. It is not a replacement for professional clinical diagnosis, emergency treatment, or prescription medicine.</p>
            <p style="margin-top: 0.75rem;">If you are experiencing severe pain, high fever, difficulty breathing, or a medical emergency, please seek immediate assistance at your nearest hospital or licensed physician.</p>
        `;
    }
    legalModal.classList.remove("hidden");
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHTML(str) {
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// =========================================================
// FreeGurukul 3500 Books Dynamic Browser
// =========================================================
let catalogAyurvedaOnly = false;
let catalogDebounceTimer = null;

function initCatalogExplorer() {
    const searchInput = document.getElementById("catalog-search-input");
    const categorySelect = document.getElementById("catalog-category-select");
    const ayurToggle = document.getElementById("catalog-ayurveda-toggle");
    const resultsGrid = document.getElementById("catalog-results-grid");
    const statusBar = document.getElementById("catalog-status-bar");

    if (!searchInput || !resultsGrid) return;

    fetch("/api/books/categories")
        .then(r => r.json())
        .then(data => {
            if (data.categories && categorySelect) {
                categorySelect.innerHTML = '<option value="">All Categories (3,500+ Books)</option>';
                data.categories.forEach(cat => {
                    const opt = document.createElement("option");
                    opt.value = cat.category;
                    opt.textContent = `${cat.category} (${cat.count})`;
                    categorySelect.appendChild(opt);
                });
            }
        })
        .catch(err => console.log("Category fetch notice:", err));

    async function loadCatalogBooks() {
        const query = searchInput.value.trim();
        const category = categorySelect ? categorySelect.value : "";
        const url = `/api/books?query=${encodeURIComponent(query)}&category=${encodeURIComponent(category)}${catalogAyurvedaOnly ? '&is_ayurveda=true' : ''}&limit=18`;

        if (statusBar) statusBar.textContent = "Searching 3,500 books database...";

        try {
            const res = await fetch(url);
            const data = await res.json();
            const books = data.books || [];

            if (statusBar) {
                statusBar.textContent = `Found ${data.total || books.length} books in catalog ${catalogAyurvedaOnly ? '(Ayurveda filtered)' : ''}. Showing top ${books.length}.`;
            }

            if (books.length === 0) {
                resultsGrid.innerHTML = '<div style="color: var(--text-muted); padding: 1.5rem; text-align: center; width: 100%;">No books matched your filter criteria. Try searching a different keyword.</div>';
                return;
            }

            resultsGrid.innerHTML = books.map(b => {
                const ayurBadge = b.is_ayurveda ? '<span style="font-size: 0.68rem; background: rgba(16,185,129,0.15); color: #10b981; padding: 2px 6px; border-radius: 4px; margin-left: 6px;"><i class="fa-solid fa-leaf"></i> Ayurveda</span>' : '';
                const downloadBtn = b.download_url ? `<a href="${escapeHTML(b.download_url)}" target="_blank" rel="noopener noreferrer" style="color: #d4af37; margin-left: auto; text-decoration: none; font-size: 0.78rem;" title="Download FreeGurukul PDF"><i class="fa-solid fa-download"></i> PDF</a>` : '';
                return `
                    <div class="scripture-chip" style="display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; text-align: left;">
                        <div style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                            <i class="fa-solid fa-book-bookmark" style="color: #10b981; margin-right: 4px;"></i>
                            <strong style="color: var(--text-light); font-size: 0.85rem;">${escapeHTML(b.title_telugu)}</strong>
                            ${ayurBadge}
                            <div style="font-size: 0.72rem; color: var(--text-muted);">${escapeHTML(b.title_english || b.category)} &bull; ${b.pages} pgs (${b.size_mb} MB)</div>
                        </div>
                        ${downloadBtn}
                    </div>
                `;
            }).join("");
        } catch (err) {
            console.error("Catalog load error:", err);
            if (statusBar) statusBar.textContent = "Unable to fetch books from API.";
        }
    }

    searchInput.addEventListener("input", () => {
        clearTimeout(catalogDebounceTimer);
        catalogDebounceTimer = setTimeout(loadCatalogBooks, 300);
    });

    if (categorySelect) {
        categorySelect.addEventListener("change", loadCatalogBooks);
    }

    if (ayurToggle) {
        ayurToggle.addEventListener("click", () => {
            catalogAyurvedaOnly = !catalogAyurvedaOnly;
            ayurToggle.classList.toggle("active", catalogAyurvedaOnly);
            ayurToggle.style.borderColor = catalogAyurvedaOnly ? "var(--accent-emerald)" : "";
            ayurToggle.style.color = catalogAyurvedaOnly ? "var(--accent-emerald)" : "";
            loadCatalogBooks();
        });
    }

    loadCatalogBooks();
}

document.addEventListener("DOMContentLoaded", () => {
    initCatalogExplorer();
});
