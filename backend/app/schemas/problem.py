from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.nodes import ExpectedForm


class ProblemCreate(BaseModel):
    content: str
    correct_answer: str
    expected_form: ExpectedForm | None = None
    target_grade: int | None = None
    grading_hints: str | None = None
    unit_ids: list[int] = []
    concept_ids: list[int] = []
    concept_weights: dict[int, float] | None = None
    auto_extract_concepts: bool = False


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


class SimilarProblemDetail(BaseModel):
    question_id: int
    similarity_score: float
    shared_concepts: list[int] = []
    only_in_new: list[int] = []
    only_in_existing: list[int] = []


class DuplicateCheckResponse(BaseModel):
    is_duplicate: bool
    mode: str = "warn"
    threshold: float = 0.85
    similar_problem_id: int | None = None
    similarity_score: float = 0.0


class ConceptExtractionResult(BaseModel):
    evaluation_concept_names: list[str] = []
    required_concept_names: list[str] = []
    matched_evaluation_concept_ids: list[int] = []
    matched_required_concept_ids: list[int] = []
    evaluation_concept_weights: dict[int, float] = {}
    required_concept_weights: dict[int, float] = {}
    inferred_expected_form: ExpectedForm | None = None
    inferred_grading_hints: str | None = None


class ProblemRegistrationResponse(BaseModel):
    problem: ProblemResponse | None = None
    registered: bool
    duplicate_check: DuplicateCheckResponse
    similar_problems: list[SimilarProblemDetail] = []
    concept_extraction: ConceptExtractionResult | None = None


class ProblemUpdate(BaseModel):
    content: str | None = None
    correct_answer: str | None = None
    expected_form: ExpectedForm | None = None
    target_grade: int | None = None
    grading_hints: str | None = None


class ProblemListResponse(BaseModel):
    problems: list[ProblemResponse]
    total: int
    page: int = 1
    page_size: int = 20


class SimilarProblemResponse(BaseModel):
    problems: list[ProblemResponse]
    similarity_scores: list[float]
    details: list[SimilarProblemDetail] = []


class ConceptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str | None = None
