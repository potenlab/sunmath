"""GraphRAG service for knowledge graph traversal and retrieval-augmented generation."""

import logging
import re

from sqlalchemy import select, text, union_all
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

from app.models.edges import (
    ConceptPrerequisite,
    ConceptRelation,
    QuestionEvaluates,
    QuestionRequires,
    QuestionUnits,
    UnitConcept,
)
from app.models.nodes import Concept, Question, Unit


class GraphRAGService:
    """Manages knowledge graph queries for concept relationships and prerequisites."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_question_metadata(self, question_id: int) -> dict | None:
        """Fetch full metadata for a question including concepts and units."""
        result = await self.db.execute(
            select(Question).where(Question.id == question_id)
        )
        question = result.scalar_one_or_none()
        if not question:
            return None

        # Get evaluation concepts (with weight)
        eval_result = await self.db.execute(
            select(Concept.id, Concept.name, QuestionEvaluates.weight)
            .join(QuestionEvaluates, QuestionEvaluates.concept_id == Concept.id)
            .where(QuestionEvaluates.question_id == question_id)
        )
        evaluation_concepts = [
            {"id": row.id, "name": row.name, "weight": row.weight}
            for row in eval_result.all()
        ]

        # Get required concepts (with weight)
        req_result = await self.db.execute(
            select(Concept.id, Concept.name, QuestionRequires.weight)
            .join(QuestionRequires, QuestionRequires.concept_id == Concept.id)
            .where(QuestionRequires.question_id == question_id)
        )
        required_concepts = [
            {"id": row.id, "name": row.name, "weight": row.weight}
            for row in req_result.all()
        ]

        # Get unit IDs
        unit_result = await self.db.execute(
            select(QuestionUnits.unit_id).where(
                QuestionUnits.question_id == question_id
            )
        )
        unit_ids = [row.unit_id for row in unit_result.all()]

        return {
            "question_id": question.id,
            "content": question.content,
            "correct_answer": question.correct_answer,
            "expected_form": question.expected_form.value,
            "grading_hints": question.grading_hints,
            "evaluation_concepts": evaluation_concepts,
            "required_concepts": required_concepts,
            "unit_ids": unit_ids,
        }

    async def get_concept_prerequisites(self, concept_id: int) -> list[dict]:
        """Return full prerequisite chain for a concept using recursive CTE."""
        cte_query = text("""
            WITH RECURSIVE prereq_chain AS (
                SELECT prerequisite_concept_id AS id, 1 AS depth
                FROM concept_prerequisites
                WHERE concept_id = :concept_id
                UNION
                SELECT cp.prerequisite_concept_id, pc.depth + 1
                FROM concept_prerequisites cp
                JOIN prereq_chain pc ON cp.concept_id = pc.id
            )
            SELECT DISTINCT c.id, c.name, c.category, pc.depth
            FROM prereq_chain pc
            JOIN concepts c ON c.id = pc.id
            ORDER BY pc.depth
        """)
        result = await self.db.execute(cte_query, {"concept_id": concept_id})
        return [
            {"id": row.id, "name": row.name, "category": row.category, "depth": row.depth}
            for row in result.all()
        ]

    async def get_concept_dependents(self, concept_id: int) -> list[dict]:
        """Forward traversal: concepts that depend on this one (recursive)."""
        cte_query = text("""
            WITH RECURSIVE dep_chain AS (
                SELECT concept_id AS id, 1 AS depth
                FROM concept_prerequisites
                WHERE prerequisite_concept_id = :concept_id
                UNION
                SELECT cp.concept_id, dc.depth + 1
                FROM concept_prerequisites cp
                JOIN dep_chain dc ON cp.prerequisite_concept_id = dc.id
            )
            SELECT DISTINCT c.id, c.name, c.category, dc.depth
            FROM dep_chain dc
            JOIN concepts c ON c.id = dc.id
            ORDER BY dc.depth
        """)
        result = await self.db.execute(cte_query, {"concept_id": concept_id})
        return [
            {"id": row.id, "name": row.name, "category": row.category, "depth": row.depth}
            for row in result.all()
        ]

    async def get_related_concepts(self, concept_id: int) -> list[dict]:
        """Lateral associations from concept_relations."""
        result = await self.db.execute(
            select(Concept.id, Concept.name, ConceptRelation.relation_type)
            .join(ConceptRelation, ConceptRelation.related_concept_id == Concept.id)
            .where(ConceptRelation.concept_id == concept_id)
        )
        return [
            {"id": row.id, "name": row.name, "relation_type": row.relation_type}
            for row in result.all()
        ]

    async def get_concepts_for_question(self, question_id: int) -> set[int]:
        """Union of evaluation + required concept IDs for a question."""
        eval_q = select(QuestionEvaluates.concept_id).where(
            QuestionEvaluates.question_id == question_id
        )
        req_q = select(QuestionRequires.concept_id).where(
            QuestionRequires.question_id == question_id
        )
        combined = union_all(eval_q, req_q)
        result = await self.db.execute(combined)
        return {row[0] for row in result.all()}

    async def get_all_questions_concept_sets(self) -> dict[int, set[int]]:
        """Concept sets for ALL questions (for similarity comparison)."""
        eval_result = await self.db.execute(
            select(QuestionEvaluates.question_id, QuestionEvaluates.concept_id)
        )
        req_result = await self.db.execute(
            select(QuestionRequires.question_id, QuestionRequires.concept_id)
        )

        concept_sets: dict[int, set[int]] = {}
        for row in eval_result.all():
            concept_sets.setdefault(row.question_id, set()).add(row.concept_id)
        for row in req_result.all():
            concept_sets.setdefault(row.question_id, set()).add(row.concept_id)
        return concept_sets

    async def get_affected_units(self, concept_ids: list[int]) -> list[dict]:
        """Units containing any of the given concepts."""
        if not concept_ids:
            return []
        result = await self.db.execute(
            select(Unit.id, Unit.name, Concept.id.label("concept_id"), Concept.name.label("concept_name"))
            .join(UnitConcept, UnitConcept.unit_id == Unit.id)
            .join(Concept, Concept.id == UnitConcept.concept_id)
            .where(UnitConcept.concept_id.in_(concept_ids))
            .distinct()
        )
        return [
            {
                "unit_id": row.id,
                "unit_name": row.name,
                "concept_id": row.concept_id,
                "concept_name": row.concept_name,
            }
            for row in result.all()
        ]

    async def get_concept_names(self, concept_ids: list[int]) -> dict[int, str]:
        """ID to name mapping for given concept IDs."""
        if not concept_ids:
            return {}
        result = await self.db.execute(
            select(Concept.id, Concept.name).where(Concept.id.in_(concept_ids))
        )
        return {row.id: row.name for row in result.all()}

    async def get_concept_weights_for_question(self, question_id: int) -> dict[int, float]:
        """Get concept weights for a question (union of evaluates + requires, max weight)."""
        eval_result = await self.db.execute(
            select(QuestionEvaluates.concept_id, QuestionEvaluates.weight)
            .where(QuestionEvaluates.question_id == question_id)
        )
        weights: dict[int, float] = {}
        for row in eval_result.all():
            weights[row.concept_id] = row.weight

        req_result = await self.db.execute(
            select(QuestionRequires.concept_id, QuestionRequires.weight)
            .where(QuestionRequires.question_id == question_id)
        )
        for row in req_result.all():
            existing = weights.get(row.concept_id, 0.0)
            weights[row.concept_id] = max(existing, row.weight)

        return weights

    async def get_all_questions_concept_weights(self) -> dict[int, dict[int, float]]:
        """Concept weight maps for ALL questions (for similarity comparison)."""
        eval_result = await self.db.execute(
            select(
                QuestionEvaluates.question_id,
                QuestionEvaluates.concept_id,
                QuestionEvaluates.weight,
            )
        )
        concept_weights: dict[int, dict[int, float]] = {}
        for row in eval_result.all():
            concept_weights.setdefault(row.question_id, {})[row.concept_id] = row.weight

        req_result = await self.db.execute(
            select(
                QuestionRequires.question_id,
                QuestionRequires.concept_id,
                QuestionRequires.weight,
            )
        )
        for row in req_result.all():
            qw = concept_weights.setdefault(row.question_id, {})
            existing = qw.get(row.concept_id, 0.0)
            qw[row.concept_id] = max(existing, row.weight)

        return concept_weights

    async def match_concept_names_with_weights(
        self, concept_entries: list,
    ) -> dict[int, float]:
        """Match concept names to IDs, preserving weights.

        Accepts both old format (list[str], weight=1.0) and new format
        (list[dict] with 'name' and 'weight' keys).
        Returns {concept_id: weight} after fuzzy matching against DB.
        """
        if not concept_entries:
            return {}

        # Normalize input to list of (name, weight) tuples
        entries: list[tuple[str, float]] = []
        for entry in concept_entries:
            if isinstance(entry, str):
                entries.append((entry, 1.0))
            elif isinstance(entry, dict):
                name = entry.get("name", "")
                weight = float(entry.get("weight", 1.0))
                weight = max(0.0, min(1.0, weight))
                entries.append((name, weight))

        result = await self.db.execute(select(Concept.id, Concept.name))
        all_concepts = result.all()

        lookup: dict[str, int] = {}
        for row in all_concepts:
            normalized = self._normalize_concept_name(row.name)
            lookup[normalized] = row.id

        matched: dict[int, float] = {}
        for name, weight in entries:
            normalized = self._normalize_concept_name(name)
            concept_id = lookup.get(normalized)
            if concept_id is not None:
                existing = matched.get(concept_id, 0.0)
                matched[concept_id] = max(existing, weight)
            else:
                logger.warning(
                    "Concept name '%s' not found in DB (normalized: '%s')",
                    name, normalized,
                )

        return matched

    async def match_concept_names(self, concept_names: list[str]) -> list[int]:
        """Match LLM-returned concept names against existing DB concepts.

        Uses normalized lookup (lowercase, underscores for spaces) to fuzzy-match.
        Logs warnings for unmatched names. Returns list of matched concept IDs.
        """
        if not concept_names:
            return []

        result = await self.db.execute(select(Concept.id, Concept.name))
        all_concepts = result.all()

        # Build normalized lookup: multiple keys per concept for flexibility
        lookup: dict[str, int] = {}
        for row in all_concepts:
            normalized = self._normalize_concept_name(row.name)
            lookup[normalized] = row.id

        matched_ids = []
        for name in concept_names:
            normalized = self._normalize_concept_name(name)
            concept_id = lookup.get(normalized)
            if concept_id is not None:
                matched_ids.append(concept_id)
            else:
                logger.warning("Concept name '%s' not found in DB (normalized: '%s')", name, normalized)

        return matched_ids

    @staticmethod
    def _normalize_concept_name(name: str) -> str:
        """Normalize concept name for matching: lowercase, collapse whitespace/underscores."""
        s = name.strip().lower()
        s = re.sub(r"[\s_-]+", "_", s)
        return s
