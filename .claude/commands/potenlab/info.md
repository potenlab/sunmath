---
name: potenlab:info
description: Display Potenlab workflow overview and status
allowed-tools:
  - Read
  - Glob
---

<objective>
Display an overview of the Potenlab workflow ecosystem and available commands.
</objective>

<process>

Read the VERSION file at `/Users/muhammadrayandika/Documents/repository/sunmath/.claude/potenlab-workflow/VERSION` to get the current version. Then respond with:

---

**Potenlab Workflow**

| Property       | Value                          |
|----------------|--------------------------------|
| Package        | potenlab-workflow              |
| Version        | {version from VERSION file}    |
| Install        | `npx potenlab-workflow`        |

**Available commands:**
- `/potenlab:hello` — Confirm installation is active
- `/potenlab:info` — This overview
- `/potenlab:plan-project` — Create all plans from PRD
- `/potenlab:complete-plan` — Generate progress.json
- `/potenlab:execute-phase` — Build a phase with parallel agents
- `/potenlab:developer` — Post-completion adjustments
- `/potenlab:review-plan` — Edit existing plans
- `/potenlab:generate-test` — Generate Vitest test files
- `/potenlab:run-test-all` — Run all tests
- `/potenlab:run-test-phase` — Run tests for a phase
- `/potenlab:verify-test` — Sync tests after changes

**Agents:**
| Agent | Model | Role |
|-------|-------|------|
| potenlab-ui-ux-specialist | Opus | Design system, wireframes, user flows |
| potenlab-tech-lead-specialist | Opus | dev-plan.md — single source of truth |
| potenlab-frontend-specialist | Opus | Component specs, file paths, patterns |
| potenlab-backend-specialist | Opus | Schema, migrations, RLS, queries |
| potenlab-progress-creator | Opus | Parse plans into progress.json |
| potenlab-high-coder | Opus | Complex multi-file implementation |
| potenlab-small-coder | Sonnet | Simple single-file tasks |
| potenlab-qa-specialist | Opus | Test generation and verification |

**Next steps:**
- Run `/potenlab:plan-project` to start planning from a PRD
- Run `npx potenlab-workflow` to update to the latest version

---

Do not add anything beyond the above.

</process>
