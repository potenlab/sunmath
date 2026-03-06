---
name: potenlab:security-review
description: Run a comprehensive security audit on the project and generate security-list.json with findings
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
Run a comprehensive security audit by spawning potenlab-security-specialist to scan the entire codebase for vulnerabilities. Produces `security-list.json` (in the same directory as `progress.json`) with all findings. After the audit, asks the user if they want to fix all findings immediately — if yes, spawns potenlab-high-coder agents to resolve them. If no, tells the user to run `/potenlab:security-resolve` later.
</objective>

<execution_context>
Read and apply rules from @/Users/muhammadrayandika/Documents/repository/sunmath/.claude/potenlab-workflow/CLAUDE.md before proceeding.
</execution_context>

<process>

## How It Works

```
/potenlab:security-review
      |
      v
  STEP 1: Locate project context (progress.json directory, plans)
      |
      v
  STEP 2: Spawn potenlab-security-specialist → security-report.md
      |
      v
  STEP 3: Parse security-report.md → security-list.json
      |
      v
  STEP 4: Display summary to user
      |
      v
  STEP 5: Ask user — "Fix all findings now?"
      |
      ├── YES → STEP 6: Spawn potenlab-high-coder agents to fix (wave-based)
      |
      └── NO  → Tell user to run /potenlab:security-resolve later
```

---

## Step 1: Locate Project Context

### 1.1 Find the docs directory (same location as progress.json)

```
Glob: **/progress.json
```

If found, extract the directory path (e.g., `docs/`). This is where `security-list.json` will be written.

If NOT found, use `docs/` as the default output directory:
```
Bash: mkdir -p docs
```

### 1.2 Read project context for the security agent

```
Glob: **/package.json
Glob: **/next.config.{js,mjs,ts}
Glob: **/dev-plan.md
Glob: **/backend-plan.md
```

Note the paths — the security-specialist will need them.

---

## Step 2: Spawn potenlab-security-specialist

Spawn a single potenlab-security-specialist agent to perform the full audit:

```
Task:
  subagent_type: potenlab-security-specialist
  description: "Security audit"
  prompt: |
    Perform a comprehensive security audit of this project.

    Scan the ENTIRE codebase for vulnerabilities across all categories:
    1. Secrets Management — hardcoded keys, tokens, credentials
    2. Input Validation & Injection — SQL injection, XSS, command injection
    3. Authentication & Session Management — JWT storage, auth middleware
    4. Row Level Security (Supabase) — RLS enabled/forced, policy coverage
    5. CSRF Protection — SameSite cookies, CSRF tokens
    6. XSS Prevention — dangerouslySetInnerHTML, CSP headers
    7. Security Headers — CSP, HSTS, X-Frame-Options, CORS
    8. Rate Limiting — API throttling, brute force protection
    9. Dependency Vulnerabilities — npm audit findings
    10. Blockchain/Wallet Security — signature verification (if applicable)

    Write your full findings to: [docs_dir]/security-report.md

    IMPORTANT: For each finding, include:
    - A unique ID (SEC-001, SEC-002, etc.)
    - Severity (CRITICAL, HIGH, MEDIUM, LOW, INFO)
    - Category name
    - File path and line number
    - Description of the vulnerability
    - Code evidence (the vulnerable code snippet)
    - Remediation (the fix with code example)

    When done, return: "COMPLETED: [docs_dir]/security-report.md | Findings: [count by severity]"
```

**Wait for the agent to complete.**

---

## Step 3: Parse security-report.md → security-list.json

After the security-specialist completes, read `security-report.md` and parse ALL findings into a structured JSON file.

### 3.1 Read the report

```
Read: [docs_dir]/security-report.md
```

### 3.2 Generate security-list.json

Parse each finding from the report into this JSON structure:

```json
{
  "generated_at": "[ISO timestamp]",
  "source": "security-report.md",
  "summary": {
    "total": 0,
    "critical": 0,
    "high": 0,
    "medium": 0,
    "low": 0,
    "info": 0,
    "resolved": 0,
    "pending": 0
  },
  "findings": [
    {
      "id": "SEC-001",
      "severity": "CRITICAL",
      "category": "Secrets Management",
      "title": "Hardcoded API key in source code",
      "description": "API key is hardcoded in src/lib/api.ts instead of using environment variables.",
      "file": "src/lib/api.ts",
      "line": 12,
      "evidence": "const apiKey = 'sk-proj-xxxxx';",
      "remediation": "Move to environment variable: const apiKey = process.env.API_KEY;",
      "status": "pending",
      "resolved_at": null,
      "resolved_by": null
    }
  ]
}
```

**Write to:** `[docs_dir]/security-list.json` (same directory as progress.json)

### Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique finding ID from the report (SEC-001, SEC-002, ...) |
| `severity` | string | CRITICAL, HIGH, MEDIUM, LOW, or INFO |
| `category` | string | Security category (Secrets Management, RLS, XSS, etc.) |
| `title` | string | Short description of the finding |
| `description` | string | Detailed explanation of the vulnerability |
| `file` | string | File path where the issue exists |
| `line` | number | Line number (0 if not specific) |
| `evidence` | string | The vulnerable code snippet |
| `remediation` | string | How to fix it |
| `status` | string | `"pending"` or `"resolved"` |
| `resolved_at` | string/null | ISO timestamp when resolved |
| `resolved_by` | string/null | Agent that resolved it |

---

## Step 4: Display Summary to User

Show a clear summary:

```
## Security Audit Complete

**Findings:**
- CRITICAL: X
- HIGH: X
- MEDIUM: X
- LOW: X
- INFO: X
- **Total: X findings**

**Output files:**
- `docs/security-report.md` — Full detailed report
- `docs/security-list.json` — Structured findings for resolution

**Top findings:**
1. [SEC-001] CRITICAL — [title] — [file]
2. [SEC-002] HIGH — [title] — [file]
3. ...
```

---

## Step 5: Ask User — Fix Now?

**If there are 0 findings with severity CRITICAL, HIGH, or MEDIUM:**

> All clear — no actionable security findings. Only informational recommendations found.

**STOP. Do not ask.**

**If there ARE actionable findings (CRITICAL, HIGH, or MEDIUM):**

Use AskUserQuestion:

```
AskUserQuestion:
  question: "Found [X] security issues ([C] critical, [H] high, [M] medium). Would you like to fix them now?"
  header: "Fix now?"
  options:
    - label: "Yes, fix all now"
      description: "Spawn high-coder agents to resolve all CRITICAL, HIGH, and MEDIUM findings"
    - label: "Yes, fix critical only"
      description: "Only fix CRITICAL severity findings now"
    - label: "No, fix later"
      description: "Keep security-list.json for later. Run /security-resolve when ready"
```

---

## Step 6: Fix Findings (if user says YES)

### 6.1 Determine scope

Based on user's answer:
- **"Yes, fix all now"** → Filter findings where `severity` is CRITICAL, HIGH, or MEDIUM and `status` is `"pending"`
- **"Yes, fix critical only"** → Filter findings where `severity` is CRITICAL and `status` is `"pending"`

### 6.2 Group findings by file

Group actionable findings by file path to minimize agent count:

```
file_groups = {
  "src/lib/api.ts": [SEC-001, SEC-005],
  "src/app/api/users/route.ts": [SEC-002, SEC-003],
  ...
}
```

### 6.3 Spawn potenlab-high-coder agents (wave-based, max 4 per wave)

**CRITICAL CONSTRAINT: The high-coder MUST NOT change any features or business logic. Only fix the security issues.**

For each file group (max 4 per wave):

```
Task:
  subagent_type: potenlab-high-coder
  description: "Security fix: [file]"
  prompt: |
    You are fixing SECURITY VULNERABILITIES ONLY. Do NOT change any features, business logic, or behavior.

    Read these files for context:
    - [docs_dir]/security-list.json — the full findings list
    - [docs_dir]/security-report.md — detailed remediation guidance

    Fix ONLY these specific findings in [file_path]:
    [List each finding ID, title, and remediation for this file]

    RULES — READ CAREFULLY:
    1. ONLY fix the listed security issues — nothing else
    2. Do NOT refactor, rename, or reorganize any code
    3. Do NOT add features, comments, or documentation
    4. Do NOT change function signatures or API contracts
    5. Do NOT modify any test files
    6. Do NOT change any business logic or data flow
    7. Preserve ALL existing functionality exactly as-is
    8. If a fix MIGHT break existing behavior, flag it and skip — do NOT apply

    For each finding you fix, return:
    "FIXED: [SEC-ID] — [what you did]"

    For each finding you could NOT fix safely:
    "SKIPPED: [SEC-ID] — [why it might break functionality]"
```

### 6.4 Update security-list.json after each wave

After each wave of agents completes:

1. **Re-read** `security-list.json`
2. **Update** status of fixed findings:
   ```json
   {
     "status": "resolved",
     "resolved_at": "[ISO timestamp]",
     "resolved_by": "potenlab-high-coder"
   }
   ```
3. **Recalculate** summary counts (`resolved`, `pending`)
4. **Write** updated `security-list.json`

### 6.5 Repeat waves until all targeted findings are resolved or skipped

---

## Step 7: Final Report

After all fixes are applied (or if user chose "No"):

```
## Security Review Complete

**Audit:**
- Total findings: X
- Resolved: Y
- Pending: Z
- Skipped (unsafe to fix): W

**Files:**
- `docs/security-report.md` — Full audit report
- `docs/security-list.json` — Tracking file (Y resolved, Z pending)

**Next steps:**
- [If pending > 0] Run `/potenlab:security-resolve` to fix remaining issues
- [If pending === 0] All actionable findings resolved
- Review `security-report.md` for INFO-level recommendations
```

</process>

<security_list_json_schema>
## security-list.json Full Schema

```json
{
  "generated_at": "2026-03-04T12:00:00.000Z",
  "source": "security-report.md",
  "summary": {
    "total": 12,
    "critical": 2,
    "high": 4,
    "medium": 3,
    "low": 2,
    "info": 1,
    "resolved": 0,
    "pending": 12
  },
  "findings": [
    {
      "id": "SEC-001",
      "severity": "CRITICAL",
      "category": "Secrets Management",
      "title": "Service role key exposed in client bundle",
      "description": "SUPABASE_SERVICE_ROLE_KEY is prefixed with NEXT_PUBLIC_ making it accessible in the browser bundle.",
      "file": ".env.local",
      "line": 3,
      "evidence": "NEXT_PUBLIC_SUPABASE_SERVICE_ROLE_KEY=eyJ...",
      "remediation": "Remove NEXT_PUBLIC_ prefix. Use SUPABASE_SERVICE_ROLE_KEY (server-only).",
      "status": "pending",
      "resolved_at": null,
      "resolved_by": null
    }
  ]
}
```
</security_list_json_schema>

<execution_rules>
## Execution Rules

### DO:
- ALWAYS spawn potenlab-security-specialist for the audit — never scan manually
- ALWAYS write security-list.json in the SAME directory as progress.json
- ALWAYS parse ALL findings from security-report.md into security-list.json
- ALWAYS ask the user before fixing (never auto-fix)
- ALWAYS constrain high-coder to security-only fixes (no feature changes)
- ALWAYS update security-list.json after each wave of fixes
- ALWAYS group findings by file to minimize agent spawns
- ALWAYS limit fix waves to max 4 agents per wave

### DO NOT:
- NEVER fix security issues without user consent
- NEVER allow high-coder to change features, business logic, or behavior
- NEVER spawn more than 4 fix agents in a single wave
- NEVER skip the security-specialist agent and scan manually
- NEVER delete security-report.md — it's the detailed reference
- NEVER mark a finding as resolved if high-coder reported it as SKIPPED
</execution_rules>
