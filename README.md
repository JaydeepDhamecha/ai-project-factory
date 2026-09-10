# AI Software Development Factory

A reusable **Claude Code project factory**.

Give it a short project description and some reference material — PDFs,
screenshots, wireframes, specification documents — run one command, and it
takes the project from discovery through requirements, architecture,
implementation, real browser testing, bug fixing, regression, security and
performance review, to a production-readiness report.

It is **generic by construction**. Nothing in this repository is tied to a
particular product, client, domain or technology stack. The factory inspects
your material, decides what kind of project it is, and generates only the
agents, documents and tests that project actually needs.

---

## What this repository is

This repository is the **factory**, not an application. Out of the box it
contains no `backend/`, `web/` or `mobile/` directory — those are created only
if and when a project you start needs them.

```
.claude/     factory agents, slash commands, skills
factory/     templates, JSON schemas, rules and gates
docs/        how the factory works
evidence/    real artefacts from real runs
examples/    worked example inputs
input/       where you put your description and references
scripts/     bootstrap and validation helpers
```

---

## Prerequisites

| Requirement | Why | Notes |
|---|---|---|
| **Claude Code** | Runs the factory | Desktop, CLI, web or IDE extension |
| **Node.js 18+** | Playwright MCP, most web toolchains | `node --version` |
| **Git** | Version control for the generated project | `git --version` |
| **Playwright MCP** | Real browser testing | Configured in `.mcp.json`, see below |
| Python 3.10+ / JDK / Xcode / Android Studio | Only if your project needs them | The factory tells you if a prerequisite is missing |

Playwright MCP is **optional but strongly recommended**. Without it the factory
will still run, but every browser-level check is recorded as `BLOCKED` with the
reason — it will never pretend a browser test happened.

---

## Setup

```bash
git clone <your-fork-url> my-project
cd my-project

# optional: verify prerequisites and factory integrity
./scripts/check-prerequisites.sh
./scripts/validate-factory.sh
```

Then open the folder in Claude Code. The bundled `.mcp.json` registers the
Playwright MCP server; approve it when Claude Code prompts.

To confirm Playwright MCP is live, run `/test --probe` or ask Claude Code to
list its MCP tools — you should see `browser_navigate`, `browser_click`,
`browser_snapshot` and friends.

---

## Starting a project

### 1. Describe the project

```bash
cp factory/templates/project/project-description.template.md input/project-description.md
```

Edit it. A few honest paragraphs beat a long vague document. Say what the
product is, who uses it, what the main things they do are, and any technology
you require. Anything you do not know, leave out — the factory will ask or
record an assumption rather than invent a business rule.

### 2. Drop in your references

```
input/references/
  requirements.pdf
  dashboard-mockup.png
  mobile-flow.jpg
  api-spec.pdf
```

Supported: `.pdf`, `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`, `.md`, `.txt`,
`.csv`, `.docx` (text extraction), `.json`, `.yaml`.

These files are **read-only**. The factory never edits, renames or moves them.
Everything it learns from them is written to `docs/source-analysis.md` with a
citation back to the source file and page.

### 3. Run one command

```
/start-project
```

That is the whole user experience. You do not create agents. You do not pick a
stack unless you want to. You do not wire up tests.

---

## What `/start-project` does

```
DISCOVER → UNDERSTAND → PLAN → SELECT AGENTS → GENERATE STRUCTURE
   → IMPLEMENT → INTEGRATE → TEST → PLAYWRIGHT → FIX → RETEST
   → REGRESSION → SECURITY → PERFORMANCE → RELEASE
```

1. Reads your description and every reference file.
2. Extracts entities, screens, roles, workflows, rules and visual language.
3. Determines project type, platforms and capabilities.
4. Chooses a technology stack (or honours yours).
5. Writes `.project/project.json` — the machine-readable manifest.
6. Generates **only the agents this project needs**.
7. Generates **only the documents this project needs**.
8. Produces a dependency-ordered, feature-sliced development plan.
9. Implements feature by feature — each slice goes backend → API → web →
   mobile → integration → browser test → QA → regression before the next
   feature starts.
10. Runs real browser tests through Playwright MCP.
11. Fixes what it finds, retests, then regression-tests.
12. Reviews security and performance.
13. Produces a release readiness report with explicit statuses.

---

## How agents are generated

The factory does not ship 21 agents and hope. It ships 21 **templates** and a
selection matrix.

`discovery` produces a capability profile:

```json
{ "web": true, "backend": true, "database": true,
  "mobile": false, "auth": true, "offline": false }
```

`agent-generator` reads `factory/rules/agent-selection-matrix.md` and
instantiates only the matching templates into `.claude/agents/project-*.md`,
filling in the project's real stack, paths and commands.

- A **web-only** project gets no `database`, `backend` or `api` agent.
- A **web + backend + database** project additionally gets `integration`.
- A **mobile** project gets mobile testing requirements and, if offline was
  requested, an `offline-sync` agent.
- An **API-only** project gets no `designer`, `web` or `playwright` agent —
  contract tests replace browser tests.

Full detail: `docs/project-generation.md` and `docs/agent-system.md`.

---

## How testing works

Five layers, each applied only where it makes sense:

| Layer | Applies to | Evidence |
|---|---|---|
| Static (lint, types, build) | everything | `evidence/implementation/` |
| Unit | everything with code | `evidence/qa/` |
| Integration / contract | backend, API, multi-platform | `evidence/api/`, `evidence/implementation/` |
| Browser (Playwright MCP) | web, admin portal | `evidence/playwright/` |
| Mobile (simulator/emulator) | mobile | `evidence/qa/mobile/` |

Every failure enters the bug-fix loop:

```
TEST → FAIL → REPRODUCE → ROOT CAUSE → FIX → RETEST → REGRESSION
```

Release-blocking failures cannot be waived silently. See
`docs/testing-strategy.md`.

---

## How Playwright MCP is used

Browser testing is first-class, not an afterthought.

The generated `playwright` agent starts the app, discovers its routes, reads
the acceptance criteria, and drives the **real UI** — forms, navigation, CRUD,
validation, loading/empty/error states, authentication, authorisation and
responsive layouts — capturing screenshots and a structured result file for
every scenario.

Two rules are absolute:

1. A scenario is only `PASS` if Playwright MCP actually executed it.
2. If Playwright MCP is unavailable, every browser scenario is recorded as
   `BLOCKED` with the reason, and the release gate reflects that. No
   substitution, no inference from reading source code, no fabricated
   screenshots.

Full protocol: `docs/playwright-strategy.md`.

---

## How the project resumes

The factory is crash-safe and context-reset-safe.

```
.project/
  project.json          manifest: type, platforms, stack, agents, phase, status
  state/
    state.json          current phase, active agent, gate results
    features.json       per-feature slice status
    journal.ndjson      append-only event log
    blockers.json       open blockers with owners
    decisions.md        architectural decision record
    test-status.json    latest result per test layer
```

Start a new Claude Code session and run:

```
/resume
```

The orchestrator reads the state, reconstructs where it was, and continues from
the next incomplete step. It never restarts from zero, and never re-implements
a feature already marked `COMPLETED` with passing evidence.

`/status` gives you a read-only snapshot at any time.

---

## Git and GitHub

- The factory itself is safe to fork and share: no secrets, no machine-specific
  paths, no client data.
- Generated projects get sensible commits at feature boundaries and gate
  passes, with a conventional-commit message format.
- **The factory never pushes to a remote, creates a repository, or opens a pull
  request without your explicit instruction.**
- `.env` is always ignored; `.env.example` is always generated.
- Your `input/references/` are committed by default so future runs can re-read
  the source of truth. If they are confidential, uncomment the last line of
  `.gitignore`.

Policy: `factory/rules/git-policy.md`.

---

## Commands

| Command | Purpose |
|---|---|
| `/start-project` | Full lifecycle from your input to release readiness |
| `/status` | Where the project is right now (read-only) |
| `/resume` | Continue from persisted state |
| `/plan` | (Re)generate the development plan only |
| `/test` | Run applicable test layers, including Playwright MCP |
| `/audit` | Independent review of coverage, consistency and risk |
| `/release` | Evaluate release gates and produce the readiness report |

---

## Documentation

| Document | Contents |
|---|---|
| `docs/factory-architecture.md` | How the factory is put together |
| `docs/agent-system.md` | Agent contract, lifecycle, write scopes |
| `docs/orchestration.md` | The phase machine, in detail |
| `docs/project-state.md` | State model, resume algorithm, recovery |
| `docs/evidence-strategy.md` | What counts as evidence, and what does not |
| `docs/factory-testing-strategy.md` | Test layers and the bug-fix loop |
| `docs/playwright-strategy.md` | Browser testing protocol and honesty rules |
| `docs/project-generation.md` | How agents and documents get generated |
| `docs/reference/master-project-agent-prompt.md` | Original end-to-end lifecycle spec this factory implements |

---

## Design principles

1. **Generic by construction** — no product knowledge in the factory.
2. **Dynamic selection** — build only what the project needs.
3. **Evidence over assertion** — if it was not run, it did not pass.
4. **Vertical slices** — features complete end-to-end, not layer by layer.
5. **Resumable** — state survives crashes, resets and new sessions.
6. **Gated** — nothing is `COMPLETED` until its gate passes.
7. **Honest** — `NOT_TESTED` and `BLOCKED` never silently become `PASS`.

---

## Licence and contribution

Add your preferred licence before publishing. To extend the factory: add a
template under `factory/templates/agents/`, register it in
`factory/rules/agent-selection-matrix.md`, and run `./scripts/validate-factory.sh`.
