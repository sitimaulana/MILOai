// MILO Microlearning Stepper Deck: Sasaran Belajar, Kosakata, Idiom, Studio Mic Check.
// Faithful implementation of Figma Node 2431-32918

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
let currentModuleData = null;

// Flashcard & Master-Detail state
let vocabIndex = 0;
let idiomIndex = 0;
let vocabList = [];
let idiomList = [];
const vocabUnderstood = new Set();
const idiomUnderstood = new Set();

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
    if (window.lucide && typeof window.lucide.createIcons === 'function') {
        window.lucide.createIcons();
    }

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

    // Initialize bottom shelf controls for Step 1
    updateShelfControls(1);
});

// ─── Tab Switching & Stepper Logic ───────────────────────────────────────────
function bindTabNavigation() {
    const tabBtns = document.querySelectorAll('.briefing-step-pill[data-tab]');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabNum = parseInt(btn.getAttribute('data-tab'), 10);
            switchTab(tabNum);
        });
    });
}

function switchTab(targetNum) {
    activeTab = targetNum;

    // Toggle Tab Panels & Stepper Pills
    for (let i = 1; i <= 4; i++) {
        const panel = document.getElementById(`tab${i}Container`);
        if (panel) {
            panel.style.display = (i === targetNum) ? 'block' : 'none';
        }

        const btn = document.getElementById(`tabBtn${i}`);
        if (btn) {
            btn.classList.toggle('active', i === targetNum);
            const numCircle = btn.querySelector('.step-num-circle');
            if (i < targetNum) {
                btn.classList.add('completed');
                if (numCircle) numCircle.innerHTML = '<i class="fa-solid fa-check" style="font-size: 11px;"></i>';
            } else {
                btn.classList.remove('completed');
                if (numCircle) numCircle.textContent = i;
            }
        }
    }

    // Update bottom shelf controls matching current step
    updateShelfControls(targetNum);

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ─── Shelf / Dock Controls Dynamic Renderer ─────────────────────────────────
function updateShelfControls(tabNum) {
    const shelfWrap = document.getElementById('shelfControlsWrap');
    if (!shelfWrap) return;

    if (tabNum === 1) {
        shelfWrap.innerHTML = `
            <button type="button" class="btn-cta-secondary" id="shelfBackToSetup">
                <i class="fa-solid fa-arrow-left"></i>
                <span>Kembali ke kategori</span>
            </button>
            <button type="button" class="btn-cta-next" id="shelfNextBtn">
                <span>Pelajari Kosakata Baru</span>
                <i class="fa-solid fa-arrow-right"></i>
            </button>
        `;
        const backBtn = document.getElementById('shelfBackToSetup');
        if (backBtn) {
            backBtn.addEventListener('click', () => {
                window.location.href = 'setup.html';
            });
        }
        const nextBtn = document.getElementById('shelfNextBtn');
        if (nextBtn) nextBtn.addEventListener('click', () => switchTab(2));
    } else if (tabNum === 2) {
        shelfWrap.innerHTML = `
            <button type="button" class="btn-cta-secondary" id="shelfBackBtn">
                <i class="fa-solid fa-arrow-left"></i>
                <span>Kembali ke Sasaran</span>
            </button>
            <button type="button" class="btn-cta-next" id="shelfNextBtn">
                <span>Pelajari Idiom</span>
                <i class="fa-solid fa-arrow-right"></i>
            </button>
        `;
        const backBtn = document.getElementById('shelfBackBtn');
        if (backBtn) backBtn.addEventListener('click', () => switchTab(1));
        const nextBtn = document.getElementById('shelfNextBtn');
        if (nextBtn) nextBtn.addEventListener('click', () => switchTab(3));
    } else if (tabNum === 3) {
        shelfWrap.innerHTML = `
            <button type="button" class="btn-cta-secondary" id="shelfBackBtn">
                <i class="fa-solid fa-arrow-left"></i>
                <span>Kembali ke Kosakata</span>
            </button>
            <button type="button" class="btn-cta-next" id="shelfNextBtn">
                <span>Uji Kesiapan Bicara</span>
                <i class="fa-solid fa-arrow-right"></i>
            </button>
        `;
        const backBtn = document.getElementById('shelfBackBtn');
        if (backBtn) backBtn.addEventListener('click', () => switchTab(2));
        const nextBtn = document.getElementById('shelfNextBtn');
        if (nextBtn) nextBtn.addEventListener('click', () => switchTab(4));
    } else if (tabNum === 4) {
        shelfWrap.innerHTML = `
            <button type="button" class="btn-cta-secondary" id="shelfBackBtn">
                <i class="fa-solid fa-arrow-left"></i>
                <span>Kembali ke Idiom</span>
            </button>
            <button type="button" class="btn-cta-next" id="shelfStartBtn" ${isMicValidated ? '' : 'disabled'}>
                <span>Mulai Percakapan dengan MILO</span>
                <i class="fa-solid fa-arrow-right"></i>
            </button>
        `;
        const backBtn = document.getElementById('shelfBackBtn');
        if (backBtn) backBtn.addEventListener('click', () => switchTab(3));
        const startBtn = document.getElementById('shelfStartBtn');
        if (startBtn) {
            startBtn.addEventListener('click', () => {
                if (!isMicValidated) {
                    alert('Silakan lakukan tes mikrofon terlebih dahulu sebelum memulai sesi.');
                    return;
                }
                window.location.href = `/ui/practice.html?session_id=${encodeURIComponent(sessionId)}&topic_id=${encodeURIComponent(currentTopicId)}`;
            });
        }
    }
}

// ─── Load Module Detail from Backend API ──────────────────────────────────────
async function loadModuleDetail(topicId) {
    const normTopicId = (topicId || 'A1').toUpperCase();
    let data = null;

    // 1. Try fetching from Backend API
    try {
        const apiUrl = `/api/v1/curriculum/topic/${encodeURIComponent(normTopicId)}`;
        let resp = null;
        try {
            resp = await fetch(apiUrl);
        } catch (fetchErr) {
            if (window.location.port && window.location.port !== '8000') {
                try {
                    resp = await fetch(`http://localhost:8000${apiUrl}`);
                } catch (e2) {}
            }
        }

        if (resp && resp.ok) {
            data = await resp.json();
        }
    } catch (err) {
        console.warn('API fetch for topic details failed, checking fallback:', err);
    }

    // 2. Fallback to local curriculum data if API unavailable
    if (!data && window.MILO_CURRICULUM_DATA) {
        data = window.MILO_CURRICULUM_DATA[normTopicId] || window.MILO_CURRICULUM_DATA['A1'];
    }

    if (!data) {
        console.error('No module data available for topic:', normTopicId);
        const titleEl = document.getElementById('lessonTitleText');
        if (titleEl) titleEl.textContent = 'Pengenalan Skenario Latihan';
        return;
    }

    currentModuleData = data;

    try {
        // 1. Populate Tab 1: Sasaran Belajar
        const topicDisplay = (typeof formatTopicDisplay === 'function')
            ? formatTopicDisplay(data)
            : { label: `Topik #${data.topic_number || data.topic_id}` };

        const titleEl = document.getElementById('lessonTitleText');
        if (titleEl) titleEl.textContent = `[${topicDisplay.label}] ${data.title}`;

        const candoEl = document.getElementById('lessonCanDoText');
        if (candoEl) candoEl.textContent = data.can_do_statement;

        const heroTrackPill = document.getElementById('heroTrackPill');
        if (heroTrackPill) {
            heroTrackPill.textContent = (data.track_name || 'JOB INTERVIEW PRACTICE').toUpperCase();
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

        // 2. Set vocabulary & idiom lists
        vocabList = Array.isArray(data.vocabulary) ? data.vocabulary : [];
        idiomList = Array.isArray(data.idioms) ? data.idioms : [];
        vocabIndex = 0;
        idiomIndex = 0;

        // 3. Render Content (Vocab Flashcard & Idioms Master-Detail)
        renderFlashcard('vocab');
        renderIdiomsMasterDetail(data);

    } catch (err) {
        console.error('Failed to populate module details:', err);
    }
}

// ─── Single-Card Interactive Flashcard Carousel for Step 2 (Kosakata Inti) ───
function renderFlashcard(type) {
    const isIdiom = (type === 'idiom');
    const containerId = isIdiom ? 'idiomFlashcardContainer' : 'vocabFlashcardContainer';
    const container = document.getElementById(containerId);
    if (!container) return;

    const list = isIdiom ? idiomList : vocabList;
    let index = isIdiom ? idiomIndex : vocabIndex;
    const understoodSet = isIdiom ? idiomUnderstood : vocabUnderstood;
    const typeLabel = isIdiom ? 'IDIOM' : 'FRASA';

    if (!list || list.length === 0) {
        container.innerHTML = `
            <div class="briefing-flashcard" style="text-align: center; padding: 48px 24px;">
                <p style="font-weight: 700; color: #64748B;">Belum ada daftar ${isIdiom ? 'idiom' : 'kosakata'} untuk topik ini.</p>
            </div>
        `;
        return;
    }

    // Clamp index
    if (index < 0) index = 0;
    if (index >= list.length) index = list.length - 1;
    if (isIdiom) idiomIndex = index;
    else vocabIndex = index;

    const item = list[index];
    const isUnderstood = understoodSet.has(index);

    // Build dots HTML
    let dotsHtml = '';
    for (let i = 0; i < list.length; i++) {
        const isActive = (i === index);
        const isCompleted = understoodSet.has(i);
        let dotClasses = 'flashcard-dot';
        if (isActive) dotClasses += ' active';
        if (isCompleted) dotClasses += ' completed';
        dotsHtml += `<button type="button" class="${dotClasses}" data-target-idx="${i}" aria-label="Buka kartu ${i + 1}">${i + 1}</button>`;
    }

    container.innerHTML = `
        <div class="briefing-flashcard">
            <!-- Top Row: Counter and Dots -->
            <div class="flashcard-top-row">
                <span class="flashcard-counter-label">${escapeHtml(typeLabel)} ${index + 1} DARI ${list.length}</span>
                <div class="flashcard-dots-row">
                    ${dotsHtml}
                </div>
            </div>

            <!-- Phrase & Meaning Row with Action Buttons -->
            <div class="flashcard-phrase-row">
                <div class="flashcard-phrase-info">
                    <h2 class="flashcard-phrase-title">${escapeHtml(item.phrase || '')}</h2>
                    <p class="flashcard-phrase-meaning">${escapeHtml(item.meaning || '')}</p>
                </div>
                <div class="flashcard-phrase-actions">
                    <button type="button" class="btn-flashcard-audio" id="btnAudio_${type}" title="Dengarkan pengucapan audio" aria-label="Dengarkan pelafalan">
                        <i class="fa-solid fa-volume-high"></i>
                        <span>Dengarkan</span>
                    </button>
                    <button type="button" class="btn-flashcard-check ${isUnderstood ? 'checked' : ''}" id="btnCheck_${type}" title="Tandai pemahaman frasa ini" aria-label="Tandai paham">
                        <i class="fa-solid fa-check"></i>
                        <span>${isUnderstood ? 'Sudah Paham' : 'Tandai Paham'}</span>
                    </button>
                </div>
            </div>

            <!-- Example Box -->
            <div class="flashcard-example-box">
                <span class="example-box-label">CONTOH DALAM PERCAKAPAN</span>
                <p class="example-box-quote">"${escapeHtml(item.example || `Use "${item.phrase}" when practicing with MILO.`)}"</p>
            </div>

            <!-- In-Card Navigation Controls -->
            <div class="flashcard-nav-row">
                <button type="button" class="btn-card-nav" id="btnPrevCard_${type}" ${index === 0 ? 'disabled' : ''}>
                    <i class="fa-solid fa-chevron-left"></i>
                    <span>Kartu Sebelumnya</span>
                </button>
                <button type="button" class="btn-card-nav" id="btnNextCard_${type}" ${index === list.length - 1 ? 'disabled' : ''}>
                    <span>Kartu Berikutnya</span>
                    <i class="fa-solid fa-chevron-right"></i>
                </button>
            </div>
        </div>
    `;

    // Bind In-Card Navigation
    const prevBtn = document.getElementById(`btnPrevCard_${type}`);
    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            if (index > 0) {
                if (isIdiom) idiomIndex--;
                else vocabIndex--;
                renderFlashcard(type);
            }
        });
    }

    const nextBtn = document.getElementById(`btnNextCard_${type}`);
    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            if (index < list.length - 1) {
                if (isIdiom) idiomIndex++;
                else vocabIndex++;
                renderFlashcard(type);
            }
        });
    }

    // Bind Dots
    const dotBtns = container.querySelectorAll('.flashcard-dot[data-target-idx]');
    dotBtns.forEach(dot => {
        dot.addEventListener('click', () => {
            const targetIdx = parseInt(dot.getAttribute('data-target-idx'), 10);
            if (!isNaN(targetIdx)) {
                if (isIdiom) idiomIndex = targetIdx;
                else vocabIndex = targetIdx;
                renderFlashcard(type);
            }
        });
    });

    // Bind Audio Button
    const audioBtn = document.getElementById(`btnAudio_${type}`);
    if (audioBtn) {
        audioBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            pronouncePhrase(item.phrase || '', audioBtn);
        });
    }

    // Bind Check / Tandai Paham Button
    const checkBtn = document.getElementById(`btnCheck_${type}`);
    if (checkBtn) {
        checkBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            if (understoodSet.has(index)) {
                understoodSet.delete(index);
                checkBtn.classList.remove('checked');
                checkBtn.querySelector('span').textContent = 'Tandai Paham';
            } else {
                understoodSet.add(index);
                checkBtn.classList.add('checked');
                checkBtn.querySelector('span').textContent = 'Sudah Paham';
                showToast(`Bagus! "${item.phrase}" ditandai paham.`);
            }

            const activeDot = container.querySelector(`.flashcard-dot[data-target-idx="${index}"]`);
            if (activeDot) {
                activeDot.classList.toggle('completed', understoodSet.has(index));
            }
        });
    }
}

// ─── 2-Column Master-Detail Layout for Idioms (Figma Node 2431-32918) ────────
function renderIdiomsMasterDetail(data) {
    const listContainer = document.getElementById('idiomsPillList');
    const detailContainer = document.getElementById('idiomDetailContainer');
    if (!listContainer || !detailContainer) return;

    if (!idiomList || idiomList.length === 0) {
        listContainer.innerHTML = `<p style="color: #64748B; font-weight: 600;">Belum ada daftar idiom untuk topik ini.</p>`;
        detailContainer.innerHTML = '';
        return;
    }

    // Clamp index
    if (idiomIndex < 0) idiomIndex = 0;
    if (idiomIndex >= idiomList.length) idiomIndex = idiomList.length - 1;

    // 1. Render Left Pill List
    listContainer.innerHTML = idiomList.map((item, idx) => {
        const isActive = (idx === idiomIndex);
        const isUnderstood = idiomUnderstood.has(idx);
        const numStr = String(idx + 1).padStart(2, '0');

        return `
            <button type="button" class="idiom-list-item ${isActive ? 'active' : ''} ${isUnderstood ? 'understood' : ''}" data-idx="${idx}" aria-label="Lihat idiom ${idx + 1}">
                <div class="idiom-item-left">
                    <span class="idiom-item-badge">${numStr}</span>
                    <span class="idiom-item-text" title="${escapeHtml(item.phrase || '')}">${escapeHtml(item.phrase || '')}</span>
                </div>
                <div class="idiom-item-icon">
                    ${isActive ? '<i class="fa-solid fa-arrow-right"></i>' : '<i class="fa-solid fa-chevron-right"></i>'}
                </div>
            </button>
        `;
    }).join('');

    // Bind clicks on list items
    const itemBtns = listContainer.querySelectorAll('.idiom-list-item');
    itemBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const idx = parseInt(btn.getAttribute('data-idx'), 10);
            if (!isNaN(idx) && idx !== idiomIndex) {
                idiomIndex = idx;
                renderIdiomsMasterDetail(data || currentModuleData);
            }
        });
    });

    // 2. Render Right Detail Card
    const curr = idiomList[idiomIndex];
    const isUnderstood = idiomUnderstood.has(idiomIndex);
    const dialogue = getIdiomDialogue(curr, idiomIndex, data || currentModuleData);

    detailContainer.innerHTML = `
        <div class="idiom-detail-card">
            <!-- Top Row: Title & Audio Button -->
            <div class="idiom-detail-header">
                <h3 class="idiom-detail-title">${escapeHtml(curr.phrase || '')}</h3>
                <button type="button" class="btn-idiom-audio" id="btnIdiomAudio" title="Dengarkan pengucapan audio" aria-label="Dengarkan">
                    <i class="fa-solid fa-volume-high"></i>
                    <span>Dengarkan</span>
                </button>
            </div>

            <!-- Makna Kontekstual -->
            <div class="idiom-meaning-block">
                <span class="idiom-badge-meaning">MAKNA KONTEKSTUAL</span>
                <p class="idiom-detail-meaning">${escapeHtml(curr.meaning || '')}</p>
            </div>

            <!-- Dialogue Simulation Box -->
            <div class="idiom-dialogue-box">
                <span class="dialogue-box-label">SIMULASI DIALOG SINGKAT</span>
                <div class="dialogue-line dialogue-milo">
                    <strong>MILO:</strong> "${escapeHtml(dialogue.milo)}"
                </div>
                <div class="dialogue-line dialogue-user">
                    <strong>Kamu:</strong> "${escapeHtml(dialogue.user)}"
                </div>
            </div>

            <!-- Bottom Action Row -->
            <div class="idiom-detail-footer">
                <span class="idiom-footer-hint">Coba ucapkan kalimat di atas dengan luwes!</span>
                <button type="button" class="btn-idiom-check ${isUnderstood ? 'checked' : ''}" id="btnIdiomCheck" title="Tandai pemahaman idiom ini">
                    <i class="fa-solid fa-check"></i>
                    <span>${isUnderstood ? 'Sudah Paham' : 'Tandai Paham'}</span>
                </button>
            </div>
        </div>
    `;

    // Bind Audio
    const audioBtn = document.getElementById('btnIdiomAudio');
    if (audioBtn) {
        audioBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            pronouncePhrase(curr.phrase || '', audioBtn);
        });
    }

    // Bind Check
    const checkBtn = document.getElementById('btnIdiomCheck');
    if (checkBtn) {
        checkBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            if (idiomUnderstood.has(idiomIndex)) {
                idiomUnderstood.delete(idiomIndex);
                checkBtn.classList.remove('checked');
                checkBtn.querySelector('span').textContent = 'Tandai Paham';
            } else {
                idiomUnderstood.add(idiomIndex);
                checkBtn.classList.add('checked');
                checkBtn.querySelector('span').textContent = 'Sudah Paham';
                showToast(`Hebat! "${curr.phrase}" ditandai paham.`);
            }

            // Update left pill item state
            const activeItem = listContainer.querySelector(`.idiom-list-item[data-idx="${idiomIndex}"]`);
            if (activeItem) {
                activeItem.classList.toggle('understood', idiomUnderstood.has(idiomIndex));
            }
        });
    }
}

function getIdiomDialogue(item, idx, data) {
    if (item.dialogue && item.dialogue.milo && item.dialogue.user) {
        return item.dialogue;
    }

    const phraseClean = (item.phrase || '').replace(/\.{2,}/g, '').trim();
    const prompts = data?.milo_prompts || [];
    const miloText = prompts[idx % Math.max(1, prompts.length)] || `Could you tell me a little bit about your current studies?`;
    let userText = `Sure! ${phraseClean} in my academic journey.`;

    if (item.example && !item.example.startsWith('Contoh:')) {
        userText = item.example;
    }

    return {
        milo: miloText,
        user: userText
    };
}

// ─── Speech Synthesis Pronunciation Helper ────────────────────────────────────
function pronouncePhrase(phrase, btnElement) {
    const cleanText = phrase.replace(/\.{2,}/g, '').trim();

    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.lang = 'en-US';
        utterance.rate = 0.92;

        if (btnElement) {
            btnElement.classList.add('is-playing');
            btnElement.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> <span>Memutar...</span>`;
        }

        utterance.onend = () => {
            if (btnElement) {
                btnElement.classList.remove('is-playing');
                btnElement.innerHTML = `<i class="fa-solid fa-volume-high"></i> <span>Dengarkan Lagi</span>`;
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

// ─── Studio Mic Check & Equalizer Visualizer ─────────────────────────────────
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
            micStatus.innerHTML = `<i class="fa-solid fa-spinner fa-spin" style="color: #FBB63A;"></i> <span>Mendengarkan... Silakan ucapkan kalimat panduan di atas!</span>`;
        }

        const stream = await navigator.mediaDevices.getUserMedia({
            audio: {
                echoCancellation: true,
                noiseSuppression: false,
                autoGainControl: true
            }
        });
        micStream = stream;

        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        if (audioContext.state === 'suspended') {
            await audioContext.resume();
        }

        analyser = audioContext.createAnalyser();
        analyser.fftSize = 128;
        analyser.smoothingTimeConstant = 0.4;

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
                    const val = dataArray[i] || 0;
                    const barHeight = Math.max(4, (val / 255) * (canvas.height - 10));

                    const grad = canvasCtx.createLinearGradient(0, canvas.height - barHeight, 0, canvas.height);
                    grad.addColorStop(0, '#86EFAC');
                    grad.addColorStop(0.6, '#7A9A82');
                    grad.addColorStop(1, '#FBB63A');

                    canvasCtx.fillStyle = grad;
                    canvasCtx.beginPath();
                    if (typeof canvasCtx.roundRect === 'function') {
                        canvasCtx.roundRect(x, canvas.height - barHeight, barWidth, barHeight, [3, 3, 0, 0]);
                    } else {
                        canvasCtx.rect(x, canvas.height - barHeight, barWidth, barHeight);
                    }
                    canvasCtx.fill();

                    x += barWidth + 3;
                }
            }

            // Vocal Range Analysis
            const vocalRange = Math.min(16, dataArray.length);
            let vocalSum = 0;
            let peakVal = 0;
            for (let i = 0; i < vocalRange; i++) {
                vocalSum += dataArray[i];
                if (dataArray[i] > peakVal) peakVal = dataArray[i];
            }
            const vocalAvg = vocalSum / vocalRange;

            let totalPeak = peakVal;
            for (let i = vocalRange; i < dataArray.length; i++) {
                if (dataArray[i] > totalPeak) totalPeak = dataArray[i];
            }

            // Real-time energy gauge with natural voice scaling
            const energyGaugeFill = document.getElementById('micEnergyGaugeFill');
            if (energyGaugeFill) {
                const effectiveVolume = Math.max(vocalAvg * 1.6, totalPeak * 0.7);
                const percent = Math.min(100, Math.max(0, Math.round((effectiveVolume / 65) * 100)));
                energyGaugeFill.style.width = `${percent}%`;
            }

            // Voice Activity Detection
            if (vocalAvg > 7 || totalPeak > 22) {
                audioSamplesCount++;
                speechEnergySum += vocalAvg;
            }

            if (audioSamplesCount >= 6 && speechEnergySum > 40) {
                validateMicSuccess(false);
                return;
            }

            animationFrameId = requestAnimationFrame(checkLevel);
        }

        checkLevel();

        // Safety timeout
        setTimeout(() => {
            if (isTestingMic && !isMicValidated) {
                stopMicTest();
                if (micStatus) {
                    micStatus.className = 'studio-status-box';
                    micStatus.innerHTML = `<i class="fa-solid fa-circle-exclamation" style="color: #F59E0B;"></i> <span>Suara belum terdeteksi. Silakan coba bicara lebih dekat ke mikrofon, atau klik tombol <strong>Lewati tes ini</strong> di bawah jika mic sudah aktif.</span>`;
                }
            }
        }, 9000);

    } catch (err) {
        console.error('Mic check error:', err);
        stopMicTest();
        if (micStatus) {
            micStatus.className = 'studio-status-box';
            let msg = 'Izin mikrofon belum diberikan pada browser.';
            if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
                msg = 'Izin mikrofon ditolak oleh browser. Klik ikon gembok di address bar untuk mengizinkan.';
            } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
                msg = 'Perangkat mikrofon tidak ditemukan. Sambungkan headset/mic atau gunakan tombol Lewati tes di bawah.';
            } else {
                msg = `Kendala akses mic: ${escapeHtml(err.message)}`;
            }
            micStatus.innerHTML = `<i class="fa-solid fa-triangle-exclamation" style="color: #EF4444;"></i> <span>${msg}</span>`;
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
    const energyGaugeFill = document.getElementById('micEnergyGaugeFill');
    const startBtn = document.getElementById('shelfStartBtn');

    if (studioLivePill) studioLivePill.classList.add('active');
    if (studioLiveStatusText) studioLiveStatusText.textContent = 'Mikrofon Siap & Optimal';

    if (energyGaugeFill) energyGaugeFill.style.width = '75%';

    if (micStatus) {
        micStatus.className = 'studio-status-box success';
        micStatus.innerHTML = `<i class="fa-solid fa-circle-check" style="color: #2D6A4F; font-size: 16px;"></i> <span><strong>Mikrofon Berhasil Divalidasi!</strong> ${bypassed ? 'Kesiapan mikrofon dikonfirmasi.' : 'Suaramu terdengar sangat jernih.'}</span>`;
    }

    if (startBtn) {
        startBtn.removeAttribute('disabled');
    }

    showToast('Mikrofon siap! Anda dapat memulai percakapan.');
}
