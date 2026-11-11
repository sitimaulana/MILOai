"""
MILO AI Backend - DeepEval Benchmark Runner & Report Generator

Executes quantitative evaluations across RAG, Feedback, and Tutor modules,
and generates structured statistical summaries for academic reports (Skripsi / PA).

Usage:
    # Run all benchmarks on pre-defined test cases
    uv run python -m evaluations.run_evaluation

    # Run RAG evaluation against live ChromaDB and LLM
    uv run python -m evaluations.run_evaluation --suite rag --live

    # Run Feedback evaluation only
    uv run python -m evaluations.run_evaluation --suite feedback
"""

import argparse
import asyncio
import csv
import json
import logging
import statistics
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("evaluations.runner")

RESULTS_DIR = Path(__file__).parent / "results"


def ensure_results_dir() -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    return RESULTS_DIR


def calculate_metric_stats(scores: List[float]) -> Dict[str, float]:
    """Calculate descriptive statistics for a list of scores."""
    valid_scores = [s for s in scores if s is not None]
    if not valid_scores:
        return {"mean": 0.0, "std_dev": 0.0, "min": 0.0, "max": 0.0, "pass_rate_pct": 0.0}

    mean_val = statistics.mean(valid_scores)
    std_val = statistics.stdev(valid_scores) if len(valid_scores) > 1 else 0.0
    pass_count = sum(1 for s in valid_scores if s >= 0.70)
    pass_rate = (pass_count / len(valid_scores)) * 100.0

    return {
        "mean": round(mean_val, 4),
        "std_dev": round(std_val, 4),
        "min": round(min(valid_scores), 4),
        "max": round(max(valid_scores), 4),
        "pass_rate_pct": round(pass_rate, 2),
    }


def export_csv_summary(summary_rows: List[Dict[str, Any]], filepath: Path) -> None:
    """Export summary metrics table to CSV."""
    if not summary_rows:
        return
    fieldnames = list(summary_rows[0].keys())
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)
    logger.info(f"📊 Exported CSV summary: {filepath}")


def export_markdown_report(
    summary_rows: List[Dict[str, Any]],
    raw_results: Dict[str, Any],
    filepath: Path,
) -> None:
    """Generate Markdown report for Bab 4 Hasil & Pembahasan."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    md_lines = [
        "# Laporan Pengujian Kuantitatif AI-MILO (DeepEval Benchmark)",
        f"**Waktu Pengujian**: {timestamp}  ",
        "**Kerangka Kerja Evaluasi**: DeepEval (LLM-as-a-Judge)  ",
        "**Threshold Kelulusan (Pass Rate)**: Skor >= 0.70 (Skala 0.0 - 1.0)  ",
        "",
        "---",
        "",
        "## 1. Ringkasan Metrik Pengujian (Tabel untuk Bab 4)",
        "",
        "| Modul | Metrik Evaluasi | Jumlah Sampel | Rata-Rata Skor | Standar Deviasi | Nilai Min | Nilai Max | Pass Rate (%) |",
        "| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |",
    ]

    for row in summary_rows:
        md_lines.append(
            f"| {row['Module']} | {row['Metric']} | {row['Sample_Count']} | {row['Mean_Score']} | {row['Std_Dev']} | {row['Min_Score']} | {row['Max_Score']} | {row['Pass_Rate_Pct']}% |"
        )

    md_lines.extend([
        "",
        "---",
        "",
        "## 2. Interpretasi Hasil Evaluasi untuk Skripsi / PA",
        "",
        "### A. Modul RAG (Retrieval-Augmented Generation)",
        "- **Faithfulness**: Mengukur tingkat kepatuhan respons MILO terhadap konteks materi di Obsidian Vault. Skor mendekati 1.0 membuktikan bahwa model tidak mengalami halusinasi dan konsisten menggunakan materi pembelajaran.",
        "- **Answer Relevancy**: Mengukur seberapa tepat respons menjawab pertanyaan atau kebutuhan speaking learner tanpa melenceng dari konteks percakapan.",
        "",
        "### B. Modul Language Feedback (CEFR Engine)",
        "- **Correction Accuracy**: Menunjukkan keakuratan deteksi kesalahan gramatikal dan ketepatan koreksi yang disarankan.",
        "- **False Positive Resistance**: Menunjukkan keandalan sistem dalam tidak menghukum atau membetulkan kalimat yang sebenarnya sudah benar dan natural.",
        "- **Pedagogical Tone**: Mengukur keramahan, kejelasan tip, dan sifat suportif dalam gaya pengajaran MILO.",
        "",
        "### C. Modul Tutor Speaking Companion",
        "- **CEFR Adaptation**: Menunjukkan bahwa kompleksitas kalimat dan kosakata yang dihasilkan berhasil beradaptasi dengan level pengguna (A1/A2/B1/B2).",
        "- **One Question Rule**: Menunjukkan konsistensi MILO dalam menjaga alur percakapan dua arah dengan selalu mengakhiri respons menggunakan satu pertanyaan pemantik.",
        "",
        "---",
        "*File laporan ini digenerate secara otomatis oleh modul `evaluations.run_evaluation`.*",
    ])

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    logger.info(f"📄 Exported Markdown thesis report: {filepath}")


def export_html_dashboard(
    summary_rows: List[Dict[str, Any]],
    raw_results: Dict[str, Any],
    filepath: Path,
) -> None:
    """Generate self-contained HTML developer dashboard with interactive charts."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    labels = [f"{r['Module']}: {r['Metric']}" for r in summary_rows]
    radar_labels = [r['Metric'] for r in summary_rows]
    scores = [r['Mean_Score'] for r in summary_rows]
    thresholds = [0.70 for _ in summary_rows]

    total_samples = sum(r['Sample_Count'] for r in summary_rows) if summary_rows else 0
    mean_val = round(sum(scores) / len(scores), 4) if scores else 0.0
    pass_rates = [r['Pass_Rate_Pct'] for r in summary_rows] if summary_rows else [0.0]
    overall_pass_rate = round(sum(pass_rates) / len(pass_rates), 2) if pass_rates else 0.0

    # Table rows HTML
    table_rows_html = ""
    for r in summary_rows:
        pass_badge = (
            f'<span class="badge pass">✓ {r["Pass_Rate_Pct"]}% PASS</span>'
            if r["Pass_Rate_Pct"] >= 70
            else f'<span class="badge fail">✗ {r["Pass_Rate_Pct"]}% FAIL</span>'
        )
        table_rows_html += f"""
        <tr>
            <td><span class="pill {r['Module'].lower()}">{r['Module']}</span></td>
            <td><strong>{r['Metric']}</strong></td>
            <td>{r['Sample_Count']}</td>
            <td><strong>{r['Mean_Score']:.4f}</strong></td>
            <td>± {r['Std_Dev']:.4f}</td>
            <td>{r['Min_Score']:.2f} / {r['Max_Score']:.2f}</td>
            <td>{pass_badge}</td>
        </tr>
        """

    # Test cases details HTML
    test_cases_html = ""
    idx = 1
    for mod_name, items in raw_results.items():
        for item in items:
            inp = item.get("input") or item.get("user_text") or item.get("user_message") or "-"
            out = item.get("actual_output") or item.get("tutor_reply") or "JSON Output"
            mod_lower = mod_name.lower()

            if mod_lower == "rag":
                score_str = f"Faith: {item.get('faithfulness_score')} | Rel: {item.get('relevancy_score')}"
                reasoning = f"<strong>Faithfulness:</strong> {item.get('faithfulness_reason', 'N/A')}<br><strong>Relevancy:</strong> {item.get('relevancy_reason', 'N/A')}"
                is_pass = item.get("faithfulness_passed") and item.get("relevancy_passed")
            elif mod_lower == "feedback":
                score_str = f"Acc: {item.get('accuracy_score')} | FP: {item.get('false_positive_score')}"
                reasoning = item.get("accuracy_reason") or "Evaluated with CEFR error detection rubric."
                is_pass = item.get("accuracy_passed") and item.get("false_positive_passed")
            else:
                score_str = f"CEFR: {item.get('cefr_adaptation_score')} | 1-Q: {item.get('one_question_score')}"
                reasoning = "Evaluated against CEFR level constraints and One Question Rule."
                is_pass = item.get("cefr_adaptation_passed") and item.get("one_question_passed")

            badge = '<span class="badge pass">PASS</span>' if is_pass else '<span class="badge fail">FAIL</span>'

            test_cases_html += f"""
            <tr>
                <td><strong>#{item.get('id', idx)}</strong></td>
                <td><span class="pill {mod_lower}">{mod_name.upper()}</span></td>
                <td style="max-width: 280px; font-size: 13px;">{inp}</td>
                <td style="max-width: 280px; font-size: 13px; color: #475569;">{out}</td>
                <td><div>{score_str}</div> {badge}</td>
                <td>
                    <details>
                        <summary style="cursor: pointer; color: #2563EB; font-weight: 600; font-size: 12px;">Lihat Reasoning</summary>
                        <div style="background: #F8FAFC; padding: 10px; border-radius: 8px; margin-top: 6px; font-size: 12px; border-left: 3px solid #FF5E36;">
                            {reasoning}
                        </div>
                    </details>
                </td>
            </tr>
            """
            idx += 1

    html_content = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MILO Backend — Evaluation & Benchmark Console</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-page: #0F172A;
            --card-bg: #1E293B;
            --border-card: #334155;
            --text-main: #F8FAFC;
            --text-muted: #94A3B8;
            --orange: #FF5E36;
            --teal: #0D9488;
            --indigo: #6366F1;
            --green: #10B981;
            --red: #EF4444;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background: var(--bg-page);
            color: var(--text-main);
            padding: 32px 40px;
            line-height: 1.5;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border-card);
            padding-bottom: 24px;
            margin-bottom: 28px;
            flex-wrap: wrap;
            gap: 16px;
        }}
        .header h1 {{ font-size: 24px; font-weight: 800; display: flex; align-items: center; gap: 10px; }}
        .header h1 span {{ color: var(--orange); }}
        .header-meta {{ font-size: 13px; color: var(--text-muted); }}
        .badge-dev {{
            background: rgba(255, 94, 54, 0.15);
            color: var(--orange);
            border: 1px solid var(--orange);
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 18px;
            margin-bottom: 28px;
        }}
        .stat-card {{
            background: var(--card-bg);
            border: 1px solid var(--border-card);
            border-radius: 16px;
            padding: 20px;
        }}
        .stat-val {{ font-size: 28px; font-weight: 800; color: #FFFFFF; margin-bottom: 4px; }}
        .stat-label {{ font-size: 12px; text-transform: uppercase; color: var(--text-muted); font-weight: 700; letter-spacing: 0.5px; }}
        .charts-grid {{
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 24px;
            margin-bottom: 32px;
        }}
        @media (max-width: 992px) {{ .charts-grid {{ grid-template-columns: 1fr; }} }}
        .chart-box {{
            background: var(--card-bg);
            border: 1px solid var(--border-card);
            border-radius: 18px;
            padding: 22px 26px;
        }}
        .chart-title {{ font-size: 16px; font-weight: 700; margin-bottom: 16px; color: #FFFFFF; }}
        .card-table {{
            background: var(--card-bg);
            border: 1px solid var(--border-card);
            border-radius: 18px;
            padding: 24px 28px;
            margin-bottom: 32px;
            overflow-x: auto;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13.5px;
            text-align: left;
        }}
        th {{
            background: #0F172A;
            padding: 12px 16px;
            color: var(--text-muted);
            border-bottom: 2px solid var(--border-card);
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        td {{
            padding: 14px 16px;
            border-bottom: 1px solid #334155;
            color: #E2E8F0;
        }}
        tr:hover td {{ background: rgba(255, 255, 255, 0.02); }}
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 700;
        }}
        .badge.pass {{ background: rgba(16, 185, 129, 0.2); color: #34D399; border: 1px solid #059669; }}
        .badge.fail {{ background: rgba(239, 68, 68, 0.2); color: #F87171; border: 1px solid #DC2626; }}
        .pill {{
            display: inline-block;
            padding: 2px 7px;
            border-radius: 6px;
            font-size: 10.5px;
            font-weight: 700;
            text-transform: uppercase;
        }}
        .pill.rag {{ background: #312E81; color: #C7D2FE; }}
        .pill.feedback {{ background: #831843; color: #FBCFE8; }}
        .pill.tutor {{ background: #064E3B; color: #A7F3D0; }}
        .btn {{
            background: var(--orange);
            color: #FFFFFF;
            border: none;
            padding: 8px 16px;
            border-radius: 10px;
            font-size: 13px;
            font-weight: 700;
            cursor: pointer;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}
        .btn:hover {{ background: #E84D25; }}
    </style>
</head>
<body>

    <div class="header">
        <div>
            <h1>MILO <span>Backend</span> — Evaluation & Benchmark Console</h1>
            <div class="header-meta">Data Pengujian Kuantitatif Ilmiah (DeepEval LLM-as-a-Judge) untuk Skripsi / PA</div>
        </div>
        <div style="display: flex; gap: 12px; align-items: center;">
            <span class="badge-dev">Developer Internal Only</span>
            <span style="font-size: 12px; color: var(--text-muted);">Diperbarui: {timestamp}</span>
        </div>
    </div>

    <!-- Stat Cards -->
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-val">{total_samples}</div>
            <div class="stat-label">Total Sampel Uji</div>
        </div>
        <div class="stat-card">
            <div class="stat-val">{mean_val * 100:.1f}%</div>
            <div class="stat-label">Rata-Rata Skor Komposit</div>
        </div>
        <div class="stat-card">
            <div class="stat-val">{overall_pass_rate:.1f}%</div>
            <div class="stat-label">Tingkat Kelulusan (Pass Rate)</div>
        </div>
        <div class="stat-card">
            <div class="stat-val">{len(summary_rows)}</div>
            <div class="stat-label">Total Metrik Pengujian</div>
        </div>
    </div>

    <!-- Charts -->
    <div class="charts-grid">
        <div class="chart-box">
            <div class="chart-title">Skor Rata-Rata per Metrik vs Target Threshold (0.70)</div>
            <div style="height: 280px;"><canvas id="barChart"></canvas></div>
        </div>
        <div class="chart-box">
            <div class="chart-title">Radar Kapabilitas AI-MILO</div>
            <div style="height: 280px;"><canvas id="radarChart"></canvas></div>
        </div>
    </div>

    <!-- Summary Table -->
    <div class="card-table">
        <div class="chart-title" style="margin-bottom: 14px;">Tabel Ringkasan Metrik Pengujian (Format Bab 4 Skripsi/PA)</div>
        <table>
            <thead>
                <tr>
                    <th>Modul</th>
                    <th>Metrik Evaluasi</th>
                    <th>Jumlah Sampel</th>
                    <th>Rata-Rata</th>
                    <th>Standar Deviasi</th>
                    <th>Min / Max</th>
                    <th>Status Kelulusan</th>
                </tr>
            </thead>
            <tbody>
                {table_rows_html}
            </tbody>
        </table>
    </div>

    <!-- Test Cases Explorer -->
    <div class="card-table">
        <div class="chart-title" style="margin-bottom: 14px;">Eksplorasi Test Case & Reasoning Evaluator (DeepEval)</div>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Modul</th>
                    <th>Input Learner</th>
                    <th>Actual Output / Feedback</th>
                    <th>Skor</th>
                    <th>Detail Reasoning</th>
                </tr>
            </thead>
            <tbody>
                {test_cases_html if test_cases_html else '<tr><td colspan="6" style="text-align: center; padding: 20px;">Belum ada test cases.</td></tr>'}
            </tbody>
        </table>
    </div>

    <script>
        const barLabels = {json.dumps(labels)};
        const radarLabels = {json.dumps(radar_labels)};
        const scores = {json.dumps(scores)};
        const thresholds = {json.dumps(thresholds)};

        // Bar Chart
        new Chart(document.getElementById('barChart'), {{
            type: 'bar',
            data: {{
                labels: barLabels,
                datasets: [
                    {{
                        label: 'Skor Rata-Rata',
                        data: scores,
                        backgroundColor: scores.map(s => s >= 0.70 ? '#FF5E36' : '#EF4444'),
                        borderRadius: 6,
                    }},
                    {{
                        label: 'Threshold (0.70)',
                        data: thresholds,
                        type: 'line',
                        borderColor: '#10B981',
                        borderDash: [5, 5],
                        pointRadius: 0
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{ beginAtZero: true, max: 1.0, grid: {{ color: '#334155' }}, ticks: {{ color: '#94A3B8' }} }},
                    x: {{ grid: {{ display: false }}, ticks: {{ color: '#94A3B8' }} }}
                }},
                plugins: {{ legend: {{ labels: {{ color: '#F8FAFC' }} }} }}
            }}
        }});

        // Radar Chart
        new Chart(document.getElementById('radarChart'), {{
            type: 'radar',
            data: {{
                labels: radarLabels,
                datasets: [
                    {{
                        label: 'Performa AI-MILO',
                        data: scores,
                        backgroundColor: 'rgba(99, 102, 241, 0.25)',
                        borderColor: '#818CF8',
                        pointBackgroundColor: '#818CF8'
                    }},
                    {{
                        label: 'Threshold (0.70)',
                        data: thresholds,
                        borderColor: '#10B981',
                        borderDash: [4, 4],
                        pointRadius: 0
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    r: {{
                        beginAtZero: true,
                        max: 1.0,
                        grid: {{ color: '#334155' }},
                        pointLabels: {{ color: '#CBD5E1', font: {{ size: 11 }} }},
                        ticks: {{ display: false }}
                    }}
                }},
                plugins: {{ legend: {{ labels: {{ color: '#F8FAFC' }} }} }}
            }}
        }});
    </script>
</body>
</html>
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)
    logger.info(f"🌐 Exported HTML developer dashboard: {filepath}")


async def main_async(args: argparse.Namespace) -> None:
    results_dir = ensure_results_dir()
    summary_rows = []
    raw_results = {}

    suite = args.suite.lower()

    # 1. RAG Evaluation
    if suite in ("all", "rag"):
        logger.info("🚀 Running RAG Evaluation Suite...")
        from evaluations.eval_rag import run_rag_evaluations

        rag_results = await run_rag_evaluations(
            use_live_pipeline=args.live,
            max_samples=args.max_samples,
        )
        raw_results["rag"] = rag_results

        # Faithfulness stats
        f_scores = [r["faithfulness_score"] for r in rag_results]
        f_stats = calculate_metric_stats(f_scores)
        summary_rows.append({
            "Module": "RAG",
            "Metric": "Faithfulness",
            "Sample_Count": len(f_scores),
            "Mean_Score": f_stats["mean"],
            "Std_Dev": f_stats["std_dev"],
            "Min_Score": f_stats["min"],
            "Max_Score": f_stats["max"],
            "Pass_Rate_Pct": f_stats["pass_rate_pct"],
        })

        # Relevancy stats
        r_scores = [r["relevancy_score"] for r in rag_results]
        r_stats = calculate_metric_stats(r_scores)
        summary_rows.append({
            "Module": "RAG",
            "Metric": "Answer Relevancy",
            "Sample_Count": len(r_scores),
            "Mean_Score": r_stats["mean"],
            "Std_Dev": r_stats["std_dev"],
            "Min_Score": r_stats["min"],
            "Max_Score": r_stats["max"],
            "Pass_Rate_Pct": r_stats["pass_rate_pct"],
        })

    # 2. Feedback Evaluation
    if suite in ("all", "feedback"):
        logger.info("🚀 Running Language Feedback Evaluation Suite...")
        from evaluations.eval_feedback import run_feedback_evaluations

        fb_results = await run_feedback_evaluations(max_samples=args.max_samples)
        raw_results["feedback"] = fb_results

        # Accuracy
        acc_scores = [r["accuracy_score"] for r in fb_results]
        acc_stats = calculate_metric_stats(acc_scores)
        summary_rows.append({
            "Module": "Feedback",
            "Metric": "Correction Accuracy",
            "Sample_Count": len(acc_scores),
            "Mean_Score": acc_stats["mean"],
            "Std_Dev": acc_stats["std_dev"],
            "Min_Score": acc_stats["min"],
            "Max_Score": acc_stats["max"],
            "Pass_Rate_Pct": acc_stats["pass_rate_pct"],
        })

        # False positive resistance
        fp_scores = [r["false_positive_score"] for r in fb_results]
        fp_stats = calculate_metric_stats(fp_scores)
        summary_rows.append({
            "Module": "Feedback",
            "Metric": "False Positive Resistance",
            "Sample_Count": len(fp_scores),
            "Mean_Score": fp_stats["mean"],
            "Std_Dev": fp_stats["std_dev"],
            "Min_Score": fp_stats["min"],
            "Max_Score": fp_stats["max"],
            "Pass_Rate_Pct": fp_stats["pass_rate_pct"],
        })

        # Pedagogical Tone
        ped_scores = [r["pedagogical_score"] for r in fb_results]
        ped_stats = calculate_metric_stats(ped_scores)
        summary_rows.append({
            "Module": "Feedback",
            "Metric": "Pedagogical Tone",
            "Sample_Count": len(ped_scores),
            "Mean_Score": ped_stats["mean"],
            "Std_Dev": ped_stats["std_dev"],
            "Min_Score": ped_stats["min"],
            "Max_Score": ped_stats["max"],
            "Pass_Rate_Pct": ped_stats["pass_rate_pct"],
        })

    # 3. Tutor Evaluation
    if suite in ("all", "tutor"):
        logger.info("🚀 Running Speaking Tutor Evaluation Suite...")
        from evaluations.eval_tutor import run_tutor_evaluations

        tutor_results = await run_tutor_evaluations(max_samples=args.max_samples)
        raw_results["tutor"] = tutor_results

        # CEFR Adaptation
        cefr_scores = [r["cefr_adaptation_score"] for r in tutor_results]
        cefr_stats = calculate_metric_stats(cefr_scores)
        summary_rows.append({
            "Module": "Tutor",
            "Metric": "CEFR Adaptation",
            "Sample_Count": len(cefr_scores),
            "Mean_Score": cefr_stats["mean"],
            "Std_Dev": cefr_stats["std_dev"],
            "Min_Score": cefr_stats["min"],
            "Max_Score": cefr_stats["max"],
            "Pass_Rate_Pct": cefr_stats["pass_rate_pct"],
        })

        # One Question Rule
        oq_scores = [r["one_question_score"] for r in tutor_results]
        oq_stats = calculate_metric_stats(oq_scores)
        summary_rows.append({
            "Module": "Tutor",
            "Metric": "One Question Rule",
            "Sample_Count": len(oq_scores),
            "Mean_Score": oq_stats["mean"],
            "Std_Dev": oq_stats["std_dev"],
            "Min_Score": oq_stats["min"],
            "Max_Score": oq_stats["max"],
            "Pass_Rate_Pct": oq_stats["pass_rate_pct"],
        })

    # Export outputs
    csv_file = results_dir / "summary_metrics.csv"
    export_csv_summary(summary_rows, csv_file)

    json_file = results_dir / "evaluation_details.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(raw_results, f, indent=2)
    logger.info(f"💾 Exported detailed JSON logs: {json_file}")

    md_file = results_dir / "REPORT_BAB4_PA.md"
    export_markdown_report(summary_rows, raw_results, md_file)

    html_file = results_dir / "evaluation_dashboard.html"
    export_html_dashboard(summary_rows, raw_results, html_file)

    print("\n" + "=" * 60)
    print("✅ EVALUATION RUN COMPLETE!")
    print(f"Summary CSV:  {csv_file}")
    print(f"Details JSON: {json_file}")
    print(f"Thesis Report:{md_file}")
    print(f"HTML Console: {html_file}")
    print("=" * 60 + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="MILO DeepEval Evaluation Benchmark Runner")
    parser.add_argument(
        "--suite",
        choices=["all", "rag", "feedback", "tutor"],
        default="all",
        help="Which evaluation suite to execute (default: all)",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Retrieve live ChromaDB context and generate live responses with MILO's LLM",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="Limit number of test cases to evaluate (useful for quick trial runs)",
    )
    args = parser.parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()

