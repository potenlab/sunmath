# SunMath Project - Detailed R&D Task Guide

> 4 core R&D tasks that must be completed before the meeting
> Created: 2026-03-05

---

## Task 1: GraphRAG Schema Design + MVP Demo

**Assignee**: (TBD)
**Priority**: Highest (connected to all questions)
**Goal**: Demonstrate at the meeting that client questions 1, 3, and 4 can be solved with a GraphRAG MVP

### Why This is the Most Important

Core theme repeatedly mentioned in meeting notes: **"I think this all connects to GraphRAG"**

- Question 1 (Duplicate problem registration prevention) → Extract problem intent from GraphRAG for comparison
- Question 3 (GraphRAG itself) → Concept-problem-student-unit relationships
- Question 4 (Wrong answer notebook) → Wrong problem → Analyze which concepts are lacking via GraphRAG

### 3 Scenarios GraphRAG Must Address

#### Scenario A: Duplicate Problem Registration Prevention (Question 1)

**Problem**: Should a problem with just one changed number be considered the "same problem"?
**Solution**: Instead of comparing problem text directly, **compare the concepts (features) linked to each problem via GraphRAG to calculate a similarity score**

```
Example:
Problem A: "Factor x² + 5x + 6"
  → Connected concepts: [Factoring, Quadratic expressions, Quadratic formula, Factor theorem]
  → Assessment goal: [Quadratic expression factoring ability]
  → Difficulty: Middle school Grade 1

Problem B: "Factor x² + 7x + 12"
  → Connected concepts: [Factoring, Quadratic expressions, Quadratic formula, Factor theorem]
  → Assessment goal: [Quadratic expression factoring ability]
  → Difficulty: Middle school Grade 1

→ Graph structure similarity: 0.95 (95%)

Problem C: "Find the circumscribed circle radius when ∠A = 60° in triangle ABC"
  → Connected concepts: [Trigonometric ratios, Circumscribed circle, Law of sines]
  → Assessment goal: [Application of law of sines]

→ Similarity between A and C: 0.05 (5%)
```

**Key: Admin sets the threshold directly**

```
Admin Settings Screen:
┌─────────────────────────────────────────────┐
│  Duplicate Problem Similarity Threshold     │
│                                             │
│  Similarity threshold: [0.85]  (0.0 ~ 1.0) │
│                                             │
│  Above this value → Block or warn           │
│  Below this value → Allow registration      │
│                                             │
│  Operation mode:                            │
│  ○ Block (cannot register if ≥ threshold)   │
│  ● Warn (warn if ≥ threshold, then choose)  │
└─────────────────────────────────────────────┘
```

**Implementation Method**:

1. When registering a problem, LLM extracts the **assessment concept list + required concept list**
2. Connect extracted concepts as GraphRAG nodes
3. When registering a new problem → Calculate **graph structure similarity** with all existing problems
4. Similarity = (concept intersection of two problems) / (concept union of two problems) (Jaccard similarity)
5. If similarity is above the admin-set threshold:
    - Block mode: Reject registration + return similar problem list
    - Warn mode: "Similar problems exist" + similar problem list → Admin decides whether to register
6. Below threshold → Register immediately

**Information shown when returning similar problems**:

```
⚠️ A problem with similarity 0.92 exists (threshold: 0.85)

Existing Problem #142: "Factor x² + 7x + 12"
  - Similarity: 0.92
  - Shared concepts: [Factoring, Quadratic expressions, Quadratic formula, Factor theorem]
  - Difference: Only coefficients differ

Existing Problem #87: "Factor x² - 4"
  - Similarity: 0.78
  - Shared concepts: [Factoring, Quadratic expressions]
  - Difference: Perfect square vs difference of squares

[Register]  [Cancel]
```

---

#### Scenario B: Intent-Based Grading (Question 3 + Grading)

**Problem**: `4/6 = 2/3` might be wrong for an elementary student but correct for a high school student
**Key Point**: Not just mathematical equivalence, but **judging based on the concept the problem is trying to evaluate**

```
Example 1: Factoring Unit
Problem: "Factor x² + 2x + 1"
  → GraphRAG lookup: Assessment goal = [Factoring ability]
  → Student answer: (x+1)² → Correct (factored form)
  → Student answer: x² + 2x + 1 → Wrong (expanded form, not factored)
  ※ Mathematically equivalent, but wrong based on problem intent

Example 2: Expansion Unit
Problem: "Expand (x+1)²"
  → GraphRAG lookup: Assessment goal = [Polynomial expansion ability]
  → Student answer: x² + 2x + 1 → Correct
  → Student answer: (x+1)² → Wrong (not expanded)

Example 3: Simplification (Grade-level differences)
Problem: "Calculate 4/6" (Elementary Grade 3, simplification unit)
  → GraphRAG lookup: Assessment goal = [Fraction simplification], Target = Elementary Grade 3
  → Student answer: 2/3 → Correct (simplification performed)
  → Student answer: 4/6 → Wrong (not simplified)

Example 4: Geometry + Coordinate Mixed
Problem: "Find the distance between points A(1,2) and B(4,6)"
  → GraphRAG lookup: Assessment goal = [Distance formula between two points], Expected form = numeric
  → Student answer: 5 → Correct
  → Student answer: √25 → Correct (mathematically equivalent + no form restriction)
  → Student answer: √((4-1)²+(6-2)²) → Correct but wrong if intent is "complete the calculation"

Example 5: Proof Problem
Problem: "Prove that the sum of interior angles of a triangle is 180°"
  → GraphRAG lookup: Assessment goal = [Triangle interior angle property proof], Required concepts = [Alternate angles of parallel lines, Corresponding angles]
  → Mathematical equivalence determination not possible → Pass evaluation concepts + required theorem list to LLM for judgment
```

**Grading Flow (Flexible Structure)**:

Grading types are not hardcoded. **Per-problem metadata stored in GraphRAG determines the grading method**.

```
1. Query GraphRAG with Problem ID
   → Returned information:
     - evaluation_concepts: Concepts this problem evaluates
     - required_concepts: Concepts needed to solve this problem
     - expected_form: Expected answer format (nullable)
       e.g.: "factored", "expanded", "simplified", "numeric", "proof", null(=any)
     - target_grade: Target grade level (affects grading criteria)
     - grading_hints: Additional grading considerations (free text)
       e.g.: "Must be in factored form to be correct", "Must include units", "Proof process required"

2. Student answer OCR

3. Grading decision (automatic branching based on expected_form)

   IF expected_form exists:
     → Check mathematical equivalence (SymPy/Maxima)
     → + Verify answer matches expected_form
     → Must pass both to be correct

   IF expected_form is null(=any):
     → Only check mathematical equivalence (SymPy/Maxima)

   IF formula equivalence determination is not possible (proof, descriptive, etc.):
     → Pass the following to LLM together:
       - Student answer
       - evaluation_concepts (assessment goals)
       - required_concepts (required concepts/theorems)
       - grading_hints (grading hints)
     → LLM determines whether assessment goals are achieved

4. target_grade-based adjustment
   → Same problem may have different expected levels by grade
   → Grade-specific notes in grading_hints
   → e.g.: "Elementary - simplification required", "High school - irreducible fraction not required"

5. Return result + save to precedent cache
```

**Advantage of this structure**: No code changes needed when new units/types are added. As long as metadata is properly entered when registering problems, any math domain can be graded with the same flow.

---

#### Scenario C: Wrong Answer Analysis & Personalized Learning (Question 4)

Not just "this unit is weak," but **must trace through the concept graph across units to find the root cause**.

```
Example: Student A's Wrong Answer History

Wrong problems:
  - Problem 17: "Find the solution to quadratic inequality x²-3x+2<0" (Quadratic inequalities unit)
  - Problem 42: "Find the vertex coordinates of parabola y=x²-4x+3" (Quadratic functions unit)
  - Problem 58: "Find the center and radius of circle x²+y²-2x-4y=0" (Circle equation/Geometry unit)

Simple Analysis (Traditional method):
  → "Weak in quadratic inequalities, quadratic functions, geometry"
  → This is useless. Are we telling them to redo all 3 units?

GraphRAG Deep Analysis:

  Step 1: Query all connected concepts for each wrong problem
    Problem 17 → [Quadratic inequalities, Quadratic equation roots, Factoring, Inequality sign determination]
    Problem 42 → [Quadratic functions, Completing the square, Vertex formula, Factoring]
    Problem 58 → [Circle equation, Completing the square, Coordinate geometry]

  Step 2: Concept frequency analysis (which concepts appear repeatedly)
    - Completing the square: 2 times (Problems 42, 58)
    - Factoring: 2 times (Problems 17, 42)
    - Quadratic equation roots: 1 time
    - Inequality sign determination: 1 time
    - Vertex formula: 1 time
    - Circle equation: 1 time
    - Coordinate geometry: 1 time

  Step 3: Prerequisite concept graph backtracking
    Completing the square ← Polynomial multiplication formulas ← Polynomial multiplication
    Factoring ← Polynomial multiplication formulas ← Polynomial multiplication

    → Common root: "Polynomial multiplication formulas" (common prerequisite of completing the square and factoring)

  Step 4: Cross-unit analysis
    This student got 3 units wrong: "Quadratic inequalities", "Quadratic functions", "Geometry (Circle equations)",
    but the actual root cause is weakness in the "Multiplication formulas → Completing the square" concept chain.

    Getting the geometry (circle equation) problem wrong isn't because geometry concepts are weak,
    but because "completing the square" processing needed to convert the circle equation to standard form isn't working.

  Step 5: Diagnosis Result
    ┌──────────────────────────────────────────────────────┐
    │ Student A Weakness Diagnosis Report                   │
    │                                                      │
    │ Core weakness: Completing the square (mastery: 0.3)  │
    │    ← Prerequisite: Multiplication formulas           │
    │      (mastery: 0.5)                                  │
    │                                                      │
    │ Affected units:                                      │
    │    - Quadratic inequalities (via factoring)          │
    │    - Quadratic functions (via completing the square)  │
    │    - Circle equations (via completing the square)     │
    │                                                      │
    │ Recommended learning path:                           │
    │    1. Review multiplication formulas                 │
    │       (start from prerequisites)                     │
    │    2. Focused practice on completing the square      │
    │    3. Re-study affected units in order               │
    │                                                      │
    │ Recommended problems: #12, #34, #56                  │
    │   (multiplication formulas unit)                     │
    │   #78, #91 (completing the square unit)              │
    └──────────────────────────────────────────────────────┘

  Key: Not "geometry is weak" but "completing the square is weak, which causes geometry problems too"
  → Solving more geometry problems is pointless. Must start with completing the square.
```

**Another Example: Hidden Cross-Unit Connections**

```
Student B Wrong Answers:
  - Problem A: Trigonometric function synthesis problem (Trigonometric functions unit) → Wrong
  - Problem B: Vector dot product angle problem (Vectors unit) → Wrong

GraphRAG Analysis:
  Problem A → [Trig function synthesis, Addition formulas, Radian measure]
  Problem B → [Vector dot product, Cosine, Radian measure]

  Common weakness: "Radian measure" (radian↔degree conversion)

  → It's not that trigonometric functions are weak, or that vectors are weak,
    "radian measure" understanding is missing, affecting both units.
```

---

### PostgreSQL Schema Design

```sql
-- ============================================
-- Core Node Tables
-- ============================================

-- Units (Textbook table of contents structure)
CREATE TABLE units (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,           -- "Solving Quadratic Equations"
    grade VARCHAR(20) NOT NULL,           -- "Middle 3", "High 1"
    subject VARCHAR(50) NOT NULL,         -- "Mathematics", "Math I"
    chapter_path TEXT NOT NULL,           -- "Middle 3 > Quadratic Equations > Solving"
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Math Concepts (Core GraphRAG nodes)
CREATE TABLE concepts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,           -- "Completing the square", "Radian measure", "Factoring"
    description TEXT,                     -- Concept description
    category VARCHAR(100),                -- Upper classification (Algebra, Geometry, Analysis, etc.) - for reference
    difficulty_level INT,                 -- 1-5
    created_at TIMESTAMP DEFAULT NOW()
);

-- Problems
CREATE TABLE questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,                -- Problem text/LaTeX
    image_url TEXT,                       -- Problem image (if any)
    correct_answer TEXT NOT NULL,         -- Correct answer LaTeX
    expected_form VARCHAR(50),            -- Expected answer format. nullable = any allowed
                                          -- e.g.: 'factored', 'expanded', 'simplified',
                                          -- 'numeric', 'proof', 'standard_form', null
    target_grade VARCHAR(20),             -- Target grade ("Elem 3", "Middle 1", "High 2")
    grading_hints TEXT,                   -- Additional grading considerations (free text)
                                          -- e.g.: "Must be in factored form to be correct"
                                          -- e.g.: "Must include units"
                                          -- e.g.: "Proof process must use parallel line properties"
                                          -- e.g.: "Elementary - simplification required"
    difficulty_level INT,                 -- 1-5
    source VARCHAR(200),                  -- Source (textbook name, etc.)
    created_at TIMESTAMP DEFAULT NOW()
);

-- Students
CREATE TABLE students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    grade VARCHAR(20) NOT NULL,
    school VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- Admin Settings
-- ============================================

CREATE TABLE admin_settings (
    key VARCHAR(100) PRIMARY KEY,
    value JSONB NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Initial setting values
INSERT INTO admin_settings (key, value) VALUES
('similarity_threshold', '{"threshold": 0.85, "mode": "warn"}'),
-- mode: "block" = block registration if above threshold
-- mode: "warn"  = warn if above threshold, then admin chooses
('confidence_threshold', '{"threshold": 0.90}');
-- LLM cross-verification trigger threshold

-- ============================================
-- Edge (Relationship) Tables
-- ============================================

-- Unit ↔ Concept relationship
CREATE TABLE unit_concepts (
    unit_id UUID REFERENCES units(id),
    concept_id UUID REFERENCES concepts(id),
    is_primary BOOLEAN DEFAULT true,      -- Whether this is the unit's primary concept
    PRIMARY KEY (unit_id, concept_id)
);

-- Concept ↔ Concept prerequisites (Core of the prerequisite learning graph!)
CREATE TABLE concept_prerequisites (
    concept_id UUID REFERENCES concepts(id),       -- Upper concept
    prerequisite_id UUID REFERENCES concepts(id),   -- Prerequisite concept
    strength FLOAT DEFAULT 1.0,           -- Relationship strength (0.0~1.0)
    PRIMARY KEY (concept_id, prerequisite_id)
);

-- Concept ↔ Concept associations (Lateral connections, not prerequisites)
-- e.g.: "Radian measure" ↔ "Trigonometric functions", "Radian measure" ↔ "Vector dot product"
CREATE TABLE concept_relations (
    concept_a_id UUID REFERENCES concepts(id),
    concept_b_id UUID REFERENCES concepts(id),
    relation_type VARCHAR(50) NOT NULL,   -- 'uses', 'related', 'extends', 'alternative'
    description TEXT,                     -- "Radian measure used in cosine calculation for vector dot product"
    PRIMARY KEY (concept_a_id, concept_b_id)
);

-- Problem → Evaluation concepts (What concepts the problem evaluates)
CREATE TABLE question_evaluates (
    question_id UUID REFERENCES questions(id),
    concept_id UUID REFERENCES concepts(id),
    is_primary_goal BOOLEAN DEFAULT true, -- Whether this is the primary assessment goal
    PRIMARY KEY (question_id, concept_id)
);

-- Problem → Unit membership
CREATE TABLE question_units (
    question_id UUID REFERENCES questions(id),
    unit_id UUID REFERENCES units(id),
    PRIMARY KEY (question_id, unit_id)
);

-- Problem → Required concepts (Concepts needed to solve this problem)
-- Not assessment goals but concepts needed for the solution. Key for wrong answer root cause tracing.
CREATE TABLE question_requires (
    question_id UUID REFERENCES questions(id),
    concept_id UUID REFERENCES concepts(id),
    PRIMARY KEY (question_id, concept_id)
);

-- ============================================
-- Student Learning History (Wrong answer notebook + Mastery)
-- ============================================

-- Student answer history
CREATE TABLE student_answers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id),
    question_id UUID REFERENCES questions(id),
    answer TEXT NOT NULL,                 -- Student answer (LaTeX)
    is_correct BOOLEAN NOT NULL,
    error_concepts UUID[],               -- Concepts that caused this wrong answer (GraphRAG analysis result)
    error_description TEXT,              -- Wrong answer cause description analyzed by LLM
    answered_at TIMESTAMP DEFAULT NOW()
);

-- Per-student concept mastery (GraphRAG aggregate)
CREATE TABLE student_concept_mastery (
    student_id UUID REFERENCES students(id),
    concept_id UUID REFERENCES concepts(id),
    mastery_level FLOAT DEFAULT 0.0,      -- 0.0 ~ 1.0
    total_attempts INT DEFAULT 0,         -- Total attempts for problems related to this concept
    correct_attempts INT DEFAULT 0,       -- Number correct
    last_attempt_at TIMESTAMP,
    PRIMARY KEY (student_id, concept_id)
);

-- Wrong answer warehouse (Dynamic wrong answer management - Question 4)
CREATE TABLE wrong_answer_warehouse (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id),
    question_id UUID REFERENCES questions(id),
    student_answer_id UUID REFERENCES student_answers(id),
    status VARCHAR(20) DEFAULT 'active',  -- 'active' → 'resolved' → 'archived'
    root_cause_concepts UUID[],           -- Root cause concepts (GraphRAG backtracking result)
    retry_count INT DEFAULT 0,
    resolved_at TIMESTAMP,                -- Timestamp when correctly re-solved
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- Diagnosis Reports (Wrong answer analysis results storage)
-- ============================================

CREATE TABLE student_diagnosis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id),
    diagnosis_date TIMESTAMP DEFAULT NOW(),
    weak_concepts JSONB NOT NULL,
    -- e.g.: [
    --   {"concept_id": "uuid", "name": "Completing the square", "mastery": 0.3,
    --    "affected_units": ["Quadratic functions", "Circle equations"],
    --    "prerequisite_chain": ["Multiplication formulas", "Polynomial multiplication"]},
    --   {"concept_id": "uuid", "name": "Radian measure", "mastery": 0.4,
    --    "affected_units": ["Trigonometric functions", "Vectors"],
    --    "prerequisite_chain": ["Angles", "Circle properties"]}
    -- ]
    recommended_questions UUID[],         -- Recommended problem ID list
    learning_path JSONB                   -- Recommended learning path
    -- e.g.: [
    --   {"step": 1, "concept": "Multiplication formulas", "reason": "Prerequisite for completing the square"},
    --   {"step": 2, "concept": "Completing the square", "reason": "Core weakness"},
    --   {"step": 3, "concept": "Quadratic functions", "reason": "Unit applying completing the square"}
    -- ]
);

-- ============================================
-- Precedent Caching (Grading result cache)
-- ============================================

CREATE TABLE answer_cache (
    question_id UUID REFERENCES questions(id),
    student_answer_normalized TEXT NOT NULL, -- Normalized student answer
    is_correct BOOLEAN NOT NULL,
    judged_by VARCHAR(50) NOT NULL,         -- 'sympy', 'maxima', 'llm', 'graphrag+sympy'
    reasoning TEXT,                          -- Judgment rationale
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (question_id, student_answer_normalized)
);

-- ============================================
-- Indexes
-- ============================================

CREATE INDEX idx_student_answers_student ON student_answers(student_id);
CREATE INDEX idx_student_answers_question ON student_answers(question_id);
CREATE INDEX idx_student_answers_correct ON student_answers(student_id, is_correct);
CREATE INDEX idx_student_mastery_student ON student_concept_mastery(student_id);
CREATE INDEX idx_student_mastery_level ON student_concept_mastery(student_id, mastery_level);
CREATE INDEX idx_wrong_warehouse_student ON wrong_answer_warehouse(student_id);
CREATE INDEX idx_wrong_warehouse_status ON wrong_answer_warehouse(status);
CREATE INDEX idx_answer_cache_question ON answer_cache(question_id);
CREATE INDEX idx_concept_prerequisites_prereq ON concept_prerequisites(prerequisite_id);
CREATE INDEX idx_concept_relations_b ON concept_relations(concept_b_id);
CREATE INDEX idx_question_evaluates_concept ON question_evaluates(concept_id);
CREATE INDEX idx_question_requires_concept ON question_requires(concept_id);
```

### GraphRAG Query Examples

```sql
-- 1. Query problem assessment goals + required concepts + grading metadata (before grading)
SELECT
    q.expected_form,
    q.target_grade,
    q.grading_hints,
    json_agg(DISTINCT jsonb_build_object('concept', c1.name, 'is_primary', qe.is_primary_goal)) AS evaluation_concepts,
    json_agg(DISTINCT c2.name) FILTER (WHERE c2.name IS NOT NULL) AS required_concepts
FROM questions q
LEFT JOIN question_evaluates qe ON qe.question_id = q.id
LEFT JOIN concepts c1 ON c1.id = qe.concept_id
LEFT JOIN question_requires qr ON qr.question_id = q.id
LEFT JOIN concepts c2 ON c2.id = qr.concept_id
WHERE q.id = 'QUESTION_UUID'
GROUP BY q.id;

-- 2. Graph structure similarity between two problems (duplicate detection - Jaccard similarity)
WITH q_a_concepts AS (
    SELECT concept_id FROM question_evaluates WHERE question_id = 'QUESTION_A_UUID'
    UNION
    SELECT concept_id FROM question_requires WHERE question_id = 'QUESTION_A_UUID'
),
q_b_concepts AS (
    SELECT concept_id FROM question_evaluates WHERE question_id = 'QUESTION_B_UUID'
    UNION
    SELECT concept_id FROM question_requires WHERE question_id = 'QUESTION_B_UUID'
),
similarity AS (
    SELECT
        COUNT(*) FILTER (WHERE a.concept_id IS NOT NULL AND b.concept_id IS NOT NULL)::FLOAT
        / NULLIF(COUNT(*)::FLOAT, 0) AS score
    FROM (
        SELECT concept_id FROM q_a_concepts
        UNION
        SELECT concept_id FROM q_b_concepts
    ) all_concepts
    LEFT JOIN q_a_concepts a USING (concept_id)
    LEFT JOIN q_b_concepts b USING (concept_id)
)
SELECT
    s.score AS similarity,
    s.score >= (SELECT (value->>'threshold')::FLOAT FROM admin_settings WHERE key = 'similarity_threshold') AS exceeds_threshold
FROM similarity s;

-- 3. Compare similarity of new problem against all existing problems during registration (return only those above threshold)
WITH new_q_concepts AS (
    -- New problem's concepts (passed temporarily since not yet registered)
    SELECT unnest(ARRAY['concept_uuid_1', 'concept_uuid_2', 'concept_uuid_3']::UUID[]) AS concept_id
),
existing_q_concepts AS (
    SELECT question_id, array_agg(concept_id) AS concepts
    FROM (
        SELECT question_id, concept_id FROM question_evaluates
        UNION
        SELECT question_id, concept_id FROM question_requires
    ) combined
    GROUP BY question_id
),
similarities AS (
    SELECT
        eq.question_id,
        -- Jaccard: intersection / union
        (SELECT COUNT(*) FROM (
            SELECT unnest(eq.concepts) INTERSECT SELECT concept_id FROM new_q_concepts
        ) i)::FLOAT
        / NULLIF((SELECT COUNT(*) FROM (
            SELECT unnest(eq.concepts) UNION SELECT concept_id FROM new_q_concepts
        ) u)::FLOAT, 0) AS similarity
    FROM existing_q_concepts eq
)
SELECT s.question_id, q.content, s.similarity
FROM similarities s
JOIN questions q ON q.id = s.question_id
WHERE s.similarity >= (SELECT (value->>'threshold')::FLOAT FROM admin_settings WHERE key = 'similarity_threshold')
ORDER BY s.similarity DESC;

-- 4. Student wrong answer deep analysis - find cross-unit weaknesses
WITH wrong_questions AS (
    -- Recent wrong problems
    SELECT DISTINCT sa.question_id
    FROM student_answers sa
    WHERE sa.student_id = 'STUDENT_UUID'
      AND sa.is_correct = false
),
-- All concepts connected to wrong problems (evaluation + required)
wrong_concepts AS (
    SELECT concept_id, COUNT(*) AS frequency
    FROM (
        SELECT qe.concept_id FROM question_evaluates qe
        JOIN wrong_questions wq ON wq.question_id = qe.question_id
        UNION ALL
        SELECT qr.concept_id FROM question_requires qr
        JOIN wrong_questions wq ON wq.question_id = qr.question_id
    ) all_concepts
    GROUP BY concept_id
),
-- Mastery level for each concept
concept_mastery AS (
    SELECT
        wc.concept_id,
        c.name,
        c.category,
        wc.frequency AS error_frequency,
        COALESCE(scm.mastery_level, 0) AS mastery
    FROM wrong_concepts wc
    JOIN concepts c ON c.id = wc.concept_id
    LEFT JOIN student_concept_mastery scm
        ON scm.concept_id = wc.concept_id AND scm.student_id = 'STUDENT_UUID'
),
-- Backtrack prerequisites of weak concepts
root_causes AS (
    SELECT DISTINCT
        cm.concept_id AS weak_concept_id,
        cm.name AS weak_concept_name,
        cm.mastery AS weak_mastery,
        cp.prerequisite_id,
        c_prereq.name AS prerequisite_name,
        COALESCE(scm_prereq.mastery_level, 0) AS prerequisite_mastery
    FROM concept_mastery cm
    JOIN concept_prerequisites cp ON cp.concept_id = cm.concept_id
    JOIN concepts c_prereq ON c_prereq.id = cp.prerequisite_id
    LEFT JOIN student_concept_mastery scm_prereq
        ON scm_prereq.concept_id = cp.prerequisite_id AND scm_prereq.student_id = 'STUDENT_UUID'
    WHERE cm.mastery < 0.6  -- Only weak concepts
)
SELECT * FROM root_causes
ORDER BY prerequisite_mastery ASC;  -- Weakest prerequisites first

-- 5. Weak concepts → Query all affected units
SELECT DISTINCT u.name AS affected_unit, u.grade, c.name AS via_concept
FROM student_concept_mastery scm
JOIN concepts c ON c.id = scm.concept_id
JOIN unit_concepts uc ON uc.concept_id = c.id
JOIN units u ON u.id = uc.unit_id
WHERE scm.student_id = 'STUDENT_UUID'
  AND scm.mastery_level < 0.5
ORDER BY scm.mastery_level ASC;

-- 6. Recommended problems: Easy problems that evaluate weak prerequisite concepts
SELECT q.id, q.content, q.difficulty_level, c.name AS target_concept
FROM questions q
JOIN question_evaluates qe ON qe.question_id = q.id
JOIN concepts c ON c.id = qe.concept_id
WHERE c.id IN (
    -- Prerequisite concepts of student's weak concepts
    SELECT cp.prerequisite_id
    FROM student_concept_mastery scm
    JOIN concept_prerequisites cp ON cp.concept_id = scm.concept_id
    WHERE scm.student_id = 'STUDENT_UUID' AND scm.mastery_level < 0.5
)
AND q.difficulty_level <= 3  -- Start with easy problems
ORDER BY q.difficulty_level ASC;
```

### MVP Demo Requirements

**What must be shown in the demo (all 3 scenarios)**:

#### Demo 1: Duplicate Problem Detection + Admin Threshold (Question 1)

```
Demo Flow:
1. Set similarity threshold = 0.85 in admin screen (mode: warn)
2. Register Problem A "Factor x²+5x+6" → Success
3. Attempt to register Problem B "Factor x²+7x+12"
   → "Similarity 0.92 - similar to existing Problem A" warning
   → Show similar problem list + shared concepts + differences
   → Admin chooses "Register" or "Cancel"
4. Register Problem C "Find circumscribed circle radius of triangle" → Similarity 0.05 → Registered immediately
5. Admin changes threshold to 0.95
6. Try Problem B again → 0.92 < 0.95 → This time registered without warning

Key message: Admin can freely adjust the threshold
```

#### Demo 2: Intent-Based Grading (Question 3)

```
Demo Flow:
1. Submit the same mathematical answer (x²+2x+1) to two problems
   - Factoring problem: expected_form = "factored" → Wrong
   - Expansion problem: expected_form = null → Correct
   → Show "grading method changes with just problem metadata, no code changes"

2. Geometry problem: "Find distance between two points"
   - expected_form = "numeric", grading_hints = "Calculation must be completed"
   - √25 → Wrong (not numeric)
   - 5 → Correct

3. Proof problem: "Prove sum of triangle interior angles"
   - expected_form = "proof"
   - grading_hints = "Must use alternate angle property of parallel lines"
   - → Pass evaluation_concepts + required_concepts + grading_hints to LLM
   - → LLM makes comprehensive judgment

Key message: Covers all math domains with just metadata, no hardcoding of units/types
```

#### Demo 3: Cross-Unit Wrong Answer Analysis (Question 4)

```
Demo Flow:
1. Set up student data:
   - Quadratic inequality problem → Wrong
   - Quadratic function vertex problem → Wrong
   - Circle equation problem → Wrong

2. "Run Analysis" button

3. Result screen:
   ❌ Simple analysis: "Weak in quadratic inequalities, quadratic functions, geometry"
   ✅ GraphRAG analysis:

   [Concept Frequency Graph]
   Completing the square: ██████ 2 times
   Factoring:             ██████ 2 times
   Radian measure:        ███    1 time

   [Root Cause Tracing]
   Completing the square(mastery: 0.3) ← Multiplication formulas(mastery: 0.5) ← Polynomial multiplication(mastery: 0.8)
                                            ↑ This is the bottleneck!

   [Impact Scope]
   Units affected by weak "multiplication formulas":
   - Quadratic inequalities (via factoring)
   - Quadratic functions (via completing the square)
   - Circle equations (via completing the square)
   - Factoring (direct impact)

   [Recommended Learning Path]
   Step 1: Review multiplication formulas → 3 recommended problems
   Step 2: Practice completing the square → 3 recommended problems
   Step 3: Re-attempt quadratic functions → 2 recommended problems

Key message: Not "geometry is weak" but "completing the square is weak, causing geometry errors too"
→ Find root causes and suggest efficient learning paths
```

**Demo Tech Stack**:

- PostgreSQL (AWS RDS)
- Python scripts (data insertion + analysis logic)
- Simple web UI or Jupyter Notebook

**Sample Data Needed**:

- 15-20 units (major units across elementary/middle/high school)
- 40-50 concepts (enough to show cross-unit connections)
- 60-80 prerequisite relationships (vertical connections between concepts)
- 20-30 association relationships (lateral connections between concepts - cross-unit relationships)
- 30-40 problems (2-3 problems per unit)
- Wrong answer data for 2-3 students (designed to show cross-unit patterns)

---

## Task 2: Gemini + LoRA Fine-Tuning Test (Google Vertex AI)

**Assignee**: (TBD)
**Priority**: High (selling point)
**Goal**: Determine whether LoRA can improve per-student handwriting OCR accuracy and how much it costs

### Background

> "I think LoRA would be good for recognizing each person's handwriting"
> "This could be our selling point"
> "You'd have to create one for each student... how cost-effective is it"

### Test Procedure

#### Step 1: Environment Setup

- [ ] Create Google Cloud project / use existing project
- [ ] Enable Vertex AI API
- [ ] Set up service account + authentication
- [ ] Verify Gemini model access

#### Step 2: Baseline Measurement

- [ ] Prepare handwriting formula image samples (minimum 50)
    - Include clean writing / messy writing / unusual notation
    - Formula types: fractions, radicals, exponents, integrals, matrices, etc.
- [ ] Measure baseline accuracy with Gemini Vision OCR
- [ ] Analyze error patterns - what types cause errors

#### Step 3: LoRA Fine-Tuning

- [ ] Check if Gemini LoRA fine-tuning is possible on Vertex AI
    - If possible: Execute fine-tuning directly
    - If not possible: Test with alternative models (PaLI, Donut, etc.)
- [ ] Prepare training data
    - Handwriting image + correct LaTeX pairs
    - Minimum 100-200 pairs (per student basis)
- [ ] Execute fine-tuning + measure results

#### Step 4: Results Analysis

**Required Deliverables**:

| Item                                               | Measurement |
| -------------------------------------------------- | ----------- |
| Baseline accuracy (before LoRA)                    | \_\_%       |
| Accuracy after LoRA                                | \_\_%       |
| Accuracy improvement                               | \_\_%       |
| Fine-tuning cost per student                       | $\_\_       |
| Fine-tuning time per student                       | \_\_ min    |
| Minimum required data volume                       | \_\_ images |
| Programmatic fine-tuning feasibility               | Y/N         |
| API-based per-student model management feasibility | Y/N         |

**Why Programmatic Fine-Tuning is Important**:

- If the academy has 100 students → Need to fine-tune 100 times
- Manual process is impossible → Must be automatable via API/SDK
- Verify if fine-tuning jobs can be submitted and managed programmatically via Vertex AI SDK

```python
# Verify if programmatic approach like this is possible
from google.cloud import aiplatform

# Per-student fine-tuning automation example
def finetune_for_student(student_id: str, training_data_path: str):
    job = aiplatform.CustomTrainingJob(
        display_name=f"lora-student-{student_id}",
        # ...
    )
    model = job.run(training_data_path)
    return model.resource_name
```

---

## Task 3: LLM Subject-Specific Testing + Cross-Verification R&D

**Assignee**: (TBD)
**Priority**: High
**Goal**: Benchmark which LLM excels at which math subject + verify method of improving accuracy through multi-model voting when confidence is low

### Background

> "I wanted to test which models are good at which subjects using various models"
> "Geometry obviously can't be done well by models without reasoning"
> "If confidence is below 90%, have another LLM solve it together for cross-checking"

### Step 1: Prepare Test Problem Sets

Minimum 10 problems per subject, 60-80 total:

| Subject                           | # Problems | Difficulty Distribution | Notes                      |
| --------------------------------- | ---------- | ----------------------- | -------------------------- |
| Algebra (equations, inequalities) | 10         | Easy 3/Med 4/Hard 3     |                            |
| Factoring/Expansion               | 10         | Easy 3/Med 4/Hard 3     | Includes form conversion   |
| Geometry (shapes, proofs)         | 10         | Easy 3/Med 4/Hard 3     | Requires reasoning         |
| Calculus                          | 10         | Easy 3/Med 4/Hard 3     |                            |
| Probability/Statistics            | 10         | Easy 3/Med 4/Hard 3     |                            |
| Mixed (descriptive)               | 10         | Med 5/Hard 5            | Multiple concepts combined |

**Standardized Problem Format**:

```
Problem: [Problem text]
Answer: [LaTeX format]
Assessment concepts: [Concept list]
Difficulty: [Easy/Medium/Hard]
```

### Step 2: Per-Model Testing

**Models to Test (7)**:

| Model             | Cost (per 1K tokens) | Characteristics              |
| ----------------- | -------------------- | ---------------------------- |
| DeepSeek-V3       | ~$0.001              | Math-specialized, affordable |
| Claude Sonnet 4.6 | ~$0.003/$0.015       | General-purpose, stable      |
| GPT-4o            | ~$0.005/$0.015       | General-purpose              |
| Gemini 2.5 Pro    | ~$0.00125/$0.01      | Best multimodal OCR          |
| o1/o3             | ~$0.015/$0.06        | Reasoning-specialized        |
| DeepSeek-R1       | ~$0.005              | Reasoning + affordable       |
| Qwen 2.5 Math     | ~$0.001              | Math-specialized open source |

**Test Method**:

```python
import json
from datetime import datetime

results = []

for model in models:
    for question in questions:
        response = call_llm(model, question)
        results.append({
            "model": model,
            "question_id": question["id"],
            "unit": question["unit"],
            "difficulty": question["difficulty"],
            "correct": check_answer(response, question["answer"]),
            "confidence": extract_confidence(response),
            "latency_ms": response["latency"],
            "cost_usd": response["cost"],
        })

# Save results as CSV
```

**Standardized Prompt Design**:

```
Please solve the following math problem.

Problem: {question}

Please respond in the following format:
1. Solution process (concisely)
2. Final answer: [answer]
3. Confidence: [0-100]%
```

### Step 3: Results Analysis Table (Required Deliverable)

**Model x Subject Accuracy Matrix**:

```
            | Algebra | Factoring | Geometry | Calculus | Prob/Stats | Mixed | Average | Cost/Problem |
DeepSeek-V3 |   _%   |     _%    |    _%   |    _%    |     _%    |  _%  |   _%   |     $__     |
Claude      |   _%   |     _%    |    _%   |    _%    |     _%    |  _%  |   _%   |     $__     |
GPT-4o      |   _%   |     _%    |    _%   |    _%    |     _%    |  _%  |   _%   |     $__     |
Gemini      |   _%   |     _%    |    _%   |    _%    |     _%    |  _%  |   _%   |     $__     |
o1/o3       |   _%   |     _%    |    _%   |    _%    |     _%    |  _%  |   _%   |     $__     |
DeepSeek-R1 |   _%   |     _%    |    _%   |    _%    |     _%    |  _%  |   _%   |     $__     |
Qwen Math   |   _%   |     _%    |    _%   |    _%    |     _%    |  _%  |   _%   |     $__     |
```

**Optimal Model Recommendation per Subject**:

```
Algebra    → [Best model] (accuracy __%, cost $__)
Factoring  → [Best model]
Geometry   → [Best model] (probably a reasoning model)
Calculus   → [Best model]
...
```

### Step 4: Voting/Cross-Verification Test

**Improving accuracy by using multiple models when confidence is low**:

```
Flow:
1. Primary model (optimal model per subject) grades
2. confidence ≥ threshold → Result confirmed
   (threshold managed in admin_settings)
3. confidence < threshold → Re-grade with secondary model
4. Primary and secondary agree → Result confirmed
5. Disagree → Deploy tertiary model → Majority vote (voting)
6. All 3 models differ → "Manual review needed" flag
```

**What Must Be Measured**:

- Single model accuracy vs voting accuracy comparison
- Cost increase rate from voting (depends on percentage of problems with confidence < threshold)
- Optimal confidence threshold exploration

### Step 5: SymPy/Maxima Integration for Additional Accuracy Improvement R&D

**Pipeline where SymPy/Maxima verifies after LLM generates an answer**:

```
When LLM says "The answer is (x+1)(x+2)":
1. Parse LLM answer → (x+1)(x+2)
2. Expand with SymPy: x² + 3x + 2
3. SymPy equivalence check against correct answer
4. If match, confirmed; if mismatch, LLM was wrong
```

**R&D Deliverables**:

- Accuracy change when adding SymPy/Maxima verification
- Which types benefit most
- Additional latency

---

## Task 4: Equivalence Recognition Engine - Maxima vs Gemini Comparison Verification

**Assignee**: (TBD)
**Priority**: Highest (key selling point)
**Goal**: Prove that Maxima can replace Wolfram and that its accuracy is truly superior compared to Gemini

### Background

> "Maxima is actually what I consider our key selling point"
> "There's an open-source option, so there's no need to use Wolfram. We can run it locally"

### Step 1: Environment Setup

```bash
# SymPy (Python)
pip install sympy

# Maxima (~5GB)
# macOS
brew install maxima
# Ubuntu
sudo apt install maxima
```

### Step 2: Prepare Test Cases

**Equivalence test set by difficulty (minimum 50 pairs)**:

```
Category 1: Basic Equivalence (SymPy sufficient)
- x+1 ↔ 1+x
- 2x+4 ↔ 2(x+2)
- x²+2x+1 ↔ (x+1)²

Category 2: Intermediate Equivalence (Testing SymPy limits)
- sin²x + cos²x ↔ 1
- (a+b)(a-b) ↔ a²-b²
- ln(e^x) ↔ x

Category 3: Advanced Equivalence (Where Maxima is needed)
- Complex trigonometric identities
- Multivariable indefinite integrals
- Series convergence determination

Category 4: Non-Equivalence (Detecting wrong answers)
- x+1 vs x+2 (obviously different)
- x² vs 2x (look similar but different)
- sin(2x) vs 2sin(x) (common mistake)

Category 5: Edge Cases
- 0/0 (undefined)
- ∞ related
- Conditional equivalence (equal only in certain ranges)
```

### Step 3: Three-Way Comparison Test

| Test Subject | Equivalence Method                                       | Cost         |
| ------------ | -------------------------------------------------------- | ------------ |
| SymPy        | `sympy.simplify(expr1 - expr2) == 0`                     | Free (local) |
| Maxima       | `is(ratsimp(expr1 - expr2) = 0)`                         | Free (local) |
| Gemini       | Prompt: "Determine if these two formulas are equivalent" | API cost     |

### Step 4: Required Deliverables

**Accuracy Comparison Table**:

```
              | Basic | Inter. | Advanced | Non-equiv. | Edge | Overall | Cost | Speed  |
SymPy         |   _% |    _%  |     _%   |      _%    |  _% |    _%   | Free | __ms  |
Maxima        |   _% |    _%  |     _%   |      _%    |  _% |    _%   | Free | __ms  |
Gemini        |   _% |    _%  |     _%   |      _%    |  _% |    _%   | $__  | __ms  |
SymPy+Maxima  |   _% |    _%  |     _%   |      _%    |  _% |    _%   | Free | __ms  |
```

**Answers to Key Questions**:

1. **Can Maxima replace Wolfram?**
    - [ ] Yes / [ ] Partially / [ ] No
    - Evidence: \_\_\_\_

2. **Is Maxima superior to Gemini for equivalence determination?**
    - [ ] Clearly superior / [ ] Similar / [ ] Gemini is better
    - Which categories show differences: \_\_\_\_

3. **Is the 3-stage pipeline (SymPy → Maxima → LLM) effective?**
    - Percentage resolved by SymPy: \_\_\_%
    - Percentage that goes to Maxima: \_\_\_%
    - Percentage that goes to LLM: \_\_\_%

**Finding What Gemini Can't Do** (point to show in meeting):

> "We need to show what Gemini can't do"

- Collect at least 3-5 equivalence cases where Gemini fails
- Show that Maxima gets the same cases correct
- → "LLMs are non-deterministic, Maxima is deterministic and accurate" message

---

## Summary: Pre-Meeting Checklist

| #   | Task                           | Key Deliverable                                                                                                                        |
| --- | ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | GraphRAG Schema + MVP          | Schema SQL + 3 scenario demos (admin threshold duplicate detection + flexible intent-based grading + cross-unit wrong answer analysis) |
| 2   | Gemini LoRA Test               | Accuracy improvement, cost, programmatic feasibility table                                                                             |
| 3   | LLM Subject Benchmark + Voting | Model x Subject accuracy matrix + voting accuracy improvement numbers                                                                  |
| 4   | Maxima vs Gemini Comparison    | Accuracy comparison table + "cases where Gemini fails but Maxima succeeds"                                                             |

**Suggested Personnel Assignment (3 people)**:

- **A**: Task 1 (GraphRAG) - Largest and most important
- **B**: Task 3 (LLM Benchmark) + Task 4 (Maxima Comparison) - Highly related, combine
- **C**: Task 2 (LoRA) - Can proceed independently

---

_Document created: 2026-03-05_
