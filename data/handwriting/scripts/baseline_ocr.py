#!/usr/bin/env python3
"""
Phase 3.1: Baseline OCR Measurement
Runs Gemini Vision on all handwriting images and measures accuracy against ground truth.
"""

import csv
import json
import os
import re
import sys
import time
from pathlib import Path

import vertexai
from vertexai.generative_models import GenerativeModel, Image

# --- Config ---
PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "express-auth-414411")
LOCATION = os.environ.get("GCP_LOCATION", "us-central1")
MODEL_NAME = "gemini-2.0-flash"

BASE_DIR = Path(__file__).resolve().parent.parent
IMAGES_DIR = BASE_DIR / "images"
MANIFEST_PATH = BASE_DIR / "manifest.csv"
RESULTS_DIR = BASE_DIR / "results"

OCR_PROMPT = r"""You are a math OCR system. Look at this handwritten math formula image and output ONLY the LaTeX representation.

Rules:
- Output ONLY the LaTeX code, nothing else
- Do NOT wrap in $ signs or \[ \] delimiters
- Use standard LaTeX commands: \frac, \sqrt, \int, \sum, \lim, \begin{pmatrix}, etc.
- For nth roots use \sqrt[n]{...}
- For definite integrals use \int_a^b
- For matrices use \begin{pmatrix}...\end{pmatrix} or \begin{vmatrix}...\end{vmatrix}
- Preserve the exact mathematical meaning
- If unsure about a symbol, make your best guess

Output the LaTeX now:"""


def normalize_latex(s: str) -> str:
    """Normalize LaTeX for comparison: strip whitespace, normalize common equivalences."""
    s = s.strip()
    # Remove surrounding delimiters if present
    for delim in [("$", "$"), ("\\(", "\\)"), ("\\[", "\\]")]:
        if s.startswith(delim[0]) and s.endswith(delim[1]):
            s = s[len(delim[0]):-len(delim[1])].strip()
    # Lowercase (X vs x from OCR)
    s = s.lower()
    # Remove \displaystyle
    s = s.replace("\\displaystyle", "")
    # Normalize thin spaces and spacing commands
    s = s.replace("\\,", "").replace("\\;", "").replace("\\:", "").replace("\\ ", " ")
    s = s.replace("\\!", "")
    # Normalize \left( \right) to just ( )
    s = s.replace("\\left(", "(").replace("\\right)", ")")
    s = s.replace("\\left[", "[").replace("\\right]", "]")
    s = s.replace("\\left|", "|").replace("\\right|", "|")
    s = s.replace("\\left\\{", "\\{").replace("\\right\\}", "\\}")
    # Normalize cdot vs times
    s = s.replace("\\times", "\\cdot")
    # Normalize \varepsilon vs \epsilon
    s = s.replace("\\varepsilon", "\\epsilon")
    # Normalize \text{adj} vs adj
    s = s.replace("\\text{adj}", "\\mathrm{adj}").replace("adj", "\\mathrm{adj}")
    # Normalize single-char exponents/subscripts: x^{2} -> x^2, a_{i} -> a_i
    s = re.sub(r"\^{([^{}])}", r"^\1", s)
    s = re.sub(r"_{([^{}])}", r"_\1", s)
    # Remove all spaces (LaTeX is whitespace-insensitive for math)
    s = re.sub(r"\s+", "", s)
    return s


def latex_matches(predicted: str, ground_truth: str) -> tuple[bool, bool]:
    """
    Returns (exact_match, normalized_match).
    exact_match: strings are identical after stripping
    normalized_match: strings match after normalization
    """
    pred_stripped = predicted.strip()
    gt_stripped = ground_truth.strip()
    exact = pred_stripped == gt_stripped
    normalized = normalize_latex(pred_stripped) == normalize_latex(gt_stripped)
    return exact, normalized


def load_manifest() -> list[dict]:
    """Load manifest.csv and return list of entries."""
    entries = []
    with open(MANIFEST_PATH, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entries.append(row)
    return entries


def run_ocr(model: GenerativeModel, image_path: Path, max_retries: int = 3) -> str:
    """Send image to Gemini Vision and extract LaTeX, with retry on rate limit."""
    img = Image.load_from_file(str(image_path))
    for attempt in range(max_retries):
        try:
            response = model.generate_content([OCR_PROMPT, img])
            return response.text.strip()
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                wait = 15 * (attempt + 1)
                print(f"  Rate limited, waiting {wait}s (attempt {attempt+1}/{max_retries})...")
                time.sleep(wait)
            else:
                raise
    return ""


def main():
    print("=" * 70)
    print("Phase 3.1: Baseline OCR Measurement")
    print(f"Model: {MODEL_NAME}")
    print("=" * 70)

    # Init Vertex AI
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    model = GenerativeModel(MODEL_NAME)

    # Load manifest
    entries = load_manifest()
    print(f"\nLoaded {len(entries)} entries from manifest.csv")

    # Create results dir
    RESULTS_DIR.mkdir(exist_ok=True)

    # Run OCR on each image
    results = []
    exact_matches = 0
    normalized_matches = 0
    errors_by_category = {}
    errors_by_difficulty = {}
    errors_by_style = {}
    error_patterns = []

    for i, entry in enumerate(entries):
        image_path = IMAGES_DIR / entry["filename"]
        ground_truth = entry["latex"]
        category = entry["category"]
        difficulty = entry["difficulty"]
        style = entry["style"]

        print(f"\n[{i+1}/{len(entries)}] {entry['filename']}")
        print(f"  Ground truth: {ground_truth}")

        if not image_path.exists():
            print(f"  ERROR: Image not found at {image_path}")
            results.append({
                **entry,
                "predicted": "FILE_NOT_FOUND",
                "exact_match": False,
                "normalized_match": False,
                "error_type": "missing_file",
            })
            continue

        try:
            predicted = run_ocr(model, image_path)
            exact, normalized = latex_matches(predicted, ground_truth)

            print(f"  Predicted:    {predicted}")
            print(f"  Exact match:  {'YES' if exact else 'NO'}")
            print(f"  Norm match:   {'YES' if normalized else 'NO'}")

            if exact:
                exact_matches += 1
            if normalized:
                normalized_matches += 1

            result = {
                **entry,
                "predicted": predicted,
                "exact_match": exact,
                "normalized_match": normalized,
            }

            if not normalized:
                error_type = categorize_error(predicted, ground_truth)
                result["error_type"] = error_type
                error_patterns.append({
                    "id": entry["id"],
                    "filename": entry["filename"],
                    "category": category,
                    "difficulty": difficulty,
                    "style": style,
                    "ground_truth": ground_truth,
                    "predicted": predicted,
                    "error_type": error_type,
                })

                # Track errors by category/difficulty/style
                errors_by_category.setdefault(category, {"total": 0, "errors": 0})
                errors_by_category[category]["errors"] += 1

                errors_by_difficulty.setdefault(difficulty, {"total": 0, "errors": 0})
                errors_by_difficulty[difficulty]["errors"] += 1

                errors_by_style.setdefault(style, {"total": 0, "errors": 0})
                errors_by_style[style]["errors"] += 1

            # Track totals
            errors_by_category.setdefault(category, {"total": 0, "errors": 0})
            errors_by_category[category]["total"] += 1

            errors_by_difficulty.setdefault(difficulty, {"total": 0, "errors": 0})
            errors_by_difficulty[difficulty]["total"] += 1

            errors_by_style.setdefault(style, {"total": 0, "errors": 0})
            errors_by_style[style]["total"] += 1

            results.append(result)

            # Rate limiting: be conservative for free tier
            time.sleep(4)

        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({
                **entry,
                "predicted": f"ERROR: {str(e)[:200]}",
                "exact_match": False,
                "normalized_match": False,
                "error_type": "api_error",
            })
            time.sleep(5)  # Back off on error

    # --- Summary ---
    total = len(entries)
    print("\n" + "=" * 70)
    print("BASELINE OCR RESULTS SUMMARY")
    print("=" * 70)

    print(f"\nTotal images:        {total}")
    print(f"Exact matches:       {exact_matches}/{total} ({exact_matches/total*100:.1f}%)")
    print(f"Normalized matches:  {normalized_matches}/{total} ({normalized_matches/total*100:.1f}%)")

    print(f"\n--- Accuracy by Category ---")
    for cat, stats in sorted(errors_by_category.items()):
        correct = stats["total"] - stats["errors"]
        pct = correct / stats["total"] * 100 if stats["total"] > 0 else 0
        print(f"  {cat:12s}: {correct}/{stats['total']} ({pct:.0f}%)")

    print(f"\n--- Accuracy by Difficulty ---")
    for diff, stats in sorted(errors_by_difficulty.items()):
        correct = stats["total"] - stats["errors"]
        pct = correct / stats["total"] * 100 if stats["total"] > 0 else 0
        print(f"  {diff:12s}: {correct}/{stats['total']} ({pct:.0f}%)")

    print(f"\n--- Accuracy by Style ---")
    for sty, stats in sorted(errors_by_style.items()):
        correct = stats["total"] - stats["errors"]
        pct = correct / stats["total"] * 100 if stats["total"] > 0 else 0
        print(f"  {sty:12s}: {correct}/{stats['total']} ({pct:.0f}%)")

    if error_patterns:
        print(f"\n--- Error Patterns ({len(error_patterns)} errors) ---")
        type_counts = {}
        for ep in error_patterns:
            t = ep.get("error_type", "unknown")
            type_counts[t] = type_counts.get(t, 0) + 1
        for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
            print(f"  {t:30s}: {c}")

    # --- Save results ---
    results_file = RESULTS_DIR / "baseline_ocr_results.json"
    with open(results_file, "w") as f:
        json.dump({
            "model": MODEL_NAME,
            "total_images": total,
            "exact_matches": exact_matches,
            "exact_accuracy": round(exact_matches / total * 100, 2),
            "normalized_matches": normalized_matches,
            "normalized_accuracy": round(normalized_matches / total * 100, 2),
            "accuracy_by_category": {
                cat: {
                    "total": s["total"],
                    "correct": s["total"] - s["errors"],
                    "accuracy": round((s["total"] - s["errors"]) / s["total"] * 100, 2),
                }
                for cat, s in sorted(errors_by_category.items())
            },
            "accuracy_by_difficulty": {
                diff: {
                    "total": s["total"],
                    "correct": s["total"] - s["errors"],
                    "accuracy": round((s["total"] - s["errors"]) / s["total"] * 100, 2),
                }
                for diff, s in sorted(errors_by_difficulty.items())
            },
            "accuracy_by_style": {
                sty: {
                    "total": s["total"],
                    "correct": s["total"] - s["errors"],
                    "accuracy": round((s["total"] - s["errors"]) / s["total"] * 100, 2),
                }
                for sty, s in sorted(errors_by_style.items())
            },
            "error_patterns": error_patterns,
            "detailed_results": results,
        }, f, indent=2)
    print(f"\nResults saved to {results_file}")

    # Also save CSV for easy viewing
    csv_file = RESULTS_DIR / "baseline_ocr_results.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id", "filename", "category", "difficulty", "style",
            "latex", "predicted", "exact_match", "normalized_match", "error_type",
        ])
        writer.writeheader()
        for r in results:
            writer.writerow({
                "id": r["id"],
                "filename": r["filename"],
                "category": r["category"],
                "difficulty": r["difficulty"],
                "style": r["style"],
                "latex": r["latex"],
                "predicted": r["predicted"],
                "exact_match": r.get("exact_match", ""),
                "normalized_match": r.get("normalized_match", ""),
                "error_type": r.get("error_type", ""),
            })
    print(f"CSV saved to {csv_file}")


def categorize_error(predicted: str, ground_truth: str) -> str:
    """Categorize the type of OCR error."""
    pred_norm = normalize_latex(predicted)
    gt_norm = normalize_latex(ground_truth)

    # Check for common error types
    if not predicted or predicted == "FILE_NOT_FOUND":
        return "no_output"

    if predicted.startswith("ERROR:"):
        return "api_error"

    # Structural differences
    pred_commands = set(re.findall(r"\\[a-zA-Z]+", pred_norm))
    gt_commands = set(re.findall(r"\\[a-zA-Z]+", gt_norm))

    missing_commands = gt_commands - pred_commands
    extra_commands = pred_commands - gt_commands

    if missing_commands or extra_commands:
        if "\\frac" in missing_commands or "\\frac" in extra_commands:
            return "fraction_structure"
        if "\\sqrt" in missing_commands or "\\sqrt" in extra_commands:
            return "radical_structure"
        if "\\int" in missing_commands or "\\int" in extra_commands:
            return "integral_structure"
        if any(c in missing_commands or c in extra_commands for c in ["\\begin", "\\pmatrix", "\\vmatrix"]):
            return "matrix_structure"
        if any(c in missing_commands or c in extra_commands for c in ["\\sum", "\\prod", "\\lim"]):
            return "operator_structure"
        return "command_difference"

    # Check for subscript/superscript issues
    if pred_norm.count("^") != gt_norm.count("^") or pred_norm.count("_") != gt_norm.count("_"):
        return "sub_superscript"

    # Check for brace mismatch
    if pred_norm.count("{") != gt_norm.count("{"):
        return "brace_mismatch"

    # Character-level differences
    if len(pred_norm) != len(gt_norm):
        return "length_difference"

    return "symbol_substitution"


if __name__ == "__main__":
    main()
