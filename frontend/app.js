// ═══════════════════════════════════════════════════════════════════════════════
// MILO AI English Tutor — Frontend Application
// ═══════════════════════════════════════════════════════════════════════════════

// ─── State ───────────────────────────────────────────────────────────────────
let sessionId = null;
let selectedLevel = 'B1';
let selectedTopic = null;
let sessionStartTime = null;
let timerInterval = null;

// Audio playback store
const audioStore = new Map();
let audioIdCounter = 0;

// Recording state
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;

// Running feedback scores (for averaging in the panel)
let feedbackHistory = [];

// ─── Screen Navigation ──────────────────────────────────────────────────────
function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    const target = document.getElementById(screenId);
    if (target) target.classList.add('active');
}

// ─── DOM References ──────────────────────────────────────────────────────────
const chatBox = document.getElementById('chatBox');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const toggleKeyboardBtn = document.getElementById('toggleKeyboardBtn');
const textInputArea = document.getElementById('textInputArea');
const typingIndicator = document.getElementById('typingIndicator');
const micBtn = document.getElementById('micBtn');
const endBtn = document.getElementById('endBtn');

// ═══════════════════════════════════════════════════════════════════════════════
// SCREEN 1: MAIN PAGE
// ═══════════════════════════════════════════════════════════════════════════════

document.getElementById('btn-start-practice').addEventListener('click', () => {
    showScreen('screen-setup');
});

document.getElementById('btn-go-dashboard').addEventListener('click', () => {
    loadDashboard();
    showScreen('screen-dashboard');
});

// ═══════════════════════════════════════════════════════════════════════════════
// SCREEN 2: SETUP FLOW
// ═══════════════════════════════════════════════════════════════════════════════

// Back button
document.getElementById('btn-setup-back').addEventListener('click', () => {
    const step2 = document.getElementById('setup-step-2');
    if (step2.classList.contains('active')) {
        step2.classList.remove('active');
        document.getElementById('setup-step-1').classList.add('active');
    } else {
        showScreen('screen-main');
    }
});

// Level selection
document.querySelectorAll('.level-card').forEach(card => {
    card.addEventListener('click', () => {
        document.querySelectorAll('.level-card').forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        selectedLevel = card.dataset.level;
    });
});

// Next: Choose Topic
document.getElementById('btn-next-topic').addEventListener('click', () => {
    document.getElementById('setup-step-1').classList.remove('active');
    document.getElementById('setup-step-2').classList.add('active');
});

// Topic selection
document.querySelectorAll('.topic-card').forEach(card => {
    card.addEventListener('click', () => {
        document.querySelectorAll('.topic-card').forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        selectedTopic = card.dataset.topic;
        document.getElementById('btn-start-session').disabled = false;
    });
});

// Start Session
document.getElementById('btn-start-session').addEventListener('click', async () => {
    if (!selectedTopic) return;
    await startSession();
});

// ═══════════════════════════════════════════════════════════════════════════════
// SESSION START
// ═══════════════════════════════════════════════════════════════════════════════

async function startSession() {
    showLoading('Preparing your session...');

    try {
        const res = await fetch('/api/v1/session/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                cefr_level: selectedLevel,
                topic: selectedTopic,
            }),
        });

        if (!res.ok) {
            const err = await res.text();
            throw new Error(`API ${res.status}: ${err}`);
        }

        const data = await res.json();
        sessionId = data.session_id;

        // Reset practice state
        chatBox.innerHTML = '';
        feedbackHistory = [];
        resetFeedbackPanel();

        // Set header info
        document.getElementById('sessionTopicBadge').textContent = data.topic_label;
        document.getElementById('sessionLevelBadge').textContent = `Level ${data.cefr_level}`;

        // Show greeting
        appendMessage(data.greeting, false, data.audio_base64);

        // Start timer
        startTimer();

        hideLoading();
        showScreen('screen-practice');
    } catch (err) {
        hideLoading();
        alert('Error starting session: ' + err.message);
        console.error(err);
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SCREEN 3: PRACTICE (Chat + Voice + Feedback)
// ═══════════════════════════════════════════════════════════════════════════════

// Back button (goes to main with confirmation)
document.getElementById('btn-practice-back').addEventListener('click', () => {
    if (confirm('Leave session? Your progress will be saved.')) {
        endCurrentSession();
    }
});

// Toggle keyboard
toggleKeyboardBtn.addEventListener('click', () => {
    if (textInputArea.style.display === 'none') {
        textInputArea.style.display = 'flex';
        messageInput.focus();
    } else {
        textInputArea.style.display = 'none';
    }
});

// ─── Helpers ─────────────────────────────────────────────────────────────────

function scrollToBottom() {
    chatBox.scrollTop = chatBox.scrollHeight;
}

function startTimer() {
    sessionStartTime = Date.now();
    const timerEl = document.getElementById('sessionTimer');
    timerInterval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - sessionStartTime) / 1000);
        const mins = String(Math.floor(elapsed / 60)).padStart(2, '0');
        const secs = String(elapsed % 60).padStart(2, '0');
        timerEl.textContent = `${mins}:${secs}`;
    }, 1000);
}

function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}

function showLoading(text) {
    document.getElementById('loadingText').textContent = text || 'Loading...';
    document.getElementById('loadingOverlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

// ─── Audio Playback ──────────────────────────────────────────────────────────

function playAudio(btnElement, audioId) {
    const base64Audio = audioStore.get(audioId);
    if (!base64Audio) return;

    const audio = new Audio("data:audio/mp3;base64," + base64Audio);
    if (btnElement) {
        const icon = btnElement.querySelector('i');
        icon.classList.remove('fa-volume-high');
        icon.classList.add('fa-spinner', 'fa-spin');
        audio.onended = () => {
            icon.classList.remove('fa-spinner', 'fa-spin');
            icon.classList.add('fa-volume-high');
        };
        audio.onerror = () => {
            icon.classList.remove('fa-spinner', 'fa-spin');
            icon.classList.add('fa-volume-high');
        };
    }
    audio.play().catch(err => console.error("Audio play failed:", err));
    return audio;
}

function autoPlayAudio(base64Audio) {
    if (!base64Audio) return;
    const audio = new Audio("data:audio/mp3;base64," + base64Audio);
    audio.play().catch(err => console.error("Auto-play failed:", err));
}

// ─── Chat UI ─────────────────────────────────────────────────────────────────

function appendMessage(text, isUser, audioBase64 = null) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${isUser ? 'user-message' : 'ai-message'}`;

    let innerHTML = `<div class="bubble">`;
    if (isUser) {
        innerHTML += `<p>${escapeHtml(text)}</p>`;
    } else {
        innerHTML += `<p>${escapeHtml(text)}</p>`;
        if (audioBase64) {
            const audioId = audioIdCounter++;
            audioStore.set(audioId, audioBase64);
            innerHTML += `<button class="play-btn" data-audio-id="${audioId}"><i class="fa-solid fa-volume-high"></i></button>`;
        }
    }
    innerHTML += `</div>`;
    msgDiv.innerHTML = innerHTML;
    chatBox.appendChild(msgDiv);

    // Attach play button listener
    if (!isUser && audioBase64) {
        const playBtn = msgDiv.querySelector('.play-btn');
        playBtn.addEventListener('click', function () {
            playAudio(this, parseInt(this.getAttribute('data-audio-id')));
        });
    }

    scrollToBottom();

    // Auto-play AI audio
    if (!isUser && audioBase64) {
        autoPlayAudio(audioBase64);
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ─── Text Chat API ───────────────────────────────────────────────────────────

async function sendMessage() {
    const text = messageInput.value.trim();
    if (!text) return;

    sendBtn.disabled = true;
    appendMessage(text, true);
    messageInput.value = '';

    typingIndicator.style.display = 'flex';
    scrollToBottom();

    try {
        const body = {
            message: text,
            return_audio: true,
            cefr_level: selectedLevel,
        };
        if (sessionId) body.session_id = sessionId;

        const response = await fetch('/api/v1/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`API ${response.status}: ${errorText}`);
        }

        const data = await response.json();
        sessionId = data.session_id;

        typingIndicator.style.display = 'none';
        appendMessage(data.response_text, false, data.audio_base64);

        // Update feedback panel with per-turn feedback
        if (data.feedback) {
            updateFeedbackPanel(data.feedback);
        }
    } catch (error) {
        console.error("Chat error:", error);
        typingIndicator.style.display = 'none';
        appendMessage("Sorry, an error occurred: " + error.message, false);
    } finally {
        sendBtn.disabled = false;
    }
}

// ─── Voice Recording & API ───────────────────────────────────────────────────

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        audioChunks = [];
        mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
            stream.getTracks().forEach(track => track.stop());
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            if (audioBlob.size > 0) await sendVoice(audioBlob);
        };

        mediaRecorder.start();
        isRecording = true;
        micBtn.classList.add('recording');
    } catch (err) {
        console.error("Microphone access denied:", err);
        alert("Please allow microphone access for speaking practice!");
    }
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
        isRecording = false;
        micBtn.classList.remove('recording');
    }
}

async function sendVoice(audioBlob) {
    appendMessage("(Sending voice...)", true);
    typingIndicator.style.display = 'flex';
    typingIndicator.querySelector('.typing-dots + *') || null;
    scrollToBottom();

    try {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');
        formData.append('return_audio', 'true');
        formData.append('cefr_level', selectedLevel);
        if (sessionId) formData.append('session_id', sessionId);

        const response = await fetch('/api/v1/voice', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Voice API ${response.status}: ${errorText}`);
        }

        const data = await response.json();
        sessionId = data.session_id;

        typingIndicator.style.display = 'none';

        // Replace placeholder with transcript
        const lastUserMsg = chatBox.querySelector('.message.user-message:last-of-type');
        if (lastUserMsg) {
            const bubble = lastUserMsg.querySelector('.bubble p');
            if (bubble && bubble.textContent.includes('Sending voice')) {
                bubble.textContent = data.transcript || "(inaudible)";
            }
        }

        appendMessage(data.response_text, false, data.audio_base64);

        // Update feedback panel
        if (data.feedback) {
            updateFeedbackPanel(data.feedback);
        }
    } catch (error) {
        console.error("Voice error:", error);
        typingIndicator.style.display = 'none';
        appendMessage("Sorry, error processing voice: " + error.message, false);
    }
}

// Mic button toggle
micBtn.addEventListener('click', () => {
    if (!isRecording) startRecording();
    else stopRecording();
});

// Text input
sendBtn.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

// ─── Feedback Panel ──────────────────────────────────────────────────────────

function updateFeedbackPanel(feedback) {
    feedbackHistory.push(feedback);

    // Calculate running averages
    const avgGrammar = avg(feedbackHistory.map(f => f.grammar_score));
    const avgVocab = avg(feedbackHistory.map(f => f.vocabulary_score));
    const avgFluency = avg(feedbackHistory.map(f => f.fluency_score));

    // Update score rings
    updateScoreRing('scoreGrammar', avgGrammar, 'grammar-ring');
    updateScoreRing('scoreVocabulary', avgVocab, 'vocab-ring');
    updateScoreRing('scoreFluency', avgFluency, 'fluency-ring');

    // Update corrections list
    if (feedback.corrections && feedback.corrections.length > 0) {
        const list = document.getElementById('correctionsList');
        // Remove "no corrections" placeholder
        const noCorr = list.querySelector('.no-corrections');
        if (noCorr) noCorr.remove();

        feedback.corrections.forEach(c => {
            const item = document.createElement('div');
            item.className = 'correction-item';
            item.innerHTML = `
                <div class="correction-original">✗ ${escapeHtml(c.original)}</div>
                <div class="correction-fixed">✓ ${escapeHtml(c.corrected)}</div>
                <div class="correction-explanation">${escapeHtml(c.explanation)}</div>
            `;
            list.prepend(item);
        });
    }

    // Update tip
    if (feedback.tip) {
        const tipSection = document.getElementById('tipSection');
        tipSection.style.display = 'block';
        document.getElementById('tipText').textContent = feedback.tip;
    }
}

function updateScoreRing(cardId, score, ringClass) {
    const card = document.getElementById(cardId);
    const valueEl = card.querySelector('.score-value');
    const ring = card.querySelector(`.${ringClass}`);

    valueEl.textContent = Math.round(score);
    ring.setAttribute('stroke-dasharray', `${score}, 100`);
}

function resetFeedbackPanel() {
    feedbackHistory = [];
    ['scoreGrammar', 'scoreVocabulary', 'scoreFluency'].forEach(id => {
        const card = document.getElementById(id);
        card.querySelector('.score-value').textContent = '--';
        card.querySelector('.ring-fill').setAttribute('stroke-dasharray', '0, 100');
    });

    document.getElementById('correctionsList').innerHTML = `
        <div class="no-corrections">
            <i class="fa-solid fa-circle-check"></i>
            <p>Start speaking to get feedback!</p>
        </div>
    `;

    document.getElementById('tipSection').style.display = 'none';
}

function avg(arr) {
    return arr.length ? arr.reduce((a, b) => a + b, 0) / arr.length : 0;
}

// ═══════════════════════════════════════════════════════════════════════════════
// END SESSION
// ═══════════════════════════════════════════════════════════════════════════════

endBtn.addEventListener('click', () => {
    if (confirm('End this practice session?')) {
        endCurrentSession();
    }
});

async function endCurrentSession() {
    if (!sessionId) {
        showScreen('screen-main');
        return;
    }

    stopTimer();
    showLoading('Calculating your scores...');

    try {
        const res = await fetch('/api/v1/session/end', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId }),
        });

        if (!res.ok) {
            const err = await res.text();
            throw new Error(`API ${res.status}: ${err}`);
        }

        const data = await res.json();
        hideLoading();
        showSessionSummary(data);
    } catch (err) {
        hideLoading();
        console.error("End session error:", err);
        showScreen('screen-main');
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// SCREEN 4: SESSION SUMMARY
// ═══════════════════════════════════════════════════════════════════════════════

function showSessionSummary(data) {
    // Header
    document.getElementById('summaryTopic').textContent = data.topic_label;
    document.getElementById('summaryDuration').textContent = `Duration: ${data.duration_minutes} mins`;

    // Overall score ring
    const overall = Math.round(data.overall_score);
    document.getElementById('overallScoreValue').textContent = overall;
    const circumference = 2 * Math.PI * 52; // r=52
    const ring = document.querySelector('.ring-fill-lg');
    setTimeout(() => {
        ring.setAttribute('stroke-dasharray', `${(overall / 100) * circumference} ${circumference}`);
    }, 100);

    // CEFR
    document.getElementById('cefrTarget').textContent = data.cefr_target;
    document.getElementById('cefrResultValue').textContent = data.cefr_result;
    const cefrEl = document.getElementById('cefrAchieved');
    if (data.cefr_achieved) {
        cefrEl.style.color = 'var(--grammar-color)';
    } else {
        cefrEl.style.color = 'var(--fluency-color)';
    }

    // Score breakdown
    const grammar = Math.round(data.avg_grammar_score);
    const vocab = Math.round(data.avg_vocabulary_score);
    const fluency = Math.round(data.avg_fluency_score);

    document.getElementById('summaryGrammarScore').textContent = grammar;
    document.getElementById('summaryVocabScore').textContent = vocab;
    document.getElementById('summaryFluencyScore').textContent = fluency;

    setTimeout(() => {
        document.getElementById('summaryGrammarBar').style.width = grammar + '%';
        document.getElementById('summaryVocabBar').style.width = vocab + '%';
        document.getElementById('summaryFluencyBar').style.width = fluency + '%';
    }, 200);

    // AI Summary
    document.getElementById('aiSummaryText').textContent = data.session_summary || 'Great practice session!';

    // Improvement areas
    const improvSection = document.getElementById('improvementSection');
    if (data.improvement_areas && data.improvement_areas.length > 0) {
        improvSection.style.display = 'block';
        const list = document.getElementById('improvementList');
        list.innerHTML = data.improvement_areas.map(a => `<li>${a}</li>`).join('');
    } else {
        improvSection.style.display = 'none';
    }

    showScreen('screen-summary');
    sessionId = null;
}

// Summary actions
document.getElementById('btn-new-session').addEventListener('click', () => {
    selectedTopic = null;
    document.querySelectorAll('.topic-card').forEach(c => c.classList.remove('selected'));
    document.getElementById('btn-start-session').disabled = true;

    // Reset setup to step 1
    document.getElementById('setup-step-2').classList.remove('active');
    document.getElementById('setup-step-1').classList.add('active');

    showScreen('screen-setup');
});

document.getElementById('btn-summary-dashboard').addEventListener('click', () => {
    loadDashboard();
    showScreen('screen-dashboard');
});

// ═══════════════════════════════════════════════════════════════════════════════
// SCREEN 5: DASHBOARD
// ═══════════════════════════════════════════════════════════════════════════════

document.getElementById('btn-dashboard-back').addEventListener('click', () => {
    showScreen('screen-main');
});

document.getElementById('btn-dashboard-start')?.addEventListener('click', () => {
    showScreen('screen-setup');
});

async function loadDashboard() {
    try {
        const res = await fetch('/api/v1/dashboard');
        if (!res.ok) throw new Error('Dashboard API error');
        const data = await res.json();

        document.getElementById('statTotalSessions').textContent = data.total_sessions;
        document.getElementById('statAvgScore').textContent = Math.round(data.avg_overall_score);
        document.getElementById('statGrammar').textContent = Math.round(data.skill_averages.grammar || 0);
        document.getElementById('statVocab').textContent = Math.round(data.skill_averages.vocabulary || 0);

        const list = document.getElementById('sessionsList');
        if (data.recent_sessions.length === 0) {
            list.innerHTML = `
                <div class="empty-state">
                    <i class="fa-solid fa-inbox"></i>
                    <p>No sessions yet. Start practicing!</p>
                    <button class="btn-primary btn-sm" onclick="showScreen('screen-setup')">
                        <i class="fa-solid fa-play"></i> Start First Session
                    </button>
                </div>
            `;
            return;
        }

        const topicIcons = {
            job_interview: 'fa-briefcase',
            academic_discussion: 'fa-graduation-cap',
            daily_conversation: 'fa-comments',
        };

        list.innerHTML = data.recent_sessions.map(s => `
            <div class="session-row">
                <div class="session-row-icon">
                    <i class="fa-solid ${topicIcons[s.topic] || 'fa-comments'}"></i>
                </div>
                <div class="session-row-info">
                    <div class="session-row-topic">${escapeHtml(s.topic_label)}</div>
                    <div class="session-row-meta">${new Date(s.created_at).toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' })} · ${s.duration_minutes} mins</div>
                </div>
                <div class="session-row-score">${Math.round(s.overall_score || 0)}</div>
                ${s.cefr_result ? `<div class="session-row-cefr">${s.cefr_result}</div>` : ''}
            </div>
        `).join('');
    } catch (err) {
        console.error("Dashboard error:", err);
    }
}
