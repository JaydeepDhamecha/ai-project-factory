# AI Project Factory

Turn requirements, PDFs and screenshots into a working, tested application.

This repository is a **factory**, not an application. You give it source
material; it decides what kind of project that implies, generates the agents
and documents that project actually needs, builds it feature by feature, tests
it in a real browser, fixes what it finds, and reports honestly on what it
could and could not verify.

---

## Contents

- [Quick start](#quick-start)
- [Prerequisites](#prerequisites)
- [What a run costs](#what-a-run-costs)
- [What this repository is](#what-this-repository-is)
- [Commands](#commands)
- [The lifecycle](#the-lifecycle)
- [How agents are generated](#how-agents-are-generated)
- [How documents are generated](#how-documents-are-generated)
- [How the factory adapts to project size](#how-the-factory-adapts-to-project-size)
- [Quality gates](#quality-gates)
- [Status vocabulary](#status-vocabulary)
- [How testing works](#how-testing-works)
- [How Playwright MCP is used](#how-playwright-mcp-is-used)
- [Responsive and landscape support](#responsive-and-landscape-support)
- [How a run resumes](#how-a-run-resumes)
- [Two repositories](#two-repositories)
- [Repository layout](#repository-layout)
- [Rules reference](#rules-reference)
- [Documentation](#documentation)
- [Troubleshooting](#troubleshooting)
- [Extending the factory](#extending-the-factory)
- [Design principles](#design-principles)
- [Licence](#licence)

---

## Quick start

```bash
git clone https://github.com/JaydeepDhamecha/ai-project-factory.git
cd ai-project-factory
./scripts/new-project.sh ../my-project
```

That creates the project **next to** the factory, not inside it, with the whole
runtime installed:

```
Projects/
├── ai-project-factory/     the factory — stays clean, reusable
└── my-project/             your product — its own directory from turn one
    ├── input/
    ├── .claude/            agents, commands, skills
    ├── factory/            rules, schemas, templates (snapshot)
    └── CLAUDE.md
```

Put your material in the new directory:

```
my-project/input/
├── project-description.md      # optional
└── references/
    ├── requirements.pdf
    ├── design.png
    └── wireframe.pdf
```

Then one command:

```bash
cd ../my-project && claude
```
```
/start-project
```

That is the entire user experience. You do not create agents, pick a stack,
write a plan or wire up tests. Everything the run produces stays in
`my-project/` — there is no extraction step and no cleanup in the factory.

> Running `/start-project` inside the factory clone also works and builds the
> product in place; `scripts/extract-project.sh` then separates them. Both
> models are supported — see [Two repositories](#two-repositories).

**Input**

- PDFs, screenshots, wireframes, specs — anything that describes the product
- an optional short description

**Output**

- requirements, user stories, acceptance criteria — numbered and cited
- architecture, technology and API decisions
- backend, web and mobile — whichever the project actually needs
- tests at every applicable layer
- real browser evidence from Playwright MCP
- security and performance review
- a production-readiness report with explicit statuses

References alone are enough. A description is optional, and the factory will
never invent business rules to fill a gap — it records them as `UNKNOWN` and
tells you.

---

## Prerequisites

| Requirement | Why | Check |
|---|---|---|
| **Claude Code** | Runs the factory | Desktop, CLI, web or IDE extension |
| **Node.js 18+** | Playwright MCP, most web toolchains | `node --version` |
| **Git** | Version control for the generated project | `git --version` |
| **Playwright MCP** | Real browser testing | Bundled in `.mcp.json` |
| Python / JDK / Xcode / Android Studio | Only if your project needs them | The factory tells you what is missing |

### Playwright MCP

The repository ships a working MCP registration — no setup beyond having
Node.js:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@0.0.82"],
      "env": {}
    }
  }
}
```

Claude Code picks this up automatically when you start it in the repository
root. The version is **pinned deliberately**: a factory that claims reproducible
evidence cannot float its browser driver on `@latest`. Bump it when you have
re-run `/test` against the new version, not before. Playwright MCP is optional but strongly recommended: without it the
factory still runs, but every browser-level check is recorded as `BLOCKED` with
the reason, `GATE-PW` fails, and release readiness cannot reach `READY`. It
will never pretend a browser test happened.

### Sanity checks

```bash
./scripts/check-prerequisites.sh    # what is installed, what is missing
./scripts/validate-factory.sh       # structural self-check of the factory
```

`validate-factory.sh` runs 182 checks across templates, schemas, rules, gate
coverage, agent contracts, placeholders and honesty invariants. It should
report **0 errors, 0 warnings** on a clean clone.

---

## What a run costs

The factory is driven by a language model, so a run costs tokens. This section
says what is measured, what is estimated, and what you can do about it. Nothing
here is a quote — your cost depends on your project.

### The repository itself is cheap

Measured on a fresh clone:

| | Tokens |
|---|---|
| `CLAUDE.md` | 2,059 |
| `AGENTS.md` | 1,550 |
| Agent roster (5 factory agents) | 311 |
| **Loaded on every turn** | **~3,900** |
| Every tracked file, if you read all of them | ~121,000 |

The whole repo is 2 MB. Cloning it and opening Claude Code costs you almost
nothing. **The repository is not where your tokens go.**

### The run is where they go

Measured on one completed reference project — a three-platform product with 28
documents, 2,498 source files and 2,676 evidence artefacts:

| What the run *wrote* | Tokens |
|---|---|
| Evidence | ~6,784,000 |
| Documents | ~258,000 |

Those are **output** tokens. Real spend is higher, because every agent reads
context before it writes.

**Read that number as a ceiling, not a forecast.** It is one large project, and
it was produced *before* the evidence fix described below. A login page is not
that project.

### Where the waste was, and what changed

Two findings from measuring that run:

1. **Evidence was 96% of everything written, and almost none of it was read
   back.** One artefact was 953,513 tokens — 73,748 lines, of which 2,472 were
   unique. It was a single root cause repeated 603 times. Across the 40 largest
   artefacts, **81.7% of lines were duplicates.**

   Cause: the evidence recipe piped command output through `tee`, which writes
   to the file *and* to the agent's context. Fixed. Logs are now written in
   full to disk and read as a bounded slice; counts, exit codes and distinct
   failures go into the directory index. Nothing is discarded — the raw file
   stays on disk permanently and `/audit` still reads it.

2. **The fix → retest → regression loop was 81% of all activity** (646 of 798
   journal events). That loop is driven by how many defects your project has,
   not by how big it is.

### What this means for your project

- **A small project is cheaper mainly because it has fewer defects**, not
  because it has fewer phases. All fifteen phases always run.
- **The single biggest cost driver you control is how clearly you specify the
  project.** Vague input produces defects, and defects drive the loop that
  dominates the bill.
- `factory/rules/scale-rules.md` merges phases into fewer dispatches for small
  projects. It is honest that this is the smaller lever.

### Keeping a run cheap

1. **Be specific in `input/`.** Every ambiguity becomes a `UNKNOWN`, a wrong
   guess, or a defect. Screens, roles, rules and validations stated plainly are
   the cheapest tokens you will ever spend.
2. **Say what you do not need.** "No mobile app", "no database", "no offline"
   each switch off a capability, and with it an agent, a document and a gate.
3. **Keep references readable.** A blurry screenshot costs more than no
   screenshot, because it gets analysed and then queried.
4. **Use `/status` rather than re-asking.** It is a read-only snapshot and
   costs a fraction of re-deriving the state.
5. **Resume, never restart.** `/resume` reads the persisted state;
   starting again re-runs work you have already paid for.
6. **Let it finish a phase.** Interrupting mid-phase usually means the work is
   redone.

### What is not yet measured

The evidence fix is verified **structurally** — schemas, rules and gates are
consistent, and `validate-factory.sh` reports 182 checks, 0 errors. Its effect
on a real run has **not** been measured yet, because that needs a full
end-to-end run to compare against the figures above. When someone runs one, the
comparison belongs here. Until then, treat the saving as a projection from the
measured redundancy, not a result.

---

## What this repository is

Out of the box this repository contains no `backend/`, `web/` or `mobile/`
directory — those are created only if a project you start needs them.

Nothing here is tied to a product, client, domain or stack. The prime directive
is in `CLAUDE.md`:

> **Build the factory's output, never the factory's assumptions.**

If a business entity name — a customer, a product, a domain noun — ever appears
in a file under `factory/`, `.claude/` or the factory's `docs/`, that is a bug.
Product-specific artefacts are *generated* into a project workspace at run time.

### Two modes

Claude Code operates in exactly one of two modes in this repository:

| Mode | Trigger | Behaviour |
|---|---|---|
| **FACTORY MODE** | `.project/project.json` does not exist | Maintaining the factory. Only `.claude/`, `factory/`, `docs/`, `scripts/`, `examples/` and root files are touched. |
| **PROJECT MODE** | `.project/project.json` exists | Building your product. The manifest and state files are authoritative; a run resumes rather than restarting. |

```bash
test -f .project/project.json && echo PROJECT_MODE || echo FACTORY_MODE
```

---

## Commands

| Command | Purpose |
|---|---|
| `/start-project` | **The** entry point. Runs the entire lifecycle autonomously. |
| `/status` | Where the project is right now — phase, gates, tests, blockers. Read-only. |
| `/resume` | Continue an interrupted run from persisted state. Never restarts from zero. |
| `/plan` | (Re)generate or revise the development plan without implementing. |
| `/test` | Run the applicable test layers, including Playwright MCP. |
| `/audit` | Independent review: requirements coverage, consistency, security, gaps. |
| `/release` | Final gate evaluation and release-readiness report. |

---

## The lifecycle

Fifteen phases, `00` to `14`, each with a gate that must pass before the run
advances.

```
DISCOVER → UNDERSTAND → PLAN → SELECT AGENTS → GENERATE STRUCTURE
   → IMPLEMENT → INTEGRATE → TEST → PLAYWRIGHT → FIX → RETEST
   → REGRESSION → SECURITY → PERFORMANCE → RELEASE
```

| # | Phase | What happens | Gate |
|---|---|---|---|
| 00 | `00-discover` | Read every input file; extract entities, screens, roles, rules, visual language; derive the capability profile | — |
| 01 | `01-understand` | Product definition, PRD, numbered and cited requirements, user stories, acceptance criteria | `GATE-REQ` |
| 02 | `02-plan` | Technology, architecture, data model, API contract, design system, dependency-ordered feature slices | `GATE-ARCH` |
| 03 | `03-select-agents` | Instantiate only the agents this project needs | — |
| 04 | `04-generate-structure` | Create documents and platform directories | `GATE-ARCH` re-check |
| 05 | `05-implement` | Build the current feature slice | `GATE-IMPL` per feature |
| 06 | `06-integrate` | Join the slice's surfaces; verify contract conformance | `GATE-INTG` per feature |
| 07 | `07-test` | Static, unit, integration, contract | `GATE-TEST` |
| 08 | `08-playwright` | Real browser validation | `GATE-PW` |
| 09 | `09-fix` | Reproduce, root-cause, fix, add regression tests | — |
| 10 | `10-retest` | Re-run what failed | `GATE-TEST` + `GATE-PW` |
| 11 | `11-regression` | Full suite across every completed feature | `GATE-REG` |
| 12 | `12-security` | Threat review, authorisation tests, dependency audit | `GATE-SEC` |
| 13 | `13-performance` | Measure against budgets | `GATE-PERF` |
| 14 | `14-release` | Final evaluation and readiness report | `GATE-REL` |

**All fifteen phases run on every project, and every gate is evaluated.** What
varies with project size is how many *agent dispatches* those phases take: on a
small project several adjacent phases share one invocation, which saves the
repeated context re-reads between them. `discovery` decides the size from cited
counts and defaults to the full pipeline whenever the inputs are thin. Nothing is
skipped for being small — see `factory/rules/scale-rules.md`, which is also
candid that this is the smaller of the two levers on cost.

Features are built as **vertical slices**: each one goes backend → API → web →
mobile → integration → browser test → QA → regression before the next feature
starts. Not layer by layer.

Detail: `docs/orchestration.md`.

---

## How agents are generated

The factory does not ship 22 agents and hope. It ships 22 **templates** and a
selection matrix.

`discovery` produces a capability profile:

```json
{ "web": true, "backend": true, "database": true,
  "mobile": false, "auth": true, "offline": false }
```

`agent-generator` reads `factory/rules/agent-selection-matrix.md` and
instantiates only the matching templates into `.claude/agents/project-*.md`,
substituting the project's real stack, paths, commands and viewports.

- A **web-only** project gets no `database`, `backend` or `api` agent.
- A **web + backend + database** project additionally gets `integration`.
- A **mobile** project gets mobile testing requirements and, if offline was
  requested, an `offline-sync` agent.
- An **API-only** project gets no `designer`, `web` or `playwright` agent —
  contract tests replace browser tests.

Some capability flags are **derived**, never asked for:

```
api            = backend AND (web OR mobile OR desktop OR adminPortal OR apiOnly)
browserTesting = web OR adminPortal
responsive     = web OR adminPortal OR mobile OR desktop
integration    = count(backend, web, mobile, desktop, adminPortal) >= 2
```

### The five factory agents

These are permanent and live in the repository:

| Agent | Role |
|---|---|
| `orchestrator` | Owns the phase machine, sequences agents, enforces gates, drives the bug-fix loop |
| `discovery` | Reads inputs, produces findings and the capability profile |
| `agent-generator` | Instantiates project agents and documents from templates |
| `workflow-validator` | Structural self-check of the factory and of generated projects |
| `project-state` | Sole writer of `.project/state/` — checkpoints, journal, resume, integrity repair |

> `project-state.md` is a **factory** agent despite its `project-` prefix. The
> `.gitignore` carries an explicit exception for it. The naming collision is
> historical; do not "fix" it by renaming without updating both.

Full detail: `docs/project-generation.md`, `docs/agent-system.md`.

---

## How documents are generated

19 document templates live in `factory/templates/docs/`. The applicable set is
chosen the same way agents are — a project without a database gets no
`database-schema.md`, and the skip is recorded with its reason.

| Template | Generated when |
|---|---|
| `project-overview`, `PRD`, `requirements`, `user-stories`, `acceptance-criteria` | always |
| `source-analysis`, `assumptions` | always |
| `technology-stack`, `architecture`, `platform-requirements`, `development-plan`, `development-status` | always |
| `api-contract` | `api` |
| `database-schema` | `database` |
| `design-system` | `web` or `mobile` |
| `offline-sync` | `offline` |
| `testing-strategy`, `security`, `deployment` | always / `deployable` |

Every generated document lands in `docs/`, alongside the factory's own
documentation. The `.gitignore` knows which is which.

---

## How the factory adapts to project size

A login page and a multi-tenant ERP are not the same amount of work. Two
mechanisms make the run fit the project, and both are automatic — you still type
only `/start-project`.

### 1. Capability-based selection

`discovery` extracts a capability profile with cited counts, and
`factory/rules/agent-selection-matrix.md` turns it into a roster. An agent whose
condition is false is **never generated**, and the rejection is recorded in
`evidence/discovery/agent-selection.md` so you can check the factory did not
simply forget.

A web-only project gets no database agent, no API contract and no integration
phase. An API-only project gets no designer and no Playwright agent, and
`GATE-PW` is recorded `NOT_APPLICABLE` — explicitly, never silently dropped.

### 2. Scale

`factory/rules/scale-rules.md` classifies the project `micro`, `small` or
`standard` from six cited counts, and that decides **how many dispatches a phase
takes**:

| Scale | Passes | Typical project |
|---|---|---|
| `micro` | 7 | A sign-in flow. ≤2 entities, ≤3 screens, 1 role, 1 platform |
| `small` | 10 | ≤8 entities, ≤12 screens, ≤3 roles, ≤2 platforms |
| `standard` | 15 | Everything else, and anything touching payments, tenancy, offline or realtime |

**All fifteen phases run at every scale, and every gate is always evaluated.**
Merging changes how often agents are invoked, not what is checked. A phase is
`NOT_APPLICABLE` only when a capability flag says the project has no such
surface — never because a pass was merged.

A project is `standard` unless every smaller condition is *affirmatively*
satisfied by a cited count. Sizing down to make a run cheaper is explicitly
forbidden: a mis-sized project hands phases to a pass that was not dimensioned
for them, and the gate that gets lost is the last one in the pass.

Two clients, one contract — a web and a mobile client rendering the same `/auth`
endpoints, with no offline or realtime — may run at `small`. Two genuinely
divergent clients may not.

### Be honest about what this saves

Measured on a completed reference run of 798 journal events:

| Band | Share |
|---|---|
| Fix → retest → regression | **81%** |
| Phases 00–04, which `micro` collapses into one pass | 3.3% |

So collapsing phases is the **smaller lever, by a wide margin**. A project that
finds twelve bugs costs twelve bug-fix loops at every scale. What actually drives
a bill is how many defects your project has — which is mostly a function of how
clearly you specified it.

### Task packets — the lever that is on the hot band

Phases 05–10 repeat per feature, per platform, and again per fix cycle. Each
per-feature agent used to open five or six whole documents to implement one
slice, because `features.json` gives it requirement **ids**, and an id can only
be resolved by reading all of `docs/requirements.md`.

`planner` now writes one **task packet** per feature —
`.project/tasks/<featureId>.json` — resolving those ids to text once, at plan
time, when the whole document set is already in context:

```json
{
  "featureId": "FEAT-002",
  "platforms": ["web", "mobile"],
  "requirements": [
    {"id": "REQ-014", "text": "Passwords must be at least 12 characters.",
     "citation": "spec.pdf p.4", "confidence": "HIGH"}
  ],
  "acceptanceCriteria": [
    {"id": "AC-031", "text": "An 11-character password is rejected inline."}
  ],
  "api": [{"method": "POST", "path": "/auth/register"}],
  "notIncluded": ["Rate-limiting policy — see docs/security.md §3"],
  "generatedFrom": {"documents": [{"path": "docs/requirements.md", "sha256": "…"}]}
}
```

Four properties keep this honest, and `workflow-validator` enforces all of them:

- **Derived, never authoritative.** Where a packet disagrees with the document
  it cites, the document wins. Opening the full document is never wrong — it is
  simply no longer the default.
- **Text is copied, never paraphrased.** Summarising a requirement into a packet
  is the failure this mechanism exists to prevent.
- **`notIncluded` is mandatory.** The packet says what it leaves out, so an agent
  knows when to go read the real document instead of assuming completeness.
- **Provenance is hashed.** When a source document changes, packets resolved
  from the old hash are stale and must be regenerated — a stale packet is a
  defect, not a nuisance.

Full rule: `factory/rules/task-packets.md`.

---

## Quality gates

Ten gates. A phase is not `COMPLETED` until its gate passes.

| Gate | Phase | Covers |
|---|---|---|
| `GATE-REQ` | 01 | Requirements numbered, cited, testable; acceptance criteria present |
| `GATE-ARCH` | 02, 04 | Architecture, stack, platform requirements, schema, API contract, design system |
| `GATE-IMPL` | 05 | Code for every criterion, lint/types/build/unit pass, no mocks on production paths |
| `GATE-INTG` | 06 | End-to-end flow across platforms, auth lifecycle, error propagation |
| `GATE-TEST` | 07, 10 | Test layers executed, coverage of acceptance criteria, no green-by-avoidance |
| `GATE-PW` | 08, 10 | Real browser validation — never waived by an agent |
| `GATE-SEC` | 12 | Authentication, authorisation, injection, exposure, dependencies, configuration |
| `GATE-PERF` | 13 | Measured against stated budgets |
| `GATE-REG` | 11 | Everything previously working still works |
| `GATE-REL` | 14 | All prior gates, zero open `CRITICAL`/`HIGH`, evidence for every claim |

Criteria are `MANDATORY`, `CONDITIONAL (flag)` or `NOT_APPLICABLE`. A gate
result is `PASS`, `FAIL` or `WAIVED` — and a waiver requires a recorded reason
and a named owner.

Full criteria: `factory/rules/quality-gates.md`.

---

## Status vocabulary

The factory uses two closed vocabularies. They are not interchangeable.

**Phase and feature status**
`NOT_STARTED` · `IN_PROGRESS` · `BLOCKED` · `READY_FOR_REVIEW` · `COMPLETED` · `FAILED`

**Test and verification status**
`PASS` · `PARTIAL` · `FAIL` · `NOT_TESTED` · `BLOCKED` · `NOT_APPLICABLE`

The rule that makes the rest of it trustworthy:

> **`NOT_TESTED` and `BLOCKED` never become `PASS`.**

A status changes only because reality changed and was observed — never because
a record was rewritten. Definitions: `factory/rules/status-vocabulary.md`.

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

The factory **fixes rather than reports**: when testing finds a defect that is
fixable inside the project, it runs the loop rather than filing it and moving
on. Release-blocking failures cannot be waived silently.

Procedure: `.claude/skills/bug-fix-loop/SKILL.md`, `docs/factory-testing-strategy.md`.

---

## How Playwright MCP is used

Browser testing is first-class, not an afterthought.

The generated `playwright` agent starts the app, discovers its routes from the
running application, reads the acceptance criteria, and drives the **real UI** —
forms, navigation, CRUD, validation, loading/empty/error states, authentication,
authorisation, resilience and responsive layouts — capturing a screenshot and a
structured result for every scenario.

Two rules are absolute:

1. A scenario is only `PASS` if Playwright MCP actually executed it.
2. If Playwright MCP is unavailable, every browser scenario is recorded as
   `BLOCKED` with the reason, and the release gate reflects that. No
   substitution, no inference from reading source code, no fabricated
   screenshots.

Full protocol: `docs/playwright-strategy.md`,
`.claude/skills/playwright-mcp/SKILL.md`.

---

## Responsive and landscape support

Every UI the factory produces — web **and** native mobile — must work across
the device classes it claims to support, in **both portrait and landscape**.

Responsiveness is treated as a correctness property, like validating a form or
handling a 500. A layout that breaks at 390 px or on rotation is a **defect**,
not a backlog item, and `responsive` is a derived flag: it is not a scope
question you get asked.

The default tested matrix:

| Class | Portrait | Landscape |
|---|---|---|
| Small phone | 360 × 740 | 740 × 360 |
| Large phone | 414 × 896 | 896 × 414 |
| Tablet | 768 × 1024 | 1024 × 768 |
| Laptop | 1280 × 800 | — |
| Desktop | 1440 × 900 | — |

What is enforced, in summary:

- no horizontal page scroll at any supported width — **measured**, not eyeballed
- mobile-first base styles; no fixed-width layout container
- navigation that collapses *and actually opens, operates and closes*
- every data table with a declared strategy: scroll container, column priority,
  or stacked cards
- modals that fit and keep their primary action reachable in short landscape
- touch targets ≥ 44 × 44 px; user scaling never disabled
- safe-area insets on all four edges — landscape insets are left and right
- **rotation preserves state**: form input, scroll position, open modals, list
  selection — verified mid-interaction, not on an empty screen

Evidence is a matrix, not a claim: `evidence/playwright/responsive-matrix.md`
carries one cell per screen × viewport × orientation, each backed by a
screenshot. A cell is never inferred from a neighbouring one — 768 px passing
says nothing about 360 px, and portrait passing says nothing about landscape.

Gated by `ARCH-6a`, `IMPL-9a`, `IMPL-9b` and `PW-11` through `PW-11e`.
Full rule: `factory/rules/responsive-rules.md`.

---

## How a run resumes

The factory is crash-safe and context-reset-safe.

```
.project/
  project.json          manifest: type, platforms, stack, agents, viewports, phase
  state/
    state.json          current phase, active agent, gate results
    features.json       per-feature slice status
    journal.ndjson      append-only event log
    blockers.json       open blockers with owners
    decisions.md        architectural decision record
    test-status.json    latest result per test layer
    checkpoints/        point-in-time snapshots
```

Start a new Claude Code session and run:

```
/resume
```

The orchestrator reads the state, reconstructs where it was, and continues from
the next incomplete step. It never restarts from zero, and never re-implements a
feature already marked `COMPLETED` with passing evidence.

`/status` gives you a read-only snapshot at any time.

> `.project/state/` has a single writer — the `project-state` agent. Other
> agents request state changes; they do not write them. This is what keeps the
> journal trustworthy under concurrency.

Detail: `docs/project-state.md`.

---

## Two repositories

The factory and the products it builds are **separate repositories**, so the
factory can evolve without being mixed up with any one project.

| | Factory repo | Generated project repo |
|---|---|---|
| Contains | `.claude/agents/{orchestrator,discovery,agent-generator,workflow-validator,project-state}.md`, `.claude/commands/`, `.claude/skills/`, `factory/`, `examples/`, `scripts/`, factory `docs/`, `AGENTS.md`, `CLAUDE.md`, `README.md`, `.gitignore` | `input/`, generated `docs/`, `.project/`, `evidence/`, `.claude/agents/project-*.md`, `backend/`, `web/`, `mobile/`, `shared/` |
| Purpose | Reusable. Evolves independently of any product. | One product. |
| Remote | `ai-project-factory` | `my-project`, `crm-project`, … |

There are two ways to get there.

### Workspace — recommended

```bash
./scripts/new-project.sh ../my-project
```

Installs the runtime (5 factory agents, commands, skills, `factory/`,
`AGENTS.md`, a pinned `.mcp.json`) into a new directory and marks it with
`.project/workspace.json`. Total size: about 550 KB.

The product is separate from the first turn. The factory clone is never written
to. The project has its own `/start-project`, `/resume`, `/status`, `/test`,
`/audit` and `/release`. **No extraction step exists.**

The copied `factory/` is a deliberate snapshot: a project keeps the rules it was
born with, so a run stays reproducible while the factory evolves. The corollary
is that a *factory* fix made inside a workspace is lost — make those upstream.

### In place — legacy, still supported

`/start-project` inside a factory clone generates the product into that working
tree. `.gitignore` excludes every generated path, so `git add .` stages factory
files only, and the project is still fully present and resumable on disk —
`.project/state/` is read from the filesystem, not from git.

When such a project is ready to live on its own:

```bash
./scripts/extract-project.sh ../my-project
cd ../my-project
git remote add origin <your-project-remote>
git push -u origin main
```

That **copies** — never moves — the manifest, state, inputs, evidence, generated
documents, project agents and source trees into a new git repository, excluding
dependency trees, build output, caches and every `.env` variant (`.env.example`
travels; a `.env.backup` does not). A belt-and-braces secret sweep runs over the
extracted tree before `git init`.

**Your source material is not published by default.** `input/references/` is
copied to disk — so `/resume` and `/audit` can still read it — but excluded from
the project's `.gitignore`. What gets committed instead is
`.project/source-manifest.json`: the name, size and SHA-256 of each reference,
enough to prove which sources the project was built from without distributing a
client's PDF. Pass `--include-inputs` to commit the originals.

> The extracted folder is a **hand-off artefact, not a second workspace.** It
> deliberately contains no `factory/`, no `.claude/commands/` and no
> `.claude/skills/`, so `/resume` and `/test` do not exist there. Finish the run
> in the factory clone, then extract.

Two rules the factory will not break:

- **It never pushes to a remote, creates a repository or opens a pull request
  without your explicit instruction.**
- `.env` is never committed; `.env.example` always is.

Policy: `factory/rules/git-policy.md`.

---

## Repository layout

```
.claude/
  agents/          5 factory agents (+ generated project-*.md at run time)
  commands/        7 slash commands
  skills/          4 reusable procedures
factory/
  templates/
    agents/        22 agent templates + _TEMPLATE.md
    docs/          19 document templates
    project/       seed manifest
  schemas/         6 JSON Schemas — manifest, state, features, journal, defect, test report
  rules/           10 rules — gates, DoD, source of truth, selection matrix, responsive, policies
docs/              factory documentation (PROJECT MODE also writes product docs here)
evidence/          real artefacts produced by real work
examples/          worked example inputs and expected manifests
input/             your description and references — read-only to the factory
scripts/           bootstrap, validation and extraction helpers
.project/          generated: manifest + state (PROJECT MODE only, not committed)
```

### Scripts

| Script | Purpose |
|---|---|
| `check-prerequisites.sh` | Report what is installed and what a run would need |
| `validate-factory.sh` | 182-check structural self-check; must be 0 errors before a commit |
| `new-project.sh` | Create a project workspace outside the factory with the runtime installed — the recommended way to start |
| `extract-project.sh` | Lift an *in-place* project out of the factory into its own directory and git repository (`--include-inputs` to publish the source references too) |

---

## Rules reference

Everything normative lives in `factory/rules/`. Agents cite these rather than
restating them.

| Rule | Defines |
|---|---|
| `quality-gates.md` | The ten gates and every criterion |
| `definition-of-done.md` | When a feature is actually finished |
| `source-of-truth.md` | Precedence between inputs, documents and code; escalation triggers |
| `status-vocabulary.md` | The closed status vocabularies and their transitions |
| `agent-selection-matrix.md` | Which agents exist for which capabilities |
| `agent-authoring-rules.md` | Agent contract, required sections, placeholder table |
| `responsive-rules.md` | Viewport matrix, layout rules, orientation rules, severities |
| `evidence-rules.md` | What counts as evidence, how it is named and indexed |
| `naming-conventions.md` | File, feature, defect and artefact naming |
| `git-policy.md` | Commits, branches, remotes, secrets, authorisation |
| `scale-rules.md` | How project size is classified, and how many dispatches each size takes |
| `task-packets.md` | The bounded reading contract on the per-feature loop |

### Non-negotiable rules

Set out in full in `CLAUDE.md`. In brief:

1. Never fabricate evidence — if it did not run, it did not pass.
2. Never claim Playwright testing that Playwright MCP did not execute.
3. A phase is not `COMPLETED` until its gate passes.
4. A feature is not done until the Definition of Done passes.
5. Respect the source-of-truth hierarchy.
6. `input/` is read-only. Never edit, normalise, move or delete it.
7. Persist state after every meaningful step.
8. Only generate what the project needs.
9. Never push or create a repository without explicit authorisation.
10. Never commit secrets.
11. Fix, don't just report.
12. Do not stop for confirmation between normal engineering steps.
13. Every UI is responsive, in both orientations.

---

## Documentation

| Document | Contents |
|---|---|
| `CLAUDE.md` | Operating rules for Claude Code in this repository — read first |
| `AGENTS.md` | Who does what |
| `docs/factory-architecture.md` | How the factory is put together |
| `docs/agent-system.md` | Agent contract, lifecycle, write scopes |
| `docs/orchestration.md` | The phase machine, in detail |
| `docs/project-generation.md` | How agents and documents get generated |
| `docs/project-state.md` | State model, resume algorithm, recovery |
| `docs/evidence-strategy.md` | What counts as evidence, and what does not |
| `docs/factory-testing-strategy.md` | Test layers and the bug-fix loop |
| `docs/playwright-strategy.md` | Browser testing protocol and honesty rules |
| `docs/reference/master-project-agent-prompt.md` | The end-to-end lifecycle spec this factory implements |

---

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `/start-project` says a project already exists | `.project/project.json` is present — you are in PROJECT MODE. Use `/resume` or `/status`. |
| Every browser scenario is `BLOCKED` | Playwright MCP did not start. Check `evidence/playwright/mcp-availability.md`, confirm Node.js 18+, restart Claude Code so `.mcp.json` is picked up. |
| `GATE-PW` is `FAIL` and will not move | By design — it is never waived by an agent. Fix the defects or record an explicit user waiver with an owner. |
| A `project-*` agent cannot be dispatched | The Agent roster is fixed when a session starts, so agents generated during `03-select-agents` are not dispatchable in that session. The orchestrator adopts the role inline and journals `inline_role_adoption`. Not a reason to restart. |
| `git add .` stages generated product files | It should not — check `.gitignore` is intact and run `./scripts/validate-factory.sh` §15. |
| `extract-project.sh` refuses | The target exists and is not empty, or it is inside the factory. Extract to an empty sibling directory. |
| A run seems to have lost its place | `/resume` reconstructs from `.project/state/`. If the journal is damaged, `project-state` runs integrity repair and records what it found. |
| `validate-factory.sh` reports errors after your edit | Read the section number it names — the check tells you which template, schema, placeholder or cross-reference broke. |

---

## Extending the factory

To add an agent:

1. Add a template under `factory/templates/agents/`, following
   `factory/templates/agents/_TEMPLATE.md` — nine required sections, a write
   scope and a gate reference.
2. Register it in `factory/rules/agent-selection-matrix.md` §2 with its
   capability condition.
3. Document any new placeholder in `factory/rules/agent-authoring-rules.md` §4.
4. Run `./scripts/validate-factory.sh` — it must report 0 errors.

To add a rule, put it in `factory/rules/`, register it in the rules loop in
`scripts/validate-factory.sh` §5, and cite it from the agents it binds.

Keep the prime directive: no product, client, domain or stack knowledge enters
the factory.

---

## Design principles

1. **Generic by construction** — no product knowledge in the factory.
2. **Dynamic selection** — build only what the project needs.
3. **Evidence over assertion** — if it was not run, it did not pass.
4. **Vertical slices** — features complete end-to-end, not layer by layer.
5. **Resumable** — state survives crashes, resets and new sessions.
6. **Gated** — nothing is `COMPLETED` until its gate passes.
7. **Honest** — `NOT_TESTED` and `BLOCKED` never silently become `PASS`.
8. **Fix, don't report** — a found defect goes through the bug-fix loop.

---

## Licence

MIT — see [`LICENSE`](LICENSE). Fork it, use it commercially, build products
with it. The projects it generates are yours and carry no licence from this
repository.
