import enum
from datetime import datetime

from sqlalchemy import String, Text, Integer, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ExpectedForm(str, enum.Enum):
    factored = "factored"
    expanded = "expanded"
    simplified = "simplified"
    numeric = "numeric"
    proof = "proof"


class Unit(Base):
    __tablename__ = "units"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    grade_level: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    concepts: Mapped[list["Concept"]] = relationship(
        secondary="unit_concepts", back_populates="units"
    )
    questions: Mapped[list["Question"]] = relationship(
        secondary="question_units", back_populates="units"
    )


class Concept(Base):
    __tablename__ = "concepts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    units: Mapped[list["Unit"]] = relationship(
        secondary="unit_concepts", back_populates="concepts"
    )


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)
    expected_form: Mapped[ExpectedForm] = mapped_column(
        Enum(ExpectedForm), default=ExpectedForm.simplified
    )
    target_grade: Mapped[int | None] = mapped_column(Integer)
    grading_hints: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    units: Mapped[list["Unit"]] = relationship(
        secondary="question_units", back_populates="questions"
    )


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    grade_level: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
