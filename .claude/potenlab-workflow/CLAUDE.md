# Potenlab Workflow — Plugin Rules

These rules are automatically applied when the potenlab-workflow plugin is active.

---

## Project Structure: Bulletproof React

All frontend code MUST follow this structure:

```
src/
├── app/              # Routes, providers, router
├── components/       # SHARED + STYLED components
│   ├── ui/           # shadcn components
│   ├── layouts/      # Page layouts
│   ├── common/       # Generic reusable (LoadingSpinner, ErrorBoundary)
│   └── {feature}/    # Feature-specific STYLED/PRESENTATIONAL components
├── config/           # Global config, env vars
├── features/         # BUSINESS LOGIC only
│   └── {name}/
│       ├── api/      # Supabase queries + React Query hooks
│       ├── components/ # BUSINESS-PURPOSE only (list, detail, create, edit, delete)
│       ├── hooks/    # Feature-specific hooks
│       ├── types/    # Feature types
│       └── utils/    # Feature utilities
├── hooks/            # Shared custom hooks
├── lib/              # Library wrappers (supabase client)
├── stores/           # Global state (Zustand)
├── types/            # Shared TypeScript types
└── utils/            # Shared utility functions
```

### Structure Rules

1. **features/{name}/components/** = Business-purpose components ONLY (list, detail, create, edit, delete)
2. **components/{feature}/** = Styled/presentational components (card, table, avatar, badge)
3. **components/ui/** = shadcn primitives, **components/common/** = generic reusables
4. **NEVER import across features** — compose at app level
5. **No barrel files** — import directly from source
6. **Unidirectional flow** — shared -> features -> app

---

## React Best Practices (Critical)

### Eliminating Waterfalls
- Use `Promise.all()` for independent async operations
- Place Suspense boundaries per data source, not per component
- Defer `await` until the value is actually needed
- Never chain sequential fetches that could run in parallel

### Bundle Size
- **No barrel file imports** — import directly from source files
- Use `next/dynamic` for heavy components not needed on initial render
- Defer non-critical third-party libraries (analytics, chat widgets)
- Configure `optimizePackageImports` in next.config.js

### Re-render Prevention
- Use `React.memo()` for components in lists or frequently re-rendering parents
- Derive state directly in render — never use useEffect to sync state
- Use functional `setState` when new state depends on previous state
- Use `useRef` for values that change but don't need re-renders

### Server Performance
- Use `React.cache()` to deduplicate identical server-side fetches
- Fetch data in parallel with `Promise.all()` in server components
- Use `after()` for non-blocking operations (logging, analytics)

---

## Supabase Postgres Best Practices (Critical)

### Schema Design
- Use `bigint GENERATED ALWAYS AS IDENTITY` or UUIDv7 for PKs (never serial, never random UUIDv4)
- Use `TIMESTAMPTZ` always (never `TIMESTAMP`)
- Use proper types: NUMERIC, BOOLEAN, JSONB — not TEXT for everything
- **Always index FK columns** — Postgres does NOT auto-index foreign keys

### RLS Policies
- Enable RLS on ALL user-data tables — no exceptions
- Use `auth.uid()` directly in policies
- Keep policies simple — use security definer functions for complex access
- Never use subqueries in policies (performance killer)

### Query Performance
- Select only needed columns (never `SELECT *`)
- Use cursor-based pagination (never OFFSET for large datasets)
- Create composite indexes for multi-column WHERE clauses
- Use `EXPLAIN ANALYZE` to validate query plans

### Connection Management
- Use Supavisor connection pooling (Supabase built-in)
- Set `idle_in_transaction_session_timeout = '30s'`
- Set `statement_timeout = '10s'`
- Use transaction mode for short-lived queries

---

## Agent Workflow

```
PRD -> ui-ux-specialist -> ui-ux-plan.md
                                |
                                v
                     tech-lead-specialist -> dev-plan.md
                                |
                     +----------+----------+
                     |                     |
              frontend-specialist    backend-specialist
              (frontend-plan.md)    (backend-plan.md)
                     |                     |
                     +----------+----------+
                                |
                     qa-specialist -> test-plan.md
                     (test scenario planning from dev-plan + backend-plan)
                                |
                     progress-creator -> progress.json
                                |
                     +----------+----------+
                     |                     |
                 high-coder          small-coder
              (complex tasks)      (simple tasks)
                     |                     |
                     +----------+----------+
                                |
                     qa-specialist -> .test.ts files
                     (test generation from test-plan.md)
                                |
                     security-specialist -> security-report.md
                     (security audit of codebase)
```

### Key Agents
| Agent | Role | Model |
|-------|------|-------|
| ui-ux-specialist | Design system, wireframes, user flows | Opus |
| tech-lead-specialist | dev-plan.md — single source of truth | Opus |
| frontend-specialist | Component specs, file paths, patterns | Opus |
| backend-specialist | Schema, migrations, RLS, queries | Opus |
| progress-creator | Parses plans into progress.json | Opus |
| high-coder | Complex multi-file implementation | Opus |
| small-coder | Simple single-file tasks | Sonnet |
| qa-specialist | Test plan creation, test generation, verification | Opus |
| security-specialist | Security audit, vulnerability scanning, RLS verification | Opus |

### Key Skills
| Skill | Trigger | What It Does |
|-------|---------|-------------|
| plan-project | /plan-project | Full planning workflow (specialists + test plan generation) |
| developer | /developer | Executes tasks from progress.json |
| review-plan | /review-plan | Reviews and adjusts existing plans |
| complete-plan | /complete-plan | Marks tasks complete in progress.json |
| execute-phase | /execute-phase | Runs tasks in a phase (wave-based, max 4 agents per wave) |
| info | /info | Shows project status and progress |
| generate-test | /generate-test | Generates .test.ts files from test-plan.md |
| run-test-all | /run-test-all | Runs all Vitest tests, produces test.result.json |
| run-test-phase | /run-test-phase | Runs tests for a specific phase |
| verify-test | /verify-test | Syncs tests after code changes |
| security-review | /security-review | Full security audit → security-list.json → optional auto-fix |
| security-resolve | /security-resolve | Resolves pending findings from security-list.json |
