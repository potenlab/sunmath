"""LoRA fine-tuning API endpoints for per-student OCR personalization."""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.api.deps_auth import require_role
from app.models.history import LoraModelStatus, StudentLoraModel
from app.models.nodes import Question
from app.models.history import StudentAnswer
from app.models.user import User, UserRole
from app.schemas.lora import (
    LoraModelResponse,
    LoraStatusResponse,
    LoraTrainResponse,
    TrainingSampleCountResponse,
)
from app.services import lora_training

logger = logging.getLogger(__name__)

# Student-facing router (mounted under /ocr)
student_router = APIRouter(prefix="/ocr", tags=["ocr"])

# Admin router (mounted under /admin/lora)
admin_router = APIRouter(prefix="/admin/lora", tags=["admin-lora"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


# ---------------------------------------------------------------------------
# Student endpoint: save training sample
# ---------------------------------------------------------------------------


@student_router.post("/training-samples")
async def save_training_sample(
    file: UploadFile = File(...),
    question_id: int = Form(...),
    current_user: User = Depends(require_role(UserRole.admin, UserRole.student)),
    db: AsyncSession = Depends(get_db),
):
    """Save a correctly-answered OCR image as a training sample."""
    student_id = current_user.student_id
    if not student_id:
        raise HTTPException(status_code=400, detail="User has no associated student")

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    image_bytes = await file.read()
    if len(image_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")

    # Verify the student answered this question correctly
    result = await db.execute(
        select(StudentAnswer)
        .where(
            StudentAnswer.student_id == student_id,
            StudentAnswer.question_id == question_id,
            StudentAnswer.is_correct == True,  # noqa: E712
        )
        .limit(1)
    )
    correct_answer_record = result.scalar_one_or_none()
    if not correct_answer_record:
        raise HTTPException(
            status_code=400,
            detail="No correct answer found for this student/question pair",
        )

    # Get the ground truth from the question
    q_result = await db.execute(
        select(Question).where(Question.id == question_id)
    )
    question = q_result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Upload image to GCS
    image_gcs_uri = lora_training.upload_training_image(
        student_id, image_bytes, file.content_type
    )

    # Save DB record
    sample = await lora_training.save_training_sample(
        db=db,
        student_id=student_id,
        question_id=question_id,
        image_gcs_uri=image_gcs_uri,
        ground_truth_latex=question.correct_answer,
        content_type=file.content_type,
    )

    return {"id": sample.id, "student_id": student_id, "image_gcs_uri": image_gcs_uri}


# ---------------------------------------------------------------------------
# Admin endpoints
# ---------------------------------------------------------------------------


async def _run_tuning_in_background(
    student_id: int,
    train_uri: str,
    val_uri: str | None,
    lora_record_id: int,
    db_url: str,
):
    """Background task to run the tuning job and update DB on completion."""
    from app.api.deps import AsyncSessionLocal

    try:
        tuning_job = lora_training.start_tuning_job(train_uri, val_uri)

        # Update the record with the real job resource name
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(StudentLoraModel).where(StudentLoraModel.id == lora_record_id)
            )
            record = result.scalar_one()
            record.tuning_job_id = tuning_job.resource_name
            await db.commit()

        logger.info(
            "Tuning job started for student %d: %s",
            student_id,
            tuning_job.resource_name,
        )
    except Exception as e:
        logger.error("Failed to start tuning for student %d: %s", student_id, e)
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(StudentLoraModel).where(StudentLoraModel.id == lora_record_id)
            )
            record = result.scalar_one()
            record.status = LoraModelStatus.failed
            await db.commit()


@admin_router.post("/train/{student_id}", response_model=LoraTrainResponse)
async def train_lora_model(
    student_id: int,
    background_tasks: BackgroundTasks,
    _: User = Depends(require_role(UserRole.admin)),
    db: AsyncSession = Depends(get_db),
):
    """Trigger LoRA fine-tuning for a student. Requires at least 10 samples."""
    sample_count = await lora_training.get_sample_count(db, student_id)
    if sample_count < 10:
        raise HTTPException(
            status_code=400,
            detail=f"Minimum 10 training samples required, student has {sample_count}",
        )

    # Check if there's already a training job in progress
    latest = await lora_training.get_latest_lora_model(db, student_id)
    if latest and latest.status in (LoraModelStatus.pending, LoraModelStatus.training):
        raise HTTPException(
            status_code=409,
            detail="A training job is already in progress for this student",
        )

    # Get samples and build JSONL
    samples = await lora_training.get_training_samples(db, student_id)
    train_uri, val_uri = lora_training.build_and_upload_training_jsonl(
        student_id, samples
    )

    # Create a DB record with a placeholder job ID
    record = await lora_training.create_lora_record(
        db=db,
        student_id=student_id,
        tuning_job_id="pending",
        samples_count=sample_count,
    )
    await db.flush()
    record_id = record.id

    # Run the actual training in background
    background_tasks.add_task(
        _run_tuning_in_background,
        student_id,
        train_uri,
        val_uri,
        record_id,
        str(settings.database_url),
    )

    return LoraTrainResponse(
        student_id=student_id,
        tuning_job_id="pending",
        status="training",
        training_samples_count=sample_count,
        message=f"Training job queued with {sample_count} samples",
    )


@admin_router.get("/status/{student_id}", response_model=LoraStatusResponse)
async def get_lora_status(
    student_id: int,
    _: User = Depends(require_role(UserRole.admin)),
    db: AsyncSession = Depends(get_db),
):
    """Check the latest LoRA training job status for a student."""
    latest = await lora_training.get_latest_lora_model(db, student_id)
    if not latest:
        return LoraStatusResponse(
            student_id=student_id,
            model=None,
            message="No LoRA model found for this student",
        )

    # If still training, refresh from Vertex AI
    if latest.status in (LoraModelStatus.pending, LoraModelStatus.training):
        if latest.tuning_job_id and latest.tuning_job_id != "pending":
            try:
                job_info = lora_training.check_tuning_job(latest.tuning_job_id)
                if job_info["has_ended"]:
                    if job_info["model_endpoint"]:
                        latest.status = LoraModelStatus.succeeded
                        latest.model_endpoint = job_info["model_endpoint"]
                        latest.model_name = job_info["model_name"]
                        latest.completed_at = datetime.now(timezone.utc)
                        # Auto-activate on success
                        await lora_training.activate_lora_model(
                            db, student_id, latest.id
                        )
                    else:
                        latest.status = LoraModelStatus.failed
                        latest.completed_at = datetime.now(timezone.utc)
                    await db.flush()
            except Exception as e:
                logger.warning(
                    "Failed to check tuning job %s: %s", latest.tuning_job_id, e
                )

    return LoraStatusResponse(
        student_id=student_id,
        model=LoraModelResponse.model_validate(latest),
        message=f"Model status: {latest.status.value}",
    )


@admin_router.get("/samples/{student_id}", response_model=TrainingSampleCountResponse)
async def get_sample_count(
    student_id: int,
    _: User = Depends(require_role(UserRole.admin)),
    db: AsyncSession = Depends(get_db),
):
    """Get the count of training samples for a student."""
    count = await lora_training.get_sample_count(db, student_id)
    return TrainingSampleCountResponse(student_id=student_id, count=count)


@admin_router.get("/models/{student_id}", response_model=list[LoraModelResponse])
async def list_lora_models(
    student_id: int,
    _: User = Depends(require_role(UserRole.admin)),
    db: AsyncSession = Depends(get_db),
):
    """List all LoRA models for a student."""
    models = await lora_training.get_all_lora_models(db, student_id)
    return [LoraModelResponse.model_validate(m) for m in models]


@admin_router.post("/activate/{model_id}")
async def activate_lora_model(
    model_id: int,
    _: User = Depends(require_role(UserRole.admin)),
    db: AsyncSession = Depends(get_db),
):
    """Manually activate a specific LoRA model."""
    result = await db.execute(
        select(StudentLoraModel).where(StudentLoraModel.id == model_id)
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    if model.status != LoraModelStatus.succeeded:
        raise HTTPException(status_code=400, detail="Only succeeded models can be activated")

    await lora_training.activate_lora_model(db, model.student_id, model_id)
    return {"message": f"Model {model_id} activated for student {model.student_id}"}
