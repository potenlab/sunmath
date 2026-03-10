"""Merge HME100K + CROHME datasets and prepare baseline training splits.

Usage:
    python data/datasets/scripts/prepare_baseline.py

Reads manifests from hme100k/ and crohme/, normalizes LaTeX,
creates 90/10 train/val split, outputs to data/datasets/baseline/
"""

from __future__ import annotations

import csv
import random
import re
from pathlib import Path

DATASETS_DIR = Path(__file__).resolve().parents[1]
HME100K_MANIFEST = DATASETS_DIR / "hme100k" / "manifest.csv"
CROHME_MANIFEST = DATASETS_DIR / "crohme" / "manifest.csv"
BASELINE_DIR = DATASETS_DIR / "baseline"
TRAIN_MANIFEST = BASELINE_DIR / "train_manifest.csv"
VAL_MANIFEST = BASELINE_DIR / "val_manifest.csv"

RANDOM_SEED = 42
VAL_RATIO = 0.10


def normalize_latex(latex: str) -> str | None:
    """Normalize LaTeX string. Returns None if malformed."""
    if not latex:
        return None

    s = latex.strip()

    # Remove common wrappers
    for wrapper in ["$$", "$", "\\[", "\\]", "\\(", "\\)"]:
        if s.startswith(wrapper):
            s = s[len(wrapper):]
        if s.endswith(wrapper):
            s = s[:-len(wrapper)]

    s = s.strip()

    if not s:
        return None

    # Skip obviously malformed entries (unbalanced braces)
    open_braces = s.count("{")
    close_braces = s.count("}")
    if open_braces != close_braces:
        return None

    # Normalize whitespace
    s = re.sub(r"\s+", " ", s).strip()

    return s


def read_manifest(path: Path, dataset: str) -> list[dict]:
    """Read a manifest CSV and tag each record with its source dataset."""
    records = []
    if not path.exists():
        print(f"Warning: Manifest not found: {path}")
        return records

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append({
                "filename": row["filename"],
                "latex": row["latex"],
                "split": row.get("split", "train"),
                "dataset": dataset,
            })
    return records


def main():
    BASELINE_DIR.mkdir(parents=True, exist_ok=True)

    print("Reading manifests...")
    hme_records = read_manifest(HME100K_MANIFEST, "hme100k")
    crohme_records = read_manifest(CROHME_MANIFEST, "crohme")

    print(f"  HME100K: {len(hme_records)} records")
    print(f"  CROHME:  {len(crohme_records)} records")

    # Merge all records
    all_records = hme_records + crohme_records

    # Normalize LaTeX and filter
    normalized = []
    skipped = 0
    for rec in all_records:
        norm = normalize_latex(rec["latex"])
        if norm is None:
            skipped += 1
            continue
        normalized.append({
            "filename": rec["filename"],
            "latex": norm,
            "dataset": rec["dataset"],
        })

    print(f"\nAfter normalization:")
    print(f"  Valid:   {len(normalized)}")
    print(f"  Skipped: {skipped}")

    # Shuffle and split 90/10
    random.seed(RANDOM_SEED)
    random.shuffle(normalized)

    split_idx = int(len(normalized) * (1 - VAL_RATIO))
    train_records = normalized[:split_idx]
    val_records = normalized[split_idx:]

    print(f"\nSplit:")
    print(f"  Train: {len(train_records)}")
    print(f"  Val:   {len(val_records)}")

    # Write output manifests
    fieldnames = ["filename", "latex", "dataset"]

    with open(TRAIN_MANIFEST, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(train_records)

    with open(VAL_MANIFEST, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(val_records)

    print(f"\nOutput:")
    print(f"  Train manifest: {TRAIN_MANIFEST}")
    print(f"  Val manifest:   {VAL_MANIFEST}")
    print("\nDone!")


if __name__ == "__main__":
    main()
