"""Student diagnosis service using wrong-answer analysis and knowledge graph."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.edges import QuestionEvaluates, QuestionRequires
from app.models.history import (
    StudentConceptMastery,
    StudentDiagnosis,
    WrongAnswerStatus,
    WrongAnswerWarehouse,
)
from app.models.nodes import Question
from app.services.graphrag import GraphRAGService


class DiagnosisService:
    """Generates student diagnoses by analyzing wrong answers and concept mastery."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.graphrag = GraphRAGService(db)

    async def generate_diagnosis(self, student_id: int) -> dict:
        """Generate a comprehensive diagnosis for a student.

        Algorithm:
        1. Get active wrong answers
        2. Count concept frequency across wrong answers
        3. Score concepts: score = frequency * (1 - mastery)
        4. Check if top candidates are prerequisites of other failing concepts
        5. Build prerequisite chains and learning path
        """
        # 1. Get active wrong answers
        wrong_answers = await self._get_active_wrong_answers(student_id)
        if not wrong_answers:
            diagnosis_data = {
                "student_id": student_id,
                "core_weaknesses": [],
                "prerequisite_chains": [],
                "learning_path": ["No active wrong answers found"],
                "recommended_problems": [],
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }
            await self._save_diagnosis(student_id, diagnosis_data)
            return diagnosis_data

        # 2. Count concept frequency across wrong answers (required concepts)
        concept_freq: dict[int, int] = {}
        for wa in wrong_answers:
            question_id = wa["question_id"]
            result = await self.db.execute(
                select(QuestionRequires.concept_id).where(
                    QuestionRequires.question_id == question_id
                )
            )
            for row in result.all():
                concept_freq[row.concept_id] = concept_freq.get(row.concept_id, 0) + 1

        if not concept_freq:
            # Fall back to evaluation concepts
            for wa in wrong_answers:
                result = await self.db.execute(
                    select(QuestionEvaluates.concept_id).where(
                        QuestionEvaluates.question_id == wa["question_id"]
                    )
                )
                for row in result.all():
                    concept_freq[row.concept_id] = concept_freq.get(row.concept_id, 0) + 1

        # 3. Get mastery levels
        mastery_map = await self._get_mastery_map(student_id)

        # 4. Score concepts: score = frequency * (1 - mastery)
        concept_scores: dict[int, float] = {}
        for cid, freq in concept_freq.items():
            mastery = mastery_map.get(cid, 0.0)
            concept_scores[cid] = freq * (1.0 - mastery)

        # 5. Sort by score descending
        sorted_concepts = sorted(concept_scores.items(), key=lambda x: x[1], reverse=True)

        # 6. Check if top candidates are prerequisites of other failing concepts
        # A true root cause is upstream — it's a prerequisite of other failing concepts
        failing_concept_ids = set(concept_freq.keys())
        root_causes = []
        for cid, score in sorted_concepts:
            if score <= 0:
                continue
            dependents = await self.graphrag.get_concept_dependents(cid)
            dependent_ids = {d["id"] for d in dependents}
            # If this concept's dependents overlap with failing concepts, it's a root cause
            overlap = dependent_ids & failing_concept_ids
            if overlap or not root_causes:
                root_causes.append(cid)
            if len(root_causes) >= 3:
                break

        # 7. Get concept names
        all_concept_ids = list(failing_concept_ids | set(root_causes))
        concept_names = await self.graphrag.get_concept_names(all_concept_ids)

        # 8. Build prerequisite chains from root causes (deduplicated, order-preserved)
        prereq_chains = []
        for rc_id in root_causes:
            prereqs = await self.graphrag.get_concept_prerequisites(rc_id)
            seen_in_chain: set[int] = set()
            chain: list[str] = []
            for p in prereqs:
                if p["id"] not in seen_in_chain:
                    seen_in_chain.add(p["id"])
                    chain.append(p["name"])
            rc_name = concept_names.get(rc_id, f"concept_{rc_id}")
            if rc_id not in seen_in_chain:
                chain.append(rc_name)
            prereq_chains.append(chain)

        # 9. Find affected units
        affected_units = await self.graphrag.get_affected_units(root_causes)

        # 10. Generate learning path
        learning_path = await self._build_learning_path(root_causes, concept_names)

        # 11. Find recommended problems
        recommended = await self._find_recommended_problems(root_causes)

        core_weaknesses = [
            concept_names.get(rc, f"concept_{rc}") for rc in root_causes
        ]

        diagnosis_data = {
            "student_id": student_id,
            "core_weaknesses": core_weaknesses,
            "prerequisite_chains": prereq_chains,
            "learning_path": learning_path,
            "recommended_problems": recommended,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

        await self._save_diagnosis(student_id, diagnosis_data)
        return diagnosis_data

    async def generate_learning_path(self, student_id: int) -> dict:
        """Generate a personalized learning path based on diagnosis."""
        diagnosis = await self.generate_diagnosis(student_id)
        return {
            "student_id": student_id,
            "path": diagnosis["learning_path"],
            "estimated_concepts": len(diagnosis["learning_path"]),
        }

    async def _get_active_wrong_answers(self, student_id: int) -> list[dict]:
        """Get active wrong answers from warehouse."""
        result = await self.db.execute(
            select(WrongAnswerWarehouse)
            .where(
                WrongAnswerWarehouse.student_id == student_id,
                WrongAnswerWarehouse.status == WrongAnswerStatus.active,
            )
        )
        return [
            {
                "id": wa.id,
                "question_id": wa.question_id,
                "answer_id": wa.answer_id,
                "retry_count": wa.retry_count,
            }
            for wa in result.scalars().all()
        ]

    async def _get_mastery_map(self, student_id: int) -> dict[int, float]:
        """Get concept mastery levels as a dict."""
        result = await self.db.execute(
            select(
                StudentConceptMastery.concept_id,
                StudentConceptMastery.mastery_level,
            ).where(StudentConceptMastery.student_id == student_id)
        )
        return {row.concept_id: row.mastery_level for row in result.all()}

    async def _build_learning_path(
        self, root_cause_ids: list[int], concept_names: dict[int, str]
    ) -> list[str]:
        """Build learning path: prerequisites first, then root cause practice."""
        path = []
        seen = set()

        for rc_id in root_cause_ids:
            # Add prerequisites first
            prereqs = await self.graphrag.get_concept_prerequisites(rc_id)
            for p in prereqs:
                if p["id"] not in seen:
                    seen.add(p["id"])
                    path.append(f"Review: {p['name']}")

            # Add root cause
            if rc_id not in seen:
                seen.add(rc_id)
                name = concept_names.get(rc_id, f"concept_{rc_id}")
                path.append(f"Practice: {name}")

        return path if path else ["No specific learning path needed"]

    async def _find_recommended_problems(self, concept_ids: list[int]) -> list[int]:
        """Find problems that evaluate root cause concepts."""
        if not concept_ids:
            return []
        result = await self.db.execute(
            select(QuestionEvaluates.question_id)
            .where(QuestionEvaluates.concept_id.in_(concept_ids))
            .distinct()
        )
        return [row.question_id for row in result.all()]

    async def _save_diagnosis(self, student_id: int, diagnosis_data: dict) -> None:
        """Save diagnosis to student_diagnoses table."""
        diagnosis = StudentDiagnosis(
            student_id=student_id,
            diagnosis_data=diagnosis_data,
        )
        self.db.add(diagnosis)
        await self.db.flush()
