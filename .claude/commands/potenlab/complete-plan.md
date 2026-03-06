---
name: potenlab:complete-plan
description: Generate progress.json from finalized plans
allowed-tools:
  - Read
  - Write
  - Glob
  - Grep
  - Task
---

<objective>
Finalize the planning phase by generating `progress.json` from all existing plan files using the potenlab-progress-creator agent.
</objective>

<execution_context>
Read and apply rules from @/Users/muhammadrayandika/Documents/repository/sunmath/.claude/potenlab-workflow/CLAUDE.md before proceeding.
</execution_context>

<process>

## When to Use

Run this command **after** `/potenlab:plan-project` has completed and all plan files exist:

```
docs/
├── ui-ux-plan.md        # Created by potenlab-ui-ux-specialist
├── dev-plan.md          # Created by potenlab-tech-lead-specialist (REQUIRED)
├── frontend-plan.md     # Created by potenlab-frontend-specialist
└── backend-plan.md      # Created by potenlab-backend-specialist
```

---

## Flow

```
/potenlab:complete-plan
      |
      v
  STEP 1: Verify plan files exist (dev-plan.md REQUIRED)
      |
      v
  STEP 2: Spawn potenlab-progress-creator agent
      |
      v
  STEP 3: Verify output and report
```

---

## Step 1: Verify Plan Files

```
Glob: **/dev-plan.md
Glob: **/frontend-plan.md
Glob: **/backend-plan.md
```

### If dev-plan.md is NOT found:

**STOP immediately.** Do NOT spawn the agent. Tell the user:

> `dev-plan.md` not found. Run `/potenlab:plan-project` first to create all plan files, then run `/potenlab:complete-plan`.

### If only frontend-plan.md or backend-plan.md is missing:

Proceed anyway — these are optional enrichment. Warn the user.

---

## Step 2: Spawn potenlab-progress-creator Agent

```
Task:
  subagent_type: potenlab-progress-creator
  description: "Generate progress.json"
  prompt: |
    Read all plan files and generate progress.json.

    REQUIRED — read this first:
    - docs/dev-plan.md

    OPTIONAL — read these for enrichment (if they exist):
    - docs/frontend-plan.md
    - docs/backend-plan.md

    Your job:
    1. Parse every phase and task from dev-plan.md
    2. Enrich tasks with file paths and details from specialist plans
    3. Classify each task as "low" or "high" complexity with a specific reason
    4. Assign agent: "potenlab-small-coder" for low, "potenlab-high-coder" for high
    5. Map dependencies between tasks
    6. Calculate summary counts

    Write the output to: docs/progress.json

    Use the Write tool to create the file. Return "Done: docs/progress.json" when complete.
```

**Wait for the agent to complete.**

---

## Step 3: Verify and Report

After the agent completes, verify the file was created:

```
Glob: docs/progress.json
```

Report success with summary of what's inside progress.json and next steps:
- Review `docs/progress.json` to verify task classifications
- Run `/potenlab:execute-phase 0` to start building

---

## Execution Rules

### DO:
- ALWAYS verify dev-plan.md exists before spawning the agent
- ALWAYS check for frontend-plan.md and backend-plan.md (optional)
- ALWAYS warn if overwriting an existing progress.json
- ALWAYS verify progress.json was created after the agent finishes

### DO NOT:
- NEVER spawn potenlab-progress-creator if dev-plan.md is missing
- NEVER pass file content in the agent prompt — use file paths only
- NEVER modify any plan files — this command is read-only for plans
- NEVER manually create progress.json — let the agent do it

</process>
