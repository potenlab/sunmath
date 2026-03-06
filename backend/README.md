# SunMath Backend

FastAPI backend for SunMath — a GraphRAG-powered math education platform with intent-based grading, concept extraction, and cross-unit student diagnosis.

## Tech Stack

- **Python 3.12**
- **FastAPI** — async web framework
- **SQLAlchemy 2.0** (async) + **asyncpg** — PostgreSQL ORM
- **Alembic** — database migrations
- **SymPy** — symbolic math equivalence checking
- **httpx** — async HTTP client for LLM API calls (OpenRouter)
- **Mangum** — AWS Lambda ASGI adapter

## Prerequisites

- Python 3.12+
- PostgreSQL 16+ (via Docker or local install)
- An OpenRouter API key (optional, for LLM grading and concept extraction)

## Quick Start

```bash
# 1. Create and activate virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start PostgreSQL (Docker)
docker run -d --name sunmath-postgres \
  -e POSTGRES_USER=sunmath \
  -e POSTGRES_PASSWORD=sunmath \
  -e POSTGRES_DB=sunmath \
  -p 5433:5432 \
  postgres:16

# 4. Configure environment
cp .env.example .env
# Edit .env with your settings (see Environment Variables below)

# 5. Run database migrations
alembic upgrade head

# 6. Seed data
python scripts/seed_admin_settings.py
python scripts/seed_all.py

# 7. Start dev server
uvicorn app.main:app --reload --port 8000
```

The API is now available at `http://localhost:8000`. Swagger docs at `http://localhost:8000/api/docs`.

## Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | `postgresql+asyncpg://sunmath:sunmath@localhost:5433/sunmath` | PostgreSQL connection string |
| `DEBUG` | No | `true` | Enable debug mode |
| `CORS_ORIGINS` | No | `["http://localhost:3000","http://localhost:5173"]` | Allowed CORS origins (JSON array) |
| `LLM_API_KEY` | No | `""` | OpenRouter API key for LLM grading/extraction |
| `LLM_MODEL` | No | `""` | Model ID on OpenRouter (e.g. `google/gemini-2.5-flash`) |
| `LLM_BASE_URL` | No | `https://openrouter.ai/api/v1` | LLM API base URL |
| `LLM_TIMEOUT` | No | `30.0` | LLM request timeout in seconds |

> **Note:** Without `LLM_API_KEY`, grading falls back to heuristic string comparison and concept extraction is disabled. All other features work normally.

## Database

### PostgreSQL Setup (Docker)

```bash
# Start
docker run -d --name sunmath-postgres \
  -e POSTGRES_USER=sunmath \
  -e POSTGRES_PASSWORD=sunmath \
  -e POSTGRES_DB=sunmath \
  -p 5433:5432 \
  postgres:16

# Stop / Start
docker stop sunmath-postgres
docker start sunmath-postgres

# Connect via psql
psql -h localhost -p 5433 -U sunmath -d sunmath
```

Port `5433` is used to avoid conflicts with a local PostgreSQL instance on the default port `5432`.

### Migrations (Alembic)

All commands run from the `backend/` directory with the virtualenv activated.

```bash
# Apply all pending migrations
alembic upgrade head

# Check current migration version
alembic current

# View migration history
alembic history

# Roll back one migration
alembic downgrade -1

# Roll back everything
alembic downgrade base

# Create a new migration (after model changes)
alembic revision --autogenerate -m "description of changes"
```

The initial migration creates 16 tables: 4 node tables, 6 edge tables, and 6 history/support tables.

### Seeding

Two seed scripts populate the database with sample data:

```bash
# 1. Seed admin settings (similarity threshold, confidence threshold, duplicate mode)
python scripts/seed_admin_settings.py

# 2. Seed all sample data (units, concepts, problems, students)
python scripts/seed_all.py
```

`seed_all.py` loads SQL files from `data/` in dependency order:
1. `seed_units.sql` — 18 units (elementary through high school)
2. `seed_concepts.sql` — 53 concepts + prerequisites + lateral relations
3. `seed_problems.sql` — 37 problems with concept/unit edges
4. `seed_students.sql` — 3 students with answer history and mastery data

To **re-seed** (clear and reload all data, preserving admin settings):

```bash
python scripts/seed_all.py --reset
```

## API Endpoints

All endpoints are under `/api/v1/`. Swagger docs available at `/api/docs`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/api/v1/admin/settings` | List all admin settings |
| `PUT` | `/api/v1/admin/settings/{key}` | Update an admin setting |
| `POST` | `/api/v1/problems` | Register a problem (with duplicate detection) |
| `GET` | `/api/v1/problems/{id}` | Get problem by ID |
| `GET` | `/api/v1/problems/{id}/similar` | Find similar problems |
| `POST` | `/api/v1/grading/grade` | Grade a student answer |
| `GET` | `/api/v1/grading/cache/stats` | Cache statistics |
| `GET` | `/api/v1/students` | List students |
| `GET` | `/api/v1/students/{id}` | Get student by ID |
| `GET` | `/api/v1/students/{id}/diagnosis` | Run wrong-answer diagnosis |
| `GET` | `/api/v1/students/{id}/mastery` | Get concept mastery data |
| `POST` | `/api/v1/benchmark/run` | Run LLM benchmark |
| `GET` | `/api/v1/benchmark/results` | Get benchmark results |

## Project Structure

```
backend/
├── alembic/                  # Database migrations
│   ├── env.py                #   Async migration environment
│   └── versions/             #   Migration files
├── app/
│   ├── main.py               # FastAPI app + Mangum handler
│   ├── config.py             # Pydantic settings (reads .env)
│   ├── api/
│   │   ├── deps.py           #   DB session dependency
│   │   └── v1/
│   │       ├── router.py     #   V1 router aggregator
│   │       ├── admin.py      #   Admin settings endpoints
│   │       ├── problems.py   #   Problem registration + similarity
│   │       ├── grading.py    #   Answer grading
│   │       ├── students.py   #   Student profiles + diagnosis
│   │       └── benchmark.py  #   LLM benchmark
│   ├── models/
│   │   ├── base.py           #   SQLAlchemy declarative base
│   │   ├── nodes.py          #   Unit, Concept, Question, Student
│   │   ├── edges.py          #   Relationship tables (6)
│   │   └── history.py        #   AnswerCache, StudentAnswer, etc.
│   ├── schemas/              # Pydantic request/response schemas
│   └── services/
│       ├── grading_engine.py #   Orchestrates SymPy → LLM → cache
│       ├── graphrag.py       #   Knowledge graph queries
│       ├── llm_router.py     #   OpenRouter LLM integration
│       ├── sympy_engine.py   #   Symbolic math checking
│       ├── similarity.py     #   Jaccard similarity for duplicates
│       └── diagnosis.py      #   Cross-unit wrong-answer analysis
├── scripts/
│   ├── seed_admin_settings.py
│   └── seed_all.py
├── tests/
├── .env.example
├── alembic.ini
├── requirements.txt
└── Dockerfile                # AWS Lambda container image
```

## Deployment (AWS Lambda)

The app is packaged as a Docker container for AWS Lambda:

```bash
docker build -t sunmath-backend .
```

The Dockerfile uses `public.ecr.aws/lambda/python:3.12` as the base image and sets the handler to `app.main.handler` (Mangum).
