"""Similarity service for finding similar/duplicate problems using concept-based Jaccard similarity."""

import re
import unicodedata

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.history import AdminSettings
from app.models.nodes import Question
from app.services.graphrag import GraphRAGService


class SimilarityService:
    """Computes concept-based Jaccard similarity between math problems."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.graphrag = GraphRAGService(db)

    @staticmethod
    def jaccard_similarity(set_a: set, set_b: set) -> float:
        """Compute Jaccard similarity: |A ∩ B| / |A ∪ B|."""
        if not set_a and not set_b:
            return 0.0
        intersection = set_a & set_b
        union = set_a | set_b
        return len(intersection) / len(union)

    @staticmethod
    def normalize_content(text: str) -> str:
        """Normalize problem content for comparison: lowercase, strip whitespace, remove accents."""
        text = unicodedata.normalize("NFKD", text)
        text = text.lower().strip()
        text = re.sub(r"\s+", " ", text)
        return text

    async def get_threshold(self) -> float:
        """Read similarity threshold from admin_settings."""
        result = await self.db.execute(
            select(AdminSettings.value).where(
                AdminSettings.key == "similarity_threshold"
            )
        )
        row = result.scalar_one_or_none()
        return float(row) if row else 0.85

    async def get_detection_mode(self) -> str:
        """Read duplicate detection mode from admin_settings."""
        result = await self.db.execute(
            select(AdminSettings.value).where(
                AdminSettings.key == "duplicate_detection_mode"
            )
        )
        row = result.scalar_one_or_none()
        return row if row else "warn"

    async def find_similar(
        self, new_concept_ids: set[int], exclude_question_id: int | None = None
    ) -> list[dict]:
        """Compare new concept set against all existing questions.

        Returns sorted list of similar problems with scores and concept details.
        """
        all_sets = await self.graphrag.get_all_questions_concept_sets()

        results = []
        for q_id, existing_concepts in all_sets.items():
            if exclude_question_id and q_id == exclude_question_id:
                continue
            score = self.jaccard_similarity(new_concept_ids, existing_concepts)
            if score > 0:
                shared = new_concept_ids & existing_concepts
                only_new = new_concept_ids - existing_concepts
                only_existing = existing_concepts - new_concept_ids
                results.append(
                    {
                        "question_id": q_id,
                        "similarity_score": round(score, 4),
                        "shared_concepts": sorted(shared),
                        "only_in_new": sorted(only_new),
                        "only_in_existing": sorted(only_existing),
                    }
                )

        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results

    async def find_content_duplicates(self, content: str) -> list[dict]:
        """Find existing problems with identical normalized content."""
        normalized = self.normalize_content(content)
        if not normalized:
            return []

        result = await self.db.execute(select(Question.id, Question.content))
        duplicates = []
        for row in result.all():
            if self.normalize_content(row.content) == normalized:
                duplicates.append(
                    {
                        "question_id": row.id,
                        "similarity_score": 1.0,
                        "shared_concepts": [],
                        "only_in_new": [],
                        "only_in_existing": [],
                    }
                )
        return duplicates

    async def check_duplicate(
        self, new_concept_ids: set[int], content: str = ""
    ) -> dict:
        """Check if a new problem's concept set is a duplicate.

        Uses concept-based Jaccard similarity first, then falls back to
        exact text content matching when concept sets are empty.

        Returns dict with is_duplicate, mode, threshold, and similar_problems.
        """
        threshold = await self.get_threshold()
        mode = await self.get_detection_mode()
        similar = await self.find_similar(new_concept_ids)

        duplicates = [s for s in similar if s["similarity_score"] >= threshold]

        # Fallback: if no concept-based duplicates found, check text content
        if not duplicates and content:
            content_dups = await self.find_content_duplicates(content)
            duplicates.extend(content_dups)

        is_duplicate = len(duplicates) > 0

        return {
            "is_duplicate": is_duplicate,
            "mode": mode,
            "threshold": threshold,
            "similar_problems": duplicates,
        }
