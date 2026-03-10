"""Schemas for baseline model training and management."""

from datetime import datetime

from pydantic import BaseModel


class BaselineTrainRequest(BaseModel):
    train_uri: str
    val_uri: str | None = None
    dataset_info: dict | None = None


class BaselineModelResponse(BaseModel):
    id: int
    tuning_job_id: str
    model_endpoint: str | None
    model_name: str | None
    status: str
    training_samples_count: int
    dataset_info: dict | None
    is_active: bool
    created_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class BaselineStatusResponse(BaseModel):
    id: int
    tuning_job_id: str
    status: str
    model_endpoint: str | None
    model_name: str | None
    has_ended: bool | None = None
