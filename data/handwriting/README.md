# Handwriting OCR Data Collection

This folder contains the scaffold for collecting handwritten math formula images
used to test and fine-tune OCR models (Phase 3 / Task 2).

## Directory Structure

```
data/handwriting/
├── manifest.csv           # Master list of all formulas
├── images/
│   ├── fractions/         # IMG_001 – IMG_010
│   ├── radicals/          # IMG_011 – IMG_018
│   ├── exponents/         # IMG_019 – IMG_026
│   ├── integrals/         # IMG_027 – IMG_036
│   ├── matrices/          # IMG_037 – IMG_045
│   └── mixed/             # IMG_046 – IMG_055
└── scripts/
    └── validate_manifest.py
```

## How to Contribute Images

### 1. Check the manifest

Open `manifest.csv` to see the full list of formulas. Each row has:

| Column | Description |
|--------|-------------|
| `id` | Unique integer ID |
| `filename` | Target path, e.g. `fractions/IMG_001.jpg` |
| `latex` | The LaTeX formula to write by hand |
| `category` | fractions, radicals, exponents, integrals, matrices, mixed |
| `difficulty` | easy, medium, hard |
| `style` | **clean**, **messy**, or **unusual** (see below) |

### 2. Write the formula by hand

- **clean** — Neat, legible handwriting on lined or blank white paper.
- **messy** — Deliberately casual or hurried handwriting. Slightly uneven
  spacing, imperfect symbols. Mimics real student work.
- **unusual** — Non-standard notation, rotated paper, colored ink, cramped
  spacing, or other edge-case styles.

### 3. Photograph the formula

- Use a **white or light background** (plain paper works best).
- Use a **dark pen or pencil** (avoid light colors like yellow).
- Ensure **good, even lighting** — avoid shadows across the formula.
- Frame the formula so it fills most of the image, with a small margin.
- Hold the camera **directly above** (not at an angle) to avoid distortion.
- Resolution doesn't matter much — phone cameras are fine.

### 4. Save the image

- Name the file to match `manifest.csv` exactly, e.g. `IMG_001.jpg`.
- Place it in the correct subdirectory under `images/`.
- Accepted formats: **JPG** or **PNG** (any resolution).

### 5. Validate

Run the validation script to check coverage:

```bash
python data/handwriting/scripts/validate_manifest.py
```

It will report how many images are collected per category and flag any issues.

## Notes

- The manifest currently has **55 formulas**. More will be added to reach
  100–200 pairs for LoRA training.
- Each formula appears once. For LoRA training, we may collect multiple
  handwriting samples per formula (different people/styles).
- Do NOT rename or reorganize files without updating `manifest.csv`.
