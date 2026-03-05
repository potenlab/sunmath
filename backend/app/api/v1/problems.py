from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.problem import (
    ProblemCreate,
    ProblemResponse,
    SimilarProblemResponse,
)

router = APIRouter(prefix="/problems", tags=["problems"])


@router.post("", response_model=ProblemResponse, status_code=201)
async def create_problem(body: ProblemCreate, db: AsyncSession = Depends(get_db)):
    """Create a new problem. (Stub)"""
    now = datetime.now(timezone.utc)
    return ProblemResponse(
        id=1,
        content=body.content,
        correct_answer=body.correct_answer,
        expected_form=body.expected_form,
        target_grade=body.target_grade,
        grading_hints=body.grading_hints,
        created_at=now,
        updated_at=now,
    )


@router.get("/{problem_id}", response_model=ProblemResponse)
async def get_problem(problem_id: int, db: AsyncSession = Depends(get_db)):
    """Get a problem by ID. (Stub)"""
    now = datetime.now(timezone.utc)
    return ProblemResponse(
        id=problem_id,
        content="Solve: x^2 + 2x + 1 = 0",
        correct_answer="x = -1",
        expected_form="simplified",
        target_grade=9,
        grading_hints=None,
        created_at=now,
        updated_at=now,
    )


@router.get("/{problem_id}/similar", response_model=SimilarProblemResponse)
async def get_similar_problems(problem_id: int, db: AsyncSession = Depends(get_db)):
    """Find similar problems. (Stub)"""
    return SimilarProblemResponse(problems=[], similarity_scores=[])
