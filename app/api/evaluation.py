"""
MILO AI Backend - Evaluation & Benchmark API Router

Provides endpoints to view, trigger, and download DeepEval quantitative benchmark
data, charts, and academic reports for the frontend dashboard and thesis/PA.
"""

import asyncio
import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/evaluation", tags=["Evaluation"])

RESULTS_DIR = Path(__file__).resolve().parent.parent.parent / "evaluations" / "results"
CSV_PATH = RESULTS_DIR / "summary_metrics.csv"
JSON_PATH = RESULTS_DIR / "evaluation_details.json"
REPORT_PATH = RESULTS_DIR / "REPORT_BAB4_PA.md"
HTML_DASHBOARD_PATH = RESULTS_DIR / "evaluation_dashboard.html"

# In-memory execution state
_eval_lock = asyncio.Lock()
_eval_status = {
    "is_running": False,
    "last_run": None,
    "current_suite": None,
    "progress_message": "Idle",
    "error": None,
}


class RunEvaluationRequest(BaseModel):
    suite: str = Field(default="all", description="Evaluation suite: 'all', 'rag', 'feedback', or 'tutor'")
    live: bool = Field(default=False, description="Whether to query live ChromaDB and LLM")
    max_samples: Optional[int] = Field(default=None, description="Max test cases per suite")


def _read_summary_csv() -> List[Dict[str, Any]]:
    """Read summary metrics from CSV."""
    if not CSV_PATH.exists():
        return []
    rows = []
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({
                "module": r.get("Module"),
                "metric": r.get("Metric"),
                "sample_count": int(r.get("Sample_Count", 0)),
                "mean_score": float(r.get("Mean_Score", 0.0)),
                "std_dev": float(r.get("Std_Dev", 0.0)),
                "min_score": float(r.get("Min_Score", 0.0)),
                "max_score": float(r.get("Max_Score", 0.0)),
                "pass_rate_pct": float(r.get("Pass_Rate_Pct", 0.0)),
            })
    return rows


def _read_details_json() -> Dict[str, Any]:
    """Read detailed evaluation logs."""
    if not JSON_PATH.exists():
        return {"rag": [], "feedback": [], "tutor": []}
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading evaluation details JSON: {e}")
        return {"rag": [], "feedback": [], "tutor": []}


async def _execute_evaluation_task(suite: str, live: bool, max_samples: Optional[int]) -> None:
    """Background task to run evaluations."""
    global _eval_status
    _eval_status["is_running"] = True
    _eval_status["current_suite"] = suite
    _eval_status["progress_message"] = f"Menjalankan benchmark ({suite})..."
    _eval_status["error"] = None

    try:
        from evaluations.run_evaluation import main_async
        import argparse

        args = argparse.Namespace(
            suite=suite,
            live=live,
            max_samples=max_samples,
        )
        await main_async(args)

        _eval_status["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        _eval_status["progress_message"] = "Evaluasi selesai dengan sukses!"
    except Exception as e:
        logger.error(f"Error during evaluation background execution: {e}", exc_info=True)
        _eval_status["error"] = str(e)
        _eval_status["progress_message"] = f"Gagal: {e}"
    finally:
        _eval_status["is_running"] = False


@router.get("/summary", summary="Get evaluation summary metrics for dashboard charts")
async def get_evaluation_summary() -> Dict[str, Any]:
    """
    Returns aggregated metric scores, pass rates, and chart data
    for rendering in the frontend evaluation dashboard.
    """
    rows = _read_summary_csv()
    
    # Calculate high-level stats
    total_samples = sum(r["sample_count"] for r in rows) if rows else 0
    mean_scores = [r["mean_score"] for r in rows] if rows else [0.0]
    overall_mean = round(sum(mean_scores) / len(mean_scores), 4) if mean_scores else 0.0
    pass_rates = [r["pass_rate_pct"] for r in rows] if rows else [0.0]
    overall_pass_rate = round(sum(pass_rates) / len(pass_rates), 2) if pass_rates else 0.0

    # Group by module for radar & bar charts
    chart_metrics = {
        "labels": [f"{r['module']}: {r['metric']}" for r in rows],
        "scores": [r["mean_score"] for r in rows],
        "thresholds": [0.70 for _ in rows],
        "pass_rates": [r["pass_rate_pct"] for r in rows],
    }

    return {
        "has_data": len(rows) > 0,
        "last_updated": datetime.fromtimestamp(CSV_PATH.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S") if CSV_PATH.exists() else None,
        "total_metrics_count": len(rows),
        "total_samples": total_samples,
        "overall_mean": overall_mean,
        "overall_pass_rate": overall_pass_rate,
        "metrics": rows,
        "chart_data": chart_metrics,
        "status": _eval_status,
    }


@router.get("/details", summary="Get detailed test case evaluation results")
async def get_evaluation_details() -> Dict[str, Any]:
    """Returns raw test case logs, answers, and LLM reasoning."""
    return _read_details_json()


@router.get("/report", summary="Get generated Markdown thesis report")
async def get_evaluation_report() -> PlainTextResponse:
    """Returns the text of REPORT_BAB4_PA.md."""
    if not REPORT_PATH.exists():
        raise HTTPException(status_code=404, detail="Laporan belum digenerate. Jalankan evaluasi terlebih dahulu.")
    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    return PlainTextResponse(content, media_type="text/markdown; charset=utf-8")


@router.get("/dashboard", response_class=HTMLResponse, summary="Internal Developer Evaluation Dashboard")
async def get_developer_dashboard() -> HTMLResponse:
    """
    Serves the internal developer/researcher evaluation dashboard.
    Intended strictly for backend monitoring and thesis benchmarks.
    """
    if not HTML_DASHBOARD_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="Dashboard belum digenerate. Jalankan benchmark terlebih dahulu melalui 'uv run python -m evaluations.run_evaluation'."
        )
    with open(HTML_DASHBOARD_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content=content)


@router.get("/status", summary="Get current evaluation execution status")
async def get_evaluation_status() -> Dict[str, Any]:
    """Check if an evaluation task is actively running in background."""
    return _eval_status


@router.post("/run", summary="Trigger a benchmark evaluation run")
async def trigger_evaluation(
    request: RunEvaluationRequest,
    background_tasks: BackgroundTasks,
) -> Dict[str, Any]:
    """
    Trigger DeepEval benchmark execution.
    Can be run for 'all', 'rag', 'feedback', or 'tutor'.
    """
    global _eval_status
    if _eval_status["is_running"]:
        return {
            "status": "already_running",
            "message": "Evaluasi benchmark sedang berjalan, mohon tunggu hingga selesai.",
            "current_status": _eval_status,
        }

    background_tasks.add_task(
        _execute_evaluation_task,
        suite=request.suite,
        live=request.live,
        max_samples=request.max_samples,
    )

    return {
        "status": "started",
        "message": f"Evaluasi suite '{request.suite}' berhasil dimulai di background.",
        "suite": request.suite,
        "live": request.live,
        "max_samples": request.max_samples,
    }


@router.get("/download/{file_type}", summary="Download evaluation output files")
async def download_file(file_type: str) -> FileResponse:
    """Download CSV, JSON, or Markdown report."""
    if file_type == "csv":
        if not CSV_PATH.exists():
            raise HTTPException(status_code=404, detail="File CSV belum tersedia.")
        return FileResponse(CSV_PATH, filename="milo_evaluation_summary.csv", media_type="text/csv")
    elif file_type == "json":
        if not JSON_PATH.exists():
            raise HTTPException(status_code=404, detail="File JSON belum tersedia.")
        return FileResponse(JSON_PATH, filename="milo_evaluation_details.json", media_type="application/json")
    elif file_type in ("md", "report"):
        if not REPORT_PATH.exists():
            raise HTTPException(status_code=404, detail="File Laporan Markdown belum tersedia.")
        return FileResponse(REPORT_PATH, filename="REPORT_BAB4_PA.md", media_type="text/markdown")
    else:
        raise HTTPException(status_code=400, detail="Tipe file tidak valid. Gunakan 'csv', 'json', atau 'report'.")

