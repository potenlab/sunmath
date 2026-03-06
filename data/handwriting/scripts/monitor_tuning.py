#!/usr/bin/env python3
"""Monitor the status of a Vertex AI tuning job and evaluate when complete."""

import json
import os
import sys
import time
from pathlib import Path

import vertexai
from vertexai.tuning import sft
from vertexai.generative_models import GenerativeModel, Image

PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "express-auth-414411")
LOCATION = os.environ.get("GCP_LOCATION", "us-central1")
JOB_RESOURCE = "projects/63184426072/locations/us-central1/tuningJobs/2214170247995326464"

BASE_DIR = Path(__file__).resolve().parent.parent
IMAGES_DIR = BASE_DIR / "images"
RESULTS_DIR = BASE_DIR / "results"

# Add scripts dir to path for importing baseline_ocr
sys.path.insert(0, str(Path(__file__).resolve().parent))
from baseline_ocr import normalize_latex, latex_matches, load_manifest, categorize_error


def main():
    vertexai.init(project=PROJECT_ID, location=LOCATION)

    print(f"Monitoring tuning job: {JOB_RESOURCE}")
    tuning_job = sft.SupervisedTuningJob(JOB_RESOURCE)
    tuning_job.refresh()

    # State mapping (from google.cloud.aiplatform_v1.types)
    state_names = {
        0: "UNSPECIFIED",
        1: "QUEUED",
        2: "PENDING",
        3: "RUNNING",
        4: "SUCCEEDED",
        5: "FAILED",
        6: "CANCELLING",
        7: "CANCELLED",
        8: "PAUSED",
        9: "EXPIRED",
    }

    start_time = time.time()

    if not tuning_job.has_ended:
        print(f"Job is still running. State: {state_names.get(tuning_job.state, tuning_job.state)}")

        if "--wait" in sys.argv:
            print("Waiting for completion (checking every 60s)...")
            while not tuning_job.has_ended:
                elapsed = int(time.time() - start_time)
                tuning_job.refresh()
                state = state_names.get(tuning_job.state, str(tuning_job.state))
                print(f"  [{elapsed}s] State: {state}")
                if not tuning_job.has_ended:
                    time.sleep(60)
        else:
            print("Run with --wait to wait for completion, or check console:")
            print(f"  https://console.cloud.google.com/vertex-ai/generative/language/locations/us-central1/tuning/tuningJob/2214170247995326464?project=63184426072")
            return

    tuning_job.refresh()
    state = state_names.get(tuning_job.state, str(tuning_job.state))
    print(f"\nFinal state: {state}")

    if tuning_job.state != 4:  # Not SUCCEEDED
        print(f"Job did not succeed. State: {state}")
        if hasattr(tuning_job, 'error') and tuning_job.error:
            print(f"Error: {tuning_job.error}")
        return

    # Job succeeded - evaluate tuned model
    endpoint = tuning_job.tuned_model_endpoint_name
    model_name = tuning_job.tuned_model_name
    print(f"\nTuned model endpoint: {endpoint}")
    print(f"Tuned model name: {model_name}")

    print("\n--- Evaluating tuned model ---")
    model = GenerativeModel(endpoint)
    entries = load_manifest()

    results = []
    exact_matches = 0
    normalized_matches = 0
    tested = 0

    for i, entry in enumerate(entries):
        image_path = IMAGES_DIR / entry["filename"]
        if not image_path.exists():
            continue

        print(f"  [{i+1}/{len(entries)}] {entry['filename']}", end=" -> ")

        try:
            img = Image.load_from_file(str(image_path))
            response = model.generate_content([
                "Convert this handwritten math formula to LaTeX:",
                img,
            ])
            predicted = response.text.strip()
            exact, normalized = latex_matches(predicted, entry["latex"])

            if exact:
                exact_matches += 1
            if normalized:
                normalized_matches += 1
            tested += 1

            status = "EXACT" if exact else ("NORM" if normalized else "MISS")
            print(f"{status} | {predicted}")

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

    print(f"\n{'=' * 60}")
    print(f"TUNED MODEL RESULTS")
    print(f"{'=' * 60}")
    print(f"Tested:              {tested}/{len(entries)}")
    print(f"Exact matches:       {exact_matches}/{tested} ({exact_matches/max(tested,1)*100:.1f}%)")
    print(f"Normalized matches:  {normalized_matches}/{tested} ({normalized_matches/max(tested,1)*100:.1f}%)")

    # Save results
    results_file = RESULTS_DIR / "lora_tuned_results.json"
    with open(results_file, "w") as f:
        json.dump({
            "tuning_job": JOB_RESOURCE,
            "tuned_model_endpoint": endpoint,
            "tuned_model_name": model_name,
            "tested": tested,
            "exact_matches": exact_matches,
            "exact_accuracy": round(exact_matches / max(tested, 1) * 100, 2),
            "normalized_matches": normalized_matches,
            "normalized_accuracy": round(normalized_matches / max(tested, 1) * 100, 2),
            "detailed_results": results,
        }, f, indent=2)
    print(f"\nResults saved to {results_file}")


if __name__ == "__main__":
    main()
