"""Baseline model training service for CROHME + HME100K datasets."""

import logging
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from vertexai.tuning import sft

from app.models.history import BaselineModel, LoraModelStatus
from app.services.lora_training import _ensure_vertex_init, SOURCE_MODEL

logger = logging.getLogger(__name__)


async def start_baseline_training(
    db: AsyncSession,
    train_uri: str,
    val_uri: str | None = None,
    dataset_info: dict | None = None,
    training_samples_count: int = 0,
) -> BaselineModel:
    """Submit a baseline SFT job to Vertex AI and create a DB record."""
    _ensure_vertex_init()

    kwargs = {
        "source_model": SOURCE_MODEL,
        "train_dataset": train_uri,
    }
    if val_uri:
        kwargs["validation_dataset"] = val_uri

    tuning_job = sft.train(**kwargs)
    logger.info("Started baseline tuning job: %s", tuning_job.resource_name)

    record = BaselineModel(
        tuning_job_id=tuning_job.resource_name,
        status=LoraModelStatus.training,
        training_samples_count=training_samples_count,
        dataset_info=dataset_info or {},
    )
    db.add(record)
    await db.flush()

    return record


async def check_baseline_job(
    db: AsyncSession, model_id: int
) -> dict:
    """Poll Vertex AI for the status of a baseline tuning job."""
    _ensure_vertex_init()

    result = await db.execute(
        select(BaselineModel).where(BaselineModel.id == model_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise ValueError(f"Baseline model {model_id} not found")

    job = sft.SupervisedTuningJob(record.tuning_job_id)
    job.refresh()

    status_info = {
        "id": record.id,
        "tuning_job_id": record.tuning_job_id,
        "status": str(job.state),
        "model_endpoint": getattr(job, "tuned_model_endpoint_name", None),
        "model_name": getattr(job, "tuned_model_name", None),
        "has_ended": job.has_ended,
    }

    # Update DB record if job has completed
    if job.has_ended:
        endpoint = getattr(job, "tuned_model_endpoint_name", None)
        model_name = getattr(job, "tuned_model_name", None)

        if endpoint:
            record.status = LoraModelStatus.succeeded
            record.model_endpoint = endpoint
            record.model_name = model_name
            record.completed_at = datetime.now(timezone.utc)
        else:
            record.status = LoraModelStatus.failed
            record.completed_at = datetime.now(timezone.utc)

        await db.flush()

    return status_info


async def get_active_baseline_model(
    db: AsyncSession,
) -> BaselineModel | None:
    """Get the currently active baseline model."""
    result = await db.execute(
        select(BaselineModel).where(
            BaselineModel.is_active == True,  # noqa: E712
            BaselineModel.status == LoraModelStatus.succeeded,
        )
    )
    return result.scalar_one_or_none()


async def activate_baseline_model(
    db: AsyncSession, model_id: int
) -> None:
    """Set one baseline model as active and deactivate all others."""
    # Deactivate all
    await db.execute(
        update(BaselineModel).values(is_active=False)
    )
    # Activate specified
    await db.execute(
        update(BaselineModel)
        .where(BaselineModel.id == model_id)
        .values(is_active=True)
    )
    await db.flush()


async def get_all_baseline_models(
    db: AsyncSession,
) -> list[BaselineModel]:
    """List all baseline models, newest first."""
    result = await db.execute(
        select(BaselineModel).order_by(BaselineModel.created_at.desc())
    )
    return list(result.scalars().all())
