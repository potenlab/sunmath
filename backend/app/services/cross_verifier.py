"""Cross-verification: voting flow, threshold testing, and SymPy verification layer."""

import logging
import time
from collections import defaultdict
from datetime import datetime, timezone

from app.schemas.llm_benchmark import (
    AccuracyCell,
    AnswerCheckResult,
    BenchmarkRun,
    StrategyComparison,
    SympyVerificationReport,
    SympyVerificationResult,
    ThresholdResult,
    VoteStep,
    VotingBenchmarkResult,
    VotingResult,
)
from app.services.benchmark_runner import (
    BENCHMARK_MODELS,
    call_model,
    check_answer,
    load_problems,
)
from app.services.llm_router import LLMRouter
from app.services.sympy_engine import SympyEngine

logger = logging.getLogger(__name__)

# Voting chain: cheapest -> mid-quality -> high-quality
PRIMARY_MODEL = "deepseek-v3"
SECONDARY_MODEL = "claude-sonnet"
TERTIARY_MODEL = "gpt-4o"


def _answers_agree(
    answer1: str,
    answer1_latex: str,
    answer2: str,
    answer2_latex: str,
    correct_answer_latex: str,
) -> bool:
    """Check if two model answers agree using SymPy then string match."""
    # Try SymPy equivalence between the two answers
    latex1 = answer1_latex or answer1
    latex2 = answer2_latex or answer2
    if latex1 and latex2:
        result = SympyEngine.check_equivalence(latex1, latex2)
        if result["error"] is None:
            return result["equivalent"]

    # Fallback: normalized string
    norm1 = LLMRouter._normalize(answer1)
    norm2 = LLMRouter._normalize(answer2)
    return norm1 == norm2 if (norm1 and norm2) else False


async def run_voting_for_problem(
    problem: dict,
    threshold: int,
) -> VotingResult:
    """Run the voting flow for a single problem.

    Flow:
    1. Call primary (deepseek-v3) -> if confidence >= threshold, accept
    2. Else call secondary (claude-sonnet) -> if agrees with primary, accept
    3. Else call tertiary (gpt-4o) -> majority vote
    4. If all 3 disagree -> flag manual review
    """
    steps: list[VoteStep] = []
    total_cost = 0.0
    correct_answer = problem["correct_answer"]
    correct_answer_latex = problem.get("correct_answer_latex", "")
    expected_form = problem.get("expected_form", "")

    # Proofs always escalate to manual review
    if expected_form == "proof":
        return VotingResult(
            problem_id=problem["id"],
            subject=problem["subject"],
            difficulty=problem["difficulty"],
            final_answer="",
            is_correct=False,
            check_method="needs_manual_review",
            steps=[],
            total_cost=0,
            accepted_at_step=0,
            needs_manual_review=True,
        )

    # Step 1: Primary model
    resp1 = await call_model(PRIMARY_MODEL, problem["content"])
    step1 = VoteStep(
        model_key=PRIMARY_MODEL,
        answer=resp1.answer,
        answer_latex=resp1.answer_latex,
        confidence=resp1.confidence,
        cost=resp1.cost,
        latency_ms=resp1.latency_ms,
        error=resp1.error,
    )
    steps.append(step1)
    total_cost += resp1.cost

    if resp1.confidence >= threshold and not resp1.error:
        check = check_answer(
            resp1.answer, resp1.answer_latex,
            correct_answer, correct_answer_latex, expected_form,
        )
        return VotingResult(
            problem_id=problem["id"],
            subject=problem["subject"],
            difficulty=problem["difficulty"],
            final_answer=resp1.answer,
            is_correct=check.is_correct,
            check_method=check.method,
            steps=steps,
            total_cost=total_cost,
            accepted_at_step=1,
        )

    # Step 2: Secondary model
    resp2 = await call_model(SECONDARY_MODEL, problem["content"])
    step2 = VoteStep(
        model_key=SECONDARY_MODEL,
        answer=resp2.answer,
        answer_latex=resp2.answer_latex,
        confidence=resp2.confidence,
        cost=resp2.cost,
        latency_ms=resp2.latency_ms,
        error=resp2.error,
    )
    steps.append(step2)
    total_cost += resp2.cost

    if _answers_agree(
        resp1.answer, resp1.answer_latex,
        resp2.answer, resp2.answer_latex,
        correct_answer_latex,
    ):
        check = check_answer(
            resp1.answer, resp1.answer_latex,
            correct_answer, correct_answer_latex, expected_form,
        )
        return VotingResult(
            problem_id=problem["id"],
            subject=problem["subject"],
            difficulty=problem["difficulty"],
            final_answer=resp1.answer,
            is_correct=check.is_correct,
            check_method=check.method,
            steps=steps,
            total_cost=total_cost,
            accepted_at_step=2,
        )

    # Step 3: Tertiary model -> majority vote
    resp3 = await call_model(TERTIARY_MODEL, problem["content"])
    step3 = VoteStep(
        model_key=TERTIARY_MODEL,
        answer=resp3.answer,
        answer_latex=resp3.answer_latex,
        confidence=resp3.confidence,
        cost=resp3.cost,
        latency_ms=resp3.latency_ms,
        error=resp3.error,
    )
    steps.append(step3)
    total_cost += resp3.cost

    # Find majority: check which pairs agree
    answers = [
        (resp1.answer, resp1.answer_latex),
        (resp2.answer, resp2.answer_latex),
        (resp3.answer, resp3.answer_latex),
    ]

    # Check 1-2 agreement (already failed above), 1-3, 2-3
    if _answers_agree(answers[0][0], answers[0][1], answers[2][0], answers[2][1], correct_answer_latex):
        # 1 and 3 agree
        final = resp1.answer
        final_latex = resp1.answer_latex
    elif _answers_agree(answers[1][0], answers[1][1], answers[2][0], answers[2][1], correct_answer_latex):
        # 2 and 3 agree
        final = resp2.answer
        final_latex = resp2.answer_latex
    else:
        # All 3 disagree -> manual review
        return VotingResult(
            problem_id=problem["id"],
            subject=problem["subject"],
            difficulty=problem["difficulty"],
            final_answer="",
            is_correct=False,
            check_method="needs_manual_review",
            steps=steps,
            total_cost=total_cost,
            accepted_at_step=0,
            needs_manual_review=True,
        )

    check = check_answer(
        final, final_latex,
        correct_answer, correct_answer_latex, expected_form,
    )
    return VotingResult(
        problem_id=problem["id"],
        subject=problem["subject"],
        difficulty=problem["difficulty"],
        final_answer=final,
        is_correct=check.is_correct,
        check_method=check.method,
        steps=steps,
        total_cost=total_cost,
        accepted_at_step=3,
    )


async def run_voting_benchmark(
    problem_ids: list[str] | None = None,
    thresholds: list[int] | None = None,
    progress_callback=None,
) -> VotingBenchmarkResult:
    """Run voting at multiple thresholds and compare to single-model baselines."""
    if thresholds is None:
        thresholds = [50, 60, 70, 80, 90]
    problems = load_problems(problem_ids)

    threshold_results: list[ThresholdResult] = []
    total_tasks = len(thresholds) * len(problems)
    task_num = 0

    for threshold in thresholds:
        results: list[VotingResult] = []
        for problem in problems:
            task_num += 1
            if progress_callback:
                progress_callback(
                    task_num, total_tasks,
                    f"threshold={threshold} {problem['id']}",
                )
            result = await run_voting_for_problem(problem, threshold)
            results.append(result)

        # Compute stats for this threshold
        non_manual = [r for r in results if not r.needs_manual_review]
        correct = sum(1 for r in non_manual if r.is_correct)
        total = len(non_manual) if non_manual else 1
        total_cost = sum(r.total_cost for r in results)
        avg_steps = sum(r.accepted_at_step for r in results) / len(results) if results else 0

        threshold_results.append(ThresholdResult(
            threshold=threshold,
            accuracy=round(correct / total * 100, 2),
            avg_cost=round(total_cost / len(results), 6) if results else 0,
            total_cost=round(total_cost, 6),
            avg_steps=round(avg_steps, 2),
            manual_review_count=sum(1 for r in results if r.needs_manual_review),
            results=results,
        ))

    # Find best threshold (highest accuracy, then lowest cost)
    best = max(threshold_results, key=lambda t: (t.accuracy, -t.total_cost))

    # Single-model baselines (from the primary model's results at threshold=100 effectively)
    single_baselines: dict[str, AccuracyCell] = {}
    for model_key in [PRIMARY_MODEL, SECONDARY_MODEL, TERTIARY_MODEL]:
        correct = 0
        total = 0
        for problem in problems:
            if problem.get("expected_form") == "proof":
                continue
            # We use results from voting runs where this model participated
            # For baseline, just count step 1 results from highest threshold
            total += 1
        # Use the highest threshold results as proxy
        if threshold_results:
            highest = threshold_results[-1]  # threshold=90
            for r in highest.results:
                for step in r.steps:
                    if step.model_key == model_key:
                        check = check_answer(
                            step.answer, step.answer_latex,
                            next(
                                (p["correct_answer"] for p in problems if p["id"] == r.problem_id),
                                "",
                            ),
                            next(
                                (p.get("correct_answer_latex", "") for p in problems if p["id"] == r.problem_id),
                                "",
                            ),
                            next(
                                (p.get("expected_form", "") for p in problems if p["id"] == r.problem_id),
                                "",
                            ),
                        )
                        if check.is_correct:
                            correct += 1
                        break
        if total > 0:
            single_baselines[model_key] = AccuracyCell(
                accuracy=round(correct / total * 100, 2),
                correct=correct,
                total=total,
            )

    run_id = datetime.now(timezone.utc).strftime("voting_%Y%m%d_%H%M%S")
    return VotingBenchmarkResult(
        run_id=run_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
        comparison=StrategyComparison(
            single_model_baseline=single_baselines,
            thresholds=threshold_results,
            best_threshold=best.threshold,
            best_accuracy=best.accuracy,
            best_cost=best.total_cost,
        ),
    )


def run_sympy_verification(run: BenchmarkRun) -> SympyVerificationReport:
    """Run SymPy verification on all results in an existing benchmark run."""
    results: list[SympyVerificationResult] = []
    problems_map: dict[str, dict] = {}

    # Build problem lookup from the run data
    for r in run.results:
        if r.problem_id not in problems_map:
            problems_map[r.problem_id] = {
                "correct_answer": r.correct_answer,
                "correct_answer_latex": "",  # Will try to get from problems file
                "expected_form": r.expected_form,
            }

    # Try to load full problem data for correct_answer_latex
    try:
        full_problems = load_problems()
        for p in full_problems:
            if p["id"] in problems_map:
                problems_map[p["id"]]["correct_answer_latex"] = p.get("correct_answer_latex", "")
    except Exception:
        pass

    for r in run.results:
        if r.expected_form == "proof":
            results.append(SympyVerificationResult(
                problem_id=r.problem_id,
                model_key=r.model_key,
                original_correct=r.check.is_correct,
                sympy_agrees=None,
                sympy_parse_success=False,
                answer_latex=r.response.answer_latex,
                correct_answer_latex=problems_map[r.problem_id].get("correct_answer_latex", ""),
                error="Skipped: proof problem",
            ))
            continue

        answer_latex = r.response.answer_latex or r.response.answer
        correct_latex = problems_map[r.problem_id].get("correct_answer_latex", "") or r.correct_answer

        if not answer_latex or not correct_latex:
            results.append(SympyVerificationResult(
                problem_id=r.problem_id,
                model_key=r.model_key,
                original_correct=r.check.is_correct,
                sympy_agrees=None,
                sympy_parse_success=False,
                answer_latex=answer_latex,
                correct_answer_latex=correct_latex,
                error="Missing LaTeX answer",
            ))
            continue

        equiv = SympyEngine.check_equivalence(answer_latex, correct_latex)
        parse_success = equiv["error"] is None

        results.append(SympyVerificationResult(
            problem_id=r.problem_id,
            model_key=r.model_key,
            original_correct=r.check.is_correct,
            sympy_agrees=equiv["equivalent"] if parse_success else None,
            sympy_parse_success=parse_success,
            answer_latex=answer_latex,
            correct_answer_latex=correct_latex,
            error=equiv.get("error"),
        ))

    # Compute summary stats
    total = len(results)
    parseable = [r for r in results if r.sympy_parse_success]
    parse_rate = len(parseable) / total * 100 if total > 0 else 0

    sympy_correct = sum(1 for r in parseable if r.sympy_agrees)
    accuracy_with = sympy_correct / len(parseable) * 100 if parseable else 0

    original_correct = sum(1 for r in results if r.original_correct)
    accuracy_without = original_correct / total * 100 if total > 0 else 0

    # By subject
    by_subject: dict[str, dict[str, float]] = defaultdict(lambda: {"parse_rate": 0, "accuracy": 0})
    subject_counts: dict[str, dict[str, list]] = defaultdict(lambda: {"parseable": [], "correct": [], "total": 0})
    for r in results:
        # Get subject from problem_id prefix
        subject = r.problem_id.split("-")[0]
        subject_counts[subject]["total"] += 1
        if r.sympy_parse_success:
            subject_counts[subject]["parseable"].append(r)
            if r.sympy_agrees:
                subject_counts[subject]["correct"].append(r)

    for subj, counts in subject_counts.items():
        total_s = counts["total"]
        parseable_s = len(counts["parseable"])
        correct_s = len(counts["correct"])
        by_subject[subj] = {
            "parse_rate": round(parseable_s / total_s * 100, 2) if total_s > 0 else 0,
            "accuracy": round(correct_s / parseable_s * 100, 2) if parseable_s > 0 else 0,
        }

    # By expected_form
    by_form: dict[str, dict[str, float]] = {}
    form_counts: dict[str, dict[str, list]] = defaultdict(lambda: {"parseable": [], "correct": [], "total": 0})
    for r in results:
        # Get form from run results
        matching = [res for res in run.results if res.problem_id == r.problem_id and res.model_key == r.model_key]
        form = matching[0].expected_form if matching else "unknown"
        form_counts[form]["total"] += 1
        if r.sympy_parse_success:
            form_counts[form]["parseable"].append(r)
            if r.sympy_agrees:
                form_counts[form]["correct"].append(r)

    for form, counts in form_counts.items():
        total_f = counts["total"]
        parseable_f = len(counts["parseable"])
        correct_f = len(counts["correct"])
        by_form[form] = {
            "parse_rate": round(parseable_f / total_f * 100, 2) if total_f > 0 else 0,
            "accuracy": round(correct_f / parseable_f * 100, 2) if parseable_f > 0 else 0,
        }

    return SympyVerificationReport(
        run_id=run.run_id,
        total_checked=total,
        sympy_parse_success_rate=round(parse_rate, 2),
        accuracy_with_sympy=round(accuracy_with, 2),
        accuracy_without_sympy=round(accuracy_without, 2),
        by_subject=dict(by_subject),
        by_expected_form=by_form,
        results=results,
    )
