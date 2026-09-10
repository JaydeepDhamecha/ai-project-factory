---
description: Generate or revise the development plan and feature slices without implementing anything.
argument-hint: "[optional: what to re-plan, e.g. 'reorder for offline-first' ]"
---

# /plan

Planning only. **No implementation happens in this command.**

Focus, if given: **$ARGUMENTS**

## Preconditions

- `.project/project.json` should exist. If it does not, run discovery and
  understanding first (phases 00–01), then plan — but do not generate agents or
  scaffold code.
- `docs/requirements.md` and `docs/acceptance-criteria.md` must exist. Without
  them a plan is guesswork; report `BLOCKED` and run `/start-project` instead.

## Steps

1. Read requirements, acceptance criteria, architecture, platform requirements
   and the capability profile.
2. Derive features. A feature is a **vertical slice** delivering user-visible
   value end to end — not "build the database", not "write the API layer".
3. Build the dependency graph. Typical ordering forces:
   - authentication before anything user-scoped,
   - core entity CRUD before features that reference it,
   - shared layout/navigation before pages that live in it,
   - read paths before write paths where that de-risks,
   - anything a demo or acceptance depends on, earlier.
4. Detect cycles. Break them by splitting a feature, not by ignoring the edge.
5. For each feature record: id, name, summary, order, priority (MoSCoW),
   `dependsOn`, requirement ids, acceptance criterion ids, the applicable
   steps, and — if `offline` — the offline classification.
6. Write `docs/development-plan.md` (human) and `.project/state/features.json`
   (machine, conforming to `factory/schemas/features.schema.json`).
7. Initialise or update `docs/development-status.md`.
8. Evaluate GATE-ARCH criterion ARCH-10.

## Output

```markdown
## Feature order

| # | Id | Feature | Depends on | Priority | Steps |
|---|----|---------|-----------|----------|-------|
| 1 | f01-authentication | Authentication | — | MUST | backend, api, web, integration, playwright, qa |
| 2 | f02-… | … | f01 | MUST | … |

## Ordering rationale
<why this order — the dependency argument, not a restatement of the table>

## Deferred / out of scope
<what was deliberately not planned, and why>
```

## Re-planning an in-flight project

- Preserve the status of features already `COMPLETED`.
- Never renumber an existing feature id — ids are stable
  (`factory/rules/naming-conventions.md`).
- New features get new ids appended.
- Record the re-plan as a decision (`ADR-NNN`) with the reason.
- Journal `decision_recorded`.
