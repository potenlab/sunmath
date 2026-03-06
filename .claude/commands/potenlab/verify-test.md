---
name: potenlab:verify-test
description: Detect code changes and update tests to stay in sync
argument-hint: "[scope]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Task
  - AskUserQuestion
---

<objective>
Detect code changes, compare against `test-plan.md`, and update both the test plan and test files to stay in sync using potenlab-qa-specialist agents.
</objective>

<execution_context>
Read and apply rules from @/Users/muhammadrayandika/Documents/repository/sunmath/.claude/potenlab-workflow/CLAUDE.md before proceeding.
</execution_context>

<process>

## When to Use

Use `/potenlab:verify-test` when:
- You just ran `/potenlab:developer` and made changes to features
- You manually edited source code and need tests updated
- You want to ensure `test-plan.md` reflects current behavior

---

## How It Works

```
/potenlab:verify-test [scope]
      |
      v
  STEP 1: Detect changes (changes.json, git diff)
      |
      v
  STEP 2: Read context (test-plan.md, vitest-best-practices.md, backend-plan.md, existing tests)
      |
      v
  STEP 3: Analyze divergence (new, changed, removed behavior)
      |
      v
  STEP 4: Update test-plan.md (targeted edits)
      |
      v
  STEP 5: Spawn potenlab-qa-specialist agents in PARALLEL (edit existing tests, create new if needed)
      |
      v
  STEP 6: Report changes
```

---

## Step 1: Detect Changes

1. Read changes.json (if exists) — recent batches, affected files
2. Run `git diff --name-only HEAD~5` — modified source files
3. Map changed files to features
4. Accept scope override from arguments

**If no changes detected and no argument:** STOP.

---

## Step 2: Read Context (MANDATORY)

1. **test-plan.md** — REQUIRED, STOP if missing
2. **references/vitest-best-practices.md** — testing rules
3. **backend-plan.md** — schema context
4. **Changed source files** — current implementations
5. **Existing test files** — current test coverage

---

## Step 3: Analyze Divergence

| Category | Action |
|----------|--------|
| New behavior | Add scenarios + generate new tests |
| Changed behavior | Update scenarios + edit tests |
| Removed behavior | Mark deprecated + remove tests |
| Schema changes | Update constraint/RLS tests |
| New feature | Add new section + generate full suite |

---

## Step 4: Update test-plan.md

Use the Edit tool for targeted changes. **Do NOT rewrite the entire file.**

---

## Step 5: Spawn potenlab-qa-specialist Agents in PARALLEL

One agent per affected feature:

```
Task:
  subagent_type: potenlab-qa-specialist
  description: "Verify tests: {feature_name}"
  prompt: |
    Update tests for "{feature_name}" after code changes.

    Change manifest: {changes}

    Read all context, then:
    - EDIT existing test files for changed behavior
    - ADD new test cases for new behavior
    - REMOVE tests for deleted functionality
    - UPDATE constraint/RLS tests for schema changes

    PREFER editing existing files over creating new ones.
    Use Edit tool for surgical changes.

    When done: "COMPLETED: {feature_name} | Files edited: [...] | Tests added/updated/removed: ..."
```

**Spawn ALL in a SINGLE message.**

---

## Step 6: Report Changes

File-level detail: edited, created, tests added/updated/removed. Suggest running `/potenlab:run-test-all` to validate.

---

## Execution Rules

### DO:
- ALWAYS detect changes before doing anything
- ALWAYS update test-plan.md BEFORE spawning test-editing agents
- ALWAYS use Edit tool for surgical changes
- ALWAYS prefer editing existing test files over creating new ones

### DO NOT:
- NEVER rewrite test-plan.md from scratch
- NEVER rewrite entire test files
- NEVER modify source code — only test files
- NEVER proceed without test-plan.md
- NEVER generate tests for features that were NOT changed

</process>
