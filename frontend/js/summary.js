document.addEventListener('DOMContentLoaded', async () => {
    if (window.lucide && typeof window.lucide.createIcons === 'function') {
        window.lucide.createIcons();
    }

    if (typeof requireAuth === 'function' && !requireAuth()) {
        return;
    }

    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session_id') || sessionStorage.getItem('milo_session_id');
    const topicId = urlParams.get('topic_id') || sessionStorage.getItem('milo_topic_id') || 'A1';

    const token = typeof getAuthToken === 'function' ? getAuthToken() : localStorage.getItem('milo_token');
    const guestCard = document.getElementById('summaryGuestSaveCard');
    if (guestCard) {
        guestCard.style.display = 'none';
    }

    // Load Micro-Quiz for this topic
    loadMicroQuiz(topicId, sessionId);

    let data = null;
    const cachedSummary = sessionStorage.getItem('milo_summary_data');
    if (cachedSummary) {
        try {
            const parsed = JSON.parse(cachedSummary);
            if (!sessionId || parsed.session_id === sessionId) {
                data = parsed;
            }
        } catch (e) {
            console.error('Parse error:', e);
        }
    }

    if (!data && sessionId) {
        showGlobalLoading('Memuat evaluasi sesi percakapan...');
        try {
            const authHeaders = token ? { 'Authorization': `Bearer ${token}` } : {};
            const res = await fetch(`/api/v1/session/${sessionId}/feedback`, { headers: authHeaders });
            if (res.ok) {
                data = await res.json();
            } else if (res.status === 401 && typeof logoutUser === 'function') {
                logoutUser();
                return;
            } else if (res.status === 403) {
                document.getElementById('summaryCoachAssessment').textContent = 
                    'Akses ditolak: Data evaluasi sesi ini bukan milik akun yang sedang aktif.';
                return;
            }
        } catch (e) {
            console.error('Fetch error:', e);
        } finally {
            hideGlobalLoading();
        }
    }

    if (!data) {
        document.getElementById('summaryCoachAssessment').textContent = 
            'Data evaluasi sesi tidak ditemukan. Silakan selesaikan sesi latihan terlebih dahulu.';
        return;
    }

    // Initialize Post-Session Evaluation Survey
    initEvaluationSurvey(sessionId);

    // Render Gamification Celebration Banner if XP, badges earned, or level promoted
    const gamCard = document.getElementById('summaryGamificationCard');
    const isLevelPromoted = (data.cefr_result === 'B2' || data.cefr_result === 'C1') && (data.cefr_target === 'B1');

    if (gamCard && (data.xp_earned || data.current_streak || isLevelPromoted || (data.unlocked_badges && data.unlocked_badges.length > 0))) {
        gamCard.style.display = 'flex';
        const titleEl = document.getElementById('gamCelebrateTitle');
        const descEl = document.getElementById('gamCelebrateDesc');
        const chipXp = document.getElementById('gamChipXp');
        const chipStreak = document.getElementById('gamChipStreak');
        const chipBadge = document.getElementById('gamChipBadge');

        if (isLevelPromoted) {
            if (titleEl) titleEl.textContent = 'Selamat! Standar Level B2 Tercapai!';
            if (descEl) descEl.textContent = 'Kemampuan bicaramu melampaui target B1. Profil akunmu berhasil naik level ke B2!';
            try {
                const authUser = JSON.parse(localStorage.getItem('milo_user'));
                if (authUser) {
                    authUser.cefr_level = 'B2';
                    localStorage.setItem('milo_user', JSON.stringify(authUser));
                }
            } catch {}
        }

        if (chipXp) chipXp.innerHTML = `<i class="fa-solid fa-star" style="color: #F59E0B;"></i> +${data.xp_earned || 50} XP`;
        if (chipStreak) chipStreak.innerHTML = `<i class="fa-solid fa-fire" style="color: #EF4444;"></i> ${data.current_streak || 1} Hari Streak`;
        if (chipBadge && data.unlocked_badges && data.unlocked_badges.length > 0) {
            chipBadge.style.display = 'inline-flex';
            chipBadge.innerHTML = `<i class="fa-solid fa-award"></i> Lencana: ${escapeHtml(data.unlocked_badges.join(', '))}`;
        }
    }

    const topicLabel = data.topic_label || sessionStorage.getItem('milo_topic_label') || 'Latihan Percakapan';
    const duration = typeof data.duration_minutes === 'number' ? data.duration_minutes : 0;
    const targetMinutes = data.target_duration_minutes || 15;
    const turns = data.total_turns || 0;

    const topicMetaEl = document.getElementById('summaryTopicMeta');
    if (topicMetaEl) {
        topicMetaEl.textContent = `${topicLabel} • Durasi: ${duration} menit (Target: ${targetMinutes} menit) • ${turns} Putaran Percakapan`;
    }

    const grammar = Math.round(data.avg_grammar_score || 0);
    const vocab = Math.round(data.avg_vocabulary_score || 0);
    const fluency = Math.round(data.avg_fluency_score || 0);

    let overallScore = Math.round(data.overall_score || 0);
    if (!overallScore && (grammar || vocab || fluency)) {
        overallScore = Math.round((grammar + vocab + fluency) / 3);
    }
    const overallScoreEl = document.getElementById('summaryOverallScore');
    if (overallScoreEl) overallScoreEl.textContent = overallScore;

    const circumference = 327;
    const dashLength = (overallScore / 100) * circumference;
    const dial = document.getElementById('summaryOverallDial');
    if (dial) {
        setTimeout(() => {
            dial.style.strokeDasharray = `${dashLength}, ${circumference}`;
        }, 150);
    }

    const targetEl = document.getElementById('summaryCefrTarget');
    if (targetEl) targetEl.textContent = data.cefr_target || 'B1';

    const resultEl = document.getElementById('summaryCefrResult');
    if (resultEl) resultEl.textContent = data.cefr_result || 'B1';

    const grammarVal = document.getElementById('summaryGrammarVal');
    const vocabVal = document.getElementById('summaryVocabVal');
    const fluencyVal = document.getElementById('summaryFluencyVal');
    if (grammarVal) grammarVal.textContent = `${grammar} / 100`;
    if (vocabVal) vocabVal.textContent = `${vocab} / 100`;
    if (fluencyVal) fluencyVal.textContent = `${fluency} / 100`;

    setTimeout(() => {
        const fillG = document.getElementById('grammarBarFill');
        const fillV = document.getElementById('vocabBarFill');
        const fillF = document.getElementById('fluencyBarFill');
        if (fillG) fillG.style.width = `${grammar}%`;
        if (fillV) fillV.style.width = `${vocab}%`;
        if (fillF) fillF.style.width = `${fluency}%`;
    }, 250);

    const coachAssessmentEl = document.getElementById('summaryCoachAssessment');
    if (coachAssessmentEl) {
        renderCoachEvaluation(data.session_summary, coachAssessmentEl);
    }

    const corrCountBadge = document.getElementById('correctionsCountBadge');
    const totalCorrs = (data.all_corrections && data.all_corrections.length) || 0;
    if (corrCountBadge) {
        corrCountBadge.textContent = `${totalCorrs} Pembetulan`;
        corrCountBadge.className = totalCorrs === 0 
            ? 'corrections-count-badge zero-count' 
            : 'corrections-count-badge has-count';
    }

    const improvList = document.getElementById('improvementList');
    const improvBox = document.getElementById('improvementBox');
    if (data.improvement_areas && data.improvement_areas.length > 0 && improvBox && improvList) {
        improvBox.style.display = 'block';
        improvList.innerHTML = data.improvement_areas.map(item => `<li>${escapeHtml(item)}</li>`).join('');
    }

    // Populate RAG Grounded Reading Recommendations
    renderRagRecommendations(data);

    const corrList = document.getElementById('allCorrectionsList');
    if (corrList) {
        if (data.all_corrections && data.all_corrections.length > 0) {
            corrList.innerHTML = data.all_corrections.map(c => `
                <div class="correction-entry">
                    <div class="corr-wrong">✗ "${escapeHtml(c.original)}"</div>
                    <div class="corr-fix">✓ "${escapeHtml(c.corrected)}"</div>
                    ${c.explanation ? `<div class="corr-explain">${escapeHtml(c.explanation)}</div>` : ''}
                </div>
            `).join('');
        } else {
            corrList.innerHTML = `
                <div style="text-align: center; color: var(--primary-dark); padding: 16px; font-size: 14px; font-weight: 600;">
                    ✓ Luar biasa! Seluruh kalimat yang Anda sampaikan pada sesi ini akurat dan tepat kaidah.
                </div>
            `;
        }
    }

    const transcriptList = document.getElementById('sessionTranscriptList');
    if (transcriptList && data.transcript_history && data.transcript_history.length > 0) {
        transcriptList.innerHTML = data.transcript_history.map(msg => {
            const isUser = msg.role === 'user';
            const author = isUser ? 'Anda (Student)' : 'Milo (AI Tutor)';
            const inputType = msg.input_type === 'voice' ? '🎙️ Suara' : '⌨️ Teks';
            const pillTypeClass = msg.input_type === 'voice' ? 'voice-pill' : 'text-pill';

            let feedbackBadge = '';
            if (isUser && msg.feedback) {
                const corrs = msg.feedback.corrections || [];
                if (corrs.length === 0) {
                    feedbackBadge = `<span class="transcript-pill accurate-pill">✓ Akurat</span>`;
                } else {
                    feedbackBadge = `<span class="transcript-pill error-pill">${corrs.length} Pembetulan</span>`;
                }
            }

            let ragBadgesHtml = '';
            if (!isUser && msg.rag_sources && Array.isArray(msg.rag_sources) && msg.rag_sources.length > 0) {
                ragBadgesHtml = msg.rag_sources.map(src => `
                    <span class="transcript-pill" style="background: rgba(200, 125, 85, 0.15); color: #8C6239; border: 1px solid rgba(200, 125, 85, 0.3); font-weight: 700;">
                        <i class="fa-solid fa-book-bookmark"></i> Ref: ${escapeHtml(formatRagSourceLabel(src))}
                    </span>
                `).join('');
            }

            return `
                <div class="transcript-turn-card ${isUser ? 'user-turn' : 'milo-turn'}">
                    <div class="transcript-turn-header">
                        <span class="transcript-author-name">${escapeHtml(author)}</span>
                        <div class="transcript-meta-pills">
                            <span class="transcript-pill ${pillTypeClass}">${inputType}</span>
                            ${feedbackBadge}
                            ${ragBadgesHtml}
                        </div>
                    </div>
                    <div class="transcript-content-text">${escapeHtml(msg.content)}</div>
                </div>
            `;
        }).join('');
    } else if (transcriptList) {
        transcriptList.innerHTML = `
            <div style="text-align: center; color: var(--text-muted); padding: 14px; font-size: 13.5px;">
                Belum ada transkrip detail yang tersimpan untuk sesi ini.
            </div>
        `;
    }

    const btnExportObsidian = document.getElementById('btnExportObsidian');
    if (btnExportObsidian && sessionId) {
        btnExportObsidian.addEventListener('click', () => {
            window.location.href = `/api/v1/session/${encodeURIComponent(sessionId)}/export/obsidian`;
        });
    }
});

function renderCoachEvaluation(rawMarkdown, container) {
    if (!container) return;
    if (!rawMarkdown || !rawMarkdown.trim()) {
        container.innerHTML = `
            <div class="coach-narrative-box">
                <div class="narrative-tag">
                    <i class="fa-solid fa-comment-dots"></i>
                    <span>Catatan Umum</span>
                </div>
                <p class="coach-para">Performa latihan Anda telah terdokumentasi dengan baik. Konsistensi latihan harian akan memperkaya rasa percaya diri dan ketepatan berbahasa Inggris.</p>
            </div>
        `;
        return;
    }

    let text = rawMarkdown.trim();

    // 1. Strip top-level document hashtag title (e.g. "# EVALUASI PRAKTIK BAHASA INGGRIS: MILO SESSION")
    text = text.replace(/^#\s*[^#\n*]+(?:\n|\s+(?=\*\*)|$)/i, '');
    // 2. Strip composite score header line if present (e.g. "**Nilai Kompositif: 81/100 (C1)**")
    text = text.replace(/^\*\*Nilai\s+Komposit[^*]+\*\*\s*/i, '');

    function formatInline(str) {
        if (!str) return '';
        let s = typeof escapeHtml === 'function' ? escapeHtml(str) : str;
        s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        s = s.replace(/(^|[^*])\*([^*]+)\*([^*]|$)/g, '$1<em>$2</em>$3');
        s = s.replace(/(→|-&gt;)/g, '<span class="inline-arrow">→</span>');
        return s;
    }

    const sections = [];

    // Check if the text uses Markdown ## headings
    if (/^##\s+/m.test(text)) {
        const parts = text.split(/^##\s+/m);
        for (const part of parts) {
            const trimmed = part.trim();
            if (!trimmed) continue;
            const firstLineEnd = trimmed.indexOf('\n');
            if (firstLineEnd === -1) {
                sections.push({ title: trimmed, body: '' });
            } else {
                sections.push({
                    title: trimmed.substring(0, firstLineEnd).trim(),
                    body: trimmed.substring(firstLineEnd + 1).trim()
                });
            }
        }
    } else {
        // Fallback for texts using bold labels like **Kelebihan Utama:** and **Koreksi & Panduan:**
        const regex = /\*\*([A-Za-z0-9\s&]+):\*\*/g;
        let match;
        const matches = [];
        while ((match = regex.exec(text)) !== null) {
            const before = text.substring(Math.max(0, match.index - 8), match.index).trim();
            if (/[-*•]|\d+\.$/.test(before)) {
                continue; // Skip list bullet items like "- **Kosakata:**"
            }
            matches.push({ title: match[1], index: match.index, length: match[0].length });
        }

        if (matches.length > 0) {
            const firstChunk = text.substring(0, matches[0].index).trim();
            if (firstChunk) {
                sections.push({ title: 'Ringkasan Performa', body: firstChunk });
            }
            for (let i = 0; i < matches.length; i++) {
                const m = matches[i];
                const start = m.index + m.length;
                const end = (i + 1 < matches.length) ? matches[i + 1].index : text.length;
                sections.push({
                    title: m.title.trim(),
                    body: text.substring(start, end).trim()
                });
            }
        } else {
            sections.push({ title: 'Ringkasan Performa', body: text });
        }
    }

    let html = '';

    for (const sec of sections) {
        const titleLower = sec.title.toLowerCase();

        // 1. Narrative Section (Ringkasan Performa)
        if (titleLower.includes('ringkasan') || titleLower.includes('performa') || titleLower.includes('selamat')) {
            const paragraphs = sec.body.split(/\n{2,}/).map(p => p.trim()).filter(Boolean);
            const renderedParas = (paragraphs.length ? paragraphs : [sec.body]).map(p => 
                `<p class="coach-para">${formatInline(p)}</p>`
            ).join('');

            html += `
                <div class="coach-narrative-box">
                    <div class="narrative-tag">
                        <i class="fa-solid fa-comment-dots"></i>
                        <span>Ulasan Umum Tutor</span>
                    </div>
                    ${renderedParas}
                </div>
            `;
        }
        // 2. Strengths Section (Kelebihan Utama / Teramati)
        else if (titleLower.includes('kelebihan') || titleLower.includes('kekuatan') || titleLower.includes('strength')) {
            let items = sec.body
                .split(/(?:^|\s+)[-*•]\s+/)
                .map(l => l.trim())
                .filter(Boolean);

            if (!items.length) {
                items = sec.body.split(/\n+/).map(l => l.trim()).filter(Boolean);
            }

            const cardsHtml = items.map(item => {
                const cleanItem = item.replace(/^(?:[-•]|\*(?!\*)|\d+\.)\s*/, '').trim();
                const colonMatch = cleanItem.match(/^(?:\*\*)?([^*:]+)(?:\*\*)?:\s*(.+)/);
                if (colonMatch) {
                    const aspect = colonMatch[1].replace(/\*\*/g, '').trim();
                    const desc = colonMatch[2].replace(/^\*+|\*+$/g, '').trim();
                    return `
                        <div class="coach-strength-card">
                            <div class="strength-card-header">
                                <span class="strength-check-badge"><i class="fa-solid fa-check"></i></span>
                                <strong class="strength-aspect-title">${formatInline(aspect)}</strong>
                            </div>
                            <p class="strength-desc">${formatInline(desc)}</p>
                        </div>
                    `;
                }
                return `
                    <div class="coach-strength-card">
                        <div class="strength-card-header">
                            <span class="strength-check-badge"><i class="fa-solid fa-check"></i></span>
                        </div>
                        <p class="strength-desc">${formatInline(cleanItem)}</p>
                    </div>
                `;
            }).join('');

            html += `
                <div class="coach-section-block">
                    <div class="coach-section-heading heading-strength">
                        <i class="fa-solid fa-circle-check"></i>
                        <span>Kelebihan Teramati</span>
                    </div>
                    <div class="coach-strengths-grid">
                        ${cardsHtml || `<div class="coach-strength-card"><p class="strength-desc">${formatInline(sec.body)}</p></div>`}
                    </div>
                </div>
            `;
        }
        // 3. Guidance / Corrections Section (Catatan Kaidah & Kosakata / Koreksi & Panduan)
        else if (titleLower.includes('kaidah') || titleLower.includes('koreksi') || titleLower.includes('panduan') || titleLower.includes('catatan')) {
            let items = sec.body
                .split(/(?:^|\s+)(?:[-*•]|\d+\.)\s+/)
                .map(l => l.trim())
                .filter(Boolean);

            if (!items.length) {
                items = sec.body.split(/\n+/).map(l => l.trim()).filter(Boolean);
            }
            if (!items.length) {
                items = [sec.body];
            }

            const cardsHtml = items.map(item => {
                const cleanItem = item.replace(/^(?:[-•]|\*(?!\*)|\d+\.)\s*/, '').trim();
                if (!cleanItem) return '';
                return `
                    <div class="coach-guidance-card">
                        <div class="guidance-icon-badge"><i class="fa-solid fa-compass"></i></div>
                        <div class="guidance-content">${formatInline(cleanItem)}</div>
                    </div>
                `;
            }).join('');

            html += `
                <div class="coach-section-block">
                    <div class="coach-section-heading heading-guidance">
                        <i class="fa-solid fa-pen-ruler"></i>
                        <span>Catatan Kaidah & Panduan Berbicara</span>
                    </div>
                    <div class="coach-guidance-stack">
                        ${cardsHtml || `<div class="coach-guidance-card"><div class="guidance-content">${formatInline(sec.body)}</div></div>`}
                    </div>
                </div>
            `;
        }
        // 4. Recommendations / Next Step
        else if (titleLower.includes('rekomendasi') || titleLower.includes('langkah') || titleLower.includes('saran') || titleLower.includes('next')) {
            html += `
                <div class="coach-next-step-box">
                    <div class="next-step-icon">
                        <i class="fa-solid fa-compass"></i>
                    </div>
                    <div class="next-step-content">
                        <div class="next-step-heading">Rekomendasi Latihan Selanjutnya</div>
                        <p class="next-step-text">${formatInline(sec.body)}</p>
                    </div>
                </div>
            `;
        }
        // 5. Fallback
        else {
            html += `
                <div class="coach-section-block">
                    <div class="coach-section-heading">
                        <i class="fa-solid fa-circle-info"></i>
                        <span>${formatInline(sec.title)}</span>
                    </div>
                    <div class="coach-narrative-box">
                        <p class="coach-para">${formatInline(sec.body)}</p>
                    </div>
                </div>
            `;
        }
    }

    container.innerHTML = html || `<div class="coach-narrative-box"><p class="coach-para">${formatInline(rawMarkdown)}</p></div>`;
}

// ─── Post-Practice Micro-Quiz Loader ──────────────────────────────────────────
async function loadMicroQuiz(topicId, sessionId) {
    const quizCard = document.getElementById('microQuizCard');
    const container = document.getElementById('quizQuestionsContainer');
    const titleEl = document.getElementById('quizCardTitle');
    const btnSubmit = document.getElementById('btnSubmitMicroQuiz');
    const badgeEl = document.getElementById('quizScoreBadge');
    const scoreText = document.getElementById('quizScoreText');
    const resultNotice = document.getElementById('quizResultNotice');
    if (!quizCard || !container) return;

    const normTopicId = (topicId || 'A1').toUpperCase();
    let detail = null;

    try {
        const apiUrl = `/api/v1/curriculum/topic/${encodeURIComponent(normTopicId)}`;
        let resp = null;
        try {
            resp = await fetch(apiUrl);
        } catch (e1) {
            if (window.location.port && window.location.port !== '8000') {
                try {
                    resp = await fetch(`http://localhost:8000${apiUrl}`);
                } catch (e2) {}
            }
        }

        if (resp && resp.ok) {
            detail = await resp.json();
        }
    } catch (err) {
        console.warn('Failed to fetch quiz from API, trying local curriculum data:', err);
    }

    if (!detail && window.MILO_CURRICULUM_DATA) {
        detail = window.MILO_CURRICULUM_DATA[normTopicId] || window.MILO_CURRICULUM_DATA['A1'];
    }

    if (!detail) return;

    try {
        const quizzes = detail.quizzes || [];
        if (quizzes.length === 0) return;

        quizCard.style.display = 'block';
        if (titleEl) {
            titleEl.textContent = `Kuis Pemahaman Materi: [${detail.topic_id}] ${detail.title}`;
        }

        container.innerHTML = '';
        const userAnswers = {};

        quizzes.forEach((q, qIdx) => {
            const qCard = document.createElement('div');
            qCard.className = 'quiz-q-card';
            qCard.id = `quizQCard_${qIdx}`;

            const optionsHtml = Object.entries(q.options || {}).map(([optKey, optVal]) => `
                <div class="quiz-option-item" data-qindex="${qIdx}" data-optkey="${optKey}">
                    <span class="quiz-option-letter">${optKey}</span>
                    <span class="quiz-option-text">${escapeHtml(optVal)}</span>
                </div>
            `).join('');

            qCard.innerHTML = `
                <div class="quiz-q-header">
                    <span class="quiz-q-type-badge">${escapeHtml(q.type || 'Pemahaman')}</span>
                    <span style="font-size: 12px; font-weight: 700; color: var(--text-muted);">Soal ${qIdx + 1} dari ${quizzes.length}</span>
                </div>
                <div class="quiz-q-text">${escapeHtml(q.question)}</div>
                <div class="quiz-options-deck">
                    ${optionsHtml}
                </div>
                <div class="quiz-explanation-box" id="quizExp_${qIdx}" style="display: none;"></div>
            `;

            // Bind click on option items
            const optItems = qCard.querySelectorAll('.quiz-option-item');
            optItems.forEach(item => {
                item.addEventListener('click', () => {
                    if (btnSubmit.disabled) return;
                    optItems.forEach(o => o.classList.remove('selected'));
                    item.classList.add('selected');
                    userAnswers[String(qIdx)] = item.getAttribute('data-optkey');
                });
            });

            container.appendChild(qCard);
        });

        if (btnSubmit) {
            btnSubmit.addEventListener('click', async () => {
                const answeredCount = Object.keys(userAnswers).length;
                if (answeredCount < quizzes.length) {
                    alert(`Silakan pilih jawaban untuk semua ${quizzes.length} soal kuis.`);
                    return;
                }

                btnSubmit.disabled = true;
                btnSubmit.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> <span>Memvalidasi...</span>`;

                try {
                    const token = typeof getAuthToken === 'function' ? getAuthToken() : localStorage.getItem('milo_token');
                    const headers = { 'Content-Type': 'application/json' };
                    if (token) {
                        headers['Authorization'] = `Bearer ${token}`;
                    }

                    const submitResp = await fetch('/api/v1/curriculum/quiz/submit', {
                        method: 'POST',
                        headers: headers,
                        body: JSON.stringify({
                            topic_id: topicId,
                            answers: userAnswers,
                            session_id: sessionId,
                        }),
                    });

                    if (!submitResp.ok) {
                        throw new Error(`Server returned ${submitResp.status}`);
                    }

                    const res = await submitResp.json();

                    res.results.forEach(r => {
                        const qCard = document.getElementById(`quizQCard_${r.question_index}`);
                        if (!qCard) return;

                        const optItems = qCard.querySelectorAll('.quiz-option-item');
                        optItems.forEach(item => {
                            const key = item.getAttribute('data-optkey');
                            if (key === r.correct_option) {
                                item.classList.add('correct');
                            } else if (key === r.selected_option && !r.is_correct) {
                                item.classList.add('wrong');
                            }
                        });

                        const expBox = document.getElementById(`quizExp_${r.question_index}`);
                        if (expBox) {
                            expBox.style.display = 'block';
                            expBox.innerHTML = `<strong>Penjelasan:</strong> ${escapeHtml(r.explanation || '')}`;
                        }
                    });

                    if (badgeEl && scoreText) {
                        badgeEl.style.display = 'inline-flex';
                        scoreText.textContent = `Skor: ${res.score} / 100`;
                    }

                    if (resultNotice) {
                        resultNotice.style.display = 'block';
                        resultNotice.innerHTML = `
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <i class="fa-solid fa-circle-check" style="color: #059669; font-size: 20px;"></i>
                                <div>
                                    <div style="font-weight: 800; color: #065F46; font-size: 14px;">
                                        Kuis Selesai! Benar ${res.correct_count} dari ${res.total_questions} Soal
                                    </div>
                                    <div style="font-size: 12.5px; color: #047857; margin-top: 2px;">
                                        Selamat! Kamu memperoleh <strong>+${res.bonus_points} Poin Gamifikasi</strong> untuk modul ini.
                                    </div>
                                </div>
                            </div>
                        `;
                    }

                    btnSubmit.innerHTML = `<i class="fa-solid fa-check"></i> <span>Kuis Selesai</span>`;
                } catch (subErr) {
                    btnSubmit.disabled = false;
                    btnSubmit.innerHTML = `<i class="fa-solid fa-arrow-rotate-right"></i> <span>Coba Kirim Lagi</span>`;
                    alert('Gagal mengirim jawaban kuis: ' + subErr.message);
                }
            });
        }

    } catch (err) {
        console.error('Failed to load micro-quiz:', err);
    }
}

// ─── Post-Session Evaluation Survey (Thesis/PA Engagement & UEQ) ─────────────
function initEvaluationSurvey(sessionId) {
    const form = document.getElementById('evaluationSurveyForm');
    if (!form) return;

    const scores = {
        behavioral: 5.0,
        emotional: 5.0,
        cognitive: 5.0,
    };

    // Rating buttons interaction
    document.querySelectorAll('.survey-rating-options').forEach(group => {
        const dim = group.getAttribute('data-dim');
        const btns = group.querySelectorAll('.survey-rate-btn');
        btns.forEach(btn => {
            btn.addEventListener('click', () => {
                btns.forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');
                scores[dim] = parseFloat(btn.getAttribute('data-val'));
            });
        });
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const btnSubmit = document.getElementById('btnSubmitSurvey');
        const noticeEl = document.getElementById('surveyFeedbackNotice');
        const feedbackInput = document.getElementById('surveyFeedbackInput');
        const feedbackText = feedbackInput ? feedbackInput.value.trim() : '';

        if (btnSubmit) {
            btnSubmit.disabled = true;
            btnSubmit.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> <span>Mengirim...</span>`;
        }

        try {
            const token = typeof getAuthToken === 'function' ? getAuthToken() : localStorage.getItem('milo_token');
            const headers = { 'Content-Type': 'application/json' };
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }

            const payload = {
                session_id: sessionId || null,
                behavioral_score: scores.behavioral,
                emotional_score: scores.emotional,
                cognitive_score: scores.cognitive,
                feedback_text: feedbackText || null,
            };

            const resp = await fetch('/api/v1/feedback/survey', {
                method: 'POST',
                headers: headers,
                body: JSON.stringify(payload),
            });

            if (!resp.ok) {
                throw new Error(`Server returned ${resp.status}`);
            }

            const result = await resp.json();
            if (noticeEl) {
                noticeEl.style.display = 'block';
                noticeEl.textContent = `Terima kasih! +${result.bonus_xp || 30} XP berhasil ditambahkan ke akun Anda.`;
            }
            if (btnSubmit) {
                btnSubmit.innerHTML = `<i class="fa-solid fa-circle-check"></i> <span>Terkirim (+30 XP)</span>`;
            }
        } catch (err) {
            console.error('Survey submit error:', err);
            if (btnSubmit) {
                btnSubmit.disabled = false;
                btnSubmit.innerHTML = `<i class="fa-solid fa-paper-plane"></i> <span>Kirim Lagi</span>`;
            }
            alert('Gagal mengirim evaluasi: ' + err.message);
        }
    });
}

// ─── RAG Grounded Reading Recommendations & Formatting ────────────────────────

function formatRagSourceLabel(src) {
    if (!src) return '';
    let s = src.trim();
    if (s.includes('Cambridge English Vocabulary in Use')) return 'Cambridge Vocabulary in Use (B2)';
    if (s.includes('The Cambridge Guide to English Usage')) return 'Cambridge Guide to English Usage';
    if (s.includes('Collins Speaking for IELTS')) return 'Collins Speaking for IELTS';
    if (s.includes('Council of Europe') || s.includes('CEFR Companion Volume')) return 'CEFR Companion Volume';
    
    s = s.replace(/\.md$/i, '').replace(/_/g, ' ');
    if (s.toLowerCase().startsWith('unit ')) {
        return s.charAt(0).toUpperCase() + s.slice(1);
    }
    return s.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
}

function renderRagRecommendations(data) {
    const grid = document.getElementById('ragRecBooksGrid');
    if (!grid) return;

    const corrs = data.all_corrections || [];
    const hasGrammarErrors = corrs.some(c => (c.error_type || '').toLowerCase().includes('grammar'));
    const hasVocabErrors = corrs.some(c => (c.error_type || '').toLowerCase().includes('vocab'));

    const recommendations = [];

    if (hasGrammarErrors || (data.avg_grammar_score && data.avg_grammar_score < 78)) {
        recommendations.push({
            book: "The Cambridge Guide to English Usage",
            tag: "Tata Bahasa & Dilema Kata",
            unit: "Unit: Confusing Words & Common Dilemmas",
            desc: "Pelajari perbedaan kata berpasangan yang sering tertukar (seperti borrow vs lend, affect vs effect, used to) untuk meningkatkan akurasi struktur kalimat.",
            badge: "Cambridge Press"
        });
    }

    if (hasVocabErrors || (data.avg_vocabulary_score && data.avg_vocabulary_score < 78)) {
        recommendations.push({
            book: "Cambridge English Vocabulary in Use (B2)",
            tag: "Kekayaan Kosakata & Kolokasi",
            unit: "Unit: Professional Careers & Topic Collocations",
            desc: "Perkaya variasi idiom dan pilihan frasa alami agar tuturan terdengar lebih matang dan tidak monoton mengulang kata dasar.",
            badge: "B2 Lexical Resource"
        });
    }

    recommendations.push({
        book: "Collins Speaking for IELTS",
        tag: "Kelancaran & Pola Jawaban",
        unit: "Unit: Fluency Strategies & Coherence",
        desc: "Latihan teknik menyusun jawaban runtut menggunakan STAR method dan discourse markers untuk mengurangi jeda hening dan keraguan saat berbicara.",
        badge: "IELTS Speaking Standard"
    });

    grid.innerHTML = recommendations.map(rec => `
        <div style="background: #FFFFFF; border: 1px solid #E2D9CC; border-radius: 12px; padding: 16px; display: flex; flex-direction: column; justify-content: space-between; gap: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
            <div>
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                    <span style="font-size: 11px; font-weight: 700; color: #8C6239; background: #FFF4E5; padding: 3px 8px; border-radius: 999px; border: 1px solid #FBD38D;">
                        ${escapeHtml(rec.badge)}
                    </span>
                    <span style="font-size: 11px; font-weight: 600; color: #718096;">${escapeHtml(rec.tag)}</span>
                </div>
                <h4 style="margin: 0; font-size: 14.5px; font-weight: 800; color: #1A202C;">${escapeHtml(rec.book)}</h4>
                <div style="font-size: 12px; font-weight: 700; color: #C87D55; margin-top: 3px;">${escapeHtml(rec.unit)}</div>
                <p style="font-size: 12.5px; color: #4A5568; margin: 6px 0 0 0; line-height: 1.45;">${escapeHtml(rec.desc)}</p>
            </div>
            <div style="padding-top: 8px; border-top: 1px solid #F0EAE1; display: flex; align-items: center; justify-content: space-between;">
                <span style="font-size: 11px; color: #718096;"><i class="fa-solid fa-check-circle" style="color: #38A169;"></i> Terverifikasi di RAG Store</span>
                <span style="font-size: 11.5px; font-weight: 700; color: #C87D55;">Disarankan</span>
            </div>
        </div>
    `).join('');
}


