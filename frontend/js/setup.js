// ═══════════════════════════════════════════════════════════════════════════════
// MILO AI English Tutor — 3-Step Setup Flow Logic (Warm Sand Mockup Theme)
// Step 1: Select CEFR Level -> Step 2: Select Daily Goal -> Step 3: Select Topic
// ═══════════════════════════════════════════════════════════════════════════════

let selectedLevel = 'B1';
let selectedGoal = '15_min';
let selectedTopic = 'job_interview';
let currentStep = 1;

const LEVEL_NAMES = {
    'B1': 'Intermediate (B1)',
    'B2': 'Upper-Int. (B2)'
};

const GOAL_DETAILS = {
    '5_min': { badge: '5 Menit / Hari', label: 'Santai & Ringan' },
    '15_min': { badge: '15 Menit / Hari', label: 'Konsisten (Rekomendasi)' },
    '30_min': { badge: '30 Menit / Hari', label: 'Intensif & Mendalam' }
};

document.addEventListener('DOMContentLoaded', () => {
    // ─── DOM References ────────────────────────────────────────────────────────
    const step1Container = document.getElementById('step1LevelContainer');
    const step2Container = document.getElementById('step2GoalContainer');
    const step3Container = document.getElementById('step3TopicContainer');

    const shelfStep1 = document.getElementById('shelfStep1');
    const shelfStep2 = document.getElementById('shelfStep2');
    const shelfStep3 = document.getElementById('shelfStep3');

    const dotStep1 = document.getElementById('dotStep1');
    const dotStep2 = document.getElementById('dotStep2');
    const dotStep3 = document.getElementById('dotStep3');

    const shelfLevelLabel = document.getElementById('shelfLevelLabel');
    const shelfGoalBadge = document.getElementById('shelfGoalBadge');
    const shelfGoalLabel = document.getElementById('shelfGoalLabel');
    const shelfFinalLevelBadge = document.getElementById('shelfFinalLevelBadge');

    const btnHeaderBack = document.getElementById('btnHeaderBack');
    const btnGotoStep2 = document.getElementById('btnGotoStep2');
    const btnBackToStep1 = document.getElementById('btnBackToStep1');
    const btnGotoStep3 = document.getElementById('btnGotoStep3');
    const btnBackToStep2 = document.getElementById('btnBackToStep2');
    const btnLaunchPractice = document.getElementById('btnLaunchPractice');

    // ─── Step Navigation Controller ────────────────────────────────────────────
    function goToStep(step) {
        currentStep = step;

        // Containers
        if (step1Container) step1Container.style.display = (step === 1) ? 'block' : 'none';
        if (step2Container) step2Container.style.display = (step === 2) ? 'block' : 'none';
        if (step3Container) step3Container.style.display = (step === 3) ? 'block' : 'none';

        // Bottom Shelves
        if (shelfStep1) shelfStep1.style.display = (step === 1) ? 'flex' : 'none';
        if (shelfStep2) shelfStep2.style.display = (step === 2) ? 'flex' : 'none';
        if (shelfStep3) shelfStep3.style.display = (step === 3) ? 'flex' : 'none';

        // Stepper Dots
        if (dotStep1) dotStep1.classList.toggle('active', step === 1);
        if (dotStep2) dotStep2.classList.toggle('active', step === 2);
        if (dotStep3) dotStep3.classList.toggle('active', step === 3);

        // Update indicators
        if (shelfFinalLevelBadge) {
            shelfFinalLevelBadge.textContent = `Level ${selectedLevel}`;
        }

        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    // Direct dot navigation
    if (dotStep1) dotStep1.addEventListener('click', () => goToStep(1));
    if (dotStep2) dotStep2.addEventListener('click', () => goToStep(2));
    if (dotStep3) dotStep3.addEventListener('click', () => goToStep(3));

    // Ensure initial button state is properly enabled since B1 is selected by default
    if (btnGotoStep2) {
        btnGotoStep2.disabled = !selectedLevel;
        btnGotoStep2.addEventListener('click', (e) => {
            e.preventDefault();
            if (!selectedLevel) {
                alert('Pilih level terlebih dahulu.');
                return;
            }
            goToStep(2);
        });
    }

    if (btnBackToStep1) {
        btnBackToStep1.addEventListener('click', (e) => {
            e.preventDefault();
            goToStep(1);
        });
    }

    if (btnGotoStep3) {
        btnGotoStep3.disabled = !selectedGoal;
        btnGotoStep3.addEventListener('click', (e) => {
            e.preventDefault();
            if (!selectedGoal) {
                alert('Pilih target harian terlebih dahulu.');
                return;
            }
            goToStep(3);
        });
    }

    if (btnBackToStep2) {
        btnBackToStep2.addEventListener('click', (e) => {
            e.preventDefault();
            goToStep(2);
        });
    }

    // Header Back button
    // Header Back button
    if (btnHeaderBack) {
        btnHeaderBack.addEventListener('click', (e) => {
            e.preventDefault();
            if (currentStep > 1) {
                goToStep(currentStep - 1);
            } else {
                // If on step 1, go back to home
                window.location.href = '/ui/index.html';
            }
        });
    }

    // Check URL parameter for initial level
    const urlParams = new URLSearchParams(window.location.search);
    const paramLevel = urlParams.get('level');
    if (paramLevel && (paramLevel.toUpperCase() === 'B1' || paramLevel.toUpperCase() === 'B2')) {
        selectedLevel = paramLevel.toUpperCase();
    }

    // ─── 1. Level Selection Handling (Step 1) ──────────────────────────────────
    const levelCards = document.querySelectorAll('#step1LevelContainer .level-selection-card[data-level]');

    levelCards.forEach(card => {
        const cardLevel = card.getAttribute('data-level');
        if (cardLevel === selectedLevel) {
            card.classList.add('selected');
        } else {
            card.classList.remove('selected');
        }

        card.addEventListener('click', () => {
            levelCards.forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            selectedLevel = card.getAttribute('data-level');

            // Enable next button
            if (btnGotoStep2) {
                btnGotoStep2.disabled = false;
            }

            // Update bottom shelf
            if (shelfLevelLabel) {
                const labelText = LEVEL_NAMES[selectedLevel] || selectedLevel;
                shelfLevelLabel.textContent = `Level Terpilih: ${labelText}`;
            }
            if (shelfFinalLevelBadge) {
                shelfFinalLevelBadge.textContent = `Level ${selectedLevel}`;
            }
        });

        // Double click can quickly advance to daily goal
        card.addEventListener('dblclick', () => {
            goToStep(2);
        });
    });

    // ─── 2. Daily Goal Selection Handling (Step 2) ─────────────────────────────
    const goalCards = document.querySelectorAll('#step2GoalContainer .goal-selection-card[data-goal]');

    goalCards.forEach(card => {
        card.addEventListener('click', () => {
            goalCards.forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            selectedGoal = card.getAttribute('data-goal');

            const info = GOAL_DETAILS[selectedGoal] || { badge: '15 Menit / Hari', label: 'Rekomendasi' };
            if (shelfGoalBadge) shelfGoalBadge.textContent = info.badge;
            if (shelfGoalLabel) shelfGoalLabel.textContent = info.label;
        });

        // Double click can quickly advance to topic
        card.addEventListener('dblclick', () => {
            goToStep(3);
        });
    });

    // ─── 3. Topic Selection Handling (Step 3) ──────────────────────────────────
    const topicCards = document.querySelectorAll('#step3TopicContainer .topic-selection-card[data-topic]');

    topicCards.forEach(card => {
        card.addEventListener('click', () => {
            topicCards.forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            selectedTopic = card.getAttribute('data-topic');
        });
    });

    // ─── 4. Diagnostic Quiz Modal ("Bingung? Cari tahu levelmu disini!") ────────
    const quizModalOverlay = document.getElementById('quizModalOverlay');
    const btnOpenLevelQuiz = document.getElementById('btnOpenLevelQuiz');
    const btnCloseQuizModal = document.getElementById('btnCloseQuizModal');
    const btnCancelQuiz = document.getElementById('btnCancelQuiz');
    const quizForm = document.getElementById('quizForm');

    if (btnOpenLevelQuiz && quizModalOverlay) {
        btnOpenLevelQuiz.addEventListener('click', () => {
            quizModalOverlay.classList.add('active');
        });
    }

    function closeQuizModal() {
        if (quizModalOverlay) quizModalOverlay.classList.remove('active');
    }

    if (btnCloseQuizModal) btnCloseQuizModal.addEventListener('click', closeQuizModal);
    if (btnCancelQuiz) btnCancelQuiz.addEventListener('click', closeQuizModal);

    if (quizModalOverlay) {
        quizModalOverlay.addEventListener('click', (e) => {
            if (e.target === quizModalOverlay) closeQuizModal();
        });
    }

    // Process Mini-Quiz form
    if (quizForm) {
        quizForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const q1Val = document.querySelector('input[name="q1"]:checked')?.value || 'B1';
            const q2Val = document.querySelector('input[name="q2"]:checked')?.value || 'B1';

            let recommended = 'B1';
            if (q1Val === 'B2' && q2Val === 'B2') {
                recommended = 'B2';
            } else if (q1Val === 'B2' || q2Val === 'B2') {
                recommended = 'B2';
            } else {
                recommended = 'B1';
            }

            selectedLevel = recommended;
            levelCards.forEach(c => {
                c.classList.remove('selected');
                if (c.getAttribute('data-level') === recommended) {
                    c.classList.add('selected');
                    c.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            });

            if (shelfLevelLabel) {
                shelfLevelLabel.textContent = `Level Terpilih: ${LEVEL_NAMES[selectedLevel] || selectedLevel}`;
            }
            if (shelfFinalLevelBadge) {
                shelfFinalLevelBadge.textContent = `Level ${selectedLevel}`;
            }

            if (btnGotoStep2) {
                btnGotoStep2.disabled = false;
            }

            closeQuizModal();
        });
    }

    // ─── 5. Launch Pre-Session Briefing ────────────────────────────────────────
    if (btnLaunchPractice) {
        btnLaunchPractice.addEventListener('click', async () => {
            if (!selectedLevel || !selectedTopic) {
                alert('Silakan pilih level dan skenario percakapan terlebih dahulu.');
                return;
            }

            // Disable button during loading
            btnLaunchPractice.disabled = true;
            btnLaunchPractice.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> <span>Menyiapkan Briefing...</span>`;

            try {
                const response = await fetch('/api/v1/session/start', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        cefr_level: selectedLevel,
                        topic: selectedTopic,
                        daily_goal: selectedGoal,
                    })
                });

                if (!response.ok) {
                    const errText = await response.text();
                    throw new Error(`Server returned ${response.status}: ${errText}`);
                }

                const data = await response.json();

                // Persist session state into sessionStorage
                sessionStorage.setItem('milo_session_id', data.session_id);
                sessionStorage.setItem('milo_topic', selectedTopic);
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

                // Smooth transition to Pre-Session Briefing Page
                window.location.href = `/ui/briefing.html?session_id=${encodeURIComponent(data.session_id)}`;
            } catch (error) {
                btnLaunchPractice.disabled = false;
                btnLaunchPractice.innerHTML = `<span>Lanjut ke Pre-Session Briefing</span> <i class="fa-solid fa-arrow-right"></i>`;
                alert('Gagal menyiapkan briefing sesi: ' + error.message);
                console.error('Launch briefing error:', error);
            }
        });
    }
});
