"""Mastery engine: updates student concept mastery after grading using EMA."""

import logging

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.history import StudentConceptMastery
from app.services.graphrag import GraphRAGService

logger = logging.getLogger(__name__)

# EMA base learning rate — scaled by concept weight per concept
ALPHA_BASE = 0.3
# Dampening factor for propagation to dependent concepts
PROPAGATION_FACTOR = 0.3


class MasteryEngine:
    """Updates student concept mastery levels using exponential moving average."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.graphrag = GraphRAGService(db)

    async def update_mastery(
        self, student_id: int, question_id: int, is_correct: bool,
    ) -> list[dict]:
        """Update mastery for all concepts tied to this question.

        Returns list of {concept_id, concept_name, old_mastery, new_mastery, delta}.
        """
        signal = 1.0 if is_correct else 0.0

        # Get concept weights for this question (union of evaluates + requires)
        concept_weights = await self.graphrag.get_concept_weights_for_question(question_id)
        if not concept_weights:
            return []

        concept_ids = list(concept_weights.keys())
        concept_names = await self.graphrag.get_concept_names(concept_ids)

        # Fetch current mastery levels
        current_mastery = await self._get_current_mastery(student_id, concept_ids)

        updates: list[dict] = []

        # Direct concept updates
        for concept_id, weight in concept_weights.items():
            old_mastery = current_mastery.get(concept_id, 0.0)
            alpha = ALPHA_BASE * weight
            new_mastery = old_mastery + alpha * (signal - old_mastery)
            new_mastery = max(0.0, min(1.0, new_mastery))
            delta = new_mastery - old_mastery

            if abs(delta) < 1e-6:
                continue

            await self._upsert_mastery(student_id, concept_id, new_mastery)
            updates.append({
                "concept_id": concept_id,
                "concept_name": concept_names.get(concept_id, f"Concept {concept_id}"),
                "old_mastery": round(old_mastery, 4),
                "new_mastery": round(new_mastery, 4),
                "delta": round(delta, 4),
            })

        # Propagate to depth-1 dependents
        propagated = await self._propagate_to_dependents(student_id, updates)
        updates.extend(propagated)

        return updates

    async def _propagate_to_dependents(
        self, student_id: int, direct_updates: list[dict],
    ) -> list[dict]:
        """Propagate mastery changes to direct dependent concepts (depth 1 only)."""
        propagated: list[dict] = []
        seen_ids = {u["concept_id"] for u in direct_updates}

        for update in direct_updates:
            dependents = await self.graphrag.get_concept_dependents(update["concept_id"])
            depth1 = [d for d in dependents if d["depth"] == 1]

            for dep in depth1:
                dep_id = dep["id"]
                if dep_id in seen_ids:
                    continue
                seen_ids.add(dep_id)

                old_mastery = await self._get_single_mastery(student_id, dep_id)
                propagation_delta = update["delta"] * PROPAGATION_FACTOR
                new_mastery = old_mastery + propagation_delta
                new_mastery = max(0.0, min(1.0, new_mastery))
                actual_delta = new_mastery - old_mastery

                if abs(actual_delta) < 1e-6:
                    continue

                await self._upsert_mastery(student_id, dep_id, new_mastery)
                propagated.append({
                    "concept_id": dep_id,
                    "concept_name": dep["name"],
                    "old_mastery": round(old_mastery, 4),
                    "new_mastery": round(new_mastery, 4),
                    "delta": round(actual_delta, 4),
                })

        return propagated

    async def _get_current_mastery(
        self, student_id: int, concept_ids: list[int],
    ) -> dict[int, float]:
        """Fetch current mastery levels for given concepts."""
        if not concept_ids:
            return {}
        result = await self.db.execute(
            select(
                StudentConceptMastery.concept_id,
                StudentConceptMastery.mastery_level,
            ).where(
                StudentConceptMastery.student_id == student_id,
                StudentConceptMastery.concept_id.in_(concept_ids),
            )
        )
        return {row.concept_id: row.mastery_level for row in result.all()}

    async def _get_single_mastery(self, student_id: int, concept_id: int) -> float:
        """Fetch mastery for a single concept, defaulting to 0.0."""
        result = await self.db.execute(
            select(StudentConceptMastery.mastery_level).where(
                StudentConceptMastery.student_id == student_id,
                StudentConceptMastery.concept_id == concept_id,
            )
        )
        row = result.scalar_one_or_none()
        return row if row is not None else 0.0

    async def _upsert_mastery(
        self, student_id: int, concept_id: int, mastery_level: float,
    ) -> None:
        """Insert or update mastery level using PostgreSQL ON CONFLICT."""
        stmt = pg_insert(StudentConceptMastery).values(
            student_id=student_id,
            concept_id=concept_id,
            mastery_level=mastery_level,
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["student_id", "concept_id"],
            set_={"mastery_level": mastery_level},
        )
        await self.db.execute(stmt)
