---
description: Read-only snapshot of the current project — phase, feature, gates, tests, defects, blockers, next step.
---

# /status

**Read-only. This command changes nothing.** Do not fix, implement or advance
anything while running it, even if a problem is obvious — report it instead.

## Steps

```bash
test -f .project/project.json || { echo "FACTORY MODE — no project started. Run /start-project."; exit 0; }
```

1. Read `.project/project.json`.
2. Ask `project-state` for the resume briefing (read path only).
3. Read `.project/state/features.json`, `blockers.json`, `test-status.json`.
4. Read the tail of `journal.ndjson` for recent activity.
5. Verify that evidence paths claimed by `COMPLETED` units actually exist, and
   flag any that do not.

## Output

```
PROJECT      <name>  (<projectType>)
PLATFORMS    web, backend
STACK        <web> / <backend> / <database>
PHASE        08-playwright        STATUS  IN_PROGRESS   ATTEMPT 2
FEATURE      f02-employee-management  (step: playwright)
AGENT        project-playwright

PHASES
  00-discover           COMPLETED   —
  01-understand         COMPLETED   GATE-REQ   PASS
  ...
  08-playwright         IN_PROGRESS GATE-PW    FAIL

FEATURES        3 total — 1 COMPLETED, 1 IN_PROGRESS, 1 NOT_STARTED
  f01-authentication        COMPLETED  DoD PASS
  f02-employee-management   IN_PROGRESS
  f03-reporting             NOT_STARTED

TESTS
  static       PASS
  unit         PASS         84/84
  integration  PASS         22/22
  browser      FAIL         11/14   evidence/playwright/results.json
  mobile       NOT_APPLICABLE

PLAYWRIGHT MCP   AVAILABLE  (probed 2026-09-08T13:40Z)

DEFECTS      BUG-003 HIGH open · BUG-004 MEDIUM open
BLOCKERS     none
RISKS        GATE-PW failing blocks release

EVIDENCE     42 artefacts · 0 broken links
RELEASE      NOT_READY

NEXT STEP    /resume → 09-fix: reproduce BUG-003
```

If a `COMPLETED` unit has missing evidence, add:

```
⚠ INTEGRITY  f01-authentication claims evidence/playwright/f01/ — path missing
```

Be accurate about what has not been done. A status report that flatters the run
is worse than no report.
