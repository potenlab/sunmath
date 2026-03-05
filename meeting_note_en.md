# SunMath Meeting Preparation - Complete Detailed Summary

> This document was created by analyzing the full 39-minute meeting recording and the client's question PDF

---

## 1. Project Overview

### 1.1 Client Information
- **Company Name**: SunMath
- **Location**: Daechi-dong
- **Industry**: Math Academy
- **Scale**: Estimated to be a fairly large academy (has a waitlist, creates its own textbooks)

### 1.2 Project Scope (What the Client Wants)
The client wants not just a simple grading engine, but a **complete math learning platform**:

1. **Automated Problem Generation** - AI creates problems
2. **Automated Answer Generation** - AI also creates answers
3. **Automated Grading** - Grading student answers
4. **Wrong Answer Analysis** - Personalized learning based on incorrect answers
5. **Problem Review** - Verification of generated problems/answers

> "Basically, it seems like they want to do everything... Obviously in Phase 1 it'll just be an MVP, but this seems like a project that could grow through Phase 2 and 3"

### 1.3 Meeting Objective
- **No finished product needed**
- **Just need to show "we can do this"**
- Being able to answer client questions 1, 2, 3, and 4 is enough

> "Basically, we just need to show them that we can do this, that we're pretty good at it"

### 1.4 Meeting Format
- 1-hour presentation
- Interactive dialogue (not a one-way presentation)
- Daehyun + another team member will attend and have a conversation
- Need 1 internal meeting before the client meeting

---

## 2. Detailed Analysis of Client's 5 Questions

### Question 1: Problem Registration - HWP/OCR Formula Normalization & Duplicate Problem Prevention

#### Client's Original Question:
> "Although commercial OCR performance has improved, there are still formula symbol recognition errors and subtle text differences from HWP parsing data. We'd like to hear your thoughts on specific formula normalization logic that can overcome these source differences (HWP vs OCR) and identify cases where expressions like x+1 and 1+x look different but have the same mathematical structure. We're also curious about how you would improve the accuracy of duplicate problem registration prevention."

#### Answer Discussed in Meeting:

**Resolving HWP vs OCR Source Differences:**
- Whether it's HWP or anything else, **convert everything to images → OCR** solves the source difference problem
- "If you just convert HWP to an image and OCR it, that should work"

**Formula Equivalence Determination:**
- This connects to Question 2 (using SymPy, Maxima)

**Duplicate Problem Registration Prevention - Key Insight:**

> "What criteria do you use to determine a problem is a duplicate? There's no standard for that either. Like, if you just change one number, is it the same problem or a different problem?"

- The client is thinking in terms of **tiers**:
  - Same type of problem
  - Same concept problem
  - Similarity percentage, etc.

**Our Proposal - Intent-Based Vector Search:**

> "I don't think vectorizing the problems themselves is very meaningful. Problems can be really long... Instead, I think we should just **extract the problem's intent** and search for problems with similar intents in a vector DB"

- Instead of vectorizing the problem itself
- **Extract the problem's intent (assessment goal)** and vectorize that
- Search by similarity in a vector DB
- This is **connected to GraphRAG**

---

### Question 2: Grading Engine Architecture (Most Important!)

#### Client's Original Question:
> "For the grading engine, we've drafted a structure using Gemini for OCR, then Stage 1 SymPy, Stage 2 Gemini, Stage 3 Wolfram. Currently, Gemini has the best performance for handwriting OCR - should we build a separately trained model, or how can we improve handwriting OCR accuracy through Gemini? We're curious about dual verification logic using Gemini's confidence scores and prompt optimization strategies for improving recognition rates. (Commercial auto-grading engines advertise ~95% accuracy.)
>
> Also, after grading sheet OCR, in the process of determining semantic equivalence, we want to design the system so that the number of times it reaches Stage 3 Wolfram converges to 0 through precedent registration. (Cost issue)"

#### Key Content Discussed in Meeting:

---

##### 2.1 Formula Equivalence Pipeline (Key Selling Point!)

**SymPy (Stage 1):**
- About 50MB, very lightweight
- Basic formula equivalence determination

**Maxima (Stage 2) - Key Differentiator:**
> "I was planning to use Maxima, a heavier engine with a GPL license. It's about 5GB. It's really good at determining formula equivalence."

> "Maxima is actually what I consider our key selling point"

> "There's an open-source option, so there's no need to use Wolfram. We can run it locally"

**Wolfram Discussion:**
> "If they're using Wolfram Alpha and Mathematica, wouldn't they have to disclose that in the presentation because of licensing?"

> "They must have a contract with Wolfram and Mathematica. A paid contract. So to sell it commercially, unless you open-source your code, you need a contract with them. Otherwise, you'll get sued. That GPL license thing..."

**Conclusion:**
- **Can replace Wolfram with Maxima (GPL, free)**
- Can run locally
- This is the **key cost reduction point**

---

##### 2.2 Precedent Caching System

> "If equivalence is confirmed - when a different answer comes in but it's determined to be equivalent, **put it in the cache**..."

> "If answers are in the DB, you don't always have to solve the problem again. **Once you solve a problem once**, from then on you just need to check equivalence, so it can be much lighter"

**Core Logic:**
1. First grading: Call API for equivalence determination
2. Save result to DB (precedent registration)
3. From then on: Instant determination via DB lookup, 0 API calls

> "You only need to solve each problem once, so that much is..."

---

##### 2.3 LLM Non-Determinism Problem & Solutions

**Problem Recognition:**
> "It's not about leaving everything to the LLM... LLMs are actually very non-deterministic. They might say correct then say incorrect, so it's hard to trust them completely"

> "So I think it's best to **use internal classic algorithms as much as possible** and have the LLM use tools that run those algorithms"

**Solution 1: Classic Algorithms First**
- Don't rely on LLMs
- Use **deterministic algorithms** like SymPy, Maxima as the main engine
- Use LLMs only as supplementary

**Solution 2: LLM Cross-Verification (Cross-check)**
> "Cross-verification seems really necessary. Because it could be wrong too, and LLMs can obviously be wrong too"

> "For example, if an LLM solved a problem and the confidence percentage for the answer is below 90%... if it's below 90%, **have another LLM solve it together** for cross-checking"

**Solution 3: Leveraging LLM-Specific Subject Strengths**
> "Among LLMs, there are those that are really good at pure math. About 7 models. Including DeepSeek and other affordable ones"

> "Looking at open-source models these days, people find what each model is good at. Similarly, **each model probably has subjects it's good at**"

> "For example, geometry obviously can't be done well by models without reasoning. Geometry requires thinking. So for those, you might only use o1 or similar"

**Proposed Testing:**
> "I wanted to **test which models are good at which subjects** using various models. I wanted to check what models are good at what"

---

##### 2.4 LoRA Fine-Tuning (Using Google Vertex AI)

> "I think **LoRA would be good for recognizing each person's handwriting**"

> "If that works well, **this could be our selling point**"

**Concerns:**
> "But you'd have to create one for each student... So we need to look at **how cost-effective** it is. The LoRA adapters..."

**Google Vertex AI Mention:**
> "Using LoRA and **looking at results from LoRA on Vertex AI** and comparing accuracy across commercial models... comparing cost-effectiveness across all of them"

**Items Requiring Testing:**
1. Whether LoRA fine-tuning is feasible
2. LoRA results on Google Vertex AI
3. Accuracy comparison with commercial models
4. Cost-effectiveness comparison

---

##### 2.5 Handwriting OCR Accuracy Improvement

**Current Situation:**
- Gemini has the best handwriting OCR performance
- Commercial auto-grading engines advertise 95% accuracy

**Proposed Methods:**

1. **Using Gemini Confidence Scores:**
   - 90% or higher → Grade immediately
   - Below 90% → Cross-verify with another LLM

2. **Leveraging LLM-Specific Strengths:**
   - Different models excel at different subjects
   - Geometry: reasoning models (o1, etc.)
   - Algebra: general models work fine

3. **LoRA Fine-Tuning:**
   - Adapting to each student's handwriting
   - Using Google Vertex AI

---

### Question 3: GraphRAG (Phase 2)

#### Client's Original Question:
> "We plan to introduce GraphRAG in Phase 2. During Phase 1 development, beyond simply storing problem and student data, we're curious about your plans for designing a DB schema that extracts relationships (Edges) between 'concept-problem-wrong answer cause' and is expandable in graph form."

#### Key Content Discussed in Meeting:

---

##### 3.1 GraphRAG Connects to All Questions

> "I think this all connects to GraphRAG. Ultimately, each problem probably has a **goal** in terms of what it represents and what knowledge it's trying to verify"

> "If what the problem aims to achieve has been accomplished, then the equivalence can be confirmed"

**Key Insight - GraphRAG Needed Even for Equivalence Determination:**

> "It's not just mathematical... AI needs to be used to determine equivalence... This is all connected to GraphRAG"

**Example:**
> "Say there's a very complex expression and a simple 1, and they're equivalent. But if the answer is 1 and someone puts a very complex expression there, **would you accept that as correct?**"

> "To determine whether those are correct or not, you **first need to know what this problem is trying to evaluate**"

---

##### 3.2 Problem Intent is Key

> "Not just the purpose of this unit, but **which units this unit is connected to**, and then defining **what knowledge this problem is trying to verify**, and then determining that all of those have been resolved so the student's answer can be considered correct"

> "**The problem's intent is what matters. We need to look at the problem's intent to judge the answer**"

---

##### 3.3 GraphRAG Application Scope

**Question 1 (Duplicate Problem Registration Prevention):**
- Extract problem intent → Vectorize → Similarity search

**Question 2 (Grading Engine):**
- Need to understand problem intent before equivalence determination
- "Is this problem evaluating factoring or expansion?"

**Question 3 (GraphRAG Itself):**
- Concept-problem-student-unit relationships

**Question 4 (Wrong Answer Notebook):**
- Wrong problem → What concept is lacking → Analysis

---

##### 3.4 GraphRAG Implementation Method

> "GraphRAG DB is basically just using **PostgreSQL** or something similar, using multiple tables and creating Edge tables"

> "We just give it to Claude and it'll work. The feeling is that we won't design the schema ourselves, we'll have Claude do it"

**Infrastructure to Use:**
- AWS
- PostgreSQL (RDS or Aurora)

---

##### 3.5 GraphRAG as an Adapter

> "For Phase 1, just use SymPy for equivalence determination and then **use GraphRAG only for special cases?**"

> "So **GraphRAG as a lightweight adapter on the front end**... I don't think there are many other use cases"

> "That's what it's for, and the actual determination itself should be done by SymPy/Maxima. They're much better at it. Definitely more accurate"

**Example:**
- `x² + 2x + 1` vs `(x+1)²` → SymPy can directly determine equivalence
- When a factoring unit problem gets an expanded answer → GraphRAG needed (checking problem intent)

> "Students might write x² + 2x + 1 or (x+1)² in various ways. For those cases, there's actually no need to use GraphRAG. But **it might be a factoring unit. In exactly that case of a factoring unit**, it determines based on that"

> "**It does need to go through GraphRAG every time**"

---

##### 3.6 Demo Preparation

> "Should I try running GraphRAG? Or should I give you my server? It'd be great if you could try running it"

> "Then give me **that chat link you mentioned**. I understand about #3 too, **I'll make it in an MVP style**"

---

### Question 4: Wrong Answer Notebook (Dynamic Wrong Answer Management)

#### Client's Original Question:
> "We'll be continuously accumulating student wrong answer data, and one idea for this is a 'wrong answer warehouse.' Students' missed problems are collected, and if they solve them correctly again, they're removed from the list. This is 'dynamic wrong answer management.' The process of clearing correctly answered problems from the wrong answer warehouse should not be simple deletion but rather a method that preserves learning history while transitioning states."

#### Content Discussed in Meeting:

> "Question 4 is so easy... preserving history while transitioning states for students..."

> "That's what I was talking about, **all the personalized problem data accumulation happens. This all goes into GraphRAG**"

> "When they get a problem wrong or right, how this... how the concept works, how it affects this student's understanding of this unit"

**Conclusion:**
- Question 4 is easy
- But this is also **connected to GraphRAG**
- Wrong problem → Which concept is lacking → Understanding analysis

---

### Question 5: Most Confident Area / Expected Bottlenecks

#### Client's Original Question:
> "What part of the overall process are you most confident about, and which part do you expect will require the most physical time?"

#### Content Discussed in Meeting:

**Confident Areas:**
- Questions 1, 2 (building commercial auto-grading engines)
- > "Questions 1 and 2 are relatively easy, like building a commercial auto-grading engine"

**Difficult Areas:**
- Question 3 (GraphRAG)
- > "Question 3 looks really difficult"
- > "I actually didn't know GraphRAG well. It's not easy"

**Expected Bottlenecks:**
- **Problem Definition**
- > "Defining the problem is the problem. I think it'll take a long time"
- > "Let's take what we've recorded and **ask AI to do the Problem Definition**... Give it to Claude and when Claude extracts everything, we'll review it"

---

## 3. Additional Discussion Items

### 3.1 Scenario Where There's No Answer Key

> "Don't you need to look up the answer from the DB? From the answer sheet? **There might be no answer sheet. The scenario where there's no answer sheet.**"

> "The academy director might create problems. Then if the director writes the answer sheet by hand, you OCR it and register it in the DB, right?"

**Academy Textbook Answer Error Issue:**
> "Academy-provided problem sheets, commercial workbooks... **sometimes the answers are wrong**. For example, there might be typos. Apparently there are lots of complaints about things like that"

> "It'd be nice if we could **review/verify these kinds of things** too"

---

### 3.2 AI Problem Generation & Token Costs

> "If the AI gets a problem wrong, does it keep solving it? Then **AI tokens will keep being consumed**, can they handle that?"

> "And generating problems in the first place is the same. And **how to reduce that** was one issue"

**Solution:**
> "Most of the problems... almost all students solve the same problems. So as I said, if problems are in the DB and there are answers for those problems, you don't always need to solve the problems again. **Once you solve a problem once**, from then on you just need to check equivalence"

---

### 3.3 99.9% Accuracy Requirement

> "How do you make the answers 99.9% or more accurate? **There can't be any controversy about the correct answer**"

---

### 3.4 Commercial Auto-Grading vs Our Differentiators

> "What they mainly asked about felt like... the focus was on how to implement a commercial auto-grading engine"

> "On top of that, **differentiating with GraphRAG**, something like that"

> "Plus **leveraging the characteristics of each LLM**. Using different characteristics of each LLM, and for ones with lower confidence, trying multiple different ones..."

---

### 3.5 Development Process Introduction

> "If we show them how we usually do software development... These days we're just **making PRDs**. We have a tool we built for creating PRDs"

> "**There's a PRD generator**. Just type in an idea and it creates a PRD"

> "Once we have a PRD, we just build the app based on that PRD. So then just **run testing** - testing with Jest, Playwright, all these things that do it on their own. Opens a browser and does everything by itself... runs everything"

---

## 4. Demo/Test Checklist (What Team Members Need to Prepare)

### 4.1 LoRA Fine-Tuning Test (Google Vertex AI)

**Purpose**: Adapting handwriting recognition per student

**Preparation**:
- [ ] Set up Google Vertex AI environment
- [ ] Test LoRA fine-tuning feasibility
- [ ] Prepare handwriting sample data
- [ ] Compare accuracy before and after fine-tuning
- [ ] Cost efficiency analysis

**Expected Results**:
- If LoRA is feasible → Our selling point
- Cost efficiency is important since it needs to be created per student

---

### 4.2 SymPy + Maxima Equivalence Determination Demo (Core!)

**Purpose**: Prove that local formula equivalence determination is possible without Wolfram

**Preparation**:
- [ ] Install and test SymPy
  - `x+1` vs `1+x` → Equivalent
  - `x² + 2x + 1` vs `(x+1)²` → Equivalent
- [ ] Install Maxima (~5GB)
  - Verify GPL license
  - Test complex formula equivalence determination
- [ ] Implement 3-stage pipeline
  1. SymPy for first pass (lightweight)
  2. If fails, Maxima for second pass (heavy, local)
  3. If still fails, LLM

**Key Message**:
- "Everything possible locally without Wolfram, zero cost"
- "We need to show what Gemini can't do"

---

### 4.3 Precedent Caching DB Schema Design

**Purpose**: Once an answer is determined, store in DB, zero API calls afterwards

**Preparation**:
- [ ] Design precedent table schema
  ```sql
  CREATE TABLE answer_cache (
    problem_id UUID,
    student_answer TEXT,
    canonical_answer TEXT,
    is_equivalent BOOLEAN,
    judged_at TIMESTAMP,
    judged_by VARCHAR(50), -- 'sympy', 'maxima', 'llm'
    PRIMARY KEY (problem_id, student_answer)
  );
  ```
- [ ] Cache hit rate simulation

---

### 4.4 LLM Subject-Specific Testing

**Purpose**: Evaluate which LLM excels at which math subject

**Preparation**:
- [ ] List of models to test (~7)
  - DeepSeek
  - Claude
  - GPT-4
  - Gemini
  - o1 (reasoning model)
  - Other affordable models
- [ ] Prepare test problems per subject
  - Algebra
  - Geometry (requires reasoning)
  - Calculus
  - Probability/Statistics
- [ ] Measure accuracy per model
- [ ] Cost-effectiveness analysis

**Expected Results**:
- Geometry: reasoning models like o1 perform well
- Algebra: general models are OK
- Can route by model

---

### 4.5 LLM Confidence-Based Cross-Verification Flow

**Purpose**: Cross-check with another LLM when confidence is below 90%

**Preparation**:
- [ ] Confidence score extraction logic
- [ ] Cross-verification flow design
  ```
  LLM A grades → confidence ≥ 90% → Result confirmed
                → confidence < 90% → Re-grade with LLM B
                                    → Both agree → Result confirmed
                                    → Both disagree → LLM C or manual review
  ```
- [ ] Prepare test cases

---

### 4.6 GraphRAG Adapter MVP

**Purpose**: For understanding problem intent (checked before equivalence determination)

**Preparation**:
- [ ] PostgreSQL-based graph structure table design
  ```
  Problem(node) ←→ Concept(node) ←→ Unit(node)
  Problem(node) ←→ Assessment Goal(node)
  Unit(node) ←→ Prerequisite Unit(edge)
  ```
- [ ] Try generating schema with Claude
- [ ] Query testing with sample data
  - "What concept is this problem trying to evaluate?"
  - "Is an expanded answer correct in a factoring unit?"
- [ ] Utilize A2B server

**Infrastructure**:
- AWS (RDS PostgreSQL or Aurora)

---

### 4.7 Intent-Based Vector Search (Duplicate Problem Registration Prevention)

**Purpose**: Vectorize the intent rather than the problem itself for similarity search

**Preparation**:
- [ ] Problem intent extraction pipeline
  1. Problem text → LLM extracts "what concept this problem evaluates"
  2. Intent vectorization
- [ ] Select vector DB (Pinecone, Chroma, etc.)
- [ ] Define similarity tiers
  - 100% identical → Reject registration
  - 80-99% similar → "Similar problem exists" alert
  - 50-79% → Register as same-type problem

---

### 4.8 HWP → Image → OCR Pipeline

**Purpose**: Resolve HWP/PDF source differences

**Preparation**:
- [ ] HWP → PDF conversion
- [ ] PDF → Image conversion
- [ ] Gemini Vision OCR test
- [ ] Verify LaTeX conversion results

**Expected Results**:
- "If you just convert HWP to an image, you can OCR it"
- Solves the source difference problem

---

## 5. Pre-Meeting Checklist

### 5.1 Internal Meeting
- [ ] 1 internal meeting before the client meeting
- [ ] Share individually prepared demos
- [ ] Role assignment (Daehyun + another member)
- [ ] Prepare expected Q&A answers

### 5.2 Materials Needed
- [ ] Laptop (for demos)
- [ ] PRD based on recording transcript
- [ ] Demo videos/screenshots

---

## 6. Key Message Summary

### 6.1 Cost Reduction
- Local equivalence determination with Maxima (GPL) without Wolfram → API cost $0
- Precedent caching means each problem only needs to be solved once

### 6.2 Accuracy Improvement
- Supplement LLM non-determinism with classic algorithms (SymPy, Maxima)
- Leverage LLM-specific strengths (subject-based routing)
- Confidence-based cross-verification

### 6.3 Differentiators
- Problem intent understanding through GraphRAG
- From simple equivalence determination → Intent-based determination
- Personalized learning analysis (wrong answers → identify weak concepts)

### 6.4 Scalability
- MVP → Project can grow through Phase 2 and 3
- Covers entire flow: problem generation, answer creation, grading, wrong answer analysis

---

## 7. Proposed Task Assignment by Person

| Task | Priority | Estimated Time | Assignee | Notes |
|------|----------|----------------|----------|-------|
| SymPy + Maxima Equivalence Determination | **Highest** | 1-2 days | | Key selling point |
| Precedent Caching DB Design | **Highest** | 0.5 days | | Key cost reduction point |
| LLM Subject-Specific Testing | High | 2-3 days | | 7 models x multiple subjects |
| LoRA + Vertex AI Testing | High | 1-2 days | | Cost efficiency review needed |
| GraphRAG MVP | Medium | 2-3 days | | Generate with Claude, collaborate |
| Confidence Cross-Verification | Medium | 1 day | | Flow design only |
| Problem Intent Vector Search | Medium | 1-2 days | | Need to select vector DB |
| HWP → OCR Pipeline | Low | 0.5 days | | Basic functionality, not difficult |

---

## 8. Reference Materials

### 8.1 Technical Keywords Summary

| Keyword | Description | Use |
|---------|-------------|-----|
| SymPy | Python formula library, 50MB | Stage 1 equivalence determination |
| Maxima | GPL math engine, 5GB, local | Stage 2 equivalence determination, Wolfram replacement |
| Gemini | Google LLM | Best handwriting OCR performance |
| LoRA | Low-Rank Adaptation | Per-student handwriting fine-tuning |
| Google Vertex AI | Google Cloud ML Platform | LoRA fine-tuning environment |
| GraphRAG | Graph + RAG | Problem-concept-student relationships |
| AWS RDS | AWS Database | PostgreSQL hosting |
| PostgreSQL | Relational DB | GraphRAG implementation |
| DeepSeek | Math-specialized LLM | Affordable and good at math |
| o1 | OpenAI reasoning model | Problems requiring reasoning like geometry |

### 8.2 File Locations
- Recording transcript: `/Users/2303-pc02/Downloads/output_transcript.txt`
- Client question PDF: `/Users/2303-pc02/Downloads/AI LaTeX Auto-Grading Proposal.pdf`
- JSON (with timestamps): `/Users/2303-pc02/Downloads/output_transcript.json`

---

## 9. Original Quote Collection

### LoRA Related
> "I think LoRA would be good for recognizing each person's handwriting"
> "If that works well, this could be our selling point"
> "But you'd have to create one for each student... So we need to look at how cost-effective it is"

### Maxima/Wolfram Related
> "I was planning to use Maxima, a heavier engine with a GPL license. It's about 5GB"
> "Maxima is actually what I consider our key selling point"
> "There's an open-source option, so there's no need to use Wolfram"

### LLM Cross-Verification Related
> "LLMs are actually very non-deterministic. They might say correct then say incorrect"
> "If the confidence percentage is below 90%... have another LLM solve it together for cross-checking"

### GraphRAG Related
> "I think this all connects to GraphRAG"
> "The problem's intent is what matters. We need to look at the problem's intent to judge the answer"
> "It does need to go through GraphRAG every time"

### Vertex AI Related
> "Using LoRA and looking at results from LoRA on Vertex AI and comparing accuracy across commercial models"

### Meeting Objective Related
> "Basically, we just need to show them that we can do this, that we're pretty good at it"
> "If we can show them we can solve questions 1, 2, 3, and 4"

---

*Document created: 2026-03-05*
*Total length: ~1,200 lines*
