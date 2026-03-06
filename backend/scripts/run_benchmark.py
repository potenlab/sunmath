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

    # Generate report for a run
    python scripts/run_benchmark.py --report <run_id>

    # Run voting benchmark
    python scripts/run_benchmark.py --voting --thresholds 50,70,90

    # SymPy verification on existing run
    python scripts/run_benchmark.py --sympy-verify <run_id>
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
    BENCHMARK_MODELS,
    load_problems,
    run_full_benchmark,
)
from app.services.benchmark_analyzer import (
    generate_full_report,
    load_run,
)
from app.services.cross_verifier import (
    run_voting_benchmark,
    run_sympy_verification,
)


def progress(current: int, total: int, label: str):
    status = f"[{current}/{total}]"
    print(f"  {status} {label}", flush=True)


def cmd_dry_run(args):
    """Validate problem loading and model config without API calls."""
    models = args.models.split(",") if args.models else list(BENCHMARK_MODELS.keys())
    problem_ids = args.problems.split(",") if args.problems else None
    problems = load_problems(problem_ids)

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

    model_names = models or list(BENCHMARK_MODELS.keys())
    problems = load_problems(problem_ids)
    total = len(problems) * len(model_names)

    print(f"Starting benchmark: {len(model_names)} models x {len(problems)} problems = {total} calls")
    print()

    run = await run_full_benchmark(
        model_keys=models,
        problem_ids=problem_ids,
        progress_callback=progress,
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


def main():
    parser = argparse.ArgumentParser(description="SunMath LLM Benchmark CLI")
    parser.add_argument("--models", type=str, help="Comma-separated model keys (default: all)")
    parser.add_argument("--problems", type=str, help="Comma-separated problem IDs (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Validate setup without API calls")
    parser.add_argument("--report", type=str, metavar="RUN_ID", help="Generate report for a run")
    parser.add_argument("--voting", action="store_true", help="Run voting benchmark")
    parser.add_argument("--thresholds", type=str, help="Comma-separated thresholds for voting (default: 50,60,70,80,90)")
    parser.add_argument("--sympy-verify", type=str, metavar="RUN_ID", help="Run SymPy verification on a run")

    args = parser.parse_args()

    if args.dry_run:
        sys.exit(cmd_dry_run(args))
    elif args.report:
        sys.exit(cmd_report(args))
    elif args.sympy_verify:
        sys.exit(cmd_sympy_verify(args))
    elif args.voting:
        sys.exit(asyncio.run(cmd_voting(args)))
    else:
        sys.exit(asyncio.run(cmd_run(args)))


if __name__ == "__main__":
    main()
