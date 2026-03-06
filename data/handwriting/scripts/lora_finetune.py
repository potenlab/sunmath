#!/usr/bin/env python3
"""
Phase 3.2: LoRA Fine-Tuning for Math Handwriting OCR
Uploads training data to GCS, creates tuning job, and measures post-tuning accuracy.
"""

import csv
import json
import os
import sys
import time
from pathlib import Path

import vertexai
from vertexai.tuning import sft
from vertexai.generative_models import GenerativeModel, Image
from google.cloud import storage

# --- Config ---
PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "express-auth-414411")
LOCATION = os.environ.get("GCP_LOCATION", "us-central1")
SOURCE_MODEL = "gemini-2.0-flash-001"
BUCKET_NAME = f"{PROJECT_ID}-sunmath-ocr"

BASE_DIR = Path(__file__).resolve().parent.parent
IMAGES_DIR = BASE_DIR / "images"
MANIFEST_PATH = BASE_DIR / "manifest.csv"
RESULTS_DIR = BASE_DIR / "results"

SYSTEM_INSTRUCTION = (
    "You are a math OCR system. Given a handwritten math formula image, "
    "output ONLY the LaTeX representation. Do not wrap in $ signs or delimiters. "
    "Use standard LaTeX commands."
)

USER_PROMPT = "Convert this handwritten math formula to LaTeX:"


def load_manifest() -> list[dict]:
    """Load manifest.csv."""
    entries = []
    with open(MANIFEST_PATH, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entries.append(row)
    return entries


def create_bucket_if_needed(bucket_name: str) -> storage.Bucket:
    """Create GCS bucket if it doesn't exist."""
    client = storage.Client(project=PROJECT_ID)
    try:
        bucket = client.get_bucket(bucket_name)
        print(f"Bucket {bucket_name} already exists")
    except Exception:
        bucket = client.create_bucket(bucket_name, location=LOCATION)
        print(f"Created bucket {bucket_name}")
    return bucket


def upload_images_to_gcs(bucket: storage.Bucket, entries: list[dict]) -> dict[str, str]:
    """Upload all images to GCS and return mapping of filename -> gs:// URI."""
    uri_map = {}
    for entry in entries:
        local_path = IMAGES_DIR / entry["filename"]
        if not local_path.exists():
            print(f"  SKIP: {entry['filename']} (file not found)")
            continue

        blob_name = f"training-images/{entry['filename']}"
        blob = bucket.blob(blob_name)

        if not blob.exists():
            blob.upload_from_filename(str(local_path), content_type="image/jpeg")
            print(f"  Uploaded: {entry['filename']}")
        else:
            print(f"  Exists:   {entry['filename']}")

        uri_map[entry["filename"]] = f"gs://{bucket.name}/{blob_name}"
    return uri_map


def create_training_jsonl(entries: list[dict], uri_map: dict[str, str], output_path: Path):
    """Create JSONL training file in Vertex AI format."""
    lines = []
    for entry in entries:
        filename = entry["filename"]
        if filename not in uri_map:
            continue

        example = {
            "systemInstruction": {
                "role": "user",
                "parts": [{"text": SYSTEM_INSTRUCTION}],
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "fileData": {
                                "mimeType": "image/jpeg",
                                "fileUri": uri_map[filename],
                            }
                        },
                        {"text": USER_PROMPT},
                    ],
                },
                {
                    "role": "model",
                    "parts": [{"text": entry["latex"]}],
                },
            ],
        }
        lines.append(json.dumps(example))

    with open(output_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Created training JSONL with {len(lines)} examples at {output_path}")
    return len(lines)


def upload_jsonl_to_gcs(bucket: storage.Bucket, local_path: Path, gcs_path: str) -> str:
    """Upload JSONL to GCS and return URI."""
    blob = bucket.blob(gcs_path)
    blob.upload_from_filename(str(local_path), content_type="application/jsonl")
    uri = f"gs://{bucket.name}/{gcs_path}"
    print(f"Uploaded JSONL to {uri}")
    return uri


def run_tuning_job(train_uri: str, validation_uri: str = None) -> sft.SupervisedTuningJob:
    """Submit and monitor a supervised fine-tuning job."""
    print(f"\nSubmitting tuning job...")
    print(f"  Source model:  {SOURCE_MODEL}")
    print(f"  Training data: {train_uri}")

    kwargs = {
        "source_model": SOURCE_MODEL,
        "train_dataset": train_uri,
    }
    if validation_uri:
        kwargs["validation_dataset"] = validation_uri

    tuning_job = sft.train(**kwargs)
    print(f"  Job created: {tuning_job.resource_name}")

    # Monitor progress
    start_time = time.time()
    while not tuning_job.has_ended:
        elapsed = int(time.time() - start_time)
        print(f"  [{elapsed}s] Status: {tuning_job.state}...")
        time.sleep(60)
        tuning_job.refresh()

    elapsed = int(time.time() - start_time)
    print(f"\nTuning job completed in {elapsed}s")
    print(f"  Final state: {tuning_job.state}")

    if tuning_job.tuned_model_endpoint_name:
        print(f"  Tuned model endpoint: {tuning_job.tuned_model_endpoint_name}")
    if tuning_job.tuned_model_name:
        print(f"  Tuned model name: {tuning_job.tuned_model_name}")

    return tuning_job


def evaluate_tuned_model(tuning_job: sft.SupervisedTuningJob, entries: list[dict]) -> dict:
    """Run OCR with the tuned model and measure accuracy."""
    from baseline_ocr import normalize_latex, latex_matches, categorize_error

    endpoint = tuning_job.tuned_model_endpoint_name
    print(f"\nEvaluating tuned model: {endpoint}")

    model = GenerativeModel(endpoint)
    results = []
    exact_matches = 0
    normalized_matches = 0

    for i, entry in enumerate(entries):
        image_path = IMAGES_DIR / entry["filename"]
        if not image_path.exists():
            continue

        print(f"  [{i+1}/{len(entries)}] {entry['filename']}", end=" ")

        try:
            img = Image.load_from_file(str(image_path))
            response = model.generate_content([USER_PROMPT, img])
            predicted = response.text.strip()

            exact, normalized = latex_matches(predicted, entry["latex"])
            if exact:
                exact_matches += 1
            if normalized:
                normalized_matches += 1

            print(f"{'MATCH' if normalized else 'MISS'}")
            results.append({
                **entry,
                "predicted": predicted,
                "exact_match": exact,
                "normalized_match": normalized,
            })
            time.sleep(4)

        except Exception as e:
            if "429" in str(e):
                print("RATE_LIMITED")
                time.sleep(15)
            else:
                print(f"ERROR: {e}")
            results.append({
                **entry,
                "predicted": f"ERROR: {str(e)[:200]}",
                "exact_match": False,
                "normalized_match": False,
            })

    tested = len([r for r in results if not r["predicted"].startswith("ERROR:")])
    print(f"\nTuned Model Results:")
    print(f"  Tested:            {tested}/{len(entries)}")
    print(f"  Exact matches:     {exact_matches}/{tested} ({exact_matches/max(tested,1)*100:.1f}%)")
    print(f"  Normalized matches:{normalized_matches}/{tested} ({normalized_matches/max(tested,1)*100:.1f}%)")

    return {
        "model": endpoint,
        "tested": tested,
        "exact_matches": exact_matches,
        "exact_accuracy": round(exact_matches / max(tested, 1) * 100, 2),
        "normalized_matches": normalized_matches,
        "normalized_accuracy": round(normalized_matches / max(tested, 1) * 100, 2),
        "detailed_results": results,
    }


def main():
    print("=" * 70)
    print("Phase 3.2: LoRA Fine-Tuning for Math OCR")
    print("=" * 70)

    # Init
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    entries = load_manifest()
    print(f"Loaded {len(entries)} entries from manifest")

    # Split into train (80%) and validation (20%)
    import random
    random.seed(42)
    shuffled = entries.copy()
    random.shuffle(shuffled)
    split_idx = int(len(shuffled) * 0.8)
    train_entries = shuffled[:split_idx]
    val_entries = shuffled[split_idx:]
    print(f"Train: {len(train_entries)}, Validation: {len(val_entries)}")

    # Step 1: Create GCS bucket and upload images
    print(f"\n--- Step 1: Upload images to GCS ---")
    bucket = create_bucket_if_needed(BUCKET_NAME)
    uri_map = upload_images_to_gcs(bucket, entries)
    print(f"Uploaded {len(uri_map)} images")

    # Step 2: Create training JSONL
    print(f"\n--- Step 2: Create training data ---")
    RESULTS_DIR.mkdir(exist_ok=True)
    train_jsonl = RESULTS_DIR / "sft_train_data.jsonl"
    val_jsonl = RESULTS_DIR / "sft_val_data.jsonl"
    create_training_jsonl(train_entries, uri_map, train_jsonl)
    create_training_jsonl(val_entries, uri_map, val_jsonl)

    # Upload JSONL to GCS
    train_uri = upload_jsonl_to_gcs(bucket, train_jsonl, "training-data/sft_train_data.jsonl")
    val_uri = upload_jsonl_to_gcs(bucket, val_jsonl, "training-data/sft_val_data.jsonl")

    # Step 3: Submit tuning job
    print(f"\n--- Step 3: Run tuning job ---")
    tuning_job = run_tuning_job(train_uri, val_uri)

    # Step 4: Evaluate tuned model
    print(f"\n--- Step 4: Evaluate tuned model ---")
    eval_results = evaluate_tuned_model(tuning_job, entries)

    # Save results
    results_file = RESULTS_DIR / "lora_finetune_results.json"
    with open(results_file, "w") as f:
        json.dump({
            "source_model": SOURCE_MODEL,
            "tuning_job": tuning_job.resource_name,
            "tuned_model": tuning_job.tuned_model_endpoint_name,
            "train_examples": len(train_entries),
            "val_examples": len(val_entries),
            "evaluation": eval_results,
        }, f, indent=2)
    print(f"\nResults saved to {results_file}")


if __name__ == "__main__":
    # Check for sub-commands
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "prepare-only":
            # Only prepare data, don't run tuning
            vertexai.init(project=PROJECT_ID, location=LOCATION)
            entries = load_manifest()
            bucket = create_bucket_if_needed(BUCKET_NAME)
            uri_map = upload_images_to_gcs(bucket, entries)
            RESULTS_DIR.mkdir(exist_ok=True)
            train_jsonl = RESULTS_DIR / "sft_train_data.jsonl"
            create_training_jsonl(entries, uri_map, train_jsonl)
            train_uri = upload_jsonl_to_gcs(bucket, train_jsonl, "training-data/sft_train_data.jsonl")
            print(f"\nData prepared. Training URI: {train_uri}")
            sys.exit(0)
    main()
