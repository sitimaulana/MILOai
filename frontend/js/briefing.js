// MILO Microlearning Stepper Deck: Sasaran Belajar, Kosakata, Idiom, Studio Mic Check.

let sessionId = null;
let currentTopicId = 'A1';
let currentTopic = 'job_interview';
let currentLevel = 'B1';
let isMicValidated = false;
let audioContext = null;
let analyser = null;
let micStream = null;
let animationFrameId = null;
let isTestingMic = false;
let activeTab = 1;

// Format human-friendly topic labels (e.g. "Academic #1", "Interview #2", "Daily #3")
if (typeof formatTopicDisplay !== 'function') {
    window.formatTopicDisplay = function(topic) {
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
    };
}

document.addEventListener('DOMContentLoaded', async () => {
    if (typeof requireAuth === 'function' && !requireAuth()) {
        return;
    }

    // 1. Resolve Session ID, Topic ID, Category & Level
    const urlParams = new URLSearchParams(window.location.search);
    sessionId = urlParams.get('session_id') || sessionStorage.getItem('milo_session_id');
    currentTopicId = urlParams.get('topic_id') || sessionStorage.getItem('milo_topic_id') || 'A1';
    currentTopic = sessionStorage.getItem('milo_topic') || 'job_interview';
    currentLevel = sessionStorage.getItem('milo_cefr_level') || 'B1';

    if (!sessionId) {
        alert('Sesi latihan belum aktif. Mengalihkan ke halaman setup...');
        window.location.href = '/ui/setup.html';
        return;
    }

    // Update Header Badges
    const badgeTopicId = document.getElementById('briefingTopicIdBadge');
    const initialTopicDisplay = sessionStorage.getItem('milo_topic_label_display') || (
        typeof formatTopicDisplay === 'function'
            ? formatTopicDisplay({ topic_id: currentTopicId, track_key: currentTopic }).label
            : `Topik ${currentTopicId}`
    );
    if (badgeTopicId) badgeTopicId.textContent = initialTopicDisplay;

    const badgeLevel = document.getElementById('briefingLevelBadge');
    if (badgeLevel) badgeLevel.textContent = `Level ${currentLevel}`;

    const badgeTopic = document.getElementById('briefingTopicBadge');
    const label = sessionStorage.getItem('milo_topic_label') || (
        currentTopic === 'job_interview' ? 'Job Interview Practice' :
        currentTopic === 'academic_discussion' ? 'Academic Discussion' : 'Daily Conversation'
    );
    if (badgeTopic) badgeTopic.textContent = label;

    // 2. Tab Navigation Binding
    bindTabNavigation();

    // 3. Load Full Microlearning Module Details from API
    await loadModuleDetail(currentTopicId);

    // 4. Initialize Studio Canvas Idle Waveform
    initIdleVisualizer();

    // 5. Mic Check Actions
    const btnTestMic = document.getElementById('btnTestMic');
    if (btnTestMic) btnTestMic.addEventListener('click', toggleMicTest);

    const btnBypass = document.getElementById('btnBypassMic');
    if (btnBypass) {
        btnBypass.addEventListener('click', () => {
            validateMicSuccess(true);
        });
    }

    // 6. Start Session CTA
    const btnStart = document.getElementById('btnStartSession');
    if (btnStart) {
        btnStart.addEventListener('click', () => {
            if (!isMicValidated) {
                alert('Silakan lakukan tes mikrofon terlebih dahulu sebelum memulai sesi.');
                return;
            }
            window.location.href = `/ui/practice.html?session_id=${encodeURIComponent(sessionId)}&topic_id=${encodeURIComponent(currentTopicId)}`;
        });
    }
});

// ─── Tab Switching & Progress Logic ──────────────────────────────────────────
function bindTabNavigation() {
    const tabBtns = document.querySelectorAll('.deck-step-btn[data-tab]');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabNum = parseInt(btn.getAttribute('data-tab'), 10);
            switchTab(tabNum);
        });
    });

    // Next / Prev Actions
    const btnNextToVocab = document.getElementById('btnNextToVocab');
    if (btnNextToVocab) btnNextToVocab.addEventListener('click', () => switchTab(2));

    const btnBackToGoal = document.getElementById('btnBackToGoal');
    if (btnBackToGoal) btnBackToGoal.addEventListener('click', () => switchTab(1));

    const btnNextToIdioms = document.getElementById('btnNextToIdioms');
    if (btnNextToIdioms) btnNextToIdioms.addEventListener('click', () => switchTab(3));

    const btnBackToVocab = document.getElementById('btnBackToVocab');
    if (btnBackToVocab) btnBackToVocab.addEventListener('click', () => switchTab(2));

    const btnNextToReady = document.getElementById('btnNextToReady');
    if (btnNextToReady) btnNextToReady.addEventListener('click', () => switchTab(4));

    const btnBackToIdioms = document.getElementById('btnBackToIdioms');
    if (btnBackToIdioms) btnBackToIdioms.addEventListener('click', () => switchTab(3));
}

function switchTab(targetNum) {
    activeTab = targetNum;

    // Progress Bar Fill
    const progressFill = document.getElementById('deckProgressFill');
    if (progressFill) {
        const percentages = { 1: '25%', 2: '50%', 3: '75%', 4: '100%' };
        progressFill.style.width = percentages[targetNum] || '25%';
    }

    // Toggle Tab Panels
    for (let i = 1; i <= 4; i++) {
        const panel = document.getElementById(`tab${i}Container`);
        if (panel) panel.style.display = (i === targetNum) ? 'flex' : 'none';

        const btn = document.getElementById(`tabBtn${i}`);
        if (btn) {
            btn.classList.toggle('active', i === targetNum);
            if (i < targetNum) {
                btn.classList.add('completed');
                const numCircle = btn.querySelector('.step-num-circle');
                if (numCircle) numCircle.innerHTML = '<i class="fa-solid fa-check" style="font-size: 11px;"></i>';
            } else {
                btn.classList.remove('completed');
                const numCircle = btn.querySelector('.step-num-circle');
                if (numCircle) numCircle.textContent = i;
            }
        }
    }

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ─── Load Module Detail from Backend API ──────────────────────────────────────
async function loadModuleDetail(topicId) {
    try {
        const resp = await fetch(`/api/v1/curriculum/topic/${encodeURIComponent(topicId)}`);
        if (!resp.ok) {
            throw new Error(`Server returned ${resp.status}`);
        }

        const data = await resp.json();

        // 1. Populate Tab 1: Sasaran Belajar
        const topicDisplay = (typeof formatTopicDisplay === 'function')
            ? formatTopicDisplay(data)
            : { label: `Topik #${data.topic_number || data.topic_id}` };

        const titleEl = document.getElementById('lessonTitleText');
        if (titleEl) titleEl.textContent = `[${topicDisplay.label}] ${data.title}`;

        if (badgeTopicId) badgeTopicId.textContent = topicDisplay.label;

        const candoEl = document.getElementById('lessonCanDoText');
        if (candoEl) candoEl.textContent = data.can_do_statement;

        const briefingEl = document.getElementById('scenarioDescription');
        if (briefingEl) briefingEl.textContent = data.briefing;

        const heroTrackPill = document.getElementById('heroTrackPill');
        if (heroTrackPill) {
            heroTrackPill.innerHTML = `<i class="fa-solid fa-graduation-cap"></i> ${escapeHtml(data.track_name || 'Microlearning Topic')}`;
        }

        // Persona Roleplay Setup
        const userRoleEl = document.getElementById('roleplayUserRole');
        const userDescEl = document.getElementById('roleplayUserDesc');
        const miloRoleEl = document.getElementById('roleplayMiloRole');
        const miloDescEl = document.getElementById('roleplayMiloDesc');

        if (data.track_code === 'TRACK_A') {
            if (userRoleEl) userRoleEl.textContent = 'Job Candidate (Pelamar Kerja)';
            if (userDescEl) userDescEl.textContent = 'Menjawab pertanyaan wawancara, menguraikan kelebihan diri, dan proyek relevan.';
            if (miloRoleEl) miloRoleEl.textContent = 'Lead Hiring Manager (Pewawancara)';
            if (miloDescEl) miloDescEl.textContent = 'Pewawancara profesional yang memandu percakapan dan mengevaluasi kesiapan karir.';
        } else if (data.track_code === 'TRACK_B') {
            if (userRoleEl) userRoleEl.textContent = 'Academic Presenter (Mahasiswa Peneliti)';
            if (userDescEl) userDescEl.textContent = 'Menyampaikan argumen kritis, membandingkan data, dan mempertahankan sudut pandang.';
            if (miloRoleEl) miloRoleEl.textContent = 'Faculty Discussion Partner (Rekan Akademik)';
            if (miloDescEl) miloDescEl.textContent = 'Rekan diskusi ilmiah yang memberikan pertanyaan pendalam dan sanggahan logis.';
        } else {
            if (userRoleEl) userRoleEl.textContent = 'Casual Speaker (Teman Ngobrol)';
            if (userDescEl) userDescEl.textContent = 'Bercerita secara santai tentang hobi, liburan, dan kehidupan sehari-hari.';
            if (miloRoleEl) miloRoleEl.textContent = 'MILO (Warm Companion)';
            if (miloDescEl) miloDescEl.textContent = 'Teman bicara yang ramah, hangat, dan selalu mendukung kelancaran bahasa Inggris Anda.';
        }

        // 2. Populate Tab 2: Vocabulary Deck
        renderVocabDeck(data.vocabulary || [], 'vocabCardsDeck', false);

        // 3. Populate Tab 3: Idioms Deck
        renderVocabDeck(data.idioms || [], 'idiomsCardsDeck', true);

        // 4. Populate RAG Grounded Curriculum Source
        const ragSourceTitle = document.getElementById('briefingRagSourceTitle');
        const ragSourceDesc = document.getElementById('briefingRagSourceDesc');
        if (ragSourceTitle && ragSourceDesc) {
            if (data.track_code === 'TRACK_A') {
                ragSourceTitle.textContent = 'Collins Speaking for IELTS (Units 1-3) & Cambridge Vocabulary in Use';
                ragSourceDesc.textContent = 'Menekankan kelancaran STAR method, vocabulary profesional, dan metrik penilaian wawancara kerja B1-B2.';
            } else if (data.track_code === 'TRACK_B') {
                ragSourceTitle.textContent = 'The Cambridge Guide to English Usage & Collins Academic Discussion';
                ragSourceDesc.textContent = 'Menekankan kesantunan sanggahan ilmiah (hedging), pembeda kata baku, dan koherensi argumen logis.';
            } else {
                ragSourceTitle.textContent = 'Cambridge English Vocabulary in Use & CEFR Companion Volume';
                ragSourceDesc.textContent = 'Menekankan ekspresi percakapan kasual, kolokasi tematik, dan deskriptor kelancaran berbicara spontan.';
            }
        }

    } catch (err) {
        console.error('Failed to load module details:', err);
        const titleEl = document.getElementById('lessonTitleText');
        if (titleEl) titleEl.textContent = 'Pengenalan Skenario Latihan';

        const renderError = (containerId, typeName) => {
            const container = document.getElementById(containerId);
            if (container) {
                container.innerHTML = `
                    <div style="text-align: center; padding: 32px 20px; background: #FFF5F5; border-radius: 14px; border: 1.5px dashed #FEB2B2; color: #9B2C2C;">
                        <i class="fa-solid fa-triangle-exclamation" style="font-size: 26px; margin-bottom: 10px; color: #E53E3E;"></i>
                        <p style="font-weight: 800; font-size: 15px; margin-bottom: 4px;">Gagal memuat ${typeName}</p>
                        <p style="font-size: 13px; color: #742A2A; margin-bottom: 14px;">Terjadi kendala saat mengambil data modul dari server.</p>
                        <button type="button" onclick="loadModuleDetail('${topicId}')" class="btn-deck-nav prev" style="display: inline-flex; margin: 0 auto; padding: 8px 18px; font-size: 13px; font-weight: 700; cursor: pointer;">
                            <i class="fa-solid fa-rotate-right"></i> Coba Muat Ulang
                        </button>
                    </div>
                `;
            }
        };
        renderError('vocabCardsDeck', 'daftar kosakata inti');
        renderError('idiomsCardsDeck', 'daftar idiom & ekspresi alami');
    }
}

function renderVocabDeck(items, containerId, isIdiom = false) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '';

    if (items.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 28px; background: var(--neutral-bg); border-radius: 14px; border: 1px dashed var(--border-subtle); color: var(--text-slate);">
                <i class="fa-regular fa-bookmark" style="font-size: 24px; margin-bottom: 8px;"></i>
                <p style="font-weight: 700;">Belum ada daftar khusus untuk topik ini.</p>
            </div>
        `;
        return;
    }

    items.forEach((item, idx) => {
        const card = document.createElement('div');
        card.className = 'vocab-detail-card';

        const orderText = isIdiom ? `Idiom ${idx + 1} dari ${items.length}` : `Frasa ${idx + 1} dari ${items.length}`;
        const labelText = isIdiom ? 'Makna Kontekstual' : 'Arti Kata';

        card.innerHTML = `
            <div class="vocab-card-top-row">
                <div class="vocab-card-phrase-group">
                    <span class="vocab-order-badge">${escapeHtml(orderText)}</span>
                    <span class="vocab-card-phrase-text">${escapeHtml(item.phrase)}</span>
                </div>
                <div class="vocab-card-actions">
                    <span class="listened-indicator" id="listened_${isIdiom ? 'idiom' : 'vocab'}_${idx}">
                        <i class="fa-solid fa-circle-check"></i>
                        <span>Didengarkan</span>
                    </span>
                    <button type="button" class="btn-listen-pronounce" title="Dengarkan contoh pengucapan audio" aria-label="Dengarkan pelafalan">
                        <i class="fa-solid fa-volume-high"></i>
                        <span>Dengarkan</span>
                    </button>
                </div>
            </div>
            <div class="vocab-card-meaning-box">
                <span class="vocab-card-meaning-label">${escapeHtml(labelText)}</span>
                <span>${escapeHtml(item.meaning)}</span>
            </div>
            <div class="vocab-card-example-box">
                <span class="vocab-card-example-label"><i class="fa-solid fa-quote-left"></i> Contoh dalam Percakapan</span>
                <div>${escapeHtml(item.example || `Gunakan frasa "${item.phrase}" untuk memperkuat respons Anda saat berbicara dengan MILO.`)}</div>
            </div>
        `;

        const btnListen = card.querySelector('.btn-listen-pronounce');
        const indicator = card.querySelector('.listened-indicator');

        if (btnListen) {
            btnListen.addEventListener('click', (e) => {
                e.stopPropagation();
                pronouncePhrase(item.phrase, btnListen, indicator);
            });
        }

        container.appendChild(card);
    });
}

// ─── Speech Synthesis Pronunciation Helper ────────────────────────────────────
function pronouncePhrase(phrase, btnElement, indicatorElement) {
    const cleanText = phrase.replace(/\.{2,}/g, '').trim();

    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.lang = 'en-US';
        utterance.rate = 0.92;

        if (btnElement) {
            btnElement.classList.add('is-playing');
            btnElement.innerHTML = `<i class="fa-solid fa-waveform-lines fa-fade"></i> <span>Memutar...</span>`;
        }

        utterance.onend = () => {
            if (btnElement) {
                btnElement.classList.remove('is-playing');
                btnElement.innerHTML = `<i class="fa-solid fa-volume-high"></i> <span>Dengarkan Lagi</span>`;
            }
            if (indicatorElement) {
                indicatorElement.classList.add('visible');
            }
        };

        utterance.onerror = () => {
            if (btnElement) {
                btnElement.classList.remove('is-playing');
                btnElement.innerHTML = `<i class="fa-solid fa-volume-high"></i> <span>Dengarkan</span>`;
            }
        };

        window.speechSynthesis.speak(utterance);
        showToast(`Pelafalan: "${cleanText}"`);
    } else {
        showToast(`"${cleanText}"`);
    }
}

function showToast(message) {
    const toast = document.getElementById('audioToast');
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => {
        toast.classList.remove('show');
    }, 2400);
}

// Studio Mic Check & Equalizer Visualizer
const canvas = document.getElementById('micVisualizerCanvas');
const canvasCtx = canvas ? canvas.getContext('2d') : null;

function initIdleVisualizer() {
    if (!canvas || !canvasCtx) return;
    let step = 0;

    function renderIdle() {
        if (isTestingMic) return;

        canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
        canvasCtx.lineWidth = 2.5;
        canvasCtx.strokeStyle = isMicValidated ? '#4ADE80' : 'rgba(122, 154, 130, 0.45)';
        canvasCtx.beginPath();

        const sliceWidth = canvas.width / 40;
        let x = 0;

        for (let i = 0; i <= 40; i++) {
            const v = Math.sin((i * 0.25) + (step * 0.05)) * (isMicValidated ? 8 : 4);
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

async function toggleMicTest() {
    const btnTestMic = document.getElementById('btnTestMic');
    const micStatus = document.getElementById('micStatusBadge');
    const studioLivePill = document.getElementById('studioLivePill');
    const studioLiveStatusText = document.getElementById('studioLiveStatusText');
    const energyGaugeFill = document.getElementById('micEnergyGaugeFill');

    if (isTestingMic) {
        stopMicTest();
        return;
    }

    try {
        isTestingMic = true;
        if (btnTestMic) btnTestMic.classList.add('listening');

        if (studioLivePill) studioLivePill.classList.add('active');
        if (studioLiveStatusText) studioLiveStatusText.textContent = 'Mendengarkan Suara Real-Time...';

        if (micStatus) {
            micStatus.className = 'studio-status-box';
            micStatus.innerHTML = `<i class="fa-solid fa-spinner fa-spin" style="color: var(--secondary);"></i> <span>Mendengarkan... Silakan ucapkan kalimat panduan di atas!</span>`;
        }

        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        micStream = stream;

        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        analyser = audioContext.createAnalyser();
        analyser.fftSize = 64; // 32 frequency bins for crisp bar equalizer

        const source = audioContext.createMediaStreamSource(stream);
        source.connect(analyser);

        const dataArray = new Uint8Array(analyser.frequencyBinCount);
        let audioSamplesCount = 0;
        let speechEnergySum = 0;

        function checkLevel() {
            if (!isTestingMic) return;

            analyser.getByteFrequencyData(dataArray);

            // Draw 32-Bar Frequency Equalizer
            if (canvas && canvasCtx) {
                canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
                const barCount = 32;
                const barWidth = (canvas.width / barCount) - 3;
                let x = 2;

                for (let i = 0; i < barCount; i++) {
                    const barHeight = Math.max(4, (dataArray[i] / 255) * (canvas.height - 12));

                    // Dynamic bar gradient from mint green to sage to warm amber
                    const grad = canvasCtx.createLinearGradient(0, canvas.height - barHeight, 0, canvas.height);
                    grad.addColorStop(0, '#86EFAC');
                    grad.addColorStop(0.6, '#7A9A82');
                    grad.addColorStop(1, '#D97706');

                    canvasCtx.fillStyle = grad;
                    canvasCtx.beginPath();
                    canvasCtx.roundRect(x, canvas.height - barHeight, barWidth, barHeight, [3, 3, 0, 0]);
                    canvasCtx.fill();

                    x += barWidth + 3;
                }
            }

            // Energy meter update
            let sum = 0;
            for (let i = 0; i < dataArray.length; i++) {
                sum += dataArray[i];
            }
            const average = sum / dataArray.length;

            if (energyGaugeFill) {
                const percent = Math.min(100, Math.round((average / 140) * 100));
                energyGaugeFill.style.width = `${percent}%`;
            }

            if (average > 14) {
                speechEnergySum += average;
                audioSamplesCount++;
            }

            if (audioSamplesCount >= 18 && speechEnergySum > 280) {
                validateMicSuccess(false);
                return;
            }

            animationFrameId = requestAnimationFrame(checkLevel);
        }

        checkLevel();

        // 8-second safety timeout
        setTimeout(() => {
            if (isTestingMic && !isMicValidated) {
                stopMicTest();
                if (micStatus) {
                    micStatus.className = 'studio-status-box';
                    micStatus.innerHTML = `<i class="fa-solid fa-circle-exclamation" style="color: #F59E0B;"></i> <span>Suara belum terdeteksi jelas. Coba bersuara lebih dekat ke mic dan tekan uji lagi.</span>`;
                }
            }
        }, 8000);

    } catch (err) {
        console.error('Mic check error:', err);
        stopMicTest();
        if (micStatus) {
            micStatus.className = 'studio-status-box';
            micStatus.innerHTML = `<i class="fa-solid fa-triangle-exclamation" style="color: #EF4444;"></i> <span>Akses mic tidak tersedia: ${escapeHtml(err.message)}</span>`;
        }
    }
}

function stopMicTest() {
    isTestingMic = false;
    const btnTestMic = document.getElementById('btnTestMic');
    if (btnTestMic) btnTestMic.classList.remove('listening');

    const studioLivePill = document.getElementById('studioLivePill');
    if (studioLivePill) studioLivePill.classList.remove('active');

    const studioLiveStatusText = document.getElementById('studioLiveStatusText');
    if (studioLiveStatusText && !isMicValidated) {
        studioLiveStatusText.textContent = 'Standby Audio Check';
    }

    const energyGaugeFill = document.getElementById('micEnergyGaugeFill');
    if (energyGaugeFill && !isMicValidated) {
        energyGaugeFill.style.width = '0%';
    }

    if (animationFrameId) cancelAnimationFrame(animationFrameId);

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

function validateMicSuccess(bypassed = false) {
    isMicValidated = true;
    stopMicTest();

    const studioLivePill = document.getElementById('studioLivePill');
    const studioLiveStatusText = document.getElementById('studioLiveStatusText');
    const micStatus = document.getElementById('micStatusBadge');
    const btnStart = document.getElementById('btnStartSession');
    const energyGaugeFill = document.getElementById('micEnergyGaugeFill');

    if (studioLivePill) studioLivePill.classList.add('active');
    if (studioLiveStatusText) studioLiveStatusText.textContent = 'Mikrofon Siap & Optimal';

    if (energyGaugeFill) energyGaugeFill.style.width = '75%';

    if (micStatus) {
        micStatus.className = 'studio-status-box success';
        micStatus.innerHTML = `<i class="fa-solid fa-circle-check" style="color: #4ADE80; font-size: 16px;"></i> <span><strong>Mikrofon Berhasil Divalidasi!</strong> ${bypassed ? 'Kesiapan mikrofon dikonfirmasi.' : 'Suaramu terdengar sangat jernih.'}</span>`;
    }

    if (btnStart) {
        btnStart.removeAttribute('disabled');
    }

    showToast('Mikrofon siap! Anda dapat memulai percakapan.');
}
