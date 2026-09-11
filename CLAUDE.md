# CLAUDE.md — AI Software Development Factory

This repository is a **factory**, not an application.

Its purpose is to take a short project description plus reference material
(PDFs, screenshots, wireframes, specs) and drive a complete software project
from discovery through production readiness — dynamically selecting the
agents, documents, technologies and tests that the project actually needs.

---

## 1. Prime directive

> **Build the factory's output, never the factory's assumptions.**

Nothing in this repository may hard-code a specific product, client, domain or
technology stack. Every product-specific artefact is *generated* into a project
workspace at run time from the templates in `factory/templates/`.

If you are ever about to write a business entity name (a customer, a product, a
domain noun) into a file under `factory/`, `.claude/` or `docs/`, stop — it
belongs in the generated project, not in the factory.

---

## 2. Two modes of operation

Claude Code operates in exactly one of two modes in this repository. Determine
the mode before doing anything else.

| Mode | Trigger | Rules |
|---|---|---|
| **FACTORY MODE** | `.project/project.json` does **not** exist, or the user is explicitly editing factory internals | You are maintaining the factory. Only touch `.claude/`, `factory/`, `docs/`, `scripts/`, `examples/`, root files. Never create `backend/`, `web/`, `mobile/`. |
| **PROJECT MODE** | `.project/project.json` exists | You are building the user's product. The manifest and state files are authoritative. Resume from `.project/state/`; never restart from zero. |

Detect with:

```bash
test -f .project/project.json && echo PROJECT_MODE || echo FACTORY_MODE
```

---

## 3. Entry points

The user drives the factory with slash commands. Do not invent new workflows
when a command already exists.

| Command | Purpose |
|---|---|
| `/start-project` | **The** entry point. Runs the entire lifecycle autonomously: discover → understand → plan → generate → implement → test → fix → regression → security → performance → release. It executes the pipeline; it never merely checks prerequisites or reports a plan. |
| `/status` | Report current phase, feature, gates, blockers, test status. Read-only. |
| `/resume` | Continue an interrupted run from persisted state. |
| `/plan` | Regenerate or revise the development plan without implementing. |
| `/test` | Run the applicable test layers, including Playwright MCP. |
| `/audit` | Independent review: requirements coverage, consistency, security, gaps. |
| `/release` | Final gate evaluation and release readiness report. |

---

## 4. Non-negotiable rules

1. **Never fabricate evidence.** If a test did not run, its status is
   `NOT_TESTED` or `BLOCKED`, with a recorded reason. `NOT_TESTED` and
   `BLOCKED` never become `PASS`.
2. **Never claim Playwright testing happened unless Playwright MCP actually
   executed.** See `docs/playwright-strategy.md`.
3. **A phase is not `COMPLETED` until its quality gate passes.** See
   `factory/rules/quality-gates.md`.
4. **A feature is not done until the Definition of Done passes.** See
   `factory/rules/definition-of-done.md`.
5. **Respect the source-of-truth hierarchy.** See
   `factory/rules/source-of-truth.md`.
6. **Preserve user input.** Files under `input/` are read-only artefacts.
   Never edit, normalise, move or delete them. Extracted content goes to
   `docs/source-analysis.md` and `evidence/discovery/`.
7. **Persist state after every meaningful step.** The run must survive a
   context reset, a crash, or a new Claude session.
8. **Only generate what the project needs.** A web-only project gets no
   database agent, no API contract, no mobile testing.
9. **Never push to a remote or create a GitHub repository without explicit
   authorisation.** See `factory/rules/git-policy.md`.
10. **Never commit secrets.** Generated projects use `.env.example`, never
    `.env`.
11. **Fix, don't just report.** When testing finds a defect that is fixable
    inside the project, run the bug-fix loop rather than filing it and moving on.
12. **Do not stop for confirmation between normal engineering steps.** Stop only
    for the escalation triggers in `factory/rules/source-of-truth.md`.
13. **Every UI is responsive, in both orientations.** Web and native mobile
    alike, across the declared viewport matrix — portrait *and* landscape. A
    layout that breaks at a supported width or on rotation is a defect, not a
    backlog item, and responsiveness is never claimed from a single viewport.
    See `factory/rules/responsive-rules.md`.

---

## 5. Canonical vocabulary

Phase and feature status: `NOT_STARTED`, `IN_PROGRESS`, `BLOCKED`,
`READY_FOR_REVIEW`, `COMPLETED`, `FAILED`.

Test and verification status: `PASS`, `PARTIAL`, `FAIL`, `NOT_TESTED`,
`BLOCKED`, `NOT_APPLICABLE`.

Gate result: `PASS`, `FAIL`, `WAIVED` (waiver requires a recorded reason and an
owner). Full definitions: `factory/rules/status-vocabulary.md`.

---

## 6. Layout

```
.claude/agents/      Factory agents (orchestrator, discovery, agent-generator,
                     workflow-validator, project-state) + generated project agents
.claude/commands/    Slash commands
.claude/skills/      Reusable procedures invoked by agents
factory/templates/   Agent, document, manifest and feature templates
factory/schemas/     JSON Schemas for manifest, state, features, reports
factory/rules/       Gates, DoD, source of truth, selection matrix, policies
docs/                Factory documentation (PROJECT MODE also writes product docs here)
evidence/            Real artefacts produced by real work
examples/            Worked example inputs and expected manifests
input/               User-supplied description and references (read-only)
.project/            Generated: manifest + state (PROJECT MODE only, not committed
                     to the factory repo — see § 9)
scripts/             Bootstrap and validation helpers
```

---

## 7. Reading order for a new session

1. This file.
2. `AGENTS.md` — who does what.
3. `.project/project.json` and `.project/state/state.json` if they exist.
4. `docs/orchestration.md` — the phase machine.
5. `factory/rules/quality-gates.md`.

Do not begin work before step 3.

---

## 8. Delegation authorisation

The factory pipeline is agent-driven. `/start-project`, `/resume`, `/plan`,
`/test`, `/audit` and `/release` are **authorised and expected to use the Agent
tool** to dispatch the factory and project agents. Any general guidance against
delegation does not apply to these commands.

The Agent tool's roster is fixed when a session starts, so `project-*` agents
generated during `03-select-agents` cannot be dispatched in the session that
created them. The orchestrator adopts those roles inline instead — same scope,
outputs and evidence — and journals `inline_role_adoption`. This is never a
reason to pause the run or ask the user to restart Claude Code.

---

## 9. Two repositories

The factory and the products it builds are **separate repositories**.

| | Factory repo | Generated project repo |
|---|---|---|
| Contains | `.claude/agents/{orchestrator,discovery,agent-generator,workflow-validator,project-state}.md`, `.claude/commands/`, `.claude/skills/`, `factory/`, `examples/`, `scripts/`, factory `docs/`, `AGENTS.md`, `CLAUDE.md`, `README.md`, `.gitignore` | `input/`, generated `docs/`, `.project/`, `evidence/`, `.claude/agents/project-*.md`, `backend/`, `web/`, `mobile/`, `shared/` |
| Purpose | Reusable. Evolves independently of any product. | One product. |
| Remote | `ai-project-factory` | `my-project`, `crm-project`, … |

Everything in the right-hand column is ignored by the factory's `.gitignore`, so
`git add .` inside a factory clone stages factory files only. A generated project
is still fully present and resumable on disk — `.project/state/` is read from the
filesystem, not from git.

To take a finished project out of the factory and give it its own repository:

```bash
./scripts/extract-project.sh ../my-project
```

Never commit a generated product into the factory repo. If you are about to
`git add` a path from the right-hand column, stop — it belongs to the project.

---
