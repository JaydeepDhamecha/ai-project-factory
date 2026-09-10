---
description: Evaluate all release gates and produce the production-readiness report.
argument-hint: "[optional: --dry-run]"
---

# /release

Decide whether this project is releasable, and say so honestly. **This command
does not deploy and does not push.**

Options: **$ARGUMENTS**

## 1. Preconditions

```bash
test -f .project/project.json || { echo "No project."; exit 0; }
```

All features must be `COMPLETED` or explicitly deferred. If any is
`IN_PROGRESS`, report `NOT_READY` and stop — do not evaluate release gates
against unfinished work.

## 2. Final regression

Re-run the full suite against the current tree, including the browser pack.
Results older than the last code change do not count. Evaluate GATE-REG.

## 3. Independent audit

Run `/audit`. Unresolved `CRITICAL` or `HIGH` findings block release.

## 4. Gate sweep

Re-evaluate every gate and report criterion by criterion:

```
GATE-REQ   PASS
GATE-ARCH  PASS
GATE-IMPL  PASS
GATE-INTG  PASS
GATE-TEST  PASS      unit 84/84, integration 22/22
GATE-PW    FAIL      3 of 14 browser scenarios failing (BUG-003)
GATE-SEC   PASS      0 CRITICAL, 0 HIGH
GATE-PERF  PASS      1 MEDIUM accepted
GATE-REG   PASS
GATE-REL   FAIL      REL-1 unsatisfied (GATE-PW)
```

## 5. Build verification

Production build for every platform, from a clean state. Migrations against a
clean database. `.env.example` complete with no real secret.

## 6. Readiness verdict

| Verdict | Meaning |
|---|---|
| `READY` | All mandatory gates pass. Zero open CRITICAL/HIGH. Builds verified. |
| `READY_WITH_CAVEATS` | All mandatory gates pass; documented MEDIUM/LOW issues remain. |
| `NOT_READY` | Any mandatory gate fails, or any CRITICAL/HIGH is open. |

`NOT_READY` is a legitimate, useful outcome. Do not soften it.

## 7. Final report

Write `evidence/release/final-report.md` covering:

1. Project summary
2. Requirements implemented (with coverage %)
3. Technology stack
4. Architecture summary
5. Features delivered / deferred
6. Web status
7. Mobile status
8. Backend status
9. Database status
10. API status
11. Playwright MCP testing status
12. Mobile testing status
13. Security review status
14. Performance review status
15. Regression status
16. Known limitations
17. Remaining risks
18. Deployment readiness
19. Artefacts created
20. Exact final status

Statuses are `PASS`, `PARTIAL`, `FAIL`, `NOT_TESTED` or `BLOCKED`. Every claim
links to evidence. `NOT_TESTED` and `BLOCKED` never appear as `PASS`.

## 8. Git

Commit the release artefacts locally. **Do not tag, push, create a repository
or open a pull request** unless the user explicitly instructs it in this
request (`factory/rules/git-policy.md`).
