"""Download and extract HME100K dataset for math handwriting OCR.

Usage:
    python data/datasets/scripts/download_hme100k.py

Requires: pip install kagglehub
Downloads from Kaggle: https://www.kaggle.com/datasets/prajwalchy/hme100k-dataset

Expected output: ~74,502 train + 24,607 test images with LaTeX labels
in data/datasets/hme100k/
"""

from __future__ import annotations

import csv
import os
import shutil
import subprocess
import sys
from pathlib import Path

DATASET_DIR = Path(__file__).resolve().parents[1] / "hme100k"
MANIFEST_PATH = DATASET_DIR / "manifest.csv"

KAGGLE_DATASET = "prajwalchy/hme100k-dataset"


def download_hme100k():
    """Download HME100K from Kaggle using kagglehub."""
    # Check if already downloaded with actual data
    labels_exist = (
        (DATASET_DIR / "train_labels.txt").exists()
        or (DATASET_DIR / "train" / "train_labels.txt").exists()
    )
    if labels_exist:
        print("HME100K labels already present, skipping download.")
        return

    DATASET_DIR.mkdir(parents=True, exist_ok=True)

    # Clean up previous failed attempt
    repo_dir = DATASET_DIR / "repo"
    if repo_dir.exists():
        shutil.rmtree(repo_dir)

    print("Downloading HME100K from Kaggle...")
    print(f"Dataset: {KAGGLE_DATASET}")

    try:
        import kagglehub
        path = kagglehub.dataset_download(KAGGLE_DATASET)
        print(f"Downloaded to: {path}")

        # Copy files from kagglehub cache to our dataset dir
        src = Path(path)
        _copy_dataset_files(src)

    except ImportError:
        print("kagglehub not installed. Trying kaggle CLI...")
        try:
            subprocess.run(
                [
                    "kaggle", "datasets", "download",
                    "-d", KAGGLE_DATASET,
                    "-p", str(DATASET_DIR),
                    "--unzip",
                ],
                check=True,
            )
            # Files may be nested, try to flatten
            _flatten_dataset_dir()
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"\nFailed to download: {e}")
            print("\nPlease install kagglehub or kaggle CLI:")
            print("  pip install kagglehub")
            print("  # or")
            print("  pip install kaggle")
            print(f"\nOr manually download from: https://www.kaggle.com/datasets/{KAGGLE_DATASET}")
            print(f"Extract to: {DATASET_DIR}")
            sys.exit(1)

    print("Download and extraction complete.")


def _copy_dataset_files(src: Path):
    """Copy dataset files from kagglehub cache to DATASET_DIR."""
    # Walk source to find train_labels.txt and figure out structure
    for labels_file in src.rglob("train_labels.txt"):
        parent = labels_file.parent
        # Copy everything from this level
        for item in parent.iterdir():
            dst = DATASET_DIR / item.name
            if dst.exists():
                continue
            if item.is_dir():
                shutil.copytree(item, dst)
            else:
                shutil.copy2(item, dst)
        return

    # Fallback: copy everything from src
    for item in src.iterdir():
        dst = DATASET_DIR / item.name
        if dst.exists():
            continue
        if item.is_dir():
            shutil.copytree(item, dst)
        else:
            shutil.copy2(item, dst)


def _flatten_dataset_dir():
    """If Kaggle extracted into a nested folder, flatten it."""
    # Look for train_labels.txt in subdirectories
    for labels_file in DATASET_DIR.rglob("train_labels.txt"):
        if labels_file.parent == DATASET_DIR:
            return  # Already flat
        parent = labels_file.parent
        for item in parent.iterdir():
            dst = DATASET_DIR / item.name
            if not dst.exists():
                item.rename(dst)
        return


def _find_labels_file(name: str) -> Path | None:
    """Find a labels file, checking multiple possible locations."""
    # Direct location
    direct = DATASET_DIR / name
    if direct.exists():
        return direct
    # Inside train/test subdirectory
    split = name.split("_")[0]  # "train" or "test"
    nested = DATASET_DIR / split / name
    if nested.exists():
        return nested
    # Search recursively
    for f in DATASET_DIR.rglob(name):
        return f
    return None


def _find_images_dir(split: str) -> Path | None:
    """Find images directory for a split."""
    # Common structures: train/, train/train_images/, train_images/
    candidates = [
        DATASET_DIR / split / f"{split}_images",
        DATASET_DIR / split,
        DATASET_DIR / f"{split}_images",
    ]
    for c in candidates:
        if c.exists() and c.is_dir():
            return c
    return None


def parse_labels(labels_file: Path, split: str, images_dir: Path | None) -> list[dict]:
    """Parse a labels file (format: filename\tlatex) into records."""
    records = []
    if not labels_file.exists():
        print(f"Warning: Labels file not found: {labels_file}")
        return records

    with open(labels_file, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t", 1)
            if len(parts) != 2:
                print(f"Warning: Malformed line {line_num} in {labels_file.name}")
                continue
            filename, latex = parts
            records.append({
                "filename": filename.strip(),
                "latex": latex.strip(),
                "split": split,
                "_images_dir": images_dir,
            })
    return records


def validate_images(records: list[dict]) -> list[dict]:
    """Validate that referenced images exist, return only valid records."""
    valid = []
    missing = 0
    for rec in records:
        images_dir = rec.pop("_images_dir", None)
        search_dirs = []
        if images_dir:
            search_dirs.append(images_dir)
        search_dirs.append(DATASET_DIR / rec["split"])
        search_dirs.append(DATASET_DIR)

        found = False
        for d in search_dirs:
            img_path = d / rec["filename"]
            if img_path.exists():
                found = True
                break
            # Try appending extensions
            for ext in [".png", ".jpg", ".jpeg", ".bmp"]:
                candidate = d / (rec["filename"] + ext)
                if candidate.exists():
                    rec["filename"] = rec["filename"] + ext
                    found = True
                    break
            if found:
                break

        if not found:
            missing += 1
            continue
        valid.append(rec)

    if missing:
        print(f"Warning: {missing} images not found, skipped.")
    return valid


def generate_manifest(records: list[dict]):
    """Write manifest.csv with columns: filename, latex, split."""
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["filename", "latex", "split"])
        writer.writeheader()
        writer.writerows(records)
    print(f"Manifest written to {MANIFEST_PATH} ({len(records)} records)")


def main():
    download_hme100k()

    print("\nLooking for labels files...")
    train_labels = _find_labels_file("train_labels.txt")
    test_labels = _find_labels_file("test_labels.txt")

    if not train_labels:
        print("ERROR: train_labels.txt not found anywhere in dataset directory.")
        print(f"Please check: {DATASET_DIR}")
        sys.exit(1)

    train_images = _find_images_dir("train")
    test_images = _find_images_dir("test")

    print(f"  Train labels: {train_labels}")
    print(f"  Test labels:  {test_labels}")
    print(f"  Train images dir: {train_images}")
    print(f"  Test images dir:  {test_images}")

    print("\nParsing labels...")
    train_records = parse_labels(train_labels, "train", train_images)
    test_records = parse_labels(test_labels, "test", test_images) if test_labels else []
    print(f"  Train labels: {len(train_records)}")
    print(f"  Test labels:  {len(test_records)}")

    print("\nValidating images...")
    all_records = validate_images(train_records + test_records)

    train_count = sum(1 for r in all_records if r["split"] == "train")
    test_count = sum(1 for r in all_records if r["split"] == "test")
    print(f"  Valid train: {train_count}")
    print(f"  Valid test:  {test_count}")

    generate_manifest(all_records)
    print("\nDone!")


if __name__ == "__main__":
    main()
