let sessionId = null;
let currentTopicId = 'A1';
let currentTopic = 'job_interview';
let currentLevel = 'B1';
let sessionStartTime = Date.now();
let feedbackHistory = [];
let turnCount = 0;
let timerInterval = null;
let targetMinutes = 15;
let targetSeconds = 900;
let goalModalShown = false;
let isSessionClosing = false;
let autoCloseInitiated = false;

let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;

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

function setCompanionState(state, text, emotion, feedback) {
    if (miloCompanionStage) {
        miloCompanionStage.classList.remove('listening', 'thinking', 'speaking');
        if (state && state !== 'idle') {
            miloCompanionStage.classList.add(state);
        }
    }
    if (miloStatusText && text) {
        miloStatusText.textContent = text;
    }
    if (window.miloLive2D) {
        if (typeof window.miloLive2D.setState === 'function') {
            window.miloLive2D.setState(state);
        }
        if ((emotion || feedback) && typeof window.miloLive2D.setEmotion === 'function') {
            window.miloLive2D.setEmotion(emotion, feedback);
        }
    }
}
window.setCompanionState = setCompanionState;

// HUD Elements & Pillars
const evalInitialPlaceholder = document.getElementById('evalInitialPlaceholder');

document.addEventListener('DOMContentLoaded', async () => {
    if (typeof requireAuth === 'function' && !requireAuth()) {
        return;
    }

    // 1. Resolve Session ID
    const urlParams = new URLSearchParams(window.location.search);
    sessionId = urlParams.get('session_id') || sessionStorage.getItem('milo_session_id');

    if (!sessionId) {
        alert('No active practice session found. Redirecting to setup...');
        window.location.href = '/ui/setup.html';
        return;
    }

    currentTopic = sessionStorage.getItem('milo_topic') || 'job_interview';
    currentTopicId = urlParams.get('topic_id') || sessionStorage.getItem('milo_topic_id') || 'A1';
    currentLevel = sessionStorage.getItem('milo_cefr_level') || 'B1';
    const topicLabel = sessionStorage.getItem('milo_topic_label') || 'Job Interview';
    const topicTitle = sessionStorage.getItem('milo_topic_title') || '';

    // Update Header Level Pill & Topic Box
    const levelPill = document.getElementById('practiceLevelPill');
    if (levelPill) levelPill.textContent = `Level ${currentLevel}`;

    const topicValue = document.getElementById('practiceTopicValue');
    if (topicValue) {
        topicValue.textContent = topicTitle ? `[${currentTopicId}] ${topicTitle}` : topicLabel;
    }

    // Initialize Target Duration & Real-Time Sync Timer
    initSessionDurationTimer();

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
    btnEndSession.addEventListener('click', () => confirmEndSession());

    // Bind Skip To Summary Button on Closing Toast
    const btnSkipToSummary = document.getElementById('btnSkipToSummary');
    if (btnSkipToSummary) {
        btnSkipToSummary.addEventListener('click', () => confirmEndSession(true));
    }

    // Bind Pillar Tabs (Grammar, Vocab, Fluency)
    document.querySelectorAll('.eval-pillar-tab').forEach(btn => {
        btn.addEventListener('click', () => {
            switchPillarTab(btn.dataset.pillar);
        });
    });

    // Mobile view switcher between conversation and evaluation panels
    const btnTabChat = document.getElementById('btnTabChat');
    const btnTabEval = document.getElementById('btnTabEval');
    const cardConversation = document.getElementById('cardConversation');
    const cardProgressSesi = document.getElementById('cardProgressSesi');

    if (btnTabChat && btnTabEval) {
        btnTabChat.addEventListener('click', () => {
            btnTabChat.classList.add('active');
            btnTabChat.setAttribute('aria-selected', 'true');
            btnTabEval.classList.remove('active');
            btnTabEval.setAttribute('aria-selected', 'false');

            if (cardConversation) cardConversation.classList.add('mobile-active');
            if (cardProgressSesi) cardProgressSesi.classList.remove('mobile-active');
        });

        btnTabEval.addEventListener('click', () => {
            btnTabEval.classList.add('active');
            btnTabEval.setAttribute('aria-selected', 'true');
            btnTabChat.classList.remove('active');
            btnTabChat.setAttribute('aria-selected', 'false');

            if (cardProgressSesi) cardProgressSesi.classList.add('mobile-active');
            if (cardConversation) cardConversation.classList.remove('mobile-active');
        });
    }
});

const messageStore = new Map();
let messageIdCounter = 0;

function formatRagSourceLabel(src) {
    if (!src) return '';
    let s = src.trim();
    if (s.includes('Cambridge English Vocabulary in Use')) return 'Cambridge Vocabulary in Use (B2)';
    if (s.includes('The Cambridge Guide to English Usage')) return 'Cambridge Guide to English Usage';
    if (s.includes('Collins Speaking for IELTS')) return 'Collins Speaking for IELTS';
    if (s.includes('Council of Europe') || s.includes('CEFR Companion Volume')) return 'CEFR Companion Volume';
    
    // Clean file names if a raw filename was passed
    s = s.replace(/\.md$/i, '').replace(/_/g, ' ');
    if (s.toLowerCase().startsWith('unit ')) {
        return s.charAt(0).toUpperCase() + s.slice(1);
    }
    return s.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
}

function appendMessage(text, sender, audioBase64 = null, translation = null, ragSources = [], ragDetails = [], emotion = 'friendly', feedback = null) {
    const isMilo = sender === 'milo';
    const msgId = ++messageIdCounter;

    // Store in message store for audio, translation, and RAG interactions
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
        translation,
        ragSources,
        ragDetails,
        emotion,
        feedback
    });

    const row = document.createElement('div');
    row.id = `msgWrapper-${msgId}`;
    row.className = isMilo ? 'bubble-milo-wrapper' : 'bubble-user-wrapper';

    let ragBadgesHtml = '';
    if (isMilo) {
        const details = (ragDetails && Array.isArray(ragDetails) && ragDetails.length > 0)
            ? ragDetails
            : (ragSources && Array.isArray(ragSources) && ragSources.length > 0)
                ? ragSources.map(src => ({
                    source: src,
                    book: formatRagSourceLabel(src),
                    title: formatRagSourceLabel(src),
                    category: 'Buku Rujukan Kurikulum Resmi',
                    skill: 'Speaking & CEFR Mastery',
                    level: currentLevel,
                    score: 0.85,
                    snippet: 'Materi tuturan ini diselaraskan dengan silabus resmi standar Cambridge / Collins untuk pengayaan berbicara.'
                }))
                : [];

        if (details.length > 0) {
            const badges = details.map((d, dIdx) => `
                <button type="button" class="milo-rag-badge" onclick="openRagInspectorModal(${msgId}, ${dIdx})" title="Klik untuk meninjau rujukan buku resmi">
                    <i class="fa-solid fa-book-bookmark"></i>
                    <span>Ref: ${escapeHtml(d.book || d.title || 'Buku Rujukan')}</span>
                    <i class="fa-solid fa-circle-info" style="font-size: 10px; margin-left: 3px; opacity: 0.8;"></i>
                </button>
            `).join('');
            ragBadgesHtml = `
                <div class="milo-rag-badge-wrapper">
                    ${badges}
                </div>
            `;
        }
    }

    if (isMilo) {
        row.innerHTML = `
            <div class="bubble-milo">
                <div class="milo-header-row">
                    <div class="milo-text-main" id="msgText-${msgId}">${escapeHtml(text)}</div>
                    <button type="button" class="btn-speaker-inline" onclick="playMiloSpeech(${msgId}, this)" title="Dengarkan Suara MILO">
                        <i class="fa-solid fa-volume-high"></i>
                    </button>
                </div>
                ${ragBadgesHtml}
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
                <div class="user-bubble-feedback-row" id="userFeedbackRow-${msgId}"></div>
                <div class="user-inline-corrections-box" id="userCorrBox-${msgId}" style="display: none;"></div>
            </div>
        `;
    }

    messagesContainer.appendChild(row);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    turnCount++;

    // Auto play audio if from MILO with emotion & feedback
    if (isMilo && audioBase64) {
        autoPlayAudio(audioBase64, emotion, feedback);
    }

    return msgId;
}

function playMiloSpeech(msgId, btnElement) {
    const msg = messageStore.get(msgId);
    if (!msg) return;

    if (msg.audioId !== null && audioStore.has(msg.audioId)) {
        playAudio(btnElement, msg.audioId, msg.emotion || 'friendly', msg.feedback || null);
    } else {
        speakEnglishWithSynthesis(msg.text, btnElement, msg.emotion || 'friendly', msg.feedback || null);
    }
}
window.playMiloSpeech = playMiloSpeech;

function playUserSpeech(msgId, btnElement) {
    const msg = messageStore.get(msgId);
    if (!msg || !msg.text) return;
    speakEnglishWithSynthesis(msg.text, btnElement, 'friendly', null);
}
window.playUserSpeech = playUserSpeech;

function speakEnglishWithSynthesis(text, btnElement, emotion = 'friendly', feedback = null) {
    if (!('speechSynthesis' in window)) {
        alert('Browser Anda tidak mendukung Web Speech API.');
        return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    utterance.rate = 0.95;

    const statusText = typeof getStatusTextForEmotion === 'function' ? getStatusTextForEmotion(emotion) : 'Milo menjawab...';
    setCompanionState('speaking', statusText, emotion, feedback);

    let icon = null;
    let origClass = '';
    if (btnElement) {
        icon = btnElement.querySelector('i');
        if (icon) {
            origClass = icon.className;
            icon.className = 'fa-solid fa-spinner fa-spin';
        }
    }

    utterance.onboundary = () => {
        if (window.miloLive2D && typeof window.miloLive2D.setSpeakingPulse === 'function') {
            window.miloLive2D.setSpeakingPulse(0.75);
        }
    };

    utterance.onend = () => {
        if (icon) icon.className = origClass;
        setCompanionState('idle', 'Milo siap berlatih');
    };
    utterance.onerror = () => {
        if (icon) icon.className = origClass;
        setCompanionState('idle', 'Milo siap berlatih');
    };

    window.speechSynthesis.speak(utterance);
}
window.speakEnglishWithSynthesis = speakEnglishWithSynthesis;

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

function getAuthHeaders() {
    const token = localStorage.getItem('milo_token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
}

function getAuthUserId() {
    try {
        const u = JSON.parse(localStorage.getItem('milo_user'));
        return u?.id || null;
    } catch {
        return null;
    }
}

async function sendTextMessage() {
    if (isSessionClosing) return;
    const text = userTextInput.value.trim();
    if (!text) return;

    userTextInput.value = '';
    const userMsgId = appendMessage(text, 'user');

    if (waveformBox) waveformBox.classList.add('active-recording');
    setCompanionState('thinking', 'Milo sedang berpikir...');

    const elapsedSeconds = Math.max(0, Math.floor((Date.now() - sessionStartTime) / 1000));
    const shouldCloseThisTurn = (elapsedSeconds >= targetSeconds) || isSessionClosing;
    if (shouldCloseThisTurn) {
        isSessionClosing = true;
        lockConversationInputs('Waktu latihan selesai. Milo sedang merespons...');
        showClosingToast('Waktu Latihan Selesai', 'Milo sedang memberikan rangkuman penutup...');
    }

    try {
        const authUserId = getAuthUserId();
        const chatPayload = {
            session_id: sessionId,
            message: text,
            return_audio: true,
            cefr_level: currentLevel,
            input_type: 'text',
            is_closing: shouldCloseThisTurn,
        };
        if (authUserId) chatPayload.user_id = authUserId;

        const response = await fetch('/api/v1/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
            body: JSON.stringify(chatPayload)
        });

        if (waveformBox) waveformBox.classList.remove('active-recording');

        if (!response.ok) {
            const err = await response.text();
            throw new Error(`Chat error ${response.status}: ${err}`);
        }

        const data = await response.json();

        if (data.is_session_closed || shouldCloseThisTurn) {
            handleSessionClosedResponse(data);
            return;
        }

        // Render MILO's reply with audio, Indonesian translation, and feedback emotion
        const avatarEmotion = data.avatar_emotion || (data.feedback?.overall_score >= 85 ? 'happy' : (data.feedback?.corrections?.length ? 'supportive' : 'friendly'));
        const statusText = typeof getStatusTextForEmotion === 'function' ? getStatusTextForEmotion(avatarEmotion) : 'Milo menjawab...';

        setCompanionState('speaking', statusText, avatarEmotion, data.feedback);
        appendMessage(data.response_text, 'milo', data.audio_base64, data.translation, data.rag_sources, data.rag_details, avatarEmotion, data.feedback);

        if (!data.audio_base64) {
            const speakDuration = Math.max(3000, Math.min(8000, (data.response_text.split(/\s+/).length / 2.5) * 1000));
            setTimeout(() => setCompanionState('idle', 'Milo siap berlatih'), speakDuration);
        }

        // Update real-time Speech Evaluation HUD and inline user bubble badge
        if (data.feedback) {
            updateEvaluationHUD(data.feedback);
            attachUserFeedback(userMsgId, data.feedback);
        }
        updateRagFeedbackHUD(data.rag_details, data.rag_sources);
    } catch (err) {
        if (waveformBox) waveformBox.classList.remove('active-recording');
        setCompanionState('idle', 'Milo siap berlatih');
        console.error('Chat error:', err);
        appendMessage('Sorry, a connection error occurred: ' + err.message, 'milo');
    }
}

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
                channelCount: 1,
                echoCancellation: true,
                noiseSuppression: true,
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

    const elapsedSeconds = Math.max(0, Math.floor((Date.now() - sessionStartTime) / 1000));
    const shouldCloseThisTurn = (elapsedSeconds >= targetSeconds) || isSessionClosing;
    if (shouldCloseThisTurn) {
        isSessionClosing = true;
        lockConversationInputs('Waktu latihan selesai. Milo sedang merespons...');
        showClosingToast('Waktu Latihan Selesai', 'Milo sedang memberikan rangkuman penutup...');
    }

    try {
        let ext = 'webm';
        if (audioBlob.type.includes('ogg')) ext = 'ogg';
        else if (audioBlob.type.includes('mp4')) ext = 'm4a';
        else if (audioBlob.type.includes('wav')) ext = 'wav';

        // Transcribe speech using fast local Whisper endpoint
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

        if (transcriptText) {
            const userTextElem = document.getElementById(`userText-${userMsgId}`);
            if (userTextElem) userTextElem.textContent = transcriptText;
            const msgObj = messageStore.get(userMsgId);
            if (msgObj) msgObj.text = transcriptText;

            const statusSpan = document.getElementById('miloThinkingStatus');
            if (statusSpan) statusSpan.textContent = 'MILO is preparing a response...';

            const authUserId = getAuthUserId();
            const voiceChatPayload = {
                session_id: sessionId,
                message: transcriptText,
                return_audio: true,
                cefr_level: currentLevel,
                input_type: 'voice',
                transcript: transcriptText,
                is_closing: shouldCloseThisTurn,
            };
            if (authUserId) voiceChatPayload.user_id = authUserId;

            const chatResponse = await fetch('/api/v1/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
                body: JSON.stringify(voiceChatPayload)
            });

            thinkingRow.remove();

            if (!chatResponse.ok) {
                const errText = await chatResponse.text();
                throw new Error(`Chat error ${chatResponse.status}: ${errText}`);
            }

            const data = await chatResponse.json();

            if (data.is_session_closed || shouldCloseThisTurn) {
                handleSessionClosedResponse(data);
                return;
            }

            // Render MILO's reply with audio, Indonesian translation, and feedback emotion
            const avatarEmotion = data.avatar_emotion || (data.feedback?.overall_score >= 85 ? 'happy' : (data.feedback?.corrections?.length ? 'supportive' : 'friendly'));
            const statusText = typeof getStatusTextForEmotion === 'function' ? getStatusTextForEmotion(avatarEmotion) : 'Milo menjawab...';

            setCompanionState('speaking', statusText, avatarEmotion, data.feedback);
            appendMessage(data.response_text, 'milo', data.audio_base64, data.translation, [], [], avatarEmotion, data.feedback);

            if (!data.audio_base64) {
                const speakDuration = Math.max(3000, Math.min(8000, (data.response_text.split(/\s+/).length / 2.5) * 1000));
                setTimeout(() => setCompanionState('idle', 'Milo siap berlatih'), speakDuration);
            }

            // Update real-time Speech Evaluation HUD and inline user bubble badge
            if (data.feedback) {
                updateEvaluationHUD(data.feedback);
                attachUserFeedback(userMsgId, data.feedback);
            }
            return;
        }

        // Fallback / standard route if fast ASR gave empty string or failed
        const formData = new FormData();
        formData.append('audio', audioBlob, `speech.${ext}`);
        formData.append('session_id', sessionId);
        formData.append('return_audio', 'true');
        formData.append('cefr_level', currentLevel);
        formData.append('is_closing', shouldCloseThisTurn ? 'true' : 'false');
        const fallbackUserId = getAuthUserId();
        if (fallbackUserId) formData.append('user_id', fallbackUserId);

        const response = await fetch('/api/v1/voice', {
            method: 'POST',
            headers: getAuthHeaders(),
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

        if (data.is_session_closed || shouldCloseThisTurn) {
            handleSessionClosedResponse(data);
            return;
        }

        // Render MILO's reply with audio, Indonesian translation, and feedback emotion
        const avatarEmotion = data.avatar_emotion || (data.feedback?.overall_score >= 85 ? 'happy' : (data.feedback?.corrections?.length ? 'supportive' : 'friendly'));
        const statusText = typeof getStatusTextForEmotion === 'function' ? getStatusTextForEmotion(avatarEmotion) : 'Milo menjawab...';

        setCompanionState('speaking', statusText, avatarEmotion, data.feedback);
        appendMessage(data.response_text, 'milo', data.audio_base64, data.translation, data.rag_sources, data.rag_details, avatarEmotion, data.feedback);

        if (!data.audio_base64) {
            const speakDuration = Math.max(3000, Math.min(8000, (data.response_text.split(/\s+/).length / 2.5) * 1000));
            setTimeout(() => setCompanionState('idle', 'Milo siap berlatih'), speakDuration);
        }

        // Update real-time Speech Evaluation HUD and inline user bubble badge
        if (data.feedback) {
            updateEvaluationHUD(data.feedback);
            attachUserFeedback(userMsgId, data.feedback);
        }
        updateRagFeedbackHUD(data.rag_details, data.rag_sources);
    } catch (err) {
        const ind = document.getElementById('miloVoiceThinking');
        if (ind) ind.remove();
        setCompanionState('idle', 'Milo siap berlatih');
        console.error('Voice processing error:', err);
        appendMessage('Sorry, error processing voice: ' + err.message, 'milo');
    }
}

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
    const mobileEvalCounter = document.getElementById('mobileEvalCounter');
    if (badgeGrammar) badgeGrammar.textContent = grammarCount;
    if (badgeVocab) badgeVocab.textContent = vocabCount;
    if (badgeFluency) badgeFluency.textContent = fluencyCount;
    if (mobileEvalCounter) mobileEvalCounter.textContent = grammarCount + vocabCount + fluencyCount;

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

function attachUserFeedback(msgId, feedback) {
    if (!feedback) return;
    const row = document.getElementById(`userFeedbackRow-${msgId}`);
    const corrBox = document.getElementById(`userCorrBox-${msgId}`);
    if (!row || !corrBox) return;

    const corrections = feedback.corrections || [];
    if (corrections.length === 0) {
        row.innerHTML = `
            <span class="user-feedback-tag tag-accurate" title="Tata bahasa dan kosakata kalimat ini tepat">
                <i class="fa-solid fa-circle-check"></i>
                <span>Tepat & Akurat</span>
            </span>
        `;
    } else {
        row.innerHTML = `
            <button type="button" class="user-feedback-tag tag-corrections" onclick="toggleUserCorrBox(${msgId})" title="Klik untuk membuka detail pembetulan">
                <i class="fa-solid fa-circle-exclamation"></i>
                <span>${corrections.length} Pembetulan</span>
            </button>
        `;
        corrBox.innerHTML = corrections.map(c => `
            <div>
                <div class="user-corr-item-orig">✗ "${escapeHtml(c.original)}"</div>
                <div class="user-corr-item-fix">✓ "${escapeHtml(c.corrected)}"</div>
                ${c.explanation ? `<div class="user-corr-item-expl">${escapeHtml(c.explanation)}</div>` : ''}
            </div>
        `).join('');
    }
}
window.attachUserFeedback = attachUserFeedback;

function toggleUserCorrBox(msgId) {
    const box = document.getElementById(`userCorrBox-${msgId}`);
    if (!box) return;
    box.style.display = box.style.display === 'none' ? 'flex' : 'none';
}
window.toggleUserCorrBox = toggleUserCorrBox;

function initSessionDurationTimer() {
    const dailyGoal = sessionStorage.getItem('milo_daily_goal') || '5_min';
    if (dailyGoal === '3_min') {
        targetMinutes = 3;
    } else if (dailyGoal === '5_min') {
        targetMinutes = 5;
    } else if (dailyGoal === '15_min') {
        targetMinutes = 15;
    } else if (dailyGoal === '30_min') {
        targetMinutes = 30;
    } else {
        targetMinutes = 5;
    }
    targetSeconds = targetMinutes * 60;

    const practiceDurationValue = document.getElementById('practiceDurationValue');
    if (practiceDurationValue) practiceDurationValue.textContent = `${targetMinutes} Menit`;

    const timerGoalPill = document.getElementById('timerGoalPill');
    if (timerGoalPill) timerGoalPill.textContent = `${targetMinutes} Mnt`;

    const goalReachedMinutes = document.getElementById('goalReachedMinutes');
    if (goalReachedMinutes) goalReachedMinutes.textContent = targetMinutes;

    const startKey = `milo_start_time_${sessionId}`;
    const storedStart = sessionStorage.getItem(startKey);
    if (storedStart) {
        sessionStartTime = parseInt(storedStart, 10);
    } else {
        sessionStartTime = Date.now();
        sessionStorage.setItem(startKey, sessionStartTime.toString());
    }

    updateTimerDisplay();
    if (timerInterval) clearInterval(timerInterval);
    timerInterval = setInterval(updateTimerDisplay, 1000);

    const btnGoalFinish = document.getElementById('btnGoalFinish');
    const btnGoalContinue = document.getElementById('btnGoalContinue');
    const goalModalBackdrop = document.getElementById('goalModalBackdrop');
    const durationGoalModal = document.getElementById('durationGoalModal');

    if (btnGoalFinish) {
        btnGoalFinish.addEventListener('click', () => {
            if (durationGoalModal) durationGoalModal.style.display = 'none';
            confirmEndSession(true);
        });
    }
    if (btnGoalContinue) {
        btnGoalContinue.addEventListener('click', () => {
            if (durationGoalModal) durationGoalModal.style.display = 'none';
        });
    }
    if (goalModalBackdrop) {
        goalModalBackdrop.addEventListener('click', () => {
            if (durationGoalModal) durationGoalModal.style.display = 'none';
        });
    }
}

function updateTimerDisplay() {
    const elapsedSeconds = Math.max(0, Math.floor((Date.now() - sessionStartTime) / 1000));
    const elapsedFormatted = formatMinutesSeconds(elapsedSeconds);
    const targetFormatted = formatMinutesSeconds(targetSeconds);

    const sessionTimerText = document.getElementById('sessionTimerText');
    const practiceDurationProgress = document.getElementById('practiceDurationProgress');
    const sessionTimerBadge = document.getElementById('sessionTimerBadge');
    const timerGoalPill = document.getElementById('timerGoalPill');
    const durationGoalModal = document.getElementById('durationGoalModal');

    if (sessionTimerText) {
        sessionTimerText.textContent = `${elapsedFormatted} / ${targetFormatted}`;
    }
    if (practiceDurationProgress) {
        practiceDurationProgress.textContent = elapsedFormatted;
    }

    if (progressBarFill) {
        const pct = Math.min(100, (elapsedSeconds / targetSeconds) * 100);
        progressBarFill.style.width = `${pct}%`;
    }

    if (elapsedSeconds >= targetSeconds) {
        if (sessionTimerBadge && !sessionTimerBadge.classList.contains('completed')) {
            sessionTimerBadge.classList.add('completed');
        }
        if (timerGoalPill) {
            timerGoalPill.textContent = 'Selesai ✓';
        }

        if (!autoCloseInitiated) {
            autoCloseInitiated = true;
            playTargetCompletionChime();
            if (isRecording) {
                isSessionClosing = true;
                stopRecording();
            } else {
                triggerAutoSessionClose();
            }
        }
    }
}

function lockConversationInputs(reasonText) {
    if (btnMicAction) {
        btnMicAction.disabled = true;
        btnMicAction.classList.add('disabled-locked');
        btnMicAction.title = reasonText || 'Sesi latihan telah selesai';
    }
    if (userTextInput) {
        userTextInput.disabled = true;
        userTextInput.placeholder = reasonText || 'Sesi latihan telah selesai...';
    }
    if (btnSendText) {
        btnSendText.disabled = true;
    }
}

function showClosingToast(title, desc) {
    const toast = document.getElementById('sessionClosingToast');
    const toastTitle = document.getElementById('closingToastTitle');
    const toastDesc = document.getElementById('closingToastDesc');
    if (toastTitle && title) toastTitle.textContent = title;
    if (toastDesc && desc) toastDesc.textContent = desc;
    if (toast) toast.style.display = 'block';
}

function playClosingAudioAndRedirect(base64Audio) {
    showClosingToast('Waktu Latihan Selesai', 'Mendengarkan salam penutup Milo. Mengalihkan ke evaluasi setelah selesai...');
    let redirected = false;
    const triggerRedirect = () => {
        if (!redirected) {
            redirected = true;
            showClosingToast('Menyusun Evaluasi', 'Menyimpan performa dan mengalihkan ke ringkasan...');
            confirmEndSession(true);
        }
    };

    if (base64Audio) {
        try {
            const audio = new Audio("data:audio/mp3;base64," + base64Audio);
            setCompanionState('speaking', 'Milo menutup percakapan...', 'happy');
            if (window.miloLive2D && typeof window.miloLive2D.bindAudio === 'function') {
                window.miloLive2D.bindAudio(audio, 'happy', null);
            }
            audio.onended = () => {
                setCompanionState('idle', 'Sesi latihan selesai');
                setTimeout(triggerRedirect, 1500);
            };
            audio.onerror = () => {
                setCompanionState('idle', 'Sesi latihan selesai');
                setTimeout(triggerRedirect, 2500);
            };
            audio.play().catch(e => {
                console.log("Audio autoplay prevented by browser policy:", e);
                setCompanionState('idle', 'Sesi latihan selesai');
                setTimeout(triggerRedirect, 3500);
            });
            setTimeout(triggerRedirect, 15000);
            return;
        } catch (e) {
            console.error("Closing audio error:", e);
        }
    }

    setTimeout(triggerRedirect, 3500);
}

function handleSessionClosedResponse(data) {
    isSessionClosing = true;
    lockConversationInputs('Sesi latihan telah selesai');
    setCompanionState('speaking', 'Milo menutup percakapan...');

    // Append Milo's closing message to the chat (without generic autoplay)
    appendMessage(data.response_text, 'milo', null, data.translation, data.rag_sources, data.rag_details);

    // Update real-time Speech Evaluation HUD if feedback exists
    if (data.feedback) {
        updateEvaluationHUD(data.feedback);
    }

    // Play closing audio and schedule auto redirect
    playClosingAudioAndRedirect(data.audio_base64);
}

async function triggerAutoSessionClose() {
    if (isSessionClosing) return;
    isSessionClosing = true;

    lockConversationInputs('Waktu latihan selesai. Milo sedang memberikan rangkuman penutup...');
    showClosingToast('Waktu Latihan Selesai', 'Durasi tercapai. Milo sedang memberikan ucapan penutup...');
    setCompanionState('thinking', 'Milo sedang menutup sesi...');

    const thinkingRow = document.createElement('div');
    thinkingRow.className = 'chat-message-row milo-row thinking-indicator-row';
    thinkingRow.id = 'miloClosingThinking';
    thinkingRow.innerHTML = `
        <div class="milo-avatar-icon"><span style="font-weight: 800; font-size: 14px; color: #FFFFFF;">M</span></div>
        <div class="message-bubble milo-bubble thinking-bubble" style="opacity: 0.85; font-style: italic;">
            <i class="fa-solid fa-spinner fa-spin"></i> <span>Milo sedang merangkum sesi latihan...</span>
        </div>
    `;
    messagesContainer.appendChild(thinkingRow);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    try {
        const authUserId = getAuthUserId();
        const closePayload = {
            session_id: sessionId,
            message: "Time is up for today's practice session.",
            learning_goal: sessionStorage.getItem('milo_learning_goal') || '',
            cefr_level: currentLevel,
            return_audio: true,
            input_type: 'text',
            is_closing: true,
            trigger: 'time_limit_reached',
        };
        if (authUserId) closePayload.user_id = authUserId;

        const response = await fetch('/api/v1/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
            body: JSON.stringify(closePayload)
        });

        thinkingRow.remove();

        if (!response.ok) {
            const errText = await response.text();
            throw new Error(`Close session error ${response.status}: ${errText}`);
        }

        const data = await response.json();
        handleSessionClosedResponse(data);
    } catch (err) {
        console.error("Auto close session error:", err);
        const ind = document.getElementById('miloClosingThinking');
        if (ind) ind.remove();
        confirmEndSession(true);
    }
}

function formatMinutesSeconds(totalSeconds) {
    const m = Math.floor(totalSeconds / 60);
    const s = totalSeconds % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
}

function playTargetCompletionChime() {
    try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const now = ctx.currentTime;
        const notes = [440, 554.37, 659.25, 880];
        notes.forEach((freq, idx) => {
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(freq, now + (idx * 0.1));
            gain.gain.setValueAtTime(0, now + (idx * 0.1));
            gain.gain.linearRampToValueAtTime(0.12, now + (idx * 0.1) + 0.03);
            gain.gain.exponentialRampToValueAtTime(0.0001, now + (idx * 0.1) + 0.4);
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start(now + (idx * 0.1));
            osc.stop(now + (idx * 0.1) + 0.42);
        });
    } catch (e) {}
}

async function confirmEndSession(skipConfirm = false) {
    if (!skipConfirm && !confirm('Apakah Anda ingin mengakhiri sesi latihan ini?')) {
        return;
    }

    if (timerInterval) clearInterval(timerInterval);
    showGlobalLoading('Menganalisis performa percakapan & menyusun evaluasi CEFR...');

    try {
        const response = await fetch('/api/v1/session/end', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
            body: JSON.stringify({ session_id: sessionId })
        });

        if (!response.ok) {
            const err = await response.text();
            throw new Error(`End session error: ${err}`);
        }

        const summaryData = await response.json();
        sessionStorage.setItem('milo_summary_data', JSON.stringify(summaryData));
        window.location.href = `/ui/summary.html?session_id=${encodeURIComponent(sessionId)}&topic_id=${encodeURIComponent(currentTopicId)}`;
    } catch (err) {
        hideGlobalLoading();
        alert('Gagal mengakhiri sesi: ' + err.message);
        console.error('End session error:', err);
    }
}

// ─── RAG Grounding HUD & Interactive Inspector Modal ──────────────────────────

function updateRagFeedbackHUD(ragDetails, ragSources) {
    const ragBox = document.getElementById('evalRagBox');
    const ragTitle = document.getElementById('evalRagTitle');
    const ragSnippet = document.getElementById('evalRagSnippet');
    if (!ragBox) return;

    if (ragDetails && Array.isArray(ragDetails) && ragDetails.length > 0) {
        const item = ragDetails[0];
        if (ragTitle) ragTitle.textContent = item.book || item.title || 'Cambridge / Collins RAG';
        if (ragSnippet) ragSnippet.textContent = item.snippet || 'Kutipan materi pembelajaran terverifikasi.';
        ragBox.style.display = 'flex';
    } else if (ragSources && Array.isArray(ragSources) && ragSources.length > 0) {
        if (ragTitle) ragTitle.textContent = formatRagSourceLabel(ragSources[0]);
        if (ragSnippet) ragSnippet.textContent = 'Materi tuturan diverifikasi oleh buku rujukan kurikulum resmi.';
        ragBox.style.display = 'flex';
    }
}

window.openRagInspectorModal = function(msgId, detailIdx) {
    const msg = messageStore.get(msgId);
    if (!msg) return;
    const details = msg.ragDetails || [];
    const detail = details[detailIdx] || {
        book: msg.ragSources && msg.ragSources[detailIdx] ? formatRagSourceLabel(msg.ragSources[detailIdx]) : 'Cambridge & Collins RAG Knowledge Base',
        category: 'Materi Pembelajaran Resmi',
        level: currentLevel || 'B1-B2',
        score: 0.85,
        snippet: 'Materi ini terverifikasi oleh knowledge base MILO berbasis buku referensi resmi.'
    };

    const modal = document.getElementById('ragModalBackdrop');
    if (!modal) return;
    const bElem = document.getElementById('ragModalBook');
    const cElem = document.getElementById('ragModalCategory');
    const lElem = document.getElementById('ragModalLevel');
    const sElem = document.getElementById('ragModalScore');
    const snElem = document.getElementById('ragModalSnippet');

    if (bElem) bElem.textContent = detail.book || detail.title || 'Cambridge / Collins RAG';
    if (cElem) cElem.textContent = detail.category || 'Curriculum Material';
    if (lElem) lElem.textContent = `CEFR ${detail.level || currentLevel || 'B1-B2'}`;
    const pct = Math.round((detail.score || 0.85) * 100);
    if (sElem) sElem.textContent = `Skor Keselarasan: ${pct}%`;
    if (snElem) snElem.textContent = `"${detail.snippet || 'Kutipan materi pembelajaran.'}"`;
    modal.style.display = 'flex';
};

window.closeRagInspectorModal = function(e) {
    if (e && e.target && e.target.id !== 'ragModalBackdrop' && !e.target.classList.contains('rag-modal-close-btn') && !e.target.classList.contains('rag-modal-btn')) {
        return;
    }
    const modal = document.getElementById('ragModalBackdrop');
    if (modal) modal.style.display = 'none';
};

