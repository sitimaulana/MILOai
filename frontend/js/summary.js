// ═══════════════════════════════════════════════════════════════════════════════
// MILO AI English Tutor — Summary & Evaluation Logic
// ═══════════════════════════════════════════════════════════════════════════════

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

    // If not cached, fetch via API
    if (!data && sessionId) {
        showGlobalLoading('Loading session feedback...');
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
            'No session evaluation data available. Please complete a practice session first.';
        return;
    }

    // 1. Meta
    const topicLabel = sessionStorage.getItem('milo_topic_label') || 'Speaking Practice';
    const duration = data.duration_minutes || 0;
    const turns = data.total_turns || 0;
    document.getElementById('summaryTopicMeta').textContent = 
        `${topicLabel} • Duration: ${duration} mins • ${turns} Speaking Turns`;

    // 4. Competency Breakdown
    const grammar = Math.round(data.avg_grammar_score || 0);
    const vocab = Math.round(data.avg_vocabulary_score || 0);
    const fluency = Math.round(data.avg_fluency_score || 0);

    // 2. Overall Dial (Circumference of r=52 is 2 * PI * 52 ≈ 327)
    let overallScore = Math.round(data.overall_score || 0);
    if (!overallScore && (grammar || vocab || fluency)) {
        overallScore = Math.round((grammar + vocab + fluency) / 3);
    }
    document.getElementById('summaryOverallScore').textContent = overallScore;
    const circumference = 327;
    const dashLength = (overallScore / 100) * circumference;
    const dial = document.getElementById('summaryOverallDial');
    if (dial) {
        setTimeout(() => {
            dial.style.strokeDasharray = `${dashLength}, ${circumference}`;
        }, 150);
    }

    // 3. CEFR Result
    document.getElementById('summaryCefrTarget').textContent = data.cefr_target || 'B1';
    const resultEl = document.getElementById('summaryCefrResult');
    resultEl.textContent = data.cefr_result || 'B1';
    const vocab = Math.round(data.avg_vocabulary_score || 0);
    const fluency = Math.round(data.avg_fluency_score || 0);

    document.getElementById('summaryGrammarVal').textContent = `${grammar} / 100`;
    document.getElementById('summaryVocabVal').textContent = `${vocab} / 100`;
    document.getElementById('summaryFluencyVal').textContent = `${fluency} / 100`;

    setTimeout(() => {
        document.getElementById('grammarBarFill').style.width = `${grammar}%`;
        document.getElementById('vocabBarFill').style.width = `${vocab}%`;
        document.getElementById('fluencyBarFill').style.width = `${fluency}%`;
    }, 250);

    // 5. Coach Assessment
    document.getElementById('summaryCoachAssessment').textContent = 
        data.session_summary || 'You made remarkable effort in this session. Consistent daily practice will further cement your speaking confidence.';

    // 6. Improvement Areas
    const improvList = document.getElementById('improvementList');
    const improvBox = document.getElementById('improvementBox');
    if (data.improvement_areas && data.improvement_areas.length > 0) {
        improvBox.style.display = 'block';
        improvList.innerHTML = data.improvement_areas.map(item => `<li>${escapeHtml(item)}</li>`).join('');
    }

    // 7. All Corrections
    const corrList = document.getElementById('allCorrectionsList');
    if (data.all_corrections && data.all_corrections.length > 0) {
        corrList.innerHTML = data.all_corrections.map(c => `
            <div class="correction-entry">
                <div class="corr-wrong">✗ ${escapeHtml(c.original)}</div>
                <div class="corr-fix">✓ ${escapeHtml(c.corrected)}</div>
                <div class="corr-explain">${escapeHtml(c.explanation)}</div>
            </div>
        `).join('');
    } else {
        corrList.innerHTML = `
            <div style="text-align: center; color: var(--grammar-color); padding: 16px; font-size: 14px;">
                <i class="fa-solid fa-circle-check" style="margin-right: 6px;"></i> Excellent job! No major grammatical or vocabulary errors recorded.
            </div>
        `;
    }
});
