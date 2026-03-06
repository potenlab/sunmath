---
name: potenlab:run-test-phase
description: Run Vitest tests for a specific phase
argument-hint: "<phase>"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - Task
  - AskUserQuestion
---

<objective>
Run Vitest tests for a specific phase from `test-plan.md`, collect results, and generate `test.result.json`. Uses potenlab-qa-specialist to analyze failures.
</objective>

<execution_context>
Read and apply rules from @/Users/muhammadrayandika/Documents/repository/sunmath/.claude/potenlab-workflow/CLAUDE.md before proceeding.
</execution_context>

<process>

## How It Works

```
/potenlab:run-test-phase [phase]
      |
      v
  STEP 1: Read test-plan.md (REQUIRED — extract phase list)
      |
      v
  STEP 2: Get phase choice (from arg or AskUserQuestion)
      |
      v
  STEP 3: Resolve test files for the chosen phase
      |
      v
  STEP 4: Run vitest with file filter (only phase's test files)
      |
      v
  STEP 5: Parse results & generate test.result.json (REPLACE)
      |
      v
  STEP 6: Analyze failures (if any) — spawn potenlab-qa-specialist
      |
      v
  STEP 7: Report results
```

---

## Step 1: Read test-plan.md

```
Glob: **/test-plan.md
Read: [found path]
```

**If test-plan.md does NOT exist:** STOP. Tell user to use `/potenlab:run-test-all` or create a test-plan.md first.

---

## Step 2: Get Phase Choice

### Option A: From arguments

```
/potenlab:run-test-phase 1     → Run Phase 1 tests
/potenlab:run-test-phase auth  → Run tests for auth phase/feature
```

### Option B: No argument

Build phase list dynamically from test-plan.md, then AskUserQuestion. Maximum **1 question**.

---

## Step 3: Resolve Test Files

Map phase → features → test files:

```
Glob: tests/features/{feature}/**/*.test.ts
Glob: tests/rls/{feature}*.test.ts
Glob: tests/constraints/{feature}*.test.ts
```

If no test files found for the chosen phase, STOP and suggest `/potenlab:generate-test`.

---

## Step 4: Run Vitest with File Filter

1. Check Supabase local status
2. Run ONLY the phase's test files:
   `npx vitest run {files} --reporter=json --reporter=default --outputFile=docs/vitest-raw-output.json 2>&1`

---

## Step 5: Parse Results & Generate test.result.json

**ALWAYS replace entirely.** Group results by feature within the phase.

---

## Step 6: Analyze Failures

If failures exist, spawn potenlab-qa-specialist for analysis.

---

## Step 7: Report Results

Per-feature breakdown, failure analysis, and next steps.

---

## Execution Rules

### DO:
- ALWAYS read test-plan.md to determine phase-to-feature mapping
- ALWAYS run ONLY the chosen phase's tests
- ALWAYS replace test.result.json entirely
- ALWAYS check Supabase local status

### DO NOT:
- NEVER run ALL tests — only the chosen phase's tests
- NEVER append to test.result.json
- NEVER modify test or source files during a test run
- NEVER proceed without test-plan.md

</process>
