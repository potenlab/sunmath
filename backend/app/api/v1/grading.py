from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.grading import GradeRequest, GradeResponse, CacheStatsResponse

router = APIRouter(prefix="/grading", tags=["grading"])


@router.post("/grade", response_model=GradeResponse)
async def grade_answer(body: GradeRequest, db: AsyncSession = Depends(get_db)):
    """Grade a student's answer. (Stub)"""
    return GradeResponse(
        is_correct=True,
        judged_by="sympy",
        reasoning="Stub: answer accepted. Grading engine not yet implemented.",
        cached=False,
    )


@router.get("/cache/stats", response_model=CacheStatsResponse)
async def get_cache_stats(db: AsyncSession = Depends(get_db)):
    """Get answer cache statistics. (Stub)"""
    return CacheStatsResponse(
        total_entries=0,
        hit_rate=0.0,
        entries_by_judge={"sympy": 0, "llm": 0, "cache": 0},
    )
