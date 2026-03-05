from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class UnitConcept(Base):
    __tablename__ = "unit_concepts"

    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id"), primary_key=True)
    concept_id: Mapped[int] = mapped_column(ForeignKey("concepts.id"), primary_key=True)


class ConceptPrerequisite(Base):
    __tablename__ = "concept_prerequisites"

    concept_id: Mapped[int] = mapped_column(ForeignKey("concepts.id"), primary_key=True)
    prerequisite_concept_id: Mapped[int] = mapped_column(
        ForeignKey("concepts.id"), primary_key=True
    )


class ConceptRelation(Base):
    __tablename__ = "concept_relations"

    concept_id: Mapped[int] = mapped_column(ForeignKey("concepts.id"), primary_key=True)
    related_concept_id: Mapped[int] = mapped_column(
        ForeignKey("concepts.id"), primary_key=True
    )
    relation_type: Mapped[str] = mapped_column(String(50), primary_key=True)


class QuestionEvaluates(Base):
    __tablename__ = "question_evaluates"

    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), primary_key=True)
    concept_id: Mapped[int] = mapped_column(ForeignKey("concepts.id"), primary_key=True)


class QuestionUnits(Base):
    __tablename__ = "question_units"

    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), primary_key=True)
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id"), primary_key=True)


class QuestionRequires(Base):
    __tablename__ = "question_requires"

    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), primary_key=True)
    concept_id: Mapped[int] = mapped_column(ForeignKey("concepts.id"), primary_key=True)
