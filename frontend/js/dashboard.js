// ═══════════════════════════════════════════════════════════════════════════════
// MILO AI English Tutor — Dashboard Logic
// ═══════════════════════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', async () => {
    await fetchDashboardMetrics();
});

async function fetchDashboardMetrics() {
    const container = document.getElementById('historySessionsContainer');

    try {
        const response = await fetch('/api/v1/dashboard');
        if (!response.ok) {
            throw new Error(`Dashboard API error: ${response.status}`);
        }

        const data = await response.json();

        // 1. Top Metrics
        document.getElementById('statTotalSessions').textContent = data.total_sessions || 0;
        document.getElementById('statOverallScore').textContent = Math.round(data.avg_overall_score || 0);
        document.getElementById('statGrammarScore').textContent = Math.round(data.skill_averages?.grammar || 0);
        document.getElementById('statVocabScore').textContent = Math.round(data.skill_averages?.vocabulary || 0);

        // 2. Recent Sessions List
        const sessions = data.recent_sessions || [];
        if (sessions.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 48px 20px; color: var(--text-subtle);">
                    <i class="fa-solid fa-folder-open" style="font-size: 38px; margin-bottom: 14px; opacity: 0.5;"></i>
                    <h4 style="font-size: 16px; color: var(--text-muted); margin-bottom: 8px;">No sessions recorded yet</h4>
                    <p style="font-size: 13px; margin-bottom: 20px;">Begin speaking with MILO to start tracking your progress.</p>
                    <a href="/ui/setup.html" class="btn-primary" style="padding: 10px 24px; font-size: 13px;">
                        <i class="fa-solid fa-play"></i> Start Your First Session
                    </a>
                </div>
            `;
            return;
        }

        const topicIcons = {
            job_interview: 'fa-briefcase',
            academic_discussion: 'fa-graduation-cap',
            daily_conversation: 'fa-comments'
        };

        container.innerHTML = sessions.map(s => {
            const iconClass = topicIcons[s.topic] || 'fa-comments';
            const dateStr = s.created_at ? new Date(s.created_at).toLocaleDateString('id-ID', {
                day: 'numeric',
                month: 'short',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            }) : 'Recent';

            const score = Math.round(s.overall_score || 0);
            const duration = s.duration_minutes || 0;

            return `
                <div class="history-item-row">
                    <div class="history-item-icon ${escapeHtml(s.topic)}">
                        <i class="fa-solid ${iconClass}"></i>
                    </div>
                    <div>
                        <div class="history-topic-name">${escapeHtml(s.topic_label)}</div>
                        <div class="history-meta-date">${dateStr} &bull; ${duration} mins</div>
                    </div>
                    <div class="history-score-pill">
                        ${score} <span style="font-size: 11px; color: var(--text-muted); font-weight: 500;">/100</span>
                    </div>
                    <div>
                        <span class="history-cefr-pill">${escapeHtml(s.cefr_result || s.cefr_level || 'B1')}</span>
                    </div>
                </div>
            `;
        }).join('');

    } catch (err) {
        console.error('Dashboard load failed:', err);
        container.innerHTML = `
            <div style="text-align: center; color: var(--error-color); padding: 30px;">
                <p>Failed to load dashboard data: ${escapeHtml(err.message)}</p>
            </div>
        `;
    }
}
