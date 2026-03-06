import enum
from datetime import datetime

from sqlalchemy import (
    Boolean, ForeignKey, Integer, String, Text, Float, Index, UniqueConstraint,
    func, Enum,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class JudgedBy(str, enum.Enum):
    sympy = "sympy"
    llm = "llm"
    cache = "cache"


class WrongAnswerStatus(str, enum.Enum):
    active = "active"
    resolved = "resolved"
    archived = "archived"


class StudentAnswer(Base):
    __tablename__ = "student_answers"
    __table_args__ = (
        Index("ix_student_answers_student_id", "student_id"),
        Index("ix_student_answers_question_id", "question_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False)
    submitted_answer: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(nullable=False)
    judged_by: Mapped[JudgedBy] = mapped_column(Enum(JudgedBy), nullable=False)
    reasoning: Mapped[str | None] = mapped_column(Text)
    submitted_at: Mapped[datetime] = mapped_column(server_default=func.now())


class StudentConceptMastery(Base):
    __tablename__ = "student_concept_mastery"

    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), primary_key=True)
    concept_id: Mapped[int] = mapped_column(ForeignKey("concepts.id"), primary_key=True)
    mastery_level: Mapped[float] = mapped_column(Float, default=0.0)
    last_updated: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


class WrongAnswerWarehouse(Base):
    __tablename__ = "wrong_answer_warehouse"
    __table_args__ = (
        Index("ix_wrong_answer_warehouse_student_id", "student_id"),
        Index("ix_wrong_answer_warehouse_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False)
    answer_id: Mapped[int] = mapped_column(ForeignKey("student_answers.id"), nullable=False)
    status: Mapped[WrongAnswerStatus] = mapped_column(
        Enum(WrongAnswerStatus), default=WrongAnswerStatus.active
    )
    retry_count: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


class AnswerCache(Base):
    __tablename__ = "answer_cache"
    __table_args__ = (
        UniqueConstraint("question_id", "submitted_answer_hash", name="uq_answer_cache_lookup"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False)
    submitted_answer_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    is_correct: Mapped[bool] = mapped_column(nullable=False)
    judged_by: Mapped[JudgedBy] = mapped_column(Enum(JudgedBy), nullable=False)
    reasoning: Mapped[str | None] = mapped_column(Text)
    cached_at: Mapped[datetime] = mapped_column(server_default=func.now())


class AdminSettings(Base):
    __tablename__ = "admin_settings"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


class StudentDiagnosis(Base):
    __tablename__ = "student_diagnoses"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    diagnosis_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(server_default=func.now())


class LoraModelStatus(str, enum.Enum):
    pending = "pending"
    training = "training"
    succeeded = "succeeded"
    failed = "failed"


class StudentTrainingSample(Base):
    __tablename__ = "student_training_samples"
    __table_args__ = (
        Index("ix_student_training_samples_student_id", "student_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False)
    image_gcs_uri: Mapped[str] = mapped_column(Text, nullable=False)
    ground_truth_latex: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class StudentLoraModel(Base):
    __tablename__ = "student_lora_models"
    __table_args__ = (
        Index("ix_student_lora_models_student_id", "student_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    tuning_job_id: Mapped[str] = mapped_column(String(500), nullable=False)
    model_endpoint: Mapped[str | None] = mapped_column(String(500), nullable=True)
    model_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[LoraModelStatus] = mapped_column(
        Enum(LoraModelStatus), default=LoraModelStatus.pending
    )
    training_samples_count: Mapped[int] = mapped_column(Integer, nullable=False)
    accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)
