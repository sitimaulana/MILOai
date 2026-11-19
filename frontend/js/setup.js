// MILO Topic Setup Flow: Category selection and microlearning module resolution.

let selectedLevel = 'B1';
let selectedGoal = '5_min';
let selectedCategory = 'job_interview';
let selectedTopicId = null;
let selectedTopicData = null;
let currentStep = 1;

const LEVEL_NAMES = {
    'B1': 'Intermediate (B1)',
    'B2': 'Upper-Int. (B2)'
};

const CATEGORY_NAMES = {
    'job_interview': 'Job Interview Practice',
    'academic_discussion': 'Academic Discussion',
    'daily_conversation': 'Daily Conversation'
};

const GOAL_DETAILS = {
    '3_min': { badge: '3 Menit / Hari', label: 'Sprint Kilat' },
    '5_min': { badge: '5 Menit / Hari', label: 'Microlearning (Rekomendasi)' },
    '15_min': { badge: '15 Menit / Hari', label: 'Latihan Lanjutan' }
};

// ─── Instant Fallback Curriculum Topics (Ensures 100% Offline / Fast Reliability) ──
const FALLBACK_CURRICULUM = [
    // Track A: Job Interview
    { topic_id: "A1", track_key: "job_interview", track_code: "TRACK_A", cefr_level: "B1", title: "Self-Introduction & Background", duration_minutes: "3-5", can_do_statement: "Mahasiswa mampu memperkenalkan latar belakang pendidikan, fokus bidang studi, dan ketertarikan karir dalam 3-4 kalimat terhubung secara percaya diri.", preview_vocab: ["I major in...", "Career aspiration"] },
    { topic_id: "A2", track_key: "job_interview", track_code: "TRACK_A", cefr_level: "B1", title: "Discussing Strengths & Soft Skills", duration_minutes: "3-5", can_do_statement: "Mahasiswa mampu menyebutkan 1-2 kelebihan diri (soft skills) beserta contoh singkat penerapannya dalam kerja tim di kampus.", preview_vocab: ["Strong suit", "Team collaboration"] },
    { topic_id: "A3", track_key: "job_interview", track_code: "TRACK_A", cefr_level: "B1", title: "Academic & Internship Projects", duration_minutes: "3-5", can_do_statement: "Mahasiswa mampu mendeskripsikan satu proyek kuliah atau pengalaman magang, peran pribadi, serta hasil yang dicapai secara terstruktur.", preview_vocab: ["Hands-on experience", "Key takeaway"] },
    { topic_id: "A4", track_key: "job_interview", track_code: "TRACK_A", cefr_level: "B2", title: "Handling Difficult Situations (STAR Method)", duration_minutes: "3-5", can_do_statement: "Mahasiswa mampu merespons pertanyaan situasional perilaku (behavioral question) menggunakan kerangka STAR secara terperinci.", preview_vocab: ["Overcame obstacles", "STAR framework"] },
    { topic_id: "A5", track_key: "job_interview", track_code: "TRACK_A", cefr_level: "B2", title: "Career Goals & Company Fit", duration_minutes: "3-5", can_do_statement: "Mahasiswa mampu mengartikulasikan aspirasi karir jangka menengah (3-5 tahun) dan alasan memilih perusahaan secara meyakinkan.", preview_vocab: ["5-year vision", "Company alignment"] },
    { topic_id: "A6", track_key: "job_interview", track_code: "TRACK_A", cefr_level: "B2", title: "Asking Questions to the Interviewer", duration_minutes: "3-5", can_do_statement: "Mahasiswa mampu mengajukan 2-3 pertanyaan kritis dan profesional kepada pewawancara di akhir sesi wawancara.", preview_vocab: ["Inquire further", "Team culture"] },

    // Track B: Academic Discussion
    { topic_id: "B1", track_key: "academic_discussion", track_code: "TRACK_B", cefr_level: "B1", title: "AI in Education: Opportunities & Risks", duration_minutes: "3-5", can_do_statement: "Mahasiswa mampu menyampaikan pandangan pribadi mengenai manfaat dan tantangan penggunaan alat kecerdasan buatan dalam proses belajar.", preview_vocab: ["Double-edged sword", "Personalized learning"] },
    { topic_id: "B2", track_key: "academic_discussion", track_code: "TRACK_B", cefr_level: "B1", title: "Renewable Energy vs Fossil Fuels", duration_minutes: "3-5", can_do_statement: "Mahasiswa mampu membandingkan keuntungan dan kendala transisi energi terbarukan di Indonesia dengan alasan logis.", preview_vocab: ["Sustainable transition", "Cost-benefit balance"] },
    { topic_id: "B3", track_key: "academic_discussion", track_code: "TRACK_B", cefr_level: "B1", title: "Social Media Impact on Student Mental Health", duration_minutes: "3-5", can_do_statement: "Mahasiswa mampu mendiskusikan korelasi antara konsumsi media sosial dan tingkat stres mahasiswa serta solusi pencegahannya.", preview_vocab: ["Mental well-being", "Digital detox"] },
    { topic_id: "B4", track_key: "academic_discussion", track_code: "TRACK_B", cefr_level: "B2", title: "Evaluating Technological Disruption", duration_minutes: "3-5", can_do_statement: "Mahasiswa mampu menguraikan dampak disrupsi teknologi terhadap pasar tenaga kerja masa depan dengan argumen pro dan kontra yang seimbang.", preview_vocab: ["Automation impact", "Paradigm shift"] },
    { topic_id: "B5", track_key: "academic_discussion", track_code: "TRACK_B", cefr_level: "B2", title: "Research Methodologies: Quantitative vs Qualitative", duration_minutes: "3-5", can_do_statement: "Mahasiswa mampu mempertahankan pilihan metodologi penelitian tugas akhir/skripsi dan menjelaskan keunggulan komparatifnya.", preview_vocab: ["Empirical evidence", "Mixed methodology"] },
    { topic_id: "B6", track_key: "academic_discussion", track_code: "TRACK_B", cefr_level: "B2", title: "Academic Integrity & Ethical Research", duration_minutes: "3-5", can_do_statement: "Mahasiswa mampu berargumentasi mengenai batasan plagiarisme, fabrikasi data, dan etika penelitian ilmiah di era generatif AI.", preview_vocab: ["Academic honesty", "Rigorous citation"] },

    // Track C: Daily Conversation
    { topic_id: "C1", track_key: "daily_conversation", track_code: "TRACK_C", cefr_level: "B1", title: "Hobbies, Weekends & Unwinding", duration_minutes: "3-5", can_do_statement: "Mahasiswa mampu menceritakan aktivitas favorit di akhir pekan dan cara melepas penat setelah perkuliahan dengan kosakata santai yang alami.", preview_vocab: ["Unwind and recharge", "Pastime activity"] },
    { topic_id: "C2", track_key: "daily_conversation", track_code: "TRACK_C", cefr_level: "B1", title: "Travel Plans & Memorable Vacations", duration_minutes: "3-5", can_do_statement: "Mahasiswa mampu menceritakan pengalaman bepergian yang paling berkesan dan menyusun rencana perjalanan liburan impian.", preview_vocab: ["Off the beaten track", "Travel itinerary"] },
    { topic_id: "C3", track_key: "daily_conversation", track_code: "TRACK_C", cefr_level: "B1", title: "Campus Life & Student Routine", duration_minutes: "3-5", can_do_statement: "Mahasiswa mampu menggambarkan rutinitas harian di kampus, dinamika tugas kuliah, serta aktivitas organisasi kemahasiswaan.", preview_vocab: ["Campus camaraderie", "Juggling assignments"] },
    { topic_id: "C4", track_key: "daily_conversation", track_code: "TRACK_C", cefr_level: "B2", title: "Work-Life Balance & Burnout Prevention", duration_minutes: "3-5", can_do_statement: "Mahasiswa mampu bertukar pandangan secara mendalam tentang batasan waktu antara pekerjaan, kuliah, dan kesehatan mental.", preview_vocab: ["Work-life boundary", "Preventing burnout"] },
    { topic_id: "C5", track_key: "daily_conversation", track_code: "TRACK_C", cefr_level: "B2", title: "Cross-Cultural Experiences & Adapting", duration_minutes: "3-5", can_do_statement: "Mahasiswa mampu mendiskusikan pengalaman adaptasi budaya, perbedaan kebiasaan sosial, dan strategi komunikasi antarbudaya.", preview_vocab: ["Culture shock", "Broaden horizons"] },
    { topic_id: "C6", track_key: "daily_conversation", track_code: "TRACK_C", cefr_level: "B2", title: "Pop Culture, Movies & Book Critiques", duration_minutes: "3-5", can_do_statement: "Mahasiswa mampu memberikan ulasan kritis, analisis alur, dan rekomendasi film atau buku favorit dengan argumen yang menarik.", preview_vocab: ["Thought-provoking", "Compelling narrative"] }
];

document.addEventListener('DOMContentLoaded', () => {
    // ─── DOM References ────────────────────────────────────────────────────────
    const step1Container = document.getElementById('step1CategoryContainer');
    const step2Container = document.getElementById('step2SpecificContainer');

    const shelfStep1 = document.getElementById('shelfStep1');
    const shelfStep2 = document.getElementById('shelfStep2');

    const dotStep1 = document.getElementById('dotStep1');
    const dotStep2 = document.getElementById('dotStep2');

    const shelfCategoryBadge = document.getElementById('shelfCategoryBadge');
    const shelfCategoryLabel = document.getElementById('shelfCategoryLabel');
    const shelfSpecificTopicBadge = document.getElementById('shelfSpecificTopicBadge');
    const shelfSpecificTopicTitle = document.getElementById('shelfSpecificTopicTitle');

    const btnHeaderBack = document.getElementById('btnHeaderBack');
    const btnGotoStep2 = document.getElementById('btnGotoStep2');
    const btnBackToStep1 = document.getElementById('btnBackToStep1');
    const btnLaunchPractice = document.getElementById('btnLaunchPractice');
    const specificTopicsGrid = document.getElementById('specificTopicsGrid');
    const stepSpecificHint = document.getElementById('stepSpecificHint');

    const setupLevelPillText = document.getElementById('setupLevelPillText');

    // ─── Initialize Active CEFR Level & Daily Goal from User Profile ─────────────
    try {
        const authUser = JSON.parse(localStorage.getItem('milo_user'));
        if (authUser && authUser.cefr_level) {
            selectedLevel = authUser.cefr_level;
        }
        if (authUser && authUser.daily_goal) {
            selectedGoal = authUser.daily_goal;
        }
    } catch {}

    function updateLevelPill() {
        if (setupLevelPillText) {
            setupLevelPillText.textContent = `Level ${selectedLevel}`;
        }
    }
    updateLevelPill();

    // ─── URL Parameters Check (?topic=...&level=...) ───────────────────────────
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('level')) {
        const urlLevel = urlParams.get('level').toUpperCase();
        if (urlLevel === 'B1' || urlLevel === 'B2') {
            selectedLevel = urlLevel;
            updateLevelPill();
        }
    }

    let startAtStep2 = false;
    if (urlParams.has('topic')) {
        const urlTopic = urlParams.get('topic');
        if (CATEGORY_NAMES[urlTopic]) {
            selectedCategory = urlTopic;
            startAtStep2 = true;
        }
    }

    // ─── Step Navigation Controller ────────────────────────────────────────────
    function goToStep(step) {
        currentStep = step;

        if (step1Container) step1Container.style.display = (step === 1) ? 'block' : 'none';
        if (step2Container) step2Container.style.display = (step === 2) ? 'block' : 'none';

        if (shelfStep1) shelfStep1.style.display = (step === 1) ? 'flex' : 'none';
        if (shelfStep2) shelfStep2.style.display = (step === 2) ? 'flex' : 'none';

        if (dotStep1) dotStep1.classList.toggle('active', step === 1);
        if (dotStep2) dotStep2.classList.toggle('active', step === 2);

        if (shelfCategoryBadge) shelfCategoryBadge.textContent = CATEGORY_NAMES[selectedCategory] || selectedCategory;

        if (step === 2) {
            loadSpecificTopics();
        }

        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    // Direct dot navigation
    if (dotStep1) dotStep1.addEventListener('click', () => goToStep(1));
    if (dotStep2) dotStep2.addEventListener('click', () => goToStep(2));

    // Bottom Shelf Navigation Buttons
    if (btnGotoStep2) btnGotoStep2.addEventListener('click', () => goToStep(2));
    if (btnBackToStep1) btnBackToStep1.addEventListener('click', () => goToStep(1));

    // Header Back Button
    if (btnHeaderBack) {
        btnHeaderBack.addEventListener('click', () => {
            if (currentStep > 1) {
                goToStep(1);
            } else {
                const isUi = window.location.pathname.includes('/ui/');
                window.location.href = isUi ? '/ui/dashboard.html' : 'dashboard.html';
            }
        });
    }

    // ─── 1. Category Selection (Step 1) ────────────────────────────────────────
    const categoryCards = document.querySelectorAll('#step1CategoryContainer .topic-selection-card[data-topic]');

    function selectCategoryCard(card, andAdvance = true) {
        categoryCards.forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        selectedCategory = card.getAttribute('data-topic');

        if (shelfCategoryBadge) {
            shelfCategoryBadge.textContent = CATEGORY_NAMES[selectedCategory] || selectedCategory;
        }
        selectedTopicId = null;
        selectedTopicData = null;

        if (andAdvance) {
            goToStep(2);
        }
    }

    categoryCards.forEach(card => {
        card.addEventListener('click', () => selectCategoryCard(card, true));
        card.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                selectCategoryCard(card, true);
            }
        });
    });

    // If starting from URL param or default, preselect card
    if (selectedCategory) {
        const preCard = Array.from(categoryCards).find(c => c.getAttribute('data-topic') === selectedCategory);
        if (preCard) selectCategoryCard(preCard, false);
    }

    // ─── 2. Load Specific Topics (Step 2) ──────────────────────────────────────
    async function loadSpecificTopics() {
        if (!specificTopicsGrid) return;

        if (stepSpecificHint) {
            stepSpecificHint.textContent = `Pilih modul microlearning untuk kategori "${CATEGORY_NAMES[selectedCategory] || selectedCategory}" (Level ${selectedLevel}):`;
        }

        specificTopicsGrid.innerHTML = `
            <div style="text-align: center; padding: 36px 16px; color: var(--text-slate);">
                <i class="fa-solid fa-spinner fa-spin" style="font-size: 24px; color: var(--primary);"></i>
                <div style="margin-top: 10px; font-weight: 600;">Memuat modul spesifik...</div>
            </div>
        `;

        let topics = [];

        try {
            const resp = await fetch(`/api/v1/curriculum/topics?track=${encodeURIComponent(selectedCategory)}&cefr_level=${encodeURIComponent(selectedLevel)}`);
            if (resp.ok) {
                topics = await resp.json();
            }
        } catch (fetchErr) {
            console.warn('API fetch failed, falling back to embedded curriculum topics:', fetchErr);
        }

        if (!topics || topics.length === 0) {
            topics = FALLBACK_CURRICULUM.filter(t => t.track_key === selectedCategory && t.cefr_level === selectedLevel);
        }

        if (!topics || topics.length === 0) {
            specificTopicsGrid.innerHTML = `
                <div style="text-align: center; padding: 32px 16px; background: #FFFFFF; border-radius: 16px; border: 1.5px dashed var(--border-subtle);">
                    <i class="fa-regular fa-folder-open" style="font-size: 28px; color: var(--text-muted); margin-bottom: 8px;"></i>
                    <p style="font-weight: 700; color: var(--text-navy);">Belum ada modul untuk level dan kategori ini.</p>
                </div>
            `;
            return;
        }

        specificTopicsGrid.innerHTML = '';

        let activeTopic = topics.find(t => t.topic_id === selectedTopicId) || topics[0];
        selectedTopicId = activeTopic.topic_id;
        selectedTopicData = activeTopic;

        updateShelfTopicInfo(activeTopic);

        topics.forEach(top => {
            const card = document.createElement('div');
            card.className = `specific-topic-card ${top.topic_id === selectedTopicId ? 'selected' : ''}`;
            card.setAttribute('tabindex', '0');
            card.setAttribute('role', 'button');
            card.setAttribute('aria-pressed', top.topic_id === selectedTopicId ? 'true' : 'false');

            let vocabChipsHtml = '';
            const previewItems = top.preview_vocab || [];
            if (previewItems.length > 0) {
                const chips = previewItems.map(w => `<span class="topic-vocab-chip">${escapeHtml(w)}</span>`).join('');
                vocabChipsHtml = `
                    <div class="topic-vocab-preview-row">
                        <span class="topic-vocab-preview-label"><i class="fa-solid fa-tags" style="font-size: 10px;"></i> Fokus Frasa:</span>
                        ${chips}
                    </div>
                `;
            }

            card.innerHTML = `
                <div class="specific-topic-header">
                    <span class="topic-id-badge"><i class="fa-solid fa-graduation-cap"></i> Modul ${escapeHtml(top.topic_id)}</span>
                    <div class="topic-meta-badges">
                        <span class="topic-meta-pill"><i class="fa-regular fa-clock"></i> ${escapeHtml(top.duration_minutes)} Mnt</span>
                        <span class="topic-meta-pill level-pill"><i class="fa-solid fa-layer-group"></i> ${escapeHtml(top.cefr_level)}</span>
                        <span class="selection-indicator"><i class="fa-solid fa-circle-check"></i> Terpilih</span>
                    </div>
                </div>
                <div class="specific-topic-title">${escapeHtml(top.title)}</div>
                <div class="specific-topic-cando-box">
                    <span class="specific-topic-cando-label"><i class="fa-solid fa-bullseye"></i> Capaian Target</span>
                    <div class="specific-topic-cando">${escapeHtml(top.can_do_statement)}</div>
                </div>
                ${vocabChipsHtml}
            `;

            function selectThisTopic() {
                document.querySelectorAll('.specific-topic-card').forEach(c => {
                    c.classList.remove('selected');
                    c.setAttribute('aria-pressed', 'false');
                });
                card.classList.add('selected');
                card.setAttribute('aria-pressed', 'true');
                selectedTopicId = top.topic_id;
                selectedTopicData = top;
                updateShelfTopicInfo(top);
            }

            card.addEventListener('click', selectThisTopic);
            card.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    selectThisTopic();
                }
            });

            card.addEventListener('dblclick', () => {
                if (btnLaunchPractice) btnLaunchPractice.click();
            });

            specificTopicsGrid.appendChild(card);
        });
    }

    function updateShelfTopicInfo(topic) {
        if (!topic) return;
        if (shelfSpecificTopicBadge) shelfSpecificTopicBadge.textContent = `[${topic.topic_id}]`;
        if (shelfSpecificTopicTitle) shelfSpecificTopicTitle.textContent = topic.title;
    }

    // ─── 3. Launch Pre-Session Briefing ────────────────────────────────────────
    if (btnLaunchPractice) {
        btnLaunchPractice.addEventListener('click', async () => {
            if (!selectedLevel || !selectedCategory || !selectedTopicId) {
                alert('Silakan pilih kategori dan topik microlearning terlebih dahulu.');
                return;
            }

            btnLaunchPractice.disabled = true;
            btnLaunchPractice.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> <span>Menyiapkan Modul...</span>`;

            try {
                const token = localStorage.getItem('milo_token');
                const userRaw = localStorage.getItem('milo_user');
                let user = null;
                try { user = userRaw ? JSON.parse(userRaw) : null; } catch {}

                const headers = { 'Content-Type': 'application/json' };
                if (token) headers['Authorization'] = `Bearer ${token}`;

                const requestPayload = {
                    cefr_level: selectedLevel,
                    topic: selectedCategory,
                    topic_id: selectedTopicId,
                    daily_goal: selectedGoal,
                };
                if (user && user.id) {
                    requestPayload.user_id = user.id;
                }

                const response = await fetch('/api/v1/session/start', {
                    method: 'POST',
                    headers: headers,
                    body: JSON.stringify(requestPayload)
                });

                if (!response.ok) {
                    const errText = await response.text();
                    throw new Error(`Server returned ${response.status}: ${errText}`);
                }

                const data = await response.json();

                sessionStorage.setItem('milo_session_id', data.session_id);
                sessionStorage.setItem('milo_topic', selectedCategory);
                sessionStorage.setItem('milo_topic_id', selectedTopicId);
                sessionStorage.setItem('milo_topic_title', data.topic_title || (selectedTopicData && selectedTopicData.title) || '');
                sessionStorage.setItem('milo_topic_label', data.topic_label);
                sessionStorage.setItem('milo_cefr_level', data.cefr_level);
                sessionStorage.setItem('milo_daily_goal', data.daily_goal || selectedGoal);
                sessionStorage.setItem('milo_initial_greeting', data.greeting);
                if (data.greeting_translation) {
                    sessionStorage.setItem('milo_initial_translation', data.greeting_translation);
                }
                if (data.audio_base64) {
                    sessionStorage.setItem('milo_initial_audio', data.audio_base64);
                }

                window.location.href = `/ui/briefing.html?session_id=${encodeURIComponent(data.session_id)}&topic_id=${encodeURIComponent(selectedTopicId)}`;
            } catch (error) {
                console.warn('Backend start session failed, using fallback session:', error);
                const mockSessionId = 'offline_' + Date.now();
                sessionStorage.setItem('milo_session_id', mockSessionId);
                sessionStorage.setItem('milo_topic', selectedCategory);
                sessionStorage.setItem('milo_topic_id', selectedTopicId);
                sessionStorage.setItem('milo_topic_title', (selectedTopicData && selectedTopicData.title) || '');
                sessionStorage.setItem('milo_topic_label', CATEGORY_NAMES[selectedCategory] || selectedCategory);
                sessionStorage.setItem('milo_cefr_level', selectedLevel);
                sessionStorage.setItem('milo_daily_goal', selectedGoal);
                window.location.href = `/ui/briefing.html?session_id=${encodeURIComponent(mockSessionId)}&topic_id=${encodeURIComponent(selectedTopicId)}`;
            }
        });
    }

    // ─── Initial Step Launch ───────────────────────────────────────────────────
    if (startAtStep2) {
        goToStep(2);
    } else {
        goToStep(1);
    }
});
