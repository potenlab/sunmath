"""Similarity service for finding similar/duplicate problems using weighted cosine similarity."""

import math
import re
import unicodedata

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.history import AdminSettings
from app.models.nodes import Question
from app.services.graphrag import GraphRAGService


class SimilarityService:
    """Computes concept-based weighted cosine similarity between math problems."""

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
    def weighted_cosine_similarity(
        weights_a: dict[int, float], weights_b: dict[int, float],
    ) -> float:
        """Compute weighted cosine similarity between two concept weight vectors."""
        if not weights_a or not weights_b:
            return 0.0
        shared_keys = set(weights_a) & set(weights_b)
        if not shared_keys:
            return 0.0
        dot = sum(weights_a[k] * weights_b[k] for k in shared_keys)
        norm_a = math.sqrt(sum(v * v for v in weights_a.values()))
        norm_b = math.sqrt(sum(v * v for v in weights_b.values()))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot / (norm_a * norm_b)

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
        self,
        new_concept_weights: dict[int, float],
        exclude_question_id: int | None = None,
    ) -> list[dict]:
        """Compare new concept weight vector against all existing questions.

        Returns sorted list of similar problems with scores and concept details.
        """
        all_weights = await self.graphrag.get_all_questions_concept_weights()

        new_keys = set(new_concept_weights)
        results = []
        for q_id, existing_weights in all_weights.items():
            if exclude_question_id and q_id == exclude_question_id:
                continue
            score = self.weighted_cosine_similarity(new_concept_weights, existing_weights)
            if score > 0:
                existing_keys = set(existing_weights)
                shared = new_keys & existing_keys
                only_new = new_keys - existing_keys
                only_existing = existing_keys - new_keys
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
        self, new_concept_weights: dict[int, float], content: str = "",
    ) -> dict:
        """Check if a new problem's concept weights are a duplicate.

        Uses weighted cosine similarity first, then falls back to
        exact text content matching when concept sets are empty.

        Returns dict with is_duplicate, mode, threshold, and similar_problems.
        """
        threshold = await self.get_threshold()
        mode = await self.get_detection_mode()
        similar = await self.find_similar(new_concept_weights)

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
