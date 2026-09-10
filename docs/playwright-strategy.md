# Playwright Strategy

Browser testing is a first-class phase of the factory, not a formality at the
end. This document explains the strategy; the executable procedure is
`.claude/skills/playwright-mcp/SKILL.md`, and the gate criteria are
`factory/rules/quality-gates.md` § GATE-PW.

---

## 1. The rule that matters most

> **Never claim Playwright testing happened unless Playwright MCP actually
> executed.**

If the tooling is unavailable, every browser scenario is `BLOCKED`, GATE-PW
fails, and the release is `NOT_READY`. That is the honest outcome and it is
acceptable. What is not acceptable:

- reading the source and concluding the UI works,
- writing scenario results that were never executed,
- producing "screenshots" by any means other than a real browser,
- downgrading a browser criterion to a code review and calling it `PASS`,
- reporting `NOT_TESTED` as though it were `PASS`.

`NOT_TESTED` and `BLOCKED` never become `PASS`. Only execution changes that.

## 2. When it applies

GATE-PW applies when `browserTesting` is true — that is, `web` or
`adminPortal`. For a mobile-only, API-only, CLI or library project, GATE-PW is
recorded `NOT_APPLICABLE` with the reason. Recorded, not omitted: a reader
must be able to tell "no browser exists" from "nobody looked".

Playwright does not test native mobile. Mobile verification belongs to
`project-mobile` and `project-qa`, and where no device or emulator is
available the result is `NOT_TESTED` or `BLOCKED`.

## 3. Sequence

```
1  probe MCP availability      → evidence/playwright/mcp-availability.md
2  start the app               → evidence/playwright/app-startup.log
3  enumerate routes live       → evidence/playwright/routes.md
4  derive scenarios from ACs
5  execute against the real UI
6  capture evidence per step
7  record failures as defects
8  hand to bug-fixer
9  re-run failed scenarios
10 regression across features
```

The probe comes first because everything after it is conditional on a real
browser. The application is started with the project's own command and must
actually respond at `appUrl` before testing begins — a failure to start is a
`CRITICAL` defect, not a testing blocker.

Routes are enumerated from the **running application**. Source is
cross-checked, but the running app is authoritative: a route that exists in
the router and 404s in the browser is a defect, and only a live enumeration
finds it.

## 4. Coverage

Scenarios derive from acceptance criteria, and each names the criteria it
covers. Every acceptance criterion with a UI surface must be covered
(GATE-PW-4).

The baseline families, per the skill:

| Family | Covers |
|---|---|
| Navigation | every route reachable, no dead links |
| Forms | valid submit, invalid submit, field validation, error text |
| CRUD | create, read, update, delete, and the list reflecting each |
| Validation | client and server rejection, and what the user sees |
| States | loading, empty, error, success |
| Authentication | login, logout, session expiry, protected redirect |
| Authorisation | each role sees and reaches only what it should |
| Responsive | each declared breakpoint |

The states family is the one most often skipped and the one that most often
breaks in production. An empty list, a failed request and a slow response are
states a user will meet; each is exercised deliberately.

Authorisation testing includes attempting to reach another user's data
directly. A UI that merely hides a control has not enforced anything.

## 5. Evidence

Under `evidence/playwright/`:

| Artefact | |
|---|---|
| `mcp-availability.md` | the probe result and timestamp |
| `app-startup.log` | captured startup output |
| `routes.md` | routes as found in the running app |
| `results.json` | per-scenario results (`test-report.schema.json`) |
| `<feature>/<NN>-<slug>.png` | screenshots from the real browser |

A screenshot is evidence only if a real browser took it during this run.
Screenshots are checked for secrets before being written — no tokens, no
personal data.

## 6. Failure

A failing scenario becomes a defect and enters the bug-fix loop: reproduce →
root cause → fix → retest → regression. The scenario is re-run after the fix,
and the regression pass re-runs previously passing scenarios to catch what the
fix broke.

A scenario is never made to pass by weakening its assertion, removing a step,
or marking it skipped. If a scenario is genuinely wrong, it is corrected and
the correction is recorded as a decision.

## 7. When MCP is unavailable

```markdown
# Playwright MCP — UNAVAILABLE
Status: BLOCKED
Probed: <ISO timestamp>
Detail: <what was checked and what came back>
Impact: All browser scenarios BLOCKED. GATE-PW FAIL. Release NOT_READY.
Remedy: Node 18+, `.mcp.json` registers @playwright/mcp,
        approve the server in Claude Code, restart the session.
```

The orchestrator continues with every phase that does not depend on the
browser, then reports the limitation prominently in the final report. A
release shipped in this state is shipped knowingly, not accidentally.

## 8. Setup

`.mcp.json` in this repository registers the server:

```json
{ "mcpServers": { "playwright": {
    "command": "npx", "args": ["-y", "@playwright/mcp@latest"], "env": {} } } }
```

Registration is not availability — Claude Code must approve and start it.
Confirm with `/test --probe`, which stops after the probe and reports.
`./scripts/check-prerequisites.sh` verifies the registration but cannot
verify a live connection from outside the session.
