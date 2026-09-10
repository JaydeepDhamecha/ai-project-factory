# Project State

How a run survives a crash, a context reset, or a new Claude Code session.

The `project-state` agent is the **sole writer** of `.project/state/`. Its
contract is `.claude/agents/project-state.md`; this document explains the
model and how to read it.

---

## 1. Why centralise

A long run outlives the context window that started it. If progress lives only
in the conversation, a reset restarts the project — the single most expensive
failure mode a factory like this has.

So progress lives on disk, in one directory, written by one agent, in one
format, validated against schemas, with an append-only audit trail. One writer
means no divergent formats and no lost updates.

## 2. Files

| File | Holds | Schema |
|---|---|---|
| `.project/project.json` | the manifest — what the project *is* | `project.schema.json` |
| `.project/state/state.json` | where the run *is* — phases, gates, position | `state.schema.json` |
| `.project/state/features.json` | feature slices and their steps | `features.schema.json` |
| `.project/state/journal.ndjson` | append-only event log | `journal-event.schema.json` |
| `.project/state/blockers.json` | open blockers and what each needs | — |
| `.project/state/test-status.json` | per-layer test results | `test-report.schema.json` |
| `.project/state/decisions.md` | decisions and their rationale | — |
| `.project/state/checkpoints/` | point-in-time snapshots | `state.schema.json` |

The manifest and the state directory are **committed**. They are the project's
memory, not scratch files — `.gitignore` deliberately does not exclude them.

### Manifest versus state

The manifest answers *what is this project* — type, platforms, capabilities,
stack, agent roster, generated documents. The state file answers *where are
we* — current phase, current feature, gate results, blockers.

The orchestrator may update a small set of manifest fields (`currentPhase`,
`status`, `releaseReadiness`, `updatedAt`). Everything under `state/` goes
through `project-state`, including for the orchestrator.

## 3. The journal

Append-only, one JSON object per line. Never rewritten, never truncated.

Because it is append-only, the journal is the tiebreaker: when `state.json`
and the journal tail disagree, **the journal wins** and the state file is
repaired from it. A summary can be written wrongly; an append-only log of what
happened is much harder to corrupt convincingly.

Events cover phase transitions, agent invocations, gate evaluations, test
executions, defect state changes, evidence writes, blockers, decisions,
protocol violations and state repairs.

## 4. Checkpoints

Written after every phase transition, feature step, gate evaluation, defect
state change and evidence write — to
`.project/state/checkpoints/<phase>-<timestamp>.json`.

Checkpoint granularity sets the worst-case loss on a crash. This granularity
means at most one step.

## 5. Resume

`/resume` invokes `project-state`, which runs the algorithm in
`.claude/agents/project-state.md` § Resume algorithm:

```
1. Manifest absent            → FACTORY MODE; nothing to resume
2. state.json absent          → initialise; report a fresh start
3. state invalid              → repair from checkpoint + journal
4. journal disagrees          → journal wins; repair state
5. locate position:
     phase IN_PROGRESS        → resume it, attempts += 1
     all COMPLETED            → the run is done
     phase FAILED             → resume there
     phase BLOCKED, resolved  → resume it
     phase BLOCKED, open      → report BLOCKED and what is needed
6. first feature step not COMPLETED
7. re-verify the last COMPLETED unit's evidence exists
     missing                  → downgrade to IN_PROGRESS, journal it
8. emit the resume briefing
```

Two rules do the real work:

- **Never re-run a `COMPLETED` step whose evidence is intact.** Redoing
  finished work wastes the budget a long run depends on.
- **Never assume progress the journal does not record.** A step whose evidence
  has vanished was not completed, whatever the state file says. It is
  downgraded and redone.

### The briefing

Resume prints what is being resumed before doing anything — project, phase,
feature, last agent, last event, completed phases, gate results, open blockers
and defects, test status, and the next step. It is printed so a person can
disagree with it before work continues.

## 6. Integrity

| Problem | Response |
|---|---|
| Schema validation fails | reject the mutation; state untouched |
| Illegal status transition | reject and report — usually an orchestrator bug |
| Honesty invariant violated | reject, journal `protocol_violation`, notify |
| `state.json` corrupt | rebuild from last checkpoint, replay journal, report what was lost |
| Journal corrupt | preserve as `journal.ndjson.corrupt-<ts>`, start fresh, report |
| `state/` missing, manifest present | reinitialise, all phases `NOT_STARTED`, warn loudly |

Every write is re-read and re-validated. A write that cannot be verified is
rolled back.

## 7. Honesty invariants

Enforced at the point of writing, so a false claim cannot enter the record:

1. `COMPLETED` requires a gate result and an evidence path that exists.
2. `PASS` cannot be written for a layer with no execution event in the
   journal.
3. `NOT_TESTED` and `BLOCKED` never transition directly to `PASS` — the work
   must actually run first.
4. Timestamps are monotonic within a run.

An attempted violation is rejected and journalled as `protocol_violation`.
The record of the attempt is itself kept.

## 8. Inspecting a run

```bash
cat .project/state/state.json | python3 -m json.tool | head -40
tail -20 .project/state/journal.ndjson
ls .project/state/checkpoints/
```

`/status` renders the same information as a briefing, read-only.
