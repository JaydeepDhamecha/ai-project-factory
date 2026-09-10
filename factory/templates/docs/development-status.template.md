# {{PROJECT_NAME}} — Development Status

> Owner: `project-planner`, then `orchestrator` · Generated. Do not hand-edit.
> Derived from `.project/state/state.json` and `.project/state/features.json`,
> which are authoritative. Last updated: {{GENERATED_AT}}

## Summary

| Field | Value |
|---|---|
| Phase | |
| Current feature | |
| Active agent | |
| Project status | |
| Release readiness | |

## Phases

| Phase | Status | Gate | Gate result | Evidence |
|---|---|---|---|---|
| 00-discover | | — | | |
| 01-understand | | GATE-REQ | | |
| 02-plan | | GATE-ARCH | | |
| 03-select-agents | | — | | |
| 04-generate-structure | | GATE-ARCH (re-check) | | |
| 05-implement | | GATE-IMPL | | |
| 06-integrate | | GATE-INTG | | |
| 07-test | | GATE-TEST | | |
| 08-playwright | | GATE-PW | | |
| 09-fix | | — | | |
| 10-retest | | GATE-TEST + GATE-PW | | |
| 11-regression | | GATE-REG | | |
| 12-security | | GATE-SEC | | |
| 13-performance | | GATE-PERF | | |
| 14-release | | GATE-REL | | |

Mirrors the gate ↔ phase map in `factory/rules/quality-gates.md`, which is
authoritative. Status vocabulary: `factory/rules/status-vocabulary.md`. A phase that does not
apply is `NOT_APPLICABLE` with a reason — never blank, never quietly skipped.

## Features

| Id | Feature | Status | Steps done | DoD | Blockers |
|---|---|---|---|---|---|

## Test status

| Layer | Result | Passed | Failed | Not tested | Evidence |
|---|---|---|---|---|---|
| Unit | | | | | |
| Integration | | | | | |
| Contract | | | | | |
| Browser (Playwright) | | | | | |
| Mobile | | | | | |
| Regression | | | | | |

`NOT_TESTED` and `BLOCKED` are reported as themselves. They never appear as
`PASS`, and a layer with no run is not omitted from this table.

## Open defects

| Id | Severity | Feature | Status | Attempts | Release blocking |
|---|---|---|---|---|---|

## Blockers

| Id | Description | Blocking | Needs | Raised |
|---|---|---|---|---|

## Recent activity

| When | Event | Detail |
|---|---|---|

Drawn from the tail of `.project/state/journal.ndjson`.
