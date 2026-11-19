// MILO AI English Tutor: Common Utilities

// Escape HTML for safe rendering
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Audio Player Map
const audioStore = new Map();
let audioIdCounter = 0;

function playAudio(btnElement, audioId) {
    const base64Audio = audioStore.get(audioId);
    if (!base64Audio) return;

    const audio = new Audio("data:audio/mp3;base64," + base64Audio);
    if (typeof window.setCompanionState === 'function') {
        window.setCompanionState('speaking', 'Milo menjawab...');
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

function autoPlayAudio(base64Audio) {
    if (!base64Audio) return;
    try {
        const audio = new Audio("data:audio/mp3;base64," + base64Audio);
        if (typeof window.setCompanionState === 'function') {
            window.setCompanionState('speaking', 'Milo menjawab...');
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
    const redirectTarget = window.location.pathname.includes('/ui/') ? '/ui/login.html' : 'login.html';
    window.location.href = redirectTarget;
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

