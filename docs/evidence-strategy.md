# Evidence Strategy

Evidence is the factory's answer to "how do you know?". It is what separates a
report from a claim.

The rules are `factory/rules/evidence-rules.md`; the procedure is
`.claude/skills/evidence-recording/SKILL.md`. This document explains why the
model is shaped as it is.

---

## 1. The problem

An agent that writes its own report can write anything. "Tests pass",
"validation works", "the login flow was verified" are cheap to produce and
expensive to check. Left alone, a long autonomous run accumulates confident
prose and no verifiable fact — and the failure is invisible until someone
tries to ship.

The factory's answer: **a claim is only as good as the artefact behind it, and
the artefact must exist on disk.**

## 2. What counts

Evidence is an artefact produced **by execution**:

- captured stdout/stderr of a command that ran,
- a screenshot taken by a real browser during this run,
- a result file written by a real test runner,
- a real HTTP request/response transcript,
- output from a real scanner,
- a diff, a build log, a migration log.

## 3. What does not

- prose describing what an agent believes would happen,
- a screenshot not captured during this run,
- a summary of tests that were not executed,
- "verified by code review" standing in for a browser test,
- a hand-written table of numbers not produced by a measurement.

Writing any of these into `evidence/` is a protocol violation — the one class
of error the factory treats as unrecoverable for the affected claim. The claim
is voided, the step reverts to `IN_PROGRESS`, and it is re-run.

## 4. Layout

```
evidence/
  discovery/      input inventory, extractions, capability profile, agent selection
  requirements/   traceability, coverage matrix
  architecture/   decision records, requirement coverage
  design/         token extraction, visual comparison
  database/       migration logs, schema verification
  api/            request/response transcripts, contract test output
  implementation/ build, lint, typecheck, unit output — per feature
  playwright/     scenario results, screenshots, MCP availability
  qa/             test runs, defect records, mobile and offline output
  security/       scan output, security report, dependency audit
  performance/    measurements, profiles, budgets
  regression/     full-suite runs, regression reports
  release/        final report, build verification, readiness
```

Per-feature evidence nests one level:
`evidence/implementation/f01-authentication/01-build.log`.

Naming is `<NN>-<slug>.<ext>` so ordering is visible in a directory listing.

Each directory is tracked with a `.gitkeep` so the layout survives a clone.

## 5. Binding evidence to claims

Evidence is not filed and forgotten. Every gate criterion marked `PASS` names
an evidence path, and the orchestrator checks that the path **exists** before
accepting it. A gate whose evidence cannot be found fails, whatever the agent
reported.

The same binding runs through the state model: `project-state` refuses to
write `COMPLETED` without a gate result and an existing evidence path, and
refuses to write `PASS` for a layer with no execution event in the journal.
The honesty rules are enforced at the point of writing, not audited later.

## 6. What evidence cannot prove

Each layer has a reach, and claiming beyond it is a violation:

| Artefact | Proves | Does not prove |
|---|---|---|
| Unit test output | a function behaves as specified | the feature works |
| Build log | the code compiles | the code is correct |
| Contract test | server and client share a shape | the UI uses it correctly |
| Screenshot | the page rendered | the workflow completes |
| Scenario result | a real journey completed | performance under load |
| Dependency scan | known CVEs in dependencies | the application is secure |

## 7. Absence is recorded

The most valuable evidence is often what is missing. A layer that did not run
is recorded as `NOT_TESTED` or `BLOCKED` with a reason — never omitted from
the report, because an omitted row reads as "fine" to anyone skimming.

`evidence/playwright/mcp-availability.md` exists whether or not MCP was
available. A run that could not test the browser says so, in the same place a
successful run would have said otherwise.

## 8. Secrets

No credential, token, key or personal datum is written into `evidence/`.
Screenshots and transcripts are checked before capture, and redacted where
needed. Evidence is committed, and a secret in a commit is a secret published.

## 9. Reading the evidence

For any claim in a final report, the reader should be able to open the named
path and see the artefact. If they cannot, the claim is not supported — and
the factory would rather say `BLOCKED` than have a reader discover that.
