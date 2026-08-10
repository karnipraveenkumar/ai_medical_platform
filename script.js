/* ==========================================================================
   0. Backend API Integration Layer
   ==========================================================================
   The backend (FastAPI) actually mounts only these routers (see
   app/main.py in the backend repo):
     - /auth    (POST /auth/register, POST /auth/login)
     - /patients (full CRUD, JWT-protected, scoped to the logged-in user)
     - /doctors  (full CRUD, NOT auth-protected)
     - /ai       (POST /ai/complete -> { prompt } -> { result })
   Everything else the UI shows (appointments booking, lab reports,
   prescriptions, billing, notifications, medical records) has NO backend
   route mounted yet, even though some models/legacy route files exist in
   the repo under backend/api/*. Those features are intentionally left as
   the original local demo/mock behaviour below - see README for the full
   list of backend work still needed.
   ========================================================================== */

// Change this if your backend runs somewhere else.
const API_BASE_URL = window.API_BASE_URL || 'http://127.0.0.1:8000';

const TOKEN_KEY = 'amp_access_token';
const PATIENT_ID_KEY = 'amp_patient_id';

function getToken() {
    return localStorage.getItem(TOKEN_KEY);
}

function setToken(token) {
    localStorage.setItem(TOKEN_KEY, token);
}

function clearSession() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(PATIENT_ID_KEY);
}

// Decode a JWT payload client-side (no verification - display only).
// The backend signs tokens with { sub: user_id, email }.
function decodeJwtPayload(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const json = decodeURIComponent(
            atob(base64)
                .split('')
                .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
                .join('')
        );
        return JSON.parse(json);
    } catch (e) {
        return null;
    }
}

/**
 * Thin wrapper around fetch() that:
 *  - prefixes API_BASE_URL
 *  - attaches the JWT Authorization header when we have one
 *  - JSON-encodes bodies (unless already a string / FormData)
 *  - throws a normalized Error with a readable message on failure
 *  - logs the user out automatically on 401 (expired/invalid token)
 */
async function apiFetch(path, { method = 'GET', body, auth = true, formEncoded = false, headers = {} } = {}) {
    const finalHeaders = { ...headers };
    let finalBody = body;

    if (formEncoded) {
        finalHeaders['Content-Type'] = 'application/x-www-form-urlencoded';
    } else if (body !== undefined && typeof body !== 'string') {
        finalHeaders['Content-Type'] = 'application/json';
        finalBody = JSON.stringify(body);
    }

    if (auth) {
        const token = getToken();
        if (token) finalHeaders['Authorization'] = `Bearer ${token}`;
    }

    let response;
    try {
        response = await fetch(`${API_BASE_URL}${path}`, {
            method,
            headers: finalHeaders,
            body: finalBody,
        });
    } catch (networkErr) {
        throw new Error(
            `Cannot reach the backend at ${API_BASE_URL}. Is it running? (${networkErr.message})`
        );
    }

    if (response.status === 204) return null;

    let data = null;
    const text = await response.text();
    if (text) {
        try {
            data = JSON.parse(text);
        } catch (e) {
            data = text;
        }
    }

    if (!response.ok) {
        if (response.status === 401 && auth) {
            clearSession();
            showAuthScreen();
        }
        const detail =
            (data && (data.detail || data.message)) ||
            `Request failed with status ${response.status}`;
        throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
    }

    return data;
}

/* ---------------------------- Auth flows ---------------------------- */

function showAuthScreen() {
    const authScreen = document.getElementById('auth-screen');
    const appContainer = document.getElementById('app-container');
    if (authScreen) authScreen.style.display = 'flex';
    if (appContainer) appContainer.style.display = 'none';
}

function showAppScreen() {
    const authScreen = document.getElementById('auth-screen');
    const appContainer = document.getElementById('app-container');
    if (authScreen) authScreen.style.display = 'none';
    if (appContainer) appContainer.style.display = 'flex';
}

function setAuthError(message) {
    const el = document.getElementById('auth-error');
    if (!el) return;
    if (!message) {
        el.style.display = 'none';
        el.innerText = '';
    } else {
        el.style.display = 'block';
        el.innerText = message;
    }
}

function initAuth() {
    const loginTab = document.getElementById('auth-tab-login');
    const registerTab = document.getElementById('auth-tab-register');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');

    if (!loginForm || !registerForm) return;

    loginTab.addEventListener('click', () => {
        loginTab.classList.add('active');
        registerTab.classList.remove('active');
        loginForm.style.display = 'flex';
        registerForm.style.display = 'none';
        setAuthError(null);
    });

    registerTab.addEventListener('click', () => {
        registerTab.classList.add('active');
        loginTab.classList.remove('active');
        registerForm.style.display = 'flex';
        loginForm.style.display = 'none';
        setAuthError(null);
    });

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        setAuthError(null);
        const email = document.getElementById('login-email').value.trim();
        const password = document.getElementById('login-password').value;
        const btn = document.getElementById('login-submit-btn');
        const original = btn.innerText;
        btn.disabled = true;
        btn.innerText = 'Logging in...';

        try {
            // The backend's /auth/login endpoint uses FastAPI's
            // OAuth2PasswordRequestForm, which requires
            // application/x-www-form-urlencoded with "username"/"password"
            // fields (NOT JSON, and NOT "email").
            const params = new URLSearchParams();
            params.set('username', email);
            params.set('password', password);
            params.set('grant_type', 'password');

            const tokenResponse = await apiFetch('/auth/login', {
                method: 'POST',
                body: params.toString(),
                formEncoded: true,
                auth: false,
            });

            setToken(tokenResponse.access_token);
            userState.email = email;
            const payload = decodeJwtPayload(tokenResponse.access_token);
            if (payload && payload.email) userState.email = payload.email;

            await bootstrapAfterLogin();
            showToast('Logged in successfully!');
        } catch (err) {
            setAuthError(err.message);
        } finally {
            btn.disabled = false;
            btn.innerText = original;
        }
    });

    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        setAuthError(null);
        const full_name = document.getElementById('register-name').value.trim();
        const email = document.getElementById('register-email').value.trim();
        const password = document.getElementById('register-password').value;
        const btn = document.getElementById('register-submit-btn');
        const original = btn.innerText;
        btn.disabled = true;
        btn.innerText = 'Creating account...';

        try {
            await apiFetch('/auth/register', {
                method: 'POST',
                body: { full_name, email, password },
                auth: false,
            });

            showToast('Account created! Logging you in...');

            // Backend has no auto-login-after-register, so we log in
            // immediately with the credentials just provided.
            const params = new URLSearchParams();
            params.set('username', email);
            params.set('password', password);
            params.set('grant_type', 'password');

            const tokenResponse = await apiFetch('/auth/login', {
                method: 'POST',
                body: params.toString(),
                formEncoded: true,
                auth: false,
            });

            setToken(tokenResponse.access_token);
            userState.name = full_name;
            userState.email = email;

            await bootstrapAfterLogin();
        } catch (err) {
            setAuthError(err.message);
        } finally {
            btn.disabled = false;
            btn.innerText = original;
        }
    });
}

function logout() {
    clearSession();
    closeModal && window.closeModal && window.closeModal();
    showAuthScreen();
    setAuthError(null);
    showToast('Logged out');
}

// Runs once we have a valid token: loads the user's real patient
// profile and doctor list from the backend, then reveals the dashboard.
async function bootstrapAfterLogin() {
    showAppScreen();
    await Promise.all([loadPatientProfile(), loadDoctors()]);
}

document.addEventListener('DOMContentLoaded', () => {
    initAuth();
    initChart();
    initSymptomChecker();
    initChatAssistant();
    initRoleSwitcher();
    initSearch();
    initModals();

    if (getToken()) {
        bootstrapAfterLogin().catch(() => {
            // Token likely expired/invalid - apiFetch already clears
            // the session and shows the auth screen on a 401.
        });
    } else {
        showAuthScreen();
    }
});

/* ==========================================================================
   1. Interactive Health Trend Chart (SVG render with hover tooltips)
   ========================================================================== */
const trendData = {
    '6m': [
        { month: 'Feb', score: 35, x: 50, y: 165 },
        { month: 'Mar', score: 68, x: 130, y: 100 },
        { month: 'Apr', score: 55, x: 210, y: 125 },
        { month: 'May', score: 72, x: 290, y: 90 },
        { month: 'Jun', score: 62, x: 370, y: 110 },
        { month: 'Jul', score: 82, x: 450, y: 70 },
        { month: 'Aug', score: 65, x: 530, y: 105 }
    ],
    '3m': [
        { month: 'Jun', score: 62, x: 100, y: 110 },
        { month: 'Jul', score: 82, x: 300, y: 70 },
        { month: 'Aug', score: 78, x: 500, y: 78 }
    ],
    '1y': [
        { month: 'Sep', score: 40, x: 50, y: 155 },
        { month: 'Nov', score: 60, x: 150, y: 115 },
        { month: 'Jan', score: 50, x: 250, y: 135 },
        { month: 'Mar', score: 68, x: 350, y: 100 },
        { month: 'May', score: 72, x: 450, y: 90 },
        { month: 'Jul', score: 82, x: 550, y: 70 }
    ]
};

function initChart() {
    const periodSelect = document.getElementById('chart-period');
    if (!periodSelect) return;

    periodSelect.addEventListener('change', (e) => {
        renderChart(e.target.value);
    });

    renderChart('6m');
}

function renderChart(period) {
    const data = trendData[period] || trendData['6m'];
    const pathElem = document.getElementById('chart-line-path');
    const pointsGroup = document.getElementById('chart-points-group');
    const tooltip = document.getElementById('chart-tooltip');

    if (!pathElem || !pointsGroup) return;

    // Generate smooth SVG curve path string (D attribute)
    let d = `M ${data[0].x} ${data[0].y}`;
    for (let i = 1; i < data.length; i++) {
        const prev = data[i - 1];
        const curr = data[i];
        const cx1 = prev.x + (curr.x - prev.x) / 2;
        const cy1 = prev.y;
        const cx2 = prev.x + (curr.x - prev.x) / 2;
        const cy2 = curr.y;
        d += ` C ${cx1} ${cy1}, ${cx2} ${cy2}, ${curr.x} ${curr.y}`;
    }

    pathElem.setAttribute('d', d);

    // Clear and render circles
    pointsGroup.innerHTML = '';
    data.forEach(item => {
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', item.x);
        circle.setAttribute('cy', item.y);
        circle.setAttribute('r', '5');
        circle.setAttribute('class', 'chart-point');

        // Hover events for custom tooltip
        circle.addEventListener('mouseenter', (e) => {
            const rect = circle.getBoundingClientRect();
            const containerRect = document.querySelector('.chart-container').getBoundingClientRect();

            tooltip.innerHTML = `<strong>${item.month} 2025</strong><br>Health Score: <strong>${item.score}%</strong>`;
            tooltip.style.left = `${rect.left - containerRect.left + 5}px`;
            tooltip.style.top = `${rect.top - containerRect.top - 10}px`;
            tooltip.style.opacity = '1';
        });

        circle.addEventListener('mouseleave', () => {
            tooltip.style.opacity = '0';
        });

        pointsGroup.appendChild(circle);
    });
}

/* ==========================================================================
   2. AI Symptom Checker Feature
   ========================================================================== */
const symptomDatabase = [
    {
        keywords: ['headache', 'fever', 'body pain', 'tired'],
        conditions: [
            { name: 'Viral Fever', match: 87 },
            { name: 'Common Cold', match: 65 },
            { name: 'Dengue Fever', match: 25 }
        ],
        recommendations: [
            'Rest and drink plenty of fluids',
            'Take paracetamol for fever relief',
            'Consult doctor if symptoms persist past 3 days',
            'Get blood test if fever continues to spike'
        ]
    },
    {
        keywords: ['cough', 'chest', 'breath', 'throat'],
        conditions: [
            { name: 'Bronchitis / Upper Respiratory', match: 82 },
            { name: 'Seasonal Allergy', match: 60 },
            { name: 'Asthma Flare-up', match: 35 }
        ],
        recommendations: [
            'Use warm steam inhalation twice daily',
            'Stay well-hydrated with warm fluids and tea',
            'Avoid exposure to dust and cold air',
            'Consult pulmonologist if shortness of breath worsens'
        ]
    },
    {
        keywords: ['stomach', 'nausea', 'vomit', 'pain', 'acid'],
        conditions: [
            { name: 'Acute Gastritis', match: 85 },
            { name: 'Food Poisoning', match: 70 },
            { name: 'Indigestion', match: 45 }
        ],
        recommendations: [
            'Follow a light BRAT diet (Bananas, Rice, Applesauce, Toast)',
            'Avoid spicy, fatty, and caffeine-containing foods',
            'Sip oral rehydration salts (ORS) slowly',
            'Seek immediate medical care if severe cramping occurs'
        ]
    }
];

function initSymptomChecker() {
    const btn = document.getElementById('btn-check-symptoms');
    const input = document.getElementById('symptom-input');

    if (!btn || !input) return;

    btn.addEventListener('click', async () => {
        const query = input.value.trim();
        if (!query) {
            alert('Please describe your symptoms before analyzing.');
            return;
        }

        const originalText = btn.innerHTML;
        btn.innerHTML = `<div class="spinner"></div> Analyzing...`;
        btn.disabled = true;

        // Backend only exposes a generic POST /ai/complete (prompt -> text)
        // endpoint - there is no dedicated /symptom-checker route that
        // returns structured condition-match percentages. So we ask the
        // model for a diagnostic-style write-up and render the real text
        // it returns, instead of fabricating fake match percentages.
        const prompt =
            'You are a medical AI assistant inside a symptom checker tool. ' +
            'A patient describes these symptoms: "' + query + '". ' +
            'List 2-4 possible (non-diagnostic) conditions this could be, and ' +
            'give 3-5 practical recommendations. Keep it concise and end with a ' +
            'reminder to consult a licensed doctor for an accurate diagnosis.';

        try {
            const data = await apiFetch('/ai/complete', {
                method: 'POST',
                body: { prompt },
            });
            renderSymptomResults(data.result);
        } catch (err) {
            renderSymptomError(err.message);
        } finally {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    });
}

function renderSymptomResults(resultText) {
    const container = document.getElementById('ai-results-container');
    if (!container) return;

    container.innerHTML = `
        <div class="ai-results-box">
            <h4 class="results-col-title">AI Assessment</h4>
            <div style="white-space:pre-wrap; font-size:0.88rem; color:var(--text-secondary); line-height:1.6; background:#f8fafc; border:1px solid var(--border-color); border-radius:12px; padding:14px;">${escapeHtml(resultText)}</div>
            <div class="disclaimer-text">
                <strong>Disclaimer:</strong> This is an AI-generated suggestion based on user input. Please consult a qualified doctor for accurate diagnostic evaluation.
            </div>
        </div>
    `;
}

function renderSymptomError(message) {
    const container = document.getElementById('ai-results-container');
    if (!container) return;
    container.innerHTML = `
        <div class="ai-results-box">
            <div style="font-size:0.88rem; color:var(--accent-red-text); background:var(--accent-red-bg); border:1px solid #fecaca; border-radius:12px; padding:14px;">
                <strong>AI service unavailable:</strong> ${escapeHtml(message)}
            </div>
        </div>
    `;
}

/* ==========================================================================
   3. Live AI Chat Assistant Component
   ========================================================================== */
function initChatAssistant() {
    const sendBtn = document.getElementById('chat-send-btn');
    const input = document.getElementById('chat-input');
    const chatContainer = document.getElementById('chat-messages');

    if (!sendBtn || !input) return;

    async function sendMessage(text) {
        const msgText = text || input.value.trim();
        if (!msgText) return;

        // Append User Message
        const userMsg = document.createElement('div');
        userMsg.className = 'chat-message user';
        userMsg.innerHTML = `<div class="bubble">${escapeHtml(msgText)}</div>`;
        chatContainer.appendChild(userMsg);

        if (!text) input.value = '';
        chatContainer.scrollTop = chatContainer.scrollHeight;

        // Typing indicator while we wait for the real backend call
        const typingMsg = document.createElement('div');
        typingMsg.className = 'chat-message bot';
        typingMsg.innerHTML = `
            <div class="ai-avatar-icon" style="width:28px; height:28px; font-size:12px; flex-shrink:0;">🤖</div>
            <div class="bubble"><div class="spinner"></div></div>
        `;
        chatContainer.appendChild(typingMsg);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        // Backend only exposes a generic POST /ai/complete endpoint (no
        // conversation/session memory), so each message is sent as a
        // fresh prompt with light framing for a medical-assistant persona.
        const prompt =
            'You are a friendly AI assistant inside a patient health dashboard. ' +
            'Answer the patient\'s message helpfully and concisely.\n\nPatient: ' +
            msgText;

        let botReply;
        try {
            const data = await apiFetch('/ai/complete', {
                method: 'POST',
                body: { prompt },
            });
            botReply = escapeHtml(data.result);
        } catch (err) {
            botReply = `<span style="color:var(--accent-red-text);">AI service unavailable: ${escapeHtml(err.message)}</span>`;
        }

        typingMsg.innerHTML = `
            <div class="ai-avatar-icon" style="width:28px; height:28px; font-size:12px; flex-shrink:0;">🤖</div>
            <div class="bubble">${botReply}</div>
        `;
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    sendBtn.addEventListener('click', () => sendMessage());
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    // Quick Prompt Chips
    document.querySelectorAll('.quick-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            const prompt = chip.dataset.prompt || chip.innerText;
            sendMessage(`Tell me about ${prompt}`);
        });
    });
}

function getAIResponse(text) {
    const lower = text.toLowerCase();
    if (lower.includes('symptom')) {
        return "I can help evaluate your symptoms! You can use the AI Symptom Checker in the center panel or describe what you're feeling right now.";
    } else if (lower.includes('lab') || lower.includes('report')) {
        return "Your latest report **Complete Blood Count (31 Jul 2025)** is normal. Thyroid profile shows slightly elevated TSH (High TSH).";
    } else if (lower.includes('medication') || lower.includes('prescription')) {
        return "You have 3 active prescriptions from Dr. Rahul Sharma and Dr. Anjali Verma. Make sure to take Paracetamol 500mg after meals.";
    } else if (lower.includes('appointment')) {
        return "You have an upcoming appointment tomorrow at 10:30 AM with **Dr. Rahul Sharma** (General Physician).";
    }
    return "Thank you for asking! Based on your health metrics, your overall score is 82%. How else may I assist your care plan today?";
}

function escapeHtml(str) {
    return str.replace(/[&<>"']/g, function (m) {
        return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[m];
    });
}

/* ==========================================================================
   4. Role Switcher Tabs (Patient / Doctor / Admin)
   ========================================================================== */
function initRoleSwitcher() {
    const roleBtns = document.querySelectorAll('.role-btn');
    const userRoleText = document.querySelector('.user-role');
    const userNameText = document.querySelector('.user-name');

    roleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            roleBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const role = btn.dataset.role;
            if (role === 'patient') {
                if (userRoleText) userRoleText.innerText = 'Patient';
                if (userNameText) userNameText.innerText = 'Praveen Kumar';
            } else if (role === 'doctor') {
                if (userRoleText) userRoleText.innerText = 'Cardiologist';
                if (userNameText) userNameText.innerText = 'Dr. Rahul Sharma';
            } else if (role === 'admin') {
                if (userRoleText) userRoleText.innerText = 'System Admin';
                if (userNameText) userNameText.innerText = 'Admin Portal';
            }
        });
    });
}

/* ==========================================================================
   5. Global Search Filter
   ========================================================================== */
function initSearch() {
    const searchInput = document.getElementById('global-search');
    if (!searchInput) return;

    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();

        // Filter appointments
        document.querySelectorAll('.appointment-item').forEach(item => {
            const text = item.innerText.toLowerCase();
            item.style.display = text.includes(query) ? 'flex' : 'none';
        });

        // Filter lab reports
        document.querySelectorAll('.report-item').forEach(item => {
            const text = item.innerText.toLowerCase();
            item.style.display = text.includes(query) ? 'flex' : 'none';
        });
    });
}

/* ==========================================================================
   6. Modal & View Handling (Edit Profile, Reschedule, Billing, Prescriptions, Toast)
   ========================================================================== */

// Helper Toast Notification Function
function showToast(message, icon = '✓') {
    let toast = document.getElementById('global-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'global-toast';
        toast.className = 'toast-notification';
        document.body.appendChild(toast);
    }
    toast.innerHTML = `<div class="toast-icon">${icon}</div> <span>${message}</span>`;
    toast.classList.add('show');
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3200);
}

// User state store. first_name/last_name/email/phone are backed by the
// real /patients API (see loadPatientProfile below); bloodGroup/emergency
// contact/address have no matching column on the backend Patient model,
// so they stay frontend-only until that's added (see README).
const userState = {
    name: 'Praveen Kumar',
    email: 'praveen.k@example.com',
    phone: '+91 98765 43210',
    bloodGroup: 'O Positive (O+)',
    emergency: '+91 98123 45678',
    address: 'Flat 402, Green Avenue, Bengaluru'
};

// Backend patient record id currently backing userState, once known.
let currentPatientId = null;

// Fetch the logged-in user's own Patient record (GET /patients returns
// only patients owned by the authenticated user). If none exists yet,
// leave currentPatientId null - it will be created the first time the
// user saves the Edit Profile form.
async function loadPatientProfile() {
    try {
        const patients = await apiFetch('/patients');
        if (Array.isArray(patients) && patients.length > 0) {
            const p = patients[0];
            currentPatientId = p.id;
            localStorage.setItem(PATIENT_ID_KEY, String(p.id));
            userState.name = `${p.first_name} ${p.last_name}`.trim();
            userState.email = p.email;
            userState.phone = p.phone || userState.phone;
        }

        document.querySelectorAll('.user-name').forEach(el => el.innerText = userState.name);
        const greeting = document.querySelector('.greeting-text h1');
        if (greeting) greeting.innerHTML = `Welcome back, ${escapeHtml(userState.name.split(' ')[0])} <span>👋</span>`;
    } catch (err) {
        showToast(`Could not load patient profile: ${err.message}`, '⚠');
    }
}

// Loads real doctors from GET /doctors and (a) fills the "Book
// Appointment" doctor <select>, (b) caches them for renderDoctorsModal().
let doctorsCache = [];
async function loadDoctors() {
    try {
        doctorsCache = await apiFetch('/doctors', { auth: false });
    } catch (err) {
        doctorsCache = [];
        showToast(`Could not load doctors: ${err.message}`, '⚠');
    }
}

function renderDoctorsModal() {
    if (!doctorsCache || doctorsCache.length === 0) {
        openModal('My Doctors', `
            <div style="padding:10px 0; font-size:0.9rem; color:var(--text-secondary);">
                No doctors found on the server yet.
            </div>
        `);
        return;
    }

    const rows = doctorsCache.map(d => `
        <div style="padding:12px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; display:flex; flex-direction:column; gap:2px;">
            <strong style="font-size:0.9rem; color:#0f172a;">Dr. ${escapeHtml(d.full_name)}</strong>
            <span style="font-size:0.8rem; color:#475569;">${escapeHtml(d.specialty || 'General')}</span>
            <span style="font-size:0.78rem; color:#94a3b8;">${escapeHtml(d.email || '')}${d.phone ? ' • ' + escapeHtml(d.phone) : ''}</span>
        </div>
    `).join('');

    openModal('My Doctors', `<div style="display:flex; flex-direction:column; gap:10px;">${rows}</div>`);
}

function initModals() {
    const modalOverlay = document.getElementById('modal-overlay');
    const modalTitle = document.getElementById('modal-title');
    const modalBody = document.getElementById('modal-body');
    const closeBtn = document.getElementById('modal-close');

    if (!modalOverlay) return;

    window.openModal = function (title, contentHtml) {
        if (modalTitle) modalTitle.innerText = title;
        if (modalBody) modalBody.innerHTML = contentHtml;
        modalOverlay.classList.add('active');
    };

    window.closeModal = function () {
        if (modalOverlay) modalOverlay.classList.remove('active');
    };

    if (closeBtn) closeBtn.addEventListener('click', window.closeModal);
    modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) window.closeModal();
    });

    // Render Edit Profile Form
    window.renderEditProfileForm = function () {
        openModal('Edit Profile Information', `
            <form id="edit-profile-form" style="display:flex; flex-direction:column; gap:14px;">
                <div class="form-group">
                    <label class="form-label">Full Name</label>
                    <input type="text" id="input-profile-name" class="form-input" value="${escapeHtml(userState.name)}" required />
                </div>
                <div class="form-group">
                    <label class="form-label">Email Address</label>
                    <input type="email" id="input-profile-email" class="form-input" value="${escapeHtml(userState.email)}" required />
                </div>
                <div class="form-group">
                    <label class="form-label">Phone Number</label>
                    <input type="tel" id="input-profile-phone" class="form-input" value="${escapeHtml(userState.phone)}" required />
                </div>
                <div class="form-group">
                    <label class="form-label">Blood Group</label>
                    <select id="input-profile-blood" class="form-select">
                        <option ${userState.bloodGroup.includes('O+') ? 'selected' : ''}>O Positive (O+)</option>
                        <option ${userState.bloodGroup.includes('A+') ? 'selected' : ''}>A Positive (A+)</option>
                        <option ${userState.bloodGroup.includes('B+') ? 'selected' : ''}>B Positive (B+)</option>
                        <option ${userState.bloodGroup.includes('AB+') ? 'selected' : ''}>AB Positive (AB+)</option>
                        <option ${userState.bloodGroup.includes('O-') ? 'selected' : ''}>O Negative (O-)</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Emergency Contact</label>
                    <input type="tel" id="input-profile-emergency" class="form-input" value="${escapeHtml(userState.emergency)}" required />
                </div>
                <div style="display:flex; gap:10px; margin-top:8px;">
                    <button type="submit" class="btn-primary" style="flex:1; justify-content:center;">Save Profile Changes</button>
                    <button type="button" onclick="renderProfileView()" style="flex:1; background:#f1f5f9; color:#475569; border:1px solid #cbd5e1; border-radius:12px; font-weight:700; cursor:pointer;">Cancel</button>
                </div>
            </form>
        `);

        document.getElementById('edit-profile-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const fullName = document.getElementById('input-profile-name').value.trim();
            const email = document.getElementById('input-profile-email').value.trim();
            const phone = document.getElementById('input-profile-phone').value.trim();
            const bloodGroup = document.getElementById('input-profile-blood').value;
            const emergency = document.getElementById('input-profile-emergency').value.trim();

            const nameParts = fullName.split(' ');
            const first_name = nameParts.shift() || fullName;
            const last_name = nameParts.join(' ') || first_name;

            const submitBtn = e.target.querySelector('button[type="submit"]');
            const originalLabel = submitBtn.innerText;
            submitBtn.disabled = true;
            submitBtn.innerText = 'Saving...';

            try {
                let patient;
                if (currentPatientId) {
                    patient = await apiFetch(`/patients/${currentPatientId}`, {
                        method: 'PUT',
                        body: { first_name, last_name, email, phone },
                    });
                } else {
                    patient = await apiFetch('/patients', {
                        method: 'POST',
                        body: { first_name, last_name, email, phone },
                    });
                    currentPatientId = patient.id;
                    localStorage.setItem(PATIENT_ID_KEY, String(patient.id));
                }

                userState.name = `${patient.first_name} ${patient.last_name}`.trim();
                userState.email = patient.email;
                userState.phone = patient.phone || phone;
                // Not part of the backend Patient schema yet - kept client-side.
                userState.bloodGroup = bloodGroup;
                userState.emergency = emergency;

                // Update UI elements across dashboard
                document.querySelectorAll('.user-name').forEach(el => el.innerText = userState.name);
                const greeting = document.querySelector('.greeting-text h1');
                if (greeting) greeting.innerHTML = `Welcome back, ${escapeHtml(userState.name.split(' ')[0])} <span>👋</span>`;

                window.closeModal();
                showToast('Profile updated successfully!');
            } catch (err) {
                showToast(`Could not save profile: ${err.message}`, '⚠');
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerText = originalLabel;
            }
        });
    };

    // Render Profile View Modal
    window.renderProfileView = function () {
        openModal('Patient Profile', `
            <div style="display:flex; flex-direction:column; align-items:center; gap:12px; text-align:center;">
                <img src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=120" style="width:76px; height:76px; border-radius:50%; object-fit:cover; border:3px solid #2563eb; box-shadow:0 4px 12px rgba(37,99,235,0.2);">
                <div>
                    <h3 style="font-size:1.15rem; color:#0f172a; margin-bottom:2px;">${escapeHtml(userState.name)}</h3>
                    <span style="font-size:0.8rem; color:#2563eb; font-weight:700;">Patient ID: ${currentPatientId ? '#' + escapeHtml(String(currentPatientId)) : 'Not saved yet'}</span>
                </div>
                <div style="width:100%; text-align:left; background:#f8fafc; padding:14px; border-radius:12px; font-size:0.85rem; border:1px solid #e2e8f0; display:flex; flex-direction:column; gap:8px; margin:6px 0;">
                    <div style="display:flex; justify-content:space-between;"><strong>Email:</strong> <span>${escapeHtml(userState.email)}</span></div>
                    <div style="display:flex; justify-content:space-between;"><strong>Phone:</strong> <span>${escapeHtml(userState.phone)}</span></div>
                    <div style="display:flex; justify-content:space-between;"><strong>Blood Group:</strong> <span>${escapeHtml(userState.bloodGroup)}</span></div>
                    <div style="display:flex; justify-content:space-between;"><strong>Emergency Contact:</strong> <span>${escapeHtml(userState.emergency)}</span></div>
                </div>
                <div style="display:flex; gap:10px; width:100%;">
                    <button onclick="renderEditProfileForm()" class="btn-primary" style="flex:1; justify-content:center;">Edit Profile</button>
                    <button onclick="logout()" style="flex:1; background:#fef2f2; color:#ef4444; border:1px solid #fecaca; border-radius:12px; font-weight:700; cursor:pointer;">Logout</button>
                </div>
            </div>
        `);
    };

    // Render Reschedule Modal
    window.renderRescheduleModal = function (appointmentItem, doctorName, specialtyTitle) {
        openModal(`Reschedule Appointment`, `
            <form id="reschedule-form" style="display:flex; flex-direction:column; gap:14px;">
                <div class="form-group">
                    <label class="form-label">Doctor / Specialist</label>
                    <input type="text" class="form-input" value="${escapeHtml(doctorName)} (${escapeHtml(specialtyTitle)})" disabled style="background:#f1f5f9; color:#64748b;" />
                </div>
                <div class="form-group">
                    <label class="form-label">Select New Date</label>
                    <input type="date" id="reschedule-date" class="form-input" required value="2025-08-20" />
                </div>
                <div class="form-group">
                    <label class="form-label">Select Time Slot</label>
                    <select id="reschedule-time" class="form-select">
                        <option>09:30 AM</option>
                        <option selected>11:00 AM</option>
                        <option>02:30 PM</option>
                        <option>04:30 PM</option>
                        <option>06:00 PM</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Reason for Rescheduling (Optional)</label>
                    <input type="text" id="reschedule-reason" class="form-input" placeholder="e.g., Personal work / Travel" />
                </div>
                <div style="display:flex; gap:10px; margin-top:8px;">
                    <button type="submit" class="btn-primary" style="flex:1; justify-content:center;">Save New Schedule</button>
                    <button type="button" onclick="closeModal()" style="flex:1; background:#f1f5f9; color:#475569; border:1px solid #cbd5e1; border-radius:12px; font-weight:700; cursor:pointer;">Cancel</button>
                </div>
            </form>
        `);

        document.getElementById('reschedule-form').addEventListener('submit', (e) => {
            e.preventDefault();
            const newDateVal = document.getElementById('reschedule-date').value;
            const newTimeVal = document.getElementById('reschedule-time').value;

            // Format date for badge (e.g. 2025-08-20 -> 20 Aug)
            const dateObj = new Date(newDateVal);
            const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
            const dayStr = String(dateObj.getDate()).padStart(2, '0');
            const monthStr = months[dateObj.getMonth()] || 'Aug';

            if (appointmentItem) {
                const dayEl = appointmentItem.querySelector('.date-day');
                const monthEl = appointmentItem.querySelector('.date-month');
                const timeEl = appointmentItem.querySelector('.appointment-time');
                if (dayEl) dayEl.innerText = dayStr;
                if (monthEl) monthEl.innerText = monthStr;
                if (timeEl) timeEl.innerText = newTimeVal;
            }

            window.closeModal();
            showToast(`Appointment rescheduled to ${dayStr} ${monthStr} at ${newTimeVal}`);
        });
    };

    // Render Billing & Payments Modal
    window.renderBillingModal = function () {
        openModal('Billing & Payments', `
            <div style="display:flex; flex-direction:column; gap:14px;">
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:14px;">
                    <div style="font-size:0.8rem; color:#64748b; font-weight:700; text-transform:uppercase;">Current Unpaid Invoice</div>
                    <div style="font-size:1.6rem; font-weight:800; color:#0f172a; margin:4px 0;">₹ 1,700.00</div>
                    <div style="font-size:0.8rem; color:#475569;">Due Date: 15 Aug 2025 • Invoice #INV-2025-88</div>
                </div>

                <div style="font-size:0.85rem; font-weight:700; color:#0f172a; margin-top:4px;">Itemized Summary</div>
                <div style="font-size:0.85rem; display:flex; flex-direction:column; gap:8px;">
                    <div style="display:flex; justify-content:space-between; padding-bottom:6px; border-bottom:1px dashed #e2e8f0;">
                        <span>Doctor Consultation (Dr. Rahul Sharma)</span>
                        <strong>₹ 500.00</strong>
                    </div>
                    <div style="display:flex; justify-content:space-between; padding-bottom:6px; border-bottom:1px dashed #e2e8f0;">
                        <span>Complete Blood Count & Liver Test</span>
                        <strong>₹ 1,200.00</strong>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-weight:800; font-size:0.95rem; color:#0f172a; padding-top:4px;">
                        <span>Total Payable Amount</span>
                        <span>₹ 1,700.00</span>
                    </div>
                </div>

                <form id="payment-form" style="margin-top:10px; display:flex; flex-direction:column; gap:12px;">
                    <div class="form-group">
                        <label class="form-label">Payment Method</label>
                        <select class="form-select" id="payment-method">
                            <option>UPI / GPay / PhonePe</option>
                            <option>Credit / Debit Card</option>
                            <option>Net Banking</option>
                        </select>
                    </div>
                    <button type="submit" class="btn-primary" style="width:100%; justify-content:center;">Pay ₹1,700 Now</button>
                </form>
            </div>
        `);

        document.getElementById('payment-form').addEventListener('submit', (e) => {
            e.preventDefault();
            window.closeModal();
            showToast('Payment of ₹1,700 received successfully! Receipt sent to email.');
        });
    };

    // Render Prescriptions Modal
    window.renderPrescriptionsModal = function () {
        openModal('My Prescriptions', `
            <div style="display:flex; flex-direction:column; gap:14px;">
                <div style="font-size:0.85rem; color:#475569;">Active Medications prescribed by your physicians:</div>
                <div style="display:flex; flex-direction:column; gap:10px;">
                    <div style="padding:12px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <strong style="font-size:0.9rem; color:#0f172a;">Paracetamol 500mg</strong>
                            <div style="font-size:0.78rem; color:#64748b;">1 Tablet after meals • 5 Days remaining</div>
                        </div>
                        <span class="badge-pill normal">Active</span>
                    </div>
                    <div style="padding:12px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <strong style="font-size:0.9rem; color:#0f172a;">Amoxicillin 250mg</strong>
                            <div style="font-size:0.78rem; color:#64748b;">1 Capsule twice daily • 3 Days remaining</div>
                        </div>
                        <span class="badge-pill normal">Active</span>
                    </div>
                    <div style="padding:12px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <strong style="font-size:0.9rem; color:#0f172a;">Cetirizine 10mg</strong>
                            <div style="font-size:0.78rem; color:#64748b;">1 Tablet at bedtime as needed</div>
                        </div>
                        <span class="badge-pill normal">Active</span>
                    </div>
                </div>
                <button onclick="showToast('Refill request submitted to Pharmacy!'); closeModal();" class="btn-primary" style="width:100%; justify-content:center; margin-top:6px;">Request Medication Refill</button>
            </div>
        `);
    };

    // Render Medical Records Modal
    window.renderMedicalRecordsModal = function () {
        openModal('Medical Records & Clinical History', `
            <div style="display:flex; flex-direction:column; gap:12px;">
                <div style="display:flex; gap:8px; border-bottom:1px solid #e2e8f0; padding-bottom:8px;">
                    <span style="font-size:0.85rem; font-weight:700; color:#2563eb; border-bottom:2px solid #2563eb; padding-bottom:4px;">Medical History</span>
                </div>
                <div style="display:flex; flex-direction:column; gap:10px; max-height:260px; overflow-y:auto;">
                    <div style="padding:10px 14px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px;">
                        <strong style="font-size:0.85rem; color:#0f172a;">Annual Health Checkup</strong>
                        <div style="font-size:0.78rem; color:#64748b;">Dr. Rahul Sharma • 12 Jan 2025</div>
                        <div style="font-size:0.8rem; color:#475569; margin-top:4px;">Blood pressure normal. Advised light cardio and vitamin D supplements.</div>
                    </div>
                    <div style="padding:10px 14px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px;">
                        <strong style="font-size:0.85rem; color:#0f172a;">Vaccination: Hepatitis B Booster</strong>
                        <div style="font-size:0.78rem; color:#64748b;">Apollo Clinic • 05 Nov 2024</div>
                        <div style="font-size:0.8rem; color:#475569; margin-top:4px;">Dose completed successfully. Next booster due in 2029.</div>
                    </div>
                </div>
                <button onclick="showToast('New clinical record draft opened.'); closeModal();" class="btn-primary" style="width:100%; justify-content:center; margin-top:6px;">Add New Record</button>
            </div>
        `);
    };

    // Render Health Summary Modal
    window.renderHealthSummaryModal = function () {
        openModal('Health Metrics & Vitals Summary', `
            <div style="display:flex; flex-direction:column; gap:14px;">
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
                    <div style="padding:12px; background:#eff6ff; border:1px solid #bfdbfe; border-radius:12px;">
                        <span style="font-size:0.75rem; color:#1d4ed8; font-weight:700; text-transform:uppercase;">Blood Pressure</span>
                        <div style="font-size:1.3rem; font-weight:800; color:#1e40af; margin-top:2px;">120 / 80</div>
                        <span style="font-size:0.725rem; color:#1e40af;">mmHg • Normal</span>
                    </div>
                    <div style="padding:12px; background:#f0fdf4; border:1px solid #bbf7d0; border-radius:12px;">
                        <span style="font-size:0.75rem; color:#15803d; font-weight:700; text-transform:uppercase;">Heart Rate</span>
                        <div style="font-size:1.3rem; font-weight:800; color:#166534; margin-top:2px;">72 bpm</div>
                        <span style="font-size:0.725rem; color:#166534;">Resting • Optimal</span>
                    </div>
                    <div style="padding:12px; background:#faf5ff; border:1px solid #e9d5ff; border-radius:12px;">
                        <span style="font-size:0.75rem; color:#7e22ce; font-weight:700; text-transform:uppercase;">Oxygen (SpO2)</span>
                        <div style="font-size:1.3rem; font-weight:800; color:#6b21a8; margin-top:2px;">98%</div>
                        <span style="font-size:0.725rem; color:#6b21a8;">Normal Level</span>
                    </div>
                    <div style="padding:12px; background:#fff7ed; border:1px solid #fed7aa; border-radius:12px;">
                        <span style="font-size:0.75rem; color:#c2410c; font-weight:700; text-transform:uppercase;">BMI Index</span>
                        <div style="font-size:1.3rem; font-weight:800; color:#9a3412; margin-top:2px;">22.4</div>
                        <span style="font-size:0.725rem; color:#9a3412;">Healthy Weight</span>
                    </div>
                </div>
                <button onclick="closeModal()" class="btn-primary" style="width:100%; justify-content:center;">Close Vitals Summary</button>
            </div>
        `);
    };

    // Wire Quick Action Buttons
    const bookBtn = document.getElementById('action-book-app');
    if (bookBtn) {
        bookBtn.addEventListener('click', (e) => {
            e.preventDefault();
            // Doctor options come from the real GET /doctors endpoint when
            // available; falls back to the original static list otherwise.
            const doctorOptionsHtml = (doctorsCache && doctorsCache.length > 0)
                ? doctorsCache.map(d => `<option>${escapeHtml(d.specialty || 'General')} - Dr. ${escapeHtml(d.full_name)}</option>`).join('')
                : `
                    <option>General Physician - Dr. Rahul Sharma</option>
                    <option>Cardiologist - Dr. Anjali Verma</option>
                    <option>Dentist - Dr. Meena Iyer</option>
                `;

            openModal('Book New Appointment', `
                <form id="book-form" style="display:flex; flex-direction:column; gap:12px;">
                    <div class="form-group">
                        <label class="form-label">Select Department / Specialist</label>
                        <select class="form-select" required>
                            ${doctorOptionsHtml}
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Preferred Date & Time</label>
                        <input type="datetime-local" class="form-input" required value="2025-08-10T10:30" />
                    </div>
                    <p style="font-size:0.75rem; color:var(--text-muted);">Note: appointment booking is not yet wired to a backend endpoint (none exists). This confirms locally only.</p>
                    <button type="submit" class="btn-primary" style="width:100%; justify-content:center;">Confirm Booking</button>
                </form>
            `);

            document.getElementById('book-form').addEventListener('submit', (ev) => {
                ev.preventDefault();
                closeModal();
                showToast('Appointment booked successfully! (local demo only)');
            });
        });
    }

    const uploadBtn = document.getElementById('action-upload-rep');
    if (uploadBtn) {
        uploadBtn.addEventListener('click', (e) => {
            e.preventDefault();
            openModal('Upload Lab Report', `
                <form id="upload-form" style="display:flex; flex-direction:column; gap:12px;">
                    <div class="form-group">
                        <label class="form-label">Report Title</label>
                        <input type="text" id="report-title-input" class="form-input" placeholder="e.g., Fasting Blood Sugar" required />
                    </div>
                    <div class="form-group">
                        <label class="form-label">Select File (PDF / JPG)</label>
                        <input type="file" class="form-input" required />
                    </div>
                    <button type="submit" class="btn-primary" style="width:100%; justify-content:center;">Upload & Analyze with AI</button>
                </form>
            `);

            document.getElementById('upload-form').addEventListener('submit', (ev) => {
                ev.preventDefault();
                const repTitle = document.getElementById('report-title-input').value.trim() || 'Uploaded Lab Report';
                closeModal();
                showToast(`Report '${repTitle}' uploaded successfully!`);
            });
        });
    }

    const supportBtn = document.getElementById('btn-contact-support');
    if (supportBtn) {
        supportBtn.addEventListener('click', () => {
            openModal('Contact Medical Support 24/7', `
                <div style="text-align:center; padding:10px; display:flex; flex-direction:column; align-items:center; gap:12px;">
                    <div style="width:54px; height:54px; border-radius:50%; background:#eff6ff; color:#2563eb; font-size:1.6rem; display:flex; align-items:center; justify-content:center;">📞</div>
                    <div>
                        <h3 style="margin-bottom:4px; color:#0f172a;">Emergency Support Line</h3>
                        <p style="font-size:1.1rem; font-weight:800; color:#2563eb;">+1 (800) 555-0199</p>
                    </div>
                    <p style="font-size:0.85rem; color:#64748b; line-height:1.4;">Our team of certified medical officers is on standby to assist you around the clock.</p>
                    <button onclick="showToast('Calling support hotline...'); closeModal();" class="btn-primary" style="width:100%; justify-content:center;">Call Hotline Now</button>
                </div>
            `);
        });
    }

    // Attach click listeners to sidebar nav items
    document.querySelectorAll('.sidebar .nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            document.querySelectorAll('.sidebar .nav-item').forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
            const title = item.innerText.trim();

            if (title.includes('AI Symptom Checker')) {
                document.querySelector('.ai-checker-card')?.scrollIntoView({ behavior: 'smooth' });
            } else if (title.includes('AI Chat Assistant')) {
                document.getElementById('chat-input')?.focus();
            } else if (title.includes('Prescriptions')) {
                renderPrescriptionsModal();
            } else if (title.includes('Billing & Payments')) {
                renderBillingModal();
            } else if (title.includes('Medical Records')) {
                renderMedicalRecordsModal();
            } else if (title.includes('Health Summary')) {
                renderHealthSummaryModal();
            } else if (title.includes('Profile Settings')) {
                renderEditProfileForm();
            } else if (title.includes('My Doctors')) {
                renderDoctorsModal();
            } else {
                openModal(title, `
                    <div style="padding:10px 0;">
                        <p style="font-size:0.9rem; color:#475569; margin-bottom:12px;">Viewing <strong>${escapeHtml(title)}</strong> records.</p>
                        <div style="background:#f8fafc; padding:14px; border-radius:12px; border:1px solid #e2e8f0; font-size:0.85rem;">
                            ✅ All records up to date.<br>
                            📊 Status: Synchronized with Health Cloud.
                        </div>
                    </div>
                `);
            }
        });
    });

    // Attach click listeners to stat links & cards
    document.querySelectorAll('.stat-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const card = link.closest('.stat-card');
            const title = card?.querySelector('.stat-title')?.innerText || 'Details';
            if (title.includes('Prescriptions')) {
                renderPrescriptionsModal();
            } else if (title.includes('Health Score')) {
                renderHealthSummaryModal();
            } else {
                const val = card?.querySelector('.stat-value')?.innerText || '';
                const detail = card?.querySelector('.stat-detail')?.innerText || '';
                openModal(title, `
                    <div style="padding:10px 0;">
                        <div style="font-size:1.8rem; font-weight:800; color:#2563eb; margin-bottom:8px;">${escapeHtml(val)}</div>
                        <p style="font-size:0.9rem; color:#475569; margin-bottom:16px;">${escapeHtml(detail)}</p>
                        <button onclick="closeModal()" class="btn-primary" style="width:100%; justify-content:center;">Close Details</button>
                    </div>
                `);
            }
        });
    });

    // Attach click listeners to Appointment Items
    document.querySelectorAll('.appointment-item').forEach(item => {
        item.addEventListener('click', () => {
            const doctor = item.querySelector('.doctor-name')?.innerText || 'Doctor';
            const specialty = item.querySelector('.specialty-title')?.innerText || 'Consultation';
            const time = item.querySelector('.appointment-time')?.innerText || '';
            openModal(`Appointment - ${escapeHtml(doctor)}`, `
                <div style="padding:10px 0; display:flex; flex-direction:column; gap:10px;">
                    <p style="font-size:0.9rem;"><strong>Specialty:</strong> ${escapeHtml(specialty)}</p>
                    <p style="font-size:0.9rem;"><strong>Scheduled Time:</strong> ${escapeHtml(time)}</p>
                    <p style="font-size:0.9rem;"><strong>Status:</strong> <span class="badge-pill confirmed">Confirmed</span></p>
                    <div style="display:flex; gap:10px; margin-top:8px;">
                        <button id="btn-reschedule-trigger" class="btn-primary" style="flex:1; justify-content:center;">Reschedule</button>
                        <button id="btn-cancel-trigger" style="flex:1; background:#fef2f2; color:#ef4444; border:1px solid #fecaca; border-radius:12px; font-weight:700; cursor:pointer;">Cancel</button>
                    </div>
                </div>
            `);

            document.getElementById('btn-reschedule-trigger')?.addEventListener('click', () => {
                renderRescheduleModal(item, doctor, specialty);
            });

            document.getElementById('btn-cancel-trigger')?.addEventListener('click', () => {
                const badge = item.querySelector('.badge-pill');
                if (badge) {
                    badge.className = 'badge-pill warning';
                    badge.innerText = 'Cancelled';
                }
                closeModal();
                showToast('Appointment cancelled');
            });
        });
    });

    // Attach click listeners to Lab Report items
    document.querySelectorAll('.report-item').forEach(item => {
        item.addEventListener('click', () => {
            const reportName = item.querySelector('.report-name')?.innerText || 'Lab Report';
            const reportDate = item.querySelector('.report-date')?.innerText || '';
            openModal(`Report Details: ${escapeHtml(reportName)}`, `
                <div style="padding:10px 0; display:flex; flex-direction:column; gap:12px;">
                    <p style="font-size:0.85rem; color:#64748b;">Date Issued: ${escapeHtml(reportDate)}</p>
                    <div style="background:#f8fafc; padding:14px; border-radius:12px; font-size:0.85rem; border:1px solid #e2e8f0; display:flex; flex-direction:column; gap:6px;">
                        <div style="display:flex; justify-content:space-between;"><span>Hemoglobin:</span> <strong>14.2 g/dL (Normal)</strong></div>
                        <div style="display:flex; justify-content:space-between;"><span>WBC Count:</span> <strong>6,500 /mcL (Normal)</strong></div>
                        <div style="display:flex; justify-content:space-between;"><span>Platelets:</span> <strong>250,000 /mcL (Normal)</strong></div>
                        <div style="display:flex; justify-content:space-between;"><span>Fasting Glucose:</span> <strong>95 mg/dL (Normal)</strong></div>
                    </div>
                    <button id="btn-download-pdf" class="btn-primary" style="width:100%; justify-content:center;">Download Report PDF</button>
                </div>
            `);

            document.getElementById('btn-download-pdf')?.addEventListener('click', () => {
                const content = `MEDICAL LAB REPORT\nPatient: ${userState.name}\nTest: ${reportName}\nDate: ${reportDate}\nStatus: Certified Normal\n`;
                const blob = new Blob([content], { type: 'text/plain' });
                const link = document.createElement('a');
                link.href = URL.createObjectURL(blob);
                link.download = `${reportName.replace(/\s+/g, '_')}_Report.txt`;
                link.click();
                closeModal();
                showToast('Report PDF downloaded successfully!');
            });
        });
    });

    // Attach click listeners to Notification Bell button
    const notiBtn = document.querySelector('.icon-btn[aria-label="Notifications"]');
    if (notiBtn) {
        notiBtn.addEventListener('click', () => {
            openModal('Notifications Hub', `
                <div style="display:flex; flex-direction:column; gap:12px;">
                    <div style="padding:12px; background:#f0fdf4; border:1px solid #bbf7d0; border-radius:10px; font-size:0.85rem;">
                        <strong>Appointment Confirmed</strong><br>Dr. Rahul Sharma tomorrow at 10:30 AM.
                    </div>
                    <div style="padding:12px; background:#eff6ff; border:1px solid #bfdbfe; border-radius:10px; font-size:0.85rem;">
                        <strong>Lab Report Ready</strong><br>Complete Blood Count results ready for download.
                    </div>
                    <button id="btn-clear-notifications" class="btn-primary" style="width:100%; justify-content:center; margin-top:4px;">Mark All as Read</button>
                </div>
            `);

            document.getElementById('btn-clear-notifications')?.addEventListener('click', () => {
                const badge = document.querySelector('.notification-badge');
                if (badge) badge.style.display = 'none';
                closeModal();
                showToast('All notifications marked as read.');
            });
        });
    }

    // Attach click listener to User Profile Button
    const userProfileBtn = document.querySelector('.user-profile-btn');
    if (userProfileBtn) {
        userProfileBtn.addEventListener('click', () => {
            renderProfileView();
        });
    }

    // Attach click listeners to link-action (View All / Start new chat)
    document.querySelectorAll('.link-action').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const cardTitle = link.closest('.card-box')?.querySelector('.card-title')?.innerText || 'Details';
            const actionText = link.innerText.trim();
            if (actionText.includes('Start new chat')) {
                const chatContainer = document.getElementById('chat-messages');
                if (chatContainer) {
                    chatContainer.innerHTML = `
                        <div class="chat-message bot">
                            <div class="ai-avatar-icon" style="width:28px; height:28px; font-size:12px; flex-shrink:0;">🤖</div>
                            <div class="bubble">New chat session started! How can I assist you today?</div>
                        </div>
                    `;
                }
                showToast('New AI Chat session started!');
            } else if (cardTitle.includes('Appointments')) {
                openModal('All Upcoming Appointments', `
                    <div style="display:flex; flex-direction:column; gap:10px;">
                        <div style="padding:10px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; font-size:0.85rem;">
                            <strong>Dr. Rahul Sharma</strong> (General Physician) • 03 Aug, 10:30 AM
                        </div>
                        <div style="padding:10px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; font-size:0.85rem;">
                            <strong>Dr. Anjali Verma</strong> (Cardiologist) • 15 Aug, 04:00 PM
                        </div>
                        <div style="padding:10px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; font-size:0.85rem;">
                            <strong>Dr. Meena Iyer</strong> (Dentist) • 28 Aug, 11:00 AM
                        </div>
                    </div>
                `);
            } else if (cardTitle.includes('Lab Reports')) {
                openModal('All Recent Lab Reports', `
                    <div style="display:flex; flex-direction:column; gap:10px;">
                        <div style="padding:10px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; font-size:0.85rem;">
                            <strong>Complete Blood Count</strong> • 31 Jul 2025 (Normal)
                        </div>
                        <div style="padding:10px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; font-size:0.85rem;">
                            <strong>Liver Function Test</strong> • 28 Jul 2025 (Normal)
                        </div>
                        <div style="padding:10px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; font-size:0.85rem;">
                            <strong>Thyroid Profile</strong> • 25 Jul 2025 (High TSH)
                        </div>
                    </div>
                `);
            }
        });
    });
}



