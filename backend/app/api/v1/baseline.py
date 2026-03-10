"""Admin endpoints for baseline model training and management."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.baseline import (
    BaselineModelResponse,
    BaselineStatusResponse,
    BaselineTrainRequest,
)
from app.services.baseline_training import (
    activate_baseline_model,
    check_baseline_job,
    get_active_baseline_model,
    get_all_baseline_models,
    start_baseline_training,
)

router = APIRouter(prefix="/admin/baseline", tags=["baseline"])


@router.post("/train", response_model=BaselineModelResponse)
async def train_baseline(
    request: BaselineTrainRequest,
    db: AsyncSession = Depends(get_db),
):
    """Trigger baseline model training with GCS URIs."""
    record = await start_baseline_training(
        db=db,
        train_uri=request.train_uri,
        val_uri=request.val_uri,
        dataset_info=request.dataset_info,
    )
    await db.commit()
    return record


@router.get("/status", response_model=BaselineStatusResponse)
async def get_status(
    db: AsyncSession = Depends(get_db),
):
    """Check the status of the latest baseline training job."""
    models = await get_all_baseline_models(db)
    if not models:
        raise HTTPException(status_code=404, detail="No baseline models found")

    latest = models[0]
    status = await check_baseline_job(db, latest.id)
    await db.commit()
    return status


@router.get("/models", response_model=list[BaselineModelResponse])
async def list_models(
    db: AsyncSession = Depends(get_db),
):
    """List all baseline models."""
    return await get_all_baseline_models(db)


@router.post("/activate/{model_id}")
async def activate_model(
    model_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Activate a specific baseline model."""
    models = await get_all_baseline_models(db)
    if not any(m.id == model_id for m in models):
        raise HTTPException(status_code=404, detail="Baseline model not found")

    await activate_baseline_model(db, model_id)
    await db.commit()
    return {"message": f"Baseline model {model_id} activated"}


@router.get("/active", response_model=BaselineModelResponse | None)
async def get_active(
    db: AsyncSession = Depends(get_db),
):
    """Get the currently active baseline model."""
    model = await get_active_baseline_model(db)
    return model
