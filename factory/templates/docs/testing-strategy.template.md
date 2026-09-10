# {{PROJECT_NAME}} — Testing Strategy

> Owner: `project-qa` · Defines which layers apply to *this* project and what
> each is allowed to claim. A layer that does not apply is declared
> `NOT_APPLICABLE` here, with a reason.

## Applicable layers

| Layer | Applies | Owner | Why / why not |
|---|---|---|---|
| Static (lint, typecheck) | | | |
| Unit | | | |
| Integration | | | |
| Contract (API) | | | |
| Browser (Playwright MCP) | | | |
| Mobile | | | |
| Accessibility | | | |
| Security | | | |
| Performance | | | |
| Regression | | | |

## What each layer may claim

| Layer | Can prove | Cannot prove |
|---|---|---|
| Unit | a function behaves as specified | the feature works |
| Integration | components agree at their boundary | the user can complete a task |
| Contract | server and client share a shape | the UI uses it correctly |
| Browser | a real user journey completes in a real browser | performance under load |
| Static | the code is well-formed | the code is correct |

Recording a claim beyond a layer's reach is a protocol violation.

## Commands

| Layer | Command |
|---|---|
| Lint | {{CMD_LINT}} |
| Typecheck | {{CMD_TYPECHECK}} |
| Unit / integration | {{CMD_TEST}} |
| Build | {{CMD_BUILD}} |

## Coverage targets

| Area | Target | Rationale |
|---|---|---|

A coverage number is a diagnostic, not a goal. It is never the sole basis for
passing `GATE-TEST`.

## Test data

| Dataset | Purpose | Contains real data |
|---|---|---|

## States every feature is tested against

Loading · empty · error · success · unauthorised · offline (where applicable).
These are the states that break in production, and the ones agents most often
skip.

## Defect handling

Every failure enters the bug-fix loop in `.claude/skills/bug-fix-loop/SKILL.md`:
reproduce → root cause → fix → retest → regression. A failure is never
downgraded to a note, and a flaky test is investigated rather than re-run
until green.

## Reporting

Results conform to `factory/schemas/test-report.schema.json` and are written
under `evidence/qa/`.

| Status | Means |
|---|---|
| `PASS` | executed, and passed |
| `PARTIAL` | executed, some assertions failed or were skipped |
| `FAIL` | executed, and failed |
| `NOT_TESTED` | never executed |
| `BLOCKED` | could not execute; reason recorded |
| `NOT_APPLICABLE` | does not apply to this project |
