#!/usr/bin/env python3
"""Generate synthetic handwritten math formula images from manifest.csv.

Renders each LaTeX formula using matplotlib and applies distortions
based on the style column (clean/messy/unusual) to simulate handwriting.

Usage:
    python data/handwriting/scripts/generate_images.py
    python data/handwriting/scripts/generate_images.py --style messy   # only messy
    python data/handwriting/scripts/generate_images.py --category integrals
    python data/handwriting/scripts/generate_images.py --force         # overwrite existing
"""

import argparse
import csv
import io
import random
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image, ImageEnhance, ImageFilter  # noqa: E402

SCRIPT_DIR = Path(__file__).resolve().parent
HANDWRITING_DIR = SCRIPT_DIR.parent
IMAGES_DIR = HANDWRITING_DIR / "images"
MANIFEST_PATH = HANDWRITING_DIR / "manifest.csv"

# Ink colors that look like pen/pencil
INK_COLORS = [
    "#1a1a1a",  # near-black
    "#2b2b2b",  # dark gray
    "#0d0d3b",  # dark blue-black
    "#1a0a0a",  # very dark brown
]

# Paper tint colors (off-white variations)
PAPER_COLORS = [
    (255, 255, 255),  # white
    (252, 250, 245),  # warm white
    (248, 248, 252),  # cool white
    (255, 253, 245),  # cream
    (245, 245, 240),  # gray-white
]


def _is_matrix_latex(latex: str) -> bool:
    """Check if LaTeX uses environments not supported by matplotlib mathtext."""
    unsupported = ["\\begin{", "\\end{"]
    return any(kw in latex for kw in unsupported)


def _render_matrix_image(latex: str, fontsize: int, color: str) -> Image.Image:
    """Render matrix/environment LaTeX by drawing bracketed grid manually.

    Matplotlib's mathtext doesn't support \\begin{pmatrix} etc., so we parse
    the matrix content and draw it as a grid with bracket characters.
    """
    import re

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # Detect bracket type
    if "vmatrix" in latex:
        left_bracket, right_bracket = "|", "|"
    elif "array" in latex and "left(" in latex:
        left_bracket, right_bracket = "(", ")"
    elif "pmatrix" in latex:
        left_bracket, right_bracket = "(", ")"
    else:
        left_bracket, right_bracket = "[", "]"

    # Check for prefix like \det
    prefix = ""
    det_match = re.match(r"^(\\det)\s*\\begin", latex)
    if det_match:
        prefix = "det "

    # Check for suffix like =ad-bc
    suffix = ""
    suffix_match = re.search(r"\\end\{[^}]+\}\s*(.+)$", latex)
    if suffix_match:
        suffix = " " + suffix_match.group(1).replace("\\", "")

    # Extract rows from matrix content
    env_match = re.search(r"\\begin\{[^}]+\}(?:\{[^}]*\})?\s*(.*?)\s*\\end\{[^}]+\}", latex)
    if env_match:
        content = env_match.group(1)
        rows_raw = content.split("\\\\")
        matrix_rows = []
        for r in rows_raw:
            r = r.strip()
            if r:
                cells = [c.strip() for c in r.split("&")]
                matrix_rows.append(cells)
    else:
        # Fallback: just render as text
        ax.text(0.5, 0.5, latex, fontsize=fontsize * 0.6, ha="center",
                va="center", color=color, family="serif")
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                    pad_inches=0.4, facecolor="white")
        plt.close(fig)
        buf.seek(0)
        return Image.open(buf).convert("RGB")

    nrows = len(matrix_rows)
    ncols = max(len(r) for r in matrix_rows) if matrix_rows else 1
    cell_size = min(0.12, 0.6 / max(nrows, ncols))
    small_font = int(fontsize * 0.7)

    # Center offset
    total_w = ncols * cell_size
    total_h = nrows * cell_size
    x_start = 0.5 - total_w / 2
    y_start = 0.5 + total_h / 2

    # Draw bracket characters
    bracket_font = int(fontsize * 0.5 * max(nrows, 2))
    ax.text(x_start - 0.06, 0.5, left_bracket, fontsize=bracket_font,
            ha="center", va="center", color=color, family="serif")
    ax.text(x_start + total_w + 0.06, 0.5, right_bracket, fontsize=bracket_font,
            ha="center", va="center", color=color, family="serif")

    # Draw prefix/suffix
    if prefix:
        ax.text(x_start - 0.16, 0.5, prefix, fontsize=small_font,
                ha="center", va="center", color=color, family="serif")
    if suffix:
        ax.text(x_start + total_w + 0.18, 0.5, suffix, fontsize=small_font,
                ha="center", va="center", color=color, family="serif")

    # Draw cell contents
    for i, row_cells in enumerate(matrix_rows):
        for j, cell in enumerate(row_cells):
            x = x_start + (j + 0.5) * cell_size
            y = y_start - (i + 0.5) * cell_size
            # Try rendering as mathtext, fall back to plain text
            try:
                ax.text(x, y, f"${cell}$", fontsize=small_font,
                        ha="center", va="center", color=color, family="serif")
            except Exception:
                ax.text(x, y, cell, fontsize=small_font,
                        ha="center", va="center", color=color, family="serif")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                pad_inches=0.4, facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf).convert("RGB")


def render_latex_to_image(latex: str, fontsize: int = 36) -> Image.Image:
    """Render a LaTeX string to a PIL Image using matplotlib."""
    color = random.choice(INK_COLORS)

    if _is_matrix_latex(latex):
        return _render_matrix_image(latex, fontsize, color)

    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.text(
        0.5, 0.5,
        f"${latex}$",
        fontsize=fontsize,
        ha="center", va="center",
        transform=ax.transAxes,
        color=color,
    )
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")
    ax.axis("off")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                pad_inches=0.4, facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf).convert("RGB")


def add_paper_texture(img: Image.Image, intensity: float = 0.3) -> Image.Image:
    """Add subtle paper-like texture/grain."""
    arr = np.array(img, dtype=np.float32)
    # Fine grain noise
    grain = np.random.normal(0, intensity * 8, arr.shape)
    arr = np.clip(arr + grain, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def tint_paper(img: Image.Image) -> Image.Image:
    """Apply a subtle paper color tint."""
    tint = random.choice(PAPER_COLORS)
    arr = np.array(img, dtype=np.float32)
    tint_arr = np.array(tint, dtype=np.float32)
    # Blend toward tint where pixels are bright (paper areas)
    brightness = arr.mean(axis=2, keepdims=True) / 255.0
    arr = arr * (1 - brightness * 0.1) + tint_arr * (brightness * 0.1)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def apply_clean(img: Image.Image) -> Image.Image:
    """Clean style: minimal distortion, slight texture."""
    img = tint_paper(img)
    img = add_paper_texture(img, intensity=0.15)
    # Very slight rotation (like slightly tilted paper)
    angle = random.uniform(-1.0, 1.0)
    img = img.rotate(angle, fillcolor=(255, 255, 255), expand=True)
    return img


def apply_messy(img: Image.Image) -> Image.Image:
    """Messy style: noise, rotation, blur, contrast variation."""
    img = tint_paper(img)
    img = add_paper_texture(img, intensity=0.5)

    # Rotation (like hurried writing)
    angle = random.uniform(-4, 4)
    img = img.rotate(angle, fillcolor=(255, 255, 255), expand=True)

    # Slight blur (like slightly unfocused photo)
    img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.5, 1.2)))

    # Contrast variation
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(random.uniform(0.8, 1.1))

    # Brightness variation (like uneven lighting)
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(random.uniform(0.92, 1.05))

    return img


def apply_unusual(img: Image.Image) -> Image.Image:
    """Unusual style: heavier transforms, perspective-like skew, more noise."""
    img = tint_paper(img)
    img = add_paper_texture(img, intensity=0.7)

    # Larger rotation
    angle = random.uniform(-7, 7)
    img = img.rotate(angle, fillcolor=(255, 255, 255), expand=True)

    # Perspective-like transform via affine shear
    w, h = img.size
    shear = random.uniform(-0.08, 0.08)
    coeffs = (1, shear, -shear * h / 2, 0, 1, 0)
    img = img.transform((w, h), Image.AFFINE, coeffs, fillcolor=(255, 255, 255))

    # Heavier blur
    img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.8, 1.8)))

    # Reduce sharpness slightly
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(random.uniform(0.6, 0.9))

    # Contrast drop (like faded ink)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(random.uniform(0.65, 0.9))

    return img


STYLE_FUNCS = {
    "clean": apply_clean,
    "messy": apply_messy,
    "unusual": apply_unusual,
}


def load_manifest(filter_style=None, filter_category=None) -> list[dict]:
    """Load and optionally filter manifest rows."""
    rows = []
    with open(MANIFEST_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if filter_style and row["style"] != filter_style:
                continue
            if filter_category and row["category"] != filter_category:
                continue
            rows.append(row)
    return rows


def generate_image(row: dict) -> Image.Image:
    """Generate a single synthetic image for a manifest row."""
    latex = row["latex"]
    style = row["style"]

    # Adjust fontsize based on complexity
    length = len(latex)
    if length > 80:
        fontsize = 24
    elif length > 50:
        fontsize = 28
    elif length > 30:
        fontsize = 32
    else:
        fontsize = 36

    img = render_latex_to_image(latex, fontsize=fontsize)
    style_func = STYLE_FUNCS.get(style, apply_clean)
    img = style_func(img)
    return img


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic handwriting images")
    parser.add_argument("--style", choices=["clean", "messy", "unusual"],
                        help="Only generate images for this style")
    parser.add_argument("--category", help="Only generate images for this category")
    parser.add_argument("--force", action="store_true",
                        help="Overwrite existing images")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for reproducibility")
    args = parser.parse_args()

    random.seed(args.seed)
    np.random.seed(args.seed)

    rows = load_manifest(filter_style=args.style, filter_category=args.category)
    if not rows:
        print("No matching rows in manifest.")
        return 0

    print(f"Generating {len(rows)} images...")
    success = 0
    failed = []

    for row in rows:
        out_path = IMAGES_DIR / row["filename"]

        if out_path.exists() and not args.force:
            print(f"  [{row['id']:>3}] SKIP (exists): {row['filename']}")
            success += 1
            continue

        try:
            img = generate_image(row)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(str(out_path), "JPEG", quality=92)
            print(f"  [{row['id']:>3}] OK: {row['filename']}")
            success += 1
        except Exception as e:
            print(f"  [{row['id']:>3}] FAIL: {row['filename']} — {e}")
            failed.append(row)

    print(f"\nDone: {success}/{len(rows)} generated")
    if failed:
        print(f"Failed ({len(failed)}):")
        for row in failed:
            print(f"  [{row['id']}] {row['filename']} — {row['latex']}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
