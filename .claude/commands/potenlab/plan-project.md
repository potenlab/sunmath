---
name: potenlab:plan-project
description: Orchestrate project planning with specialist agents (includes test plan generation)
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - Task
  - AskUserQuestion
  - WebFetch
  - WebSearch
---

<objective>
Orchestrate a complete project planning workflow with sequential agent handoff and parallel specialist execution. Creates all plan files from a PRD, including test-plan.md for downstream test generation.
</objective>

<execution_context>
Read and apply rules from @/Users/muhammadrayandika/Documents/repository/sunmath/.claude/potenlab-workflow/CLAUDE.md before proceeding.
</execution_context>

<process>

## Orchestration Flow

```
/potenlab:plan-project
  |
  v
+----------------------------------------------------------+
|  STEP 1: AskUserQuestion (MANDATORY)                     |
|  - Validate user intent                                   |
|  - Locate PRD / gather project description                |
|  - Clarify scope, tech stack, priorities                  |
+----------------------------------------------------------+
  |
  v
+----------------------------------------------------------+
|  STEP 2: Ensure /docs directory                           |
+----------------------------------------------------------+
  |
  v
+----------------------------------------------------------+
|  STEP 3: Spawn potenlab-ui-ux-specialist (SEQUENTIAL)    |
|  - Reads PRD                                              |
|  - Writes: docs/ui-ux-plan.md                            |
+----------------------------------------------------------+
  |
  v
+----------------------------------------------------------+
|  STEP 4: Spawn potenlab-tech-lead-specialist (SEQUENTIAL)|
|  - Reads: docs/ui-ux-plan.md                             |
|  - Writes: docs/dev-plan.md                              |
+----------------------------------------------------------+
  |
  v
+----------------------------------------------------------+
|  STEP 5: PARALLEL — frontend + backend specialists       |
|                                                           |
|  potenlab-frontend-specialist ──Read──> docs/dev-plan.md  |
|                               ──Write─> docs/frontend-plan.md |
|                                                           |
|  potenlab-backend-specialist  ──Read──> docs/dev-plan.md  |
|                               ──Write─> docs/backend-plan.md  |
+----------------------------------------------------------+
  |
  v
+----------------------------------------------------------+
|  STEP 6: Spawn potenlab-qa-specialist (SEQUENTIAL)       |
|  - Reads: docs/dev-plan.md + docs/backend-plan.md        |
|  - Writes: docs/test-plan.md                             |
+----------------------------------------------------------+
  |
  v
+----------------------------------------------------------+
|  STEP 7: Report completion with file summary              |
+----------------------------------------------------------+
```

---

## Step 1: Validate User Intent (MANDATORY)

**You MUST use AskUserQuestion before spawning any agents. Never skip this step.**

### 1.1 Locate PRD

Search for the PRD file first:

```
Glob: **/prd.md
Glob: **/PRD.md
Glob: docs/prd.md
```

### 1.2 Ask User — Project Scope

**ALWAYS ask this question regardless of PRD existence.**

```
AskUserQuestion:
  question: "What would you like to plan? Please confirm the scope."
  header: "Plan Scope"
  options:
    - label: "Full project from PRD"
      description: "Plan the entire project from the PRD file"
    - label: "Specific feature only"
      description: "Plan a single feature or module"
    - label: "I'll describe it now"
      description: "No PRD — I'll describe what to plan"
```

### 1.3 Ask User — PRD Location (if not found automatically)

```
AskUserQuestion:
  question: "Where is your PRD file located?"
  header: "PRD Path"
  options:
    - label: "docs/prd.md (Recommended)"
      description: "Standard location in docs folder"
    - label: "prd.md (root)"
      description: "In the project root directory"
    - label: "I'll provide the path"
      description: "Enter a custom file path"
```

### 1.4 Ask User — UI/UX Priority

```
AskUserQuestion:
  question: "What is the UI/UX priority for this project?"
  header: "UI Priority"
  options:
    - label: "Speed to market (Recommended)"
      description: "Use shadcn defaults, minimal customization"
    - label: "Custom brand design"
      description: "Detailed design system, unique visual identity"
    - label: "Accessibility first"
      description: "WCAG AAA compliance, inclusive design"
```

### 1.5 Ask User — Tech Stack (if not specified in PRD)

```
AskUserQuestion:
  question: "What tech stack should we use?"
  header: "Tech Stack"
  options:
    - label: "Next.js + Supabase (Recommended)"
      description: "Full-stack React with Postgres backend"
    - label: "React + Express + PostgreSQL"
      description: "Traditional stack with Node backend"
    - label: "Already specified in PRD"
      description: "Use what's defined in the PRD"
```

### Question Rules

- **MANDATORY:** You MUST ask at least the Plan Scope question (1.2) before proceeding
- Ask a maximum of **5 questions total**
- Skip questions that are already answered in the PRD
- Track: `questionsAsked` (start at 0, stop at 5)
- Do NOT proceed to Step 2 until user has answered

---

## Step 2: Ensure /docs Directory

Before spawning agents, ensure the output directory exists:

```
Bash: mkdir -p docs
```

---

## Step 3: Spawn potenlab-ui-ux-specialist (SEQUENTIAL)

**This agent runs FIRST, alone. It creates the design foundation that all other plans depend on.**

```
Task:
  subagent_type: potenlab-ui-ux-specialist
  description: "Create UI/UX plan"
  prompt: |
    Read the PRD at: {prd_path}

    User preferences:
    - UI Priority: {ui_priority from Step 1.4}
    - Tech Stack: {tech_stack from Step 1.5}
    - Scope: {scope from Step 1.2}

    Write your complete ui-ux-plan.md to: docs/ui-ux-plan.md

    Include:
    - User research and personas
    - Information architecture
    - User flows
    - Design system (colors, typography, spacing)
    - Component library specifications
    - Wireframes for all key pages
    - Accessibility checklist (WCAG 2.1 AA minimum)
    - Micro-interactions and animation guidelines
    - Implementation guidelines for developer handoff

    Write the file using the Write tool. Return "Done: docs/ui-ux-plan.md" when complete.
```

**Wait for this agent to complete before proceeding to Step 4.**

After the agent completes, verify the file was created:

```
Glob: docs/ui-ux-plan.md
```

If the file does not exist, report the error and stop. Do NOT proceed.

---

## Step 4: Spawn potenlab-tech-lead-specialist (SEQUENTIAL)

**This agent runs SECOND. It reads ui-ux-plan.md and creates the single source of truth dev-plan.md.**

```
Task:
  subagent_type: potenlab-tech-lead-specialist
  description: "Create dev plan from UI/UX"
  prompt: |
    Read the UI/UX plan at: docs/ui-ux-plan.md
    Also read the PRD at: {prd_path}

    Create dev-plan.md as the SINGLE SOURCE OF TRUTH for this project.

    Translate the design decisions, wireframes, component specs, and accessibility
    requirements from ui-ux-plan.md into a minimal, phased development checklist.

    Phases:
    - Phase 0: Foundation (project setup, design tokens)
    - Phase 1: Backend (schema, API, RLS)
    - Phase 2: Shared UI (src/components/)
    - Phase 3: Features (src/features/)
    - Phase 4: Integration (routing, API wiring)
    - Phase 5: Polish (a11y, animations)

    Every task must have:
    - Output: file paths or artifacts
    - Behavior: how it works
    - Verify: concrete check steps

    Write the file to: docs/dev-plan.md
    Do NOT create progress.json — that is handled separately.

    Write the file using the Write tool. Return "Done: docs/dev-plan.md" when complete.
```

**Wait for this agent to complete before proceeding to Step 5.**

After the agent completes, verify the file was created:

```
Glob: docs/dev-plan.md
```

If the file does not exist, report the error and stop. Do NOT proceed.

---

## Step 5: Spawn potenlab-frontend-specialist + potenlab-backend-specialist (PARALLEL)

**These two agents run IN PARALLEL. Both read dev-plan.md and write their own specialist plans.**

**CRITICAL: Spawn both agents in a SINGLE message with two Task tool calls.**

```
[Single message with 2 Task tool calls]

Task 1: potenlab-frontend-specialist
  subagent_type: potenlab-frontend-specialist
  description: "Create frontend plan"
  prompt: |
    Read the dev plan at: docs/dev-plan.md
    Also read the UI/UX plan at: docs/ui-ux-plan.md for design context.

    Create frontend-plan.md with detailed component specifications:
    - Exact file paths following Bulletproof React structure
    - TypeScript interfaces and props for every component
    - shadcn component discovery and mapping
    - Business components (features/) vs styled components (components/) separation
    - Data fetching hooks with React Query
    - State management approach
    - Performance checklist (Vercel React best practices)
    - Accessibility checklist
    - Component index table

    Write the file to: docs/frontend-plan.md
    Write the file using the Write tool. Return "Done: docs/frontend-plan.md" when complete.

Task 2: potenlab-backend-specialist
  subagent_type: potenlab-backend-specialist
  description: "Create backend plan"
  prompt: |
    Read the dev plan at: docs/dev-plan.md
    Also read the UI/UX plan at: docs/ui-ux-plan.md for user flow context.

    Create backend-plan.md with detailed backend specifications:
    - Table definitions with columns, types, constraints, defaults
    - Migration SQL (copy-paste ready)
    - RLS policies with concrete SQL
    - Index specifications (especially FK indexes)
    - Query specifications for each frontend feature
    - Connection strategy (pooling, timeouts)
    - Schema diagram
    - Migration execution order
    - Anti-patterns to avoid

    Write the file to: docs/backend-plan.md
    Write the file using the Write tool. Return "Done: docs/backend-plan.md" when complete.
```

**Wait for BOTH agents to complete before proceeding to Step 6.**

---

## Step 6: Spawn potenlab-qa-specialist (SEQUENTIAL) — Generate Test Plan

**This agent reads dev-plan.md and backend-plan.md to create a comprehensive test plan that maps every feature to testable scenarios. This test-plan.md is later consumed by `/potenlab:generate-test`.**

```
Task:
  subagent_type: potenlab-qa-specialist
  description: "Create test plan"
  prompt: |
    You are generating a TEST PLAN document — NOT test code.

    Read these files first (MANDATORY):
    - docs/dev-plan.md (single source of truth — all phases and tasks)
    - docs/backend-plan.md (schema, RLS policies, constraints, queries)

    Also read if available:
    - docs/frontend-plan.md (component specs, data fetching patterns)

    Create docs/test-plan.md with the following structure:

    # Test Plan

    ## Overview
    - Project name and description (from dev-plan.md)
    - Testing approach: behavior-driven, Vitest + Supabase local
    - No UI/browser testing — database behavior only

    ## Test Infrastructure
    - Vitest configuration requirements
    - Supabase local setup (http://127.0.0.1:54321)
    - Shared test utilities needed (admin client, auth helpers)
    - Environment variables (SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY)

    ## Phase-by-Phase Test Scenarios

    For EACH phase in dev-plan.md that has backend/data tasks:

    ### Phase {N}: {name}

    #### {feature_name}
    - Tables involved: (from backend-plan.md)
    - RLS policies: (list each policy)
    - Test file: tests/features/{name}/{name}.test.ts

    CRUD Tests:
    - [ ] Create with valid data → verify inserted
    - [ ] Create with missing required fields → expect error
    - [ ] Read own data → verify returned
    - [ ] Update own data → verify changed
    - [ ] Delete own data → verify removed

    RLS Policy Tests:
    - [ ] Owner can SELECT own rows
    - [ ] Other user CANNOT SELECT owner's rows
    - [ ] Owner can INSERT with own user_id
    - [ ] (map ALL policies from backend-plan.md)

    Constraint Tests:
    - [ ] NOT NULL violations for each required column
    - [ ] UNIQUE constraint violations
    - [ ] CHECK / FK constraint violations

    Edge Cases:
    - [ ] Empty string inputs, boundary values

    ## Test Priority Matrix
    ## Summary (total features, scenarios, estimated test files)

    IMPORTANT:
    - This is a PLAN document, not test code. Write markdown, not TypeScript.
    - Map every RLS policy from backend-plan.md to specific test scenarios.
    - Skip purely frontend tasks (CSS, layout, design tokens).

    Write the file to: docs/test-plan.md
    Write the file using the Write tool. Return "Done: docs/test-plan.md" when complete.
```

**Wait for this agent to complete before proceeding to Step 7.**

---

## Step 7: Report Completion

After all agents have completed, provide a summary:

```markdown
## Project Planning Complete

### Plans Created

| # | File | Agent | Description |
|---|------|-------|-------------|
| 1 | docs/ui-ux-plan.md | potenlab-ui-ux-specialist | Design system, wireframes, user flows, accessibility |
| 2 | docs/dev-plan.md | potenlab-tech-lead-specialist | Single source of truth — phased development checklist |
| 3 | docs/frontend-plan.md | potenlab-frontend-specialist | Component specs, file paths, props, patterns |
| 4 | docs/backend-plan.md | potenlab-backend-specialist | Schema, migrations, RLS policies, queries |
| 5 | docs/test-plan.md | potenlab-qa-specialist | Test scenarios mapped to features, RLS, constraints |

### Next Steps

1. Review `docs/dev-plan.md` for the full task breakdown
2. Review `docs/test-plan.md` for test coverage mapping
3. Use `/potenlab:complete-plan` to generate progress.json
4. Use `/potenlab:generate-test` to generate .test.ts files from test-plan.md
```

---

## Error Handling

### PRD Not Found
```
1. AskUserQuestion for the path
2. If still not found, ask user to create one
3. Do NOT proceed without a valid PRD or project description
```

### Agent Fails (ui-ux or tech-lead)
```
1. Report which agent failed
2. Do NOT proceed to downstream agents
3. Ask user to fix the issue and re-run
```

### frontend or backend Specialist Fails
```
1. Report which specialist failed
2. The other specialist's output is still valid
3. Proceed to qa-specialist (it only requires dev-plan.md; backend-plan.md is enrichment)
```

### qa-specialist Fails
```
1. Report the error
2. All other plan files are still valid — proceed to report
3. User can re-run qa-specialist later or create test-plan.md manually
```

---

## Token Optimization

**File-based handoff — agents WRITE files, downstream agents READ files.**

```
CORRECT:
  potenlab-ui-ux-specialist     ──Write──> docs/ui-ux-plan.md
  potenlab-tech-lead-specialist ──Read───> docs/ui-ux-plan.md
  potenlab-tech-lead-specialist ──Write──> docs/dev-plan.md
  frontend/backend              ──Read───> docs/dev-plan.md
  potenlab-qa-specialist        ──Read───> docs/dev-plan.md + docs/backend-plan.md
  potenlab-qa-specialist        ──Write──> docs/test-plan.md

WRONG:
  Agent A returns content → passed in Agent B prompt
```

---

## Execution Rules

### DO:
- ALWAYS ask at least one AskUserQuestion before spawning agents
- ALWAYS run potenlab-ui-ux-specialist FIRST and ALONE
- ALWAYS wait for ui-ux-plan.md before spawning potenlab-tech-lead-specialist
- ALWAYS wait for dev-plan.md before spawning frontend + backend
- ALWAYS spawn frontend + backend in PARALLEL (single message, two Task calls)
- ALWAYS wait for backend-plan.md before spawning potenlab-qa-specialist
- ALWAYS verify output files exist after each agent completes
- ALWAYS ensure docs/ directory exists before any agent runs

### DO NOT:
- NEVER skip AskUserQuestion — user validation is mandatory
- NEVER spawn potenlab-tech-lead-specialist before potenlab-ui-ux-specialist completes
- NEVER spawn frontend/backend before tech-lead completes
- NEVER spawn potenlab-qa-specialist before frontend/backend complete
- NEVER pass file content in agent prompts — use file paths only
- NEVER proceed if a critical agent fails (ui-ux, tech-lead) — report and stop
- NEVER ask more than 5 questions total

</process>
