import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.api.deps_auth import require_role
from app.models.edges import QuestionEvaluates, QuestionRequires, QuestionUnits
from app.models.user import User, UserRole
from app.models.nodes import Concept, ExpectedForm, Question
from sqlalchemy import func as sa_func
from app.schemas.problem import (
    ConceptExtractionResult,
    ConceptResponse,
    ConceptWeightDetail,
    DuplicateCheckResponse,
    ProblemCreate,
    ProblemListResponse,
    ProblemRegistrationResponse,
    ProblemResponse,
    ProblemUpdate,
    QuestionMetadataResponse,
    SimilarProblemDetail,
    SimilarProblemResponse,
)
from app.services.graphrag import GraphRAGService
from app.services.llm_router import LLMRouter
from app.services.similarity import SimilarityService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/problems", tags=["problems"])


@router.get("", response_model=ProblemListResponse)
async def list_problems(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.admin, UserRole.student)),
):
    """List all problems with pagination."""
    offset = (page - 1) * page_size
    total_result = await db.execute(select(sa_func.count()).select_from(Question))
    total = total_result.scalar() or 0
    result = await db.execute(
        select(Question).order_by(Question.created_at.desc()).offset(offset).limit(page_size)
    )
    questions = result.scalars().all()
    return ProblemListResponse(
        problems=[ProblemResponse.model_validate(q) for q in questions],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=ProblemRegistrationResponse, status_code=201)
async def create_problem(body: ProblemCreate, db: AsyncSession = Depends(get_db), _: User = Depends(require_role(UserRole.admin))):
    """Create a new problem with duplicate detection and optional concept extraction."""
    concept_extraction = None
    eval_concept_ids: list[int] = []
    req_concept_ids: list[int] = []
    eval_weights: dict[int, float] = {}
    req_weights: dict[int, float] = {}

    # Auto-extract concepts via LLM if requested and no concepts provided
    if body.auto_extract_concepts and not body.concept_ids and not body.concept_weights:
        llm = LLMRouter()
        extracted = await llm.extract_concepts(body.content)
        if extracted:
            graphrag = GraphRAGService(db)
            eval_entries = extracted.get("evaluation_concepts", [])
            req_entries = extracted.get("required_concepts", [])

            # Use weighted matching (handles both list[str] and list[dict] formats)
            eval_weights = await graphrag.match_concept_names_with_weights(eval_entries)
            req_weights = await graphrag.match_concept_names_with_weights(req_entries)
            eval_concept_ids = list(eval_weights.keys())
            req_concept_ids = list(req_weights.keys())

            # Extract display names (handle both old and new format)
            eval_names = [
                e["name"] if isinstance(e, dict) else e for e in eval_entries
            ]
            req_names = [
                e["name"] if isinstance(e, dict) else e for e in req_entries
            ]

            # Infer expected_form from LLM if not provided by user
            inferred_form = None
            raw_form = extracted.get("expected_form")
            if raw_form:
                try:
                    inferred_form = ExpectedForm(raw_form)
                except ValueError:
                    logger.warning("LLM returned invalid expected_form: %s", raw_form)

            concept_extraction = ConceptExtractionResult(
                evaluation_concept_names=eval_names,
                required_concept_names=req_names,
                matched_evaluation_concept_ids=eval_concept_ids,
                matched_required_concept_ids=req_concept_ids,
                evaluation_concept_weights=eval_weights,
                required_concept_weights=req_weights,
                inferred_expected_form=inferred_form,
                inferred_grading_hints=extracted.get("grading_hints"),
            )

    # Build effective concept weights for duplicate check
    # Priority: concept_weights > concept_ids (as {id: 1.0}) > LLM-extracted weights
    if body.concept_weights:
        effective_weights = dict(body.concept_weights)
    elif body.concept_ids:
        effective_weights = {cid: 1.0 for cid in body.concept_ids}
    else:
        effective_weights = {**eval_weights, **req_weights}

    # Determine effective expected_form and grading_hints
    effective_form = body.expected_form
    effective_hints = body.grading_hints
    if concept_extraction:
        if effective_form is None and concept_extraction.inferred_expected_form:
            effective_form = concept_extraction.inferred_expected_form
        if effective_hints is None and concept_extraction.inferred_grading_hints:
            effective_hints = concept_extraction.inferred_grading_hints
    # Final default
    if effective_form is None:
        effective_form = ExpectedForm.simplified

    similarity_svc = SimilarityService(db)
    dup_result = await similarity_svc.check_duplicate(effective_weights, content=body.content)

    similar_details = [
        SimilarProblemDetail(**s) for s in dup_result["similar_problems"]
    ]

    dup_check = DuplicateCheckResponse(
        is_duplicate=dup_result["is_duplicate"],
        mode=dup_result["mode"],
        threshold=dup_result["threshold"],
        similar_problem_id=(
            dup_result["similar_problems"][0]["question_id"]
            if dup_result["similar_problems"]
            else None
        ),
        similarity_score=(
            dup_result["similar_problems"][0]["similarity_score"]
            if dup_result["similar_problems"]
            else 0.0
        ),
    )

    # Block mode: reject duplicates
    if dup_result["is_duplicate"] and dup_result["mode"] == "block":
        raise HTTPException(
            status_code=409,
            detail={
                "message": "Duplicate problem detected",
                "duplicate_check": dup_check.model_dump(),
                "similar_problems": [s.model_dump() for s in similar_details],
            },
        )

    # Insert question
    question = Question(
        content=body.content,
        correct_answer=body.correct_answer,
        expected_form=effective_form,
        target_grade=body.target_grade,
        grading_hints=effective_hints,
    )
    db.add(question)
    await db.flush()

    # Insert edge records — evaluation concepts (with weights)
    if body.concept_weights:
        # User-provided concept_weights go to QuestionEvaluates
        for concept_id, weight in body.concept_weights.items():
            db.add(QuestionEvaluates(
                question_id=question.id, concept_id=concept_id, weight=weight,
            ))
    elif body.concept_ids:
        # User-provided concept_ids go to QuestionEvaluates (weight=1.0)
        for concept_id in body.concept_ids:
            db.add(QuestionEvaluates(question_id=question.id, concept_id=concept_id))
    elif eval_concept_ids:
        # LLM-extracted evaluation concepts with weights
        for concept_id in eval_concept_ids:
            weight = eval_weights.get(concept_id, 1.0)
            db.add(QuestionEvaluates(
                question_id=question.id, concept_id=concept_id, weight=weight,
            ))

    # Insert required concept edges (with weights)
    for concept_id in req_concept_ids:
        weight = req_weights.get(concept_id, 1.0)
        db.add(QuestionRequires(
            question_id=question.id, concept_id=concept_id, weight=weight,
        ))

    # Insert unit edges
    for unit_id in body.unit_ids:
        db.add(QuestionUnits(question_id=question.id, unit_id=unit_id))

    return ProblemRegistrationResponse(
        problem=ProblemResponse.model_validate(question),
        registered=True,
        duplicate_check=dup_check,
        similar_problems=similar_details,
        concept_extraction=concept_extraction,
    )


@router.get("/{problem_id}", response_model=ProblemResponse)
async def get_problem(problem_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(require_role(UserRole.admin, UserRole.student))):
    """Get a problem by ID."""
    result = await db.execute(
        select(Question).where(Question.id == problem_id)
    )
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="Problem not found")
    return ProblemResponse.model_validate(question)


@router.put("/{problem_id}", response_model=ProblemResponse)
async def update_problem(problem_id: int, body: ProblemUpdate, db: AsyncSession = Depends(get_db), _: User = Depends(require_role(UserRole.admin))):
    """Update a problem by ID."""
    result = await db.execute(
        select(Question).where(Question.id == problem_id)
    )
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="Problem not found")
    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(question, key, value)
    db.add(question)
    await db.flush()
    await db.refresh(question)
    return ProblemResponse.model_validate(question)


@router.delete("/{problem_id}", status_code=204)
async def delete_problem(problem_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(require_role(UserRole.admin))):
    """Delete a problem by ID, including all related edge records."""
    result = await db.execute(
        select(Question).where(Question.id == problem_id)
    )
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="Problem not found")

    # Delete related edge records first (no FK cascade in DB)
    from sqlalchemy import delete as sa_delete
    await db.execute(sa_delete(QuestionEvaluates).where(QuestionEvaluates.question_id == problem_id))
    await db.execute(sa_delete(QuestionRequires).where(QuestionRequires.question_id == problem_id))
    await db.execute(sa_delete(QuestionUnits).where(QuestionUnits.question_id == problem_id))

    await db.delete(question)
    await db.flush()


@router.get("/{problem_id}/metadata", response_model=QuestionMetadataResponse)
async def get_problem_metadata(problem_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(require_role(UserRole.admin))):
    """Get full metadata for a problem including concept weights and units."""
    graphrag = GraphRAGService(db)
    metadata = await graphrag.get_question_metadata(problem_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Problem not found")
    return QuestionMetadataResponse(
        question_id=metadata["question_id"],
        content=metadata["content"],
        correct_answer=metadata["correct_answer"],
        expected_form=metadata["expected_form"],
        grading_hints=metadata["grading_hints"],
        evaluation_concepts=[
            ConceptWeightDetail(**c) for c in metadata["evaluation_concepts"]
        ],
        required_concepts=[
            ConceptWeightDetail(**c) for c in metadata["required_concepts"]
        ],
        unit_ids=metadata["unit_ids"],
    )


@router.get("/{problem_id}/similar", response_model=SimilarProblemResponse)
async def get_similar_problems(problem_id: int, db: AsyncSession = Depends(get_db), _: User = Depends(require_role(UserRole.admin))):
    """Find problems similar to the given problem."""
    graphrag = GraphRAGService(db)
    concept_weights = await graphrag.get_concept_weights_for_question(problem_id)
    if not concept_weights:
        raise HTTPException(status_code=404, detail="Problem not found or has no concepts")

    similarity_svc = SimilarityService(db)
    similar = await similarity_svc.find_similar(concept_weights, exclude_question_id=problem_id)

    # Fetch the actual Question records for similar problems
    similar_question_ids = [s["question_id"] for s in similar]
    problems = []
    scores = []
    details = []

    if similar_question_ids:
        result = await db.execute(
            select(Question).where(Question.id.in_(similar_question_ids))
        )
        question_map = {q.id: q for q in result.scalars().all()}

        for s in similar:
            q = question_map.get(s["question_id"])
            if q:
                problems.append(ProblemResponse.model_validate(q))
                scores.append(s["similarity_score"])
                details.append(SimilarProblemDetail(**s))

    return SimilarProblemResponse(
        problems=problems, similarity_scores=scores, details=details
    )


@router.get("/concepts/all", response_model=list[ConceptResponse])
async def list_concepts(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.admin)),
):
    """List all concepts for the concept picker."""
    result = await db.execute(
        select(Concept).order_by(Concept.name)
    )
    return [ConceptResponse.model_validate(c) for c in result.scalars().all()]
