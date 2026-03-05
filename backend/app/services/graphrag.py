"""GraphRAG service for knowledge graph traversal and retrieval-augmented generation."""

from sqlalchemy.ext.asyncio import AsyncSession


class GraphRAGService:
    """Manages knowledge graph queries for concept relationships and prerequisites."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_concept_prerequisites(self, concept_id: int) -> list[dict]:
        """Return prerequisite chain for a concept. TODO: Phase 2."""
        raise NotImplementedError

    async def get_related_concepts(self, concept_id: int) -> list[dict]:
        """Return related concepts via graph traversal. TODO: Phase 2."""
        raise NotImplementedError

    async def get_unit_concept_graph(self, unit_id: int) -> dict:
        """Return full concept graph for a unit. TODO: Phase 2."""
        raise NotImplementedError
