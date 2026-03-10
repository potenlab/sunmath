"""Convert CROHME InkML files to PNG images with LaTeX labels.

Usage:
    python data/datasets/scripts/convert_crohme.py

Parses InkML files from data/datasets/crohme/raw/,
renders strokes to PNG, and generates manifest.csv.

Expected output: ~3,900 rendered images with LaTeX labels
"""

import csv
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

DATASET_DIR = Path(__file__).resolve().parents[1] / "crohme"
RAW_DIR = DATASET_DIR / "raw"
IMAGES_DIR = DATASET_DIR / "images"
MANIFEST_PATH = DATASET_DIR / "manifest.csv"

IMAGE_SIZE = 256
LINE_WIDTH = 2.5
DPI = 72

# InkML namespace
INKML_NS = {"ink": "http://www.w3.org/2003/InkML"}


def parse_inkml(filepath: Path) -> dict | None:
    """Parse an InkML file to extract strokes and LaTeX annotation.

    Returns dict with 'strokes' (list of np arrays) and 'latex' (str),
    or None if parsing fails.
    """
    try:
        tree = ET.parse(filepath)
    except ET.ParseError:
        return None

    root = tree.getroot()

    # Extract LaTeX annotation
    latex = None
    # Try with namespace
    for annotation in root.findall(".//ink:annotation", INKML_NS):
        if annotation.get("type") == "truth":
            latex = annotation.text
            break
    # Try without namespace
    if latex is None:
        for annotation in root.iter():
            tag = annotation.tag.split("}")[-1] if "}" in annotation.tag else annotation.tag
            if tag == "annotation" and annotation.get("type") == "truth":
                latex = annotation.text
                break

    if not latex:
        return None

    # Clean LaTeX: remove $ wrappers
    latex = latex.strip()
    if latex.startswith("$") and latex.endswith("$"):
        latex = latex[1:-1].strip()

    # Extract strokes (traces)
    strokes = []
    for trace in root.iter():
        tag = trace.tag.split("}")[-1] if "}" in trace.tag else trace.tag
        if tag != "trace":
            continue
        text = trace.text
        if not text:
            continue
        points = []
        for point_str in text.strip().split(","):
            coords = point_str.strip().split()
            if len(coords) >= 2:
                try:
                    x, y = float(coords[0]), float(coords[1])
                    points.append([x, y])
                except ValueError:
                    continue
        if len(points) >= 2:
            strokes.append(np.array(points))

    if not strokes:
        return None

    return {"strokes": strokes, "latex": latex}


def render_strokes(strokes: list[np.ndarray], output_path: Path):
    """Render stroke data to a PNG image (white bg, black strokes)."""
    fig, ax = plt.subplots(1, 1, figsize=(IMAGE_SIZE / DPI, IMAGE_SIZE / DPI), dpi=DPI)
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")

    for stroke in strokes:
        ax.plot(stroke[:, 0], -stroke[:, 1], "k-", linewidth=LINE_WIDTH)

    ax.set_aspect("equal")
    ax.axis("off")

    # Add small margin
    ax.margins(0.1)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        output_path,
        bbox_inches="tight",
        pad_inches=0.05,
        facecolor="white",
        dpi=DPI,
    )
    plt.close(fig)


def detect_split(filepath: Path) -> str:
    """Detect train/test/val split from file path."""
    parts = str(filepath).lower()
    if "test" in parts:
        return "test"
    if "val" in parts or "valid" in parts:
        return "val"
    return "train"


def main():
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    inkml_files = list(RAW_DIR.rglob("*.inkml"))
    if not inkml_files:
        print(f"No InkML files found in {RAW_DIR}")
        print("Run download_crohme.py first.")
        return

    print(f"Found {len(inkml_files)} InkML files")

    records = []
    errors = 0

    for i, inkml_path in enumerate(inkml_files):
        if (i + 1) % 100 == 0:
            print(f"  Processing {i + 1}/{len(inkml_files)}...")

        parsed = parse_inkml(inkml_path)
        if parsed is None:
            errors += 1
            continue

        split = detect_split(inkml_path)
        filename = f"{inkml_path.stem}.png"
        output_path = IMAGES_DIR / split / filename

        try:
            render_strokes(parsed["strokes"], output_path)
        except Exception as e:
            print(f"  Error rendering {inkml_path.name}: {e}")
            errors += 1
            continue

        records.append({
            "filename": f"{split}/{filename}",
            "latex": parsed["latex"],
            "split": split,
        })

    # Write manifest
    with open(MANIFEST_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["filename", "latex", "split"])
        writer.writeheader()
        writer.writerows(records)

    print(f"\nConversion complete!")
    print(f"  Total processed: {len(records)}")
    print(f"  Errors: {errors}")

    # Split breakdown
    split_counts = {}
    for r in records:
        split_counts[r["split"]] = split_counts.get(r["split"], 0) + 1
    for split, count in sorted(split_counts.items()):
        print(f"  {split}: {count}")

    print(f"\nManifest: {MANIFEST_PATH}")
    print(f"Images:   {IMAGES_DIR}")


if __name__ == "__main__":
    main()
