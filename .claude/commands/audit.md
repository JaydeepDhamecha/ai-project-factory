---
description: Independent review of the project — requirements coverage, consistency, evidence integrity, security, quality and gaps. Read-only.
argument-hint: "[optional: area to focus on]"
---

# /audit

An adversarial second look. Assume the implementation is wrong and try to prove
it. **Read-only — record findings, do not fix them here.**

Focus, if given: **$ARGUMENTS**

## 1. Structural integrity

Invoke `workflow-validator` over the whole project. Every error it reports is
an audit finding.

## 2. Requirements coverage

- Every requirement in `docs/requirements.md` → a feature → implementing code.
- Every acceptance criterion → an executed test, or an explicitly recorded gap.
- Anything implemented that no requirement asked for (scope creep).
- Requirements silently dropped between the PRD and the plan.

Produce a traceability matrix: requirement → feature → code → test → evidence.

## 3. Evidence integrity — the core of the audit

For every `PASS` in the project:

- Does the named evidence file exist?
- Was it produced by execution, or is it prose describing an expectation?
- Is there a matching execution event in `journal.ndjson`?
- Do the counts in the report match the raw output?
- Did any `NOT_TESTED` or `BLOCKED` become `PASS` without a re-run?
- Were tests skipped, disabled or deleted near a defect fix?

Any "yes" to the negative cases is a `CRITICAL` finding — the factory's honesty
invariants outrank every other concern.

## 4. Consistency

- Implementation vs `docs/api-contract.md`.
- Code vs `docs/database-schema.md`.
- UI vs `docs/design-system.md` and the supplied visual references.
- Web vs mobile domain behaviour.
- Documents vs each other (a change made in one and not its dependants).

## 5. Quality

Placeholders, mocks or fake data on production paths; `TODO`/`FIXME` on
release-blocking paths; dead code; swallowed errors; missing validation;
duplicated logic that should be shared; unhandled promise rejections; missing
loading/empty/error states.

## 6. Security

Re-check GATE-SEC independently rather than trusting the security agent's
report: secrets in the tree, authorisation enforced server-side, injection
surfaces, XSS/CSRF/CORS, upload handling, sensitive data in logs and errors,
dependency advisories, insecure defaults.

## 7. Operational readiness

`.env.example` completeness, migrations on a clean database, health checks,
logging, error reporting, build reproducibility.

## Output

`evidence/release/audit-<timestamp>.md`:

```markdown
# Audit — <timestamp>
Result: PASS | PASS_WITH_FINDINGS | FAIL
Findings: 2 CRITICAL, 3 HIGH, 7 MEDIUM, 4 LOW

## CRITICAL
### AUD-001 — Browser tests reported PASS with no MCP execution record
Evidence: .project/state/journal.ndjson has no `test_executed` for f03
Impact:   GATE-PW result is not trustworthy
Remedy:   re-run /test browser for f03

## Traceability matrix
| REQ | Feature | Code | Test | Evidence | Status |
```

Findings become defects or blockers for the orchestrator to schedule. The audit
itself fixes nothing.
