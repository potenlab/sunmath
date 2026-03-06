"""Per-student LoRA fine-tuning service for handwriting OCR."""

import json
import logging
import random
import uuid
from datetime import datetime, timezone

import vertexai
from google.cloud import storage
from google.oauth2 import service_account
from vertexai.tuning import sft

from sqlalchemy import select, func as sa_func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.history import (
    LoraModelStatus,
    StudentLoraModel,
    StudentTrainingSample,
)

logger = logging.getLogger(__name__)

SOURCE_MODEL = "gemini-2.0-flash-001"

SYSTEM_INSTRUCTION = (
    "You are a math OCR system. Given a handwritten math formula image, "
    "output ONLY the LaTeX representation. Do not wrap in $ signs or delimiters. "
    "Use standard LaTeX commands."
)

USER_PROMPT = "Convert this handwritten math formula to LaTeX:"

_vertex_initialized = False


def _ensure_vertex_init():
    global _vertex_initialized
    if not _vertex_initialized:
        credentials = None
        if settings.google_application_credentials:
            credentials = service_account.Credentials.from_service_account_file(
                settings.google_application_credentials,
            )
        vertexai.init(
            project=settings.gcp_project_id,
            location=settings.gcp_location,
            credentials=credentials,
        )
        _vertex_initialized = True


def _get_gcs_client() -> storage.Client:
    if settings.google_application_credentials:
        credentials = service_account.Credentials.from_service_account_file(
            settings.google_application_credentials,
        )
        return storage.Client(
            project=settings.gcp_project_id, credentials=credentials
        )
    return storage.Client(project=settings.gcp_project_id)


# ---------------------------------------------------------------------------
# GCS operations
# ---------------------------------------------------------------------------

CONTENT_TYPE_TO_EXT = {
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}


def upload_training_image(
    student_id: int, image_bytes: bytes, content_type: str
) -> str:
    """Upload a training image to GCS and return the gs:// URI."""
    ext = CONTENT_TYPE_TO_EXT.get(content_type, "jpg")
    blob_name = f"students/{student_id}/images/{uuid.uuid4()}.{ext}"

    client = _get_gcs_client()
    bucket = client.bucket(settings.gcs_bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_string(image_bytes, content_type=content_type)

    uri = f"gs://{settings.gcs_bucket_name}/{blob_name}"
    logger.info("Uploaded training image: %s", uri)
    return uri


def build_and_upload_training_jsonl(
    student_id: int,
    samples: list[StudentTrainingSample],
) -> tuple[str, str | None]:
    """Build Vertex AI SFT-format JSONL, 80/20 train/val split, upload to GCS.

    Returns (train_uri, val_uri | None).
    """
    shuffled = list(samples)
    random.seed(42)
    random.shuffle(shuffled)

    split_idx = int(len(shuffled) * 0.8)
    train_samples = shuffled[:split_idx]
    val_samples = shuffled[split_idx:]

    def _to_jsonl(sample_list: list[StudentTrainingSample]) -> str:
        lines = []
        for s in sample_list:
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
                                    "mimeType": s.content_type,
                                    "fileUri": s.image_gcs_uri,
                                }
                            },
                            {"text": USER_PROMPT},
                        ],
                    },
                    {
                        "role": "model",
                        "parts": [{"text": s.ground_truth_latex}],
                    },
                ],
            }
            lines.append(json.dumps(example))
        return "\n".join(lines) + "\n"

    client = _get_gcs_client()
    bucket = client.bucket(settings.gcs_bucket_name)

    # Upload train JSONL
    train_blob_name = f"students/{student_id}/training-data/sft_train.jsonl"
    train_blob = bucket.blob(train_blob_name)
    train_blob.upload_from_string(
        _to_jsonl(train_samples), content_type="application/jsonl"
    )
    train_uri = f"gs://{settings.gcs_bucket_name}/{train_blob_name}"

    # Upload val JSONL (only if enough samples)
    val_uri = None
    if len(val_samples) >= 1:
        val_blob_name = f"students/{student_id}/training-data/sft_val.jsonl"
        val_blob = bucket.blob(val_blob_name)
        val_blob.upload_from_string(
            _to_jsonl(val_samples), content_type="application/jsonl"
        )
        val_uri = f"gs://{settings.gcs_bucket_name}/{val_blob_name}"

    logger.info(
        "Uploaded JSONL for student %d: train=%d, val=%d",
        student_id,
        len(train_samples),
        len(val_samples),
    )
    return train_uri, val_uri


# ---------------------------------------------------------------------------
# Vertex AI tuning
# ---------------------------------------------------------------------------


def start_tuning_job(
    train_uri: str, val_uri: str | None = None
) -> sft.SupervisedTuningJob:
    """Submit a supervised fine-tuning job to Vertex AI."""
    _ensure_vertex_init()

    kwargs = {
        "source_model": SOURCE_MODEL,
        "train_dataset": train_uri,
    }
    if val_uri:
        kwargs["validation_dataset"] = val_uri

    tuning_job = sft.train(**kwargs)
    logger.info("Started tuning job: %s", tuning_job.resource_name)
    return tuning_job


def check_tuning_job(job_resource_name: str) -> dict:
    """Refresh a tuning job and return its current status."""
    _ensure_vertex_init()

    job = sft.SupervisedTuningJob(job_resource_name)
    job.refresh()

    return {
        "status": str(job.state),
        "model_endpoint": getattr(job, "tuned_model_endpoint_name", None),
        "model_name": getattr(job, "tuned_model_name", None),
        "has_ended": job.has_ended,
    }


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------


async def save_training_sample(
    db: AsyncSession,
    student_id: int,
    question_id: int,
    image_gcs_uri: str,
    ground_truth_latex: str,
    content_type: str,
) -> StudentTrainingSample:
    """Save a training sample record to the database."""
    sample = StudentTrainingSample(
        student_id=student_id,
        question_id=question_id,
        image_gcs_uri=image_gcs_uri,
        ground_truth_latex=ground_truth_latex,
        content_type=content_type,
    )
    db.add(sample)
    await db.flush()
    return sample


async def get_training_samples(
    db: AsyncSession, student_id: int
) -> list[StudentTrainingSample]:
    """Get all training samples for a student."""
    result = await db.execute(
        select(StudentTrainingSample)
        .where(StudentTrainingSample.student_id == student_id)
        .order_by(StudentTrainingSample.created_at)
    )
    return list(result.scalars().all())


async def get_sample_count(db: AsyncSession, student_id: int) -> int:
    """Get the count of training samples for a student."""
    result = await db.execute(
        select(sa_func.count())
        .select_from(StudentTrainingSample)
        .where(StudentTrainingSample.student_id == student_id)
    )
    return result.scalar_one()


async def create_lora_record(
    db: AsyncSession,
    student_id: int,
    tuning_job_id: str,
    samples_count: int,
) -> StudentLoraModel:
    """Create a LoRA model record for a new tuning job."""
    record = StudentLoraModel(
        student_id=student_id,
        tuning_job_id=tuning_job_id,
        status=LoraModelStatus.training,
        training_samples_count=samples_count,
    )
    db.add(record)
    await db.flush()
    return record


async def get_active_lora_model(
    db: AsyncSession, student_id: int
) -> StudentLoraModel | None:
    """Get the active LoRA model for a student (succeeded + is_active)."""
    result = await db.execute(
        select(StudentLoraModel).where(
            StudentLoraModel.student_id == student_id,
            StudentLoraModel.is_active == True,  # noqa: E712
            StudentLoraModel.status == LoraModelStatus.succeeded,
        )
    )
    return result.scalar_one_or_none()


async def get_latest_lora_model(
    db: AsyncSession, student_id: int
) -> StudentLoraModel | None:
    """Get the most recent LoRA model for a student."""
    result = await db.execute(
        select(StudentLoraModel)
        .where(StudentLoraModel.student_id == student_id)
        .order_by(StudentLoraModel.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_all_lora_models(
    db: AsyncSession, student_id: int
) -> list[StudentLoraModel]:
    """Get all LoRA models for a student."""
    result = await db.execute(
        select(StudentLoraModel)
        .where(StudentLoraModel.student_id == student_id)
        .order_by(StudentLoraModel.created_at.desc())
    )
    return list(result.scalars().all())


async def activate_lora_model(
    db: AsyncSession, student_id: int, model_id: int
) -> None:
    """Activate a specific model and deactivate all others for the student."""
    # Deactivate all models for this student
    await db.execute(
        update(StudentLoraModel)
        .where(StudentLoraModel.student_id == student_id)
        .values(is_active=False)
    )
    # Activate the specified model
    await db.execute(
        update(StudentLoraModel)
        .where(
            StudentLoraModel.id == model_id,
            StudentLoraModel.student_id == student_id,
        )
        .values(is_active=True)
    )
    await db.flush()
