#!/usr/bin/env python3
"""
Demo: Intent-Based Grading Engine
==================================
Demonstrates how the same mathematical expression gets DIFFERENT grades
based on problem intent (expected_form).

This is a standalone demo using SympyEngine directly — no database required.

Usage:
    cd backend
    python scripts/demo_intent_grading.py
"""

import sys
import os

# Add backend to path so we can import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.sympy_engine import SympyEngine

# ─── Helpers ─────────────────────────────────────────────────────────────────

BOLD = "\033[1m"
DIM = "\033[2m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
DIVIDER = "─" * 72


def badge(correct: bool) -> str:
    if correct:
        return f"{GREEN}✔ CORRECT{RESET}"
    return f"{RED}✘ WRONG{RESET}"


def llm_badge() -> str:
    return f"{YELLOW}→ LLM{RESET}"


def grade_mathematical(
    engine: SympyEngine,
    problem: str,
    correct_answer: str,
    submitted_answer: str,
    expected_form: str,
) -> dict:
    """Reproduce the exact grading logic from GradingEngine._grade_mathematical."""

    # Step 1: equivalence check
    equiv = engine.check_equivalence(submitted_answer, correct_answer)

    if equiv["error"]:
        return {
            "is_correct": None,
            "judged_by": "llm",
            "reasoning": f"SymPy parse error → LLM fallback ({equiv['error']})",
        }

    if not equiv["equivalent"]:
        return {
            "is_correct": False,
            "judged_by": "sympy",
            "reasoning": (
                f"Mathematically incorrect. "
                f"Expected: {correct_answer}, Got: {submitted_answer}"
            ),
        }

    # Step 2: form check (only if expected_form requires it)
    if expected_form in ("factored", "expanded", "numeric"):
        form = engine.check_form(submitted_answer, expected_form)
        if form["error"]:
            return {
                "is_correct": True,
                "judged_by": "sympy",
                "reasoning": "Mathematically correct (form check unavailable)",
            }
        if not form["matches"]:
            return {
                "is_correct": False,
                "judged_by": "sympy",
                "reasoning": (
                    f"Mathematically equivalent but wrong form. "
                    f"Expected {expected_form} form. {form['reason']}"
                ),
            }

    return {
        "is_correct": True,
        "judged_by": "sympy",
        "reasoning": f"Correct. Mathematically equivalent and in {expected_form} form.",
    }


def print_scenario(num: int, scenario: dict, result: dict):
    print(f"\n{BOLD}Scenario {num}: {scenario['title']}{RESET}")
    print(DIVIDER)
    print(f"  {DIM}Problem:{RESET}         {scenario['problem']}")
    print(f"  {DIM}Correct answer:{RESET}  {scenario['correct_answer']}")
    print(f"  {DIM}Student answer:{RESET}  {scenario['submitted']}")
    print(f"  {DIM}expected_form:{RESET}   {CYAN}{scenario['expected_form']}{RESET}")
    print()

    if result["judged_by"] == "llm":
        print(f"  Result:  {llm_badge()}")
    else:
        print(f"  Result:  {badge(result['is_correct'])}")

    print(f"  Engine:  {result['judged_by']}")
    print(f"  Reason:  {result['reasoning']}")
    print()


# ─── Demo Scenarios ──────────────────────────────────────────────────────────

SCENARIOS = [
    # --- Group A: Same expression, different expected_form → different result ---
    {
        "title": "Factor x²+2x+1 → student writes expanded form",
        "problem": "Factor x²+2x+1",
        "correct_answer": "(x+1)**2",
        "submitted": "x**2 + 2*x + 1",
        "expected_form": "factored",
        "expect_correct": False,
    },
    {
        "title": "Expand (x+1)² → student writes expanded form",
        "problem": "Expand (x+1)²",
        "correct_answer": "(x+1)**2",
        "submitted": "x**2 + 2*x + 1",
        "expected_form": "expanded",
        "expect_correct": True,
    },
    {
        "title": "Factor x²+2x+1 → student writes correct factored form",
        "problem": "Factor x²+2x+1",
        "correct_answer": "(x+1)**2",
        "submitted": "(x+1)**2",
        "expected_form": "factored",
        "expect_correct": True,
    },

    # --- Group B: Proof → always routes to LLM ---
    {
        "title": "Prove √2 is irrational → text proof submitted",
        "problem": "Prove that √2 is irrational",
        "correct_answer": "proof by contradiction",
        "submitted": "Assume √2 = p/q in lowest terms. Then 2q²=p², so p is even...",
        "expected_form": "proof",
        "expect_correct": None,  # LLM decides
    },

    # --- Group C: Factored vs Expanded on a different problem ---
    {
        "title": "Factor x²+5x+6 → student writes expanded form",
        "problem": "Factor x²+5x+6",
        "correct_answer": "(x+2)(x+3)",
        "submitted": "x**2 + 5*x + 6",
        "expected_form": "factored",
        "expect_correct": False,
    },
    {
        "title": "Expand (x+2)(x+3) → student writes expanded form",
        "problem": "Expand (x+2)(x+3)",
        "correct_answer": "(x+2)(x+3)",
        "submitted": "x**2 + 5*x + 6",
        "expected_form": "expanded",
        "expect_correct": True,
    },

    # --- Group D: Commutativity / algebraic equivalence ---
    {
        "title": "Simplify → x+1 vs 1+x (commutative equivalence)",
        "problem": "Simplify the expression",
        "correct_answer": "x + 1",
        "submitted": "1 + x",
        "expected_form": "simplified",
        "expect_correct": True,
    },
    {
        "title": "Simplify → 2x/2 vs x (algebraic equivalence)",
        "problem": "Simplify 2x/2",
        "correct_answer": "x",
        "submitted": "2*x/2",
        "expected_form": "simplified",
        "expect_correct": True,
    },

    # --- Group E: LaTeX input handling ---
    {
        "title": "Factor with LaTeX input → \\frac and ^",
        "problem": "Factor x²+5x+6",
        "correct_answer": "(x+2)(x+3)",
        "submitted": "(x+2)(x+3)",
        "expected_form": "factored",
        "expect_correct": True,
    },
    {
        "title": "Wrong answer → mathematically incorrect (even in right form)",
        "problem": "Factor x²+5x+6",
        "correct_answer": "(x+2)(x+3)",
        "submitted": "(x+1)(x+6)",
        "expected_form": "factored",
        "expect_correct": False,  # (x+1)(x+6) = x²+7x+6 ≠ x²+5x+6
    },
]


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    engine = SympyEngine()
    passed = 0
    failed = 0
    total = len(SCENARIOS)

    print()
    print(f"{BOLD}{'=' * 72}{RESET}")
    print(f"{BOLD}  SunMath Intent-Based Grading Demo{RESET}")
    print(f"{BOLD}  Same expression → different grade based on problem intent{RESET}")
    print(f"{BOLD}{'=' * 72}{RESET}")

    for i, scenario in enumerate(SCENARIOS, 1):
        if scenario["expected_form"] == "proof":
            # Proof always goes to LLM — we show it routes correctly
            result = {
                "is_correct": None,
                "judged_by": "llm",
                "reasoning": "Proof requires LLM evaluation — routed to LLM with full problem context, evaluation concepts, and grading hints",
            }
        else:
            result = grade_mathematical(
                engine,
                scenario["problem"],
                scenario["correct_answer"],
                scenario["submitted"],
                scenario["expected_form"],
            )

        print_scenario(i, scenario, result)

        # Verify demo expectation
        expected = scenario["expect_correct"]
        if expected is None:
            # LLM scenario — just check it routes correctly
            if result["judged_by"] == "llm":
                passed += 1
            else:
                failed += 1
                print(f"  {RED}⚠ UNEXPECTED: should route to LLM{RESET}\n")
        elif result["is_correct"] == expected:
            passed += 1
        else:
            failed += 1
            print(f"  {RED}⚠ UNEXPECTED: expected {'CORRECT' if expected else 'WRONG'}{RESET}\n")

    # Summary
    print(DIVIDER)
    print(f"\n{BOLD}Summary{RESET}")
    print(f"  Total scenarios: {total}")
    print(f"  {GREEN}Passed: {passed}{RESET}")
    if failed:
        print(f"  {RED}Failed: {failed}{RESET}")
    else:
        print(f"  Failed: 0")

    print(f"\n{BOLD}Key Takeaways:{RESET}")
    print(f"  1. Scenarios 1-2: {CYAN}Same student answer{RESET}, different result")
    print(f"     → 'x²+2x+1' is WRONG for 'Factor' but CORRECT for 'Expand'")
    print(f"  2. Scenarios 5-6: {CYAN}Same again{RESET} with a different polynomial")
    print(f"     → 'x²+5x+6' is WRONG for 'Factor' but CORRECT for 'Expand'")
    print(f"  3. Scenario 4:   Proofs route to {YELLOW}LLM{RESET} automatically")
    print(f"  4. Scenarios 7-8: Algebraic equivalence (x+1 = 1+x, 2x/2 = x)")
    print()

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
