"""Grading engine orchestrating SymPy, LLM, and cache for answer evaluation."""

from sqlalchemy.ext.asyncio import AsyncSession


class GradingEngine:
    """Orchestrates answer grading via SymPy first, then LLM fallback, with caching."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def grade(
        self,
        question_id: int,
        submitted_answer: str,
        correct_answer: str,
        expected_form: str,
    ) -> dict:
        """Grade a submitted answer. Returns dict with is_correct, judged_by, reasoning. TODO: Phase 2."""
        raise NotImplementedError

    async def get_cache_stats(self) -> dict:
        """Return cache hit statistics. TODO: Phase 2."""
        raise NotImplementedError
