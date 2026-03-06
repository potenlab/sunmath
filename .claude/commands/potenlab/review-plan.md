---
name: potenlab:review-plan
description: Edit existing plans based on user feedback
argument-hint: "[feedback]"
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
Edit and update all existing plan files based on user feedback, following the same orchestration flow as `/potenlab:plan-project` but in EDIT mode (not creation from scratch). Also updates progress.json if it exists.
</objective>

<execution_context>
Read and apply rules from @/Users/muhammadrayandika/Documents/repository/sunmath/.claude/potenlab-workflow/CLAUDE.md before proceeding.
</execution_context>

<process>

## How It Differs from /potenlab:plan-project

| Aspect | /potenlab:plan-project | /potenlab:review-plan |
|--------|------------------------|----------------------|
| Purpose | Create plans from scratch | Edit existing plans |
| Input | PRD file | User feedback + existing plans |
| Agent action | Write new files | Read existing, apply changes, rewrite |
| progress.json | Not created | Updated/regenerated if it exists |

---

## Flow

```
/potenlab:review-plan [user feedback OR empty]
      |
      v
  STEP 1: Get review feedback (from arg or AskUserQuestion)
      |
      v
  STEP 2: Verify all 4 plan files exist (REQUIRED)
      |
      v
  STEP 3: Spawn potenlab-ui-ux-specialist (EDIT mode, SEQUENTIAL)
      |
      v
  STEP 4: Spawn potenlab-tech-lead-specialist (EDIT mode, SEQUENTIAL)
      |
      v
  STEP 5: Spawn frontend + backend specialists (EDIT mode, PARALLEL)
      |
      v
  STEP 6: Update progress.json (CONDITIONAL — only if exists)
      |
      v
  STEP 7: Report changes
```

---

## Step 1: Get Review Feedback

### Option A: Feedback from arguments

```
/potenlab:review-plan change the auth flow to use OAuth
/potenlab:review-plan add a dark mode toggle
```

Extract the feedback directly. **Do NOT ask questions.**

### Option B: No arguments provided

Use AskUserQuestion to gather feedback. Maximum **3 questions**.

---

## Step 2: Verify Existing Plan Files

Check that ALL 4 plan files exist:

```
Glob: **/ui-ux-plan.md
Glob: **/dev-plan.md
Glob: **/frontend-plan.md
Glob: **/backend-plan.md
Glob: **/progress.json
```

If any REQUIRED file is missing, STOP and tell user to run `/potenlab:plan-project` first.

Track `has_progress_json = true/false`.

---

## Steps 3-5: Agent Execution

Same sequential flow as `/potenlab:plan-project`:

1. **potenlab-ui-ux-specialist** — EDIT mode (sequential)
2. **potenlab-tech-lead-specialist** — EDIT mode (sequential)
3. **potenlab-frontend-specialist** + **potenlab-backend-specialist** — EDIT mode (parallel)

Each agent receives `{user_feedback}` and is told to EDIT existing files, not rewrite from scratch. Each adds a Revision Log section.

---

## Step 6: Update progress.json (CONDITIONAL)

Only if `has_progress_json == true`:

Spawn **potenlab-progress-creator** to regenerate progress.json from updated plans.

---

## Step 7: Report Changes

Summary of all updated files with status, Revision Log info, and next steps.

---

## Execution Rules

### DO:
- ALWAYS check for arguments first — skip AskUserQuestion if feedback is in arguments
- ALWAYS verify all 4 plan files exist before spawning agents
- ALWAYS pass `{user_feedback}` to EVERY agent
- ALWAYS run potenlab-ui-ux-specialist first, then tech-lead, then frontend+backend parallel
- ALWAYS update progress.json if it existed before the review
- ALWAYS tell agents this is EDIT mode

### DO NOT:
- NEVER rewrite plans from scratch — this is an edit operation
- NEVER skip the sequential order
- NEVER ask more than 3 questions
- NEVER ask questions if the user provided arguments
- NEVER pass file content in prompts — use file paths only

</process>
