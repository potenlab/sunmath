---
name: potenlab:execute-phase
description: Execute all tasks in a phase with wave-based parallel coder agents (max 4 per wave)
argument-hint: "<phase-number>"
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
Execute all pending tasks in a specific development phase using wave-based parallel execution (max 4 agents per wave). Spawns potenlab-small-coder / potenlab-high-coder agents based on progress.json complexity classification. Updates progress.json after EACH wave so completed tasks immediately unblock dependents.
</objective>

<execution_context>
Read and apply rules from @/Users/muhammadrayandika/Documents/repository/sunmath/.claude/potenlab-workflow/CLAUDE.md before proceeding.
</execution_context>

<process>

## How It Works

```
/potenlab:execute-phase [phase_number]
      |
      v
  STEP 1: Get phase number (from arg or AskUserQuestion)
      |
      v
  STEP 2: Read progress.json, filter executable tasks
      |
      v
  STEP 3: Group tasks by complexity → plan waves (max 4 per wave)
      |
      v
  STEP 4: WAVE LOOP
      |   ┌──────────────────────────────────────────────┐
      |   │  4a. Re-read progress.json, filter tasks      │
      |   │  4b. Take next batch (up to 4 tasks)          │
      |   │  4c. Spawn agents in parallel (1 message)     │
      |   │  4d. Wait for all agents in wave               │
      |   │  4e. Update progress.json IMMEDIATELY          │
      |   │  4f. If more executable tasks → loop to 4a     │
      |   └──────────────────────────────────────────────┘
      |
      v
  STEP 5: Final report (all waves combined)
```

---

## Step 1: Get Phase Number

### Option A: From arguments

If the user provides a phase number:
```
/potenlab:execute-phase 0
/potenlab:execute-phase 3
```

Extract the phase number directly. **Do NOT ask questions — proceed to Step 2.**

### Option B: No argument provided

If the user invokes with no argument, you MUST use AskUserQuestion:

```
AskUserQuestion:
  question: "Which phase would you like to execute?"
  header: "Phase"
  options:
    - label: "Phase 0: Foundation"
      description: "Project setup, design tokens, config files"
    - label: "Phase 1: Backend"
      description: "Database schema, migrations, RLS policies"
    - label: "Phase 2: Shared UI"
      description: "Shared components in src/components/"
    - label: "Phase 3: Features"
      description: "Feature modules in src/features/"
```

Read progress.json first to determine which phases exist, then build the options dynamically.

---

## Step 2: Read progress.json and Analyze Phase

### 2.1 Locate and read progress.json

```
Glob: **/progress.json
Read: [found path]
```

**If progress.json does NOT exist:**
> `progress.json` not found. Run `/potenlab:complete-plan` first to generate the task tracker.

**STOP. Do NOT proceed.**

### 2.2 Find the target phase

Parse progress.json and locate the phase object matching the requested phase number.

### 2.3 Filter executable tasks

From the target phase, collect tasks that meet ALL criteria:

```
executable_tasks = phase.tasks.filter(task =>
  task.status === "pending" AND
  task.blocked_by.length === 0
)
```

---

## Step 3: Group Tasks by Agent Type and Plan Waves

Split `executable_tasks` into two groups based on progress.json classification:

```
small_tasks = executable_tasks.filter(t => t.complexity === "low")
  → Each spawns a potenlab-small-coder agent

high_tasks = executable_tasks.filter(t => t.complexity === "high")
  → Each spawns a potenlab-high-coder agent
```

Combine and chunk into waves of max 4. Report the execution plan before spawning.

---

## Step 4: Wave-Based Parallel Execution

**CRITICAL: Max 4 agents per wave. Update progress.json AFTER EACH wave. Re-filter between waves.**

### Wave Loop

Repeat until no more executable tasks:

1. **Re-read** progress.json (previous wave may have changed it)
2. **Filter** executable tasks (pending + unblocked)
3. **Take** up to 4 tasks for this wave
4. **Spawn** agents in ONE message (max 4 Task tool calls)
   - `complexity: "low"` → potenlab-small-coder
   - `complexity: "high"` → potenlab-high-coder
5. **Wait** for all agents in this wave to complete
6. **Update progress.json IMMEDIATELY:**
   - Mark completed/blocked tasks
   - Remove completed task IDs from ALL `blocked_by` arrays across ALL phases
   - Update phase progress count
   - Recalculate summary counts
   - Write updated progress.json
7. **Loop** back to step 1 (newly unblocked tasks may now be executable)

### Agent Prompt Templates

**potenlab-small-coder** (for `complexity === "low"`):
```
Task:
  subagent_type: potenlab-small-coder
  description: "Task {task.id}: {task.name}"
  prompt: |
    Execute task {task.id}: {task.name}
    [Read all plans, implement small task, verify]
    Do NOT update progress.json — orchestrator handles that after each wave.
    Return: "COMPLETED: {task.id} — {task.name} | Files: [list]"
    Or: "BLOCKED: {task.id} — {reason}"
```

**potenlab-high-coder** (for `complexity === "high"`):
```
Task:
  subagent_type: potenlab-high-coder
  description: "Task {task.id}: {task.name}"
  prompt: |
    Execute task {task.id}: {task.name}
    [Read all plans, implement complex task, self-review, verify]
    Do NOT update progress.json — orchestrator handles that after each wave.
    Return: "COMPLETED: {task.id} — {task.name} | Files: [list]"
    Or: "BLOCKED: {task.id} — {reason}"
```

---

## Step 5: Final Report

Report with results grouped by wave, summary counts, phase progress, newly unblocked tasks, and next steps.

---

## Execution Rules

### DO:
- ALWAYS read progress.json before spawning any agents
- ALWAYS check `blocked_by` is empty before including a task
- ALWAYS limit each wave to a maximum of 4 agents
- ALWAYS update progress.json AFTER EACH WAVE (not after the entire phase)
- ALWAYS re-read progress.json and re-filter between waves
- ALWAYS use potenlab-small-coder for `complexity: "low"` and potenlab-high-coder for `complexity: "high"`
- ALWAYS remove completed task IDs from blocked_by arrays across ALL phases after each wave

### DO NOT:
- NEVER spawn more than 4 agents in a single wave
- NEVER execute tasks where `blocked_by` is non-empty
- NEVER execute tasks where `status` is already `"completed"`
- NEVER let agents update progress.json — only the orchestrator does that (after each wave)
- NEVER wait until the entire phase finishes to update progress.json — update after EACH wave

</process>
