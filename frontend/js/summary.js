document.addEventListener('DOMContentLoaded', async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session_id') || sessionStorage.getItem('milo_session_id');

    let data = null;
    const cachedSummary = sessionStorage.getItem('milo_summary_data');
    if (cachedSummary) {
        try {
            data = JSON.parse(cachedSummary);
        } catch (e) {
            console.error('Parse error:', e);
        }
    }

    if (!data && sessionId) {
        showGlobalLoading('Memuat evaluasi sesi percakapan...');
        try {
            const res = await fetch(`/api/v1/session/${sessionId}/feedback`);
            if (res.ok) {
                data = await res.json();
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

            return `
                <div class="transcript-turn-card ${isUser ? 'user-turn' : 'milo-turn'}">
                    <div class="transcript-turn-header">
                        <span class="transcript-author-name">${escapeHtml(author)}</span>
                        <div class="transcript-meta-pills">
                            <span class="transcript-pill ${pillTypeClass}">${inputType}</span>
                            ${feedbackBadge}
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
