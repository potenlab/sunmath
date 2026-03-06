# SunMath Research: Task 1 — GraphRAG Schema Design + MVP Demo

> How to integrate each component into our existing system
> Created: 2026-03-06

---

## Overview

Task 1 is the **highest priority** task. It covers 3 scenarios that must be demonstrated:

| Scenario | Client Question | What It Proves |
|----------|----------------|----------------|
| A: Duplicate Detection | Q1 — Prevent duplicate problems | Concept-based similarity catches "same idea, different numbers" |
| B: Intent-Based Grading | Q3 — GraphRAG for grading | Same answer graded differently based on problem context |
| C: Wrong Answer Analysis | Q4 — Smart wrong answer notebook | Cross-unit root cause tracing, not just "this unit is weak" |

---

## Current System Status

### What's Already Built (Backend)

| Component | File | Status |
|-----------|------|--------|
| GraphRAG Service | `backend/app/services/graphrag.py` | Implemented — recursive CTE queries, concept traversal |
| Similarity Service | `backend/app/services/similarity.py` | Implemented — Jaccard similarity, threshold check |
| Grading Engine | `backend/app/services/grading_engine.py` | Implemented — Cache > SymPy > LLM pipeline |
| SymPy Engine | `backend/app/services/sympy_engine.py` | Implemented — equivalence + form check |
| LLM Router | `backend/app/services/llm_router.py` | Implemented — OpenRouter API, concept extraction |
| Diagnosis Service | `backend/app/services/diagnosis.py` | Implemented — wrong answer analysis, learning path |
| DB Models (nodes) | `backend/app/models/nodes.py` | Implemented — Unit, Concept, Question, Student |
| DB Models (edges) | `backend/app/models/edges.py` | Implemented — all relationship tables |
| DB Models (history) | `backend/app/models/history.py` | Implemented — answers, cache, wrong answer warehouse |

### What's Already Built (Frontend)

| Component | File | Status |
|-----------|------|--------|
| Grading Page | `frontend/src/app/[locale]/grading/page.tsx` | Mock UI — OCR pipeline + grading with mock data |

### What's NOT Built Yet

| Component | Needed For | Priority |
|-----------|-----------|----------|
| Seed data (concepts, units, problems, relationships) | All 3 demos | P0 |
| Problem registration API with duplicate check | Scenario A | P0 |
| Frontend: Problem Registration page | Scenario A | P0 |
| Frontend: Admin Settings page (threshold control) | Scenario A | P0 |
| Connect grading page to real backend API | Scenario B | P0 |
| Frontend: Wrong Answer Analysis page | Scenario C | P0 |
| Frontend: Student Diagnosis result view | Scenario C | P0 |

---

## Scenario A: Duplicate Problem Detection

### How It Works

```
Teacher registers new problem
        |
        v
LLM extracts concepts from problem text
  (via LLMRouter.extract_concepts)
        |
        v
Match concept names to DB concepts
  (via GraphRAGService.match_concept_names)
        |
        v
Compute Jaccard similarity against all existing problems
  (via SimilarityService.check_duplicate)
        |
        v
Compare against admin threshold (default: 0.85)
        |
  >= threshold          < threshold
        |                    |
        v                    v
  WARN or BLOCK          Register immediately
  Show similar problems
```

### How To Integrate

#### Step 1: Create Seed Data

We need sample data to make the demo work. Create a seed script at `backend/scripts/seed_demo_data.py`:

**Required seed data:**
- 15-20 units (elementary through high school math)
- 40-50 concepts with names matching Korean math curriculum
- 60-80 prerequisite relationships (concept A requires concept B)
- 20-30 lateral associations (concept A relates to concept B)
- 30-40 problems with `evaluation_concepts` and `required_concepts` linked

**Example concept tree (partial):**
```
Polynomial multiplication
  └── Multiplication formulas (a+b)^2, (a-b)^2
        ├── Factoring
        │     └── Quadratic equation solving
        │           └── Quadratic inequalities
        └── Completing the square
              ├── Quadratic functions (vertex form)
              └── Circle equations (standard form)
```

**How to run:**
```bash
cd backend
python -m scripts.seed_demo_data
```

#### Step 2: Add Problem Registration Endpoint

File: `backend/app/api/v1/problems.py`

The endpoint already exists but needs the duplicate check flow:

```python
# Pseudocode for the registration flow:

@router.post("/problems/register")
async def register_problem(body: ProblemCreate, db: AsyncSession):
    # 1. Use LLM to extract concepts from problem text
    extracted = await llm_router.extract_concepts(body.content)

    # 2. Match extracted concept names to DB concept IDs
    concept_ids = await graphrag.match_concept_names(
        extracted["evaluation_concepts"] + extracted["required_concepts"]
    )

    # 3. Check for duplicates
    dup_check = await similarity_service.check_duplicate(set(concept_ids))

    if dup_check["is_duplicate"]:
        # Return similar problems + let frontend handle warn/block
        return {
            "status": "duplicate_warning",
            "threshold": dup_check["threshold"],
            "mode": dup_check["mode"],
            "similar_problems": dup_check["similar_problems"],
            "extracted_concepts": extracted,
        }

    # 4. No duplicates — register the problem
    # Insert into questions table + link concepts via edge tables
    ...
    return {"status": "registered", "problem_id": new_problem.id}
```

#### Step 3: Frontend — Problem Registration Page

Create: `frontend/src/app/[locale]/problems/register/page.tsx`

**UI Flow:**
1. Teacher enters problem text + correct answer
2. Clicks "Register"
3. Backend extracts concepts + checks similarity
4. If similar problems found:
   - Show warning with similar problem list
   - Show shared concepts and differences
   - "Register Anyway" or "Cancel" buttons
5. If no duplicates → success message

#### Step 4: Frontend — Admin Settings Page

Create: `frontend/src/app/[locale]/admin/settings/page.tsx`

**UI Elements:**
- Similarity threshold slider (0.0 ~ 1.0, default 0.85)
- Detection mode toggle: "Block" vs "Warn"
- Save button → calls `PUT /api/v1/admin/settings`

**Backend endpoint already exists:** `backend/app/api/v1/admin.py`

---

## Scenario B: Intent-Based Grading

### How It Works

```
Student answer (OCR text) + Problem ID
        |
        v
Query GraphRAG for problem metadata
  → expected_form, grading_hints, evaluation_concepts, required_concepts
        |
        v
Cache check (question_id + normalized_answer_hash)
        |
  HIT                    MISS
   |                       |
   v                       v
Return cached         Branch by expected_form:
result                 |
                       ├── "proof" → LLM grading (pass all context)
                       |
                       ├── "factored"/"expanded"/"numeric" →
                       |     SymPy equivalence check
                       |     + SymPy form check
                       |     Both must pass
                       |
                       └── null (any form) →
                             SymPy equivalence check only
                       |
                       v
                Save result to cache
                Save student answer
                Update wrong answer warehouse
```

### How To Integrate

#### Step 1: Connect Frontend to Backend API

The grading page currently uses **mock data**. Replace mock logic with real API calls.

File: `frontend/src/app/[locale]/grading/page.tsx`

**Current (mock):**
```typescript
// Mock OCR + mock grading
const MOCK_OCR = { "1": { text: "x^2+2x+1", confidence: 0.94 } };
const gradeAnswer = (problem, answer) => { /* local logic */ };
```

**Target (real API):**
```typescript
// Step 1: Call OCR endpoint (Task 2 scope, mock for now)
const ocrResult = await fetch("/api/v1/ocr", {
  method: "POST",
  body: formData, // image file
});

// Step 2: Call grading endpoint
const gradeResult = await fetch("/api/v1/grading/grade", {
  method: "POST",
  body: JSON.stringify({
    student_id: selectedStudentId,
    question_id: selectedProblemId,
    submitted_answer: ocrResult.text,
  }),
});
```

**Backend grading endpoint:** `backend/app/api/v1/grading.py`

The `GradingEngine.grade()` method handles the full pipeline:
1. Cache check
2. GraphRAG metadata fetch
3. SymPy equivalence + form check
4. LLM fallback if needed
5. Cache result + save student answer

#### Step 2: Verify Demo Problems Cover All Cases

The demo needs to show **same answer, different grading** based on problem intent:

| Problem | Expected Form | Answer: `x^2+2x+1` | Answer: `(x+1)^2` |
|---------|--------------|---------------------|-------------------|
| "Factor x^2+2x+1" | factored | WRONG (correct math, wrong form) | CORRECT |
| "Expand (x+1)^2" | expanded | CORRECT | WRONG (correct math, wrong form) |

And form-specific grading:

| Problem | Expected Form | Answer: `sqrt(25)` | Answer: `5` |
|---------|--------------|--------------------|----|
| "Find the distance..." | numeric | WRONG (not simplified) | CORRECT |

And LLM fallback:

| Problem | Expected Form | Grading Method |
|---------|--------------|---------------|
| "Prove triangle angles = 180" | proof | LLM (SymPy can't handle proofs) |

These are all already in the seed data plan. Make sure the `questions` table has matching `expected_form` and `grading_hints`.

#### Step 3: Add Student Selector to Grading Page

Currently the grading page has no student concept. Add:
- A student dropdown (or hardcoded demo students)
- This is needed because `GradingEngine.grade()` requires `student_id` to track wrong answers

---

## Scenario C: Wrong Answer Analysis

### How It Works

```
Student has multiple wrong answers across different units
        |
        v
DiagnosisService.generate_diagnosis(student_id)
        |
        v
1. Get all active wrong answers from warehouse
        |
        v
2. For each wrong answer → get required_concepts from GraphRAG
   Count concept frequency (which concepts appear repeatedly)
        |
        v
3. Score concepts: score = frequency * (1 - mastery)
   Higher score = more impactful weakness
        |
        v
4. Root cause detection:
   Check if top concepts are prerequisites of other failing concepts
   (A concept that affects multiple downstream concepts = root cause)
        |
        v
5. Prerequisite chain backtracking (recursive CTE):
   "Completing the square" ← "Multiplication formulas" ← "Polynomial multiplication"
        |
        v
6. Output:
   - Core weaknesses (root cause concepts)
   - Prerequisite chains (what to fix first)
   - Affected units (scope of impact)
   - Learning path (ordered steps)
   - Recommended problems (easy problems for weak concepts)
```

### How To Integrate

#### Step 1: Prepare Demo Student Data

We need 2-3 students with **intentionally designed wrong answer patterns** that show cross-unit weaknesses.

**Student A example:**
```
Wrong: "Quadratic inequality x^2-3x+2<0" (Quadratic Inequalities unit)
Wrong: "Find vertex of y=x^2-4x+3" (Quadratic Functions unit)
Wrong: "Circle equation x^2+y^2-2x-4y=0" (Circle Equations unit)

Expected diagnosis:
  Root cause = "Completing the square" (mastery: 0.3)
  Prerequisite = "Multiplication formulas" (mastery: 0.5)
  NOT "geometry is weak" — it's "completing the square is weak"
```

**Student B example:**
```
Wrong: "Trig function synthesis" (Trig unit)
Wrong: "Vector dot product angle" (Vectors unit)

Expected diagnosis:
  Root cause = "Radian measure" (missing radian/degree conversion)
  Cross-unit: affects both Trig and Vectors
```

Add to seed script: `backend/scripts/seed_demo_data.py`
- Insert `student_answers` with `is_correct=false`
- Insert `wrong_answer_warehouse` entries with `status='active'`
- Insert `student_concept_mastery` with low values for target concepts

#### Step 2: Frontend — Diagnosis Page

Create: `frontend/src/app/[locale]/diagnosis/page.tsx`

**UI Layout:**

```
┌─ Student Selector ─────────────────────────────────────────┐
│ [Student A ▼]           [Run Analysis]                     │
└────────────────────────────────────────────────────────────┘

┌─ Wrong Answer History ─────────────────────────────────────┐
│ Problem 17: Quadratic inequality x^2-3x+2<0      ❌       │
│ Problem 42: Find vertex of y=x^2-4x+3            ❌       │
│ Problem 58: Circle equation x^2+y^2-2x-4y=0      ❌       │
└────────────────────────────────────────────────────────────┘

┌─ Simple Analysis (Traditional) ────────────────────────────┐
│ ❌ "Weak in: Quadratic Inequalities, Quadratic Functions,  │
│     Circle Equations"                                      │
│ → Useless. Just lists the units they got wrong.            │
└────────────────────────────────────────────────────────────┘

┌─ GraphRAG Deep Analysis ──────────────────────────────────┐
│                                                            │
│ [Concept Frequency]                                        │
│   Completing the square: ██████████ 2 times                │
│   Factoring:             ██████████ 2 times                │
│   Quadratic eq roots:    █████      1 time                 │
│                                                            │
│ [Root Cause Tracing]                                       │
│   Completing the square (0.3)                              │
│     ← Multiplication formulas (0.5)  ← ROOT CAUSE         │
│       ← Polynomial multiplication (0.8)                    │
│                                                            │
│ [Affected Units]                                           │
│   - Quadratic Inequalities (via factoring)                 │
│   - Quadratic Functions (via completing the square)        │
│   - Circle Equations (via completing the square)           │
│                                                            │
│ [Recommended Learning Path]                                │
│   Step 1: Review Multiplication Formulas → Problems #12,34│
│   Step 2: Practice Completing the Square → Problems #78,91│
│   Step 3: Re-attempt affected units                        │
└────────────────────────────────────────────────────────────┘
```

**API call:**
```typescript
const diagnosis = await fetch(`/api/v1/students/${studentId}/diagnosis`, {
  method: "POST",
});
```

**Backend endpoint:** `backend/app/api/v1/students.py` → calls `DiagnosisService.generate_diagnosis()`

#### Step 3: Visualize the Concept Graph (Optional but Impressive)

Consider adding a simple graph visualization using a library like `react-force-graph` or `d3`:
- Nodes = concepts (colored by mastery level: green=high, red=low)
- Edges = prerequisite relationships
- Highlight the root cause path in red

This would make the demo much more visually compelling.

---

## Task 2: LoRA Fine-Tuning — Per-Student Handwriting OCR

### What LoRA Does in SunMath

LoRA (Low-Rank Adaptation) creates a **small personalized adapter per student** on top of Gemini Vision so it can better recognize that student's specific handwriting. It sits in the **OCR step** of the grading pipeline — before SymPy or LLM ever sees the answer.

```
Without LoRA:
  Student image → Gemini Vision (generic) → "x2+2x+1" (misread) → SymPy grades WRONG input

With LoRA:
  Student image → Gemini Vision + Student LoRA → "x^2+2x+1" (correct) → SymPy grades RIGHT input
```

### Where LoRA Fits in the Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     GRADING PIPELINE                            │
│                                                                 │
│  ┌──────────┐    ┌───────────────────────┐    ┌──────────────┐  │
│  │  Image   │    │   OCR Layer           │    │  Grading     │  │
│  │  Upload  │───>│   Gemini Vision       │───>│  Engine      │  │
│  │          │    │   + LoRA adapter       │    │  (SymPy/LLM) │  │
│  └──────────┘    │   (per student)        │    └──────────────┘  │
│                  └───────────────────────┘                       │
│                           │                                      │
│                  ┌────────┴────────┐                             │
│                  │  Vertex AI      │                             │
│                  │  LoRA Registry  │                             │
│                  │                 │                             │
│                  │  Student A LoRA │                             │
│                  │  Student B LoRA │                             │
│                  │  Student C LoRA │                             │
│                  └─────────────────┘                             │
└─────────────────────────────────────────────────────────────────┘
```

### How It Works

| Step | What Happens | Details |
|------|-------------|---------|
| 1. Collect samples | Teacher/student uploads 100-200 handwriting images | Each image paired with correct LaTeX |
| 2. Fine-tune | Vertex AI trains a LoRA adapter for that student | Small adapter (~few MB), not full model retrain |
| 3. Deploy | Adapter is registered and linked to student_id | Managed via Vertex AI SDK |
| 4. Use at grading time | OCR request includes student_id → loads their adapter | Better handwriting recognition |

### How To Integrate

#### Step 1: Vertex AI Environment Setup

```bash
# Prerequisites
pip install google-cloud-aiplatform

# Authentication
gcloud auth application-default login
gcloud config set project <PROJECT_ID>

# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com
```

**Config to add** in `backend/app/config.py`:
```python
class Settings(BaseSettings):
    # ... existing settings ...

    # Vertex AI / LoRA
    gcp_project_id: str = ""
    gcp_region: str = "us-central1"
    vertex_ai_enabled: bool = False
    lora_base_model: str = "gemini-2.0-flash"  # or alternative
```

#### Step 2: Create LoRA Service

Create: `backend/app/services/lora_service.py`

```python
from google.cloud import aiplatform

class LoRAService:
    """Manages per-student LoRA adapters on Vertex AI."""

    def __init__(self, project_id: str, region: str):
        aiplatform.init(project=project_id, location=region)
        self.project_id = project_id
        self.region = region

    async def create_training_job(
        self, student_id: int, training_data_gcs_path: str
    ) -> dict:
        """Submit a LoRA fine-tuning job for a student.

        Args:
            student_id: Student to fine-tune for
            training_data_gcs_path: GCS path to JSONL training data
                Format: {"image": "gs://...", "text": "LaTeX output"}

        Returns:
            dict with job_id, status, estimated_time
        """
        # NOTE: Check if Gemini supports LoRA on Vertex AI first
        # If not, fallback to PaLI or Donut model
        job = aiplatform.CustomTrainingJob(
            display_name=f"lora-student-{student_id}",
            script_path="training/lora_train.py",
            container_uri="us-docker.pkg.dev/vertex-ai/training/pytorch-gpu",
        )
        # Submit job...
        return {
            "job_id": job.resource_name,
            "student_id": student_id,
            "status": "submitted",
        }

    async def get_adapter_for_student(self, student_id: int) -> str | None:
        """Look up the deployed LoRA adapter endpoint for a student.

        Returns endpoint URL or None if no adapter exists.
        """
        # Query Vertex AI Model Registry for student's adapter
        ...

    async def run_ocr_with_lora(
        self, student_id: int, image_bytes: bytes
    ) -> dict:
        """Run OCR using student's LoRA adapter (if available).

        Falls back to base Gemini Vision if no adapter exists.

        Returns:
            dict with text, confidence, used_lora (bool)
        """
        adapter_endpoint = await self.get_adapter_for_student(student_id)

        if adapter_endpoint:
            # Use fine-tuned model
            result = await self._call_endpoint(adapter_endpoint, image_bytes)
            return {**result, "used_lora": True}
        else:
            # Fallback to base Gemini Vision
            result = await self._call_base_model(image_bytes)
            return {**result, "used_lora": False}
```

#### Step 3: Add OCR Endpoint

Create: `backend/app/api/v1/ocr.py`

```python
@router.post("/ocr")
async def ocr_image(
    student_id: int,
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
):
    """OCR a student's handwriting image.

    Uses LoRA adapter if available for the student,
    otherwise falls back to base Gemini Vision.
    """
    image_bytes = await file.read()

    lora_service = LoRAService(
        project_id=settings.gcp_project_id,
        region=settings.gcp_region,
    )

    result = await lora_service.run_ocr_with_lora(student_id, image_bytes)

    return {
        "text": result["text"],
        "confidence": result["confidence"],
        "used_lora": result["used_lora"],
        "student_id": student_id,
    }
```

#### Step 4: DB Model for LoRA Adapters

Add to `backend/app/models/nodes.py`:

```python
class StudentLoRAAdapter(Base):
    __tablename__ = "student_lora_adapters"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    vertex_ai_endpoint: Mapped[str | None] = mapped_column(Text)
    base_model: Mapped[str] = mapped_column(String(100))  # "gemini-2.0-flash"
    training_samples: Mapped[int] = mapped_column(Integer)  # how many images used
    baseline_accuracy: Mapped[float | None] = mapped_column()  # before LoRA
    tuned_accuracy: Mapped[float | None] = mapped_column()  # after LoRA
    status: Mapped[str] = mapped_column(String(20))  # "training", "ready", "failed"
    training_cost_usd: Mapped[float | None] = mapped_column()
    training_time_minutes: Mapped[float | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
```

#### Step 5: Training Data Preparation

Students/teachers upload handwriting samples via a dedicated page.

**Training data format** (JSONL on GCS):
```json
{"image_uri": "gs://sunmath-training/student-42/sample-001.png", "label": "x^2 + 2x + 1"}
{"image_uri": "gs://sunmath-training/student-42/sample-002.png", "label": "\\frac{3}{4}"}
{"image_uri": "gs://sunmath-training/student-42/sample-003.png", "label": "\\sqrt{25}"}
```

**Minimum requirement:** 100-200 image+LaTeX pairs per student.

**Collection strategies:**
- Teacher scans existing homework/tests
- Student writes sample formulas from a template sheet
- Gradually collect from graded submissions (active learning)

#### Step 6: Frontend — LoRA Management Page

Create: `frontend/src/app/[locale]/admin/lora/page.tsx`

**UI Layout:**
```
┌─ LoRA Adapter Management ─────────────────────────────────┐
│                                                            │
│ ┌─ Student List ────────────────────────────────────────┐  │
│ │ Student    │ Status   │ Samples │ Accuracy │ Cost     │  │
│ │────────────┼──────────┼─────────┼──────────┼──────────│  │
│ │ Student A  │ Ready    │ 150     │ 78%→96%  │ $0.42    │  │
│ │ Student B  │ Training │ 120     │ --       │ --       │  │
│ │ Student C  │ No Data  │ 0       │ --       │ --       │  │
│ └───────────────────────────────────────────────────────┘  │
│                                                            │
│ ┌─ Upload Training Data ────────────────────────────────┐  │
│ │ Student: [Student C ▼]                                │  │
│ │                                                        │  │
│ │ [Upload Images]  [Use Template Sheet]                  │  │
│ │                                                        │  │
│ │ Uploaded: 0/100 minimum                               │  │
│ │ [Start Fine-Tuning]  (disabled until 100+ samples)    │  │
│ └───────────────────────────────────────────────────────┘  │
│                                                            │
│ ┌─ Results Dashboard ──────────────────────────────────┐   │
│ │ Average accuracy improvement: +18%                    │   │
│ │ Average cost per student: $0.38                       │   │
│ │ Average training time: 12 min                         │   │
│ └───────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────┘
```

#### Step 7: Connect to Grading Pipeline

Update the grading page OCR step to use the LoRA-aware endpoint:

```typescript
// In grading/page.tsx — replace mock OCR with real call
const ocrResult = await fetch("/api/v1/ocr", {
  method: "POST",
  body: (() => {
    const fd = new FormData();
    fd.append("student_id", selectedStudentId);
    fd.append("file", uploadedFile);
    return fd;
  })(),
});

const { text, confidence, used_lora } = await ocrResult.json();

// Show in pipeline UI:
// "Gemini Vision OCR" → "Gemini Vision OCR + LoRA" (if used_lora)
```

### Feasibility Questions to Resolve First

Before building, these must be answered (from Task 2 in tasks_en.md):

| Question | Why It Matters | How to Test |
|----------|---------------|-------------|
| Does Gemini support LoRA on Vertex AI? | If NO → must use PaLI or Donut instead | Check Vertex AI docs, try API call |
| Can fine-tuning be submitted via SDK? | 100 students = 100 jobs, must be automated | Write test script with Vertex AI SDK |
| What's the cost per student? | Must be economical at scale | Run one fine-tuning job, measure cost |
| What's the minimum training data? | Affects onboarding friction | Test with 50, 100, 200 samples |
| Can adapters be hot-swapped at inference? | Need to load correct adapter per student | Test endpoint switching |

### Fallback Plan (If Gemini LoRA Not Available)

```
Priority 1: Gemini Vision + LoRA on Vertex AI
    ↓ (not supported)
Priority 2: PaLI model + LoRA on Vertex AI
    ↓ (not supported)
Priority 3: Donut (open-source) + LoRA self-hosted
    ↓ (too complex for MVP)
Priority 4: Base Gemini Vision without LoRA (accept lower accuracy)
```

**PaLI** — Google's multimodal model, likely supports fine-tuning on Vertex AI
**Donut** — Open-source by Naver, guaranteed LoRA support, but requires self-hosting

### Key Metrics to Measure

| Metric | Target | How to Measure |
|--------|--------|---------------|
| Baseline accuracy (no LoRA) | Document | Test 50+ images with base Gemini Vision |
| Post-LoRA accuracy | > 95% | Test same 50+ images with fine-tuned adapter |
| Accuracy improvement | > 10% | Delta between baseline and post-LoRA |
| Cost per student | < $1 | Vertex AI billing after fine-tuning job |
| Training time per student | < 30 min | Measure job duration |
| Minimum training samples | ~100 | Test accuracy at 50, 100, 200 samples |
| Programmatic feasibility | Y/N | Can SDK submit + manage jobs? |

### LoRA Integration Checklist

- [ ] Verify Gemini LoRA support on Vertex AI (or select fallback model)
- [ ] Set up GCP project + Vertex AI API + service account
- [ ] Add GCP config to `backend/app/config.py`
- [ ] Create `StudentLoRAAdapter` DB model + migration
- [ ] Implement `LoRAService` with training job submission
- [ ] Implement `LoRAService.run_ocr_with_lora()` with adapter fallback
- [ ] Create `/api/v1/ocr` endpoint
- [ ] Create training data upload endpoint + GCS storage
- [ ] Build LoRA management admin page
- [ ] Run baseline accuracy measurement (50+ images)
- [ ] Execute first LoRA fine-tuning job
- [ ] Measure post-LoRA accuracy + cost + time
- [ ] Connect grading page OCR step to real `/api/v1/ocr` endpoint
- [ ] Document results in comparison table

---

## Integration Checklist (Ordered)

### Phase 1: Data Foundation (Do First)

- [ ] Create comprehensive seed data script with all entities and relationships
- [ ] Run Alembic migrations to ensure DB schema is up to date
- [ ] Verify seed data creates proper graph structure (concepts linked correctly)
- [ ] Test GraphRAG queries manually against seeded data

### Phase 2: Scenario B — Intent-Based Grading (Fastest to Demo)

- [ ] Verify `GradingEngine.grade()` works end-to-end with seeded data
- [ ] Test: same answer `x^2+2x+1` against factoring vs expansion problem
- [ ] Test: `sqrt(25)` vs `5` against numeric-expected problem
- [ ] Test: proof submission triggers LLM fallback
- [ ] Connect frontend grading page to real `/api/v1/grading/grade` endpoint
- [ ] Add student selector dropdown to grading page

### Phase 3: Scenario A — Duplicate Detection

- [ ] Test `LLMRouter.extract_concepts()` returns reasonable concepts
- [ ] Test `GraphRAGService.match_concept_names()` matches against DB
- [ ] Test `SimilarityService.check_duplicate()` catches similar problems
- [ ] Build problem registration endpoint with full flow
- [ ] Build admin settings page (threshold + mode)
- [ ] Build problem registration page with duplicate warning UI

### Phase 4: Scenario C — Wrong Answer Analysis

- [ ] Seed student wrong answer data (designed for cross-unit patterns)
- [ ] Test `DiagnosisService.generate_diagnosis()` returns correct root causes
- [ ] Verify prerequisite chain backtracking works
- [ ] Build diagnosis page with comparison (simple vs GraphRAG analysis)
- [ ] Add concept frequency visualization
- [ ] Add learning path display

### Phase 5: Task 2 — LoRA Fine-Tuning (Can Run in Parallel)

- [ ] Verify Gemini LoRA feasibility on Vertex AI
- [ ] Set up GCP project + Vertex AI + service account
- [ ] Implement `LoRAService` + `StudentLoRAAdapter` model
- [ ] Create OCR endpoint with LoRA adapter support
- [ ] Run baseline OCR accuracy measurement
- [ ] Execute first fine-tuning job + measure results
- [ ] Build LoRA management admin page
- [ ] Connect grading page to real OCR endpoint

---

## Tech Stack Reference

| Layer | Technology | Already Set Up? |
|-------|-----------|----------------|
| Frontend | Next.js + TypeScript + Tailwind | Yes |
| Backend | FastAPI + SQLAlchemy (async) | Yes |
| Database | PostgreSQL | Schema defined, needs RDS setup |
| Math Engine | SymPy | Implemented in `sympy_engine.py` |
| LLM | OpenRouter (configurable model) | Implemented in `llm_router.py` |
| Graph Queries | Recursive CTEs via SQLAlchemy | Implemented in `graphrag.py` |
| OCR | Gemini Vision (via Vertex AI) | Not yet — needs `lora_service.py` |
| Fine-Tuning | Vertex AI + LoRA | Not yet — needs feasibility check first |
| Cloud Storage | GCS (training images) | Not yet — needed for LoRA training data |

---

## Key Files Reference

```
backend/
├── app/
│   ├── api/v1/
│   │   ├── grading.py          # Grading API endpoints
│   │   ├── problems.py         # Problem CRUD + registration
│   │   ├── students.py         # Student endpoints + diagnosis
│   │   └── admin.py            # Admin settings endpoints
│   ├── models/
│   │   ├── nodes.py            # Unit, Concept, Question, Student
│   │   ├── edges.py            # All relationship tables
│   │   └── history.py          # Answers, cache, wrong answer warehouse
│   ├── services/
│   │   ├── graphrag.py         # Knowledge graph traversal
│   │   ├── similarity.py       # Jaccard similarity + duplicate check
│   │   ├── grading_engine.py   # Cache > SymPy > LLM pipeline
│   │   ├── sympy_engine.py     # Math equivalence + form check
│   │   ├── llm_router.py       # LLM API calls + concept extraction
│   │   ├── diagnosis.py        # Wrong answer analysis + learning path
│   │   └── lora_service.py     # TODO: Per-student LoRA adapter management
│   └── schemas/                # Pydantic request/response models
├── scripts/
│   └── seed_demo_data.py       # TODO: Create demo seed data
└── alembic/                    # DB migrations

frontend/
├── src/app/[locale]/
│   ├── grading/page.tsx        # Grading demo (mock, needs real API)
│   ├── problems/register/      # TODO: Problem registration page
│   ├── diagnosis/              # TODO: Wrong answer analysis page
│   ├── admin/settings/         # TODO: Admin threshold settings
│   └── admin/lora/             # TODO: LoRA adapter management page
└── messages/                   # i18n translations (en.json, ko.json)
```
