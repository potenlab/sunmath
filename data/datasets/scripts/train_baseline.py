"""Submit a Vertex AI SFT job for the baseline OCR model.

Usage:
    python data/datasets/scripts/train_baseline.py \
        --credentials google.json \
        --project express-auth-414411 \
        --bucket express-auth-414411-sunmath-ocr \
        --poll
"""

import argparse
import sys
import time

import vertexai
from google.oauth2 import service_account
from vertexai.tuning import sft

# Same source model as lora_training.py
SOURCE_MODEL = "gemini-2.0-flash-001"

POLL_INTERVAL_SECONDS = 60


def main():
    parser = argparse.ArgumentParser(
        description="Train baseline LoRA model via Vertex AI SFT"
    )
    parser.add_argument(
        "--credentials", default=None, help="Path to GCP service account JSON"
    )
    parser.add_argument("--project", required=True, help="GCP project ID")
    parser.add_argument("--location", default="us-central1", help="GCP region")
    parser.add_argument("--bucket", required=True, help="GCS bucket name")
    parser.add_argument(
        "--train-uri",
        default=None,
        help="Override train JSONL URI (default: gs://{bucket}/baseline/training-data/sft_train.jsonl)",
    )
    parser.add_argument(
        "--val-uri",
        default=None,
        help="Override val JSONL URI (default: gs://{bucket}/baseline/training-data/sft_val.jsonl)",
    )
    parser.add_argument(
        "--poll",
        action="store_true",
        help="Poll until the tuning job completes",
    )
    args = parser.parse_args()

    train_uri = args.train_uri or f"gs://{args.bucket}/baseline/training-data/sft_train.jsonl"
    val_uri = args.val_uri or f"gs://{args.bucket}/baseline/training-data/sft_val.jsonl"

    # Initialize Vertex AI
    credentials = None
    if args.credentials:
        credentials = service_account.Credentials.from_service_account_file(
            args.credentials
        )

    vertexai.init(
        project=args.project,
        location=args.location,
        credentials=credentials,
    )
    print(f"Initialized Vertex AI: project={args.project}, location={args.location}")

    # Submit SFT job
    print(f"\nSubmitting SFT job...")
    print(f"  Source model: {SOURCE_MODEL}")
    print(f"  Train URI:    {train_uri}")
    print(f"  Val URI:      {val_uri}")

    tuning_job = sft.train(
        source_model=SOURCE_MODEL,
        train_dataset=train_uri,
        validation_dataset=val_uri,
    )

    print(f"\nTuning job submitted!")
    print(f"  Job resource name: {tuning_job.resource_name}")

    if not args.poll:
        print("\nRun with --poll to wait for completion, or check status with:")
        print(f"  gcloud ai tuning-jobs describe {tuning_job.resource_name}")
        return

    # Poll until completion
    print("\nPolling for completion...")
    while True:
        tuning_job.refresh()
        state = str(tuning_job.state)
        print(f"  [{time.strftime('%H:%M:%S')}] Status: {state}")

        if tuning_job.has_ended:
            break

        time.sleep(POLL_INTERVAL_SECONDS)

    # Print results
    endpoint = getattr(tuning_job, "tuned_model_endpoint_name", None)
    model_name = getattr(tuning_job, "tuned_model_name", None)

    print(f"\nJob finished!")
    print(f"  Final state:  {tuning_job.state}")
    print(f"  Model name:   {model_name}")
    print(f"  Endpoint:     {endpoint}")

    if endpoint:
        print(f"\nAdd this to your backend/.env:")
        print(f"  BASELINE_MODEL_ENDPOINT={endpoint}")
    else:
        print("\nNo endpoint returned - the job may have failed.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
