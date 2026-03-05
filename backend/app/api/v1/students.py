from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.student import (
    DiagnosisResponse,
    WrongAnswerListResponse,
    MasteryListResponse,
    LearningPathResponse,
)

router = APIRouter(prefix="/students", tags=["students"])


@router.get("/{student_id}/diagnosis", response_model=DiagnosisResponse)
async def get_diagnosis(student_id: int, db: AsyncSession = Depends(get_db)):
    """Get student diagnosis. (Stub)"""
    return DiagnosisResponse(
        student_id=student_id,
        core_weaknesses=["factoring"],
        prerequisite_chains=[["arithmetic", "algebra", "factoring"]],
        learning_path=["Review arithmetic basics", "Practice algebra", "Learn factoring"],
        recommended_problems=[1, 2, 3],
        generated_at=datetime.now(timezone.utc),
    )


@router.get("/{student_id}/wrong-answers", response_model=WrongAnswerListResponse)
async def get_wrong_answers(student_id: int, db: AsyncSession = Depends(get_db)):
    """Get student's wrong answer warehouse. (Stub)"""
    return WrongAnswerListResponse(
        student_id=student_id,
        wrong_answers=[],
        total=0,
    )


@router.get("/{student_id}/mastery", response_model=MasteryListResponse)
async def get_mastery(student_id: int, db: AsyncSession = Depends(get_db)):
    """Get student's concept mastery levels. (Stub)"""
    return MasteryListResponse(
        student_id=student_id,
        masteries=[],
    )


@router.get("/{student_id}/learning-path", response_model=LearningPathResponse)
async def get_learning_path(student_id: int, db: AsyncSession = Depends(get_db)):
    """Get student's personalized learning path. (Stub)"""
    return LearningPathResponse(
        student_id=student_id,
        path=["Review basics", "Practice intermediate", "Advance"],
        estimated_concepts=10,
    )
