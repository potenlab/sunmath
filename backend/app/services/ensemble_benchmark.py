"""Ensemble benchmark simulation using existing benchmark data.

Simulates multiple ensemble/voting strategies over pre-collected model responses
(6 models x 60 problems) and produces a comparison report.

No new API calls — purely offline analysis.
"""

import json
import logging
from collections import defaultdict
from pathlib import Path

from app.services.benchmark_runner import (
    _values_match,
    check_answer,
)
from app.services.cross_verifier import _answers_agree

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _project_root() -> Path:
    here = Path(__file__).resolve().parent  # app/services/
    return here.parent.parent.parent        # project root


def _load_problems_map() -> dict[str, dict]:
    """Load benchmark problems and return {problem_id: problem_dict}."""
    root = _project_root()
    path = root / "data" / "benchmark_problems.json"
    with open(path) as f:
        data = json.load(f)
    return {p["id"]: p for p in data["problems"]}


def _load_merged_results() -> dict[str, dict[str, dict]]:
    """Load and merge benchmark results from two runs.

    Attaches correct_answer_latex from the problems file to each result.

    Returns:
        {problem_id: {model_key: result_dict, ...}, ...}
    """
    root = _project_root()
    run1_path = root / "data" / "benchmark_results" / "run_20260308_063827.json"
    run2_path = root / "data" / "benchmark_results" / "run_20260309_045501.json"

    problems_map = _load_problems_map()
    merged: dict[str, dict[str, dict]] = defaultdict(dict)

    with open(run1_path) as f:
        run1 = json.load(f)
    for r in run1["results"]:
        # Skip deepseek-r1 from run 1 — run 2 has the fixed version
        if r["model_key"] == "deepseek-r1":
            continue
        # Attach correct_answer_latex from problems file
        prob = problems_map.get(r["problem_id"], {})
        r["correct_answer_latex"] = prob.get("correct_answer_latex", "")
        merged[r["problem_id"]][r["model_key"]] = r

    with open(run2_path) as f:
        run2 = json.load(f)
    for r in run2["results"]:
        prob = problems_map.get(r["problem_id"], {})
        r["correct_answer_latex"] = prob.get("correct_answer_latex", "")
        merged[r["problem_id"]][r["model_key"]] = r

    return dict(merged)


ALL_MODELS = [
    "deepseek-v3", "claude-sonnet", "gpt-4o", "o3-mini", "deepseek-r1", "qwen-2.5-72b",
]

# Ordered cheapest → most expensive (by avg cost per call)
COST_ORDER = [
    "qwen-2.5-72b", "deepseek-v3", "deepseek-r1", "gpt-4o", "o3-mini", "claude-sonnet",
]

TOP3_MODELS = ["claude-sonnet", "qwen-2.5-72b", "deepseek-r1"]

# ---------------------------------------------------------------------------
# Answer clustering
# ---------------------------------------------------------------------------

def _cluster_answers(
    answers: list[dict],
) -> list[list[dict]]:
    """Group answers into agreement clusters.

    Each answer dict must have: answer, answer_latex, weight, model_key, confidence.
    Returns list of clusters, each cluster is a list of answer dicts.
    """
    clusters: list[list[dict]] = []
    for ans in answers:
        placed = False
        for cluster in clusters:
            rep = cluster[0]
            if _answers_agree(
                ans["answer"], ans["answer_latex"],
                rep["answer"], rep["answer_latex"],
                "",  # correct_answer_latex not needed for inter-answer comparison
            ):
                cluster.append(ans)
                placed = True
                break
        if not placed:
            clusters.append([ans])
    return clusters


def _pick_winner(
    clusters: list[list[dict]],
    weighted: bool = False,
) -> dict | None:
    """Pick the winning cluster by vote count (or total weight if weighted)."""
    if not clusters:
        return None

    if weighted:
        best_cluster = max(
            clusters,
            key=lambda c: sum(a["weight"] for a in c),
        )
    else:
        best_cluster = max(clusters, key=len)

    # Return highest-confidence answer from the winning cluster as representative
    return max(best_cluster, key=lambda a: a.get("confidence", 0))


# ---------------------------------------------------------------------------
# Individual strategies
# ---------------------------------------------------------------------------

def _check_result(
    answer: str,
    answer_latex: str,
    result: dict,
) -> bool:
    """Check if an ensemble answer is correct against ground truth."""
    check = check_answer(
        model_answer=answer,
        model_answer_latex=answer_latex,
        correct_answer=result["correct_answer"],
        correct_answer_latex=result.get("correct_answer_latex", ""),
        expected_form=result.get("expected_form", ""),
    )
    return check.is_correct


def strategy_majority_vote_all(
    problem_results: dict[str, dict],
    any_result: dict,
) -> dict:
    """Majority vote across all 6 models."""
    answers = []
    total_cost = 0.0
    for mk in ALL_MODELS:
        r = problem_results.get(mk)
        if not r or r["response"].get("error"):
            continue
        answers.append({
            "answer": r["response"]["answer"],
            "answer_latex": r["response"].get("answer_latex", ""),
            "confidence": r["response"].get("confidence", 0),
            "weight": 1,
            "model_key": mk,
        })
        total_cost += r["response"].get("cost", 0)

    clusters = _cluster_answers(answers)
    winner = _pick_winner(clusters, weighted=False)
    if not winner:
        return {"answer": "", "correct": False, "cost": total_cost, "models_used": 0}

    correct = _check_result(winner["answer"], winner["answer_latex"], any_result)
    return {
        "answer": winner["answer"],
        "correct": correct,
        "cost": total_cost,
        "models_used": len(answers),
    }


def strategy_majority_vote_top3(
    problem_results: dict[str, dict],
    any_result: dict,
) -> dict:
    """Majority vote among the 3 most accurate models."""
    answers = []
    total_cost = 0.0
    for mk in TOP3_MODELS:
        r = problem_results.get(mk)
        if not r or r["response"].get("error"):
            continue
        answers.append({
            "answer": r["response"]["answer"],
            "answer_latex": r["response"].get("answer_latex", ""),
            "confidence": r["response"].get("confidence", 0),
            "weight": 1,
            "model_key": mk,
        })
        total_cost += r["response"].get("cost", 0)

    clusters = _cluster_answers(answers)
    winner = _pick_winner(clusters, weighted=False)
    if not winner:
        return {"answer": "", "correct": False, "cost": total_cost, "models_used": 0}

    correct = _check_result(winner["answer"], winner["answer_latex"], any_result)
    return {
        "answer": winner["answer"],
        "correct": correct,
        "cost": total_cost,
        "models_used": len(answers),
    }


def strategy_confidence_weighted(
    problem_results: dict[str, dict],
    any_result: dict,
) -> dict:
    """Confidence-weighted vote: weight = model's self-reported confidence (0-100)."""
    answers = []
    total_cost = 0.0
    for mk in ALL_MODELS:
        r = problem_results.get(mk)
        if not r or r["response"].get("error"):
            continue
        conf = r["response"].get("confidence", 50)
        answers.append({
            "answer": r["response"]["answer"],
            "answer_latex": r["response"].get("answer_latex", ""),
            "confidence": conf,
            "weight": conf,
            "model_key": mk,
        })
        total_cost += r["response"].get("cost", 0)

    clusters = _cluster_answers(answers)
    winner = _pick_winner(clusters, weighted=True)
    if not winner:
        return {"answer": "", "correct": False, "cost": total_cost, "models_used": 0}

    correct = _check_result(winner["answer"], winner["answer_latex"], any_result)
    return {
        "answer": winner["answer"],
        "correct": correct,
        "cost": total_cost,
        "models_used": len(answers),
    }


def strategy_accuracy_weighted(
    problem_results: dict[str, dict],
    any_result: dict,
    model_accuracy_by_bucket: dict[str, dict[str, float]],
) -> dict:
    """Accuracy-weighted vote: weight = model's historical accuracy for this subject+difficulty."""
    subject = any_result["subject"]
    difficulty = any_result["difficulty"]
    bucket = f"{subject}_{difficulty}"

    answers = []
    total_cost = 0.0
    for mk in ALL_MODELS:
        r = problem_results.get(mk)
        if not r or r["response"].get("error"):
            continue
        weight = model_accuracy_by_bucket.get(mk, {}).get(bucket, 0.5)
        answers.append({
            "answer": r["response"]["answer"],
            "answer_latex": r["response"].get("answer_latex", ""),
            "confidence": r["response"].get("confidence", 0),
            "weight": weight,
            "model_key": mk,
        })
        total_cost += r["response"].get("cost", 0)

    clusters = _cluster_answers(answers)
    winner = _pick_winner(clusters, weighted=True)
    if not winner:
        return {"answer": "", "correct": False, "cost": total_cost, "models_used": 0}

    correct = _check_result(winner["answer"], winner["answer_latex"], any_result)
    return {
        "answer": winner["answer"],
        "correct": correct,
        "cost": total_cost,
        "models_used": len(answers),
    }


def strategy_cascade(
    problem_results: dict[str, dict],
    any_result: dict,
    confidence_threshold: int = 85,
) -> dict:
    """Cascade: cheapest model first, escalate if confidence < threshold.

    Chain: deepseek-v3 → qwen-2.5-72b → claude-sonnet
    """
    cascade_chain = ["deepseek-v3", "qwen-2.5-72b", "claude-sonnet"]
    total_cost = 0.0
    models_used = 0

    for mk in cascade_chain:
        r = problem_results.get(mk)
        if not r or r["response"].get("error"):
            continue
        models_used += 1
        total_cost += r["response"].get("cost", 0)
        conf = r["response"].get("confidence", 0)
        if conf >= confidence_threshold or mk == cascade_chain[-1]:
            # Accept this answer
            answer = r["response"]["answer"]
            answer_latex = r["response"].get("answer_latex", "")
            correct = _check_result(answer, answer_latex, any_result)
            return {
                "answer": answer,
                "correct": correct,
                "cost": total_cost,
                "models_used": models_used,
            }

    return {"answer": "", "correct": False, "cost": total_cost, "models_used": models_used}


def strategy_best_per_subject(
    problem_results: dict[str, dict],
    any_result: dict,
    best_model_by_subject: dict[str, str],
) -> dict:
    """Oracle: pick the best model per subject (upper bound reference)."""
    subject = any_result["subject"]
    best_mk = best_model_by_subject.get(subject, "claude-sonnet")

    r = problem_results.get(best_mk)
    if not r or r["response"].get("error"):
        return {"answer": "", "correct": False, "cost": 0, "models_used": 0}

    answer = r["response"]["answer"]
    answer_latex = r["response"].get("answer_latex", "")
    correct = _check_result(answer, answer_latex, any_result)
    cost = r["response"].get("cost", 0)
    return {
        "answer": answer,
        "correct": correct,
        "cost": cost,
        "models_used": 1,
    }


# ---------------------------------------------------------------------------
# Pre-compute accuracy tables from the data
# ---------------------------------------------------------------------------

def _compute_accuracy_tables(
    merged: dict[str, dict[str, dict]],
) -> tuple[
    dict[str, dict[str, float]],  # model -> {bucket -> accuracy}
    dict[str, str],               # subject -> best_model
    dict[str, dict],              # model -> {correct, total, accuracy}
]:
    """Pre-compute per-model, per-bucket accuracy from the benchmark data."""
    # Per model per bucket
    bucket_stats: dict[str, dict[str, dict]] = defaultdict(
        lambda: defaultdict(lambda: {"correct": 0, "total": 0}),
    )
    # Per model overall
    overall: dict[str, dict] = defaultdict(lambda: {"correct": 0, "total": 0})
    # Per model per subject
    subject_stats: dict[str, dict[str, dict]] = defaultdict(
        lambda: defaultdict(lambda: {"correct": 0, "total": 0}),
    )

    for pid, models in merged.items():
        for mk, r in models.items():
            subject = r["subject"]
            difficulty = r["difficulty"]
            bucket = f"{subject}_{difficulty}"
            is_correct = r["check"]["is_correct"]

            bucket_stats[mk][bucket]["total"] += 1
            overall[mk]["total"] += 1
            subject_stats[mk][subject]["total"] += 1
            if is_correct:
                bucket_stats[mk][bucket]["correct"] += 1
                overall[mk]["correct"] += 1
                subject_stats[mk][subject]["correct"] += 1

    # Convert to accuracy fractions
    model_accuracy_by_bucket: dict[str, dict[str, float]] = {}
    for mk, buckets in bucket_stats.items():
        model_accuracy_by_bucket[mk] = {}
        for bucket, stats in buckets.items():
            total = stats["total"]
            model_accuracy_by_bucket[mk][bucket] = (
                stats["correct"] / total if total > 0 else 0.5
            )

    # Best model per subject
    best_model_by_subject: dict[str, str] = {}
    all_subjects = set()
    for mk, subjects in subject_stats.items():
        for subj in subjects:
            all_subjects.add(subj)

    for subj in all_subjects:
        best_mk = None
        best_acc = -1.0
        for mk in ALL_MODELS:
            stats = subject_stats.get(mk, {}).get(subj, {"correct": 0, "total": 0})
            total = stats["total"]
            acc = stats["correct"] / total if total > 0 else 0.0
            if acc > best_acc:
                best_acc = acc
                best_mk = mk
        if best_mk:
            best_model_by_subject[subj] = best_mk

    # Overall accuracy dict
    model_overall: dict[str, dict] = {}
    for mk in ALL_MODELS:
        stats = overall.get(mk, {"correct": 0, "total": 0})
        total = stats["total"]
        model_overall[mk] = {
            "correct": stats["correct"],
            "total": total,
            "accuracy": round(stats["correct"] / total * 100, 2) if total > 0 else 0,
        }

    return model_accuracy_by_bucket, best_model_by_subject, model_overall


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def _run_all_strategies(
    merged: dict[str, dict[str, dict]],
) -> dict:
    """Run all 6 strategies across all problems and return structured results."""
    accuracy_by_bucket, best_by_subject, model_overall = _compute_accuracy_tables(merged)

    strategies = {
        "majority_vote_all": {"correct": 0, "total": 0, "cost": 0.0, "results": []},
        "majority_vote_top3": {"correct": 0, "total": 0, "cost": 0.0, "results": []},
        "confidence_weighted": {"correct": 0, "total": 0, "cost": 0.0, "results": []},
        "accuracy_weighted": {"correct": 0, "total": 0, "cost": 0.0, "results": []},
        "cascade_85": {"correct": 0, "total": 0, "cost": 0.0, "results": []},
        "best_per_subject": {"correct": 0, "total": 0, "cost": 0.0, "results": []},
    }

    problem_ids = sorted(merged.keys())

    for pid in problem_ids:
        problem_results = merged[pid]
        # Use any model's result to get ground truth metadata
        any_result = next(iter(problem_results.values()))

        # Skip proof problems (no automated checking)
        if any_result.get("expected_form") == "proof":
            continue

        # --- Majority vote all 6 ---
        res = strategy_majority_vote_all(problem_results, any_result)
        strategies["majority_vote_all"]["total"] += 1
        strategies["majority_vote_all"]["cost"] += res["cost"]
        if res["correct"]:
            strategies["majority_vote_all"]["correct"] += 1
        strategies["majority_vote_all"]["results"].append({
            "problem_id": pid, **res,
            "subject": any_result["subject"],
            "difficulty": any_result["difficulty"],
        })

        # --- Majority vote top 3 ---
        res = strategy_majority_vote_top3(problem_results, any_result)
        strategies["majority_vote_top3"]["total"] += 1
        strategies["majority_vote_top3"]["cost"] += res["cost"]
        if res["correct"]:
            strategies["majority_vote_top3"]["correct"] += 1
        strategies["majority_vote_top3"]["results"].append({
            "problem_id": pid, **res,
            "subject": any_result["subject"],
            "difficulty": any_result["difficulty"],
        })

        # --- Confidence-weighted ---
        res = strategy_confidence_weighted(problem_results, any_result)
        strategies["confidence_weighted"]["total"] += 1
        strategies["confidence_weighted"]["cost"] += res["cost"]
        if res["correct"]:
            strategies["confidence_weighted"]["correct"] += 1
        strategies["confidence_weighted"]["results"].append({
            "problem_id": pid, **res,
            "subject": any_result["subject"],
            "difficulty": any_result["difficulty"],
        })

        # --- Accuracy-weighted ---
        res = strategy_accuracy_weighted(problem_results, any_result, accuracy_by_bucket)
        strategies["accuracy_weighted"]["total"] += 1
        strategies["accuracy_weighted"]["cost"] += res["cost"]
        if res["correct"]:
            strategies["accuracy_weighted"]["correct"] += 1
        strategies["accuracy_weighted"]["results"].append({
            "problem_id": pid, **res,
            "subject": any_result["subject"],
            "difficulty": any_result["difficulty"],
        })

        # --- Cascade ---
        res = strategy_cascade(problem_results, any_result, confidence_threshold=85)
        strategies["cascade_85"]["total"] += 1
        strategies["cascade_85"]["cost"] += res["cost"]
        if res["correct"]:
            strategies["cascade_85"]["correct"] += 1
        strategies["cascade_85"]["results"].append({
            "problem_id": pid, **res,
            "subject": any_result["subject"],
            "difficulty": any_result["difficulty"],
        })

        # --- Best per subject ---
        res = strategy_best_per_subject(problem_results, any_result, best_by_subject)
        strategies["best_per_subject"]["total"] += 1
        strategies["best_per_subject"]["cost"] += res["cost"]
        if res["correct"]:
            strategies["best_per_subject"]["correct"] += 1
        strategies["best_per_subject"]["results"].append({
            "problem_id": pid, **res,
            "subject": any_result["subject"],
            "difficulty": any_result["difficulty"],
        })

    return {
        "strategies": strategies,
        "model_overall": model_overall,
        "best_by_subject": best_by_subject,
    }


def _format_report(data: dict) -> str:
    """Format the ensemble comparison into a readable report."""
    strategies = data["strategies"]
    model_overall = data["model_overall"]
    best_by_subject = data["best_by_subject"]

    lines: list[str] = []
    lines.append("=" * 80)
    lines.append("ENSEMBLE BENCHMARK SIMULATION REPORT")
    lines.append("=" * 80)
    lines.append("")

    # --- Individual model baselines ---
    lines.append("INDIVIDUAL MODEL BASELINES")
    lines.append("-" * 60)
    lines.append(f"{'Model':<20} {'Correct':>8} {'Total':>6} {'Accuracy':>10} {'Rank':>6}")
    lines.append("-" * 60)

    sorted_models = sorted(
        model_overall.items(),
        key=lambda x: -x[1]["accuracy"],
    )
    best_single_accuracy = sorted_models[0][1]["accuracy"]
    for rank, (mk, stats) in enumerate(sorted_models, 1):
        lines.append(
            f"{mk:<20} {stats['correct']:>8} {stats['total']:>6} "
            f"{stats['accuracy']:>9.1f}% {rank:>6}"
        )
    lines.append(f"\nBest single model: {sorted_models[0][0]} @ {best_single_accuracy:.1f}%")
    lines.append("")

    # --- Ensemble strategy comparison ---
    lines.append("ENSEMBLE STRATEGY COMPARISON")
    lines.append("-" * 80)
    lines.append(
        f"{'Strategy':<25} {'Correct':>8} {'Total':>6} {'Accuracy':>10} "
        f"{'vs Best':>8} {'Cost':>10}"
    )
    lines.append("-" * 80)

    strategy_order = [
        ("majority_vote_all", "Majority Vote (all 6)"),
        ("majority_vote_top3", "Majority Vote (top 3)"),
        ("confidence_weighted", "Confidence-Weighted"),
        ("accuracy_weighted", "Accuracy-Weighted"),
        ("cascade_85", "Cascade (conf>=85)"),
        ("best_per_subject", "Best-per-Subject *"),
    ]

    for key, label in strategy_order:
        s = strategies[key]
        total = s["total"]
        acc = s["correct"] / total * 100 if total > 0 else 0
        delta = acc - best_single_accuracy
        delta_str = f"+{delta:.1f}%" if delta >= 0 else f"{delta:.1f}%"
        lines.append(
            f"{label:<25} {s['correct']:>8} {total:>6} {acc:>9.1f}% "
            f"{delta_str:>8} ${s['cost']:>9.4f}"
        )

    lines.append("")
    lines.append("* Best-per-Subject is an oracle upper bound (not a practical strategy)")
    lines.append("")

    # --- Best model per subject ---
    lines.append("BEST MODEL PER SUBJECT (Oracle Selection)")
    lines.append("-" * 40)
    for subj, mk in sorted(best_by_subject.items()):
        lines.append(f"  {subj:<30} {mk}")
    lines.append("")

    # --- By difficulty breakdown ---
    lines.append("ACCURACY BY DIFFICULTY")
    lines.append("-" * 80)

    difficulties = ["easy", "medium", "hard"]
    header = f"{'Strategy':<25}"
    for d in difficulties:
        header += f" {d:>10}"
    lines.append(header)
    lines.append("-" * 80)

    # Individual models
    for mk, _ in sorted_models:
        row = f"{mk:<25}"
        for diff in difficulties:
            diff_results = [
                r for pid, models in _load_merged_results_cached().items()
                for mk2, r in models.items()
                if mk2 == mk and r["difficulty"] == diff
                and r.get("expected_form") != "proof"
            ]
            correct = sum(1 for r in diff_results if r["check"]["is_correct"])
            total = len(diff_results)
            acc = correct / total * 100 if total > 0 else 0
            row += f" {acc:>9.1f}%"
        lines.append(row)

    lines.append("")

    # Ensemble strategies
    for key, label in strategy_order:
        s = strategies[key]
        row = f"{label:<25}"
        for diff in difficulties:
            diff_results = [r for r in s["results"] if r["difficulty"] == diff]
            correct = sum(1 for r in diff_results if r["correct"])
            total = len(diff_results)
            acc = correct / total * 100 if total > 0 else 0
            row += f" {acc:>9.1f}%"
        lines.append(row)

    lines.append("")

    # --- Problems where ensemble beats/loses vs best single model ---
    lines.append("ENSEMBLE vs BEST SINGLE MODEL — PROBLEM-LEVEL DETAIL")
    lines.append("-" * 80)

    # Use majority_vote_all as the primary ensemble to compare
    best_mk = sorted_models[0][0]
    merged = _load_merged_results_cached()

    ensemble_wins = []
    ensemble_losses = []
    for res in strategies["majority_vote_all"]["results"]:
        pid = res["problem_id"]
        best_r = merged.get(pid, {}).get(best_mk)
        if not best_r:
            continue
        best_correct = best_r["check"]["is_correct"]
        ens_correct = res["correct"]
        if ens_correct and not best_correct:
            ensemble_wins.append(pid)
        elif not ens_correct and best_correct:
            ensemble_losses.append(pid)

    lines.append(f"\nMajority Vote (all 6) vs {best_mk}:")
    lines.append(f"  Ensemble wins (correct where best model wrong): {len(ensemble_wins)}")
    if ensemble_wins:
        lines.append(f"    {', '.join(ensemble_wins)}")
    lines.append(f"  Ensemble losses (wrong where best model correct): {len(ensemble_losses)}")
    if ensemble_losses:
        lines.append(f"    {', '.join(ensemble_losses)}")
    lines.append("")

    # --- Cascade analysis ---
    lines.append("CASCADE STRATEGY ANALYSIS")
    lines.append("-" * 60)
    cascade_results = strategies["cascade_85"]["results"]
    models_used_counts = defaultdict(int)
    for r in cascade_results:
        models_used_counts[r["models_used"]] += 1
    lines.append(f"  Confidence threshold: 85")
    lines.append(f"  Chain: deepseek-v3 → qwen-2.5-72b → claude-sonnet")
    for n_models in sorted(models_used_counts.keys()):
        count = models_used_counts[n_models]
        pct = count / len(cascade_results) * 100
        lines.append(f"  Stopped at model {n_models}: {count} problems ({pct:.0f}%)")

    cascade_cost = strategies["cascade_85"]["cost"]
    all6_cost = strategies["majority_vote_all"]["cost"]
    lines.append(f"  Total cost: ${cascade_cost:.4f} vs all-6 cost: ${all6_cost:.4f}")
    if all6_cost > 0:
        savings = (1 - cascade_cost / all6_cost) * 100
        lines.append(f"  Cost savings: {savings:.0f}%")
    lines.append("")

    # --- Conclusions ---
    lines.append("CONCLUSIONS")
    lines.append("-" * 60)

    # Find best ensemble
    best_ensemble_key = None
    best_ensemble_acc = 0
    for key, _ in strategy_order:
        s = strategies[key]
        total = s["total"]
        acc = s["correct"] / total * 100 if total > 0 else 0
        if acc > best_ensemble_acc:
            best_ensemble_acc = acc
            best_ensemble_key = key

    best_label = dict(strategy_order).get(best_ensemble_key, best_ensemble_key)
    delta = best_ensemble_acc - best_single_accuracy

    if delta > 0:
        lines.append(
            f"  Best ensemble strategy: {best_label} at {best_ensemble_acc:.1f}% "
            f"(+{delta:.1f}% over best single model)"
        )
        lines.append("  Ensembles DO improve accuracy over the best individual model.")
    elif delta == 0:
        lines.append(
            f"  Best ensemble strategy: {best_label} at {best_ensemble_acc:.1f}% "
            f"(matches best single model)"
        )
        lines.append("  Ensembles match but do not improve over the best individual model.")
    else:
        lines.append(
            f"  Best ensemble strategy: {best_label} at {best_ensemble_acc:.1f}% "
            f"({delta:.1f}% vs best single model)"
        )
        lines.append("  Ensembles do NOT improve over the best individual model.")

    # Cost-effectiveness
    cascade_acc = strategies["cascade_85"]["correct"] / strategies["cascade_85"]["total"] * 100
    lines.append(f"\n  Cascade strategy: {cascade_acc:.1f}% accuracy at ${cascade_cost:.4f}")
    lines.append(f"  Best single model ({sorted_models[0][0]}): {best_single_accuracy:.1f}%")

    lines.append("")
    lines.append("=" * 80)

    return "\n".join(lines)


# Cache for repeated access during report generation
_merged_cache: dict[str, dict[str, dict]] | None = None


def _load_merged_results_cached() -> dict[str, dict[str, dict]]:
    global _merged_cache
    if _merged_cache is None:
        _merged_cache = _load_merged_results()
    return _merged_cache


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

async def main():
    """Run the ensemble benchmark simulation and print the report."""
    logging.basicConfig(level=logging.WARNING)

    print("Loading benchmark data...")
    merged = _load_merged_results()
    global _merged_cache
    _merged_cache = merged

    print(f"Loaded {len(merged)} problems across {len(ALL_MODELS)} models")
    print("Running ensemble simulations...\n")

    data = _run_all_strategies(merged)
    report = _format_report(data)
    print(report)

    # Save report to file
    out_path = _project_root() / "data" / "benchmark_results" / "ensemble_report.txt"
    with open(out_path, "w") as f:
        f.write(report)
    print(f"\nReport saved to: {out_path}")

    # Also save raw data as JSON
    json_path = _project_root() / "data" / "benchmark_results" / "ensemble_results.json"
    # Strip per-problem results for a cleaner summary JSON
    summary = {}
    for key, s in data["strategies"].items():
        total = s["total"]
        summary[key] = {
            "correct": s["correct"],
            "total": total,
            "accuracy": round(s["correct"] / total * 100, 2) if total > 0 else 0,
            "cost": round(s["cost"], 6),
        }
    summary["model_baselines"] = data["model_overall"]
    summary["best_model_per_subject"] = data["best_by_subject"]

    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Summary JSON saved to: {json_path}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
