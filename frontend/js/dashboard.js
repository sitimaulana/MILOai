// ═══════════════════════════════════════════════════════════════════════════════
// MILO AI English Tutor: Dashboard Logic (Warm Sand Cohesive Theme)
// ═══════════════════════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', async () => {
    await fetchDashboardMetrics();
});

async function fetchDashboardMetrics() {
    const container = document.getElementById('historySessionsContainer');
    const badge = document.getElementById('sessionCountBadge');

    try {
        const response = await fetch('/api/v1/dashboard');
        if (!response.ok) {
            throw new Error(`Dashboard API error: ${response.status}`);
        }

        const data = await response.json();

        // 1. Top Metrics Summary
        const total = data.total_sessions || 0;
        const overall = Math.round(data.avg_overall_score || 0);
        const grammar = Math.round(data.skill_averages?.grammar || 0);
        const vocab = Math.round(data.skill_averages?.vocabulary || 0);
        const fluency = Math.round(data.skill_averages?.fluency || 0);

        const elTotal = document.getElementById('statTotalSessions');
        const elOverall = document.getElementById('statOverallScore');
        const elGrammar = document.getElementById('statGrammarScore');
        const elVocab = document.getElementById('statVocabScore');
        const elFluency = document.getElementById('statFluencyScore');

        if (elTotal) elTotal.textContent = total;
        if (elOverall) elOverall.textContent = overall;
        if (elGrammar) elGrammar.textContent = grammar;
        if (elVocab) elVocab.textContent = vocab;
        if (elFluency) elFluency.textContent = fluency;

        // 2. Recent Sessions List
        const sessions = data.recent_sessions || [];
        if (badge) {
            badge.textContent = `${sessions.length} Sesi Terakhir`;
        }

        if (sessions.length === 0) {
            container.innerHTML = `
                <div class="empty-history-box">
                    <div class="empty-history-title">Belum ada riwayat latihan</div>
                    <p class="empty-history-desc">
                        Mulai percakapan pertamamu bersama MILO untuk memantau kelancaran, akurasi grammar, dan evaluasi CEFR.
                    </p>
                    <a href="/ui/setup.html" class="btn-dash-primary" style="font-size: 13.5px; padding: 10px 22px;">
                        Mulai Sesi Pertama
                    </a>
                </div>
            `;
            return;
        }

        const topicLabelsIndo = {
            job_interview: 'Simulasi Wawancara Kerja',
            academic_discussion: 'Diskusi Akademik & Presentasi',
            daily_conversation: 'Percakapan Sehari-hari'
        };

        container.innerHTML = sessions.map(s => {
            const displayTitle = topicLabelsIndo[s.topic] || s.topic_label || 'Latihan Percakapan';
            
            const dateStr = s.created_at ? new Date(s.created_at).toLocaleDateString('id-ID', {
                day: 'numeric',
                month: 'short',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            }) : 'Sesi Terkini';

            const score = Math.round(s.overall_score || 0);
            const duration = s.duration_minutes || 0;
            const cefrLevel = s.cefr_result || s.cefr_level || 'B1';

            return `
                <div class="history-item-row">
                    <div class="history-item-left">
                        <div>
                            <div class="history-topic-name">${escapeHtml(displayTitle)}</div>
                            <div class="history-meta-date">
                                <span>${dateStr}</span>
                                <span>&bull;</span>
                                <span>${duration} menit</span>
                            </div>
                        </div>
                    </div>
                    <div class="history-item-right">
                        <div class="history-score-pill" title="Skor Keseluruhan">
                            <span>${score}</span>
                            <span style="font-size: 11px; opacity: 0.75; font-weight: 600;">/100</span>
                        </div>
                        <span class="history-cefr-pill" title="Level CEFR">Level ${escapeHtml(cefrLevel)}</span>
                        <a href="/ui/summary.html?session_id=${encodeURIComponent(s.session_id)}" class="btn-view-summary">
                            <span>Detail</span>
                            <i class="fa-solid fa-chevron-right" style="font-size: 11px;"></i>
                        </a>
                    </div>
                </div>
            `;
        }).join('');

    } catch (err) {
        console.error('Dashboard load failed:', err);
        container.innerHTML = `
            <div style="text-align: center; color: #EF4444; padding: 36px 20px;">
                <i class="fa-solid fa-triangle-exclamation" style="font-size: 28px; margin-bottom: 8px;"></i>
                <p style="font-weight: 700;">Gagal memuat data dashboard: ${escapeHtml(err.message)}</p>
            </div>
        `;
    }
}
