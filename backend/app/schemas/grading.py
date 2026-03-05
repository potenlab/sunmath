from pydantic import BaseModel, ConfigDict

from app.models.history import JudgedBy


class GradeRequest(BaseModel):
    student_id: int
    question_id: int
    submitted_answer: str


class GradeResponse(BaseModel):
    is_correct: bool
    judged_by: JudgedBy
    reasoning: str
    cached: bool = False


class CacheStatsResponse(BaseModel):
    total_entries: int
    hit_rate: float
    entries_by_judge: dict[str, int]
