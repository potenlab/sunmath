"""API endpoints for LLM benchmark under /benchmark/llm/."""

import json
import logging
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.config import settings
from app.schemas.llm_benchmark import (
    BenchmarkReport,
    BenchmarkRun,
    BenchmarkRunRequest,
    RunListItem,
    RunListResponse,
    RunStatusResponse,
    SympyVerificationReport,
    VotingBenchmarkResult,
    VotingRunRequest,
)
from app.services import benchmark_analyzer, benchmark_runner, cross_verifier
from app.services.benchmark_runner import _project_root

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/benchmark/llm", tags=["llm-benchmark"])

# In-memory progress tracking for async runs
_run_progress: dict[str, dict] = {}


def _progress_callback(run_id: str):
    def cb(current: int, total: int, label: str):
        _run_progress[run_id] = {
            "status": "running",
            "progress": current,
            "total": total,
            "message": label,
        }
    return cb


async def _run_benchmark_task(run_id: str, request: BenchmarkRunRequest):
    try:
        _run_progress[run_id] = {"status": "running", "progress": 0, "total": 0, "message": "Starting..."}
        await benchmark_runner.run_full_benchmark(
            model_keys=request.models,
            problem_ids=request.problems,
            progress_callback=_progress_callback(run_id),
        )
        _run_progress[run_id]["status"] = "completed"
        _run_progress[run_id]["message"] = "Done"
    except Exception as exc:
        logger.exception("Benchmark run %s failed", run_id)
        _run_progress[run_id] = {
            "status": "failed",
            "progress": 0,
            "total": 0,
            "message": str(exc),
        }


async def _run_voting_task(run_id: str, request: VotingRunRequest):
    try:
        _run_progress[run_id] = {"status": "running", "progress": 0, "total": 0, "message": "Starting voting..."}
        result = await cross_verifier.run_voting_benchmark(
            problem_ids=request.problems,
            thresholds=request.thresholds,
            progress_callback=_progress_callback(run_id),
        )
        # Save voting results
        out_dir = _project_root() / settings.benchmark_results_dir
        out_dir.mkdir(parents=True, exist_ok=True)
        with open(out_dir / f"voting_{run_id}.json", "w") as f:
            json.dump(result.model_dump(), f, indent=2)
        _run_progress[run_id]["status"] = "completed"
        _run_progress[run_id]["message"] = "Done"
    except Exception as exc:
        logger.exception("Voting run %s failed", run_id)
        _run_progress[run_id] = {
            "status": "failed",
            "progress": 0,
            "total": 0,
            "message": str(exc),
        }


@router.post("/run", response_model=RunStatusResponse)
async def start_benchmark(request: BenchmarkRunRequest, background_tasks: BackgroundTasks):
    """Start a benchmark run in the background."""
    from datetime import datetime, timezone
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    background_tasks.add_task(_run_benchmark_task, run_id, request)
    return RunStatusResponse(
        run_id=run_id,
        status="running",
        message="Benchmark started",
    )


@router.get("/status/{run_id}", response_model=RunStatusResponse)
async def get_status(run_id: str):
    """Poll benchmark run progress."""
    info = _run_progress.get(run_id)
    if not info:
        # Check if run completed earlier (results file exists)
        path = _project_root() / settings.benchmark_results_dir / f"run_{run_id}.json"
        if path.exists():
            return RunStatusResponse(run_id=run_id, status="completed", message="Done")
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    return RunStatusResponse(
        run_id=run_id,
        status=info["status"],
        progress=info["progress"],
        total=info["total"],
        message=info["message"],
    )


@router.get("/runs", response_model=RunListResponse)
async def list_runs():
    """List all completed benchmark runs."""
    runs_data = benchmark_analyzer.list_runs()
    items = [RunListItem(**r) for r in runs_data]
    return RunListResponse(runs=items)


@router.get("/results/{run_id}", response_model=BenchmarkRun)
async def get_results(run_id: str):
    """Get full raw results for a benchmark run."""
    try:
        return benchmark_analyzer.load_run(run_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")


@router.get("/report/{run_id}", response_model=BenchmarkReport)
async def get_report(run_id: str):
    """Get analyzed report for a benchmark run."""
    try:
        run = benchmark_analyzer.load_run(run_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    return benchmark_analyzer.generate_full_report(run)


@router.post("/voting/run", response_model=RunStatusResponse)
async def start_voting(request: VotingRunRequest, background_tasks: BackgroundTasks):
    """Start a voting benchmark run in the background."""
    from datetime import datetime, timezone
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    background_tasks.add_task(_run_voting_task, run_id, request)
    return RunStatusResponse(
        run_id=run_id,
        status="running",
        message="Voting benchmark started",
    )


@router.get("/voting/results/{run_id}", response_model=VotingBenchmarkResult)
async def get_voting_results(run_id: str):
    """Get voting benchmark results."""
    path = _project_root() / settings.benchmark_results_dir / f"voting_{run_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Voting run {run_id} not found")
    with open(path) as f:
        data = json.load(f)
    return VotingBenchmarkResult(**data)


@router.get("/sympy-verify/{run_id}", response_model=SympyVerificationReport)
async def sympy_verify(run_id: str):
    """Run SymPy verification on an existing benchmark run."""
    try:
        run = benchmark_analyzer.load_run(run_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    return cross_verifier.run_sympy_verification(run)
