# CLAUDE.md — {{PROJECT_NAME}}

This directory is a **project workspace** created by the AI Software
Development Factory. It builds exactly one product: **{{PROJECT_NAME}}**.

| | |
|---|---|
| Created | {{CREATED_AT}} |
| Factory version | {{FACTORY_VERSION}} |

---

## 1. Mode — there is only one

A session opened here is **always in PROJECT MODE**, before and after
`.project/project.json` exists. `.project/workspace.json` marks this directory
as a workspace; its presence is the mode.

You are building the product. You are **not** maintaining the factory.

`factory/` and `.claude/` here are a **snapshot** of the factory as it was at
{{CREATED_AT}}, taken so this project stays reproducible while the factory moves
on. Fix a product bug here. Do **not** fix a factory bug here — it would be
silently lost the next time a project is scaffolded. Factory improvements belong
in the factory repository.

---

## 2. Prime directive

> **Build {{PROJECT_NAME}}. Record what is true.**

The factory's rule against naming a product in a factory file does not apply in
this directory. This directory *is* the product. Name it freely in source,
documents and evidence.

---

## 3. Entry points

| Command | Purpose |
|---|---|
| `/start-project` | Run the lifecycle: discover → understand → plan → generate → implement → test → fix → regression → security → performance → release. Resumes automatically if a run exists. |
| `/status` | Current phase, feature, gates, tests, blockers. Read-only. |
| `/resume` | Continue an interrupted run from `.project/state/`. |
| `/plan` | Regenerate the development plan without implementing. |
| `/test` | Run the applicable test layers, including Playwright MCP. |
| `/audit` | Independent review: coverage, consistency, security, gaps. |
| `/release` | Final gate evaluation and readiness report. |

Put your material in `input/` first:

- `input/project-description.md` — what you want built
- `input/references/` — PDFs, screenshots, wireframes, specs

Both are **read-only artefacts**. Never edit, normalise, move or delete them.
Extracted content goes to `docs/source-analysis.md` and `evidence/discovery/`.

---

## 4. Non-negotiable rules

The full set lives in `factory/rules/`. These are the ones that get broken:

1. **Never fabricate evidence.** A test that did not run is `NOT_TESTED` or
   `BLOCKED`, with a recorded reason. Neither ever becomes `PASS`.
2. **Never claim Playwright testing happened unless Playwright MCP actually
   executed.** See `docs/playwright-strategy.md` if present, else
   `.claude/skills/playwright-mcp/SKILL.md`.
3. **A phase is not `COMPLETED` until its gate passes** —
   `factory/rules/quality-gates.md`.
4. **A feature is not done until the Definition of Done passes** —
   `factory/rules/definition-of-done.md`.
5. **Respect the source-of-truth hierarchy** —
   `factory/rules/source-of-truth.md`.
6. **Persist state after every meaningful step.** The run must survive a
   context reset, a crash or a new session.
7. **Never push to a remote or create a repository without explicit
   authorisation** — `factory/rules/git-policy.md`.
8. **Never commit secrets.** `.env.example`, never `.env`.
9. **`input/references/` is not committed** unless you decide otherwise;
   `.project/source-manifest.json` records what was used.
10. **Fix, don't just report.** A defect fixable here goes through the bug-fix
    loop, not into a backlog.
11. **Do not stop for confirmation between normal engineering steps.** Stop only
    for the escalation triggers in `factory/rules/source-of-truth.md`.
12. **Every UI is responsive, in both orientations**, across the declared
    viewport matrix — `factory/rules/responsive-rules.md`.

---

## 5. Vocabulary

Phase and feature status: `NOT_STARTED`, `IN_PROGRESS`, `BLOCKED`,
`READY_FOR_REVIEW`, `COMPLETED`, `FAILED`.

Test and verification status: `PASS`, `PARTIAL`, `FAIL`, `NOT_TESTED`,
`BLOCKED`, `NOT_APPLICABLE`.

Gate result: `PASS`, `FAIL`, `WAIVED` (a waiver needs a reason and an owner).

Definitions: `factory/rules/status-vocabulary.md`.

---

## 6. Layout

```
input/            Your description and references (read-only)
.project/         Manifest, run state, checkpoints, journal
docs/             Generated product documentation
evidence/         Real artefacts from real runs
.claude/agents/   Factory agents + this project's generated agents
.claude/commands/ Slash commands
.claude/skills/   Reusable procedures
factory/          Rules, schemas and templates (snapshot — read, do not edit)
backend/ web/ mobile/ shared/   Whatever the manifest calls for
```

---

## 7. Reading order for a new session

1. This file.
2. `.project/project.json` and `.project/state/state.json`, if they exist.
3. `AGENTS.md` — who does what.
4. `docs/orchestration.md` — the phase machine.
5. `factory/rules/quality-gates.md`.

Do not begin work before step 2.
