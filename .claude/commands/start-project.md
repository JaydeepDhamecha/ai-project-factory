---
description: Analyse the supplied description and references, generate the project, and drive it from requirements to production readiness.
argument-hint: "[optional: extra instructions or constraints]"
---

# /start-project

Primary entry point of the factory. The user supplies input and runs this once.

Extra instructions from the user, if any: **$ARGUMENTS**

---

## Preconditions

```bash
test -f .project/project.json && echo "PROJECT EXISTS — use /resume" || echo "NEW PROJECT"
ls -la input/ input/references/ 2>/dev/null
```

- If `.project/project.json` already exists → **do not start over.** Report the
  current state and tell the user to run `/resume`. Only re-run
  `/start-project` if the user explicitly asks to discard and restart, and
  confirm that first.
- If `input/project-description.md` is missing and `input/references/` is
  empty → stop and tell the user exactly what to provide:

  ```
  cp factory/templates/project/project-description.template.md input/project-description.md
  # then put PDFs / screenshots / wireframes into input/references/
  ```

---

## Execution

Act as the `orchestrator` agent (`.claude/agents/orchestrator.md`). Load
`CLAUDE.md`, `AGENTS.md` and `factory/rules/` first. Then run the phase machine
end to end, without pausing between normal engineering steps.

### 00 — DISCOVER
Invoke `discovery`. Read the description and **every** reference file — PDFs
page by page, images examined visually. Produce `docs/project-overview.md`,
`docs/source-analysis.md`, the input inventory and the capability profile.

### 01 — UNDERSTAND
Produce `docs/PRD.md`, `docs/requirements.md`, `docs/user-stories.md`,
`docs/acceptance-criteria.md`, `docs/assumptions.md`. Every requirement gets an
id, a citation and a confidence level. **Evaluate GATE-REQ.**

### 02 — PLAN
Platform requirements → technology decision → architecture → design system →
database schema → API contract → development plan, each only where the
capability profile calls for it. Slice the plan vertically and order it by
dependency. **Evaluate GATE-ARCH.**

### 03 — SELECT AGENTS
Write `.project/project.json`. Invoke `agent-generator` to instantiate only the
required agents and document set. Record rejections with reasons. Invoke
`workflow-validator`.

### 04 — GENERATE STRUCTURE
Create only the directories the platforms require. Scaffold the chosen stack,
configuration, `.env.example`, and the test harness. Do not create
`backend/`, `web/` or `mobile/` unless the manifest says so.
**Re-evaluate GATE-ARCH.**

### 05–11 — BUILD, per feature, in dependency order

For each feature slice:

```
database → backend → api → web → mobile → integration
   → test → playwright → fix → retest → regression
```

Skip steps the profile excludes; record them as `NOT_APPLICABLE`. Evaluate
GATE-IMPL, GATE-INTG, GATE-TEST and GATE-PW for the slice. Run the bug-fix loop
on any failure. Do not start the next feature until this one satisfies the
Definition of Done — or is explicitly deferred with a reason.

### 12 — SECURITY
Full review per GATE-SEC. Fix what is fixable. `evidence/security/security-report.md`.

### 13 — PERFORMANCE
Measure, do not estimate. Fix meaningful regressions. Skip micro-optimisation.

### 11 — FULL REGRESSION
Re-run everything, including the browser pack. `evidence/regression/final-regression-report.md`.

### 14 — RELEASE
Invoke `reviewer` for an independent audit, then `release`. Evaluate GATE-REL.
Produce `evidence/release/final-report.md`.

---

## Rules for this run

1. Checkpoint through `project-state` after every phase, feature step, gate and
   defect change. The run must be resumable at any instant.
2. Never claim a test ran that did not run.
3. Probe Playwright MCP before phase 08 and record the result. If unavailable,
   mark browser scenarios `BLOCKED`, fail GATE-PW, continue the rest, and say
   so plainly in the final report.
4. Do not ask the user for confirmation between ordinary steps. Escalate only
   for the six triggers in `factory/rules/source-of-truth.md`.
5. Never invent major business functionality. Record it as `UNKNOWN` and build
   the surrounding structure.
6. Do not push to any remote.

---

## Final report

Report with explicit statuses (`PASS` / `PARTIAL` / `FAIL` / `NOT_TESTED` /
`BLOCKED`), covering: project summary, requirements implemented, stack,
architecture, features, per-platform status, database, API, browser testing,
mobile testing, security, performance, regression, known limitations, risks,
deployment readiness, artefacts created, and the exact final status.

`NOT_TESTED` and `BLOCKED` are never reported as `PASS`.
