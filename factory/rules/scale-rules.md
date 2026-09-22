# Scale rules

A login page and a multi-tenant ERP are not the same amount of work, but the
factory used to run them identically: fifteen phases, fifteen dispatches, the
same document set. This file defines the one lever that varies with size — and,
more importantly, the much longer list of things that do not.

---

## 1. What scale is, and what it is not

`scale` is a field on the manifest (`factory/schemas/project.schema.json`), one
of `micro`, `small` or `standard`. It governs **how many agent dispatches a
phase takes**.

It does **not** govern:

- whether a phase runs — **all fifteen always run**;
- whether a gate is evaluated — **every gate is always evaluated**;
- whether a criterion is `MANDATORY` — scale never retypes a criterion;
- whether a phase is `NOT_APPLICABLE` — **scale never produces that status.**

> A phase is `NOT_APPLICABLE` only when a **capability flag** says the project has
> no such surface — the three cases in `docs/orchestration.md` §4, unchanged by
> this file. "We merged it into another pass" is not a reason, and a phase that a
> pass has already begun cannot legally become `NOT_APPLICABLE` anyway
> (`factory/rules/status-vocabulary.md`: the status is reachable only from
> `NOT_STARTED`).

**Merge dispatch, never merge state.** A *pass* is a unit of invocation. A
*phase* is a unit of record. `.project/state/state.json` always carries fifteen
phase entries with their own statuses, gates and verdicts, whatever the scale.

`standard` is the degenerate case, not a separate path: every pass contains
exactly one phase, `mode: SINGLE`. The pass mechanism is always on, so there is
one record format and one set of checks rather than two code paths.

---

## 2. Classifying a project

Decided by `discovery` in `00-discover`, from counts it already extracts with
citations. Every condition in a column must hold; any miss falls through.

| Signal | `micro` | `small` | otherwise |
|---|---|---|---|
| Entities | ≤ 2 | ≤ 8 | `standard` |
| Screens | ≤ 3 | ≤ 12 | `standard` |
| Roles | ≤ 1 | ≤ 3 | `standard` |
| Workflows | ≤ 2 | ≤ 8 | `standard` |
| Platforms | 1 | ≤ 2 | `standard` |
| Reference files | ≤ 2 | ≤ 6 | `standard` |

### Hard demotions to `standard`, whatever the counts say

1. Any of `payments`, `multiTenant`, `offline`, `realtime`, `i18n` or
   `backgroundJobs` is true. Money movement, tenancy isolation, conflict
   resolution and locale do not belong in a merged pass.
2. `existingCodebase` is true — reading someone else's code is not small reading.
3. Any reference file is unreadable or only partly analysed. **You cannot size
   what you have not read.**
4. Any of the six counts is unknown.
5. `web` and `mobile` are both true — **unless all four of the following hold**,
   in which case `small` is permitted (never `micro`: two client surfaces are
   not micro, whatever the screen count).

   | | Condition | Why |
   |---|---|---|
   | a | Both clients consume the **same** API contract, with no client-only domain logic | Divergence is what makes two surfaces expensive. Two thin renderers of one contract are one design problem, not two. |
   | b | `offline`, `realtime` and `backgroundJobs` are all false | Each turns a second client into a second consistency model. |
   | c | Combined screens across both clients ≤ 12, and the `small` row is satisfied on every other signal | The normal `small` bar still has to be cleared. |
   | d | The references **cover both clients** — a cited screen or spec for each | You cannot size a surface you have not seen. One client's screens do not describe the other's. |

   Record all four verdicts with citations in `scale-assessment.md`. A missing
   or uncited condition is a failed condition, and the demotion stands.

   The rule used to be absolute, and it was too blunt: a two-screen sign-in flow
   rendered by a web client and a mobile client against one `/auth` contract was
   forced to `standard` — fifteen dispatches for a project whose entire surface
   is a login form and a registration form. That is the case this exception
   exists for. It is **not** a licence to merge a web app and a mobile app that
   happen to share a backend; condition (a) is the load-bearing one.

### The default rule

> A project is `standard` unless **every** `micro` or `small` condition is
> affirmatively satisfied by a **cited count**. An absent count, an uncertain
> count, or a count the references do not support is a `standard` count.

### The safety rail

`.claude/agents/discovery.md` forbids marking a capability true "to be safe",
because a false-positive flag generates work nobody asked for. The mirror applies
here, and it is the more dangerous direction:

> **Never size a project down to make the run cheaper.** A mis-sized project
> hands phases to a pass that was never dimensioned for them, and the gate that
> gets lost is the last one in the pass.

### Recording the verdict

`evidence/discovery/scale-assessment.md`: one row per signal with its count, the
threshold, the citation, and the verdict; then the demotion checklist; then the
overall result. Same discipline `discovery` already applies to every capability
flag — no undetermined values.

### Re-confirmation, and promotion only

`scale` is **proposed** in `00-discover` and **confirmed** at the end of
`02-plan`, once `features.json` exists: more than 2 features voids `micro`, more
than 6 voids `small`.

Promotion — `micro` → `small` → `standard` — is legal at any point and is
journalled as a decision. **Demotion mid-run is forbidden.** Once phases have run
as separate dispatches you cannot un-run them, and re-sizing down mid-run is
precisely how a gate gets dropped.

---

## 3. Pass composition

Two rules constrain every merge map. They are not stylistic.

**Rule 1 — the per-feature boundary is impassable.** Phases 05–10 repeat per
feature; 11–14 run once. No pass may straddle that line.

**Rule 2 — a gate carrying a never-waivable criterion is never last, and never
shares a pass.** `GATE-PW` (PW-1, PW-15), `GATE-SEC` (SEC-2, SEC-11) and
`GATE-REL` (REL-3, REL-10, REL-11) hold seven of the factory's never-waivable
criteria. A pass agent that has spent its context on three prior phases is
exactly the agent that fabricates the fourth gate's evidence, and when a context
window compacts mid-pass **the work most likely to be lost is the work at the
end**. So `GATE-PW` and `GATE-REL` stay solo at every scale, and `GATE-SEC`
leads its pass.

**Rule 3 — `GATE-REL` is never merged at all.** REL-1 asserts over every prior
gate. A pass cannot evaluate its own precondition.

### `micro` — 15 phases, 7 passes

| Pass | Phases | Gates, in phase order | Why they share a dispatch |
|---|---|---|---|
| `P1-frame` | 00, 01, 02, 03, 04 | GATE-REQ, GATE-ARCH, GATE-ARCH (re-check) | All five read the same inputs and write only into `docs/`. 03 and 04 are already the same agent. Re-reading the inputs five times costs more than the work. |
| `P2-slice` | 05, 06, 07 | GATE-IMPL, GATE-INTG, GATE-TEST | Real duplicate elimination: IMPL-5 and TEST-2 are the *same* execution, IMPL-12 and TEST-7 the *same* evidence write. One run now serves both. Per feature. |
| `P3-browser` | 08 | GATE-PW | Solo, by rule 2. Per feature. |
| `P4-repair` | 09, 10 | GATE-TEST, GATE-PW re-evaluation | Already one loop in practice; 10 needs 09's reproduction and the same running app. Per feature, re-entrant per fix cycle. |
| `P5-regress` | 11 | GATE-REG | Solo. |
| `P6-harden` | 12, 13 | GATE-SEC (leads), GATE-PERF | Both drive the finished app. One app lifecycle. |
| `P7-ship` | 14 | GATE-REL | Solo, by rule 3. |

### `small` — 15 phases, 10 passes

`P1-read` (00, 01 → GATE-REQ) · `P2-design` (02, 03, 04 → GATE-ARCH ×2) ·
`P3-slice` (05, 06 → GATE-IMPL, GATE-INTG, per feature) · `P4-test`
(07 → GATE-TEST, per feature) · `P5-browser` (08 → GATE-PW, solo, per feature) ·
`P6-repair` (09, 10, per feature) · then 11, 12, 13, 14 each solo
(GATE-REG, GATE-SEC, GATE-PERF, GATE-REL).

### `standard` — 15 phases, 15 passes

Unchanged. Every pass `mode: SINGLE`, one phase each.

---

## 4. Invariants

These are what make merging safe. Each is an accounting identity, checkable by
someone other than the agent that ran the pass — deliberately the same shape as
the roster identity in `factory/rules/agent-selection-matrix.md`.

**I-1 — Gate conservation.** For every pass:

```
count(gates evaluated for phases in the pass)
  == count(phases in the pass that declare a gate)
```

A pass cannot be marked complete until that holds. `project-state` checks it at
write time; `workflow-validator` re-checks it independently. **This is the
invariant that stops a gate evaporating inside a merge.**

**I-2 — Evaluation order is phase order.** A pass evaluates its gates in phase
order, and each gate's evaluation timestamp is at or before the next phase's
start. Otherwise GATE-IMPL gets judged against post-test state and a criterion
that should have failed passes.

**I-3 — Per-phase checkpointing.** The orchestrator checkpoints at every
*intra-pass* phase boundary, never only at the pass boundary. Worst-case crash
loss stays one phase; a pass-level checkpoint would silently raise it to five.

**I-4 — `NOT_APPLICABLE` requires a named capability flag.** Never a pass id,
never a scale, never a schedule.

**I-5 — Promotion only.** See §2.

---

## 5. What scale does not buy

Stated plainly, because the temptation is to oversell it.

Measured on a completed reference run of 798 journal events, the fix → retest →
regression band was **646 of them — 81%**. Phases 00–04, which `micro` collapses
into a single pass, were **26 events — 3.3%**.

Merging removes dispatch overhead: repeated re-reads of the rules and documents,
repeated handoff blocks, and one app lifecycle in `P6-harden`. In `P2-slice` it
removes one genuinely duplicated test execution per feature.

**It removes no defect, no gate evaluation, no evidence write and no test run
outside that one duplicate.** A project that finds twelve bugs costs twelve
bug-fix loops at every scale. On a run that finds defects — which is every real
run — the saving trends toward zero.

If a project is expensive, the cost is almost never the number of phases. It is
the defect loop, and the evidence those phases write. See
`.claude/skills/evidence-recording/SKILL.md` §1 and §4, which is the larger
lever by a wide margin.
