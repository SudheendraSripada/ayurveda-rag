// State Management
let conversationHistory = [];
let isGenerating = false;
let currentSources = [];

// DOM Elements
const chatMessages = document.getElementById("chat-messages");
const welcomeScreen = document.getElementById("welcome-screen");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const btnSend = document.getElementById("btn-send");
const checkboxRerank = document.getElementById("checkbox-rerank");
const btnNewChat = document.getElementById("btn-new-chat");
const btnClearChat = document.getElementById("btn-clear-chat");
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

// Popover Element
const citationPopover = document.getElementById("citation-popover");
const popoverBookTitle = document.getElementById("popover-book-title");
const popoverPage = document.getElementById("popover-page");
const popoverExcerpt = document.getElementById("popover-excerpt");

// Initialize on DOM Load
document.addEventListener("DOMContentLoaded", () => {
    marked.setOptions({ breaks: true, gfm: true });
    setupEventListeners();
    checkConfig();
});

function setupEventListeners() {
    // Chat Submit
    chatForm.addEventListener("submit", handleSubmit);

    // Auto-resizing textarea & Keybindings
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

    // New Chat / Clear Chat
    btnNewChat.addEventListener("click", resetConversation);
    btnClearChat.addEventListener("click", resetConversation);

    // Quick Prompt Chips & Welcome Cards
    document.querySelectorAll("[data-prompt]").forEach(el => {
        el.addEventListener("click", () => {
            const promptText = el.getAttribute("data-prompt");
            if (promptText) {
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
    
    // Hide popover on global click
    document.addEventListener("click", (e) => {
        if (!e.target.closest(".inline-citation") && !e.target.closest(".source-chip")) {
            citationPopover.classList.add("hidden");
        }
    });
}

// Check Backend Config
async function checkConfig() {
    try {
        const res = await fetch("/api/config-status");
        const data = await res.json();
        if (data.configured) {
            pineconeKeyInput.placeholder = "••••••••••••••••••••••••••••••••";
            geminiKeyInput.placeholder = "••••••••••••••••••••••••••••••••";
            pineconeIndexInput.value = data.index_name || "ayurveda-index";
        }
        
        // Fetch index stats
        const statsRes = await fetch("/api/index-stats");
        const statsData = await statsRes.json();
        if (statsData.exists && statsData.total_vector_count > 0) {
            corpusBadge.innerHTML = `<i class="fa-solid fa-check"></i> <span>${statsData.total_vector_count.toLocaleString()} Chunks Active</span>`;
        }
    } catch (err) {
        console.error("Config check note:", err);
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
            alert("Settings updated successfully.");
            settingsModal.classList.add("hidden");
            checkConfig();
        } else {
            const err = await res.json();
            alert("Error: " + err.detail);
        }
    } catch (err) {
        alert("Failed to save settings.");
    }
}

// Reset Conversation
function resetConversation() {
    conversationHistory = [];
    currentSources = [];
    chatMessages.innerHTML = "";
    chatMessages.appendChild(welcomeScreen);
    welcomeScreen.classList.remove("hidden");
    chatInput.value = "";
    chatInput.style.height = "auto";
    chatInput.focus();
}

// Handle Message Submission
async function handleSubmit(e) {
    e.preventDefault();
    const userText = chatInput.value.trim();
    if (!userText || isGenerating) return;

    // Hide welcome hero on first message
    welcomeScreen.classList.add("hidden");

    // Append User Message to UI
    appendMessage("user", userText);
    conversationHistory.push({ role: "user", content: userText });

    // Reset input
    chatInput.value = "";
    chatInput.style.height = "auto";
    isGenerating = true;
    btnSend.disabled = true;

    // Append Typing Indicator
    const typingIndicatorEl = createTypingIndicator();
    chatMessages.appendChild(typingIndicatorEl);
    scrollToBottom();

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                messages: conversationHistory,
                rerank: checkboxRerank.checked
            })
        });

        const data = await response.json();
        typingIndicatorEl.remove();

        if (response.ok) {
            currentSources = data.sources || [];
            appendMessage("doctor", data.reply, data.sources);
            conversationHistory.push({ role: "model", content: data.reply });
        } else {
            appendErrorMessage(data.detail || "Failed to generate doctor consultation. Please verify API keys in Settings.");
        }
    } catch (err) {
        typingIndicatorEl.remove();
        appendErrorMessage("Network error connecting to backend. Please ensure the server is running on http://127.0.0.1:8000.");
    } finally {
        isGenerating = false;
        btnSend.disabled = false;
        scrollToBottom();
    }
}

// Append Message Bubble to UI
function appendMessage(sender, text, sources = []) {
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

        // Attach event listeners for citation pills and source chips
        attachCitationListeners(row, sources);
    } else {
        row.innerHTML = `
            <div class="message-bubble">
                ${escapeHTML(text)}
            </div>
        `;
    }

    chatMessages.appendChild(row);
    scrollToBottom();
}

// Render Sources Tray (Perplexity Style)
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
            <div class="sources-label"><i class="fa-solid fa-book-bookmark"></i> Scriptural Sources (${sources.length})</div>
            <div class="sources-chips">
                ${chipsHtml}
            </div>
        </div>
    `;
}

// Parse markdown and convert [1], [2] into interactive citation badges
function formatMessageWithCitations(text, sources) {
    // Replace [1], [2], [1][2] with interactive badge elements before markdown
    let processed = text.replace(/\[(\d+)\]/g, (match, p1) => {
        const idx = parseInt(p1, 10);
        return `<a class="inline-citation" data-source-idx="${idx - 1}" href="javascript:void(0);">[${idx}]</a>`;
    });

    return marked.parse(processed);
}

// Attach hover / click popovers to citations
function attachCitationListeners(container, sources) {
    if (!sources || sources.length === 0) return;

    // Attach to inline citations [1], [2]
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
        <div class="message-bubble" style="padding: 0.9rem 1.25rem;">
            <div class="typing-indicator">
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span style="margin-left: 8px; font-size: 0.8rem; color: var(--text-muted); font-style: italic;">Consulting classical Ayurvedic scriptures...</span>
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
