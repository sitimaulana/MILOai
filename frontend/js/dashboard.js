// MILO AI English Tutor: Dashboard metrics and session history logic.

document.addEventListener('DOMContentLoaded', async () => {
    await fetchDashboardMetrics();
    await fetchKnowledgeBaseSummary();
});

async function fetchDashboardMetrics() {
    if (typeof requireAuth === 'function' && !requireAuth()) {
        return;
    }

    const container = document.getElementById('historySessionsContainer');
    const badge = document.getElementById('sessionCountBadge');

    try {
        const token = typeof getAuthToken === 'function' ? getAuthToken() : localStorage.getItem('milo_token');
        const user = typeof getAuthUser === 'function' ? getAuthUser() : null;

        const guestPrompt = document.getElementById('guestAuthPrompt');
        if (guestPrompt) guestPrompt.style.display = 'none';

        const subtitleElem = document.getElementById('dashSubtitleText');
        if (subtitleElem && user) {
            const displayName = user.full_name || user.username;
            subtitleElem.textContent = `Halo, ${displayName}! Pantau peningkatan kompetensi Grammar, Vocabulary, dan Fluency dari setiap sesi percakapan Anda bersama MILO.`;
        }

        const response = typeof miloFetch === 'function' 
            ? await miloFetch('/api/v1/dashboard')
            : await fetch('/api/v1/dashboard', {
                headers: token ? { 'Authorization': `Bearer ${token}` } : {}
            });

        if (!response.ok) {
            if (response.status === 401 && typeof logoutUser === 'function') {
                logoutUser();
                return;
            }
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

        // 1b. Check Placement Baseline Score
        try {
            const placementResp = await fetch('/api/v1/curriculum/placement/history', {
                headers: token ? { 'Authorization': `Bearer ${token}` } : {}
            });
            if (placementResp.ok) {
                const historyData = await placementResp.json();
                if (Array.isArray(historyData) && historyData.length > 0) {
                    const latest = historyData[0];
                    const placementPill = document.getElementById('dashPlacementText');
                    if (placementPill) {
                        placementPill.textContent = `Baseline: ${Math.round(latest.score_percentage)}% (${latest.selected_level})`;
                    }
                    const cefrDesc = document.getElementById('cefrTrackDescText');
                    if (cefrDesc) {
                        cefrDesc.textContent = `Level aktif Anda: Level ${latest.selected_level} (Skor Tes Awal: ${Math.round(latest.score_percentage)}%).`;
                    }
                }
            }
        } catch {}

        // 2. Gamification & Badges
        const gamSection = document.getElementById('gamificationSection');
        if (data.gamification) {
            const gam = data.gamification;
            if (gamSection) gamSection.style.display = 'flex';
            
            const elPoints = document.getElementById('gamPointsVal');
            const elStreak = document.getElementById('gamStreakVal');
            const elHighest = document.getElementById('gamHighestStreakVal');
            if (elPoints) elPoints.textContent = `${gam.points || 0} XP`;
            if (elStreak) elStreak.textContent = `${gam.current_streak || 0} Hari Streak`;
            if (elHighest) elHighest.textContent = `Rekor: ${gam.highest_streak || 0} Hari`;

            const badgesContainer = document.getElementById('badgesContainer');
            if (badgesContainer && Array.isArray(gam.badges)) {
                if (gam.badges.length > 0) {
                    const badgeIcons = {
                        first_step: 'fa-shoe-prints',
                        streak_3: 'fa-fire',
                        streak_7: 'fa-crown',
                        grammar_master: 'fa-spell-check',
                        fluency_star: 'fa-microphone-lines',
                        cefr_b2_achieved: 'fa-award',
                    };
                    badgesContainer.innerHTML = gam.badges.map(b => {
                        const iconClass = badgeIcons[b.badge_key] || 'fa-medal';
                        const earnedDate = b.earned_at ? new Date(b.earned_at).toLocaleDateString('id-ID', {
                            day: 'numeric',
                            month: 'short',
                            year: 'numeric'
                        }) : 'Telah diperoleh';
                        return `
                            <div class="badge-item-chip">
                                <div class="badge-item-icon">
                                    <i class="fa-solid ${iconClass}"></i>
                                </div>
                                <div class="badge-item-info">
                                    <span class="badge-item-name">${escapeHtml(b.badge_title)}</span>
                                    <span class="badge-item-date">${earnedDate}</span>
                                </div>
                            </div>
                        `;
                    }).join('');
                } else {
                    badgesContainer.innerHTML = `<p class="badge-empty-note">Selesaikan sesi latihan atau kuis pertama untuk membuka lencana pertama Anda!</p>`;
                }
            }
        } else if (gamSection) {
            gamSection.style.display = 'none';
        }

        // 3. Skill Progress Breakdown
        const skillSection = document.getElementById('skillProgressSection');
        const skillContainer = document.getElementById('skillProgressContainer');
        if (skillSection && skillContainer && Array.isArray(data.skill_progress) && data.skill_progress.length > 0) {
            skillSection.style.display = 'block';
            const skillNamesIndo = {
                grammar: 'Tata Bahasa (Grammar)',
                vocabulary: 'Kosakata (Vocabulary)',
                fluency: 'Kelancaran (Fluency)',
            };
            skillContainer.innerHTML = data.skill_progress.map(sp => {
                const name = skillNamesIndo[sp.skill.toLowerCase()] || sp.skill;
                return `
                    <div class="skill-prog-card">
                        <div class="skill-prog-header">
                            <span class="skill-prog-name">${escapeHtml(name)}</span>
                            <span class="skill-prog-score">${Math.round(sp.score || 0)}/100</span>
                        </div>
                        <div class="skill-prog-meta">
                            <span><i class="fa-solid fa-layer-group" style="margin-right: 4px; color: var(--text-muted);"></i> ${sp.sessions_count || 0} sesi</span>
                            <span>&bull;</span>
                            <span><i class="fa-solid fa-circle-check" style="margin-right: 4px; color: var(--primary);"></i> ${sp.total_corrections || 0} catatan</span>
                        </div>
                    </div>
                `;
            }).join('');
        } else if (skillSection) {
            skillSection.style.display = 'none';
        }

        // 4. Recent Sessions List
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

// ─── RAG Knowledge Base Architecture & Reference Books Showcase ───────────────

async function fetchKnowledgeBaseSummary() {
    const grid = document.getElementById('ragBooksShowcaseGrid');
    const vectorText = document.getElementById('ragVectorCountText');
    if (!grid) return;

    try {
        const resp = await fetch('/api/v1/curriculum/knowledge-base/summary');
        let data = null;
        if (resp.ok) {
            data = await resp.json();
        }

        const books = (data && data.reference_books) || [
            {
                title: "Collins Speaking for IELTS",
                author: "Karen Kovacs",
                category: "Speaking & Fluency",
                units_count: 11,
                cefr: "B1 - B2",
                topics: "Job Interview, Academic Discussion, Presentation, Storytelling",
                badge: "IELTS Standard",
            },
            {
                title: "Cambridge English Vocabulary in Use",
                author: "Michael McCarthy & Felicity O'Dell",
                category: "Vocabulary & Collocations",
                units_count: 30,
                cefr: "B2",
                topics: "Work & Careers, Tech & Society, Emotions, Phrasal Verbs",
                badge: "Cambridge Official",
            },
            {
                title: "The Cambridge Guide to English Usage",
                author: "Pam Peters",
                category: "Grammar & Common Dilemmas",
                units_count: 8,
                cefr: "B1 - B2",
                topics: "Borrow vs Lend, Affect vs Effect, Used to, Say vs Tell",
                badge: "Grammar Remediation",
            },
            {
                title: "CEFR Companion Volume",
                author: "Council of Europe",
                category: "Spoken Interaction Benchmarks",
                units_count: 7,
                cefr: "A1 - C2 (Focused B1-B2)",
                topics: "Spoken Interaction, Informal Discussion, Goal-Oriented Cooperation",
                badge: "Council of Europe",
            },
        ];

        if (vectorText && data && data.vector_count) {
            vectorText.textContent = `${data.vector_count} Vektor`;
        }

        grid.innerHTML = books.map(b => `
            <div style="background: #FFFFFF; border: 1px solid #E2D9CC; border-radius: 12px; padding: 18px; display: flex; flex-direction: column; justify-content: space-between; gap: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.03); transition: transform 0.2s ease;">
                <div>
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                        <span style="font-size: 11px; font-weight: 700; color: #8C6239; background: #FFF4E5; padding: 3px 8px; border-radius: 999px; border: 1px solid #FBD38D;">
                            ${escapeHtml(b.badge || 'Verified')}
                        </span>
                        <span style="font-size: 11px; font-weight: 600; color: #2B6CB0; background: #EBF8FF; padding: 2px 6px; border-radius: 4px;">
                            ${escapeHtml(b.cefr || 'B1-B2')}
                        </span>
                    </div>
                    <h4 style="margin: 0; font-size: 15px; font-weight: 800; color: #1A202C; line-height: 1.35;">${escapeHtml(b.title)}</h4>
                    <div style="font-size: 11.5px; color: #718096; margin-top: 3px;">Penulis: ${escapeHtml(b.author || '-')}</div>
                    <div style="font-size: 12px; font-weight: 700; color: #C87D55; margin-top: 8px;">
                        <i class="fa-solid fa-layer-group" style="font-size: 11px;"></i> ${b.units_count || 10} Unit Materi Terindeks
                    </div>
                    <p style="font-size: 12px; color: #4A5568; margin: 6px 0 0 0; line-height: 1.45;">${escapeHtml(b.topics || b.category)}</p>
                </div>
                <div style="padding-top: 10px; border-top: 1px solid #F0EAE1; display: flex; align-items: center; justify-content: space-between; font-size: 11px;">
                    <span style="color: #22543D; font-weight: 600;"><i class="fa-solid fa-circle-check" style="color: #38A169;"></i> Aktif di ChromaDB</span>
                    <span style="color: #718096;">Dense & BM25</span>
                </div>
            </div>
        `).join('');
    } catch (err) {
        console.warn('Knowledge base summary fetch failed, using fallback:', err);
    }
}

