Phase 0: Backend + Database Setup — Implementation Plan

Overview

Set up the complete FastAPI backend scaffolding, PostgreSQL database with full GraphRAG schema, and all API endpoint stubs. No frontend, no Google Cloud.

Prerequisites

- Python 3.12 (/opt/homebrew/bin/python3.12)
- Docker 28.5.1 (for PostgreSQL)
- Git repo on feat/backend branch

---

Step 1: Project Scaffolding + Virtual Environment

Create directory structure:
sunmath/
├── backend/
│ ├── app/
│ │ ├── **init**.py
│ │ ├── main.py
│ │ ├── config.py
│ │ ├── api/
│ │ │ ├── **init**.py
│ │ │ ├── deps.py
│ │ │ └── v1/
│ │ │ ├── **init**.py
│ │ │ ├── router.py
│ │ │ ├── problems.py
│ │ │ ├── grading.py
│ │ │ ├── students.py
│ │ │ ├── admin.py
│ │ │ └── benchmark.py
│ │ ├── services/
│ │ │ ├── **init**.py
│ │ │ ├── graphrag.py
│ │ │ ├── grading_engine.py
│ │ │ ├── similarity.py
│ │ │ ├── diagnosis.py
│ │ │ ├── sympy_engine.py
│ │ │ └── llm_router.py
│ │ ├── models/
│ │ │ ├── **init**.py
│ │ │ ├── base.py
│ │ │ ├── nodes.py
│ │ │ ├── edges.py
│ │ │ └── history.py
│ │ └── schemas/
│ │ ├── **init**.py
│ │ ├── problem.py
│ │ ├── grading.py
│ │ ├── student.py
│ │ ├── admin.py
│ │ └── benchmark.py
│ ├── scripts/
│ │ └── seed_admin_settings.py
│ ├── tests/
│ │ └── **init**.py
│ ├── requirements.txt
│ ├── Dockerfile
│ └── .env.example
├── data/
│ └── schema.sql
└── docker-compose.yml

Actions:

1.  Create all directories and **init**.py files
2.  Create Python 3.12 venv at backend/.venv
3.  Create requirements.txt with: fastapi, uvicorn[standard], mangum, sqlalchemy[asyncio], asyncpg, alembic, sympy, pydantic, pydantic-settings, python-dotenv,
    httpx, python-multipart
4.  pip install -r requirements.txt
5.  Add .gitignore (Python, .env, .venv, pycache)
6.  Create .env.example and backend/.env

---

Step 2: Docker Compose + PostgreSQL

Files: docker-compose.yml

- PostgreSQL 16 Alpine container (sunmath-postgres)
- Credentials: sunmath/sunmath DB: sunmath
- Port 5432
- Named volume for persistence
- Healthcheck configured

Actions:

1.  Create docker-compose.yml
2.  docker-compose up -d
3.  Verify with docker exec ... psql

---

Step 3: Configuration + FastAPI App Skeleton

Files: app/config.py, app/main.py

- config.py: Pydantic BaseSettings reading from .env — database_url, LLM API keys, debug, cors_origins
- main.py: FastAPI app with CORS, health check, v1 router, Mangum handler, lifespan for DB connection test

Verification: uvicorn app.main:app --reload → GET /health returns 200

---

Step 4: SQLAlchemy Models (Full Schema)

Files: app/models/base.py, nodes.py, edges.py, history.py, **init**.py

Node tables (nodes.py):

- Unit — id, name, description, grade_level, timestamps
- Concept — id, name (unique), description, category, timestamps
- Question — id, content, correct_answer, expected_form (enum: factored/expanded/simplified/numeric/proof), target_grade, grading_hints, timestamps
- Student — id, name, grade_level, timestamps
- Relationships via secondary tables

Edge tables (edges.py):

- UnitConcept — composite PK (unit_id, concept_id)
- ConceptPrerequisite — composite PK (concept_id, prerequisite_concept_id)
- ConceptRelation — composite PK + relation_type
- QuestionEvaluates — composite PK (question_id, concept_id)
- QuestionUnits — composite PK (question_id, unit_id)
- QuestionRequires — composite PK (question_id, concept_id)

History + support tables (history.py):

- StudentAnswer — id, student_id, question_id, submitted_answer, is_correct, judged_by (enum), reasoning, submitted_at + indexes
- StudentConceptMastery — composite PK (student_id, concept_id), mastery_level (float), last_updated
- WrongAnswerWarehouse — id, student_id, question_id, answer_id, status (enum: active/resolved/archived), retry_count, timestamps + indexes
- AnswerCache — id, question_id, submitted_answer_hash, is_correct, judged_by, reasoning, cached_at + unique index on (question_id, hash)
- AdminSettings — key (PK), value, description, updated_at
- StudentDiagnosis — id, student_id, diagnosis_data (JSONB), generated_at

SQLAlchemy 2.0 patterns: Mapped[], mapped_column(), async_sessionmaker, expire_on_commit=False

---

Step 5: Database Session + Dependencies

Files: app/api/deps.py

- create_async_engine with pool_pre_ping, pool_size=5
- async_sessionmaker with expire_on_commit=False
- get_db() dependency: yields session, auto-commit on success, rollback on error

---

Step 6: Alembic Async Migrations

Actions:

1.  alembic init alembic (from backend dir)
2.  Edit alembic/env.py for async: import models via app.models.Base, use async_engine_from_config, override URL from settings
3.  Edit alembic.ini to remove hardcoded URL
4.  alembic revision --autogenerate -m "initial schema"
5.  alembic upgrade head
6.  Verify all 16 tables exist in PostgreSQL

---

Step 7: Pydantic Schemas (Request/Response)

Files: app/schemas/problem.py, grading.py, student.py, admin.py, benchmark.py, **init**.py

Key schemas:

- ProblemCreate, ProblemResponse, SimilarProblemResponse, DuplicateCheckResponse
- GradeRequest, GradeResponse, CacheStatsResponse
- DiagnosisResponse (core_weaknesses, prerequisite_chains, learning_path, recommended_problems)
- SettingResponse, SettingUpdate, SettingsListResponse
- BenchmarkMatrixResponse, BenchmarkRecommendationResponse

All response schemas use ConfigDict(from_attributes=True).

---

Step 8: API Route Stubs (All 13 Endpoints)

Files: app/api/v1/problems.py, grading.py, students.py, admin.py, benchmark.py, router.py
┌────────┬─────────────────────────────────────┬──────────────────────────┐
│ Method │ Path │ Status │
├────────┼─────────────────────────────────────┼──────────────────────────┤
│ POST │ /api/v1/problems │ Stub │
├────────┼─────────────────────────────────────┼──────────────────────────┤
│ GET │ /api/v1/problems/{id} │ Stub │
├────────┼─────────────────────────────────────┼──────────────────────────┤
│ GET │ /api/v1/problems/{id}/similar │ Stub │
├────────┼─────────────────────────────────────┼──────────────────────────┤
│ POST │ /api/v1/grading/grade │ Stub │
├────────┼─────────────────────────────────────┼──────────────────────────┤
│ GET │ /api/v1/grading/cache/stats │ Stub │
├────────┼─────────────────────────────────────┼──────────────────────────┤
│ GET │ /api/v1/students/{id}/diagnosis │ Stub │
├────────┼─────────────────────────────────────┼──────────────────────────┤
│ GET │ /api/v1/students/{id}/wrong-answers │ Stub │
├────────┼─────────────────────────────────────┼──────────────────────────┤
│ GET │ /api/v1/students/{id}/mastery │ Stub │
├────────┼─────────────────────────────────────┼──────────────────────────┤
│ GET │ /api/v1/students/{id}/learning-path │ Stub │
├────────┼─────────────────────────────────────┼──────────────────────────┤
│ GET │ /api/v1/admin/settings │ Working (real DB query) │
├────────┼─────────────────────────────────────┼──────────────────────────┤
│ PUT │ /api/v1/admin/settings/{key} │ Working (real DB update) │
├────────┼─────────────────────────────────────┼──────────────────────────┤
│ GET │ /api/v1/benchmark/matrix │ Stub │
├────────┼─────────────────────────────────────┼──────────────────────────┤
│ GET │ /api/v1/benchmark/recommendations │ Stub │
└────────┴─────────────────────────────────────┴──────────────────────────┘
Admin endpoints will be fully functional (read/write to DB). All others return stub data.

router.py combines all sub-routers under /api/v1.

---

Step 9: Service Layer Stubs

Files: app/services/graphrag.py, grading_engine.py, similarity.py, diagnosis.py, sympy_engine.py, llm_router.py, **init**.py

Each service as a class with method signatures and docstrings. sympy_engine.py includes a basic working check_equivalence() using SymPy. All others are TODO
stubs for Phase 2.

---

Step 10: Seed Admin Settings + Reference SQL

Files: scripts/seed_admin_settings.py, data/schema.sql

- Seed script inserts: similarity_threshold=0.85, confidence_threshold=0.90, duplicate_detection_mode=warn
- schema.sql is reference documentation of the full schema (not used by Alembic, just for inspection)

---

Step 11: Dockerfile (Lambda-ready)

File: backend/Dockerfile

- Base: public.ecr.aws/lambda/python:3.12
- Install deps, copy app, CMD app.main.handler

---

Verification

After completion, these should all pass:

# 1. PostgreSQL running

docker ps | grep sunmath-postgres

# 2. All 16 tables exist

docker exec sunmath-postgres psql -U sunmath -d sunmath -c "\dt"

# 3. Admin settings seeded

docker exec sunmath-postgres psql -U sunmath -d sunmath -c "SELECT \* FROM admin_settings;"

# 4. FastAPI starts clean

cd backend && source .venv/bin/activate && uvicorn app.main:app --reload

# 5. Health check

curl http://localhost:8000/health → {"status": "healthy", ...}

# 6. Admin settings API works

curl http://localhost:8000/api/v1/admin/settings → returns 3 settings

# 7. OpenAPI docs render

open http://localhost:8000/api/docs → all 13 endpoints visible

# 8. All stubs respond without errors

curl -X POST http://localhost:8000/api/v1/grading/grade \
 -H "Content-Type: application/json" \
 -d '{"student_id":1,"question_id":1,"submitted_answer":"x^2+2x+1"}'
