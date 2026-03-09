from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.api.deps_auth import require_role
from app.models.user import User, UserRole
from app.schemas.grading import GradeRequest, GradeResponse, CacheStatsResponse
from app.services.grading_engine import GradingEngine

router = APIRouter(prefix="/grading", tags=["grading"])


@router.post("/grade", response_model=GradeResponse)
async def grade_answer(body: GradeRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_role(UserRole.admin, UserRole.student))):
    """Grade a student's answer through the full grading pipeline."""
    # Students can only grade with their own student_id
    if current_user.role == UserRole.student and current_user.student_id != body.student_id:
        raise HTTPException(status_code=403, detail="You can only submit answers for your own student profile")
    engine = GradingEngine(db)
    result = await engine.grade(body.student_id, body.question_id, body.submitted_answer)
    return GradeResponse(
        is_correct=result["is_correct"],
        judged_by=result["judged_by"],
        reasoning=result["reasoning"],
        cached=result["cached"],
        mastery_updates=result.get("mastery_updates", []),
    )


@router.get("/cache/stats", response_model=CacheStatsResponse)
async def get_cache_stats(db: AsyncSession = Depends(get_db), _: User = Depends(require_role(UserRole.admin))):
    """Get answer cache statistics."""
    engine = GradingEngine(db)
    stats = await engine.get_cache_stats()
    return CacheStatsResponse(**stats)
