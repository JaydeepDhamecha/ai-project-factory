# {{PROJECT_NAME}} — Development Plan

> Owner: `project-planner` · The authoritative feature order.
> Machine-readable twin: `.project/state/features.json`
> (`factory/schemas/features.schema.json`). If the two disagree, the JSON wins
> and this document is regenerated.

## Ordering rationale

Why this order and not another — dependencies, risk, and what unblocks the
most downstream work.

## Feature slices

Each feature is a **vertical slice**: it goes from data to interface to
verified behaviour before the next one starts. The factory does not build a
whole backend and test at the end.

| Order | Id | Feature | Priority | Depends on | Requirements | Steps |
|---|---|---|---|---|---|---|
| 1 | f01-{{FEATURE_SLUG}} | | MUST | — | | {{FEATURE_STEPS}} |

Priority: `MUST` · `SHOULD` · `COULD` · `WONT`.
Steps are drawn from: database → backend → api → web → mobile → integration →
playwright → qa → regression, and **only the steps this project needs appear**.

## Per-feature detail

### f01-{{FEATURE_SLUG}}

| Field | Value |
|---|---|
| Summary | |
| Requirements | |
| Acceptance criteria | |
| Depends on | |
| Offline class | |
| Definition of Done | `factory/rules/definition-of-done.md` |

Steps:

| Step | Agent | Status | Evidence |
|---|---|---|---|

## Dependency graph

```
f01 → f02 → f04
  └─→ f03
```

## Deferred

| Id | Feature | Why deferred | Revisit when |
|---|---|---|---|

Deferral is a decision and is recorded. Quietly dropping a feature is not.

## Risks to the plan

| Risk | Affects | Likelihood | Mitigation |
|---|---|---|---|
