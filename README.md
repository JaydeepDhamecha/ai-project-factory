# AI Project Factory

Turn requirements, PDFs and screenshots into a working application.

---

## Usage

```bash
git clone https://github.com/YOUR-ORG/ai-project-factory.git
cd ai-project-factory
claude
```

Put your material here:

```
input/
├── project-description.md      # optional
└── references/
    ├── requirements.pdf
    ├── design.png
    └── wireframe.pdf
```

Then run one command:

```
/start-project
```

That is the entire user experience. You do not create agents, pick a stack,
write a plan or wire up tests.

**Input**

- PDFs, screenshots, wireframes, specs
- an optional short description

**Output**

- requirements, user stories, acceptance criteria
- architecture and technology decisions
- backend, web and mobile — whichever the project actually needs
- tests at every applicable layer
- real browser testing evidence from Playwright MCP
- security and performance review
- a production-readiness report with honest statuses

References alone are enough. A description is optional, and the factory will
never invent business rules to fill a gap — it records them as `UNKNOWN` and
tells you.

---

## Prerequisites

| Requirement | Why | Notes |
|---|---|---|
| **Claude Code** | Runs the factory | Desktop, CLI, web or IDE extension |
| **Node.js 18+** | Playwright MCP, most web toolchains | `node --version` |
| **Git** | Version control for the generated project | `git --version` |
| **Playwright MCP** | Real browser testing | Registered in the bundled `.mcp.json` |
| Python / JDK / Xcode / Android Studio | Only if your project needs them | The factory tells you what is missing |

Playwright MCP is optional but strongly recommended. Without it the factory
still runs, but every browser-level check is recorded as `BLOCKED` with the
reason — it will never pretend a browser test happened.

Optional sanity checks before you start:

```bash
./scripts/check-prerequisites.sh
./scripts/validate-factory.sh
```

---

## What this repository is

This repository is the **factory**, not an application. Out of the box it
contains no `backend/`, `web/` or `mobile/` directory — those are created only
if a project you start needs them.

```
.claude/     factory agents, slash commands, skills
factory/     templates, JSON schemas, rules and gates
docs/        how the factory works
examples/    worked example inputs
input/       where you put your description and references
scripts/     bootstrap, validation and extraction helpers
```

Nothing here is tied to a product, client, domain or stack. The factory inspects
your material, decides what kind of project it is, and generates only the agents,
documents and tests that project actually needs.

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

## Two repositories

The factory and the products it builds are **separate repositories**, so the
factory can evolve without being mixed up with any one project.

```
GitHub
├── ai-project-factory     this repository — reusable
├── my-project             a generated project
├── crm-project            another generated project
└── ecommerce-project      another generated project
```

Generation happens in place inside your factory clone, but `.gitignore` excludes
every generated path — `.project/`, `evidence/`, `input/references/`, generated
`docs/`, `.claude/agents/project-*.md`, `backend/`, `web/`, `mobile/`. So
`git add .` in a factory clone stages factory files only. Your project is still
fully present and resumable on disk; `.project/state/` is read from the
filesystem, not from git.

When a project is ready to live on its own:

```bash
./scripts/extract-project.sh ../my-project
cd ../my-project
git remote add origin <your-project-remote>
git push -u origin main
```

That copies — never moves — the manifest, state, inputs, evidence, generated
documents, project agents and source trees into a new git repository, excluding
dependency trees, build output, caches and `.env`.

Two rules the factory will not break:

- **It never pushes to a remote, creates a repository or opens a pull request
  without your explicit instruction.**
- `.env` is never committed; `.env.example` always is.

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
