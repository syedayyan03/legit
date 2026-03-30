const API_URL = 'http://127.0.0.1:8000';

// Global state
let currentUser = JSON.parse(localStorage.getItem('currentUser')) || null;
let authToken = localStorage.getItem('authToken') || null;

// Auth Check
function checkAuth() {
    const isDashboardPage = window.location.pathname.includes('dashboard.html');
    const isDetectorPage = window.location.pathname.includes('detector.html');

    if ((isDashboardPage || isDetectorPage) && !authToken) {
        window.location.href = 'login.html';
    }
}

// Analyze Job Function
async function analyzeJob() {
    const urlInput = document.getElementById('jobUrl');
    const url = urlInput.value.trim();

    if (!url) {
        showErrorPopup("⚠️ Empty Input", "Please paste a job link to analyze.");
        return;
    }

    // Basic URL validation
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
        showErrorPopup("⚠️ Invalid URL", "Please enter a valid URL starting with http:// or https://");
        return;
    }

    const modal = document.getElementById('resultModal');
    const loading = document.getElementById('modalLoading');
    const result = document.getElementById('modalResult');

    modal.style.display = 'flex';
    loading.style.display = 'block';
    result.style.display = 'none';

    try {
        const headers = { 'Content-Type': 'application/json' };
        if (authToken) {
            headers['Authorization'] = `Bearer ${authToken}`;
        }

        const response = await fetch(`${API_URL}/analyze-job`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({ url })
        });

        const data = await response.json();

        if (response.ok) {
            if (data.status === "filtered") {
                loading.style.display = 'none';
                modal.style.display = 'none';
                showPopup("Not a Job Website", "The link entered is not related to a job portal.", "warning");
            } else {
                displayResult(data);
            }
        } else {
            loading.style.display = 'none';
            // Show backend error in modal
            const errorMsg = data.detail || "Analysis failed.";
            if (response.status === 401) {
                showResultError("🔒 Session Expired", "Your login session has expired. Please login again.", "#ff9800");
                setTimeout(() => { window.location.href = 'login.html'; }, 2000);
            } else if (response.status === 503) {
                showResultError("🌐 Connection Failed", `Could not connect to the website:\n${url}\n\nThe website may be down or blocking our request.`, "#e74c3c");
            } else if (response.status === 504) {
                showResultError("⏱️ Timeout", `The website took too long to respond:\n${url}\n\nPlease try again later.`, "#e74c3c");
            } else {
                showResultError("❌ Error", errorMsg, "#e74c3c");
            }
        }
    } catch (error) {
        console.error("Error:", error);
        loading.style.display = 'none';
        showResultError(
            "🔌 Connection Error",
            `Could not connect to the LEGIT backend server.\n\nPlease make sure the server is running.\nBackend URL: ${API_URL}`,
            "#e74c3c"
        );
    }
}

// Show error/info inside the modal (styled popup)
function showResultError(title, message, color) {
    const result = document.getElementById('modalResult');
    const statusText = document.getElementById('statusText');
    const confidenceText = document.getElementById('confidenceText');
    const appType = document.getElementById('appType');
    const riskFactors = document.getElementById('riskFactors');
    const dataCollected = document.getElementById('dataCollected');
    const explanation = document.getElementById('explanation');

    statusText.innerText = title;
    statusText.style.color = color || "var(--danger)";
    confidenceText.innerText = "";
    appType.innerText = "N/A";
    riskFactors.innerHTML = '';
    riskFactors.innerText = 'N/A';
    dataCollected.innerHTML = '';
    dataCollected.innerText = 'N/A';
    explanation.innerText = message;

    result.style.display = 'block';
}

// Show error as a quick popup (for input validation before opening modal)
function showErrorPopup(title, message) {
    const modal = document.getElementById('resultModal');
    const loading = document.getElementById('modalLoading');
    modal.style.display = 'flex';
    loading.style.display = 'none';
    showResultError(title, message, "#ff9800");
}

function displayResult(data) {
    const result = document.getElementById('modalResult');
    const statusText = document.getElementById('statusText');
    const confidenceText = document.getElementById('confidenceText');
    const appType = document.getElementById('appType');
    const riskFactors = document.getElementById('riskFactors');
    const dataCollected = document.getElementById('dataCollected');
    const explanation = document.getElementById('explanation');
    const loading = document.getElementById('modalLoading');

    loading.style.display = 'none';

    // Normal result display
    statusText.innerText = data.prediction || "Unknown Status";
    statusText.style.color = data.prediction === "Fake Job" ? "var(--danger)" : "var(--success)";
    
    confidenceText.innerText = data.confidence !== undefined ? `Confidence: ${data.confidence}%` : "";
    appType.innerText = data.type || "N/A";

    riskFactors.innerHTML = '';
    const risks = data.risk_factors || [];
    risks.forEach(risk => {
        const span = document.createElement('span');
        span.className = 'risk-tag';
        span.innerText = risk;
        riskFactors.appendChild(span);
    });
    if (risks.length === 0) riskFactors.innerText = 'No significant risks detected.';

    dataCollected.innerHTML = '';
    const collected = data.data_collected || [];
    collected.forEach(item => {
        const span = document.createElement('span');
        span.className = 'data-tag';
        span.innerText = item;
        dataCollected.appendChild(span);
    });
    if (collected.length === 0) dataCollected.innerText = 'No sensitive data requests detected.';

    explanation.innerText = data.prediction === "Fake Job" 
        ? "This posting shows patterns commonly associated with fraudulent job advertisements. Exercise extreme caution." 
        : "This posting appears legitimate based on our machine learning analysis of similar real job ads.";

    result.style.display = 'block';
}

function closeModal() {
    document.getElementById('resultModal').style.display = 'none';
}

// Custom Modal Popup (replaces alerts and toasts)
function showPopup(title, message, type = 'info') {
    // Remove existing if any
    const existing = document.getElementById('customPopupOverlay');
    if (existing) existing.remove();

    const colors = {
        success: '#2ecc71',
        error: '#e74c3c',
        warning: '#ff9800',
        info: '#3498db'
    };
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };

    // Create overlay
    const overlay = document.createElement('div');
    overlay.id = 'customPopupOverlay';
    overlay.style.cssText = `
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);
        display: flex; justify-content: center; align-items: center;
        z-index: 10000;
    `;

    // Create popup box
    const popup = document.createElement('div');
    popup.className = 'glass';
    popup.style.cssText = `
        background: rgba(15, 23, 42, 0.9);
        padding: 2rem; border-radius: 12px;
        max-width: 400px; width: 90%; text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        animation: popupFade 0.3s ease;
    `;

    popup.innerHTML = `
        <div style="font-size: 3rem; margin-bottom: 1rem;">${icons[type]}</div>
        <h3 style="margin-bottom: 0.5rem; color: ${colors[type]};">${title}</h3>
        <p style="color: var(--text-muted); margin-bottom: 1.5rem;">${message}</p>
        <button id="closePopupBtn" style="
            background: var(--primary); color: white; border: none;
            padding: 0.8rem 2rem; border-radius: 6px; cursor: pointer;
            font-weight: 600; width: 100%;
        ">OK</button>
    `;

    overlay.appendChild(popup);
    document.body.appendChild(overlay);

    // Add animation style
    if (!document.getElementById('popupStyle')) {
        const style = document.createElement('style');
        style.id = 'popupStyle';
        style.textContent = `@keyframes popupFade { from { opacity: 0; transform: scale(0.9); } to { opacity: 1; transform: scale(1); } }`;
        document.head.appendChild(style);
    }

    // Close logic
    document.getElementById('closePopupBtn').onclick = () => overlay.remove();
}

// Signup
async function handleSignup(e) {
    e.preventDefault();
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch(`${API_URL}/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password })
        });

        const data = await response.json();
        if (response.ok) {
            showPopup("Success", "Account created successfully! Redirecting to login...", "success");
            setTimeout(() => { window.location.href = 'login.html'; }, 2000);
        } else {
            showPopup("Signup Failed", data.detail || "Could not create account.", "error");
        }
    } catch (e) {
        showPopup("Connection Error", "Server error. Make sure the backend is running.", "error");
    }
}

// Login
async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();
        if (response.ok) {
            localStorage.setItem('authToken', data.access_token);
            localStorage.setItem('currentUser', JSON.stringify(data.user));
            showPopup("Login Successful", "Redirecting to dashboard...", "success");
            setTimeout(() => { window.location.href = 'dashboard.html'; }, 1500);
        } else {
            showPopup("Login Failed", data.detail || "Invalid email or password.", "error");
        }
    } catch (e) {
        showPopup("Connection Error", "Server error. Make sure the backend is running.", "error");
    }
}

function logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    window.location.href = 'login.html';
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    
    // Attach forms if they exist
    const signupForm = document.getElementById('signupForm');
    if (signupForm) signupForm.addEventListener('submit', handleSignup);
    
    const loginForm = document.getElementById('loginForm');
    if (loginForm) loginForm.addEventListener('submit', handleLogin);

    // Update UI for logged in users
    if (authToken && currentUser) {
        const navLinks = document.querySelector('.nav-links');
        // We only want to update nav links on pages like index.html or other public pages
        if (navLinks && !window.location.pathname.includes('dashboard.html') && !window.location.pathname.includes('detector.html')) {
             navLinks.innerHTML = `
                <a href="index.html">Home</a>
                <a href="dashboard.html">Dashboard</a>
                <span style="color:var(--text-muted); margin-left:1rem;">Hi, ${currentUser.name}</span>
                <a href="#" onclick="logout()" class="btn-login" style="margin-left:1rem;">Logout</a>
            `;
        }
    }
});
