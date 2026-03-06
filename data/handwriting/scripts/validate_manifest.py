#!/usr/bin/env python3
"""Validate handwriting OCR manifest against actual image files.

Checks:
  - Which images listed in manifest.csv exist on disk
  - Coverage stats per category
  - Orphan images (on disk but not in manifest)

Usage:
    python data/handwriting/scripts/validate_manifest.py
"""

import csv
import sys
from collections import defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
HANDWRITING_DIR = SCRIPT_DIR.parent
IMAGES_DIR = HANDWRITING_DIR / "images"
MANIFEST_PATH = HANDWRITING_DIR / "manifest.csv"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def load_manifest() -> list[dict]:
    """Load manifest.csv and return list of row dicts."""
    if not MANIFEST_PATH.exists():
        print(f"ERROR: manifest.csv not found at {MANIFEST_PATH}")
        sys.exit(1)

    rows = []
    with open(MANIFEST_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def find_all_images() -> set[Path]:
    """Find all image files under images/ directory."""
    images = set()
    for ext in IMAGE_EXTENSIONS:
        images.update(IMAGES_DIR.rglob(f"*{ext}"))
    return images


def validate():
    rows = load_manifest()
    print(f"Manifest loaded: {len(rows)} entries\n")

    # Track per-category stats
    category_total = defaultdict(int)
    category_found = defaultdict(int)
    missing = []
    found = []

    manifest_paths = set()

    for row in rows:
        cat = row["category"]
        filename = row["filename"]
        category_total[cat] += 1

        img_path = IMAGES_DIR / filename
        manifest_paths.add(img_path.resolve())

        # Check with any valid extension
        exists = False
        stem = img_path.stem
        parent = img_path.parent
        for ext in IMAGE_EXTENSIONS:
            if (parent / f"{stem}{ext}").exists():
                exists = True
                break

        if exists:
            category_found[cat] += 1
            found.append(row)
        else:
            missing.append(row)

    # Coverage summary
    total_found = sum(category_found.values())
    total = len(rows)

    print("=" * 50)
    print("COVERAGE SUMMARY")
    print("=" * 50)
    print(f"{'Category':<15} {'Found':>6} {'Total':>6} {'%':>7}")
    print("-" * 40)
    for cat in sorted(category_total.keys()):
        f = category_found[cat]
        t = category_total[cat]
        pct = (f / t * 100) if t > 0 else 0
        print(f"{cat:<15} {f:>6} {t:>6} {pct:>6.1f}%")
    print("-" * 40)
    pct_total = (total_found / total * 100) if total > 0 else 0
    print(f"{'TOTAL':<15} {total_found:>6} {total:>6} {pct_total:>6.1f}%")
    print()

    # Missing images
    if missing:
        print(f"MISSING IMAGES ({len(missing)}):")
        for row in missing:
            print(f"  [{row['id']:>3}] {row['filename']:<30} {row['latex']}")
    else:
        print("All images present!")
    print()

    # Orphan images (on disk but not in manifest)
    all_images = find_all_images()
    manifest_resolved = set()
    for row in rows:
        parent = IMAGES_DIR / Path(row["filename"]).parent
        stem = Path(row["filename"]).stem
        for ext in IMAGE_EXTENSIONS:
            p = (parent / f"{stem}{ext}").resolve()
            manifest_resolved.add(p)

    orphans = [img for img in all_images if img.resolve() not in manifest_resolved]
    if orphans:
        print(f"ORPHAN IMAGES ({len(orphans)}) — on disk but not in manifest:")
        for img in sorted(orphans):
            rel = img.relative_to(IMAGES_DIR)
            print(f"  {rel}")
    else:
        print("No orphan images found.")

    # Style distribution
    print()
    print("STYLE DISTRIBUTION:")
    style_counts = defaultdict(int)
    for row in rows:
        style_counts[row["style"]] += 1
    for style in sorted(style_counts.keys()):
        print(f"  {style:<12} {style_counts[style]:>3}")

    # Difficulty distribution
    print()
    print("DIFFICULTY DISTRIBUTION:")
    diff_counts = defaultdict(int)
    for row in rows:
        diff_counts[row["difficulty"]] += 1
    for diff in ["easy", "medium", "hard"]:
        print(f"  {diff:<12} {diff_counts[diff]:>3}")

    print()
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(validate())
