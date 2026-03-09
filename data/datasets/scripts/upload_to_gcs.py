"""Upload baseline dataset images to GCS and generate Vertex AI SFT JSONL.

Usage:
    python data/datasets/scripts/upload_to_gcs.py \
        --bucket express-auth-414411-sunmath-ocr \
        --credentials google.json

Uploads images to gs://{bucket}/baseline/images/{dataset}/{filename}
Generates JSONL in the same format as lora_training.py
"""

import argparse
import csv
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from google.cloud import storage
from google.oauth2 import service_account

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

DATASETS_DIR = Path(__file__).resolve().parents[1]
BASELINE_DIR = DATASETS_DIR / "baseline"
PROGRESS_FILE = BASELINE_DIR / "upload_progress.json"

# Reuse exact same constants from lora_training.py
SYSTEM_INSTRUCTION = (
    "You are a math OCR system. Given a handwritten math formula image, "
    "output ONLY the LaTeX representation. Do not wrap in $ signs or delimiters. "
    "Use standard LaTeX commands."
)

USER_PROMPT = "Convert this handwritten math formula to LaTeX:"

CONTENT_TYPE_MAP = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".bmp": "image/bmp",
    ".webp": "image/webp",
}

NUM_WORKERS = 16


def get_gcs_client(credentials_path: str | None, project_id: str | None) -> storage.Client:
    if credentials_path:
        creds = service_account.Credentials.from_service_account_file(credentials_path)
        return storage.Client(project=project_id, credentials=creds)
    return storage.Client(project=project_id)


def load_progress() -> set[str]:
    """Load set of already-uploaded filenames for resume support."""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, "r") as f:
            data = json.load(f)
            return set(data.get("uploaded", []))
    return set()


def save_progress(uploaded: set[str]):
    """Save progress to disk."""
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, "w") as f:
        json.dump({"uploaded": list(uploaded)}, f)


def resolve_image_path(filename: str, dataset: str) -> Path | None:
    """Resolve the local path for an image file."""
    dataset_dir = DATASETS_DIR / dataset
    # Direct path
    path = dataset_dir / filename
    if path.exists():
        return path
    # Try under images/
    path = dataset_dir / "images" / filename
    if path.exists():
        return path
    # Try under train/test dirs
    for subdir in ["train", "test", "val"]:
        path = dataset_dir / subdir / filename
        if path.exists():
            return path
    return None


def upload_single_image(
    client: storage.Client,
    bucket_name: str,
    local_path: Path,
    gcs_blob_name: str,
    content_type: str,
) -> str:
    """Upload a single image to GCS. Returns the gs:// URI."""
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(gcs_blob_name)
    blob.upload_from_filename(str(local_path), content_type=content_type)
    return f"gs://{bucket_name}/{gcs_blob_name}"


def build_sft_example(gcs_uri: str, content_type: str, latex: str) -> dict:
    """Build a single SFT training example in Vertex AI format.

    Same format as lora_training.py lines 111-139.
    """
    return {
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
                            "mimeType": content_type,
                            "fileUri": gcs_uri,
                        }
                    },
                    {"text": USER_PROMPT},
                ],
            },
            {
                "role": "model",
                "parts": [{"text": latex}],
            },
        ],
    }


def process_manifest(
    manifest_path: Path,
    split_name: str,
    bucket_name: str,
    credentials_path: str | None,
    project_id: str | None,
) -> list[dict]:
    """Upload images from a manifest and return SFT examples."""
    records = []
    with open(manifest_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        records = list(reader)

    if not records:
        print(f"  No records in {manifest_path}")
        return []

    uploaded = load_progress()
    client = get_gcs_client(credentials_path, project_id)
    sft_examples = []
    to_upload = []

    for rec in records:
        filename = rec["filename"]
        dataset = rec["dataset"]
        latex = rec["latex"]
        ext = Path(filename).suffix.lower()
        content_type = CONTENT_TYPE_MAP.get(ext, "image/png")

        gcs_blob_name = f"baseline/images/{dataset}/{filename}"
        gcs_uri = f"gs://{bucket_name}/{gcs_blob_name}"

        if filename in uploaded:
            # Already uploaded, just build the SFT example
            sft_examples.append(build_sft_example(gcs_uri, content_type, latex))
            continue

        local_path = resolve_image_path(filename, dataset)
        if local_path is None:
            continue

        to_upload.append({
            "local_path": local_path,
            "gcs_blob_name": gcs_blob_name,
            "gcs_uri": gcs_uri,
            "content_type": content_type,
            "latex": latex,
            "filename": filename,
        })

    print(f"  {split_name}: {len(sft_examples)} already uploaded, {len(to_upload)} to upload")

    if to_upload:
        iterator = tqdm(total=len(to_upload), desc=f"  Uploading {split_name}") if tqdm else None

        with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
            futures = {}
            for item in to_upload:
                future = executor.submit(
                    upload_single_image,
                    client,
                    bucket_name,
                    item["local_path"],
                    item["gcs_blob_name"],
                    item["content_type"],
                )
                futures[future] = item

            for future in as_completed(futures):
                item = futures[future]
                try:
                    future.result()
                    sft_examples.append(
                        build_sft_example(item["gcs_uri"], item["content_type"], item["latex"])
                    )
                    uploaded.add(item["filename"])
                except Exception as e:
                    print(f"\n  Error uploading {item['filename']}: {e}")

                if iterator:
                    iterator.update(1)

        if iterator:
            iterator.close()

        save_progress(uploaded)

    return sft_examples


def upload_jsonl(
    client: storage.Client,
    bucket_name: str,
    examples: list[dict],
    gcs_path: str,
):
    """Upload JSONL data to GCS."""
    jsonl_content = "\n".join(json.dumps(ex) for ex in examples) + "\n"
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(gcs_path)
    blob.upload_from_string(jsonl_content, content_type="application/jsonl")
    uri = f"gs://{bucket_name}/{gcs_path}"
    print(f"  Uploaded JSONL: {uri} ({len(examples)} examples)")
    return uri


def main():
    parser = argparse.ArgumentParser(description="Upload baseline dataset to GCS")
    parser.add_argument("--bucket", required=True, help="GCS bucket name")
    parser.add_argument("--credentials", default=None, help="Path to service account JSON")
    parser.add_argument("--project", default=None, help="GCP project ID")
    args = parser.parse_args()

    train_manifest = BASELINE_DIR / "train_manifest.csv"
    val_manifest = BASELINE_DIR / "val_manifest.csv"

    if not train_manifest.exists():
        print(f"Train manifest not found: {train_manifest}")
        print("Run prepare_baseline.py first.")
        return

    print("Uploading training images...")
    train_examples = process_manifest(
        train_manifest, "train", args.bucket, args.credentials, args.project
    )

    val_examples = []
    if val_manifest.exists():
        print("\nUploading validation images...")
        val_examples = process_manifest(
            val_manifest, "val", args.bucket, args.credentials, args.project
        )

    print("\nUploading JSONL files...")
    client = get_gcs_client(args.credentials, args.project)

    train_uri = upload_jsonl(
        client, args.bucket, train_examples, "baseline/training-data/sft_train.jsonl"
    )
    if val_examples:
        val_uri = upload_jsonl(
            client, args.bucket, val_examples, "baseline/training-data/sft_val.jsonl"
        )

    print("\nDone!")
    print(f"\nUse these URIs for baseline training:")
    print(f"  Train: gs://{args.bucket}/baseline/training-data/sft_train.jsonl")
    if val_examples:
        print(f"  Val:   gs://{args.bucket}/baseline/training-data/sft_val.jsonl")


if __name__ == "__main__":
    main()
