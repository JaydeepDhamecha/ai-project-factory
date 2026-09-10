# Orchestration

The phase machine the `orchestrator` runs. Authoritative for order; gate
criteria live in `factory/rules/quality-gates.md`.

---

## 1. Phases

| # | Phase | Purpose | Primary agent | Gate |
|---|---|---|---|---|
| 00 | `00-discover` | Read inputs, extract requirements, build the capability profile | `discovery` | — |
| 01 | `01-understand` | Turn findings into requirements, stories, acceptance criteria | `project-requirements` | GATE-REQ |
| 02 | `02-plan` | Architecture, stack, dependency-ordered feature slices | `project-architect`, `project-planner` | GATE-ARCH |
| 03 | `03-select-agents` | Evaluate the selection matrix; instantiate the roster | `agent-generator` | — (`workflow-validator`) |
| 04 | `04-generate-structure` | Create documents and platform directories | `agent-generator` | GATE-ARCH (re-check) |
| 05 | `05-implement` | Build the current feature slice | per-step agent | GATE-IMPL (per feature) |
| 06 | `06-integrate` | Join the slice's surfaces | `project-integration` | GATE-INTG (per feature) |
| 07 | `07-test` | Static, unit, integration, contract | `project-qa` | GATE-TEST |
| 08 | `08-playwright` | Real browser validation | `project-playwright` | GATE-PW |
| 09 | `09-fix` | Bug-fix loop over open defects | `project-bug-fixer` | — (loop) |
| 10 | `10-retest` | Re-run what failed | `project-qa`, `project-playwright` | GATE-TEST + GATE-PW |
| 11 | `11-regression` | Full suite across completed features | `project-regression` | GATE-REG |
| 12 | `12-security` | Threat review, authorisation tests, dependency audit | `project-security` | GATE-SEC |
| 13 | `13-performance` | Measure against budgets | `project-performance` | GATE-PERF |
| 14 | `14-release` | Final gate evaluation and readiness report | `orchestrator`, `project-release` | GATE-REL |

Phase ids are stable and appear in `.project/project.json`, the state file and
every evidence path. The enum lives in `factory/schemas/project.schema.json`.

## 2. Flow

```
00 discover
     ▼
01 understand ──GATE-REQ──▶
     ▼
02 plan ──GATE-ARCH──▶
     ▼
03 select agents ──validator──▶
     ▼
04 generate structure ──GATE-ARCH──▶
     ▼
   ┌───────────── per feature slice, in dependency order ─────────────┐
   │  05 implement ──GATE-IMPL──▶  06 integrate ──GATE-INTG──▶        │
   │  07 test ──GATE-TEST──▶  08 playwright ──GATE-PW──▶              │
   │         │ any failure                                            │
   │         ▼                                                        │
   │  09 fix ──▶ 10 retest ──▶ back to the failed gate                │
   └──────────────────────────────────────────────────────────────────┘
     ▼
11 regression ──GATE-REG──▶
     ▼
12 security ──GATE-SEC──▶   13 performance ──GATE-PERF──▶
     ▼
14 release ──GATE-REL──▶  final report
```

Phases 05–10 repeat per feature. Phases 11–14 run once, over the whole
project, after every feature has completed or been explicitly deferred.

## 3. Vertical slices

Within `05-implement`, a feature is built through only the steps that apply:

```
database → backend → api → web → mobile → integration → playwright → qa → regression
```

A web-only project's slice is `web → playwright → qa → regression`. An
API-only project's is `database → backend → api → qa → regression`, and
GATE-PW is recorded `NOT_APPLICABLE` — recorded, not omitted.

The factory does not build a whole backend and test at the end. Each slice is
verified before the next begins, so an architectural mistake surfaces after
one feature rather than after all of them.

## 4. Skipping a phase

A phase whose capability condition is false is set `NOT_APPLICABLE` with a
reason, and its gate is likewise `NOT_APPLICABLE`. It is never left
`NOT_STARTED`, and never silently omitted — the difference between "does not
apply" and "we forgot" must be visible in the state file.

| Phase | Skipped when |
|---|---|
| `08-playwright` | `browserTesting` false (no web surface) |
| `06-integrate` | fewer than two surfaces |
| `13-performance` | no runtime surface |

## 5. Gate evaluation

At each boundary the orchestrator:

1. Reads the gate's criteria from `factory/rules/quality-gates.md`.
2. Evaluates each criterion against evidence that exists on disk.
3. Records a criterion-level result, not a single verdict.
4. Advances on `PASS`, or on a `WAIVED` carrying a reason and a named owner.
5. On `FAIL`, does not advance: it identifies the unsatisfied criteria,
   dispatches the owning agent, and re-evaluates.

A criterion marked `PASS` must name an evidence path that exists. A gate whose
evidence cannot be found is a `FAIL`, regardless of what any agent reported.

## 6. The bug-fix loop

```
test ──▶ FAIL ──▶ reproduce ──▶ root cause ──▶ fix ──▶ retest ──▶ regression
                       ▲                                    │
                       └──────────── still failing ─────────┘
```

Driven through `.claude/skills/bug-fix-loop/SKILL.md`. Attempts are bounded by
`maxAttemptsPerDefect`. On exhaustion the defect is recorded `DEFERRED` with
its severity; a `CRITICAL` or `HIGH` deferral marks the release `NOT_READY`
and escalates. The loop is never exited by lowering the severity, disabling
the test, or narrowing the assertion.

## 7. Escalation

The orchestrator runs to completion without asking permission between normal
engineering steps. It stops only for the triggers in
`factory/rules/source-of-truth.md` — missing information it cannot safely
assume, a contradiction it cannot resolve, an irreversible or outward-facing
action, an exhausted fix budget, a policy boundary, or a request to push to a
remote.

Everything that does not depend on the blocked item is completed first. A
blocked run reports precisely what is needed to unblock it.

## 8. State

Every phase transition, feature step, gate evaluation and defect change is
checkpointed through `project-state`. The orchestrator never writes
`.project/state/` directly. See `docs/project-state.md`.

## 9. Termination

| Outcome | Means |
|---|---|
| `COMPLETED` | every feature completed or explicitly deferred, every mandatory gate passed, final report published |
| `BLOCKED` | work stopped on an escalation trigger; everything independent of it was finished |
| `FAILED` | a mandatory gate could not be passed within budget |

`BLOCKED` and `FAILED` are honest outcomes and are preferred to a false
`COMPLETED`.
