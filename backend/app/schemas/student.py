from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.history import WrongAnswerStatus


class StudentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    grade_level: int | None
    created_at: datetime


class ConceptMasteryResponse(BaseModel):
    concept_id: int
    concept_name: str
    mastery_level: float
    last_updated: datetime


class MasteryListResponse(BaseModel):
    student_id: int
    masteries: list[ConceptMasteryResponse]


class WrongAnswerResponse(BaseModel):
    id: int
    question_id: int
    question_content: str
    submitted_answer: str
    status: WrongAnswerStatus
    retry_count: int
    created_at: datetime


class WrongAnswerListResponse(BaseModel):
    student_id: int
    wrong_answers: list[WrongAnswerResponse]
    total: int


class ConceptFrequency(BaseModel):
    concept_name: str
    count: float
    mastery: float


class RecommendedProblem(BaseModel):
    question_id: int
    concept_name: str


class DiagnosisResponse(BaseModel):
    student_id: int
    core_weaknesses: list[str]
    prerequisite_chains: list[list[str]]
    learning_path: list[str]
    recommended_problems: list[int]
    concept_frequencies: list[ConceptFrequency] = []
    recommended_problems_detail: list[RecommendedProblem] = []
    generated_at: datetime


class LearningPathResponse(BaseModel):
    student_id: int
    path: list[str]
    estimated_concepts: int


class StudentCreate(BaseModel):
    name: str
    grade_level: int | None = None


class StudentUpdate(BaseModel):
    name: str | None = None
    grade_level: int | None = None


class StudentListResponse(BaseModel):
    students: list[StudentResponse]
    total: int


class StudentSummaryResponse(BaseModel):
    id: int
    name: str
    grade_level: int | None
    wrong_answers: int
    root_cause: str | None
    mastery: float
    status: str


class StudentSummaryListResponse(BaseModel):
    students: list[StudentSummaryResponse]
    total: int
    needs_attention: int
    total_wrong_answers: int
