# Agent System

What an agent is in this factory, what every agent must declare, and how work
is divided so two agents never own the same file.

---

## 1. Two populations

| | Factory agents | Project agents |
|---|---|---|
| Where | `.claude/agents/<id>.md` | `.claude/agents/project-<template>[-<variant>].md` |
| Count | 5, fixed | 0–22+, chosen per project |
| Origin | authored | generated from `factory/templates/agents/` |
| Lifetime | permanent | one project |
| Knows the product | no | yes |

### Factory agents

| Agent | Owns |
|---|---|
| `orchestrator` | the phase machine, gate evaluation, the final report |
| `discovery` | reading inputs, building the capability profile |
| `agent-generator` | instantiating project agents and documents |
| `workflow-validator` | structural self-check of factory and project |
| `project-state` | sole writer of `.project/state/` |

Only the orchestrator may advance a phase, evaluate a gate, or declare
anything `COMPLETED`. Only `project-state` may write state. Concentrating
those two powers is what keeps a long run coherent.

## 2. The nine-section contract

Every agent file — factory or generated — has these sections, in this order.
`scripts/validate-factory.sh` §8 enforces it.

| § | Section | Answers |
|---|---|---|
| 1 | Purpose | why this agent exists |
| 2 | Responsibilities | what it does, numbered |
| 3 | Inputs | what it reads |
| 4 | Required documents | what must exist before it starts |
| 5 | Files it can modify | its write scope — allowed and denied |
| 6 | Outputs | what it produces, including evidence paths |
| 7 | Validation | what it checks before reporting |
| 8 | Completion criteria | when it may report done |
| 9 | Failure handling | what it does when each thing goes wrong |

Sections 5, 7 and 9 carry the weight. An agent without an explicit write scope
edits whatever seems reasonable; an agent without §9 improvises under
pressure, which is when improvisation is least wanted.

### Frontmatter

```yaml
---
name: <id matching the filename stem>
description: <one line saying when to invoke it>
model: inherit
---
```

## 3. Write scopes

Every path in the repository has at most one owning agent.

| Rule | |
|---|---|
| One owner per path | two agents may not both list a path as allowed |
| Denied is explicit | §5 names what the agent must not touch, not just what it may |
| `input/` is read-only | for every agent, without exception |
| Factory internals are read-only in PROJECT MODE | generation never rewrites `.claude/agents/orchestrator.md` and its four peers |
| State goes through `project-state` | no other agent writes `.project/state/` |
| Documents have one author | the generator creates the stub; the owning agent writes the content |

Where one template serves two surfaces — a customer app and an admin portal —
the generator emits two agents with disambiguated ids and non-overlapping
scopes:

```
project-web-customer.md   scope: apps/customer
project-web-admin.md      scope: apps/admin
```

## 4. Lifecycle

```
selected ──▶ generated ──▶ validated ──▶ invoked ──▶ reports ──▶ checkpointed
   │             │             │                        │
matrix     placeholders    9 sections,             PASS / PARTIAL /
condition   substituted    scope, gate ref         FAIL / BLOCKED
```

An agent is invoked only if it is in `selectedAgents`. The orchestrator never
invokes an agent absent from the roster, and never performs an agent's work
itself — if it finds itself implementing, it has skipped selection and must
stop and correct that.

## 5. Reporting

An agent reports one of `PASS`, `PARTIAL`, `FAIL`, `NOT_TESTED`, `BLOCKED`,
`NOT_APPLICABLE` (`factory/rules/status-vocabulary.md`), with:

- what it did,
- evidence paths that exist,
- what it did not do, and why,
- anything it assumed.

An agent may not mark its own phase `COMPLETED`; it reports, and the
orchestrator decides against the gate.

## 6. Failure

| Situation | Agent's obligation |
|---|---|
| Missing required document | report `BLOCKED` naming it — do not improvise the content |
| A tool is unavailable | report `BLOCKED` with the reason — do not substitute reasoning for execution |
| Its own validation fails | fix what it can, report `FAILED` with the remainder |
| Asked for work outside its scope | decline and name the owning agent |
| Ambiguity in requirements | apply `factory/rules/source-of-truth.md`, record the assumption, continue |

## 7. Adding a template

1. Copy `factory/templates/agents/_TEMPLATE.md`.
2. Write all nine sections; give §5 an explicit scope that overlaps nobody.
3. Add a row to `factory/rules/agent-selection-matrix.md` §2 with its
   condition.
4. Document any new placeholder in `factory/rules/agent-authoring-rules.md` §4.
5. Reference the gate the agent's work feeds.
6. Run `./scripts/validate-factory.sh`.

A template not in the matrix is never generated; a matrix row without a
template is an error the validator catches.
