from fastapi import APIRouter

from app.api.v1.problems import router as problems_router
from app.api.v1.grading import router as grading_router
from app.api.v1.students import router as students_router
from app.api.v1.admin import router as admin_router
from app.api.v1.benchmark import router as benchmark_router

v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(problems_router)
v1_router.include_router(grading_router)
v1_router.include_router(students_router)
v1_router.include_router(admin_router)
v1_router.include_router(benchmark_router)
