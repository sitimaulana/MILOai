// MILO AI English Tutor: Common Utilities

// Escape HTML for safe rendering
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Format human-friendly topic labels (e.g. "Academic #1", "Interview #2", "Daily #3")
// Avoids confusion between technical module codes and CEFR proficiency levels.
function formatTopicDisplay(topic) {
    if (!topic) return { label: 'Topik', icon: 'fa-book-open', shortTrack: 'Topik', number: 1 };

    const code = (topic.track_code || '').toUpperCase();
    const key = (topic.track_key || '').toLowerCase();
    const id = (topic.topic_id || '').toUpperCase();

    let shortTrack = 'Topik';
    let icon = 'fa-book-open';

    if (code === 'TRACK_A' || key.includes('interview') || id.startsWith('A')) {
        shortTrack = 'Interview';
        icon = 'fa-briefcase';
    } else if (code === 'TRACK_B' || key.includes('academic') || id.startsWith('B')) {
        shortTrack = 'Academic';
        icon = 'fa-graduation-cap';
    } else if (code === 'TRACK_C' || key.includes('daily') || id.startsWith('C')) {
        shortTrack = 'Daily';
        icon = 'fa-comments';
    }

    let num = topic.topic_number;
    if (!num && id) {
        const match = id.match(/\d+$/);
        if (match) num = parseInt(match[0], 10);
    }
    num = num || 1;

    return {
        label: `${shortTrack} #${num}`,
        icon: icon,
        shortTrack: shortTrack,
        number: num,
    };
}

// Audio Player Map
const audioStore = new Map();
let audioIdCounter = 0;

function getStatusTextForEmotion(emotion) {
    switch (emotion) {
        case 'happy':
            return 'Milo senang & bangga dengan kemajuanmu! ✨';
        case 'supportive':
            return 'Milo memberikan tips & masukan evaluasi 💡';
        case 'curious':
            return 'Milo mendengarkan dengan antusias 🤔';
        case 'speaking':
        default:
            return 'Milo menjawab...';
    }
}

function playAudio(btnElement, audioId, emotion = 'friendly', feedback = null) {
    const base64Audio = audioStore.get(audioId);
    if (!base64Audio) return;

    const audio = new Audio("data:audio/mp3;base64," + base64Audio);
    const statusText = getStatusTextForEmotion(emotion);
    if (typeof window.setCompanionState === 'function') {
        window.setCompanionState('speaking', statusText, emotion, feedback);
    }
    if (window.miloLive2D && typeof window.miloLive2D.bindAudio === 'function') {
        window.miloLive2D.bindAudio(audio, emotion, feedback);
    }

    if (btnElement) {
        const icon = btnElement.querySelector('i');
        const origClass = icon ? icon.className : '';
        if (icon) {
            icon.className = 'fa-solid fa-spinner fa-spin';
        }
        audio.onended = () => {
            if (icon) icon.className = origClass;
            if (typeof window.setCompanionState === 'function') {
                window.setCompanionState('idle', 'Milo siap berlatih');
            }
        };
        audio.onerror = () => {
            if (icon) icon.className = origClass;
            if (typeof window.setCompanionState === 'function') {
                window.setCompanionState('idle', 'Milo siap berlatih');
            }
        };
    } else {
        audio.onended = () => {
            if (typeof window.setCompanionState === 'function') {
                window.setCompanionState('idle', 'Milo siap berlatih');
            }
        };
    }
    audio.play().catch(err => {
        console.error("Audio playback error:", err);
        if (typeof window.setCompanionState === 'function') {
            window.setCompanionState('idle', 'Milo siap berlatih');
        }
    });
    return audio;
}

function autoPlayAudio(base64Audio, emotion = 'friendly', feedback = null) {
    if (!base64Audio) return;
    try {
        const audio = new Audio("data:audio/mp3;base64," + base64Audio);
        const statusText = getStatusTextForEmotion(emotion);
        if (typeof window.setCompanionState === 'function') {
            window.setCompanionState('speaking', statusText, emotion, feedback);
        }
        if (window.miloLive2D && typeof window.miloLive2D.bindAudio === 'function') {
            window.miloLive2D.bindAudio(audio, emotion, feedback);
        }
        audio.onended = () => {
            if (typeof window.setCompanionState === 'function') {
                window.setCompanionState('idle', 'Milo siap berlatih');
            }
        };
        audio.onerror = () => {
            if (typeof window.setCompanionState === 'function') {
                window.setCompanionState('idle', 'Milo siap berlatih');
            }
        };
        audio.play().catch(err => {
            console.log("Auto-play prevented by browser policy:", err);
            if (typeof window.setCompanionState === 'function') {
                window.setCompanionState('idle', 'Milo siap berlatih');
            }
        });
        return audio;
    } catch (e) {
        console.error("Audio autoplay failed:", e);
    }
}

// Show/Hide Global Loading Modal
function showGlobalLoading(text) {
    let overlay = document.getElementById('globalLoadingModal');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'globalLoadingModal';
        overlay.className = 'loading-modal-backdrop';
        overlay.innerHTML = `
            <div class="loading-box">
                <div class="spinner-glow"></div>
                <p id="globalLoadingText" style="font-weight: 600; color: var(--text-main);">Loading...</p>
            </div>
        `;
        document.body.appendChild(overlay);
    }
    const label = document.getElementById('globalLoadingText');
    if (label) label.textContent = text || 'Loading...';
    overlay.style.display = 'flex';
}

function hideGlobalLoading() {
    const overlay = document.getElementById('globalLoadingModal');
    if (overlay) overlay.style.display = 'none';
}

function getAuthToken() {
    return localStorage.getItem('milo_token');
}

function getAuthUser() {
    const raw = localStorage.getItem('milo_user');
    if (!raw) return null;
    try {
        return JSON.parse(raw);
    } catch {
        return null;
    }
}

function logoutUser() {
    localStorage.removeItem('milo_token');
    localStorage.removeItem('milo_user');
    sessionStorage.clear();
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    const isLoginPage = currentPage === 'login.html' || currentPage === 'register.html';
    const redirectTarget = resolvePageUrl('login.html');
    if (!isLoginPage && currentPage !== 'index.html') {
        window.location.href = `${redirectTarget}?redirect=${encodeURIComponent(currentPage)}`;
    } else {
        window.location.href = redirectTarget;
    }
}

function requireAuth() {
    const token = getAuthToken();
    const user = getAuthUser();
    if (!token || !user) {
        logoutUser();
        return false;
    }
    return true;
}

function getAuthHeaders(extraHeaders = {}) {
    const token = getAuthToken();
    const headers = { ...extraHeaders };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
}

async function miloFetch(url, options = {}) {
    options.headers = options.headers || {};
    const token = getAuthToken();
    if (token && !options.headers['Authorization'] && !options.headers['authorization']) {
        options.headers['Authorization'] = `Bearer ${token}`;
    }
    const response = await fetch(url, options);
    if (response.status === 401) {
        logoutUser();
        throw new Error('Sesi autentikasi telah berakhir. Silakan login kembali.');
    }
    return response;
}

function resolvePageUrl(filename) {
    const isUiMounted = window.location.pathname.includes('/ui/');
    return isUiMounted ? `/ui/${filename}` : filename;
}

function initAuthNav() {
    const user = getAuthUser();
    const token = getAuthToken();
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    const redirectParam = encodeURIComponent(currentPage);

    const loginUrl = `${resolvePageUrl('login.html')}?redirect=${redirectParam}`;
    const registerUrl = `${resolvePageUrl('register.html')}?redirect=${redirectParam}`;
    const setupUrl = resolvePageUrl('setup.html');

    // 1. Navbar Action Wrapper (index, dashboard, summary)
    const containers = document.querySelectorAll('.nav-action-wrapper');
    containers.forEach(container => {
        if (token && user) {
            const initial = (user.full_name || user.username || 'M').charAt(0).toUpperCase();
            const displayName = user.full_name || user.username;
            const cefr = user.cefr_level || 'B1';

            container.innerHTML = `
                <div class="user-profile-nav-pill" title="Masuk sebagai ${escapeHtml(displayName)}">
                    <span class="user-nav-avatar">${escapeHtml(initial)}</span>
                    <span class="user-nav-username">${escapeHtml(displayName)}</span>
                    <span class="user-nav-cefr">${escapeHtml(cefr)}</span>
                    <button type="button" class="btn-nav-logout" title="Keluar dari akun" aria-label="Keluar dari akun" onclick="logoutUser()">
                        <i class="fa-solid fa-arrow-right-from-bracket"></i>
                    </button>
                </div>
                <a href="${setupUrl}" class="nav-cta-btn">Mulai Latihan</a>
            `;
        } else {
            container.innerHTML = `
                <a href="${loginUrl}" class="nav-secondary-btn">Masuk</a>
                <a href="${registerUrl}" class="nav-cta-btn">Daftar</a>
            `;
        }
    });

    // 2. Setup Top Header User Status
    const setupStatus = document.getElementById('setupUserStatus');
    if (setupStatus) {
        if (token && user) {
            const initial = (user.full_name || user.username || 'M').charAt(0).toUpperCase();
            const displayName = user.full_name || user.username;
            setupStatus.innerHTML = `
                <div class="setup-user-badge" title="Tersambung ke akun ${escapeHtml(displayName)}">
                    <span class="avatar-mini">${escapeHtml(initial)}</span>
                    <span class="user-name-mini">${escapeHtml(displayName)}</span>
                </div>
            `;
        } else {
            setupStatus.innerHTML = `
                <a href="${loginUrl}" class="setup-login-link" title="Masuk untuk menyimpan riwayat sesi">
                    <i class="fa-solid fa-arrow-right-to-bracket"></i>
                    <span>Masuk</span>
                </a>
            `;
        }
    }
}

function initMobileNav() {
    const navToggle = document.getElementById('nav-toggle');
    const navDrawer = document.getElementById('mobile-nav-drawer');
    if (navToggle && navDrawer) {
        navToggle.addEventListener('click', () => {
            const isHidden = navDrawer.hasAttribute('hidden');
            if (isHidden) {
                navDrawer.removeAttribute('hidden');
                navToggle.setAttribute('aria-expanded', 'true');
            } else {
                navDrawer.setAttribute('hidden', '');
                navToggle.setAttribute('aria-expanded', 'false');
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    initAuthNav();
    initMobileNav();
});

