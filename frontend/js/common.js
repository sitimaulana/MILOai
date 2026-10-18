// ═══════════════════════════════════════════════════════════════════════════════
// MILO AI English Tutor — Common Utilities
// ═══════════════════════════════════════════════════════════════════════════════

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
    if (btnElement) {
        const icon = btnElement.querySelector('i');
        const origClass = icon ? icon.className : '';
        if (icon) {
            icon.className = 'fa-solid fa-spinner fa-spin';
        }
        audio.onended = () => {
            if (icon) icon.className = origClass;
        };
        audio.onerror = () => {
            if (icon) icon.className = origClass;
        };
    }
    audio.play().catch(err => console.error("Audio playback error:", err));
    return audio;
}

function autoPlayAudio(base64Audio) {
    if (!base64Audio) return;
    try {
        const audio = new Audio("data:audio/mp3;base64," + base64Audio);
        audio.play().catch(err => console.log("Auto-play prevented by browser policy:", err));
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
