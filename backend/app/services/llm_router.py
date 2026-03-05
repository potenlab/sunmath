"""LLM router for dispatching grading requests to appropriate LLM providers."""


class LLMRouter:
    """Routes grading requests to configured LLM provider (Claude, GPT, etc.)."""

    async def grade_answer(
        self,
        question_content: str,
        correct_answer: str,
        submitted_answer: str,
        grading_hints: str | None = None,
    ) -> dict:
        """Send grading request to LLM and return result. TODO: Phase 2."""
        raise NotImplementedError
