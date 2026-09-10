# {{PROJECT_NAME}} — Acceptance Criteria

> Owner: `project-requirements` · Every criterion must be objectively
> verifiable by an executed test.

## Format

```
AC-NNN-n
  Given  <precondition / state>
  When   <action>
  Then   <observable outcome>
  Verified by: unit | integration | browser | mobile | manual
  Test:        <test id or path, once written>
  Status:      NOT_TESTED | PASS | FAIL | BLOCKED | NOT_APPLICABLE
```

Criteria state observable outcomes, never implementation. "The list shows 20
rows and a Next control" is verifiable; "pagination works correctly" is not.

## REQ-001 — {{REQUIREMENT_TITLE}}

AC-001-1

## Mandatory coverage per screen-bearing requirement

Each gets criteria for: happy path, validation failure, empty state, error
state, loading state, and — where `{{CAP_AUTHZ}}` — an unauthorised-access
negative case.

## Coverage matrix

| AC | Layer | Test | Last result | Evidence |
|---|---|---|---|---|

A criterion with no test is recorded here as an explicit gap, never omitted.
