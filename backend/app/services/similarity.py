"""Similarity service for finding similar/duplicate problems."""


class SimilarityService:
    """Computes similarity between math problems for deduplication and recommendations."""

    async def find_similar(self, problem_content: str, threshold: float = 0.85) -> list[dict]:
        """Find problems similar to the given content. TODO: Phase 2."""
        raise NotImplementedError

    async def check_duplicate(self, problem_content: str) -> dict:
        """Check if a problem is a duplicate. TODO: Phase 2."""
        raise NotImplementedError
