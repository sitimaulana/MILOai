// ═══════════════════════════════════════════════════════════════════════════════
// MILO AI English Tutor: Practice Room Logic (Exact Mockup Theme)
// ═══════════════════════════════════════════════════════════════════════════════

// Session State
let sessionId = null;
let currentTopic = 'job_interview';
let currentLevel = 'B1';
let sessionStartTime = Date.now();
let feedbackHistory = [];
let turnCount = 0;

// Media Recording State
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;

// DOM Elements
const messagesContainer = document.getElementById('messagesContainer');
const userTextInput = document.getElementById('userTextInput');
const btnSendText = document.getElementById('btnSendText');
const btnToggleKeyboard = document.getElementById('btnToggleKeyboard');
const textInputSlide = document.getElementById('textInputSlide');
const btnMicAction = document.getElementById('btnMicAction');
const btnEndSession = document.getElementById('btnEndSession');
const waveformBox = document.getElementById('waveformBox');
const progressBarFill = document.getElementById('progressBarFill');

// 2D Companion Stage Elements
const miloCompanionStage = document.getElementById('miloCompanionStage');
const miloStatusText = document.getElementById('miloStatusText');

function setCompanionState(state, text) {
    if (miloCompanionStage) {
        miloCompanionStage.classList.remove('listening', 'thinking', 'speaking');
        if (state && state !== 'idle') {
            miloCompanionStage.classList.add(state);
        }
    }
    if (miloStatusText && text) {
        miloStatusText.textContent = text;
    }
}
window.setCompanionState = setCompanionState;

// HUD Elements & Pillars
const evalInitialPlaceholder = document.getElementById('evalInitialPlaceholder');

document.addEventListener('DOMContentLoaded', async () => {
    // 1. Resolve Session ID
    const urlParams = new URLSearchParams(window.location.search);
    sessionId = urlParams.get('session_id') || sessionStorage.getItem('milo_session_id');

    if (!sessionId) {
        alert('No active practice session found. Redirecting to setup...');
        window.location.href = '/ui/setup.html';
        return;
    }

    currentTopic = sessionStorage.getItem('milo_topic') || 'job_interview';
    currentLevel = sessionStorage.getItem('milo_cefr_level') || 'B1';
    const topicLabel = sessionStorage.getItem('milo_topic_label') || 'Job Interview';

    // Update Header Level Pill & Topic Box
    const levelPill = document.getElementById('practiceLevelPill');
    if (levelPill) levelPill.textContent = `Level ${currentLevel}`;

    const topicValue = document.getElementById('practiceTopicValue');
    if (topicValue) topicValue.textContent = topicLabel;

    // Show initial greeting from MILO
    const initialGreeting = sessionStorage.getItem('milo_initial_greeting') ||
        "Good morning! Thank you for coming in today. Please have a seat. Let's start: could you tell me a little bit about yourself?";
    const initialAudio = sessionStorage.getItem('milo_initial_audio');
    const initialTranslation = sessionStorage.getItem('milo_initial_translation');

    appendMessage(initialGreeting, 'milo', initialAudio, initialTranslation);

    // Bind Keyboard Slide Toggle
    btnToggleKeyboard.addEventListener('click', () => {
        if (textInputSlide.style.display === 'none') {
            textInputSlide.style.display = 'flex';
            userTextInput.focus();
        } else {
            textInputSlide.style.display = 'none';
        }
    });

    // Bind Text Send
    btnSendText.addEventListener('click', sendTextMessage);
    userTextInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendTextMessage();
    });

    // Bind Mic Action
    btnMicAction.addEventListener('click', toggleRecording);

    // Bind End Session
    btnEndSession.addEventListener('click', confirmEndSession);

    // Bind Pillar Tabs (Grammar, Vocab, Fluency)
    document.querySelectorAll('.eval-pillar-tab').forEach(btn => {
        btn.addEventListener('click', () => {
            switchPillarTab(btn.dataset.pillar);
        });
    });
});

// ─── Message Store & Tracking ───────────────────────────────────────────────
const messageStore = new Map();
let messageIdCounter = 0;

// ─── Messaging ───────────────────────────────────────────────────────────────
function appendMessage(text, sender, audioBase64 = null, translation = null) {
    const isMilo = sender === 'milo';
    const msgId = ++messageIdCounter;

    // Store in message store for audio & translation interactions
    let audioId = null;
    if (audioBase64) {
        audioId = audioIdCounter++;
        audioStore.set(audioId, audioBase64);
    }
    messageStore.set(msgId, {
        id: msgId,
        text,
        sender,
        audioBase64,
        audioId,
        translation
    });

    const row = document.createElement('div');
    row.id = `msgWrapper-${msgId}`;
    row.className = isMilo ? 'bubble-milo-wrapper' : 'bubble-user-wrapper';

    if (isMilo) {
        row.innerHTML = `
            <div class="bubble-milo">
                <div class="milo-header-row">
                    <div class="milo-text-main" id="msgText-${msgId}">${escapeHtml(text)}</div>
                    <button type="button" class="btn-speaker-inline" onclick="playMiloSpeech(${msgId}, this)" title="Dengarkan Suara MILO">
                        <i class="fa-solid fa-volume-high"></i>
                    </button>
                </div>
                <div class="bubble-translation-wrapper">
                    <button type="button" class="btn-bubble-translate" id="btnTrans-${msgId}" onclick="toggleBubbleTranslation(${msgId}, this)" title="Terjemahkan ke Bahasa Indonesia">
                        <i class="fa-solid fa-language"></i>
                        <span>Terjemahkan</span>
                    </button>
                    <div class="milo-translation-body" id="transBox-${msgId}" style="display: none;">
                        <div class="milo-translation-text">
                            <span id="transText-${msgId}">${escapeHtml(translation || '')}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    } else {
        row.innerHTML = `
            <div class="bubble-user">
                <div class="user-bubble-top">
                    <div class="user-text-main" id="userText-${msgId}">${escapeHtml(text)}</div>
                    <div class="user-avatar-badge" title="Anda">
                        <span style="font-weight: 700; font-size: 11px;">You</span>
                    </div>
                </div>
                <div class="user-bubble-actions">
                    <button type="button" class="btn-bubble-action-user" onclick="playUserSpeech(${msgId}, this)" title="Dengarkan pengucapan kalimat Anda">
                        <i class="fa-solid fa-volume-high"></i>
                        <span>Dengarkan</span>
                    </button>
                    <button type="button" class="btn-bubble-action-user btn-user-translate" id="btnTrans-${msgId}" onclick="toggleBubbleTranslation(${msgId}, this)" title="Terjemahkan kalimat ini ke Bahasa Indonesia">
                        <i class="fa-solid fa-language"></i>
                        <span>Terjemahkan</span>
                    </button>
                </div>
                <div class="user-translation-body" id="transBox-${msgId}" style="display: none;">
                    <div class="user-translation-text">
                        <span id="transText-${msgId}">${escapeHtml(translation || '')}</span>
                    </div>
                </div>
            </div>
        `;
    }

    messagesContainer.appendChild(row);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    // Update Progress bar width slightly per turn
    turnCount++;
    if (progressBarFill) {
        const pct = Math.min(95, 20 + (turnCount * 12));
        progressBarFill.style.width = `${pct}%`;
    }

    // Auto play audio if from MILO
    if (isMilo && audioBase64) {
        autoPlayAudio(audioBase64);
    }

    return msgId;
}

// ─── Audio Playback Handlers ────────────────────────────────────────────────
function playMiloSpeech(msgId, btnElement) {
    const msg = messageStore.get(msgId);
    if (!msg) return;

    if (msg.audioId !== null && audioStore.has(msg.audioId)) {
        playAudio(btnElement, msg.audioId);
    } else {
        speakEnglishWithSynthesis(msg.text, btnElement);
    }
}
window.playMiloSpeech = playMiloSpeech;

function playUserSpeech(msgId, btnElement) {
    const msg = messageStore.get(msgId);
    if (!msg || !msg.text) return;
    speakEnglishWithSynthesis(msg.text, btnElement);
}
window.playUserSpeech = playUserSpeech;

function speakEnglishWithSynthesis(text, btnElement) {
    if (!('speechSynthesis' in window)) {
        alert('Browser Anda tidak mendukung Web Speech API.');
        return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    utterance.rate = 0.95;

    let icon = null;
    let origClass = '';
    if (btnElement) {
        icon = btnElement.querySelector('i');
        if (icon) {
            origClass = icon.className;
            icon.className = 'fa-solid fa-spinner fa-spin';
        }
    }

    utterance.onend = () => {
        if (icon) icon.className = origClass;
    };
    utterance.onerror = () => {
        if (icon) icon.className = origClass;
    };

    window.speechSynthesis.speak(utterance);
}
window.speakEnglishWithSynthesis = speakEnglishWithSynthesis;

// ─── Inline Translation Toggle ──────────────────────────────────────────────
async function toggleBubbleTranslation(msgId, btnElement) {
    const msg = messageStore.get(msgId);
    if (!msg) return;

    const transBox = document.getElementById(`transBox-${msgId}`);
    const transText = document.getElementById(`transText-${msgId}`);
    if (!transBox || !transText) return;

    // Toggle close if already open
    if (transBox.style.display !== 'none') {
        transBox.style.display = 'none';
        btnElement.classList.remove('active');
        btnElement.innerHTML = `<i class="fa-solid fa-language"></i> <span>Terjemahkan</span>`;
        return;
    }

    // If translation is already stored, display immediately
    if (msg.translation && msg.translation.trim()) {
        transText.textContent = msg.translation;
        transBox.style.display = 'block';
        btnElement.classList.add('active');
        btnElement.innerHTML = `<i class="fa-solid fa-check"></i> <span>Tutup Terjemahan</span>`;
        return;
    }

    // Translation needs to be fetched on-demand via /api/v1/chat/translate
    try {
        transText.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> <span>Menerjemahkan ke Bahasa Indonesia...</span>`;
        transBox.style.display = 'block';
        btnElement.classList.add('active');
        btnElement.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> <span>Menerjemahkan...</span>`;

        const resp = await fetch('/api/v1/translate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: msg.text })
        });

        if (!resp.ok) {
            throw new Error(`Server returned ${resp.status}`);
        }

        const data = await resp.json();
        const indonesianText = data.translation || '(Tidak dapat diterjemahkan)';
        msg.translation = indonesianText;
        transText.textContent = indonesianText;
        btnElement.innerHTML = `<i class="fa-solid fa-check"></i> <span>Tutup Terjemahan</span>`;
    } catch (err) {
        console.error('Translation error:', err);
        transText.textContent = 'Gagal memuat terjemahan. Silakan coba lagi.';
        btnElement.innerHTML = `<i class="fa-solid fa-arrow-rotate-right"></i> <span>Coba Lagi</span>`;
    }
}
window.toggleBubbleTranslation = toggleBubbleTranslation;

// ─── Send Text ───────────────────────────────────────────────────────────────
async function sendTextMessage() {
    const text = userTextInput.value.trim();
    if (!text) return;

    userTextInput.value = '';
    appendMessage(text, 'user');

    if (waveformBox) waveformBox.classList.add('active-recording');
    setCompanionState('thinking', 'Milo sedang berpikir...');

    try {
        const response = await fetch('/api/v1/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId,
                message: text,
                return_audio: true,
                cefr_level: currentLevel,
            })
        });

        if (waveformBox) waveformBox.classList.remove('active-recording');

        if (!response.ok) {
            const err = await response.text();
            throw new Error(`Chat error ${response.status}: ${err}`);
        }

        const data = await response.json();

        // Render MILO's reply with audio and Indonesian translation
        setCompanionState('speaking', 'Milo menjawab...');
        appendMessage(data.response_text, 'milo', data.audio_base64, data.translation);
        setTimeout(() => setCompanionState('idle', 'Milo siap berlatih'), 4000);

        // Update real-time Speech Evaluation HUD
        if (data.feedback) {
            updateEvaluationHUD(data.feedback);
        }
    } catch (err) {
        if (waveformBox) waveformBox.classList.remove('active-recording');
        setCompanionState('idle', 'Milo siap berlatih');
        console.error('Chat error:', err);
        appendMessage('Sorry, a connection error occurred: ' + err.message, 'milo');
    }
}

// ─── Voice Recording ─────────────────────────────────────────────────────────
async function toggleRecording() {
    if (!isRecording) {
        await startRecording();
    } else {
        stopRecording();
    }
}

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            audio: {
                channelCount: 1, // Clean mono audio for Whisper
                echoCancellation: true,
                noiseSuppression: false, // Turn off aggressive WebRTC gating so Whisper gets clear, unclipped speech
                autoGainControl: true,
            }
        });
        audioChunks = [];

        let chosenMime = 'audio/webm';
        if (typeof MediaRecorder !== 'undefined') {
            if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
                chosenMime = 'audio/webm;codecs=opus';
            } else if (MediaRecorder.isTypeSupported('audio/webm')) {
                chosenMime = 'audio/webm';
            } else if (MediaRecorder.isTypeSupported('audio/ogg;codecs=opus')) {
                chosenMime = 'audio/ogg;codecs=opus';
            } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
                chosenMime = 'audio/mp4';
            }
        }

        const recorderOptions = chosenMime ? { mimeType: chosenMime, audioBitsPerSecond: 128000 } : undefined;
        mediaRecorder = new MediaRecorder(stream, recorderOptions);

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
            stream.getTracks().forEach(track => track.stop());
            const blobType = mediaRecorder.mimeType || chosenMime || 'audio/webm';
            const audioBlob = new Blob(audioChunks, { type: blobType });

            if (audioBlob.size > 500) {
                await sendVoiceMessage(audioBlob);
            } else {
                appendMessage('(Recording too short. Please speak while the microphone is active.)', 'milo');
            }
        };

        mediaRecorder.start();
        isRecording = true;
        btnMicAction.classList.add('recording');
        if (waveformBox) waveformBox.classList.add('active-recording');
        setCompanionState('listening', 'Milo mendengarkan kamu...');
    } catch (err) {
        console.error('Mic access error:', err);
        setCompanionState('idle', 'Milo siap berlatih');
        alert('Please allow microphone permissions in your browser to speak with MILO!');
    }
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
        isRecording = false;
        btnMicAction.classList.remove('recording');
        if (waveformBox) waveformBox.classList.remove('active-recording');
        setCompanionState('thinking', 'Milo memproses suara...');
    }
}

async function sendVoiceMessage(audioBlob) {
    const userMsgId = appendMessage('(Listening...)', 'user');

    // Visual indicator that MILO is processing
    const thinkingRow = document.createElement('div');
    thinkingRow.className = 'chat-message-row milo-row thinking-indicator-row';
    thinkingRow.id = 'miloVoiceThinking';
    thinkingRow.innerHTML = `
        <div class="milo-avatar-icon"><span style="font-weight: 800; font-size: 14px; color: #FFFFFF;">M</span></div>
        <div class="message-bubble milo-bubble thinking-bubble" style="opacity: 0.85; font-style: italic;">
            <i class="fa-solid fa-spinner fa-spin"></i> <span id="miloThinkingStatus">MILO is listening...</span>
        </div>
    `;
    messagesContainer.appendChild(thinkingRow);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    try {
        let ext = 'webm';
        if (audioBlob.type.includes('ogg')) ext = 'ogg';
        else if (audioBlob.type.includes('mp4')) ext = 'm4a';
        else if (audioBlob.type.includes('wav')) ext = 'wav';

        // ── Phase 1: Ultra-fast local Whisper ASR (~0.3s on RTX 3050 CUDA) ──
        const asrFormData = new FormData();
        asrFormData.append('audio', audioBlob, `speech.${ext}`);

        let transcriptText = '';
        try {
            const asrResponse = await fetch('/api/v1/voice/transcribe', {
                method: 'POST',
                body: asrFormData,
            });
            if (asrResponse.ok) {
                const asrData = await asrResponse.json();
                transcriptText = (asrData.transcript || '').trim();
            }
        } catch (asrErr) {
            console.warn('Fast ASR endpoint unreachable, will fallback to full voice pipeline:', asrErr);
        }

        // If fast ASR returned text:
        if (transcriptText) {
            // INSTANT UI UPDATE: User sees what they said within 0.3s!
            const userTextElem = document.getElementById(`userText-${userMsgId}`);
            if (userTextElem) userTextElem.textContent = transcriptText;
            const msgObj = messageStore.get(userMsgId);
            if (msgObj) msgObj.text = transcriptText;

            const statusSpan = document.getElementById('miloThinkingStatus');
            if (statusSpan) statusSpan.textContent = 'MILO is preparing a response...';

            // ── Phase 2: Query Tutor & TTS with recognized text ──
            const chatResponse = await fetch('/api/v1/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: sessionId,
                    message: transcriptText,
                    return_audio: true,
                    cefr_level: currentLevel,
                })
            });

            thinkingRow.remove();

            if (!chatResponse.ok) {
                const errText = await chatResponse.text();
                throw new Error(`Chat error ${chatResponse.status}: ${errText}`);
            }

            const data = await chatResponse.json();

            // Render MILO's reply with audio and Indonesian translation
            setCompanionState('speaking', 'Milo menjawab...');
            appendMessage(data.response_text, 'milo', data.audio_base64, data.translation);
            setTimeout(() => setCompanionState('idle', 'Milo siap berlatih'), 4000);

            // Update real-time Speech Evaluation HUD
            if (data.feedback) {
                updateEvaluationHUD(data.feedback);
            }
            return;
        }

        // Fallback / standard route if fast ASR gave empty string or failed
        const formData = new FormData();
        formData.append('audio', audioBlob, `speech.${ext}`);
        formData.append('session_id', sessionId);
        formData.append('return_audio', 'true');
        formData.append('cefr_level', currentLevel);

        const response = await fetch('/api/v1/voice', {
            method: 'POST',
            body: formData,
        });

        thinkingRow.remove();

        if (!response.ok) {
            const errText = await response.text();
            let parsedDetail = errText;
            try {
                const parsed = JSON.parse(errText);
                parsedDetail = parsed.detail || errText;
            } catch (e) {}
            throw new Error(`Voice error ${response.status}: ${parsedDetail}`);
        }

        const data = await response.json();

        // Update placeholder user bubble with actual transcript
        const finalTranscript = data.transcript || '(Inaudible speech)';
        const userTextElem = document.getElementById(`userText-${userMsgId}`);
        if (userTextElem) userTextElem.textContent = finalTranscript;
        const msgObj = messageStore.get(userMsgId);
        if (msgObj) msgObj.text = finalTranscript;

        // Render MILO's reply with audio and Indonesian translation
        setCompanionState('speaking', 'Milo menjawab...');
        appendMessage(data.response_text, 'milo', data.audio_base64, data.translation);
        setTimeout(() => setCompanionState('idle', 'Milo siap berlatih'), 4000);

        // Update real-time Speech Evaluation HUD
        if (data.feedback) {
            updateEvaluationHUD(data.feedback);
        }
    } catch (err) {
        const ind = document.getElementById('miloVoiceThinking');
        if (ind) ind.remove();
        setCompanionState('idle', 'Milo siap berlatih');
        console.error('Voice processing error:', err);
        appendMessage('Sorry, error processing voice: ' + err.message, 'milo');
    }
}

// ─── Real-Time AI Speech Evaluation HUD (Tanpa Score, Fokus Pembetulan & Tips) ───
let grammarCount = 0;
let vocabCount = 0;
let fluencyCount = 0;

function switchPillarTab(pillar) {
    const tabGrammar = document.getElementById('tabGrammar');
    const tabVocab = document.getElementById('tabVocab');
    const tabFluency = document.getElementById('tabFluency');
    const paneGrammar = document.getElementById('paneGrammar');
    const paneVocab = document.getElementById('paneVocab');
    const paneFluency = document.getElementById('paneFluency');

    [tabGrammar, tabVocab, tabFluency].forEach(btn => btn?.classList.remove('active'));
    [paneGrammar, paneVocab, paneFluency].forEach(pane => {
        if (pane) pane.style.display = 'none';
    });

    if (pillar === 'grammar') {
        tabGrammar?.classList.add('active');
        if (paneGrammar) paneGrammar.style.display = 'flex';
    } else if (pillar === 'vocab') {
        tabVocab?.classList.add('active');
        if (paneVocab) paneVocab.style.display = 'flex';
    } else if (pillar === 'fluency') {
        tabFluency?.classList.add('active');
        if (paneFluency) paneFluency.style.display = 'flex';
    }
}

function updateEvaluationHUD(feedback) {
    if (!feedback) return;
    feedbackHistory.push(feedback);

    const evalInitialPlaceholder = document.getElementById('evalInitialPlaceholder');
    if (evalInitialPlaceholder) {
        evalInitialPlaceholder.style.display = 'none';
    }

    // Default to active tab or grammar
    const activeTab = document.querySelector('.eval-pillar-tab.active')?.dataset.pillar || 'grammar';
    switchPillarTab(activeTab);

    // Group corrections by error_type
    const corrections = feedback.corrections || [];
    const grammarCorrs = corrections.filter(c => (c.error_type || '').toLowerCase() === 'grammar');
    const vocabCorrs = corrections.filter(c => (c.error_type || '').toLowerCase().includes('vocab'));
    const fluencyCorrs = corrections.filter(c => (c.error_type || '').toLowerCase().includes('fluency'));

    // Handle unclassified corrections
    const otherCorrs = corrections.filter(c => {
        const t = (c.error_type || '').toLowerCase();
        return t !== 'grammar' && !t.includes('vocab') && !t.includes('fluency');
    });
    grammarCorrs.push(...otherCorrs);

    // Update Tab Badges (Correction Count)
    grammarCount += grammarCorrs.length;
    vocabCount += vocabCorrs.length;
    fluencyCount += fluencyCorrs.length;

    const badgeGrammar = document.getElementById('badgeGrammar');
    const badgeVocab = document.getElementById('badgeVocab');
    const badgeFluency = document.getElementById('badgeFluency');
    if (badgeGrammar) badgeGrammar.textContent = grammarCount;
    if (badgeVocab) badgeVocab.textContent = vocabCount;
    if (badgeFluency) badgeFluency.textContent = fluencyCount;

    // Render streams for each pillar
    const streamGrammar = document.getElementById('streamGrammar');
    const streamVocab = document.getElementById('streamVocab');
    const streamFluency = document.getElementById('streamFluency');

    renderPillarCorrections(streamGrammar, grammarCorrs, 'Tata bahasa Anda sudah tepat!');
    renderPillarCorrections(streamVocab, vocabCorrs, 'Pilihan kata sudah variatif & sesuai konteks!');
    renderPillarCorrections(streamFluency, fluencyCorrs, 'Alur kalimat Anda mengalir secara natural!');

    // Update Pillar Specific Tips
    const tipTextGrammar = document.getElementById('tipTextGrammar');
    const tipTextVocab = document.getElementById('tipTextVocab');
    const tipTextFluency = document.getElementById('tipTextFluency');

    if (feedback.grammar_tip && tipTextGrammar) {
        tipTextGrammar.textContent = feedback.grammar_tip;
    }
    if (feedback.vocabulary_tip && tipTextVocab) {
        tipTextVocab.textContent = feedback.vocabulary_tip;
    }
    if (feedback.fluency_tip && tipTextFluency) {
        tipTextFluency.textContent = feedback.fluency_tip;
    } else if (feedback.tip && tipTextFluency) {
        tipTextFluency.textContent = feedback.tip;
    }

    // Encouragement Note
    const evalPositiveNote = document.getElementById('evalPositiveNote');
    const evalPositiveText = document.getElementById('evalPositiveText');
    if (feedback.positive_note && evalPositiveNote && evalPositiveText) {
        evalPositiveNote.style.display = 'flex';
        evalPositiveText.textContent = feedback.positive_note;
    }
}

function renderPillarCorrections(container, items, emptyMessage) {
    if (!container) return;

    // If there are real correction items, remove existing empty message
    const emptyItem = container.querySelector('.pillar-empty-item');
    if (items.length > 0 && emptyItem) {
        emptyItem.remove();
    }

    if (items.length === 0 && container.children.length === 0) {
        container.innerHTML = `<div class="pillar-empty-item">✓ ${escapeHtml(emptyMessage)}</div>`;
        return;
    }

    items.forEach(c => {
        const card = document.createElement('div');
        card.className = 'pillar-corr-card';
        card.innerHTML = `
            <div class="pillar-corr-orig">✗ ${escapeHtml(c.original)}</div>
            <div class="pillar-corr-fixed">✓ ${escapeHtml(c.corrected)}</div>
            ${c.explanation ? `<div class="pillar-corr-expl">${escapeHtml(c.explanation)}</div>` : ''}
        `;
        container.prepend(card);
    });
}

function avg(nums) {
    if (!nums || nums.length === 0) return 0;
    return nums.reduce((a, b) => a + b, 0) / nums.length;
}

// ─── End Session ─────────────────────────────────────────────────────────────
async function confirmEndSession() {
    if (!confirm('Apakah Anda ingin mengakhiri sesi latihan ini?')) {
        return;
    }

    showGlobalLoading('Menganalisis hasil percakapan & menghitung skor CEFR...');

    try {
        const response = await fetch('/api/v1/session/end', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
        });

        if (!response.ok) {
            const err = await response.text();
            throw new Error(`End session error: ${err}`);
        }

        const summaryData = await response.json();

        // Store result for summary page
        sessionStorage.setItem('milo_summary_data', JSON.stringify(summaryData));

        // Navigate to dedicated summary page
        window.location.href = `/ui/summary.html?session_id=${encodeURIComponent(sessionId)}`;
    } catch (err) {
        hideGlobalLoading();
        alert('Gagal mengakhiri sesi: ' + err.message);
        console.error('End session error:', err);
    }
}
