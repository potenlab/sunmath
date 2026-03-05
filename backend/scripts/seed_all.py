"""Seed script to load all sample data into PostgreSQL.

Loads data in dependency order:
1. Units
2. Concepts + unit_concepts + concept_prerequisites + concept_relations
3. Questions + question_units + question_evaluates + question_requires
4. Students + student_answers + student_concept_mastery + wrong_answer_warehouse

Usage:
    cd backend
    source .venv/bin/activate
    python scripts/seed_all.py [--reset]

    --reset: Drop and re-insert all seed data (preserves admin_settings)
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text

from app.api.deps import async_engine

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

SQL_FILES_ORDER = [
    "seed_units.sql",
    "seed_concepts.sql",
    "seed_problems.sql",
    "seed_students.sql",
]

# Tables to clear when --reset is used (reverse dependency order)
TABLES_TO_CLEAR = [
    "wrong_answer_warehouse",
    "student_concept_mastery",
    "student_answers",
    "student_diagnoses",
    "answer_cache",
    "question_requires",
    "question_evaluates",
    "question_units",
    "concept_relations",
    "concept_prerequisites",
    "unit_concepts",
    "questions",
    "students",
    "concepts",
    "units",
]


async def check_data_exists() -> bool:
    """Check if seed data already exists."""
    async with async_engine.begin() as conn:
        result = await conn.execute(text("SELECT COUNT(*) FROM units"))
        count = result.scalar()
        return count > 0


async def reset_data():
    """Clear all seed data tables (preserves admin_settings)."""
    async with async_engine.begin() as conn:
        for table in TABLES_TO_CLEAR:
            await conn.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
            print(f"  Cleared: {table}")
    print()


async def execute_sql_file(filepath: Path):
    """Execute a SQL file against the database."""
    sql_content = filepath.read_text(encoding="utf-8")

    async with async_engine.begin() as conn:
        # Strip inline comments and split into individual statements
        statements = []
        current = []
        for line in sql_content.split("\n"):
            stripped = line.strip()
            # Skip empty lines and full-line comments
            if not stripped or stripped.startswith("--"):
                continue
            # Strip inline comments for semicolon detection
            code_part = stripped
            if "--" in stripped:
                # Find -- that's not inside a string (simple heuristic)
                idx = stripped.index("--")
                code_part = stripped[:idx].strip()
            current.append(code_part)
            if code_part.endswith(";"):
                statements.append("\n".join(current))
                current = []

        # Handle any remaining content
        if current:
            remaining = "\n".join(current).strip()
            if remaining:
                statements.append(remaining)

        for stmt in statements:
            stmt = stmt.strip()
            if not stmt:
                continue
            try:
                await conn.execute(text(stmt))
            except Exception as e:
                print(f"  ERROR executing statement: {e}")
                print(f"  Statement (first 300 chars): {stmt[:300]}...")
                raise


async def verify_data():
    """Verify all data was loaded correctly."""
    checks = [
        ("units", "SELECT COUNT(*) FROM units"),
        ("concepts", "SELECT COUNT(*) FROM concepts"),
        ("unit_concepts", "SELECT COUNT(*) FROM unit_concepts"),
        ("concept_prerequisites", "SELECT COUNT(*) FROM concept_prerequisites"),
        ("concept_relations", "SELECT COUNT(*) FROM concept_relations"),
        ("questions", "SELECT COUNT(*) FROM questions"),
        ("question_units", "SELECT COUNT(*) FROM question_units"),
        ("question_evaluates", "SELECT COUNT(*) FROM question_evaluates"),
        ("question_requires", "SELECT COUNT(*) FROM question_requires"),
        ("students", "SELECT COUNT(*) FROM students"),
        ("student_answers", "SELECT COUNT(*) FROM student_answers"),
        ("student_concept_mastery", "SELECT COUNT(*) FROM student_concept_mastery"),
        ("wrong_answer_warehouse", "SELECT COUNT(*) FROM wrong_answer_warehouse"),
    ]

    print("Data verification:")
    print("-" * 45)
    all_ok = True
    async with async_engine.begin() as conn:
        for name, query in checks:
            result = await conn.execute(text(query))
            count = result.scalar()
            status = "OK" if count > 0 else "EMPTY"
            if count == 0:
                all_ok = False
            print(f"  {name:30s} {count:5d}  [{status}]")

    print("-" * 45)
    return all_ok


async def verify_demo_scenarios():
    """Verify the key demo scenarios are correctly set up."""
    print("\nDemo scenario verification:")
    print("=" * 60)

    async with async_engine.begin() as conn:
        # Demo: Student A's wrong answers should all trace to completing_the_square
        result = await conn.execute(text("""
            SELECT q.id, q.content, sa.submitted_answer, sa.is_correct
            FROM student_answers sa
            JOIN questions q ON q.id = sa.question_id
            WHERE sa.student_id = 1 AND sa.is_correct = false
            ORDER BY q.id
        """))
        rows = result.fetchall()
        print("\nStudent A (Kim Minjun) - wrong answers:")
        for row in rows:
            print(f"  Q{row[0]}: {row[1][:60]}...")
            print(f"    Submitted: {row[2]}")

        # Verify these questions require completing_the_square
        result = await conn.execute(text("""
            SELECT DISTINCT c.name
            FROM student_answers sa
            JOIN question_requires qr ON qr.question_id = sa.question_id
            JOIN concepts c ON c.id = qr.concept_id
            WHERE sa.student_id = 1 AND sa.is_correct = false
            ORDER BY c.name
        """))
        rows = result.fetchall()
        concepts = [row[0] for row in rows]
        has_cts = "completing_the_square" in concepts
        print(f"\n  Required concepts across wrong answers: {concepts}")
        print(f"  Contains completing_the_square: {'YES' if has_cts else 'NO'}")

        # Demo: Student B's wrong answers should trace to radian_measure
        result = await conn.execute(text("""
            SELECT q.id, q.content, sa.submitted_answer, sa.is_correct
            FROM student_answers sa
            JOIN questions q ON q.id = sa.question_id
            WHERE sa.student_id = 2 AND sa.is_correct = false
            ORDER BY q.id
        """))
        rows = result.fetchall()
        print("\n\nStudent B (Lee Soyeon) - wrong answers:")
        for row in rows:
            print(f"  Q{row[0]}: {row[1][:60]}...")
            print(f"    Submitted: {row[2]}")

        result = await conn.execute(text("""
            SELECT DISTINCT c.name
            FROM student_answers sa
            JOIN question_requires qr ON qr.question_id = sa.question_id
            JOIN concepts c ON c.id = qr.concept_id
            WHERE sa.student_id = 2 AND sa.is_correct = false
            ORDER BY c.name
        """))
        rows = result.fetchall()
        concepts = [row[0] for row in rows]
        has_rad = "radian_measure" in concepts
        print(f"\n  Required concepts across wrong answers: {concepts}")
        print(f"  Contains radian_measure: {'YES' if has_rad else 'NO'}")

        # Verify prerequisite chain: multiplication_formulas -> completing_the_square
        result = await conn.execute(text("""
            WITH RECURSIVE prereq_chain AS (
                SELECT concept_id, prerequisite_concept_id, 1 as depth
                FROM concept_prerequisites
                WHERE concept_id = (SELECT id FROM concepts WHERE name = 'completing_the_square')
                UNION ALL
                SELECT cp.concept_id, cp.prerequisite_concept_id, pc.depth + 1
                FROM concept_prerequisites cp
                JOIN prereq_chain pc ON cp.concept_id = pc.prerequisite_concept_id
                WHERE pc.depth < 10
            )
            SELECT c.name, pc.depth
            FROM prereq_chain pc
            JOIN concepts c ON c.id = pc.prerequisite_concept_id
            ORDER BY pc.depth
        """))
        rows = result.fetchall()
        print("\n\nPrerequisite chain for completing_the_square:")
        for row in rows:
            indent = "  " * row[1]
            print(f"  {indent}depth {row[1]}: {row[0]}")

    print("\n" + "=" * 60)


async def main():
    reset = "--reset" in sys.argv

    print("SunMath Data Seeding Script")
    print("=" * 40)

    # Check if data already exists
    if not reset and await check_data_exists():
        print("\nSeed data already exists. Use --reset to re-seed.")
        print("Running verification only...\n")
        ok = await verify_data()
        await verify_demo_scenarios()
        await async_engine.dispose()
        sys.exit(0 if ok else 1)

    if reset:
        print("\nResetting seed data...")
        await reset_data()

    # Load SQL files in order
    for filename in SQL_FILES_ORDER:
        filepath = DATA_DIR / filename
        if not filepath.exists():
            print(f"ERROR: {filepath} not found!")
            await async_engine.dispose()
            sys.exit(1)

        print(f"Loading {filename}...")
        await execute_sql_file(filepath)
        print(f"  Done.")

    print("\nAll seed data loaded successfully.\n")

    # Verify
    ok = await verify_data()
    await verify_demo_scenarios()

    await async_engine.dispose()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    asyncio.run(main())
