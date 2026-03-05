from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.nodes import ExpectedForm


class ProblemCreate(BaseModel):
    content: str
    correct_answer: str
    expected_form: ExpectedForm = ExpectedForm.simplified
    target_grade: int | None = None
    grading_hints: str | None = None
    unit_ids: list[int] = []
    concept_ids: list[int] = []


class ProblemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content: str
    correct_answer: str
    expected_form: ExpectedForm
    target_grade: int | None
    grading_hints: str | None
    created_at: datetime
    updated_at: datetime


class SimilarProblemResponse(BaseModel):
    problems: list[ProblemResponse]
    similarity_scores: list[float]


class DuplicateCheckResponse(BaseModel):
    is_duplicate: bool
    similar_problem_id: int | None = None
    similarity_score: float = 0.0
