# Testing Strategy (Factory)

How the factory decides what to test, what each layer may claim, and what
happens when something fails.

> Named `factory-testing-strategy.md` to avoid colliding with the generated
> product document `docs/testing-strategy.md`, which a project receives from
> `factory/templates/docs/testing-strategy.template.md`.

---

## 1. Layers are selected, not assumed

A project gets only the layers its capability profile justifies. Each layer is
declared applicable or `NOT_APPLICABLE` **with a reason** — never left
undeclared.

| Layer | Applies when | Owner |
|---|---|---|
| Static (lint, typecheck) | always | implementing agent |
| Unit | always | implementing agent |
| Integration | ≥ 2 surfaces | `project-integration` |
| Contract | `api` | `project-api` |
| Browser | `browserTesting` | `project-playwright` |
| Mobile | `mobile` | `project-mobile`, `project-qa` |
| Security | always | `project-security` |
| Performance | a runtime surface exists | `project-performance` |
| Regression | always | `project-regression` |

An API-only project has no browser layer, and GATE-PW is `NOT_APPLICABLE`.
A web-only static site has no contract layer. Neither is a gap.

## 2. Testing happens per slice

Tests run **inside** each vertical feature slice, not in a phase at the end.
A feature reaches `07-test` and `08-playwright` before the next feature
starts.

The reason is economic: a defect found one feature after it was introduced is
cheap; the same defect found after twelve features have been built on top of
it is not. Testing at the end also tends to compress under time pressure —
testing per slice cannot.

## 3. What each layer may claim

| Layer | Can prove | Cannot prove |
|---|---|---|
| Static | the code is well-formed | the code is correct |
| Unit | a function behaves as specified | the feature works |
| Integration | components agree at a boundary | a user can complete a task |
| Contract | server and client share a shape | the UI uses it correctly |
| Browser | a real journey completes in a real browser | behaviour under load |
| Performance | measured numbers under measured conditions | behaviour in production |

Recording a claim beyond a layer's reach is a protocol violation. "Unit tests
pass, therefore the feature works" is the most common form.

## 4. States every feature is tested against

Loading · empty · error · success · unauthorised · offline (where applicable).

These are the states that break in production and the ones an autonomous
agent most often skips, because the happy path is the one described in the
requirements.

## 5. Status vocabulary

| Status | Means |
|---|---|
| `PASS` | executed, and passed |
| `PARTIAL` | executed; some assertions failed or were skipped |
| `FAIL` | executed, and failed |
| `NOT_TESTED` | never executed |
| `BLOCKED` | could not execute; reason recorded |
| `NOT_APPLICABLE` | does not apply to this project |

`NOT_TESTED` and `BLOCKED` never become `PASS` without execution. A layer with
no run is reported, not omitted.

## 6. The bug-fix loop

```
test ──▶ FAIL ──▶ reproduce ──▶ root cause ──▶ fix ──▶ retest ──▶ regression
                       ▲                                    │
                       └──────────── still failing ─────────┘
```

Procedure: `.claude/skills/bug-fix-loop/SKILL.md`.

| Step | Requirement |
|---|---|
| Reproduce | a deterministic reproduction before any fix |
| Root cause | the cause, not the symptom — recorded |
| Fix | narrowest change that addresses the cause |
| Retest | the original failing case, re-executed |
| Regression | previously passing tests, re-executed |

Attempts are bounded by `maxAttemptsPerDefect`. On exhaustion the defect is
`DEFERRED` with its severity; `CRITICAL` or `HIGH` marks the release
`NOT_READY` and escalates.

### Never

- weaken an assertion to make a test pass,
- delete, skip or `@ignore` a failing test,
- re-run a flaky test until it passes — investigate it,
- lower a defect's severity to clear a gate,
- fix the symptom and close the defect.

Rule 11 of `CLAUDE.md` — *fix, don't just report* — means a fixable defect is
fixed in the loop, not filed and left.

## 7. Regression

`11-regression` re-runs the full applicable suite across every completed
feature. Its purpose is to catch what the fixes broke, which is why it runs
after `09-fix`/`10-retest` and again before release.

## 8. Reporting

Results conform to `factory/schemas/test-report.schema.json` and are written
under `evidence/qa/` and `evidence/regression/`. Counts are reported as
executed/passed/failed/not-tested — never as a bare percentage, which hides
what did not run.
