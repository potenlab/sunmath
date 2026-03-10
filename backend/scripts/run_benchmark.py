"""CLI script for running LLM benchmarks.

Usage:
    cd backend
    source .venv/bin/activate

    # Dry run (validate setup, no API calls)
    python scripts/run_benchmark.py --dry-run

    # Smoke test: 2 problems, 1 model
    python scripts/run_benchmark.py --models deepseek-v3 --problems ALG-E01,ALG-E02

    # Full benchmark: all 6 models x 60 problems
    python scripts/run_benchmark.py

    # CSAT 2026 benchmark: all 6 models x 46 problems
    python scripts/run_benchmark.py --dataset csat-2026

    # CSAT 2026 dry run
    python scripts/run_benchmark.py --dataset csat-2026 --dry-run

    # Generate report for a run
    python scripts/run_benchmark.py --report <run_id>

    # Run voting benchmark
    python scripts/run_benchmark.py --voting --thresholds 50,70,90

    # SymPy verification on existing run
    python scripts/run_benchmark.py --sympy-verify <run_id>

    # Retry only failed entries from a previous run
    python scripts/run_benchmark.py --retry-failed <run_id>

    # Retry only claude-sonnet failures
    python scripts/run_benchmark.py --retry-failed <run_id> --models claude-sonnet
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings
from app.services.benchmark_runner import (
    BENCHMARK_DATASETS,
    BENCHMARK_MODELS,
    call_model,
    check_answer,
    load_problems,
    run_full_benchmark,
    save_results,
    _format_problem_content,
)
from app.services.benchmark_analyzer import (
    generate_full_report,
    load_run,
)
from app.services.cross_verifier import (
    run_voting_benchmark,
    run_sympy_verification,
)
from app.schemas.llm_benchmark import ProblemResult


def progress(current: int, total: int, label: str):
    status = f"[{current}/{total}]"
    print(f"  {status} {label}", flush=True)


def cmd_dry_run(args):
    """Validate problem loading and model config without API calls."""
    models = args.models.split(",") if args.models else list(BENCHMARK_MODELS.keys())
    problem_ids = args.problems.split(",") if args.problems else None
    dataset = args.dataset
    problems = load_problems(problem_ids, dataset=dataset)

    print(f"Dataset: {dataset} ({BENCHMARK_DATASETS[dataset]})")

    print(f"Models ({len(models)}):")
    for m in models:
        if m not in BENCHMARK_MODELS:
            print(f"  {m} -- UNKNOWN MODEL KEY")
            continue
        info = BENCHMARK_MODELS[m]
        print(f"  {m}: {info['id']} ({info['type']}) "
              f"${info['input_cost_per_m']}/{info['output_cost_per_m']} per M tokens")

    print(f"\nProblems ({len(problems)}):")
    for p in problems[:5]:
        print(f"  {p['id']}: {p['subject']}/{p['difficulty']} -- {p['content'][:60]}...")
    if len(problems) > 5:
        print(f"  ... and {len(problems) - 5} more")

    total = len(problems) * len(models)
    print(f"\nTotal API calls: {total}")
    print(f"LLM API key: {'set' if settings.llm_api_key else 'NOT SET'}")
    print(f"LLM base URL: {settings.llm_base_url}")
    print(f"Results dir: {settings.benchmark_results_dir}")

    if not settings.llm_api_key:
        print("\nWARNING: LLM_API_KEY is not set. Benchmark will fail.")
        return 1
    print("\nDry run OK. Ready to benchmark.")
    return 0


async def cmd_run(args):
    """Run the full benchmark."""
    models = args.models.split(",") if args.models else None
    problem_ids = args.problems.split(",") if args.problems else None
    dataset = args.dataset

    model_names = models or list(BENCHMARK_MODELS.keys())
    problems = load_problems(problem_ids, dataset=dataset)
    total = len(problems) * len(model_names)

    print(f"Dataset: {dataset}")
    print(f"Starting benchmark: {len(model_names)} models x {len(problems)} problems = {total} calls")
    print()

    run = await run_full_benchmark(
        model_keys=models,
        problem_ids=problem_ids,
        progress_callback=progress,
        dataset=dataset,
    )

    print(f"\nBenchmark complete!")
    print(f"  Run ID: {run.run_id}")
    print(f"  Total cost: ${run.total_cost:.4f}")
    print(f"  Duration: {run.total_duration_s}s")
    print(f"  Results saved to: {settings.benchmark_results_dir}/run_{run.run_id}.*")

    # Quick accuracy summary
    from app.services.benchmark_analyzer import compute_accuracy_matrix
    accuracy = compute_accuracy_matrix(run)
    print("\nOverall accuracy:")
    for model, cell in sorted(accuracy.overall.items(), key=lambda x: -x[1].accuracy):
        print(f"  {model}: {cell.accuracy}% ({cell.correct}/{cell.total})")

    return 0


def cmd_report(args):
    """Generate a report for an existing run."""
    run_id = args.report
    try:
        run = load_run(run_id)
    except FileNotFoundError:
        print(f"Run {run_id} not found in {settings.benchmark_results_dir}/")
        return 1

    report = generate_full_report(run)
    print(report.summary)

    print("\nAccuracy by subject:")
    for model, subjects in report.accuracy.by_subject.items():
        cells = " | ".join(f"{s}: {c.accuracy}%" for s, c in sorted(subjects.items()))
        print(f"  {model}: {cells}")

    print("\nRecommendations:")
    for rec in report.recommendations:
        flag = " [reasoning advantage]" if rec.reasoning_advantage else ""
        print(f"  {rec.subject}: {rec.best_model} ({rec.accuracy}%, ${rec.avg_cost:.6f}/problem){flag}")

    # Save report JSON
    out_dir = Path(settings.benchmark_results_dir)
    report_path = out_dir / f"report_{run_id}.json"
    with open(report_path, "w") as f:
        json.dump(report.model_dump(), f, indent=2)
    print(f"\nFull report saved to: {report_path}")
    return 0


async def cmd_voting(args):
    """Run voting benchmark."""
    problem_ids = args.problems.split(",") if args.problems else None
    thresholds = [int(t) for t in args.thresholds.split(",")] if args.thresholds else None

    print("Starting voting benchmark...")
    if thresholds:
        print(f"  Thresholds: {thresholds}")
    print()

    result = await run_voting_benchmark(
        problem_ids=problem_ids,
        thresholds=thresholds,
        progress_callback=progress,
    )

    print(f"\nVoting benchmark complete!")
    print(f"  Run ID: {result.run_id}")
    print(f"  Best threshold: {result.comparison.best_threshold}")
    print(f"  Best accuracy: {result.comparison.best_accuracy}%")
    print(f"  Best cost: ${result.comparison.best_cost:.4f}")

    print("\nThreshold comparison:")
    for t in result.comparison.thresholds:
        print(f"  threshold={t.threshold}: {t.accuracy}% accuracy, "
              f"${t.total_cost:.4f} cost, {t.avg_steps} avg steps, "
              f"{t.manual_review_count} manual reviews")

    # Save
    out_dir = Path(settings.benchmark_results_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / f"voting_{result.run_id}.json", "w") as f:
        json.dump(result.model_dump(), f, indent=2)
    print(f"\nResults saved to: {out_dir}/voting_{result.run_id}.json")
    return 0


def cmd_sympy_verify(args):
    """Run SymPy verification on an existing run."""
    run_id = args.sympy_verify
    try:
        run = load_run(run_id)
    except FileNotFoundError:
        print(f"Run {run_id} not found in {settings.benchmark_results_dir}/")
        return 1

    report = run_sympy_verification(run)

    print(f"SymPy Verification Report for run {run_id}")
    print(f"  Total checked: {report.total_checked}")
    print(f"  Parse success rate: {report.sympy_parse_success_rate}%")
    print(f"  Accuracy with SymPy: {report.accuracy_with_sympy}%")
    print(f"  Accuracy without SymPy: {report.accuracy_without_sympy}%")

    print("\nBy subject:")
    for subj, stats in sorted(report.by_subject.items()):
        print(f"  {subj}: parse={stats['parse_rate']}%, accuracy={stats['accuracy']}%")

    print("\nBy expected form:")
    for form, stats in sorted(report.by_expected_form.items()):
        print(f"  {form}: parse={stats['parse_rate']}%, accuracy={stats['accuracy']}%")

    # Save
    out_dir = Path(settings.benchmark_results_dir)
    report_path = out_dir / f"sympy_verify_{run_id}.json"
    with open(report_path, "w") as f:
        json.dump(report.model_dump(), f, indent=2)
    print(f"\nFull report saved to: {report_path}")
    return 0


async def cmd_retry_failed(args):
    """Retry only failed entries from a previous run, merge results back."""
    run_id = args.retry_failed
    try:
        run = load_run(run_id)
    except FileNotFoundError:
        print(f"Run {run_id} not found in {settings.benchmark_results_dir}/")
        return 1

    # Find failed entries
    failed_indices = []
    for i, r in enumerate(run.results):
        if r.response.error:
            failed_indices.append(i)

    if not failed_indices:
        print(f"No failures in run {run_id}. Nothing to retry.")
        return 0

    # Optional model filter
    model_filter = set(args.models.split(",")) if args.models else None

    # Build retry list
    retry_list = []
    for i in failed_indices:
        r = run.results[i]
        if model_filter and r.model_key not in model_filter:
            continue
        retry_list.append((i, r))

    if not retry_list:
        print("No matching failures to retry after applying model filter.")
        return 0

    # Load problem data for re-checking answers
    problems_data = load_problems(dataset=run.dataset)
    problems_by_id = {p["id"]: p for p in problems_data}

    print(f"Retrying {len(retry_list)} failed entries from run {run_id}")
    from collections import Counter
    model_counts = Counter(r.model_key for _, r in retry_list)
    for model, count in model_counts.most_common():
        print(f"  {model}: {count}")
    print()

    success_count = 0
    still_failed = 0

    for task_num, (idx, old_result) in enumerate(retry_list, 1):
        problem = problems_by_id.get(old_result.problem_id)
        if not problem:
            print(f"  [{task_num}/{len(retry_list)}] {old_result.problem_id} x {old_result.model_key} -- problem not found, skipping")
            continue

        print(f"  [{task_num}/{len(retry_list)}] {old_result.problem_id} x {old_result.model_key}", end="", flush=True)

        prompt_content = _format_problem_content(problem)
        response = await call_model(old_result.model_key, prompt_content)

        check = check_answer(
            model_answer=response.answer,
            model_answer_latex=response.answer_latex,
            correct_answer=problem["correct_answer"],
            correct_answer_latex=problem.get("correct_answer_latex", ""),
            expected_form=problem.get("expected_form", ""),
            model_error=response.error,
        )

        new_result = ProblemResult(
            problem_id=old_result.problem_id,
            subject=old_result.subject,
            difficulty=old_result.difficulty,
            model_key=old_result.model_key,
            model_id=old_result.model_id,
            response=response,
            check=check,
            correct_answer=old_result.correct_answer,
            expected_form=old_result.expected_form,
        )

        # Replace in-place
        run.results[idx] = new_result

        if response.error:
            print(f" -- STILL FAILED: {response.error[:80]}")
            still_failed += 1
        else:
            correct_mark = "correct" if check.is_correct else f"wrong (got {response.answer})"
            print(f" -- OK: {correct_mark}")
            success_count += 1

    # Recalculate total cost
    run.total_cost = sum(r.response.cost for r in run.results)

    # Save merged results (overwrite original)
    save_results(run)

    remaining_errors = sum(1 for r in run.results if r.response.error)
    print(f"\nRetry complete:")
    print(f"  Recovered: {success_count}/{len(retry_list)}")
    print(f"  Still failed: {still_failed}")
    print(f"  Total errors remaining: {remaining_errors}/{len(run.results)}")
    print(f"  Updated cost: ${run.total_cost:.4f}")
    print(f"  Results saved to: {settings.benchmark_results_dir}/run_{run.run_id}.*")

    return 0


def main():
    parser = argparse.ArgumentParser(description="SunMath LLM Benchmark CLI")
    parser.add_argument("--models", type=str, help="Comma-separated model keys (default: all)")
    parser.add_argument("--problems", type=str, help="Comma-separated problem IDs (default: all)")
    parser.add_argument(
        "--dataset", type=str, default="original",
        choices=list(BENCHMARK_DATASETS.keys()),
        help=f"Benchmark dataset to use (default: original). Available: {', '.join(BENCHMARK_DATASETS)}",
    )
    parser.add_argument("--dry-run", action="store_true", help="Validate setup without API calls")
    parser.add_argument("--report", type=str, metavar="RUN_ID", help="Generate report for a run")
    parser.add_argument("--voting", action="store_true", help="Run voting benchmark")
    parser.add_argument("--thresholds", type=str, help="Comma-separated thresholds for voting (default: 50,60,70,80,90)")
    parser.add_argument("--sympy-verify", type=str, metavar="RUN_ID", help="Run SymPy verification on a run")
    parser.add_argument("--retry-failed", type=str, metavar="RUN_ID", help="Retry failed entries from a previous run and merge results")

    args = parser.parse_args()

    if args.dry_run:
        sys.exit(cmd_dry_run(args))
    elif args.report:
        sys.exit(cmd_report(args))
    elif args.sympy_verify:
        sys.exit(cmd_sympy_verify(args))
    elif args.voting:
        sys.exit(asyncio.run(cmd_voting(args)))
    elif args.retry_failed:
        sys.exit(asyncio.run(cmd_retry_failed(args)))
    else:
        sys.exit(asyncio.run(cmd_run(args)))


if __name__ == "__main__":
    main()
