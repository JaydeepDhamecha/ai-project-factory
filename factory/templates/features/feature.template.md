# {{FEATURE_ID}} — {{FEATURE_NAME}}

> One vertical slice. Instantiated by `project-planner` into
> `docs/development-plan.md` § Per-feature detail. The machine-readable twin
> is an entry in `.project/state/features.json`
> (`factory/schemas/features.schema.json`), which is authoritative.

## Summary

| Field | Value |
|---|---|
| Id | {{FEATURE_ID}} |
| Order | |
| Priority | `MUST` \| `SHOULD` \| `COULD` \| `WONT` |
| Depends on | |
| Offline class | |
| Status | `NOT_STARTED` |

## Scope

What this slice delivers, end to end. One or two sentences.

### Out of scope

What a reader might reasonably expect here and will not find. Prevents the
slice quietly growing during implementation.

## Requirements

| REQ | Statement | Source |
|---|---|---|

## Acceptance criteria

| AC | Given / When / Then | Layer that verifies it |
|---|---|---|

Every criterion names the layer that will verify it. A criterion no layer can
verify is either rewritten or accepted as `NOT_TESTED` before work starts —
never discovered at the gate.

## Steps

Only the steps this project needs. The full sequence is
database → backend → api → web → mobile → integration → playwright → qa →
regression.

| # | Step | Agent | Status | Evidence |
|---|---|---|---|---|
| 1 | {{FEATURE_STEPS}} | | `NOT_STARTED` | |

A step that does not apply is `NOT_APPLICABLE` with a reason, not absent.

## States to implement and test

| State | Applies | Behaviour |
|---|---|---|
| Loading | | |
| Empty | | |
| Error | | |
| Success | | |
| Unauthorised | | |
| Offline | | |

## Definition of Done

Evaluated against `factory/rules/definition-of-done.md`. The slice is done
only when every applicable line passes with evidence.

| Criterion | Result | Evidence |
|---|---|---|
| Requirements satisfied | | |
| Acceptance criteria satisfied | | |
| Implementation complete | | |
| Tests pass | | |
| Integration passes | | |
| Browser validation passes | | |
| Mobile validation passes | | |
| Security checks pass | | |
| Regression passes | | |

## Defects

| Id | Severity | Status | Evidence |
|---|---|---|---|

## Decisions and assumptions

| # | Decision / assumption | Rationale | Source |
|---|---|---|---|
