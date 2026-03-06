"""Core benchmark harness: call models via OpenRouter, check answers, save results."""

import asyncio
import csv
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import httpx

from app.config import settings
from app.schemas.llm_benchmark import (
    AnswerCheckResult,
    BenchmarkRun,
    ModelResponse,
    ProblemResult,
)
from app.services.llm_router import LLMRouter
from app.services.sympy_engine import SympyEngine

logger = logging.getLogger(__name__)

BENCHMARK_MODELS: dict[str, dict] = {
    "deepseek-v3": {
        "id": "deepseek/deepseek-chat",
        "type": "standard",
        "input_cost_per_m": 0.27,
        "output_cost_per_m": 1.10,
    },
    "claude-sonnet": {
        "id": "anthropic/claude-sonnet-4",
        "type": "standard",
        "input_cost_per_m": 3.00,
        "output_cost_per_m": 15.00,
    },
    "gpt-4o": {
        "id": "openai/gpt-4o",
        "type": "standard",
        "input_cost_per_m": 2.50,
        "output_cost_per_m": 10.00,
    },
    "o3-mini": {
        "id": "openai/o3-mini",
        "type": "reasoning",
        "input_cost_per_m": 1.10,
        "output_cost_per_m": 4.40,
    },
    "deepseek-r1": {
        "id": "deepseek/deepseek-reasoner",
        "type": "reasoning",
        "input_cost_per_m": 0.55,
        "output_cost_per_m": 2.19,
    },
    "qwen-2.5-72b": {
        "id": "qwen/qwen-2.5-72b-instruct",
        "type": "standard",
        "input_cost_per_m": 0.27,
        "output_cost_per_m": 0.27,
    },
}

SOLVER_SYSTEM_PROMPT = """\
You are a math problem solver. Solve the given problem step by step.
Respond with JSON only:
{"solution": "...", "answer": "...", "answer_latex": "...", "confidence": 0-100}"""

_client: httpx.AsyncClient | None = None


def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(timeout=60.0)
    return _client


def _project_root() -> Path:
    """Resolve project root (parent of backend/)."""
    # Works whether cwd is project root or backend/
    here = Path(__file__).resolve().parent  # app/services/
    backend = here.parent.parent            # backend/
    return backend.parent                   # project root


def load_problems(filter_ids: list[str] | None = None) -> list[dict]:
    """Load benchmark problems from data/benchmark_problems.json."""
    path = _project_root() / "data" / "benchmark_problems.json"
    with open(path) as f:
        data = json.load(f)
    problems = data["problems"]
    if filter_ids:
        id_set = set(filter_ids)
        problems = [p for p in problems if p["id"] in id_set]
    return problems


async def call_model(
    model_key: str,
    problem_content: str,
    max_retries: int = 3,
) -> ModelResponse:
    """Call a model via OpenRouter and return parsed response."""
    model_info = BENCHMARK_MODELS[model_key]
    model_id = model_info["id"]
    client = _get_client()

    for attempt in range(max_retries):
        start = time.monotonic()
        try:
            resp = await client.post(
                f"{settings.llm_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.llm_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model_id,
                    "messages": [
                        {"role": "system", "content": SOLVER_SYSTEM_PROMPT},
                        {"role": "user", "content": f"Problem:\n{problem_content}"},
                    ],
                    "temperature": 0.1,
                    "max_tokens": 1000,
                },
            )
            latency_ms = (time.monotonic() - start) * 1000

            if resp.status_code in (429, 500, 502, 503):
                wait = (2**attempt) * 2
                logger.warning(
                    "%s returned %d, retrying in %ds (attempt %d/%d)",
                    model_key, resp.status_code, wait, attempt + 1, max_retries,
                )
                await asyncio.sleep(wait)
                continue

            resp.raise_for_status()
            data = resp.json()
            choice = data["choices"][0]
            content = choice["message"]["content"]
            usage = data.get("usage", {})

            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            cost = (
                input_tokens * model_info["input_cost_per_m"] / 1_000_000
                + output_tokens * model_info["output_cost_per_m"] / 1_000_000
            )

            parsed = LLMRouter._parse_json_response(content)
            if parsed:
                return ModelResponse(
                    answer=str(parsed.get("answer", "")),
                    answer_latex=str(parsed.get("answer_latex", "")),
                    confidence=int(parsed.get("confidence", 0)),
                    solution=str(parsed.get("solution", "")),
                    latency_ms=latency_ms,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cost=cost,
                )

            return ModelResponse(
                answer=content.strip()[:200],
                latency_ms=latency_ms,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
                error="Failed to parse JSON from model response",
            )

        except httpx.TimeoutException:
            latency_ms = (time.monotonic() - start) * 1000
            if attempt < max_retries - 1:
                await asyncio.sleep(2**attempt)
                continue
            return ModelResponse(latency_ms=latency_ms, error="Timeout")
        except httpx.HTTPStatusError as exc:
            latency_ms = (time.monotonic() - start) * 1000
            return ModelResponse(latency_ms=latency_ms, error=f"HTTP {exc.response.status_code}")
        except Exception as exc:
            return ModelResponse(error=str(exc))

    return ModelResponse(error=f"Failed after {max_retries} retries")


def check_answer(
    model_answer: str,
    model_answer_latex: str,
    correct_answer: str,
    correct_answer_latex: str,
    expected_form: str,
    model_error: str | None = None,
) -> AnswerCheckResult:
    """Verify model answer: SymPy equivalence -> normalized string match -> manual review."""
    if model_error:
        return AnswerCheckResult(is_correct=False, method="model_error")
    if expected_form == "proof":
        return AnswerCheckResult(is_correct=False, method="needs_manual_review")

    # Try SymPy equivalence with LaTeX answers first
    latex_to_check = model_answer_latex or model_answer
    correct_latex = correct_answer_latex or correct_answer
    if latex_to_check and correct_latex:
        result = SympyEngine.check_equivalence(latex_to_check, correct_latex)
        if result["error"] is None:
            return AnswerCheckResult(is_correct=result["equivalent"], method="sympy")

    # Fallback: normalized string match
    norm_model = LLMRouter._normalize(model_answer)
    norm_correct = LLMRouter._normalize(correct_answer)
    if norm_model and norm_correct:
        return AnswerCheckResult(
            is_correct=norm_model == norm_correct,
            method="string_match",
        )

    return AnswerCheckResult(is_correct=False, method="needs_manual_review")


async def run_full_benchmark(
    model_keys: list[str] | None = None,
    problem_ids: list[str] | None = None,
    progress_callback: Callable[[int, int, str], None] | None = None,
) -> BenchmarkRun:
    """Run benchmark iterating problem-by-problem to spread rate limit pressure."""
    models = model_keys or list(BENCHMARK_MODELS.keys())
    problems = load_problems(problem_ids)

    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    total_tasks = len(problems) * len(models)
    results: list[ProblemResult] = []
    total_cost = 0.0
    start_time = time.monotonic()
    task_num = 0

    for problem in problems:
        for model_key in models:
            task_num += 1
            if progress_callback:
                progress_callback(
                    task_num,
                    total_tasks,
                    f"{problem['id']} x {model_key}",
                )

            response = await call_model(model_key, problem["content"])

            check = check_answer(
                model_answer=response.answer,
                model_answer_latex=response.answer_latex,
                correct_answer=problem["correct_answer"],
                correct_answer_latex=problem.get("correct_answer_latex", ""),
                expected_form=problem.get("expected_form", ""),
                model_error=response.error,
            )

            result = ProblemResult(
                problem_id=problem["id"],
                subject=problem["subject"],
                difficulty=problem["difficulty"],
                model_key=model_key,
                model_id=BENCHMARK_MODELS[model_key]["id"],
                response=response,
                check=check,
                correct_answer=problem["correct_answer"],
                expected_form=problem.get("expected_form", ""),
            )
            results.append(result)
            total_cost += response.cost

    duration = time.monotonic() - start_time

    run = BenchmarkRun(
        run_id=run_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
        models=models,
        problem_count=len(problems),
        results=results,
        total_cost=total_cost,
        total_duration_s=round(duration, 2),
    )

    save_results(run)
    return run


def save_results(run: BenchmarkRun) -> Path:
    """Write benchmark results to JSON + CSV in data/benchmark_results/."""
    out_dir = _project_root() / settings.benchmark_results_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    # JSON
    json_path = out_dir / f"run_{run.run_id}.json"
    with open(json_path, "w") as f:
        json.dump(run.model_dump(), f, indent=2)

    # CSV summary
    csv_path = out_dir / f"run_{run.run_id}.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "problem_id", "subject", "difficulty", "model_key",
            "answer", "correct_answer", "is_correct", "check_method",
            "confidence", "latency_ms", "cost", "error",
        ])
        for r in run.results:
            writer.writerow([
                r.problem_id, r.subject, r.difficulty, r.model_key,
                r.response.answer, r.correct_answer,
                r.check.is_correct, r.check.method,
                r.response.confidence, round(r.response.latency_ms, 1),
                round(r.response.cost, 6), r.response.error or "",
            ])

    logger.info("Results saved: %s, %s", json_path, csv_path)
    return json_path
