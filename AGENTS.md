# AGENTS.md — Agent Registry

Two populations of agents exist in this repository.

- **Factory agents** — permanent, product-agnostic, live in `.claude/agents/`.
  They run the factory itself and ship with the repository.
- **Project agents** — generated per project by the `agent-generator` from
  templates in `factory/templates/agents/`, written into `.claude/agents/` with
  a `project-` prefix, and recorded in `.project/project.json`.

An agent that is not in the manifest's `selectedAgents` list must not be
invoked. An agent must not write outside the paths its definition allows.

---

## 1. Factory agents (permanent)

| Agent | File | Role |
|---|---|---|
| `orchestrator` | `.claude/agents/orchestrator.md` | Owns the phase machine. Selects agents, sequences features, enforces gates, drives the bug-fix loop, produces the final report. The only agent allowed to change `currentPhase`. |
| `discovery` | `.claude/agents/discovery.md` | Reads `input/`, all PDFs and images, and any existing repository code. Produces the discovery findings and the proposed capability profile. Never implements. |
| `agent-generator` | `.claude/agents/agent-generator.md` | Turns the capability profile into a concrete agent roster by instantiating templates. Never implements product code. |
| `workflow-validator` | `.claude/agents/workflow-validator.md` | Structural self-check: schemas, cross-references, gate coverage, orphaned agents, missing documents. Runs at factory build time and after every generation step. |
| `project-state` | `.claude/agents/project-state.md` | Sole writer of `.project/state/`. Append-only journal, checkpoint, resume, integrity repair. |

### Factory agent interaction

```
                       ┌──────────────┐
   user command  ─────▶│ orchestrator │◀──── resume ──── project-state
                       └──────┬───────┘
              ┌───────────────┼────────────────┐
              ▼               ▼                ▼
        discovery      agent-generator   workflow-validator
              │               │                │
              └──── writes ───┴──── reads ─────┘
                              ▼
                    generated project agents
```

Every factory agent reports outcomes back to the orchestrator; only the
orchestrator advances phases; only `project-state` writes state files.

---

## 2. Project agents (generated on demand)

Templates live in `factory/templates/agents/`. Selection is governed by
`factory/rules/agent-selection-matrix.md` and the capability flags in the
manifest. **No project generates all of them.**

| Template | Generated when | Primary output |
|---|---|---|
| `product` | always | `docs/PRD.md`, `docs/project-overview.md` |
| `requirements` | always | `docs/requirements.md`, `docs/user-stories.md`, `docs/acceptance-criteria.md` |
| `planner` | always | `docs/development-plan.md`, `.project/state/features.json` |
| `architect` | always | `docs/architecture.md` |
| `technology` | always | `docs/technology-stack.md` |
| `designer` | `web` or `mobile` or `adminPortal` | `docs/design-system.md` |
| `database` | `database` | `docs/database-schema.md`, migrations |
| `api` | `api` or `backend` | `docs/api-contract.md` |
| `backend` | `backend` | server implementation |
| `web` | `web` or `adminPortal` | web client implementation |
| `mobile` | `mobile` | mobile client implementation |
| `integration` | ≥ 2 of {backend, web, mobile} | wiring, contract conformance |
| `qa` | always | `docs/testing-strategy.md`, automated tests |
| `playwright` | `browserTesting` (implied by `web`/`adminPortal`) | `evidence/playwright/` |
| `bug-fixer` | always | defect fixes + `evidence/qa/defects/` |
| `regression` | always | `evidence/regression/` |
| `security` | always | `docs/security.md`, `evidence/security/` |
| `performance` | `backend` or `web` or `mobile` | `evidence/performance/` |
| `devops` | `deployable` | `docs/deployment.md`, CI, containers |
| `reviewer` | always | independent audit report |
| `release` | always | release readiness report |
| `offline-sync` | `offline` | `docs/offline-sync.md` |

### Naming

Generated files: `.claude/agents/project-<template>.md`
Generated agent id in the manifest: `project-<template>`

### Contract every agent obeys

Each agent definition — factory or generated — must declare all nine sections
required by `factory/rules/agent-authoring-rules.md`:

1. Purpose
2. Responsibilities
3. Inputs
4. Required documents
5. Files it can modify
6. Outputs
7. Validation
8. Completion criteria
9. Failure handling

`workflow-validator` fails the build if any section is missing.

---

## 3. Escalation path

```
project agent  ──fails──▶  orchestrator  ──cannot resolve──▶  user
      │                          │
      └── defect ──▶ bug-fixer ──┘   (loop, bounded by maxFixAttempts)
```

An agent never escalates directly to the user. It reports `FAILED` with a
reason to the orchestrator, which decides between retry, bug-fix loop,
re-planning, `BLOCKED`, or user escalation.

---

## 4. Where each agent may write

Write scopes are enforced by convention and audited by `workflow-validator`.

| Agent class | Allowed write paths |
|---|---|
| orchestrator | `.project/` (via project-state), `docs/development-status.md`, final reports |
| discovery | `docs/project-overview.md`, `docs/source-analysis.md`, `evidence/discovery/` |
| agent-generator | `.claude/agents/project-*.md`, manifest `selectedAgents` |
| workflow-validator | `evidence/*/validation-*.md` |
| project-state | `.project/state/**` |
| document agents | their own `docs/*.md` + matching `evidence/<phase>/` |
| implementation agents | their platform source tree + their tests |
| test agents | tests + `evidence/<phase>/` (never product source) |
| bug-fixer | any product source, plus `evidence/qa/defects/` |

A test agent that "fixes" product code directly is a protocol violation — it
must hand the defect to `bug-fixer`.
