"""Pydantic schemas for LLM benchmark, voting, and SymPy verification."""

from pydantic import BaseModel, ConfigDict


# --- Core result schemas ---

class ModelResponse(BaseModel):
    answer: str = ""
    answer_latex: str = ""
    confidence: int = 0
    solution: str = ""
    latency_ms: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    cost: float = 0.0
    error: str | None = None


class AnswerCheckResult(BaseModel):
    is_correct: bool
    method: str  # "sympy" | "value_extraction" | "string_match" | "needs_manual_review"


class ProblemResult(BaseModel):
    problem_id: str
    subject: str
    difficulty: str
    model_key: str
    model_id: str
    response: ModelResponse
    check: AnswerCheckResult
    correct_answer: str
    expected_form: str


class BenchmarkRun(BaseModel):
    run_id: str
    timestamp: str
    models: list[str]
    problem_count: int
    results: list[ProblemResult]
    total_cost: float = 0.0
    total_duration_s: float = 0.0


# --- Analysis / report schemas ---

class AccuracyCell(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    accuracy: float
    correct: int
    total: int


class AccuracyMatrix(BaseModel):
    by_subject: dict[str, dict[str, AccuracyCell]]  # model -> subject -> cell
    by_difficulty: dict[str, dict[str, AccuracyCell]]  # model -> difficulty -> cell
    overall: dict[str, AccuracyCell]  # model -> cell


class CostCell(BaseModel):
    avg_cost: float
    total_cost: float
    count: int


class CostMatrix(BaseModel):
    by_model: dict[str, CostCell]
    by_model_subject: dict[str, dict[str, CostCell]]  # model -> subject -> cell


class SubjectRecommendation(BaseModel):
    subject: str
    best_model: str
    accuracy: float
    avg_cost: float
    reasoning_advantage: bool  # True if reasoning model outperforms by >10%


class BenchmarkReport(BaseModel):
    run_id: str
    accuracy: AccuracyMatrix
    costs: CostMatrix
    recommendations: list[SubjectRecommendation]
    summary: str


# --- Cross-verification / voting schemas ---

class VoteStep(BaseModel):
    model_key: str
    answer: str
    answer_latex: str
    confidence: int
    cost: float
    latency_ms: float
    error: str | None = None


class VotingResult(BaseModel):
    problem_id: str
    subject: str
    difficulty: str
    final_answer: str
    is_correct: bool
    check_method: str
    steps: list[VoteStep]
    total_cost: float
    accepted_at_step: int  # 1 = primary only, 2 = secondary confirmed, 3 = majority, 0 = manual
    needs_manual_review: bool = False


class ThresholdResult(BaseModel):
    threshold: int
    accuracy: float
    avg_cost: float
    total_cost: float
    avg_steps: float
    manual_review_count: int
    results: list[VotingResult]


class StrategyComparison(BaseModel):
    single_model_baseline: dict[str, AccuracyCell]  # model -> cell
    thresholds: list[ThresholdResult]
    best_threshold: int
    best_accuracy: float
    best_cost: float


class VotingBenchmarkResult(BaseModel):
    run_id: str
    timestamp: str
    comparison: StrategyComparison


# --- SymPy verification schemas ---

class SympyVerificationResult(BaseModel):
    problem_id: str
    model_key: str
    original_correct: bool
    sympy_agrees: bool | None  # None if parse failed
    sympy_parse_success: bool
    answer_latex: str
    correct_answer_latex: str
    error: str | None = None


class SympyVerificationReport(BaseModel):
    run_id: str
    total_checked: int
    sympy_parse_success_rate: float
    accuracy_with_sympy: float
    accuracy_without_sympy: float
    by_subject: dict[str, dict[str, float]]  # subject -> {parse_rate, accuracy}
    by_expected_form: dict[str, dict[str, float]]  # form -> {parse_rate, accuracy}
    results: list[SympyVerificationResult]


# --- API request/response schemas ---

class BenchmarkRunRequest(BaseModel):
    models: list[str] | None = None  # None = all models
    problems: list[str] | None = None  # None = all problems


class VotingRunRequest(BaseModel):
    problems: list[str] | None = None
    thresholds: list[int] = [50, 60, 70, 80, 90]


class RunStatusResponse(BaseModel):
    run_id: str
    status: str  # "running" | "completed" | "failed"
    progress: int = 0
    total: int = 0
    message: str = ""


class RunListItem(BaseModel):
    run_id: str
    timestamp: str
    models: list[str]
    problem_count: int
    total_cost: float


class RunListResponse(BaseModel):
    runs: list[RunListItem]
