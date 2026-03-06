---
name: potenlab:developer
description: Post-completion adjustments tracked in changes.json
argument-hint: "[description]"
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
Handle post-completion adjustments by analyzing change requests, creating tracked tasks in `changes.json`, and spawning coder agents (potenlab-small-coder / potenlab-high-coder) in parallel.
</objective>

<execution_context>
Read and apply rules from @/Users/muhammadrayandika/Documents/repository/sunmath/.claude/potenlab-workflow/CLAUDE.md before proceeding.
</execution_context>

<process>

## When to Use

Use `/potenlab:developer` when:
- All phases are **already completed** via `/potenlab:execute-phase`
- You need **adjustments, fixes, or tweaks** to existing code
- You want changes **tracked separately** from the original progress.json

Use `/potenlab:execute-phase` instead when:
- You're still building the initial project phases

---

## How It Works

```
/potenlab:developer [change description]
      |
      v
  STEP 1: Get change request (from arg or AskUserQuestion)
      |
      v
  STEP 2: Read project context (progress.json, plans, codebase)
      |
      v
  STEP 3: Analyze & create change tasks
      |
      v
  STEP 4: Write docs/changes.json (create or APPEND new batch)
      |
      v
  STEP 5: Spawn agents in PARALLEL (one per task)
      |
      v
  STEP 6: Update changes.json with results
      |
      v
  STEP 7: Report results
```

---

## Step 1: Get Change Request

### Option A: From arguments

If the user provides a description:
```
/potenlab:developer fix the login button hover state
/potenlab:developer add dark mode toggle to settings
```

Extract the change request directly. **Do NOT ask questions — proceed to Step 2.**

### Option B: No argument provided

If the user invokes with no argument, you MUST use AskUserQuestion:

```
AskUserQuestion:
  question: "What change or adjustment do you need?"
  header: "Change Type"
  options:
    - label: "Bug fix"
      description: "Something is broken or behaving incorrectly"
    - label: "UI/UX adjustment"
      description: "Visual or interaction changes"
    - label: "Feature tweak"
      description: "Modify existing functionality"
    - label: "I'll describe it"
      description: "Provide detailed description"
```

### Question Rules
- Maximum **2 questions** to gather the change request
- If the user provided arguments, ask **ZERO questions**

---

## Step 2: Read Project Context

Read all available context:

```
Glob: **/progress.json → understand what was built
Glob: **/dev-plan.md → original plan
Glob: **/frontend-plan.md → component specs
Glob: **/backend-plan.md → schema specs
Glob: **/changes.json → previous change batches
Glob: src/**/*.{ts,tsx} → existing codebase
```

---

## Step 3: Analyze & Create Change Tasks

Break the user's change request into concrete, implementable tasks.

### Classify complexity

| Complexity | Criteria | Agent |
|------------|----------|-------|
| `low` | 1-2 files, single concern | `potenlab-small-coder` |
| `high` | 3+ files, cross-file coordination | `potenlab-high-coder` |

---

## Step 4: Write changes.json

### Batch numbering

Each invocation creates a new batch:
- First run: Batch `C1` with tasks `C1.1`, `C1.2`, ...
- Second run: Batch `C2` with tasks `C2.1`, `C2.2`, ...

If `changes.json` already exists — read it and APPEND a new batch.

---

## Step 5: Spawn Agents in PARALLEL

**Same parallel spawning mechanism as `/potenlab:execute-phase`.**

Filter executable tasks (pending + unblocked), then spawn ALL in a SINGLE message.

For `complexity: "low"` → `potenlab-small-coder`
For `complexity: "high"` → `potenlab-high-coder`

**Wait for ALL agents to complete before proceeding to Step 6.**

---

## Step 6: Update changes.json

1. Mark completed/blocked tasks
2. Update blocked_by within the batch
3. Update batch progress
4. Recalculate global summary
5. Update timestamp and write

---

## Step 7: Report Results

Report with results table, batch summary, blocked tasks, and next steps.

---

## Re-running for Blocked Tasks

When `/potenlab:developer` is invoked and `changes.json` already has unblocked tasks from a previous batch, ask:

```
AskUserQuestion:
  question: "Found {N} unblocked tasks from batch {batch_id}. Execute them or start a new change?"
  header: "Pending Work"
  options:
    - label: "Execute unblocked tasks (Recommended)"
      description: "Finish pending work from batch {batch_id}"
    - label: "New change request"
      description: "Skip pending tasks and create a new batch"
    - label: "Both"
      description: "Execute pending tasks AND add new changes"
```

---

## Execution Rules

### DO:
- ALWAYS read project context before creating tasks
- ALWAYS create or append to changes.json — never modify progress.json
- ALWAYS use batch IDs with "C" prefix (C1, C2, C3...)
- ALWAYS spawn ALL unblocked tasks in a SINGLE parallel message
- ALWAYS update changes.json after agents complete
- ALWAYS check for previously blocked tasks before creating a new batch

### DO NOT:
- NEVER modify progress.json — that tracks the original build
- NEVER execute blocked tasks (blocked_by is non-empty)
- NEVER spawn potenlab-high-coder for low-complexity changes
- NEVER spawn potenlab-small-coder for high-complexity changes
- NEVER let agents update changes.json
- NEVER ask more than 2 questions

</process>
