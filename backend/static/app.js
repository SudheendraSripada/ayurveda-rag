// State management
let isConfigured = false;
let uploadIntervals = {}; // Poll tracking for files

// DOM Elements
const btnUserView = document.getElementById("btn-user-view");
const btnAdminView = document.getElementById("btn-admin-view");
const userView = document.getElementById("user-view");
const adminView = document.getElementById("admin-view");

const adminLockCard = document.getElementById("admin-lock-card");
const adminContent = document.getElementById("admin-content");
const adminPasscode = document.getElementById("admin-passcode");
const btnUnlockAdmin = document.getElementById("btn-unlock-admin");

const configStatusBadge = document.getElementById("config-status-badge");
const configForm = document.getElementById("config-form");
const pineconeKeyInput = document.getElementById("pinecone-key");
const pineconeIndexInput = document.getElementById("pinecone-index");
const geminiKeyInput = document.getElementById("gemini-key");

const statIndexStatus = document.getElementById("stat-index-status");
const statTotalVectors = document.getElementById("stat-total-vectors");
const btnRefreshStats = document.getElementById("btn-refresh-stats");
const btnClearIndex = document.getElementById("btn-clear-index");

const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("file-input");
const uploadProgressContainer = document.getElementById("upload-progress-container");
const uploadItemsList = document.getElementById("upload-items-list");

const libraryEmptyState = document.getElementById("library-empty-state");
const libraryTable = document.getElementById("library-table");
const libraryList = document.getElementById("library-list");
const libraryCountBadge = document.getElementById("library-count-badge");

const searchForm = document.getElementById("search-form");
const searchInput = document.getElementById("search-input");
const checkboxRerank = document.getElementById("checkbox-rerank");
const remedyLoading = document.getElementById("remedy-loading");
const remedyError = document.getElementById("remedy-error");
const remedyResultCard = document.getElementById("remedy-result-card");
const remedyContentMarkdown = document.getElementById("remedy-content-markdown");
const btnPrintRemedy = document.getElementById("btn-print-remedy");

const sourcesHeader = document.getElementById("sources-header");
const sourcesListContainer = document.getElementById("sources-list-container");
const sourcesSection = document.querySelector(".sources-section");
const sourceCount = document.getElementById("source-count");

// Initialize on Load
document.addEventListener("DOMContentLoaded", () => {
    checkConfigStatus();
    setupEventListeners();
    
    // Configure markdown parser options
    marked.setOptions({
        breaks: true,
        gfm: true
    });
});

// Setup Event Listeners
function setupEventListeners() {
    // Navigation Toggles
    btnUserView.addEventListener("click", () => {
        btnUserView.classList.add("active");
        btnAdminView.classList.remove("active");
        userView.classList.remove("hidden");
        adminView.classList.add("hidden");
    });

    btnAdminView.addEventListener("click", () => {
        btnAdminView.classList.add("active");
        btnUserView.classList.remove("active");
        adminView.classList.remove("hidden");
        userView.classList.add("hidden");
    });

    // Admin Passcode Lock
    btnUnlockAdmin.addEventListener("click", unlockAdminConsole);
    adminPasscode.addEventListener("keypress", (e) => {
        if (e.key === "Enter") unlockAdminConsole();
    });

    // Config Save Form
    configForm.addEventListener("submit", saveConfiguration);

    // Refresh Stats
    btnRefreshStats.addEventListener("click", fetchIndexStats);
    
    // Reset Database
    btnClearIndex.addEventListener("click", purgeDatabase);

    // File Upload Handlers
    dropZone.addEventListener("click", () => fileInput.click());
    fileInput.addEventListener("change", handleFileSelect);
    
    // Drag & Drop
    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.classList.add("dragover");
    });
    
    dropZone.addEventListener("dragleave", () => {
        dropZone.classList.remove("dragover");
    });
    
    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.classList.remove("dragover");
        if (e.dataTransfer.files.length > 0) {
            uploadFile(e.dataTransfer.files[0]);
        }
    });

    // Remedy Query Form
    searchForm.addEventListener("submit", executeRemedySearch);

    // Accordion toggle for references
    sourcesHeader.addEventListener("click", () => {
        sourcesSection.classList.toggle("expanded");
        sourcesListContainer.classList.toggle("hidden");
    });

    // Print Remedy
    btnPrintRemedy.addEventListener("click", () => {
        window.print();
    });
}

// Config Status Check
async function checkConfigStatus() {
    try {
        const res = await fetch("/api/config-status");
        const status = await res.json();
        
        isConfigured = status.configured;
        if (status.configured) {
            configStatusBadge.textContent = "Configured";
            configStatusBadge.className = "badge badge-success";
            
            // Prefill with placeholders if configured to hide raw keys
            pineconeKeyInput.placeholder = "••••••••••••••••••••••••••••••••";
            geminiKeyInput.placeholder = "••••••••••••••••••••••••••••••••";
            pineconeIndexInput.value = status.index_name;
            
            // Refresh stats
            fetchIndexStats();
            fetchLibrary();
        } else {
            configStatusBadge.textContent = "Unconfigured";
            configStatusBadge.className = "badge badge-error";
        }
    } catch (err) {
        console.error("Failed to check configuration status:", err);
    }
}

// Unlock Admin View
function unlockAdminConsole() {
    const pin = adminPasscode.value.trim();
    if (pin === "admin123") {
        adminLockCard.classList.add("hidden");
        adminContent.classList.remove("hidden");
        adminPasscode.value = "";
    } else {
        alert("Incorrect passcode. Try again!");
        adminPasscode.value = "";
        adminPasscode.focus();
    }
}

// Save Configurations
async function saveConfiguration(e) {
    e.preventDefault();
    
    const pineconeKey = pineconeKeyInput.value.trim();
    const geminiKey = geminiKeyInput.value.trim();
    const indexName = pineconeIndexInput.value.trim();
    
    const saveBtn = document.getElementById("btn-save-config");
    saveBtn.disabled = true;
    saveBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Saving...';
    
    try {
        const response = await fetch("/api/config", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                pinecone_api_key: pineconeKey || "",
                pinecone_index_name: indexName,
                gemini_api_key: geminiKey || ""
            })
        });
        
        const data = await response.json();
        if (response.ok) {
            alert(data.message);
            isConfigured = true;
            configStatusBadge.textContent = "Configured";
            configStatusBadge.className = "badge badge-success";
            
            // Clear input text and show placeholders
            pineconeKeyInput.value = "";
            geminiKeyInput.value = "";
            pineconeKeyInput.placeholder = "••••••••••••••••••••••••••••••••";
            geminiKeyInput.placeholder = "••••••••••••••••••••••••••••••••";
            
            fetchIndexStats();
            fetchLibrary();
        } else {
            alert("Configuration Error: " + data.detail);
        }
    } catch (err) {
        alert("Failed to save credentials: network error.");
    } finally {
        saveBtn.disabled = false;
        saveBtn.innerHTML = '<i class="fa-solid fa-floppy-disk"></i> Validate & Save Keys';
    }
}

// Fetch Index Stats
async function fetchIndexStats() {
    try {
        const res = await fetch("/api/index-stats");
        const stats = await res.json();
        
        if (stats.exists) {
            statIndexStatus.textContent = "Online & Ready";
            statIndexStatus.className = "stat-value text-success";
            statTotalVectors.textContent = stats.total_vector_count.toLocaleString();
        } else {
            statIndexStatus.textContent = "Offline / Empty";
            statIndexStatus.className = "stat-value text-error";
            statTotalVectors.textContent = "0";
            if (stats.error) {
                console.error("Pinecone status details:", stats.error);
            }
        }
    } catch (err) {
        console.error("Failed to fetch index stats:", err);
    }
}

// Fetch Library File Catalog
async function fetchLibrary() {
    try {
        const res = await fetch("/api/documents");
        const docs = await res.json();
        
        const filenames = Object.keys(docs);
        libraryCountBadge.textContent = `${filenames.length} Book${filenames.length === 1 ? '' : 's'}`;
        
        if (filenames.length === 0) {
            libraryEmptyState.classList.remove("hidden");
            libraryTable.classList.add("hidden");
            return;
        }
        
        libraryEmptyState.classList.add("hidden");
        libraryTable.classList.remove("hidden");
        
        libraryList.innerHTML = "";
        filenames.forEach(name => {
            const doc = docs[name];
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td class="book-title-cell"><i class="fa-solid fa-file-pdf text-error"></i> ${doc.filename}</td>
                <td>${doc.chunk_count.toLocaleString()}</td>
                <td>${doc.indexed_at}</td>
                <td class="text-right">
                    <button class="btn-delete-doc" data-filename="${doc.filename}" title="Remove Book Metadata"><i class="fa-solid fa-trash-can"></i></button>
                </td>
            `;
            
            tr.querySelector(".btn-delete-doc").addEventListener("click", async (e) => {
                if (confirm(`Are you sure you want to remove the metadata index reference for '${doc.filename}'?`)) {
                    await deleteDocumentMetadata(doc.filename);
                }
            });
            
            libraryList.appendChild(tr);
        });
    } catch (err) {
        console.error("Failed to fetch document library:", err);
    }
}

// Delete Document Metadata
async function deleteDocumentMetadata(filename) {
    try {
        const res = await fetch(`/api/documents/${filename}`, { method: "DELETE" });
        if (res.ok) {
            fetchLibrary();
        } else {
            const err = await res.json();
            alert("Error: " + err.detail);
        }
    } catch (e) {
        console.error(e);
    }
}

// Purge and Reset DB
async function purgeDatabase() {
    if (!confirm("CRITICAL WARNING: This will completely delete the Pinecone index, library catalog records, and all uploaded text passages. This cannot be undone! Are you sure?")) {
        return;
    }
    
    const purgeBtn = document.getElementById("btn-clear-index");
    purgeBtn.disabled = true;
    purgeBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Resetting...';
    
    try {
        const res = await fetch("/api/clear-index", { method: "POST" });
        const data = await res.json();
        
        if (res.ok) {
            alert(data.message);
            fetchIndexStats();
            fetchLibrary();
        } else {
            alert("Error resetting database: " + data.detail);
        }
    } catch (err) {
        alert("Failed to reset database: network error.");
    } finally {
        purgeBtn.disabled = false;
        purgeBtn.innerHTML = '<i class="fa-solid fa-trash-can"></i> Purge & Delete Index';
    }
}

// Upload Book Ingestion
function handleFileSelect(e) {
    if (e.target.files.length > 0) {
        uploadFile(e.target.files[0]);
    }
}

async function uploadFile(file) {
    if (!isConfigured) {
        alert("Please configure and save API credentials first!");
        return;
    }
    
    if (!file.name.endsWith(".pdf")) {
        alert("Only PDF files are supported.");
        return;
    }
    
    const formData = new FormData();
    formData.append("file", file);
    
    // Add to progress items list
    uploadProgressContainer.classList.remove("hidden");
    const itemEl = document.createElement("div");
    itemEl.className = "upload-item";
    itemEl.id = `upload-${file.name.replace(/[^a-zA-Z0-9]/g, '_')}`;
    itemEl.innerHTML = `
        <div class="upload-item-header">
            <span class="upload-item-name">${file.name}</span>
            <span class="upload-item-status badge badge-process">Uploading...</span>
        </div>
        <div class="upload-progress-bar-wrapper">
            <div class="upload-progress-bar" style="width: 15%"></div>
        </div>
        <p class="upload-item-desc">Sending file to backend server...</p>
    `;
    uploadItemsList.appendChild(itemEl);
    
    try {
        const res = await fetch("/api/upload", {
            method: "POST",
            body: formData
        });
        
        const data = await res.json();
        if (res.ok) {
            itemEl.querySelector(".upload-progress-bar").style.width = "40%";
            itemEl.querySelector(".upload-item-status").textContent = "Ingesting";
            itemEl.querySelector(".upload-item-desc").textContent = "Background text extraction and segment chunking started.";
            
            // Start polling progress
            startPollingUpload(file.name, itemEl);
        } else {
            itemEl.querySelector(".upload-item-status").textContent = "Failed";
            itemEl.querySelector(".upload-item-status").className = "upload-item-status badge badge-error";
            itemEl.querySelector(".upload-item-desc").textContent = `Upload failed: ${data.detail}`;
            itemEl.querySelector(".upload-progress-bar").style.width = "0%";
        }
    } catch (err) {
        itemEl.querySelector(".upload-item-status").textContent = "Failed";
        itemEl.querySelector(".upload-item-status").className = "upload-item-status badge badge-error";
        itemEl.querySelector(".upload-item-desc").textContent = "Upload failed: network error.";
    }
}

// Poll Background Progress
function startPollingUpload(filename, itemEl) {
    const progressBar = itemEl.querySelector(".upload-progress-bar");
    const statusBadge = itemEl.querySelector(".upload-item-status");
    const descText = itemEl.querySelector(".upload-item-desc");
    
    progressBar.classList.add("processing");
    progressBar.style.width = "75%";
    
    const intervalId = setInterval(async () => {
        try {
            const res = await fetch("/api/upload-status");
            const statusMap = await res.json();
            
            const fileStatus = statusMap[filename];
            if (fileStatus) {
                descText.textContent = fileStatus.progress;
                
                if (fileStatus.status === "Completed") {
                    clearInterval(intervalId);
                    progressBar.classList.remove("processing");
                    progressBar.style.width = "100%";
                    statusBadge.textContent = "Completed";
                    statusBadge.className = "upload-item-status badge badge-success";
                    descText.textContent = `Successfully indexed! Segmented into ${fileStatus.chunks} chunks in Pinecone.`;
                    
                    // Refresh library and stats
                    fetchLibrary();
                    fetchIndexStats();
                    
                    // Remove progress item after 5 seconds
                    setTimeout(() => {
                        itemEl.remove();
                        if (uploadItemsList.children.length === 0) {
                            uploadProgressContainer.classList.add("hidden");
                        }
                    }, 5000);
                } else if (fileStatus.status === "Failed") {
                    clearInterval(intervalId);
                    progressBar.classList.remove("processing");
                    progressBar.style.width = "0%";
                    statusBadge.textContent = "Failed";
                    statusBadge.className = "upload-item-status badge badge-error";
                    descText.textContent = fileStatus.progress;
                }
            }
        } catch (e) {
            console.error("Error polling upload status:", e);
        }
    }, 2000);
    
    uploadIntervals[filename] = intervalId;
}

// User Remedy Finder: Search Symptoms
async function executeRemedySearch(e) {
    e.preventDefault();
    
    const queryText = searchInput.value.trim();
    const useRerank = checkboxRerank.checked;
    
    if (!queryText) return;
    
    // UI State resets
    remedyLoading.classList.remove("hidden");
    remedyError.classList.add("hidden");
    remedyResultCard.classList.add("hidden");
    
    // Scroll to loading indicator
    remedyLoading.scrollIntoView({ behavior: "smooth" });
    
    try {
        const response = await fetch("/api/query", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                query: queryText,
                rerank: useRerank
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Render Markdown remedy content
            remedyContentMarkdown.innerHTML = marked.parse(data.remedy);
            
            // Render reference sources
            renderSources(data.sources);
            
            // Show result card
            remedyLoading.classList.add("hidden");
            remedyResultCard.classList.remove("hidden");
            remedyResultCard.scrollIntoView({ behavior: "smooth" });
        } else {
            remedyLoading.classList.add("hidden");
            remedyError.classList.remove("hidden");
            document.getElementById("error-message").textContent = data.detail || "Failed to generate remedy. Please check server logs.";
        }
    } catch (err) {
        remedyLoading.classList.add("hidden");
        remedyError.classList.remove("hidden");
        document.getElementById("error-message").textContent = "Network error. Make sure the FastAPI server is running.";
    }
}

// Render Accordion References List
function renderSources(sources) {
    sourcesListContainer.innerHTML = "";
    sourceCount.textContent = sources.length;
    
    if (!sources || sources.length === 0) {
        sourcesListContainer.innerHTML = `
            <div class="empty-state">
                <i class="fa-solid fa-circle-info"></i>
                <p>No matching passages found in the document library. General remedy generated.</p>
            </div>
        `;
        return;
    }
    
    // Render source cards
    sources.forEach(src => {
        const card = document.createElement("div");
        card.className = "source-excerpt-card";
        
        // Convert score to percentage
        const matchPct = Math.round(src.score * 100);
        
        card.innerHTML = `
            <div class="source-card-header">
                <span class="source-book-name"><i class="fa-solid fa-book"></i> ${src.source_book}</span>
                <div>
                    <span class="source-page">Page ${src.page_number}</span>
                    <span class="badge badge-success" style="margin-left: 5px">${matchPct}% Relevance</span>
                </div>
            </div>
            <p class="source-text">"${src.text.trim()}"</p>
        `;
        sourcesListContainer.appendChild(card);
    });
}
