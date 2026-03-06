from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.history import LoraModelStatus


class TrainingSampleCountResponse(BaseModel):
    student_id: int
    count: int


class LoraModelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    tuning_job_id: str
    model_endpoint: str | None
    model_name: str | None
    status: LoraModelStatus
    training_samples_count: int
    accuracy: float | None
    is_active: bool
    created_at: datetime
    completed_at: datetime | None


class LoraTrainResponse(BaseModel):
    student_id: int
    tuning_job_id: str
    status: str
    training_samples_count: int
    message: str


class LoraStatusResponse(BaseModel):
    student_id: int
    model: LoraModelResponse | None
    message: str
