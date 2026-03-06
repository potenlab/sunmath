---
name: potenlab:run-test-all
description: Run all Vitest tests and generate test.result.json
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
Run every Vitest test file in the project, collect results, and generate `test.result.json`. Uses potenlab-qa-specialist to analyze failures.
</objective>

<execution_context>
Read and apply rules from @/Users/muhammadrayandika/Documents/repository/sunmath/.claude/potenlab-workflow/CLAUDE.md before proceeding.
</execution_context>

<process>

## How It Works

```
/potenlab:run-test-all
      |
      v
  STEP 1: Discover all test files
      |
      v
  STEP 2: Read test-plan.md for context (optional — map tests to phases)
      |
      v
  STEP 3: Run vitest (check Supabase, run npx vitest run)
      |
      v
  STEP 4: Parse results & generate test.result.json (REPLACE, never append)
      |
      v
  STEP 5: Analyze failures (if any) — spawn potenlab-qa-specialist
      |
      v
  STEP 6: Report results
```

---

## Step 1: Discover All Test Files

```
Glob: tests/**/*.test.ts
Glob: supabase/**/*.test.ts
```

**If no test files found:** STOP. Tell user to run `/potenlab:generate-test` first.

---

## Step 2: Read test-plan.md for Context

Optional — for grouping results by phase.

---

## Step 3: Run Vitest

1. Check Supabase local is running (`npx supabase status`)
2. If not running, warn and ask user
3. Execute: `npx vitest run --reporter=json --reporter=default --outputFile=docs/vitest-raw-output.json 2>&1`

---

## Step 4: Parse Results & Generate test.result.json

**ALWAYS replace test.result.json entirely — never append.**

Parse raw vitest JSON output into structured format with:
- Summary (total, passed, failed, skipped, pass_rate)
- By directory breakdown
- By phase breakdown (if test-plan.md exists)
- Per-suite details with failures

Write to: `docs/test.result.json`

Clean up: `rm docs/vitest-raw-output.json`

---

## Step 5: Analyze Failures (if any)

If ALL tests passed → skip this step.

If failures exist, spawn potenlab-qa-specialist:

```
Task:
  subagent_type: potenlab-qa-specialist
  description: "Analyze test failures"
  prompt: |
    Analyze test failures from docs/test.result.json.
    Read failing test files and source files.
    Determine root cause for each failure.
    Provide specific fix recommendations.
    Do NOT modify any files. Analysis only.
```

---

## Step 6: Report Results

Summary with pass rate, results by directory, results by phase, failure analysis, and next steps.

---

## Execution Rules

### DO:
- ALWAYS discover test files before running
- ALWAYS replace test.result.json entirely
- ALWAYS check Supabase local status
- ALWAYS group results by directory AND by phase
- ALWAYS spawn potenlab-qa-specialist for failure analysis

### DO NOT:
- NEVER append to test.result.json
- NEVER skip running tests and generate fake results
- NEVER modify test or source files during a test run

</process>
