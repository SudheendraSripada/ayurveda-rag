// State Management
let currentSessionId = null;
let chatSessions = [];
let isGenerating = false;
let currentSources = [];

// Storage Keys
const SESSIONS_STORAGE_KEY = "sushruta_chat_sessions_v1";
const SITE_LANG_STORAGE_KEY = "sushruta_site_language_v1";
const RESPONSE_LANG_STORAGE_KEY = "sushruta_response_language_v1";

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
        "faq_a3": "Yes. Your conversation history is saved exclusively in your browser localStorage. No personal consultation logs are sold or stored permanently on third-party tracking databases.",
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
        "pillar_4_desc": "మీ సంభాషణలు మీ బ్రౌజర్‌లోనే ఉంటాయి, ఎలాంటి వ్యక్తిగత డేటా నిల్వ చేయబడదు.",
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
        "faq_a3": "అవును. మీ చాట్ డేటా మీ కంప్యూటర్‌లోనే లోకల్‌గా నిల్వ చేయబడుతుంది.",
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
        "pillar_4_desc": "आपकी स्वास्थ्य चर्चा केवल आपके ब्राउज़र में सुरक्षित रहती है।",
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
        "faq_a3": "हाँ, आपकी सभी बातचीत केवल आपके लोकल डिवाइस पर ही रहती है।",
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

// Settings Modal Elements
const btnSettingsModal = document.getElementById("btn-settings-modal");
const settingsModal = document.getElementById("settings-modal");
const btnCloseSettings = document.getElementById("btn-close-settings");
const btnCancelSettings = document.getElementById("btn-cancel-settings");
const settingsForm = document.getElementById("settings-form");
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
document.addEventListener("DOMContentLoaded", () => {
    marked.setOptions({ breaks: true, gfm: true });
    
    // 1. Restore & Apply Website UI Language
    const savedSiteLang = localStorage.getItem(SITE_LANG_STORAGE_KEY) || "English";
    if (landingSiteLang) landingSiteLang.value = savedSiteLang;
    if (chatSiteLang) chatSiteLang.value = savedSiteLang;
    applySiteLanguage(savedSiteLang);

    // 2. Restore Chat Response Language in Chatbox
    const savedResponseLang = localStorage.getItem(RESPONSE_LANG_STORAGE_KEY) || "English";
    if (chatResponseLang) chatResponseLang.value = savedResponseLang;
    
    loadChatSessions();
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

    // 5. Sidebar Collapse / Expand
    if (btnToggleSidebar) {
        btnToggleSidebar.addEventListener("click", () => {
            sidebar.classList.toggle("collapsed");
        });
    }

    if (btnCollapseSidebar) {
        btnCollapseSidebar.addEventListener("click", () => {
            sidebar.classList.add("collapsed");
        });
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

    // 9. Quick Prompt Cards (Works on both Landing & Chat views)
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

    // 10. Settings Modal
    btnSettingsModal.addEventListener("click", () => settingsModal.classList.remove("hidden"));
    btnCloseSettings.addEventListener("click", () => settingsModal.classList.add("hidden"));
    btnCancelSettings.addEventListener("click", () => settingsModal.classList.add("hidden"));
    settingsForm.addEventListener("submit", saveSettings);

    // 11. Legal Modals from Footer
    if (btnFooterPrivacy) btnFooterPrivacy.addEventListener("click", () => openLegalModal("privacy"));
    if (btnFooterTerms) btnFooterTerms.addEventListener("click", () => openLegalModal("terms"));
    if (btnFooterDisclaimer) btnFooterDisclaimer.addEventListener("click", () => openLegalModal("disclaimer"));
    btnCloseLegal.addEventListener("click", () => legalModal.classList.add("hidden"));
    btnDismissLegal.addEventListener("click", () => legalModal.classList.add("hidden"));

    // 12. Global Click to close Popover & Modals
    document.addEventListener("click", (e) => {
        if (!e.target.closest(".inline-citation") && !e.target.closest(".source-chip")) {
            citationPopover.classList.add("hidden");
        }
    });
}

// Apply Website UI Language Translations to all [data-i18n] elements
function applySiteLanguage(lang) {
    const dict = I18N_DICTIONARY[lang] || I18N_DICTIONARY["English"];
    document.querySelectorAll("[data-i18n]").forEach(el => {
        const key = el.getAttribute("data-i18n");
        if (dict[key]) {
            el.innerHTML = dict[key];
        }
    });
}

// View Switching Functions
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

// Local Storage Session Management
function loadChatSessions() {
    try {
        const stored = localStorage.getItem(SESSIONS_STORAGE_KEY);
        chatSessions = stored ? JSON.parse(stored) : [];
    } catch (e) {
        chatSessions = [];
    }

    if (chatSessions.length > 0) {
        loadSession(chatSessions[0].id);
    } else {
        startNewSession();
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

function startNewSession() {
    currentSessionId = "session_" + Date.now();
    const newSession = {
        id: currentSessionId,
        title: "New Consultation",
        messages: [],
        timestamp: new Date().toISOString()
    };
    chatSessions.unshift(newSession);
    saveChatSessions();
    loadSession(currentSessionId);
}

function loadSession(sessionId) {
    currentSessionId = sessionId;
    const session = chatSessions.find(s => s.id === sessionId);
    if (!session) return;

    chatMessages.innerHTML = "";
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

function clearAllHistory() {
    if (confirm("Are you sure you want to clear all consultation history?")) {
        chatSessions = [];
        localStorage.removeItem(SESSIONS_STORAGE_KEY);
        startNewSession();
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

        item.querySelector(".btn-delete-session").addEventListener("click", (e) => {
            e.stopPropagation();
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
    try {
        const res = await fetch("/api/config-status");
        const data = await res.json();
        if (data.configured) {
            pineconeKeyInput.placeholder = "••••••••••••••••••••••••••••••••";
            geminiKeyInput.placeholder = "••••••••••••••••••••••••••••••••";
            pineconeIndexInput.value = data.index_name || "ayurveda-index";
        }
        
        const statsRes = await fetch("/api/index-stats");
        const statsData = await statsRes.json();
        if (statsData.exists && statsData.total_vector_count > 0) {
            corpusBadge.innerHTML = `<i class="fa-solid fa-check"></i> <span>${statsData.total_vector_count.toLocaleString()} Chunks Active</span>`;
        }
    } catch (err) {
        console.error("Config check notice:", err);
    }
}

// Save Settings
async function saveSettings(e) {
    e.preventDefault();
    const payload = {
        pinecone_api_key: pineconeKeyInput.value.trim() || undefined,
        pinecone_index_name: pineconeIndexInput.value.trim() || "ayurveda-index",
        gemini_api_key: geminiKeyInput.value.trim() || undefined
    };

    try {
        const res = await fetch("/api/config", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            alert("API configuration saved successfully.");
            settingsModal.classList.add("hidden");
            checkBackendConfig();
        } else {
            const err = await res.json();
            alert("Error: " + err.detail);
        }
    } catch (err) {
        alert("Failed to save settings: Network error.");
    }
}

// Handle Message Submission
async function handleSubmit(e) {
    e.preventDefault();
    const userText = chatInput.value.trim();
    if (!userText || isGenerating) return;

    welcomeScreen.classList.add("hidden");

    // Retrieve active session
    let session = chatSessions.find(s => s.id === currentSessionId);
    if (!session) {
        startNewSession();
        session = chatSessions.find(s => s.id === currentSessionId);
    }

    // Set session title from first question
    if (session.messages.length === 0) {
        session.title = userText.length > 26 ? userText.substring(0, 24) + "..." : userText;
    }

    // Add user message to state & UI
    session.messages.push({ role: "user", content: userText });
    appendMessage("user", userText);
    saveChatSessions();

    chatInput.value = "";
    chatInput.style.height = "auto";
    isGenerating = true;
    btnSend.disabled = true;

    // Add typing indicator
    const typingIndicatorEl = createTypingIndicator();
    chatMessages.appendChild(typingIndicatorEl);
    scrollToBottom();

    // Use Selected Response Language from Chatbox Selector
    const chosenResponseLang = chatResponseLang ? chatResponseLang.value : "English";

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                messages: session.messages,
                language: chosenResponseLang,
                rerank: checkboxRerank.checked
            })
        });

        const data = await response.json();
        typingIndicatorEl.remove();

        if (response.ok) {
            currentSources = data.sources || [];
            session.messages.push({ role: "model", content: data.reply, sources: data.sources });
            appendMessage("doctor", data.reply, data.sources);
            saveChatSessions();
        } else {
            appendErrorMessage(data.detail || "Failed to generate doctor consultation. Please check your Gemini API key.");
        }
    } catch (err) {
        typingIndicatorEl.remove();
        appendErrorMessage("Network error connecting to the Sushruta AI backend. Please verify your local server is running.");
    } finally {
        isGenerating = false;
        btnSend.disabled = false;
        scrollToBottom();
    }
}

// Append Message UI Bubble
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

    const rect = anchorEl.getBoundingClientRect();
    citationPopover.style.left = Math.min(rect.left, window.innerWidth - 380) + "px";
    citationPopover.style.top = (rect.bottom + 8) + "px";

    citationPopover.classList.remove("hidden");
}

function createTypingIndicator() {
    const row = document.createElement("div");
    row.className = "message-row doctor";
    row.id = "typing-row";
    row.innerHTML = `
        <div class="message-avatar">
            <i class="fa-solid fa-leaf"></i>
        </div>
        <div class="message-bubble" style="padding: 0.85rem 1.2rem;">
            <div class="typing-indicator">
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span style="margin-left: 8px; font-size: 0.78rem; color: var(--text-muted); font-style: italic;">Consulting classical Ayurvedic scriptures...</span>
            </div>
        </div>
    `;
    return row;
}

function appendErrorMessage(errorText) {
    const row = document.createElement("div");
    row.className = "message-row doctor";
    row.innerHTML = `
        <div class="message-avatar" style="color: #ef4444; border-color: rgba(239,68,68,0.3); background: rgba(239,68,68,0.1);">
            <i class="fa-solid fa-triangle-exclamation"></i>
        </div>
        <div class="message-bubble" style="border-color: rgba(239,68,68,0.3); background: rgba(239,68,68,0.05); color: #fca5a5;">
            <strong>Consultation Notice:</strong> ${escapeHTML(errorText)}
        </div>
    `;
    chatMessages.appendChild(row);
    scrollToBottom();
}

function openLegalModal(type) {
    if (type === "privacy") {
        legalModalTitle.innerHTML = '<i class="fa-solid fa-user-shield"></i> Privacy Policy';
        legalModalContent.innerHTML = `
            <p><strong>Last Updated: 2026</strong></p>
            <p>Sushruta AI is committed to protecting your personal health privacy:</p>
            <ul style="margin-left: 1.25rem; margin-top: 0.5rem;">
                <li><strong>Local-First Storage</strong>: Your consultation history is stored directly in your web browser's local storage. We do not sell or monetize personal health data.</li>
                <li><strong>API Processing</strong>: Queries are processed securely via encrypted TLS connections to Google Gemini and Pinecone vector databases solely to generate your Ayurvedic remedy.</li>
                <li><strong>No User Profiles Required</strong>: You can consult freely without creating an account or providing personally identifiable information.</li>
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
