# SunMath MVP 1 - Product Requirements Document

> Version: 1.1
> Created: 2026-03-05
> Updated: 2026-03-05
> Status: Draft

---

## 1. Executive Summary

### 1.1 Product Vision
SunMath is an AI-powered math learning platform for SunMath Academy (Daechi-dong). It automates grading, detects duplicate problems, and provides personalized learning diagnostics by understanding *what* a problem is testing — not just whether the answer is mathematically correct.

### 1.2 MVP 1 Scope
MVP 1 covers **3 deliverables** to demonstrate technical feasibility at the client meeting:

| # | Deliverable | Purpose |
|---|-------------|---------|
| 1 | GraphRAG Schema + MVP Demo | Answer client questions 1, 3, 4 (duplicate detection, intent-based grading, wrong answer analysis) |
| 2 | Gemini + LoRA Fine-Tuning Test | Prove per-student handwriting OCR adaptation is feasible and cost-effective |
| 3 | LLM Subject Benchmark + Cross-Verification | Show which LLMs are best for which math subjects + voting improves accuracy |

### 1.3 Success Criteria
- Client sees: **"This team can build what we need"**
- All 3 demos run end-to-end without manual intervention
- Concrete numbers for accuracy, cost, and feasibility in deliverables 2 and 3

---

## 2. Problem Statement

### 2.1 Client Pain Points
1. **No intelligent duplicate detection** — Changing one number creates a "new" problem. No way to detect conceptual similarity.
2. **Grading ignores problem intent** — `(x+1)²` and `x²+2x+1` are mathematically equivalent, but one is wrong if the problem asks for factoring.
3. **Shallow wrong answer analysis** — Current systems say "weak in geometry" instead of finding the root cause (e.g., "completing the square" is the actual gap).
4. **Handwriting OCR accuracy** — Student handwriting varies wildly; generic OCR isn't enough.
5. **LLM non-determinism** — Single LLM grading is unreliable; need verification mechanisms.

### 2.2 Why These 3 Tasks for MVP 1
- **Task 1 (GraphRAG)** addresses pain points 1, 2, 3 — the core intelligence layer
- **Task 2 (LoRA)** addresses pain point 4 — the input accuracy layer
- **Task 3 (LLM Benchmark)** addresses pain point 5 — the reliability layer

---

## 3. Target Users

| User | Role | Key Needs |
|------|------|-----------|
| Academy Admin | Manages problem bank, sets grading rules | Duplicate detection thresholds, problem registration, grading configuration |
| Teacher | Reviews grading results, tracks student progress | Wrong answer analysis reports, learning path recommendations |
| Student | Takes tests, reviews wrong answers | Personalized wrong answer notebook, recommended practice problems |
| System (Automated) | Runs grading pipeline | OCR → equivalence check → intent validation → result caching |

---

## 4. Functional Requirements

### 4.1 Task 1: GraphRAG Schema + MVP Demo

#### FR-1.1: Problem Registration with Duplicate Detection
**Description**: When a new problem is registered, the system extracts its assessment concepts and required concepts via LLM, then compares against all existing problems using Jaccard similarity on the concept graph.

**Acceptance Criteria**:
- [ ] LLM extracts `evaluation_concepts` and `required_concepts` from problem text
- [ ] System calculates Jaccard similarity against all existing problems
- [ ] If similarity >= admin threshold:
  - Block mode: reject registration, return similar problem list
  - Warn mode: show warning with similar problems, admin decides
- [ ] If similarity < threshold: register immediately
- [ ] Similar problem list shows: similarity score, shared concepts, differences
- [ ] Admin can change threshold (0.0–1.0) and mode (block/warn) at any time

**Demo Scenario**:
```
1. Register "Factor x²+5x+6" → success
2. Register "Factor x²+7x+12" → warning (similarity 0.92 > threshold 0.85)
3. Register "Find circumscribed circle radius" → success (similarity 0.05)
4. Change threshold to 0.95 → "Factor x²+7x+12" now passes
```

#### FR-1.2: Intent-Based Grading
**Description**: Grading considers not just mathematical equivalence but the problem's assessment intent. The same answer can be correct or wrong depending on what the problem is testing.

**Acceptance Criteria**:
- [ ] Each problem has metadata: `expected_form`, `target_grade`, `grading_hints`
- [ ] Grading flow branches automatically based on `expected_form`:
  - If `expected_form` exists → check equivalence AND form compliance
  - If `expected_form` is null → check equivalence only
  - If equivalence check is impossible (proofs, etc.) → pass context to LLM
- [ ] Same mathematical expression graded differently based on problem intent
- [ ] No code changes needed when new problem types are added — metadata-driven

**Demo Scenario**:
```
1. "Factor x²+2x+1" → student writes "x²+2x+1" → WRONG (not factored)
2. "Expand (x+1)²" → student writes "x²+2x+1" → CORRECT
3. Proof problem → LLM judges with evaluation_concepts + grading_hints
```

#### FR-1.3: Cross-Unit Wrong Answer Analysis
**Description**: When a student gets problems wrong across multiple units, the system traces through the concept prerequisite graph to find root causes instead of just listing weak units.

**Acceptance Criteria**:
- [ ] System collects all concepts linked to wrong answers (evaluation + required)
- [ ] Frequency analysis identifies repeatedly-failing concepts
- [ ] Prerequisite graph backtracking finds common root causes
- [ ] Diagnosis report shows:
  - Core weakness with mastery level
  - Prerequisite chain
  - All affected units
  - Recommended learning path (prerequisite-first order)
  - Recommended practice problems
- [ ] Report distinguishes root cause from symptoms (e.g., "completing the square is weak" not "geometry is weak")

**Demo Scenario**:
```
Student fails: quadratic inequality + quadratic function vertex + circle equation
→ Root cause: "completing the square" (mastery 0.3), not 3 separate weaknesses
→ Learning path: multiplication formulas → completing the square → affected units
```

#### FR-1.4: PostgreSQL Schema
**Acceptance Criteria**:
- [ ] All node tables created: `units`, `concepts`, `questions`, `students`
- [ ] All edge tables created: `unit_concepts`, `concept_prerequisites`, `concept_relations`, `question_evaluates`, `question_units`, `question_requires`
- [ ] Student history tables: `student_answers`, `student_concept_mastery`, `wrong_answer_warehouse`
- [ ] Support tables: `admin_settings`, `student_diagnosis`, `answer_cache`
- [ ] All indexes created for query performance
- [ ] Sample data loaded (15-20 units, 40-50 concepts, 30-40 problems, 2-3 students)

#### FR-1.5: Precedent Caching
**Acceptance Criteria**:
- [ ] First grading result saved to `answer_cache`
- [ ] Subsequent identical answer lookups return cached result (0 API calls)
- [ ] Cache records which engine judged (`sympy`, `maxima`, `llm`, `graphrag+sympy`)

---

### 4.2 Task 2: Gemini + LoRA Fine-Tuning Test

#### FR-2.1: Baseline OCR Measurement
**Acceptance Criteria**:
- [ ] 50+ handwriting formula images prepared (clean, messy, unusual notation)
- [ ] Formula types covered: fractions, radicals, exponents, integrals, matrices
- [ ] Gemini Vision baseline accuracy measured and documented
- [ ] Error patterns categorized by formula type

#### FR-2.2: LoRA Fine-Tuning Execution
**Acceptance Criteria**:
- [ ] Vertex AI environment configured and operational
- [ ] LoRA fine-tuning feasibility confirmed (Gemini or alternative model)
- [ ] Training data prepared: 100-200 handwriting image + LaTeX pairs
- [ ] Fine-tuning executed and post-tuning accuracy measured

#### FR-2.3: Results Analysis Report
**Acceptance Criteria**:
- [ ] Comparison table completed with all fields:
  - Baseline accuracy, post-LoRA accuracy, improvement delta
  - Cost per student, time per student, minimum data volume
  - Programmatic fine-tuning feasibility (Y/N)
  - API-based model management feasibility (Y/N)
- [ ] Cost-effectiveness analysis for scaling (100+ students)
- [ ] Clear recommendation: proceed with LoRA or not

---

### 4.3 Task 3: LLM Subject Benchmark + Cross-Verification

#### FR-3.1: Benchmark Test Suite
**Acceptance Criteria**:
- [ ] 60-80 math problems prepared across 6 subjects
  - Algebra, Factoring/Expansion, Geometry, Calculus, Probability/Statistics, Mixed
  - Each subject: 10 problems with difficulty distribution (Easy 3 / Med 4 / Hard 3)
- [ ] Standardized format: problem text, LaTeX answer, assessment concepts, difficulty

#### FR-3.2: Model Accuracy Matrix
**Acceptance Criteria**:
- [ ] 7 models tested: DeepSeek-V3, Claude Sonnet, GPT-4o, Gemini 2.5 Pro, o1/o3, DeepSeek-R1, Qwen 2.5 Math
- [ ] Per-model, per-subject accuracy recorded
- [ ] Cost per problem calculated for each model
- [ ] Latency measured for each model
- [ ] Optimal model recommendation per subject produced

#### FR-3.3: Cross-Verification (Voting) System
**Acceptance Criteria**:
- [ ] Confidence extraction working for all tested models
- [ ] Voting flow implemented:
  - confidence >= threshold → accept
  - confidence < threshold → second model
  - agreement → accept; disagreement → third model → majority vote
  - all differ → flag for manual review
- [ ] Voting accuracy vs single-model accuracy compared
- [ ] Cost increase from voting quantified
- [ ] Optimal confidence threshold identified

#### FR-3.4: SymPy/Maxima Verification Integration
**Acceptance Criteria**:
- [ ] Pipeline: LLM answer → parse → SymPy/Maxima verification → confirm/reject
- [ ] Accuracy improvement from adding verification measured
- [ ] Additional latency from verification measured
- [ ] Types that benefit most identified

---

## 5. Non-Functional Requirements

### 5.1 Performance
| Metric | Target |
|--------|--------|
| Grading latency (cached) | < 100ms |
| Grading latency (SymPy) | < 500ms |
| Grading latency (Maxima) | < 2s |
| Grading latency (LLM fallback) | < 10s |
| Duplicate detection query | < 3s for 1000 problems |
| Wrong answer analysis | < 5s per student |

### 5.2 Accuracy Targets
| Metric | Target |
|--------|--------|
| Mathematical equivalence (SymPy + Maxima) | > 99% |
| Intent-based grading correctness | > 95% |
| Handwriting OCR (Gemini baseline) | > 90% |
| Handwriting OCR (with LoRA) | > 95% |
| LLM grading with voting | > 95% |
| Correct answer must have 0 controversy | 99.9% |

### 5.3 Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| **Frontend** | Next.js (React) | App Router, TypeScript, Tailwind CSS |
| **Backend** | FastAPI (Python) | Async, Pydantic models, OpenAPI docs |
| **Compute** | AWS Lambda (via Mangum) | All API endpoints, SymPy, LLM calls, GraphRAG queries |
| **Database** | PostgreSQL (AWS RDS Aurora) | GraphRAG schema, caching, student data |
| **LLM APIs** | Gemini, Claude, GPT-4o, DeepSeek, o1, Qwen | Subject-routed with cross-verification |
| **Math Engine** | SymPy (bundled in Lambda, ~50MB) | Handles all demo equivalence cases |
| **Fine-Tuning** | Google Vertex AI | LoRA for handwriting OCR |
| **Frontend Hosting** | Vercel or AWS Amplify | Next.js deployment |
| **IaC** | AWS CDK or SAM | Lambda + API Gateway + RDS |

**MVP 1 simplification — No ECS, no Maxima:**
- SymPy handles all equivalence checks needed for the demo (basic algebra, factoring, expansion, etc.)
- When SymPy can't resolve → fall through to LLM (Stage 3) instead of Maxima
- Precedent caching means each problem is solved only once anyway
- This keeps infrastructure to just **Lambda + RDS** — simple, cheap, fast to deploy

**Post-MVP (production):** Add Maxima on ECS Fargate for advanced cases (complex trig identities, multivariable integrals) where SymPy fails and LLM is unreliable. The grading pipeline already has the 3-stage structure — Maxima just slots in as Stage 2 later.

---

## 6. System Architecture (MVP 1)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  FRONTEND — Next.js (Vercel / AWS Amplify)                              │
│                                                                         │
│  ┌───────────────┐  ┌───────────────┐  ┌─────────────────────────────┐ │
│  │ Admin Panel    │  │ Grading View  │  │ Student Diagnosis Dashboard │ │
│  │               │  │               │  │                             │ │
│  │ • Threshold   │  │ • Submit      │  │ • Concept frequency graph   │ │
│  │   settings    │  │   answer      │  │ • Root cause tracing        │ │
│  │ • Register    │  │ • View result │  │ • Learning path             │ │
│  │   problems    │  │ • Cache stats │  │ • Recommended problems      │ │
│  │ • Duplicate   │  │               │  │                             │ │
│  │   warnings    │  │               │  │                             │ │
│  └───────┬───────┘  └───────┬───────┘  └──────────────┬──────────────┘ │
└──────────┼──────────────────┼──────────────────────────┼────────────────┘
           │                  │                          │
           ▼                  ▼                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  API GATEWAY (AWS)                                                      │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  BACKEND — FastAPI on AWS Lambda (via Mangum adapter)                   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ API Routes                                                       │   │
│  │                                                                   │   │
│  │  POST /problems/register     — Extract concepts, check dupes     │   │
│  │  POST /grading/grade         — Intent-based grading              │   │
│  │  GET  /grading/cache-stats   — Cache hit rate                    │   │
│  │  GET  /students/{id}/diagnosis — Wrong answer analysis           │   │
│  │  GET  /students/{id}/wrong-answers — Wrong answer warehouse      │   │
│  │  PUT  /admin/settings        — Threshold, mode config            │   │
│  │  GET  /benchmark/results     — LLM benchmark data                │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────────┐   │
│  │ Services     │  │ Math Engine  │  │ LLM Router                 │   │
│  │              │  │              │  │                            │   │
│  │ • GraphRAG   │  │ • SymPy      │  │ • Subject-based routing   │   │
│  │   queries    │  │   (bundled   │  │ • Confidence extraction   │   │
│  │ • Concept    │  │    in Lambda │  │ • Cross-verification      │   │
│  │   extraction │  │    ~50MB)    │  │   (voting)                │   │
│  │ • Similarity │  │              │  │ • Gemini / Claude / GPT   │   │
│  │   calculation│  │ Stage 1:     │  │   / DeepSeek / o1 / Qwen │   │
│  │ • Caching    │  │   SymPy      │  │                            │   │
│  │              │  │ Stage 2:     │  │ (LLM = fallback when      │   │
│  │              │  │   → LLM      │  │  SymPy can't resolve)     │   │
│  │              │  │   fallback   │  │                            │   │
│  └──────────────┘  └──────────────┘  └────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  DATA LAYER — PostgreSQL (AWS RDS Aurora)                               │
│                                                                         │
│  ┌──────────┐ ┌──────────────┐ ┌────────────┐ ┌──────────────────┐   │
│  │ Nodes    │ │ Edges        │ │ History    │ │ Cache/Settings   │   │
│  │          │ │              │ │            │ │                  │   │
│  │ units    │ │ unit_        │ │ student_   │ │ answer_cache     │   │
│  │ concepts │ │  concepts    │ │  answers   │ │ admin_settings   │   │
│  │ questions│ │ concept_     │ │ student_   │ │ student_         │   │
│  │ students │ │  prerequisites│ │  concept_  │ │  diagnosis       │   │
│  │          │ │ concept_     │ │  mastery   │ │                  │   │
│  │          │ │  relations   │ │ wrong_     │ │                  │   │
│  │          │ │ question_    │ │  answer_   │ │                  │   │
│  │          │ │  evaluates   │ │  warehouse │ │                  │   │
│  │          │ │ question_    │ │            │ │                  │   │
│  │          │ │  units       │ │            │ │                  │   │
│  │          │ │ question_    │ │            │ │                  │   │
│  │          │ │  requires    │ │            │ │                  │   │
│  └──────────┘ └──────────────┘ └────────────┘ └──────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘

Post-MVP addition (when needed):
  ┌──────────────────────┐
  │ MAXIMA SERVICE       │  ← Slots in as Stage 2 between SymPy and LLM
  │ AWS ECS Fargate      │
  │ • Maxima engine ~5GB │
  │ • For advanced cases │
  └──────────────────────┘
```

### 6.1 Key Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Backend framework | FastAPI | Async, auto-generated OpenAPI docs, Pydantic validation, Python ecosystem for SymPy/ML |
| Lambda adapter | Mangum | Wraps ASGI (FastAPI) for Lambda with zero code changes |
| Math engine (MVP) | SymPy only | Handles all demo cases; ~50MB fits easily in Lambda |
| Math engine (post-MVP) | + Maxima on ECS Fargate | Add later for advanced trig/calculus edge cases |
| Frontend | Next.js | React ecosystem, SSR for initial load, App Router for clean API integration |
| DB | Aurora PostgreSQL | Managed, scalable, serverless option available for cost optimization |
| Infra total (MVP) | **Lambda + RDS only** | Minimal moving parts, fast to deploy, cheap to run |

### 6.2 API Design Summary

```
# Problem Management
POST   /api/v1/problems                    # Register problem (with dupe check)
GET    /api/v1/problems/{id}               # Get problem details
GET    /api/v1/problems/{id}/similar       # Get similar problems

# Grading
POST   /api/v1/grading/grade              # Grade a student answer
GET    /api/v1/grading/cache/stats         # Cache hit statistics

# Student Analytics
GET    /api/v1/students/{id}/diagnosis     # Run wrong answer analysis
GET    /api/v1/students/{id}/wrong-answers # Wrong answer warehouse
GET    /api/v1/students/{id}/mastery       # Concept mastery levels
GET    /api/v1/students/{id}/learning-path # Recommended learning path

# Admin
GET    /api/v1/admin/settings              # Get all settings
PUT    /api/v1/admin/settings/{key}        # Update setting (threshold, mode)

# Benchmark (Task 3 results)
GET    /api/v1/benchmark/matrix            # Model x Subject accuracy matrix
GET    /api/v1/benchmark/recommendations   # Optimal model per subject
```

---

## 7. Data Requirements

### 7.1 Sample Data for Demo
| Data Type | Volume | Purpose |
|-----------|--------|---------|
| Units | 15-20 | Elementary/Middle/High school math units |
| Concepts | 40-50 | Cross-unit connections visible |
| Prerequisite relationships | 60-80 | Vertical concept chains |
| Association relationships | 20-30 | Lateral cross-unit connections |
| Problems | 30-40 | 2-3 per unit |
| Students | 2-3 | With designed wrong answer patterns |
| Wrong answers | 15-20 | Cross-unit pattern visible |
| Handwriting images | 50+ | For LoRA baseline/test |
| Benchmark problems | 60-80 | For LLM subject testing |

### 7.2 Korean Math Curriculum Coverage
The sample data must cover concepts that demonstrate cross-unit dependencies:
- **Elementary**: Fractions, simplification, basic arithmetic
- **Middle School**: Factoring, expansion, quadratic equations, functions
- **High School**: Trigonometry, calculus, vectors, circle equations, complex numbers

---

## 8. Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|------------|
| LoRA fine-tuning not supported for Gemini on Vertex AI | High | Medium | Fallback to alternative models (PaLI, Donut); document findings either way |
| GraphRAG queries too slow at scale | Medium | Low | MVP uses small dataset; optimize with indexes; acceptable for demo |
| LLM confidence scores unreliable | Medium | Medium | Test multiple extraction methods; fallback to always-vote for demo |
| Maxima installation issues on demo machine | High | Low | Pre-install and test; have Docker container as backup |
| Insufficient Korean math training data for LoRA | Medium | Medium | Source from academy materials; synthetic data as supplement |
| Client expects production-ready product | High | Low | Set expectations clearly: "feasibility proof, not production" |

---

## 9. Out of Scope (MVP 1)

The following are explicitly **not** in MVP 1 but are noted for future phases:

- AI problem generation (client question, but deferred)
- AI answer generation (client question, but deferred)
- Full HWP → OCR pipeline (basic concept only, not production)
- Authentication / user management / multi-tenancy
- CI/CD pipeline
- Load testing / scalability testing
- Task 4: Maxima vs Gemini formal comparison (deferred to MVP 2)
- Mobile-responsive frontend (desktop-first for meeting demo)
- Student self-service portal (admin/teacher views only for MVP)

---

## 10. Meeting Presentation Strategy

### Key Messages to Convey

1. **Cost Reduction**: "Maxima (GPL, free, local) replaces Wolfram. Precedent caching means each problem is solved only once."
2. **Beyond Simple Grading**: "We don't just check math equivalence — we understand what the problem is testing."
3. **Root Cause Analysis**: "We don't say 'geometry is weak' — we find 'completing the square is weak, which cascades to geometry.'"
4. **Adaptive OCR**: "LoRA adapts to each student's handwriting over time."
5. **Reliable AI**: "We don't blindly trust one LLM — we route by subject and cross-verify when uncertain."

### Demo Order (Recommended)
1. **Intent-based grading** (most impressive visual impact)
2. **Cross-unit wrong answer analysis** (strongest differentiator)
3. **Duplicate problem detection** (practical value)
4. **LLM benchmark results** (data-driven credibility)
5. **LoRA results** (future capability)

---

*Document created: 2026-03-05*
