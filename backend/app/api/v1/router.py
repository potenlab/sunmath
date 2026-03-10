from fastapi import APIRouter

from app.api.v1.problems import router as problems_router
from app.api.v1.grading import router as grading_router
from app.api.v1.students import router as students_router
from app.api.v1.admin import router as admin_router
from app.api.v1.benchmark import router as benchmark_router
from app.api.v1.llm_benchmark import router as llm_benchmark_router
from app.api.v1.auth import router as auth_router
from app.api.v1.ocr import router as ocr_router
from app.api.v1.lora import student_router as lora_student_router
from app.api.v1.lora import admin_router as lora_admin_router
from app.api.v1.baseline import router as baseline_router

v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(problems_router)
v1_router.include_router(grading_router)
v1_router.include_router(students_router)
v1_router.include_router(admin_router)
v1_router.include_router(benchmark_router)
v1_router.include_router(llm_benchmark_router)
v1_router.include_router(auth_router)
v1_router.include_router(ocr_router)
v1_router.include_router(lora_student_router)
v1_router.include_router(lora_admin_router)
v1_router.include_router(baseline_router)
