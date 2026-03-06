# Reference Docs — Navigation Guide

## Overview

Best practices reference docs used by specialist agents. Covers Supabase/Postgres (backend-specialist), Vitest testing (all agents writing tests), and application security (security-specialist).

## Structure

```
references/
  AGENTS.md                    # This navigation guide
  {prefix}-{topic}.md          # Individual reference files (30 Postgres)
  vitest-best-practices.md     # Consolidated vitest testing guide
```

## Usage

1. Read this file (`AGENTS.md`) for the full reference index
2. Read individual files for detailed documentation
3. Reference files are loaded on-demand — read only what you need

---

## Vitest Testing

| File | Impact | Use When |
|------|--------|----------|
| `vitest-best-practices.md` | CRITICAL | Writing, reviewing, or refactoring `*.test.ts` / `*.spec.ts` files |

Covers: organization, AAA pattern, parameterized tests, error handling, assertions, test doubles, async testing, performance, vitest features, snapshot testing.

---

## Supabase Postgres

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | Query Performance | CRITICAL | `query-` |
| 2 | Connection Management | CRITICAL | `conn-` |
| 3 | Security & RLS | CRITICAL | `security-` |
| 4 | Schema Design | HIGH | `schema-` |
| 5 | Concurrency & Locking | MEDIUM-HIGH | `lock-` |
| 6 | Data Access Patterns | MEDIUM | `data-` |
| 7 | Monitoring & Diagnostics | LOW-MEDIUM | `monitor-` |
| 8 | Advanced Features | LOW | `advanced-` |

Reference files are named `{prefix}-{topic}.md` (e.g., `query-missing-indexes.md`).

## Available References

**Query Performance** (`query-`):
- `query-missing-indexes.md`
- `query-composite-indexes.md`
- `query-covering-indexes.md`
- `query-index-types.md`
- `query-partial-indexes.md`

**Connection Management** (`conn-`):
- `conn-pooling.md`
- `conn-limits.md`
- `conn-idle-timeout.md`
- `conn-prepared-statements.md`

**Security & RLS** (`security-`):
- `security-rls-basics.md`
- `security-rls-performance.md`
- `security-privileges.md`

**Schema Design** (`schema-`):
- `schema-primary-keys.md`
- `schema-data-types.md`
- `schema-foreign-key-indexes.md`
- `schema-lowercase-identifiers.md`
- `schema-partitioning.md`

**Concurrency & Locking** (`lock-`):
- `lock-short-transactions.md`
- `lock-deadlock-prevention.md`
- `lock-skip-locked.md`
- `lock-advisory.md`

**Data Access Patterns** (`data-`):
- `data-n-plus-one.md`
- `data-pagination.md`
- `data-batch-inserts.md`
- `data-upsert.md`

**Monitoring & Diagnostics** (`monitor-`):
- `monitor-explain-analyze.md`
- `monitor-pg-stat-statements.md`
- `monitor-vacuum-analyze.md`

**Advanced Features** (`advanced-`):
- `advanced-jsonb-indexing.md`
- `advanced-full-text-search.md`

---

*31 reference files across 9 categories*