---
name: potenlab:security-resolve
description: Resolve pending security findings from security-list.json
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
Find and read `security-list.json`, display pending security findings, and spawn potenlab-high-coder agents to fix them. This command is used when the user previously ran `/potenlab:security-review` but chose NOT to fix findings at that time, or when there are remaining pending findings after a partial fix.
</objective>

<execution_context>
Read and apply rules from @/Users/muhammadrayandika/Documents/repository/sunmath/.claude/potenlab-workflow/CLAUDE.md before proceeding.
</execution_context>

<process>

## How It Works

```
/potenlab:security-resolve
      |
      v
  STEP 1: Find security-list.json
      |
      ├── NOT FOUND → STOP (tell user to run /security-review first)
      |
      └── FOUND
          |
          v
      STEP 2: Read and analyze pending findings
          |
          ├── 0 PENDING → STOP (all findings already resolved)
          |
          └── HAS PENDING
              |
              v
          STEP 3: Display pending findings summary
              |
              v
          STEP 4: Ask user — scope of fix
              |
              v
          STEP 5: Spawn potenlab-high-coder agents (wave-based, max 4)
              |
              v
          STEP 6: Update security-list.json after each wave
              |
              v
          STEP 7: Final report
```

---

## Step 1: Find security-list.json

```
Glob: **/security-list.json
```

### If NOT found:

**STOP immediately.** Tell the user:

> `security-list.json` not found. Run `/potenlab:security-review` first to perform a security audit and generate the findings list.

**Do NOT proceed. Do NOT scan for vulnerabilities manually.**

### If found:

Read the file and proceed to Step 2.

```
Read: [found path]
```

Note the directory path — this is where the updated file will be written back.

---

## Step 2: Read and Analyze Pending Findings

Parse the JSON and filter for pending findings:

```
pending_findings = findings.filter(f => f.status === "pending")
actionable = pending_findings.filter(f => f.severity in ["CRITICAL", "HIGH", "MEDIUM"])
```

### If 0 pending findings:

> All security findings are already resolved. No action needed.
>
> Run `/potenlab:security-review` again if you want a fresh audit.

**STOP.**

### If pending findings exist but ALL are LOW/INFO:

> All remaining findings are LOW or INFO severity — these are recommendations, not vulnerabilities.
>
> Would you like to address them anyway?

Use AskUserQuestion:
```
AskUserQuestion:
  question: "Only LOW/INFO findings remain. Address them?"
  header: "Fix low?"
  options:
    - label: "Yes, fix them"
      description: "Apply LOW and INFO recommendations"
    - label: "No, skip"
      description: "These are optional improvements"
```

If "No", **STOP.**

---

## Step 3: Display Pending Findings Summary

Show the user what needs to be fixed:

```
## Pending Security Findings

**From:** security-list.json
**Total pending:** X findings

### By Severity:
- CRITICAL: X
- HIGH: X
- MEDIUM: X
- LOW: X
- INFO: X

### Pending Findings:
| ID | Severity | Category | Title | File |
|----|----------|----------|-------|------|
| SEC-001 | CRITICAL | Secrets | Hardcoded API key | src/lib/api.ts:12 |
| SEC-003 | HIGH | RLS | Missing RLS on orders table | supabase/migrations/... |
| ... | ... | ... | ... | ... |

### Previously Resolved: Y findings
```

---

## Step 4: Ask User — Scope of Fix

Use AskUserQuestion:

```
AskUserQuestion:
  question: "Which findings would you like to fix?"
  header: "Fix scope"
  options:
    - label: "Fix all pending"
      description: "Resolve all [X] pending findings (CRITICAL + HIGH + MEDIUM + LOW)"
    - label: "Fix critical + high only"
      description: "Resolve only CRITICAL and HIGH severity findings"
    - label: "Fix critical only"
      description: "Resolve only CRITICAL severity findings"
    - label: "Pick specific findings"
      description: "Choose which findings to fix by ID"
```

### If "Pick specific findings":

Use AskUserQuestion to let the user select (show up to 4 findings as options, or ask for IDs as text input).

---

## Step 5: Spawn potenlab-high-coder Agents (Wave-Based)

### 5.1 Filter findings based on user's scope choice

```
target_findings = pending_findings filtered by user's severity choice
```

### 5.2 Also read security-report.md for detailed remediation

```
Glob: **/security-report.md
Read: [found path]
```

The report has detailed remediation steps that the high-coder needs.

### 5.3 Group findings by file

```
file_groups = {
  "src/lib/api.ts": [SEC-001, SEC-005],
  "src/app/api/users/route.ts": [SEC-002, SEC-003],
  ...
}
```

### 5.4 Spawn agents in waves (max 4 per wave)

**CRITICAL CONSTRAINT: The high-coder MUST NOT change any features or business logic. Security fixes ONLY.**

For each file group (max 4 agents per wave):

```
Task:
  subagent_type: potenlab-high-coder
  description: "Security fix: [file]"
  prompt: |
    You are fixing SECURITY VULNERABILITIES ONLY. Do NOT change any features, business logic, or behavior.

    Read these files for context:
    - [path to security-list.json] — the findings to fix
    - [path to security-report.md] — detailed remediation guidance

    Fix ONLY these specific findings in [file_path]:

    [For each finding in this file group:]
    ---
    **[SEC-ID]** ([severity]) — [title]
    File: [file]:[line]
    Evidence: [evidence snippet]
    Remediation: [remediation instructions]
    ---

    RULES — READ CAREFULLY:
    1. ONLY fix the listed security issues — nothing else
    2. Do NOT refactor, rename, or reorganize any code
    3. Do NOT add features, comments, or documentation beyond the fix
    4. Do NOT change function signatures or API contracts
    5. Do NOT modify any test files
    6. Do NOT change any business logic or data flow
    7. Preserve ALL existing functionality exactly as-is
    8. If a fix MIGHT break existing behavior, flag it and skip — do NOT apply
    9. Read the surrounding code carefully to understand context before fixing

    For each finding you fix, return:
    "FIXED: [SEC-ID] — [what you did]"

    For each finding you could NOT fix safely:
    "SKIPPED: [SEC-ID] — [why it might break functionality]"
```

### 5.5 Wait for all agents in this wave to complete

---

## Step 6: Update security-list.json After Each Wave

After each wave completes:

### 6.1 Parse agent results

For each agent response:
- Extract `FIXED: SEC-XXX` entries → mark as resolved
- Extract `SKIPPED: SEC-XXX` entries → keep as pending, add skip reason

### 6.2 Re-read security-list.json

```
Read: [path to security-list.json]
```

### 6.3 Update findings

For each FIXED finding:
```json
{
  "status": "resolved",
  "resolved_at": "[ISO timestamp]",
  "resolved_by": "potenlab-high-coder"
}
```

### 6.4 Recalculate summary

```json
{
  "summary": {
    "resolved": [count of resolved findings],
    "pending": [count of pending findings]
  }
}
```

### 6.5 Write updated security-list.json

```
Write: [path to security-list.json]
```

### 6.6 If more findings to fix → loop to Step 5.4 (next wave)

---

## Step 7: Final Report

After all waves complete:

```
## Security Resolve Complete

**Results:**
- Targeted: X findings
- Fixed: Y findings
- Skipped (unsafe): Z findings
- Still pending: W findings

### Fixed:
| ID | Severity | Title | Fix Applied |
|----|----------|-------|-------------|
| SEC-001 | CRITICAL | Hardcoded API key | Moved to env variable |
| SEC-003 | HIGH | Missing RLS | Enabled RLS + policies |
| ... | ... | ... | ... |

### Skipped (unsafe to fix automatically):
| ID | Severity | Title | Reason |
|----|----------|-------|--------|
| SEC-007 | MEDIUM | ... | Might break auth flow |
| ... | ... | ... | ... |

**Files updated:**
- `docs/security-list.json` — Updated with resolution status

**Next steps:**
- [If skipped > 0] Review skipped findings manually — they may require architectural changes
- [If pending > 0] Run `/potenlab:security-resolve` again for remaining items
- [If all resolved] Run `/potenlab:security-review` for a fresh audit to verify fixes
- Run your test suite to verify no features were broken
```

</process>

<execution_rules>
## Execution Rules

### DO:
- ALWAYS look for security-list.json FIRST — STOP if not found
- ALWAYS read security-report.md for detailed remediation context
- ALWAYS show the user pending findings before fixing
- ALWAYS ask the user what scope to fix (never auto-fix without consent)
- ALWAYS constrain high-coder to security-only fixes (no feature changes)
- ALWAYS update security-list.json after each wave of fixes
- ALWAYS group findings by file to minimize agent spawns
- ALWAYS limit fix waves to max 4 agents per wave
- ALWAYS report skipped findings with reasons

### DO NOT:
- NEVER proceed without security-list.json — tell user to run /security-review
- NEVER scan for vulnerabilities manually — this command ONLY resolves existing findings
- NEVER allow high-coder to change features, business logic, or behavior
- NEVER spawn more than 4 fix agents in a single wave
- NEVER mark a finding as resolved if high-coder reported it as SKIPPED
- NEVER delete or regenerate security-report.md — it's the source of truth for remediation
- NEVER fix findings the user didn't approve
</execution_rules>
