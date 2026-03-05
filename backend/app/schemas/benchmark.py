from pydantic import BaseModel


class ConceptMasteryCell(BaseModel):
    concept_id: int
    concept_name: str
    mastery_level: float


class StudentBenchmarkRow(BaseModel):
    student_id: int
    student_name: str
    concepts: list[ConceptMasteryCell]


class BenchmarkMatrixResponse(BaseModel):
    rows: list[StudentBenchmarkRow]
    concept_names: list[str]


class RecommendedAction(BaseModel):
    student_id: int
    student_name: str
    weak_concepts: list[str]
    suggested_problems: list[int]


class BenchmarkRecommendationResponse(BaseModel):
    recommendations: list[RecommendedAction]
