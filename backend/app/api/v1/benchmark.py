from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.benchmark import BenchmarkMatrixResponse, BenchmarkRecommendationResponse

router = APIRouter(prefix="/benchmark", tags=["benchmark"])


@router.get("/matrix", response_model=BenchmarkMatrixResponse)
async def get_benchmark_matrix(db: AsyncSession = Depends(get_db)):
    """Get student-concept mastery matrix. (Stub)"""
    return BenchmarkMatrixResponse(rows=[], concept_names=[])


@router.get("/recommendations", response_model=BenchmarkRecommendationResponse)
async def get_recommendations(db: AsyncSession = Depends(get_db)):
    """Get teaching recommendations based on benchmark data. (Stub)"""
    return BenchmarkRecommendationResponse(recommendations=[])
