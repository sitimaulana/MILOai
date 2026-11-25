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

// ─── Book Configurations (Figma Node 2403-1595 Closed Book Showcase) ────────
const BOOK_CONFIG = {
    'job_interview': {
        title: 'Interview Playbook',
        spineClass: 'spine-blue',
        trackLabel: 'Job Interview Practice',
        subtitleDesc: '3 simulasi terstruktur untuk menaklukkan pertanyaan HRD',
        shortTrack: 'Interview'
    },
    'academic_discussion': {
        title: 'Campus Handbook',
        spineClass: 'spine-green',
        trackLabel: 'Academic Discussion Practice',
        subtitleDesc: '3 modul diskusi ilmiah, presentasi, dan adu argumen',
        shortTrack: 'Academic'
    },
    'daily_conversation': {
        title: 'Everyday Guide',
        spineClass: 'spine-yellow',
        trackLabel: 'Daily Conversation Practice',
        subtitleDesc: '3 topik percakapan praktis untuk situasi sehari-hari',
        shortTrack: 'Daily'
    }
};

// ─── Instant Fallback Curriculum Topics (Ensures 100% Offline / Fast Reliability) ──
const FALLBACK_CURRICULUM = [
    // Track A: Job Interview Practice
    { topic_id: "A1", track_key: "job_interview", track_code: "TRACK_A", cefr_level: "B1", title: "Self-Introduction & Background", duration_minutes: "3-5", can_do_statement: "Mahasiswa mampu memperkenalkan latar belakang pendidikan, fokus bidang studi, dan ketertarikan karir dalam 3-4 kalimat terhubung secara percaya diri.", preview_vocab: ["I recently graduated with a degree in...", "My primary career aspiration is..."] },
    { topic_id: "A2", track_key: "job_interview", track_code: "TRACK_A", cefr_level: "B1", title: "Discussing Strengths & Soft Skills", duration_minutes: "3-5", can_do_statement: "Mahasiswa mampu menyebutkan 1-2 kelebihan diri (soft skills) beserta contoh singkat penerapannya dalam kerja tim di kampus.", preview_vocab: ["One of my key strengths is...", "I thrive in collaborative team environments..."] },
    { topic_id: "A3", track_key: "job_interview", track_code: "TRACK_A", cefr_level: "B1", title: "Handling Behavioral Scenarios (STAR Method)", duration_minutes: "3-5", can_do_statement: "Mahasiswa mampu menjawab pertanyaan perilaku kerja menggunakan metode STAR (Situation, Task, Action, Result) secara terstruktur.", preview_vocab: ["In that specific situation, my task was...", "As a result, our team successfully delivered..."] },
    { topic_id: "A4", track_key: "job_interview", track_code: "TRACK_A", cefr_level: "B2", title: "Handling Difficult Situations (STAR Method)", duration_minutes: "3-5", can_do_statement: "Mahasiswa mampu merespons pertanyaan situasional perilaku (behavioral question) menggunakan kerangka STAR secara terperinci.", preview_vocab: ["Overcame obstacles", "STAR framework"] },
    { topic_id: "A5", track_key: "job_interview", track_code: "TRACK_A", cefr_level: "B2", title: "Career Goals & Company Fit", duration_minutes: "3-5", can_do_statement: "Mahasiswa mampu mengartikulasikan aspirasi karir jangka menengah (3-5 tahun) dan alasan memilih perusahaan secara meyakinkan.", preview_vocab: ["5-year vision", "Company alignment"] },
    { topic_id: "A6", track_key: "job_interview", track_code: "TRACK_A", cefr_level: "B2", title: "Asking Questions to the Interviewer", duration_minutes: "3-5", can_do_statement: "Mahasiswa mampu mengajukan 2-3 pertanyaan kritis dan profesional kepada pewawancara di akhir sesi wawancara.", preview_vocab: ["Inquire further", "Team culture"] },

    // Track B: Academic Discussion (Figma Node 2403-1595 exact match)
    { topic_id: "B1", track_key: "academic_discussion", track_code: "TRACK_B", cefr_level: "B1", title: "Artificial Intelligence in Education", duration_minutes: "3-5", can_do_statement: "Mahasiswa mampu menyampaikan opini sederhana beserta alasan logis mengenai manfaat dan batasan penggunaan kecerdasan buatan (AI) dalam perkuliahan.", preview_vocab: ["In my opinion, AI tools can be beneficial for...", "On the other hand, relying too much on..."] },
    { topic_id: "B2", track_key: "academic_discussion", track_code: "TRACK_B", cefr_level: "B1", title: "Final Project (Capstone) Progress", duration_minutes: "3-5", can_do_statement: "Mahasiswa mampu memaparkan progres tugas akhir/skripsi secara ringkas, meliputi apa yang sudah diselesaikan, apa yang sedang dikerjakan, dan target selanjutnya.", preview_vocab: ["So far, I have completed the...", "Currently, I am in the middle of..."] },
    { topic_id: "B3", track_key: "academic_discussion", track_code: "TRACK_B", cefr_level: "B1", title: "Agreeing & Disagreeing Politely", duration_minutes: "3-5", can_do_statement: "Mahasiswa mampu menyetujui sebagian pendapat rekan diskusi sekaligus menyampaikan sanggahan atau sudut pandang berbeda secara santun dan akademis.", preview_vocab: ["I see your point, however...", "That is a valid argument, but have we considered..."] },
    { topic_id: "B4", track_key: "academic_discussion", track_code: "TRACK_B", cefr_level: "B2", title: "Evaluating Technological Disruption", duration_minutes: "3-5", can_do_statement: "Mahasiswa mampu menguraikan dampak disrupsi teknologi terhadap pasar tenaga kerja masa depan dengan argumen pro dan kontra yang seimbang.", preview_vocab: ["Automation impact", "Paradigm shift"] },
    { topic_id: "B5", track_key: "academic_discussion", track_code: "TRACK_B", cefr_level: "B2", title: "Research Methodologies: Quantitative vs Qualitative", duration_minutes: "3-5", can_do_statement: "Mahasiswa mampu mempertahankan pilihan metodologi penelitian tugas akhir/skripsi dan menjelaskan keunggulan komparatifnya.", preview_vocab: ["Empirical evidence", "Mixed methodology"] },
    { topic_id: "B6", track_key: "academic_discussion", track_code: "TRACK_B", cefr_level: "B2", title: "Academic Integrity & Ethical Research", duration_minutes: "3-5", can_do_statement: "Mahasiswa mampu berargumentasi mengenai batasan plagiarisme, fabrikasi data, dan etika penelitian ilmiah di era generatif AI.", preview_vocab: ["Academic honesty", "Rigorous citation"] },

    // Track C: Daily Conversation
    { topic_id: "C1", track_key: "daily_conversation", track_code: "TRACK_C", cefr_level: "B1", title: "Hobbies, Weekend & Unwinding", duration_minutes: "3-5", can_do_statement: "Mahasiswa mampu menceritakan aktivitas favorit di akhir pekan dan cara melepas penat setelah perkuliahan dengan kosakata santai yang alami.", preview_vocab: ["Whenever I get some free time, I love to...", "It helps me unwind and recharge after..."] },
    { topic_id: "C2", track_key: "daily_conversation", track_code: "TRACK_C", cefr_level: "B1", title: "Travel Plans & Memorable Vacations", duration_minutes: "3-5", can_do_statement: "Mahasiswa mampu menceritakan pengalaman bepergian yang paling berkesan dan menyusun rencana perjalanan liburan impian.", preview_vocab: ["One of the most memorable trips I had was...", "I am really looking forward to visiting..."] },
    { topic_id: "C3", track_key: "daily_conversation", track_code: "TRACK_C", cefr_level: "B1", title: "Campus Life & Student Routine", duration_minutes: "3-5", can_do_statement: "Mahasiswa mampu menggambarkan rutinitas harian di kampus, dinamika tugas kuliah, serta aktivitas organisasi kemahasiswaan.", preview_vocab: ["My typical day on campus begins with...", "Juggling lectures and coursework requires..."] },
    { topic_id: "C4", track_key: "daily_conversation", track_code: "TRACK_C", cefr_level: "B2", title: "Work-Life Balance & Burnout Prevention", duration_minutes: "3-5", can_do_statement: "Mahasiswa mampu bertukar pandangan secara mendalam tentang batasan waktu antara pekerjaan, kuliah, dan kesehatan mental.", preview_vocab: ["Work-life boundary", "Preventing burnout"] },
    { topic_id: "C5", track_key: "daily_conversation", track_code: "TRACK_C", cefr_level: "B2", title: "Cross-Cultural Experiences & Adapting", duration_minutes: "3-5", can_do_statement: "Mahasiswa mampu mendiskusikan pengalaman adaptasi budaya, perbedaan kebiasaan sosial, dan strategi komunikasi antarbudaya.", preview_vocab: ["Culture shock", "Broaden horizons"] },
    { topic_id: "C6", track_key: "daily_conversation", track_code: "TRACK_C", cefr_level: "B2", title: "Pop Culture, Movies & Book Critiques", duration_minutes: "3-5", can_do_statement: "Mahasiswa mampu memberikan ulasan kritis, analisis alur, dan rekomendasi film atau buku favorit dengan argumen yang menarik.", preview_vocab: ["Thought-provoking", "Compelling narrative"] }
];

document.addEventListener('DOMContentLoaded', () => {
    if (window.lucide && typeof window.lucide.createIcons === 'function') {
        window.lucide.createIcons();
    }

    if (typeof requireAuth === 'function' && !requireAuth()) {
        return;
    }

    // ─── DOM References ────────────────────────────────────────────────────────
    const step1Container = document.getElementById('step1CategoryContainer');
    const stepBookContainer = document.getElementById('stepBookCoverContainer');
    const step2Container = document.getElementById('step2SpecificContainer');

    const scrapbookWrapper = document.getElementById('scrapbookWrapper');
    const interactiveBookCard = document.getElementById('interactiveBookCard');
    const btnBookOpen = document.getElementById('btnBookOpen');
    const btnBookBackToCategory = document.getElementById('btnBookBackToCategory');
    const bookBookmarkText = document.getElementById('bookBookmarkText');
    const bookSpine = document.getElementById('bookSpine');
    const bookTitleHeading = document.getElementById('bookTitleHeading');
    const bookSubtitleLevel = document.getElementById('bookSubtitleLevel');
    const bookSubtitleDesc = document.getElementById('bookSubtitleDesc');
    const insideTrackBadge = document.getElementById('insideTrackBadge');
    const insideWelcomeTitle = document.getElementById('insideWelcomeTitle');

    const shelfStep1 = document.getElementById('shelfStep1');
    const shelfStep2 = document.getElementById('shelfStep2');
    const setupBottomShelf = document.querySelector('.setup-bottom-shelf');

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
    function updateBookCoverUI() {
        const config = BOOK_CONFIG[selectedCategory] || BOOK_CONFIG['job_interview'];
        if (bookTitleHeading) bookTitleHeading.textContent = config.title;
        if (bookSubtitleLevel) bookSubtitleLevel.textContent = `${config.trackLabel} (Level ${selectedLevel})`;
        if (bookSubtitleDesc) bookSubtitleDesc.textContent = config.subtitleDesc;
        if (insideTrackBadge) insideTrackBadge.textContent = (config.shortTrack + ' Practice').toUpperCase();
        if (insideWelcomeTitle) insideWelcomeTitle.textContent = config.title;
        if (bookSpine) {
            bookSpine.className = `book-spine ${config.spineClass}`;
        }
        if (bookBookmarkText) {
            let uName = 'milo';
            try {
                const u = JSON.parse(localStorage.getItem('milo_user'));
                if (u && (u.username || u.full_name)) uName = u.username || u.full_name;
            } catch {}
            bookBookmarkText.textContent = `${uName} - ${selectedLevel}`;
        }
        if (scrapbookWrapper) {
            scrapbookWrapper.classList.remove('opening');
        }
        if (interactiveBookCard) {
            interactiveBookCard.classList.remove('opening');
        }
    }

    function goToStep(step) {
        currentStep = step;

        const isStep1 = (step === 1);
        const isBook = (step === 'book' || step === 1.5);
        const isStep2 = (step === 2);

        if (step1Container) step1Container.style.display = isStep1 ? 'block' : 'none';
        if (stepBookContainer) stepBookContainer.style.display = isBook ? 'block' : 'none';
        if (step2Container) step2Container.style.display = isStep2 ? 'block' : 'none';

        // Bottom shelf is hidden in Step 1 and Book cover, shown only in Step 2
        if (setupBottomShelf) {
            setupBottomShelf.style.display = isStep2 ? 'flex' : 'none';
        }

        if (shelfStep1) shelfStep1.style.display = 'none';
        if (shelfStep2) shelfStep2.style.display = isStep2 ? 'flex' : 'none';

        if (dotStep1) dotStep1.classList.toggle('active', isStep1);
        if (dotStep2) dotStep2.classList.toggle('active', isStep2);

        if (shelfCategoryBadge) shelfCategoryBadge.textContent = CATEGORY_NAMES[selectedCategory] || selectedCategory;
        if (stepSpecificHint) {
            stepSpecificHint.textContent = `Pilih modul microlearning untuk kategori "${CATEGORY_NAMES[selectedCategory] || selectedCategory}" (Level ${selectedLevel}):`;
        }

        if (isBook) {
            updateBookCoverUI();
        } else if (isStep2) {
            loadSpecificTopics();
        }

        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    // Direct dot navigation
    if (dotStep1) dotStep1.addEventListener('click', () => goToStep(1));
    if (dotStep2) dotStep2.addEventListener('click', () => goToStep(2));

    // Bottom Shelf Navigation Buttons
    if (btnGotoStep2) btnGotoStep2.addEventListener('click', () => goToStep(2));
    if (btnBackToStep1) {
        btnBackToStep1.addEventListener('click', () => goToStep(1));
    }

    // Book Cover Interactions: 3D Scrapbook Cover Opens to the left
    function handleBookOpen() {
        if (!interactiveBookCard || interactiveBookCard.classList.contains('opening')) return;
        if (scrapbookWrapper) scrapbookWrapper.classList.add('opening');
        interactiveBookCard.classList.add('opening');
        setTimeout(() => {
            goToStep(2);
            if (scrapbookWrapper) scrapbookWrapper.classList.remove('opening');
            interactiveBookCard.classList.remove('opening');
        }, 760);
    }

    if (interactiveBookCard) {
        interactiveBookCard.addEventListener('click', handleBookOpen);
        interactiveBookCard.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                handleBookOpen();
            }
        });
    }

    if (btnBookOpen) {
        btnBookOpen.addEventListener('click', (e) => {
            e.stopPropagation();
            handleBookOpen();
        });
    }

    if (btnBookBackToCategory) {
        btnBookBackToCategory.addEventListener('click', () => goToStep(1));
    }

    // Header Back Button
    if (btnHeaderBack) {
        btnHeaderBack.addEventListener('click', () => {
            if (currentStep === 2) {
                goToStep('book');
            } else if (currentStep === 'book' || currentStep === 1.5) {
                goToStep(1);
            } else {
                const isUi = window.location.pathname.includes('/ui/');
                window.location.href = isUi ? '/ui/dashboard.html' : 'dashboard.html';
            }
        });
    }

    // ─── 1. Category Selection (Step 1) ────────────────────────────────────────
    const categoryCards = document.querySelectorAll('#step1CategoryContainer [data-topic]');

    function selectCategoryCard(card, andAdvance = true) {
        categoryCards.forEach(c => {
            c.classList.remove('selected');
            c.setAttribute('aria-pressed', 'false');
        });
        card.classList.add('selected');
        card.setAttribute('aria-pressed', 'true');
        selectedCategory = card.getAttribute('data-topic');

        if (shelfCategoryBadge) {
            shelfCategoryBadge.textContent = CATEGORY_NAMES[selectedCategory] || selectedCategory;
        }
        if (stepSpecificHint) {
            stepSpecificHint.textContent = `Pilih modul microlearning untuk kategori "${CATEGORY_NAMES[selectedCategory] || selectedCategory}" (Level ${selectedLevel}):`;
        }
        selectedTopicId = null;
        selectedTopicData = null;

        if (andAdvance) {
            goToStep('book');
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

    // If starting from URL param or default, preselect card and activate initial step
    if (selectedCategory) {
        const preCard = Array.from(categoryCards).find(c => c.getAttribute('data-topic') === selectedCategory);
        if (preCard) selectCategoryCard(preCard, false);
    }

    // Explicitly initialize view to Step 1 (or Step 2 if URL specifies ?topic=...)
    goToStep(startAtStep2 ? 2 : 1);

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
                        <span class="topic-vocab-preview-label">Fokus Frasa:</span>
                        <div class="topic-vocab-chips-list">
                            ${chips}
                        </div>
                    </div>
                `;
            }

            const topicDisplay = (typeof formatTopicDisplay === 'function')
                ? formatTopicDisplay(top)
                : { label: `Topik #${top.topic_number || top.topic_id}`, icon: 'fa-book-open' };

            card.innerHTML = `
                <div class="specific-topic-header">
                    <span class="topic-id-badge">${escapeHtml(topicDisplay.label.toUpperCase())}</span>
                    <span class="selection-indicator"><i class="fa-solid fa-check"></i> Terpilih</span>
                </div>
                <div class="specific-topic-title">${escapeHtml(top.title)}</div>
                <div class="specific-topic-cando-box">
                    <span class="specific-topic-cando-label">CAPAIAN TARGET</span>
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
        const topicDisplay = (typeof formatTopicDisplay === 'function')
            ? formatTopicDisplay(topic)
            : { label: `Topik #${topic.topic_number || topic.topic_id}` };
        if (shelfSpecificTopicBadge) shelfSpecificTopicBadge.textContent = topicDisplay.label;
        if (shelfSpecificTopicTitle) shelfSpecificTopicTitle.textContent = topic.title;
    }

    // ─── 3. Launch Pre-Session Briefing ────────────────────────────────────────
    if (btnLaunchPractice) {
        btnLaunchPractice.addEventListener('click', async () => {
            if (!selectedLevel || !selectedCategory || !selectedTopicId) {
                alert('Silakan pilih kategori dan topik microlearning terlebih dahulu.');
                return;
            }

            // Save user-friendly topic display label for subsequent screens
            if (selectedTopicData) {
                const topicDisplay = (typeof formatTopicDisplay === 'function')
                    ? formatTopicDisplay(selectedTopicData)
                    : null;
                if (topicDisplay) {
                    sessionStorage.setItem('milo_topic_label_display', topicDisplay.label);
                }
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
