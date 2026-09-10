# Factory Architecture

How this repository is put together, and why.

---

## 1. What the factory is

A set of instructions, templates, schemas and rules that let Claude Code take
a project description plus reference material and drive a software project
from discovery to production readiness.

There is no runtime, no server and no compiled artefact. The factory is
**executable documentation**: Claude Code reads it and behaves accordingly.
That makes precision and internal consistency load-bearing — a contradiction
between two files is a bug, which is why `scripts/validate-factory.sh` exists.

## 2. The prime directive

> Build the factory's output, never the factory's assumptions.

Nothing under `.claude/`, `factory/`, `docs/` or `scripts/` may name a
specific product, client or business domain. Product-specific artefacts are
*generated* into a workspace at run time.

## 3. Two modes

| Mode | Trigger | What may be touched |
|---|---|---|
| FACTORY | no `.project/project.json` | factory internals only |
| PROJECT | `.project/project.json` exists | the product; factory internals are read-only |

```bash
test -f .project/project.json && echo PROJECT_MODE || echo FACTORY_MODE
```

The distinction matters because the same repository is both the tool and the
workspace. Without the check, a session asked to "add a login page" in an
un-started repository would start writing product code into the factory.

## 4. Layers

```
        user
          │  /start-project, /resume, /status …
          ▼
   .claude/commands/          thin entry points; no logic of their own
          │
          ▼
   .claude/agents/            five factory agents
     orchestrator ────────────▶ owns the phase machine
     discovery                  reads inputs, builds the capability profile
     agent-generator            instantiates project agents + documents
     workflow-validator         structural self-check
     project-state              sole writer of .project/state/
          │
          │ reads
          ▼
   factory/rules/             gates, DoD, source of truth, selection matrix
   factory/schemas/           machine-checkable shapes
   factory/templates/         what gets instantiated
          │
          │ generates
          ▼
   .claude/agents/project-*   project agents, chosen by capability
   docs/*.md                  project documents, chosen by capability
   .project/                  manifest + state
   evidence/                  artefacts of real work
```

## 5. Directory map

| Path | Contents | Mode |
|---|---|---|
| `.claude/agents/` | 5 factory agents; generated `project-*` agents join them | both |
| `.claude/commands/` | 7 slash commands | both |
| `.claude/skills/` | 4 reusable procedures | both |
| `factory/templates/agents/` | 22 agent templates + `_TEMPLATE.md` | factory |
| `factory/templates/docs/` | 19 document templates + selection table | factory |
| `factory/templates/project/` | seed manifest, description template | factory |
| `factory/templates/features/` | vertical-slice template | factory |
| `factory/schemas/` | 6 JSON Schemas | factory |
| `factory/rules/` | 9 rule files | factory |
| `docs/` | factory documentation; PROJECT MODE also writes product docs here | both |
| `evidence/` | 13 phase directories | project |
| `examples/` | worked inputs and expected manifests | factory |
| `input/` | user-supplied, read-only | project |
| `.project/` | generated manifest and state, committed | project |
| `scripts/` | prerequisite check, factory self-check | factory |

### Name collisions in `docs/`

Factory documentation and generated product documentation share `docs/`. Where
a name would collide, the factory document takes a `factory-` prefix:
`docs/factory-architecture.md` (factory) versus `docs/architecture.md`
(generated), `docs/factory-testing-strategy.md` versus
`docs/testing-strategy.md`. Adding a factory document means checking the
generated-document list in `factory/templates/docs/README.md` first.

## 6. Where authority lives

| Question | Answered by |
|---|---|
| Which agents does this project get? | `factory/rules/agent-selection-matrix.md` |
| Which documents does it get? | `factory/templates/docs/README.md` |
| Can this phase complete? | `factory/rules/quality-gates.md` |
| Is this feature done? | `factory/rules/definition-of-done.md` |
| Which source wins a conflict? | `factory/rules/source-of-truth.md` |
| What does this status word mean? | `factory/rules/status-vocabulary.md` |
| What shape is this file? | `factory/schemas/` |
| What is the project? | `.project/project.json` |
| Where are we? | `.project/state/state.json` |

Exactly one file answers each question. Where a second file needs the same
fact, it links rather than restates — duplicated rules drift.

## 7. Design principles

1. **Generic by construction.** No product knowledge in the factory.
2. **Dynamic selection.** Build only what the capability profile requires; a
   web-only project gets no database agent and no API contract.
3. **Evidence over assertion.** If it was not run, it did not pass.
4. **Vertical slices.** Features complete end to end, not layer by layer.
5. **Resumable.** State survives crashes, context resets and new sessions.
6. **Gated.** Nothing is `COMPLETED` until its gate passes.
7. **Honest.** `NOT_TESTED` and `BLOCKED` never silently become `PASS`.

## 8. Self-check

```bash
./scripts/check-prerequisites.sh   # tools present?
./scripts/validate-factory.sh      # factory internally consistent?
```

The validator checks layout, agent and command presence, schema validity,
seed-manifest conformance, the nine-section agent contract, gate definition
versus reference, placeholder coverage, document-template coverage, clone
integrity, and the honesty invariants. It exits non-zero on any error.

## 9. Further reading

| Document | Covers |
|---|---|
| `docs/agent-system.md` | the agent contract and write scopes |
| `docs/orchestration.md` | the phase machine |
| `docs/project-generation.md` | how agents and documents are selected |
| `docs/project-state.md` | state, journal and resume |
| `docs/evidence-strategy.md` | what counts as evidence |
| `docs/factory-testing-strategy.md` | test layers and the bug-fix loop |
| `docs/playwright-strategy.md` | browser testing and its honesty rules |
