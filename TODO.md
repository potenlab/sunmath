# SunMath MVP 1 - To-Do List

> Track all tasks for MVP 1 delivery
> Created: 2026-03-05

---

## Legend

- `[ ]` Not started
- `[~]` In progress
- `[x]` Complete
- `[!]` Blocked
- **P0** = Must have for meeting | **P1** = Should have | **P2** = Nice to have

---

## Phase 0: Environment & Infrastructure Setup

### 0.1 Project Scaffolding
- [ ] **P0** — Create monorepo structure:
  ```
  sunmath/
  ├── backend/                 # FastAPI app
  │   ├── app/
  │   │   ├── main.py          # FastAPI app + Mangum handler
  │   │   ├── api/
  │   │   │   └── v1/
  │   │   │       ├── problems.py
  │   │   │       ├── grading.py
  │   │   │       ├── students.py
  │   │   │       ├── admin.py
  │   │   │       └── benchmark.py
  │   │   ├── services/        # Business logic
  │   │   │   ├── graphrag.py
  │   │   │   ├── grading_engine.py
  │   │   │   ├── similarity.py
  │   │   │   ├── diagnosis.py
  │   │   │   ├── sympy_engine.py
  │   │   │   └── llm_router.py
  │   │   ├── models/          # SQLAlchemy / Pydantic models
  │   │   ├── db/              # DB connection, migrations
  │   │   └── config.py        # Settings, env vars
  │   ├── tests/
  │   ├── requirements.txt
  │   └── Dockerfile           # For Lambda container image
  ├── frontend/                # Next.js app
  │   ├── src/
  │   │   ├── app/             # App Router pages
  │   │   │   ├── admin/
  │   │   │   ├── grading/
  │   │   │   ├── students/
  │   │   │   └── benchmark/
  │   │   ├── components/
  │   │   └── lib/             # API client, types
  │   ├── package.json
  │   └── next.config.js
  ├── data/                    # Sample data SQL/JSON
  │   ├── schema.sql
  │   ├── seed_units.sql
  │   ├── seed_concepts.sql
  │   ├── seed_problems.sql
  │   └── seed_students.sql
  └── infra/                   # AWS CDK or SAM templates
  ```
- [ ] **P0** — Initialize git repository

### 0.2 Backend Setup
- [ ] **P0** — Create Python virtual environment
- [ ] **P0** — Install core dependencies:
  - `fastapi`, `uvicorn`, `mangum` (Lambda adapter)
  - `sqlalchemy`, `asyncpg`, `alembic` (DB)
  - `sympy` (math engine)
  - `pydantic`, `pydantic-settings` (config/validation)
  - `httpx` (async HTTP for Maxima service + LLM calls)
- [ ] **P0** — Create FastAPI app skeleton with health check endpoint
- [ ] **P0** — Set up Mangum handler for Lambda deployment
- [ ] **P0** — Set up LLM API keys: Gemini, Claude, GPT-4o, DeepSeek, OpenAI (o1)
- [ ] **P0** — Verify local `uvicorn` dev server runs

### 0.3 Frontend Setup
- [ ] **P0** — Initialize Next.js project (App Router, TypeScript, Tailwind CSS)
- [ ] **P0** — Create basic layout: sidebar navigation + main content area
- [ ] **P0** — Set up API client (`fetch` wrapper or `axios`) pointing to FastAPI
- [ ] **P0** — Create placeholder pages: Admin, Grading, Students, Benchmark

### 0.4 Database Setup
- [ ] **P0** — Provision PostgreSQL (local Docker for dev, AWS RDS Aurora for prod)
- [ ] **P0** — Run schema creation SQL (all node tables, edge tables, history tables, indexes)
- [ ] **P0** — Insert `admin_settings` initial values (similarity_threshold: 0.85, confidence_threshold: 0.90)
- [ ] **P0** — Set up SQLAlchemy models matching the schema
- [ ] **P0** — Verify DB connection from FastAPI

### 0.5 Google Cloud Setup (for Task 2)
- [ ] **P0** — Google Cloud project created or selected
- [ ] **P0** — Vertex AI API enabled
- [ ] **P0** — Service account + authentication configured
- [ ] **P0** — Gemini model access verified

---

## Phase 1: Sample Data Preparation

### 1.1 Curriculum Graph Data
- [ ] **P0** — Create 15-20 units spanning elementary/middle/high school math
  - [ ] Elementary: fractions, simplification, basic operations
  - [ ] Middle school: factoring, expansion, quadratic equations, functions
  - [ ] High school: trigonometry, calculus, vectors, circle equations
- [ ] **P0** — Create 40-50 math concepts with descriptions and categories
- [ ] **P0** — Create 60-80 prerequisite relationships (concept → prerequisite concept)
  - Must include chains like: polynomial multiplication → multiplication formulas → completing the square
  - Must include chains like: angles → radian measure → trigonometric functions
- [ ] **P1** — Create 20-30 lateral association relationships (cross-unit concept links)

### 1.2 Problem Data
- [ ] **P0** — Create 30-40 problems (2-3 per unit) with full metadata:
  - `content` (problem text in LaTeX)
  - `correct_answer` (LaTeX)
  - `expected_form` (factored/expanded/simplified/numeric/proof/null)
  - `target_grade`
  - `grading_hints`
- [ ] **P0** — Link problems to evaluation concepts (`question_evaluates`)
- [ ] **P0** — Link problems to required concepts (`question_requires`)
- [ ] **P0** — Link problems to units (`question_units`)

### 1.3 Student Wrong Answer Data (for Demo 3)
- [ ] **P0** — Create 2-3 student profiles
- [ ] **P0** — Design Student A's wrong answers to show cross-unit pattern:
  - Quadratic inequality → wrong (needs factoring + completing the square)
  - Quadratic function vertex → wrong (needs completing the square)
  - Circle equation → wrong (needs completing the square)
  - Root cause: multiplication formulas → completing the square chain
- [ ] **P1** — Design Student B's wrong answers to show different cross-unit pattern:
  - Trig function synthesis → wrong (needs radian measure)
  - Vector dot product → wrong (needs radian measure)
  - Root cause: radian measure
- [ ] **P0** — Insert student_answers records
- [ ] **P0** — Calculate and insert student_concept_mastery records
- [ ] **P0** — Insert wrong_answer_warehouse records

### 1.4 LLM Benchmark Data (for Task 3)
- [ ] **P0** — Prepare 60-80 math problems across 6 subjects:
  - [ ] Algebra (equations, inequalities): 10 problems (Easy 3 / Med 4 / Hard 3)
  - [ ] Factoring/Expansion: 10 problems (Easy 3 / Med 4 / Hard 3)
  - [ ] Geometry (shapes, proofs): 10 problems (Easy 3 / Med 4 / Hard 3)
  - [ ] Calculus: 10 problems (Easy 3 / Med 4 / Hard 3)
  - [ ] Probability/Statistics: 10 problems (Easy 3 / Med 4 / Hard 3)
  - [ ] Mixed/Descriptive: 10 problems (Med 5 / Hard 5)
- [ ] **P0** — Standardize format: problem text, LaTeX answer, concepts, difficulty

### 1.5 Handwriting OCR Data (for Task 2)
- [ ] **P0** — Collect 50+ handwriting formula images
  - [ ] Clean handwriting samples
  - [ ] Messy handwriting samples
  - [ ] Unusual notation samples
  - [ ] Formula types: fractions, radicals, exponents, integrals, matrices
- [ ] **P0** — Create ground truth LaTeX for each image
- [ ] **P1** — Prepare 100-200 image+LaTeX pairs for LoRA training set

### 1.6 Data Loading
- [ ] **P0** — Write Python script to load all sample data into PostgreSQL
- [ ] **P0** — Run data loading script and verify data integrity
- [ ] **P0** — Test core GraphRAG queries against loaded data

---

## Phase 2: Task 1 — GraphRAG Core Logic (Backend)

### 2.1 Concept Extraction Service (`services/graphrag.py`)
- [ ] **P0** — Build LLM prompt to extract evaluation_concepts from problem text
- [ ] **P0** — Build LLM prompt to extract required_concepts from problem text
- [ ] **P0** — Build LLM prompt to extract expected_form and grading_hints
- [ ] **P0** — Parse LLM output → map to existing concept IDs in DB
- [ ] **P1** — Handle new concepts not yet in DB (create or flag for review)

### 2.2 Duplicate Detection — Demo 1 (`services/similarity.py` + `api/v1/problems.py`)
- [ ] **P0** — `POST /api/v1/problems` — Register problem endpoint
- [ ] **P0** — Implement Jaccard similarity calculation between two problems
- [ ] **P0** — Implement "compare new problem vs all existing problems" query
- [ ] **P0** — Implement threshold check against `admin_settings.similarity_threshold`
- [ ] **P0** — Return similar problem list with: score, shared concepts, differences
- [ ] **P0** — Support block mode and warn mode
- [ ] **P0** — `PUT /api/v1/admin/settings/similarity_threshold` — Admin threshold update
- [ ] **P0** — Test: register similar problem → warning triggered
- [ ] **P0** — Test: register unrelated problem → no warning
- [ ] **P0** — Test: change threshold → behavior changes accordingly

### 2.3 Intent-Based Grading (Demo 2)
- [ ] **P0** — Implement GraphRAG metadata lookup for a problem:
  - evaluation_concepts, required_concepts, expected_form, target_grade, grading_hints
- [ ] **P0** — Implement grading branch logic:
  - expected_form exists → equivalence + form check
  - expected_form null → equivalence only
  - proof/descriptive → LLM with full context
- [ ] **P0** — Integrate SymPy equivalence check (Stage 1)
- [ ] **P1** — Implement LLM fallback when SymPy can't resolve (Stage 2, replaces Maxima for MVP)
- [ ] **P0** — Implement expected_form validation (is answer in factored/expanded/numeric form?)
- [ ] **P0** — Implement LLM grading with context (evaluation_concepts + grading_hints)
- [ ] **P0** — Test: same answer, different problem intents → different grading results
- [ ] **P0** — Test: proof problem → LLM judges correctly with context

### 2.4 Precedent Caching
- [ ] **P0** — On grading completion → save to `answer_cache`
- [ ] **P0** — On grading request → check `answer_cache` first
- [ ] **P0** — Record `judged_by` (sympy/maxima/llm/graphrag+sympy)
- [ ] **P0** — Test: first grading uses engine, second grading uses cache

### 2.5 Wrong Answer Analysis (Demo 3)
- [ ] **P0** — Query: collect all concepts linked to student's wrong answers
- [ ] **P0** — Implement concept frequency analysis
- [ ] **P0** — Implement prerequisite graph backtracking (find root causes)
- [ ] **P0** — Implement cross-unit impact analysis (weak concept → affected units)
- [ ] **P0** — Generate diagnosis report:
  - Core weakness + mastery level
  - Prerequisite chain
  - Affected units
  - Recommended learning path
  - Recommended practice problems
- [ ] **P0** — Test: Student A's 3 wrong answers → root cause is "completing the square"
- [ ] **P1** — Test: Student B's 2 wrong answers → root cause is "radian measure"

### 2.6 Wrong Answer Warehouse (Dynamic Management)
- [ ] **P1** — State transitions: active → resolved → archived
- [ ] **P1** — When student re-solves correctly → status = resolved, preserve history
- [ ] **P1** — Retry count tracking
- [ ] **P1** — Learning history preserved (never deleted, only state transitions)

---

## Phase 3: Task 2 — LoRA Fine-Tuning Test

### 3.1 Baseline Measurement
- [ ] **P0** — Run Gemini Vision OCR on all 50+ handwriting samples
- [ ] **P0** — Calculate baseline accuracy (correct LaTeX / total images)
- [ ] **P0** — Categorize errors by formula type
- [ ] **P0** — Document error patterns

### 3.2 LoRA Fine-Tuning
- [ ] **P0** — Research: Is Gemini LoRA fine-tuning available on Vertex AI?
  - If YES:
    - [ ] **P0** — Prepare training data in required format
    - [ ] **P0** — Execute LoRA fine-tuning
    - [ ] **P0** — Measure post-tuning accuracy
  - If NO:
    - [ ] **P0** — Document why not available
    - [ ] **P1** — Test alternative: PaLI or Donut model
    - [ ] **P1** — Measure alternative model accuracy
- [ ] **P0** — Test programmatic fine-tuning via Vertex AI SDK
- [ ] **P0** — Test API-based model management (deploy, switch, delete per-student models)

### 3.3 Results Report
- [ ] **P0** — Fill in results table:

| Item | Result |
|------|--------|
| Baseline accuracy (before LoRA) | _% |
| Accuracy after LoRA | _% |
| Accuracy improvement | _% |
| Fine-tuning cost per student | $_ |
| Fine-tuning time per student | _ min |
| Minimum required data volume | _ images |
| Programmatic fine-tuning feasibility | Y/N |
| API-based per-student model management | Y/N |

- [ ] **P0** — Write cost-effectiveness analysis (scaling to 100+ students)
- [ ] **P0** — Write recommendation: proceed with LoRA or not

---

## Phase 4: Task 3 — LLM Benchmark + Cross-Verification

### 4.1 Benchmark Execution
- [ ] **P0** — Write benchmark harness script:
  - Loops through models × problems
  - Records: correct/incorrect, confidence, latency, cost
  - Saves results to CSV/JSON
- [ ] **P0** — Design standardized prompt (problem → solution + answer + confidence)
- [ ] **P0** — Run benchmark for all 7 models:
  - [ ] DeepSeek-V3
  - [ ] Claude Sonnet
  - [ ] GPT-4o
  - [ ] Gemini 2.5 Pro
  - [ ] o1/o3
  - [ ] DeepSeek-R1
  - [ ] Qwen 2.5 Math
- [ ] **P0** — Handle API errors, rate limits, timeouts gracefully

### 4.2 Results Analysis
- [ ] **P0** — Generate Model × Subject accuracy matrix
- [ ] **P0** — Calculate cost per problem for each model
- [ ] **P0** — Produce "optimal model per subject" recommendation table
- [ ] **P0** — Identify which subjects need reasoning models (likely geometry)
- [ ] **P1** — Visualize results (charts/graphs for presentation)

### 4.3 Cross-Verification (Voting)
- [ ] **P0** — Implement confidence score extraction from each model's response
- [ ] **P0** — Implement voting flow:
  ```
  Primary model → confidence >= threshold → accept
                → confidence < threshold → secondary model
                → agree → accept
                → disagree → tertiary model → majority vote
                → all differ → flag manual review
  ```
- [ ] **P0** — Run voting test on full benchmark set
- [ ] **P0** — Compare: single model accuracy vs voting accuracy
- [ ] **P0** — Measure: cost increase from voting
- [ ] **P1** — Test multiple threshold values to find optimal

### 4.4 SymPy/Maxima Verification Layer
- [ ] **P1** — Implement: LLM answer → parse LaTeX → SymPy verify against correct answer
- [ ] **P1** — Measure accuracy improvement from adding verification
- [ ] **P1** — Measure additional latency
- [ ] **P1** — Identify which problem types benefit most

---

## Phase 5: Frontend (Next.js)

### 5.1 Admin Panel (`/admin`)
- [ ] **P0** — Settings page:
  - Similarity threshold slider (0.0–1.0) + mode toggle (block/warn)
  - Confidence threshold slider
  - Save button → `PUT /api/v1/admin/settings/{key}`
- [ ] **P0** — Problem registration page:
  - Problem text input (LaTeX support)
  - Answer input, expected_form dropdown, target_grade, grading_hints
  - Submit → `POST /api/v1/problems`
  - Display duplicate warning modal with similar problem list when triggered

### 5.2 Grading View (`/grading`)
- [ ] **P0** — Grade submission form:
  - Select problem (dropdown or search)
  - Enter student answer (text input, LaTeX)
  - Submit → `POST /api/v1/grading/grade`
- [ ] **P0** — Result display:
  - Correct/Wrong badge
  - Judged by (sympy/maxima/llm/cache)
  - Reasoning text
  - Problem metadata shown (expected_form, grading_hints)
- [ ] **P1** — Cache statistics panel → `GET /api/v1/grading/cache/stats`

### 5.3 Student Diagnosis Dashboard (`/students/{id}`)
- [ ] **P0** — Wrong answer list with status (active/resolved/archived)
- [ ] **P0** — "Run Analysis" button → `GET /api/v1/students/{id}/diagnosis`
- [ ] **P0** — Diagnosis result display:
  - Concept frequency bar chart
  - Root cause tracing visualization (prerequisite chain)
  - Affected units list
  - Recommended learning path (numbered steps)
  - Recommended practice problems
- [ ] **P0** — Side-by-side: naive analysis vs GraphRAG analysis
- [ ] **P1** — Concept mastery heatmap → `GET /api/v1/students/{id}/mastery`

### 5.4 Benchmark Dashboard (`/benchmark`)
- [ ] **P0** — Model × Subject accuracy matrix table
- [ ] **P0** — Optimal model per subject recommendation cards
- [ ] **P0** — Voting accuracy improvement comparison
- [ ] **P1** — Interactive charts (bar chart per subject, cost comparison)

### 5.5 LoRA Results Page (`/benchmark/lora`)
- [ ] **P0** — Before/after accuracy comparison display
- [ ] **P0** — Cost and feasibility summary table
- [ ] **P0** — Recommendation statement

---

## Phase 6: End-to-End Demo Flows

### 6.1 Demo 1: Duplicate Detection (via Admin Panel UI)
- [ ] **P0** — Walkthrough:
  1. Open Admin → show threshold = 0.85, mode = warn
  2. Register Problem A "Factor x²+5x+6" → success toast
  3. Register Problem B "Factor x²+7x+12" → warning modal (similarity 0.92)
     - Shows shared concepts, differences
     - Click "Register" or "Cancel"
  4. Register Problem C "Find circumscribed circle radius" → success (similarity 0.05)
  5. Change threshold to 0.95 in settings
  6. Re-register Problem B → passes without warning
- [ ] **P0** — Verify all API calls work end-to-end

### 6.2 Demo 2: Intent-Based Grading (via Grading View UI)
- [ ] **P0** — Walkthrough:
  1. Grade `x²+2x+1` on factoring problem → WRONG (expected_form = "factored")
  2. Grade `x²+2x+1` on expansion problem → CORRECT (expected_form = null)
  3. Grade `√25` on distance problem → WRONG (expected numeric); `5` → CORRECT
  4. Submit proof answer → LLM judges with context → show reasoning
- [ ] **P0** — Show metadata in UI driving the grading (no code changes needed)

### 6.3 Demo 3: Cross-Unit Wrong Answer Analysis (via Student Dashboard UI)
- [ ] **P0** — Walkthrough:
  1. Open Student A dashboard → show wrong answers across 3 units
  2. Click "Run Analysis"
  3. Results appear:
     - Concept frequency chart
     - Root cause trace: completing the square ← multiplication formulas
     - Affected units list
     - Learning path: Step 1 → Step 2 → Step 3
     - Recommended problems
  4. Side-by-side with naive "3 units are weak" analysis
- [ ] **P0** — Verify diagnosis API returns correct root cause

### 6.4 Demo 4: LLM Benchmark + LoRA (via Benchmark Dashboard)
- [ ] **P0** — Show Model × Subject accuracy matrix
- [ ] **P0** — Show optimal model recommendations
- [ ] **P0** — Show voting accuracy improvement
- [ ] **P0** — Show LoRA before/after results

---

## Phase 7: Deployment & Pre-Meeting

### 7.1 AWS Deployment (Lambda + RDS only)
- [ ] **P0** — Deploy FastAPI to Lambda (container image via ECR)
- [ ] **P0** — Set up API Gateway → Lambda
- [ ] **P0** — Deploy PostgreSQL on RDS Aurora
- [ ] **P0** — Deploy Next.js frontend (Vercel or Amplify)
- [ ] **P0** — Environment variables configured (DB connection, API keys)
- [ ] **P0** — Verify end-to-end: frontend → API Gateway → Lambda → RDS

### 7.2 Internal Review
- [ ] **P0** — Run all 4 demos end-to-end on deployed environment
- [ ] **P0** — Internal meeting: review all demos, assign speaking roles
- [ ] **P0** — Prepare for Q&A (anticipated client questions)
- [ ] **P0** — Ensure all API keys work and have sufficient quota
- [ ] **P0** — Test on meeting room network (avoid firewall issues)

### 7.3 Presentation Materials
- [ ] **P0** — All demo flows tested and stable on production URL
- [ ] **P1** — Backup screenshots/recordings in case of live demo failure
- [ ] **P1** — Architecture diagram ready to show

### 7.4 Key Messages Rehearsal
- [ ] **P0** — Cost reduction: "Maxima replaces Wolfram, caching reduces API to near-zero"
- [ ] **P0** — Intelligence: "We grade based on problem intent, not just math equivalence"
- [ ] **P0** — Root cause: "We find WHY students fail, not just WHERE"
- [ ] **P0** — Reliability: "Subject-specific LLM routing + cross-verification"
- [ ] **P0** — Scalability: "Metadata-driven — no code changes for new problem types"
- [ ] **P0** — Production-ready: "FastAPI + Next.js + AWS — ready to scale"

---

## Dependency Graph

```
Phase 0 (Setup: Backend + Frontend + DB + Maxima + GCP)
    │
    ▼
Phase 1 (Sample Data Preparation)
    │
    ├──────────────┬──────────────┐
    ▼              ▼              ▼
Phase 2        Phase 3        Phase 4
(GraphRAG      (LoRA          (LLM Benchmark
 Backend)       Test)          + Voting)
    │              │              │
    ▼              │              │
Phase 5            │              │
(Frontend)         │              │
    │              │              │
    └──────────────┴──────────────┘
                   │
                   ▼
             Phase 6 (E2E Demo Flows)
                   │
                   ▼
             Phase 7 (Deploy + Meeting Prep)
```

**Parallelizable**:
- Phases 2, 3, 4 can run simultaneously (different team members)
- Phase 5 (Frontend) can start once Phase 2 API routes are defined (even with mock data)
- Phase 3 (LoRA) and Phase 4 (LLM Benchmark) are fully independent

---

## Team Assignment (Suggested)

| Person | Phases | Focus |
|--------|--------|-------|
| **Person A** | 0.1, 0.4, 1.1-1.3, 1.6, 2, 6.1-6.3 | Backend: GraphRAG schema, APIs, core logic, demo flows |
| **Person B** | 0.2 (partial), 1.4, 4, 5.4, 6.4 | Backend: LLM benchmark, voting, benchmark UI |
| **Person C** | 0.3, 0.6, 1.5, 3, 5.5 | LoRA: Vertex AI setup, fine-tuning test, results |
| **Person A or B** | 0.3 (frontend), 5.1-5.3, 7.1 | Frontend: Next.js pages, deployment |
| **All** | 7.2-7.4 | Pre-meeting review and rehearsal |

---

*Document created: 2026-03-05*
*Updated: 2026-03-05 — Added FastAPI + Next.js + Lambda stack*
