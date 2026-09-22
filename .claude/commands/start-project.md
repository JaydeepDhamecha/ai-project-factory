---
description: Analyse the supplied description and references, generate the project, and drive it from requirements to production readiness.
argument-hint: "[constraints, or --restart to discard an existing run]"
---

# /start-project

The single top-level entry point of the factory. The user drops material into
`input/` and runs this once. Everything else — agent generation, documents,
stack selection, implementation, browser testing, fixing, regression, security,
release — happens underneath this command without further prompting.

Extra instructions from the user, if any: **$ARGUMENTS**

---

## 0. Execution contract — read this before anything else

This command **executes the pipeline**. It is not a checker, not a readiness
report, and not a plan for approval.

| Forbidden in this command | Required instead |
|---|---|
| Reporting what you *would* do | Doing it, then reporting evidence paths |
| Printing a phase list and ending the turn | Running the phases |
| Stopping because `.project/project.json` exists | Auto-continuing that run |
| Telling the user to run `/resume` | Resuming, here, now |
| Asking "shall I proceed?" between phases | Proceeding |
| Ending the turn between phase N and N+1 | Continuing in the same turn |

You are **authorised and required to use the Agent tool** for this command.
CLAUDE.md grants that authorisation for the factory pipeline; the general
restriction on delegation does not apply here.

You end your turn in exactly three situations:

1. `ROUTE=NEED_INPUT` below — there is genuinely nothing to build from.
2. One of the six escalation triggers in `factory/rules/source-of-truth.md`
   fires, and no further work is possible without the user.
3. The run reaches `14-release` and the final report is written.

Anything else is a protocol violation. Journal it as such if it happens.

Load `CLAUDE.md`, `AGENTS.md`, `docs/orchestration.md` and `factory/rules/`
before step 1.

---

## 1. Bootstrap — one command, never halts

```bash
mkdir -p input/references .project/state evidence
DESC=0; [ -s input/project-description.md ] && DESC=1
REFS=$(find input/references -type f ! -name '.gitkeep' ! -name '.DS_Store' 2>/dev/null | wc -l | tr -d ' ')
MAN=0;  [ -f .project/project.json ] && MAN=1
case "$DESC$REFS$MAN" in
  00*) ROUTE=NEED_INPUT ;;
  *)   [ "$MAN" = 1 ] && ROUTE=CONTINUE_RUN || ROUTE=FULL_RUN ;;
esac
[ "$DESC$REFS" = "00" ] && ROUTE=NEED_INPUT
echo "DESCRIPTION=$DESC  REFERENCES=$REFS  MANIFEST=$MAN  ROUTE=$ROUTE"
find input -type f ! -name '.gitkeep' ! -name '.DS_Store' 2>/dev/null
```

If `$ARGUMENTS` contains `--restart`, override to `ROUTE=RESTART`.

---

## 2. Route

| ROUTE | Meaning | Action |
|---|---|---|
| `FULL_RUN` | Input present, no manifest | Run phases `00` → `14`. Start at step 3. |
| `CONTINUE_RUN` | Input present, manifest exists | **Do not stop.** Invoke `project-state`, run the resume algorithm, print the briefing, then carry on from the next incomplete step through to `14-release`. Never re-run a `COMPLETED` step whose evidence exists. |
| `RESTART` | User passed `--restart` | Destructive. Confirm once, naming exactly what will be deleted (`.project/`, generated docs, generated `project-*` agents, platform directories). On confirmation, archive to `.project/archive/<timestamp>/`, then `FULL_RUN`. |
| `NEED_INPUT` | No description **and** no references | The only non-escalation stop. Print the block below and end the turn. |

`NEED_INPUT` message — print verbatim, then stop:

```
Nothing to build from. Give the factory material and run /start-project again.

  1. Put your PDFs, screenshots, wireframes or specs here:
       input/references/

  2. Optionally add a short description:
       cp factory/templates/project/project-description.template.md \
          input/project-description.md

Either one is enough. References alone are sufficient — a description is not
required.
```

**A description is never required when references exist.** If `DESCRIPTION=0`
and `REFERENCES>0`, proceed: `discovery` derives the overview from the
references and records every derivation as `DERIVED` in `docs/assumptions.md`.

---

## 3. Delegation protocol

Dispatch each unit of work with the Agent tool, using the invocation block from
`.claude/agents/orchestrator.md` § Invocation protocol:

```
AGENT / PHASE / FEATURE / SCOPE / INPUTS / CRITERIA / EVIDENCE / GATE / BUDGET
```

and require back `STATUS / EVIDENCE / VALIDATION / NOTES / DEFECTS`. A success
claim without `EVIDENCE` is rejected and re-run.

**Generated agents in a first session.** Phase `03` writes
`.claude/agents/project-*.md`, but the Agent tool's roster is fixed when the
session starts — on a fresh clone those agents are not yet dispatchable. Do not
stop, and do not tell the user to restart Claude Code. For each such unit:

1. Read `.claude/agents/project-<role>.md`.
2. Adopt that agent's role inline — same scope, same write permissions, same
   outputs, same evidence paths, same reply block.
3. Journal `inline_role_adoption` with the role and the reason.

Delegation and inline adoption are equivalent for gate purposes. What is never
equivalent is skipping the work.

Run independent agents concurrently where the phase allows it (for example
`project-designer` and `project-database` inside `02-plan`); keep dependent
agents sequential.

---

## 4. The pipeline

Checkpoint through `project-state` after every phase, feature step, gate
evaluation and defect change. Evaluate each gate criterion by criterion against
`factory/rules/quality-gates.md`. Do not advance on a failed gate.

### 00 — DISCOVER
`discovery`. Read the description if present and **every** reference — PDFs page
by page, images examined visually, not by filename. Write
`evidence/discovery/input-inventory.md`, `evidence/discovery/extractions/**`,
`docs/source-analysis.md` (every finding cited to file and page),
`docs/project-overview.md`, `docs/capability-profile.md`.
A reference that cannot be read is a blocker with a named reason — never a guess.
*No gate.*

### 01 — UNDERSTAND
`project-product` → `project-requirements`. Produce `docs/PRD.md`,
`docs/requirements.md`, `docs/user-stories.md`, `docs/acceptance-criteria.md`,
`docs/assumptions.md`. Every requirement carries an id, a citation and a
confidence level. **GATE-REQ.**

### 02 — PLAN
`project-technology` → `project-architect` → (`project-designer`,
`project-database`, `project-api` as the capability profile allows) →
`project-planner`. Produce the platform requirements, stack, architecture,
design system, schema, contract and a dependency-ordered, **vertically sliced**
development plan plus `.project/state/features.json`. **GATE-ARCH.**

### 03 — SELECT AGENTS
Write `.project/project.json` from
`factory/templates/project/project.template.json`. Invoke `agent-generator` to
instantiate only the agents and documents the profile requires, per
`factory/rules/agent-selection-matrix.md`; record every rejection with its
reason. Write the `scale` that `discovery` proposed into the manifest — absent
reads as `standard`. Invoke `workflow-validator`. *No gate.*

The phase headings in this file are **phases**, not dispatches. At `micro` or
`small` several of them share one agent invocation, per
`factory/rules/scale-rules.md` §3. Every phase still runs and every gate is
still evaluated; only the number of invocations changes.

### 04 — GENERATE STRUCTURE
`agent-generator` + `project-devops`. Create only the directories the manifest's
platforms require — no `backend/`, `web/` or `mobile/` otherwise. Scaffold the
stack, configuration, `.env.example` (never `.env`) and the test harness.
**GATE-ARCH re-check.**

### 05–11 — BUILD, one feature slice at a time, in dependency order

```
database → backend → api → web → mobile → integration
   → test → playwright → fix → retest → regression
```

Steps the profile excludes are recorded `NOT_APPLICABLE`, not skipped silently.
Evaluate **GATE-IMPL, GATE-INTG, GATE-TEST, GATE-PW** per slice. Any failure
enters the `bug-fix-loop` skill immediately — fix, do not file and move on. A
feature is not finished until `factory/rules/definition-of-done.md` passes, or
it is explicitly deferred with a recorded reason. Then start the next feature.

Probe Playwright MCP before the first `08-playwright` and record the probe
result. If it is unavailable: every browser scenario is `BLOCKED` with the
reason, GATE-PW fails, the rest of the pipeline continues, and the limitation
appears prominently in the final report. Reading source code is never a
substitute for a browser run.

### 12 — SECURITY
`project-security`. Full review per GATE-SEC; fix what is practical.
`evidence/security/security-report.md`. **GATE-SEC.**

### 13 — PERFORMANCE
`project-performance`. Measure, never estimate. Fix meaningful regressions;
skip micro-optimisation. **GATE-PERF.**

### 11 — FULL REGRESSION
`project-regression`. Re-run every layer including the browser pack.
`evidence/regression/final-regression-report.md`. **GATE-REG.**

### 14 — RELEASE
`project-reviewer` for an independent adversarial audit, then `project-release`.
**GATE-REL.** Produce `evidence/release/final-report.md`.

---

## 5. Standing rules for this run

1. Never fabricate evidence. `NOT_TESTED` and `BLOCKED` never become `PASS`.
2. Never claim Playwright testing without a real Playwright MCP execution.
3. Never invent major business functionality — pricing, permissions,
   regulatory or financial rules. Record `UNKNOWN`, build the surrounding
   structure, leave a marked seam, escalate at the next checkpoint.
4. `input/` is read-only. Never edit, rename, move or normalise it.
5. Commit locally at feature and gate boundaries. **Never** push to a remote or
   create a repository. See `factory/rules/git-policy.md`.
6. Never commit `.env` or any secret.
7. State must survive a context reset. If context is compacted mid-run, re-read
   `.project/state/state.json` and continue from the last checkpoint — do not
   restart, and do not hand the run back to the user.

---

## 6. Final report

Only at `14-release`. Explicit statuses throughout
(`PASS` / `PARTIAL` / `FAIL` / `NOT_TESTED` / `BLOCKED` / `NOT_APPLICABLE`),
covering: project summary, requirements implemented vs deferred, stack,
architecture, features, per-platform status, database, API, browser testing,
mobile testing, security, performance, regression, known limitations, risks,
deployment readiness, artefacts created, and the exact final status.

Then tell the user how to take the project out of the factory:

```
./scripts/extract-project.sh ../<project-name>
```
