# Evidence Rules

Evidence is the factory's answer to "how do you know?". It is the difference
between a report and a claim.

---

## 1. What evidence is

Evidence is an artefact produced **by execution**:

- captured stdout/stderr of a real command,
- a screenshot taken by a real browser,
- a structured result file written by a real test runner,
- a real HTTP request/response transcript,
- a scan report emitted by a real scanner,
- a diff, a build log, a migration log.

## 2. What evidence is not

- Prose describing what an agent believes would happen.
- A screenshot that was not captured during this run.
- A test result summarising tests that were not executed.
- A "verified by code review" claim standing in for a browser test.
- A hand-written table of numbers not produced by a measurement.

Writing any of these into `evidence/` is a protocol violation, and is the one
class of error the factory treats as unrecoverable for the affected claim: the
claim is voided and the step re-run.

---

## 3. Layout

```
evidence/
  discovery/      input inventory, extractions, capability profile, agent selection
  requirements/   requirement traceability, coverage matrix
  architecture/   decision records, validation of arch vs requirements
  design/         design token extraction, visual reference comparisons
  database/       migration logs, schema dumps, constraint checks
  api/            request/response transcripts, contract test output
  implementation/ build, lint, typecheck, unit output per feature
  playwright/     browser scenario results, screenshots, MCP availability
  qa/             test runs, defect records, mobile test output
  security/       scan output, security report, dependency audit
  performance/    measurements, profiles, budgets
  regression/     full-suite runs, regression reports
  release/        final report, build verification, readiness checklist
```

Per-feature evidence nests one level:
`evidence/implementation/<feature-id>/build.log`

---

## 4. Naming

```
<NN>-<slug>.<ext>
```

Example: `evidence/playwright/auth/01-login-valid.png`,
`evidence/implementation/f01-auth/02-typecheck.log`.

Every directory containing evidence carries a `README.md` or `index.md`
listing what was run, when, by which agent, and the result.

---

## 5. Required metadata

Each evidence set has a manifest entry or header recording:

| Field | Example |
|---|---|
| `agent` | `project-playwright` |
| `phase` | `08-playwright` |
| `feature` | `f01-authentication` |
| `command` | `npx playwright test` / `browser_click(...)` |
| `startedAt` / `finishedAt` | ISO-8601 |
| `result` | `PASS` / `FAIL` / `PARTIAL` / `BLOCKED` |
| `exitCode` | `0` |
| `notes` | free text |

---

## 6. Absence of evidence

When a check could not run, the factory records the absence explicitly rather
than leaving a gap:

```markdown
# Browser validation — NOT EXECUTED

Status: BLOCKED
Reason: Playwright MCP server not reachable. Tool probe returned no
        `browser_navigate` tool. `.mcp.json` present; server did not start.
Attempted at: 2026-09-08T14:22:11Z
Impact: GATE-PW FAIL. Release readiness cannot be READY.
Remedy: install Node 18+, run `npx -y @playwright/mcp@latest --version`,
        restart Claude Code, re-run `/test`.
```

A missing evidence file with no such record is itself a validation failure.

---

## 7. Retention and Git

- Markdown, JSON and log evidence is committed.
- Screenshots are committed when they are small and materially useful
  (visual comparison, failure states).
- Videos, traces and archives are ignored by `.gitignore` — regenerable and
  large. If one matters, summarise it in markdown and reference it.
- Evidence is never deleted to make a report look cleaner. Superseded evidence
  is kept and marked superseded.

---

## 8. Traceability

Every claim in a final report links to evidence:

```markdown
| Requirement | Status | Evidence |
|---|---|---|
| REQ-014 bulk archive | PASS | evidence/playwright/records/07-bulk-archive.png |
| REQ-021 export CSV | NOT_TESTED | evidence/qa/coverage-gaps.md#req-021 |
```

`/audit` walks these links. A broken link is a finding.
