"""Benchmark analysis: accuracy matrix, cost analysis, model recommendations."""

import json
import logging
from collections import defaultdict
from pathlib import Path

from app.config import settings
from app.schemas.llm_benchmark import (
    AccuracyCell,
    AccuracyMatrix,
    BenchmarkReport,
    BenchmarkRun,
    CostCell,
    CostMatrix,
    SubjectRecommendation,
)
from app.services.benchmark_runner import BENCHMARK_MODELS, _project_root

logger = logging.getLogger(__name__)


def load_run(run_id: str) -> BenchmarkRun:
    """Load a benchmark run from JSON."""
    path = _project_root() / settings.benchmark_results_dir / f"run_{run_id}.json"
    with open(path) as f:
        data = json.load(f)
    return BenchmarkRun(**data)


def load_latest_run() -> BenchmarkRun | None:
    """Load the most recent benchmark run."""
    out_dir = _project_root() / settings.benchmark_results_dir
    json_files = sorted(out_dir.glob("run_*.json"), reverse=True)
    if not json_files:
        return None
    with open(json_files[0]) as f:
        data = json.load(f)
    return BenchmarkRun(**data)


def list_runs() -> list[dict]:
    """List all completed benchmark runs (metadata only)."""
    out_dir = _project_root() / settings.benchmark_results_dir
    runs = []
    for path in sorted(out_dir.glob("run_*.json"), reverse=True):
        with open(path) as f:
            data = json.load(f)
        runs.append({
            "run_id": data["run_id"],
            "timestamp": data["timestamp"],
            "models": data["models"],
            "problem_count": data["problem_count"],
            "total_cost": data.get("total_cost", 0),
        })
    return runs


def _build_accuracy_cell(correct: int, total: int) -> AccuracyCell:
    return AccuracyCell(
        accuracy=round(correct / total * 100, 2) if total > 0 else 0.0,
        correct=correct,
        total=total,
    )


def compute_accuracy_matrix(run: BenchmarkRun) -> AccuracyMatrix:
    """Compute model x subject/difficulty accuracy percentages."""
    # Counters: model -> group -> (correct, total)
    by_subject: dict[str, dict[str, list[int]]] = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    by_difficulty: dict[str, dict[str, list[int]]] = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    overall: dict[str, list[int]] = defaultdict(lambda: [0, 0])

    for r in run.results:
        if r.check.method == "needs_manual_review":
            continue

        by_subject[r.model_key][r.subject][1] += 1
        by_difficulty[r.model_key][r.difficulty][1] += 1
        overall[r.model_key][1] += 1

        if r.check.is_correct:
            by_subject[r.model_key][r.subject][0] += 1
            by_difficulty[r.model_key][r.difficulty][0] += 1
            overall[r.model_key][0] += 1

    return AccuracyMatrix(
        by_subject={
            model: {
                subj: _build_accuracy_cell(counts[0], counts[1])
                for subj, counts in subjects.items()
            }
            for model, subjects in by_subject.items()
        },
        by_difficulty={
            model: {
                diff: _build_accuracy_cell(counts[0], counts[1])
                for diff, counts in diffs.items()
            }
            for model, diffs in by_difficulty.items()
        },
        overall={
            model: _build_accuracy_cell(counts[0], counts[1])
            for model, counts in overall.items()
        },
    )


def compute_cost_matrix(run: BenchmarkRun) -> CostMatrix:
    """Compute average cost per problem per model."""
    by_model: dict[str, list[float]] = defaultdict(list)
    by_model_subject: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))

    for r in run.results:
        by_model[r.model_key].append(r.response.cost)
        by_model_subject[r.model_key][r.subject].append(r.response.cost)

    def _cell(costs: list[float]) -> CostCell:
        total = sum(costs)
        return CostCell(
            avg_cost=round(total / len(costs), 6) if costs else 0,
            total_cost=round(total, 6),
            count=len(costs),
        )

    return CostMatrix(
        by_model={m: _cell(costs) for m, costs in by_model.items()},
        by_model_subject={
            m: {s: _cell(costs) for s, costs in subjects.items()}
            for m, subjects in by_model_subject.items()
        },
    )


def recommend_optimal_models(
    accuracy: AccuracyMatrix,
    costs: CostMatrix,
    run: BenchmarkRun,
) -> list[SubjectRecommendation]:
    """For each subject, pick the best model by weighted score."""
    subjects: set[str] = set()
    for model_subjects in accuracy.by_subject.values():
        subjects.update(model_subjects.keys())

    # Compute avg latency per model
    latency_by_model: dict[str, list[float]] = defaultdict(list)
    for r in run.results:
        latency_by_model[r.model_key].append(r.response.latency_ms)
    avg_latency = {
        m: sum(lats) / len(lats) if lats else 0
        for m, lats in latency_by_model.items()
    }

    # Normalize latency and cost for scoring
    max_latency = max(avg_latency.values()) if avg_latency else 1
    max_cost = max(
        (c.avg_cost for c in costs.by_model.values()),
        default=1,
    ) or 1

    recommendations = []
    for subject in sorted(subjects):
        best_score = -1.0
        best_model = ""
        best_acc = 0.0
        best_cost_val = 0.0

        # Check if reasoning models outperform standard by >10%
        reasoning_acc = []
        standard_acc = []

        for model_key in accuracy.by_subject:
            cell = accuracy.by_subject[model_key].get(subject)
            if not cell:
                continue

            model_type = BENCHMARK_MODELS.get(model_key, {}).get("type", "standard")
            if model_type == "reasoning":
                reasoning_acc.append(cell.accuracy)
            else:
                standard_acc.append(cell.accuracy)

            # Weighted score: accuracy 0.6, cost 0.2, latency 0.2
            cost_cell = costs.by_model.get(model_key)
            norm_cost = (cost_cell.avg_cost / max_cost) if cost_cell else 1
            norm_lat = (avg_latency.get(model_key, max_latency) / max_latency)

            score = (
                cell.accuracy / 100 * 0.6
                + (1 - norm_cost) * 0.2
                + (1 - norm_lat) * 0.2
            )

            if score > best_score:
                best_score = score
                best_model = model_key
                best_acc = cell.accuracy
                best_cost_val = cost_cell.avg_cost if cost_cell else 0

        avg_reasoning = sum(reasoning_acc) / len(reasoning_acc) if reasoning_acc else 0
        avg_standard = sum(standard_acc) / len(standard_acc) if standard_acc else 0
        reasoning_advantage = avg_reasoning > avg_standard + 10

        recommendations.append(SubjectRecommendation(
            subject=subject,
            best_model=best_model,
            accuracy=best_acc,
            avg_cost=round(best_cost_val, 6),
            reasoning_advantage=reasoning_advantage,
        ))

    return recommendations


def generate_full_report(run: BenchmarkRun) -> BenchmarkReport:
    """Generate a complete analysis report for a benchmark run."""
    accuracy = compute_accuracy_matrix(run)
    costs = compute_cost_matrix(run)
    recommendations = recommend_optimal_models(accuracy, costs, run)

    # Build summary
    overall_lines = []
    for model, cell in sorted(accuracy.overall.items(), key=lambda x: -x[1].accuracy):
        cost_cell = costs.by_model.get(model)
        cost_str = f"${cost_cell.total_cost:.4f}" if cost_cell else "N/A"
        overall_lines.append(f"  {model}: {cell.accuracy}% ({cell.correct}/{cell.total}) | cost: {cost_str}")

    reasoning_flags = [r for r in recommendations if r.reasoning_advantage]
    reasoning_note = ""
    if reasoning_flags:
        subjects = ", ".join(r.subject for r in reasoning_flags)
        reasoning_note = f"\nReasoning models outperform by >10% in: {subjects}"

    summary = (
        f"Benchmark {run.run_id}: {run.problem_count} problems x {len(run.models)} models\n"
        f"Total cost: ${run.total_cost:.4f} | Duration: {run.total_duration_s}s\n\n"
        f"Overall accuracy:\n" + "\n".join(overall_lines) + reasoning_note
    )

    return BenchmarkReport(
        run_id=run.run_id,
        accuracy=accuracy,
        costs=costs,
        recommendations=recommendations,
        summary=summary,
    )
