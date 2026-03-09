"""Grading engine orchestrating SymPy, LLM, and cache for answer evaluation."""

import hashlib

from sqlalchemy import select, func, case, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.history import (
    AnswerCache,
    JudgedBy,
    StudentAnswer,
    WrongAnswerStatus,
    WrongAnswerWarehouse,
)
from app.models.nodes import Question
from app.services.graphrag import GraphRAGService
from app.services.llm_router import LLMRouter
from app.services.mastery_engine import MasteryEngine
from app.services.sympy_engine import SympyEngine


class GradingEngine:
    """Orchestrates answer grading via SymPy first, then LLM fallback, with caching."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.graphrag = GraphRAGService(db)
        self.sympy = SympyEngine()
        self.llm = LLMRouter()

    async def grade(
        self,
        student_id: int,
        question_id: int,
        submitted_answer: str,
    ) -> dict:
        """Main grading pipeline.

        Returns dict with: is_correct, judged_by, reasoning, cached
        """
        answer_hash = self._compute_hash(submitted_answer)

        # 1. Cache check
        cached = await self._check_cache(question_id, answer_hash)
        if cached:
            # Save student answer record even for cached results
            answer_id = await self._save_student_answer(
                student_id, question_id, submitted_answer,
                cached["is_correct"], JudgedBy.cache, cached["reasoning"],
            )
            if not cached["is_correct"]:
                await self._add_to_wrong_answers(student_id, question_id, answer_id)
            else:
                await self._resolve_wrong_answers(student_id, question_id)

            # Update concept mastery
            mastery_engine = MasteryEngine(self.db)
            mastery_updates = await mastery_engine.update_mastery(
                student_id, question_id, cached["is_correct"],
            )

            return {
                "is_correct": cached["is_correct"],
                "judged_by": "cache",
                "reasoning": cached["reasoning"],
                "cached": True,
                "mastery_updates": mastery_updates,
            }

        # 2. Fetch question metadata
        metadata = await self.graphrag.get_question_metadata(question_id)
        if not metadata:
            return {
                "is_correct": False,
                "judged_by": "sympy",
                "reasoning": f"Question {question_id} not found",
                "cached": False,
            }

        correct_answer = metadata["correct_answer"]
        expected_form = metadata["expected_form"]

        # 3. Branch on expected_form
        if expected_form == "proof":
            result = await self._grade_proof(metadata, submitted_answer)
        else:
            result = await self._grade_mathematical(
                metadata, submitted_answer, correct_answer, expected_form
            )

        # 4. Save to cache
        await self._save_to_cache(
            question_id, answer_hash,
            result["is_correct"], result["judged_by"], result["reasoning"],
        )

        # 5. Save student answer
        judged_by_enum = JudgedBy(result["judged_by"])
        answer_id = await self._save_student_answer(
            student_id, question_id, submitted_answer,
            result["is_correct"], judged_by_enum, result["reasoning"],
        )

        # 6. Wrong answer warehouse management
        if not result["is_correct"]:
            await self._add_to_wrong_answers(student_id, question_id, answer_id)
        else:
            await self._resolve_wrong_answers(student_id, question_id)

        # 7. Update concept mastery
        mastery_engine = MasteryEngine(self.db)
        mastery_updates = await mastery_engine.update_mastery(
            student_id, question_id, result["is_correct"],
        )

        return {
            "is_correct": result["is_correct"],
            "judged_by": result["judged_by"],
            "reasoning": result["reasoning"],
            "cached": False,
            "mastery_updates": mastery_updates,
        }

    async def _grade_mathematical(
        self, metadata: dict, submitted_answer: str,
        correct_answer: str, expected_form: str,
    ) -> dict:
        """SymPy-based grading path."""
        # Check equivalence
        equiv_result = self.sympy.check_equivalence(submitted_answer, correct_answer)

        if equiv_result["error"]:
            # Parse error -> LLM fallback
            llm_result = await self.llm.grade_answer(
                metadata["content"],
                correct_answer,
                submitted_answer,
                metadata.get("grading_hints"),
                metadata.get("evaluation_concepts"),
            )
            return {
                "is_correct": llm_result["is_correct"],
                "judged_by": "llm",
                "reasoning": llm_result["reasoning"],
            }

        if not equiv_result["equivalent"]:
            return {
                "is_correct": False,
                "judged_by": "sympy",
                "reasoning": (
                    f"Mathematically incorrect. "
                    f"Expected: {correct_answer}, Got: {submitted_answer}"
                ),
            }

        # Equivalent — now check form if needed
        if expected_form in ("factored", "expanded", "numeric"):
            form_result = self.sympy.check_form(submitted_answer, expected_form)
            if form_result["error"]:
                # Can't check form, accept as correct
                return {
                    "is_correct": True,
                    "judged_by": "sympy",
                    "reasoning": "Mathematically correct (form check unavailable)",
                }
            if not form_result["matches"]:
                return {
                    "is_correct": False,
                    "judged_by": "sympy",
                    "reasoning": (
                        f"Mathematically equivalent but wrong form. "
                        f"Expected {expected_form} form. {form_result['reason']}"
                    ),
                }

        return {
            "is_correct": True,
            "judged_by": "sympy",
            "reasoning": f"Correct. Answer is mathematically equivalent and in {expected_form} form.",
        }

    async def _grade_proof(self, metadata: dict, submitted_answer: str) -> dict:
        """LLM-based grading path for proofs."""
        llm_result = await self.llm.grade_answer(
            metadata["content"],
            metadata["correct_answer"],
            submitted_answer,
            metadata.get("grading_hints"),
            metadata.get("evaluation_concepts"),
        )
        return {
            "is_correct": llm_result["is_correct"],
            "judged_by": "llm",
            "reasoning": llm_result["reasoning"],
        }

    @staticmethod
    def _compute_hash(answer: str) -> str:
        """Compute SHA-256 hash of normalized answer."""
        normalized = answer.strip().lower()
        return hashlib.sha256(normalized.encode()).hexdigest()

    async def _check_cache(self, question_id: int, answer_hash: str) -> dict | None:
        """Look up cached grading result."""
        result = await self.db.execute(
            select(AnswerCache).where(
                AnswerCache.question_id == question_id,
                AnswerCache.submitted_answer_hash == answer_hash,
            )
        )
        cached = result.scalar_one_or_none()
        if cached:
            return {
                "is_correct": cached.is_correct,
                "judged_by": cached.judged_by.value,
                "reasoning": cached.reasoning or "",
            }
        return None

    async def _save_to_cache(
        self, question_id: int, answer_hash: str,
        is_correct: bool, judged_by: str, reasoning: str,
    ) -> None:
        """Save grading result to cache."""
        judged_by_enum = JudgedBy(judged_by)
        cache_entry = AnswerCache(
            question_id=question_id,
            submitted_answer_hash=answer_hash,
            is_correct=is_correct,
            judged_by=judged_by_enum,
            reasoning=reasoning,
        )
        self.db.add(cache_entry)
        await self.db.flush()

    async def _save_student_answer(
        self, student_id: int, question_id: int, submitted_answer: str,
        is_correct: bool, judged_by: JudgedBy, reasoning: str,
    ) -> int:
        """Save student answer record. Returns the answer ID."""
        answer = StudentAnswer(
            student_id=student_id,
            question_id=question_id,
            submitted_answer=submitted_answer,
            is_correct=is_correct,
            judged_by=judged_by,
            reasoning=reasoning,
        )
        self.db.add(answer)
        await self.db.flush()
        return answer.id

    async def _add_to_wrong_answers(
        self, student_id: int, question_id: int, answer_id: int,
    ) -> None:
        """Add to wrong answer warehouse with retry_count tracking."""
        # Check for existing entry to inherit retry_count
        result = await self.db.execute(
            select(WrongAnswerWarehouse)
            .where(
                WrongAnswerWarehouse.student_id == student_id,
                WrongAnswerWarehouse.question_id == question_id,
            )
            .order_by(WrongAnswerWarehouse.created_at.desc())
            .limit(1)
        )
        existing = result.scalar_one_or_none()
        retry_count = (existing.retry_count + 1) if existing else 0

        entry = WrongAnswerWarehouse(
            student_id=student_id,
            question_id=question_id,
            answer_id=answer_id,
            status=WrongAnswerStatus.active,
            retry_count=retry_count,
        )
        self.db.add(entry)
        await self.db.flush()

    async def _resolve_wrong_answers(
        self, student_id: int, question_id: int,
    ) -> None:
        """Resolve active wrong answer entries when student answers correctly."""
        await self.db.execute(
            update(WrongAnswerWarehouse)
            .where(
                WrongAnswerWarehouse.student_id == student_id,
                WrongAnswerWarehouse.question_id == question_id,
                WrongAnswerWarehouse.status == WrongAnswerStatus.active,
            )
            .values(status=WrongAnswerStatus.resolved)
        )

    async def get_cache_stats(self) -> dict:
        """Return cache statistics."""
        # Total entries
        total_result = await self.db.execute(
            select(func.count(AnswerCache.id))
        )
        total = total_result.scalar() or 0

        # Entries by judge type
        by_judge_result = await self.db.execute(
            select(AnswerCache.judged_by, func.count(AnswerCache.id))
            .group_by(AnswerCache.judged_by)
        )
        entries_by_judge = {"sympy": 0, "llm": 0, "cache": 0}
        for row in by_judge_result.all():
            entries_by_judge[row[0].value] = row[1]

        # Approximate hit rate from student_answers judged by cache
        cache_hits_result = await self.db.execute(
            select(func.count(StudentAnswer.id)).where(
                StudentAnswer.judged_by == JudgedBy.cache
            )
        )
        cache_hits = cache_hits_result.scalar() or 0

        total_answers_result = await self.db.execute(
            select(func.count(StudentAnswer.id))
        )
        total_answers = total_answers_result.scalar() or 0

        hit_rate = (cache_hits / total_answers) if total_answers > 0 else 0.0

        return {
            "total_entries": total,
            "hit_rate": round(hit_rate, 4),
            "entries_by_judge": entries_by_judge,
        }
