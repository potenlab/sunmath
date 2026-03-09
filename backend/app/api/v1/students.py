from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.api.deps_auth import require_role
from app.models.user import User, UserRole
from app.models.history import (
    StudentAnswer,
    StudentConceptMastery,
    WrongAnswerWarehouse,
)
from app.models.nodes import Concept, Question, Student
from app.schemas.student import (
    ConceptMasteryResponse,
    DiagnosisResponse,
    LearningPathResponse,
    MasteryListResponse,
    StudentCreate,
    StudentListResponse,
    StudentResponse,
    StudentUpdate,
    WrongAnswerListResponse,
    WrongAnswerResponse,
)
from app.services.diagnosis import DiagnosisService

router = APIRouter(prefix="/students", tags=["students"])


async def _verify_student(student_id: int, db: AsyncSession) -> None:
    """Verify student exists, raise 404 if not."""
    result = await db.execute(
        select(Student.id).where(Student.id == student_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Student not found")


@router.get("", response_model=StudentListResponse)
async def list_students(db: AsyncSession = Depends(get_db), _: User = Depends(require_role(UserRole.admin))):
    """List all students."""
    total_result = await db.execute(select(sa_func.count()).select_from(Student))
    total = total_result.scalar() or 0
    result = await db.execute(select(Student).order_by(Student.created_at.desc()))
    students = result.scalars().all()
    return StudentListResponse(
        students=[StudentResponse.model_validate(s) for s in students],
        total=total,
    )


@router.post("", response_model=StudentResponse, status_code=201)
async def create_student(body: StudentCreate, db: AsyncSession = Depends(get_db), _: User = Depends(require_role(UserRole.admin))):
    """Create a new student."""
    student = Student(name=body.name, grade_level=body.grade_level)
    db.add(student)
    await db.flush()
    await db.refresh(student)
    return StudentResponse.model_validate(student)


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(student_id: int, body: StudentUpdate, db: AsyncSession = Depends(get_db), _: User = Depends(require_role(UserRole.admin))):
    """Update a student."""
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(student, key, value)
    db.add(student)
    await db.flush()
    await db.refresh(student)
    return StudentResponse.model_validate(student)


@router.delete("/{student_id}", status_code=204)
async def delete_student(student_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(require_role(UserRole.admin))):
    """Delete a student."""
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    await db.delete(student)
    await db.flush()


@router.get("/{student_id}/diagnosis", response_model=DiagnosisResponse)
async def get_diagnosis(student_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_role(UserRole.admin, UserRole.student))):
    """Get student diagnosis with root cause analysis."""
    if current_user.role == UserRole.student and current_user.student_id != student_id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    await _verify_student(student_id, db)
    svc = DiagnosisService(db)
    diagnosis = await svc.generate_diagnosis(student_id)
    return DiagnosisResponse(
        student_id=diagnosis["student_id"],
        core_weaknesses=diagnosis["core_weaknesses"],
        prerequisite_chains=diagnosis["prerequisite_chains"],
        learning_path=diagnosis["learning_path"],
        recommended_problems=diagnosis["recommended_problems"],
        concept_frequencies=diagnosis.get("concept_frequencies", []),
        recommended_problems_detail=diagnosis.get("recommended_problems_detail", []),
        generated_at=diagnosis["generated_at"],
    )


@router.get("/{student_id}/wrong-answers", response_model=WrongAnswerListResponse)
async def get_wrong_answers(student_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_role(UserRole.admin, UserRole.student))):
    """Get student's wrong answer warehouse."""
    if current_user.role == UserRole.student and current_user.student_id != student_id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    await _verify_student(student_id, db)

    result = await db.execute(
        select(
            WrongAnswerWarehouse,
            StudentAnswer.submitted_answer,
            Question.content,
        )
        .join(StudentAnswer, StudentAnswer.id == WrongAnswerWarehouse.answer_id)
        .join(Question, Question.id == WrongAnswerWarehouse.question_id)
        .where(WrongAnswerWarehouse.student_id == student_id)
        .order_by(WrongAnswerWarehouse.created_at.desc())
    )
    rows = result.all()

    wrong_answers = [
        WrongAnswerResponse(
            id=wa.id,
            question_id=wa.question_id,
            question_content=q_content,
            submitted_answer=submitted,
            status=wa.status,
            retry_count=wa.retry_count,
            created_at=wa.created_at,
        )
        for wa, submitted, q_content in rows
    ]

    return WrongAnswerListResponse(
        student_id=student_id,
        wrong_answers=wrong_answers,
        total=len(wrong_answers),
    )


@router.get("/{student_id}/mastery", response_model=MasteryListResponse)
async def get_mastery(student_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_role(UserRole.admin, UserRole.student))):
    """Get student's concept mastery levels sorted by mastery ascending."""
    if current_user.role == UserRole.student and current_user.student_id != student_id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    await _verify_student(student_id, db)

    result = await db.execute(
        select(
            StudentConceptMastery.concept_id,
            Concept.name,
            StudentConceptMastery.mastery_level,
            StudentConceptMastery.last_updated,
        )
        .join(Concept, Concept.id == StudentConceptMastery.concept_id)
        .where(StudentConceptMastery.student_id == student_id)
        .order_by(StudentConceptMastery.mastery_level.asc())
    )
    rows = result.all()

    masteries = [
        ConceptMasteryResponse(
            concept_id=row.concept_id,
            concept_name=row.name,
            mastery_level=row.mastery_level,
            last_updated=row.last_updated,
        )
        for row in rows
    ]

    return MasteryListResponse(student_id=student_id, masteries=masteries)


@router.get("/{student_id}/learning-path", response_model=LearningPathResponse)
async def get_learning_path(student_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_role(UserRole.admin, UserRole.student))):
    """Get student's personalized learning path."""
    if current_user.role == UserRole.student and current_user.student_id != student_id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    await _verify_student(student_id, db)
    svc = DiagnosisService(db)
    path_data = await svc.generate_learning_path(student_id)
    return LearningPathResponse(
        student_id=path_data["student_id"],
        path=path_data["path"],
        estimated_concepts=path_data["estimated_concepts"],
    )
