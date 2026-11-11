// ═══════════════════════════════════════════════════════════════════════════════
// MILO AI English Tutor: Pre-Session Briefing ("Jaring Pengaman" Logic)
// Scenario Context + Playful Cyan Target Vocabulary + Interactive Mic Check
// ═══════════════════════════════════════════════════════════════════════════════

const VOCAB_DATABASE = {
    job_interview: {
        B1: [
            "I have experience in...",
            "My key strengths include...",
            "In my previous role...",
            "Problem-solving skills",
            "Team collaboration",
            "I am passionate about...",
            "Handling tight deadlines",
            "Career development"
        ],
        B2: [
            "To spearhead innovative projects...",
            "Demonstrated proficiency in...",
            "Overcoming unforeseen obstacles...",
            "Strategic decision-making",
            "Proven track record of success",
            "Thriving in fast-paced environments",
            "Cross-functional leadership",
            "Optimizing team workflows"
        ]
    },
    academic_discussion: {
        B1: [
            "In my opinion,...",
            "According to recent studies,...",
            "One major advantage is...",
            "On the other hand,...",
            "Evidence suggests that...",
            "Critical thinking",
            "From my perspective,...",
            "A significant factor is..."
        ],
        B2: [
            "From an empirical standpoint,...",
            "A compelling counterargument is...",
            "Significant correlation between...",
            "Theoretical implications",
            "Challenging conventional wisdom",
            "Paradigm shift in research",
            "Qualitative and quantitative data",
            "Substantiating the hypothesis"
        ]
    },
    daily_conversation: {
        B1: [
            "To be honest,...",
            "I really enjoy spending time...",
            "As far as I know,...",
            "Speaking of which,...",
            "Catch up with friends",
            "Unwind after a busy day",
            "A habit of mine is...",
            "Looking forward to..."
        ],
        B2: [
            "Frankly speaking,...",
            "It totally resonated with me because...",
            "Off the top of my head,...",
            "Every once in a while,...",
            "Broaden my horizons",
            "Striking a healthy balance",
            "Spontaneous adventure",
            "Navigating everyday challenges"
        ]
    }
};

const SCENARIOS = {
    job_interview: {
        tag: "Roleplay: Job Candidate & Hiring Manager",
        desc: "Kamu berperan sebagai kandidat pelamar kerja yang sedang menjalani sesi wawancara profesional bersama MILO (Hiring Manager). Ceritakan latar belakang, pencapaian kerja, serta keahlian terbaikmu dengan terstruktur dan percaya diri."
    },
    academic_discussion: {
        tag: "Roleplay: Academic Scholar & Discussion Partner",
        desc: "Kamu berperan sebagai mahasiswa / peneliti yang mendiskusikan topik sains, teknologi, atau isu kontemporer bersama MILO. Gunakan penalaran logis, sampaikan argumen terstruktur, dan kemukakan pandangan kritismu."
    },
    daily_conversation: {
        tag: "Roleplay: Friendly Casual Chat",
        desc: "Kamu sedang mengobrol santai layaknya teman akrab bersama MILO. Ceritakan tentang aktivitas harianmu, hobi seru, rencana akhir pekan, atau pengalaman menarik akhir-akhir ini tanpa beban."
    }
};

// ─── State Variables ─────────────────────────────────────────────────────────
let sessionId = null;
let currentTopic = 'job_interview';
let currentLevel = 'B1';
let isMicValidated = false;
let audioContext = null;
let analyser = null;
let micStream = null;
let animationFrameId = null;
let isTestingMic = false;

document.addEventListener('DOMContentLoaded', () => {
    // 1. Resolve Session State
    const urlParams = new URLSearchParams(window.location.search);
    sessionId = urlParams.get('session_id') || sessionStorage.getItem('milo_session_id');

    if (!sessionId) {
        alert('Tidak ada sesi latihan aktif. Mengalihkan ke pemilihan level...');
        window.location.href = '/ui/setup.html';
        return;
    }

    currentTopic = sessionStorage.getItem('milo_topic') || 'job_interview';
    currentLevel = sessionStorage.getItem('milo_cefr_level') || 'B1';
    const topicLabel = sessionStorage.getItem('milo_topic_label') || 'Job Interview Practice';

    // 2. Update Header Badges
    const levelBadge = document.getElementById('briefingLevelBadge');
    if (levelBadge) levelBadge.textContent = `Level ${currentLevel}`;

    const topicBadge = document.getElementById('briefingTopicBadge');
    if (topicBadge) topicBadge.textContent = topicLabel;

    // 3. Populate Scenario Context
    const scenarioData = SCENARIOS[currentTopic] || SCENARIOS.job_interview;
    const roleplayTag = document.getElementById('scenarioRoleplayTag');
    if (roleplayTag) roleplayTag.textContent = scenarioData.tag;

    const scenarioDesc = document.getElementById('scenarioDescription');
    if (scenarioDesc) scenarioDesc.textContent = scenarioData.desc;

    // 4. Populate Target Vocabulary Chips (Playful Cyan)
    const chipsContainer = document.getElementById('vocabChipsContainer');
    const topicVocabList = VOCAB_DATABASE[currentTopic] || VOCAB_DATABASE.job_interview;
    const vocabList = topicVocabList[currentLevel] || topicVocabList.B1;

    if (chipsContainer) {
        chipsContainer.innerHTML = '';
        vocabList.forEach(phrase => {
            const chip = document.createElement('div');
            chip.className = 'vocab-chip';
            chip.innerHTML = `<span>${phrase}</span> <i class="fa-solid fa-volume-high"></i>`;
            chip.title = `Klik untuk mendengarkan pelafalan "${phrase}"`;

            // Pronounce phrase on click using SpeechSynthesis
            chip.addEventListener('click', () => {
                pronouncePhrase(phrase);
            });

            chipsContainer.appendChild(chip);
        });
    }

    // 5. Initialize Canvas Idle Waveform
    initIdleVisualizer();

    // 6. Mic Check Handling
    const btnTestMic = document.getElementById('btnTestMic');
    if (btnTestMic) {
        btnTestMic.addEventListener('click', toggleMicTest);
    }

    // 7. Start Session CTA
    const btnStartSession = document.getElementById('btnStartSession');
    if (btnStartSession) {
        btnStartSession.addEventListener('click', () => {
            if (!isMicValidated) {
                alert('Silakan lakukan tes mikrofon terlebih dahulu sebelum memulai sesi.');
                return;
            }
            // Navigate to practice room
            window.location.href = `/ui/practice.html?session_id=${encodeURIComponent(sessionId)}`;
        });
    }
});

// ─── Phrase Pronunciation Helper ─────────────────────────────────────────────
function pronouncePhrase(phrase) {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(phrase);
        utterance.lang = 'en-US';
        utterance.rate = 0.95;
        window.speechSynthesis.speak(utterance);
        showToast(`🔊 Pelafalan: "${phrase}"`);
    } else {
        showToast(`"${phrase}"`);
    }
}

function showToast(message) {
    const toast = document.getElementById('audioToast');
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => {
        toast.classList.remove('show');
    }, 2200);
}

// ─── Visualizer Canvas Setup ──────────────────────────────────────────────────
const canvas = document.getElementById('micVisualizerCanvas');
const canvasCtx = canvas ? canvas.getContext('2d') : null;

function initIdleVisualizer() {
    if (!canvas || !canvasCtx) return;
    let step = 0;

    function renderIdle() {
        if (isTestingMic) return; // Switch to live audio stream

        canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
        canvasCtx.lineWidth = 2.5;
        canvasCtx.strokeStyle = isMicValidated ? '#7A9A82' : '#CBD5CD';
        canvasCtx.beginPath();

        const sliceWidth = canvas.width / 50;
        let x = 0;

        for (let i = 0; i <= 50; i++) {
            const v = Math.sin((i * 0.2) + (step * 0.05)) * (isMicValidated ? 6 : 3);
            const y = (canvas.height / 2) + v;

            if (i === 0) canvasCtx.moveTo(x, y);
            else canvasCtx.lineTo(x, y);

            x += sliceWidth;
        }

        canvasCtx.stroke();
        step++;
        animationFrameId = requestAnimationFrame(renderIdle);
    }

    renderIdle();
}

// ─── Interactive Mic Check & Stream Processing ────────────────────────────────
async function toggleMicTest() {
    const btnTestMic = document.getElementById('btnTestMic');
    const micStatus = document.getElementById('micStatusBadge');
    const micCard = document.getElementById('micCheckCard');

    if (isTestingMic) {
        stopMicTest();
        return;
    }

    try {
        isTestingMic = true;
        btnTestMic.classList.add('listening');
        micStatus.className = 'mic-status-badge';
        micStatus.innerHTML = `<i class="fa-solid fa-spinner fa-spin" style="color: var(--secondary);"></i> Mendengarkan suara... Ucapkan: <em>"Hello MILO, I am ready"</em>`;

        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        micStream = stream;

        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        analyser = audioContext.createAnalyser();
        analyser.fftSize = 256;

        const source = audioContext.createMediaStreamSource(stream);
        source.connect(analyser);

        const dataArray = new Uint8Array(analyser.frequencyBinCount);
        let consecutiveVoiceFrames = 0;
        const requiredVoiceFrames = 18; // ~1.5 seconds of vocal input

        function drawLiveWave() {
            if (!isTestingMic) return;

            analyser.getByteFrequencyData(dataArray);

            // Compute average volume level
            let sum = 0;
            for (let i = 0; i < dataArray.length; i++) {
                sum += dataArray[i];
            }
            const avgVolume = sum / dataArray.length;

            // Draw dynamic frequency waveform
            canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
            canvasCtx.lineWidth = 3;
            canvasCtx.strokeStyle = '#8C6239';
            canvasCtx.beginPath();

            const sliceWidth = canvas.width / dataArray.length;
            let x = 0;

            for (let i = 0; i < dataArray.length; i++) {
                const normalized = dataArray[i] / 255.0;
                const amplitude = (normalized * canvas.height * 0.7);
                const y = (canvas.height / 2) + ((i % 2 === 0 ? 1 : -1) * amplitude);

                if (i === 0) canvasCtx.moveTo(x, y);
                else canvasCtx.lineTo(x, y);

                x += sliceWidth;
            }

            canvasCtx.stroke();

            // Detect vocal speech above ambient threshold
            if (avgVolume > 14) {
                consecutiveVoiceFrames++;
            }

            if (consecutiveVoiceFrames >= requiredVoiceFrames) {
                // Success! Microphone validated
                validateMicSuccess();
                return;
            }

            requestAnimationFrame(drawLiveWave);
        }

        drawLiveWave();

        // Safety timeout: if after 7 seconds nothing heard, prompt gently
        setTimeout(() => {
            if (isTestingMic && !isMicValidated) {
                micStatus.innerHTML = `<i class="fa-solid fa-triangle-exclamation" style="color: #F59E0B;"></i> Belum ada suara terdeteksi. Silakan bicara lebih dekat ke mikrofon dan coba lagi.`;
                stopMicTest();
            }
        }, 8000);

    } catch (err) {
        console.error('Mic access error:', err);
        isTestingMic = false;
        btnTestMic.classList.remove('listening');
        micStatus.innerHTML = `<i class="fa-solid fa-circle-xmark" style="color: #EF4444;"></i> Akses mikrofon ditolak. Izinkan izin mikrofon di browser untuk melanjutkan.`;
        alert('Mohon izinkan akses mikrofon di browser untuk menguji suara.');
    }
}

function stopMicTest() {
    isTestingMic = false;
    const btnTestMic = document.getElementById('btnTestMic');
    if (btnTestMic) btnTestMic.classList.remove('listening');

    if (micStream) {
        micStream.getTracks().forEach(track => track.stop());
        micStream = null;
    }
    if (audioContext && audioContext.state !== 'closed') {
        audioContext.close();
        audioContext = null;
    }

    initIdleVisualizer();
}

function validateMicSuccess() {
    isMicValidated = true;
    stopMicTest();

    const micCard = document.getElementById('micCheckCard');
    const micStatus = document.getElementById('micStatusBadge');
    const btnStart = document.getElementById('btnStartSession');
    const shelfNote = document.getElementById('shelfReminderNote');

    if (micCard) micCard.classList.add('tested');

    if (micStatus) {
        micStatus.className = 'mic-status-badge success';
        micStatus.innerHTML = `<i class="fa-solid fa-circle-check" style="color: #7A9A82; font-size: 15px;"></i> <strong>Mikrofon Berhasil Tervalidasi!</strong> Suaramu terdengar jernih.`;
    }

    // Unlock Start Session CTA
    if (btnStart) {
        btnStart.removeAttribute('disabled');
        btnStart.innerHTML = `<span>Mulai Sesi Percakapan</span>`;
    }

    if (shelfNote) {
        shelfNote.innerHTML = `<span style="color: #24472F; font-weight: 700;">Mic Check berhasil! Kamu siap berbicara bersama MILO.</span>`;
    }

    // Play subtle pleasant chime
    playSuccessChime();
    showToast('Mikrofon siap digunakan!');
}

function playSuccessChime() {
    try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const now = ctx.currentTime;
        const notes = [523.25, 659.25, 783.99]; // C5, E5, G5 major triad

        notes.forEach((freq, idx) => {
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();

            osc.type = 'sine';
            osc.frequency.setValueAtTime(freq, now + (idx * 0.08));

            gain.gain.setValueAtTime(0, now + (idx * 0.08));
            gain.gain.linearRampToValueAtTime(0.12, now + (idx * 0.08) + 0.02);
            gain.gain.exponentialRampToValueAtTime(0.0001, now + (idx * 0.08) + 0.35);

            osc.connect(gain);
            gain.connect(ctx.destination);

            osc.start(now + (idx * 0.08));
            osc.stop(now + (idx * 0.08) + 0.36);
        });
    } catch (e) {
        // AudioContext chime fallback (non-blocking)
    }
}
