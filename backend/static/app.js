// State Management
let currentSessionId = null;
let chatSessions = [];
let isGenerating = false;
let currentSources = [];

// Storage Keys
const SESSIONS_STORAGE_KEY = "sushruta_chat_sessions_v1";

// DOM Elements
const sidebar = document.getElementById("sidebar");
const btnToggleSidebar = document.getElementById("btn-toggle-sidebar");
const btnCollapseSidebar = document.getElementById("btn-collapse-sidebar");

const tabChat = document.getElementById("tab-chat");
const tabBrochure = document.getElementById("tab-brochure");
const btnHeaderBrochure = document.getElementById("btn-header-brochure");
const btnTryConsultation = document.getElementById("btn-try-consultation");

const chatView = document.getElementById("chat-view");
const brochureView = document.getElementById("brochure-view");

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
const btnOpenPrivacy = document.getElementById("btn-open-privacy");
const btnOpenTerms = document.getElementById("btn-open-terms");
const btnOpenDisclaimer = document.getElementById("btn-open-disclaimer");

// Popover Elements
const citationPopover = document.getElementById("citation-popover");
const popoverBookTitle = document.getElementById("popover-book-title");
const popoverPage = document.getElementById("popover-page");
const popoverExcerpt = document.getElementById("popover-excerpt");

// Initialize on DOM Ready
document.addEventListener("DOMContentLoaded", () => {
    marked.setOptions({ breaks: true, gfm: true });
    loadChatSessions();
    setupEventListeners();
    checkBackendConfig();
});

// Event Listeners
function setupEventListeners() {
    // Sidebar Collapse / Expand
    btnToggleSidebar.addEventListener("click", () => {
        sidebar.classList.toggle("collapsed");
    });

    btnCollapseSidebar.addEventListener("click", () => {
        sidebar.classList.add("collapsed");
    });

    // View Switching
    tabChat.addEventListener("click", () => switchView("chat"));
    tabBrochure.addEventListener("click", () => switchView("brochure"));
    btnHeaderBrochure.addEventListener("click", () => switchView("brochure"));
    btnTryConsultation.addEventListener("click", () => switchView("chat"));

    // Chat Form Submission
    chatForm.addEventListener("submit", handleSubmit);

    // Textarea Auto-expand & Enter to Send
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

    // New Chat & Clear Current
    btnNewChat.addEventListener("click", () => startNewSession());
    btnClearChat.addEventListener("click", () => clearCurrentSession());
    btnClearAllHistory.addEventListener("click", clearAllHistory);

    // Quick Topic Chips & Cards
    document.querySelectorAll("[data-prompt]").forEach(el => {
        el.addEventListener("click", () => {
            const promptText = el.getAttribute("data-prompt");
            if (promptText) {
                switchView("chat");
                chatInput.value = promptText;
                chatInput.dispatchEvent(new Event("input"));
                chatForm.dispatchEvent(new Event("submit"));
            }
        });
    });

    // Settings Modal
    btnSettingsModal.addEventListener("click", () => settingsModal.classList.remove("hidden"));
    btnCloseSettings.addEventListener("click", () => settingsModal.classList.add("hidden"));
    btnCancelSettings.addEventListener("click", () => settingsModal.classList.add("hidden"));
    settingsForm.addEventListener("submit", saveSettings);

    // Legal Modals
    btnOpenPrivacy.addEventListener("click", () => openLegalModal("privacy"));
    btnOpenTerms.addEventListener("click", () => openLegalModal("terms"));
    btnOpenDisclaimer.addEventListener("click", () => openLegalModal("disclaimer"));
    btnCloseLegal.addEventListener("click", () => legalModal.classList.add("hidden"));
    btnDismissLegal.addEventListener("click", () => legalModal.classList.add("hidden"));

    // Global Click to close Popover & Modals
    document.addEventListener("click", (e) => {
        if (!e.target.closest(".inline-citation") && !e.target.closest(".source-chip")) {
            citationPopover.classList.add("hidden");
        }
    });
}

// Switch between Chat and Brochure Views
function switchView(viewName) {
    if (viewName === "chat") {
        chatView.classList.add("active");
        chatView.classList.remove("hidden");
        brochureView.classList.add("hidden");
        tabChat.classList.add("active");
        tabBrochure.classList.remove("active");
        chatInput.focus();
    } else {
        brochureView.classList.remove("hidden");
        chatView.classList.add("hidden");
        chatView.classList.remove("active");
        tabBrochure.classList.add("active");
        tabChat.classList.remove("active");
    }
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
            switchView("chat");
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

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                messages: session.messages,
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
