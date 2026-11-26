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

function getStatusTextForEmotion(emotion, feedback = null) {
    if (feedback && feedback.corrections && feedback.corrections.length > 0) {
        return 'Milo memberikan tips evaluasi 💡';
    }
    if (feedback && typeof feedback.overall_score === 'number' && feedback.overall_score >= 85) {
        return 'Milo senang & bangga dengan kemajuanmu! ✨';
    }
    switch (emotion) {
        case 'happy':
            return 'Milo senang & bangga dengan kemajuanmu! ✨';
        case 'supportive':
            return 'Milo memberikan tips evaluasi 💡';
        case 'curious':
            return 'Milo mendengarkan dengan antusias 🤔';
        case 'speaking':
        default:
            return 'Milo menjawab...';
    }
}

function getIdleStatusTextForEmotion(emotion, feedback = null) {
    if (feedback && feedback.corrections && feedback.corrections.length > 0) {
        return 'Milo menyemangatimu: simak tips evaluasi 💡';
    }
    if (feedback && typeof feedback.overall_score === 'number' && feedback.overall_score >= 85) {
        return 'Bagus sekali! Milo bangga dengan kemajuanmu ✨';
    }
    switch (emotion) {
        case 'happy':
            return 'Bagus sekali! Milo siap untuk latihan berikutnya ✨';
        case 'supportive':
            return 'Semangat! Coba terapkan tips di samping 💡';
        case 'curious':
            return 'Milo menunggu ceritamu... 🎤';
        default:
            return 'Milo siap berlatih';
    }
}

function playAudio(btnElement, audioId, emotion = 'friendly', feedback = null, text = '') {
    const base64Audio = audioStore.get(audioId);
    if (!base64Audio) return;

    const audio = new Audio("data:audio/mp3;base64," + base64Audio);
    const statusText = getStatusTextForEmotion(emotion, feedback);
    if (typeof window.setCompanionState === 'function') {
        window.setCompanionState('speaking', statusText, emotion, feedback);
    }
    if (window.miloLive2D && typeof window.miloLive2D.bindAudio === 'function') {
        window.miloLive2D.bindAudio(audio, emotion, feedback, text);
    }

    if (btnElement) {
        const icon = btnElement.querySelector('i');
        const origClass = icon ? icon.className : '';
        if (icon) {
            icon.className = 'fa-solid fa-spinner fa-spin';
        }
        audio.onended = () => {
            if (icon) icon.className = origClass;
            const idleText = getIdleStatusTextForEmotion(emotion, feedback);
            if (typeof window.setCompanionState === 'function') {
                window.setCompanionState('idle', idleText, emotion, feedback);
            }
        };
        audio.onerror = () => {
            if (icon) icon.className = origClass;
            const idleText = getIdleStatusTextForEmotion(emotion, feedback);
            if (typeof window.setCompanionState === 'function') {
                window.setCompanionState('idle', idleText, emotion, feedback);
            }
        };
    } else {
        audio.onended = () => {
            const idleText = getIdleStatusTextForEmotion(emotion, feedback);
            if (typeof window.setCompanionState === 'function') {
                window.setCompanionState('idle', idleText, emotion, feedback);
            }
        };
    }
    audio.play().catch(err => {
        console.error("Audio playback error:", err);
        const idleText = getIdleStatusTextForEmotion(emotion, feedback);
        if (typeof window.setCompanionState === 'function') {
            window.setCompanionState('idle', idleText, emotion, feedback);
        }
    });
    return audio;
}

function autoPlayAudio(base64Audio, emotion = 'friendly', feedback = null, text = '') {
    if (!base64Audio) return;
    try {
        const audio = new Audio("data:audio/mp3;base64," + base64Audio);
        const statusText = getStatusTextForEmotion(emotion, feedback);
        if (typeof window.setCompanionState === 'function') {
            window.setCompanionState('speaking', statusText, emotion, feedback);
        }
        if (window.miloLive2D && typeof window.miloLive2D.bindAudio === 'function') {
            window.miloLive2D.bindAudio(audio, emotion, feedback, text);
        }
        audio.onended = () => {
            const idleText = getIdleStatusTextForEmotion(emotion, feedback);
            if (typeof window.setCompanionState === 'function') {
                window.setCompanionState('idle', idleText, emotion, feedback);
            }
        };
        audio.onerror = () => {
            const idleText = getIdleStatusTextForEmotion(emotion, feedback);
            if (typeof window.setCompanionState === 'function') {
                window.setCompanionState('idle', idleText, emotion, feedback);
            }
        };
        audio.play().catch(err => {
            console.log("Auto-play prevented by browser policy:", err);
            const idleText = getIdleStatusTextForEmotion(emotion, feedback);
            if (typeof window.setCompanionState === 'function') {
                window.setCompanionState('idle', idleText, emotion, feedback);
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

    // Toggle links that require login (e.g. Ruang Latihan & Dashboard)
    const isLoggedIn = Boolean(token && user);
    if (document.body) {
        document.body.classList.toggle('logged-in', isLoggedIn);
    }
    const authRequiredLinks = document.querySelectorAll('.auth-required-nav');
    authRequiredLinks.forEach(link => {
        if (isLoggedIn) {
            link.style.setProperty('display', link.classList.contains('mobile-nav-link') ? 'flex' : 'inline-block', 'important');
        } else {
            link.style.setProperty('display', 'none', 'important');
        }
    });

    const authGuestLinks = document.querySelectorAll('.auth-guest-nav');
    authGuestLinks.forEach(link => {
        if (isLoggedIn) {
            link.style.setProperty('display', 'none', 'important');
        } else {
            link.style.setProperty('display', link.classList.contains('mobile-nav-link') ? 'flex' : 'inline-block', 'important');
        }
    });

    // 1. Navbar Action Wrapper (index, dashboard, summary)
    const isIndexOrSetup = currentPage === '' || currentPage === 'index.html' || currentPage === 'setup.html' || currentPage === 'briefing.html';
    const containers = document.querySelectorAll('.nav-action-wrapper');
    containers.forEach(container => {
        if (isLoggedIn) {
            const initial = (user.full_name || user.username || 'M').charAt(0).toUpperCase();
            const displayName = user.full_name || user.username;
            const cefr = user.cefr_level || 'B1';
            const ctaBtn = isIndexOrSetup ? '' : `<a href="${setupUrl}" class="nav-cta-btn">Mulai Latihan</a>`;

            container.innerHTML = `
                <div class="user-profile-nav-pill" title="Masuk sebagai ${escapeHtml(displayName)}">
                    <span class="user-nav-avatar">${escapeHtml(initial)}</span>
                    <span class="user-nav-username">${escapeHtml(displayName)}</span>
                    <span class="user-nav-cefr">${escapeHtml(cefr)}</span>
                    <button type="button" class="btn-nav-logout" title="Keluar dari akun" aria-label="Keluar dari akun" onclick="logoutUser()">
                        <i class="fa-solid fa-arrow-right-from-bracket"></i>
                    </button>
                </div>
                ${ctaBtn}
            `;

            // Hide the 'Masuk' menu link in nav-menu when user is logged in
            const masukLink = document.getElementById('nav-link-masuk');
            if (masukLink) masukLink.style.display = 'none';
            const mobileMasuk = document.getElementById('mobile-nav-link-masuk');
            if (mobileMasuk) mobileMasuk.style.display = 'none';
        } else {
            if (isIndexOrSetup) {
                container.innerHTML = '';
            } else {
                container.innerHTML = `
                    <a href="${loginUrl}" class="nav-secondary-btn">Masuk</a>
                    <a href="${registerUrl}" class="nav-cta-btn">Daftar</a>
                `;
            }
            const masukLink = document.getElementById('nav-link-masuk');
            if (masukLink) masukLink.style.display = '';
            const mobileMasuk = document.getElementById('mobile-nav-link-masuk');
            if (mobileMasuk) mobileMasuk.style.display = '';
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

