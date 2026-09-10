---
name: playwright-mcp
description: Procedure for driving a real browser through Playwright MCP to validate a web application against its acceptance criteria, capture evidence, and report honestly when the tooling is unavailable. Use in phase 08-playwright and during retest and regression.
---

# Playwright MCP Testing

Real browser, real clicks, real evidence.

## 1. Probe before anything else

Determine whether Playwright MCP tools are actually available in this session —
`browser_navigate`, `browser_snapshot`, `browser_click`, `browser_type`,
`browser_take_screenshot` and related.

Record the result at `evidence/playwright/mcp-availability.md` and in the
manifest under `mcp.playwright`.

**If unavailable:**

```markdown
# Playwright MCP — UNAVAILABLE
Status: BLOCKED
Probed: <ISO timestamp>
Detail: <what was checked and what came back>
Impact: All browser scenarios BLOCKED. GATE-PW FAIL. Release NOT_READY.
Remedy: ensure Node 18+, `.mcp.json` registers @playwright/mcp,
        approve the server in Claude Code, restart the session.
```

Then stop the browser phase. Do **not** read source code and infer that the UI
works. Do not write scenario results. Do not produce screenshots by any other
means. `BLOCKED` is the correct, honest outcome.

## 2. Start the application

Start it with the project's dev/start command, in the background, and wait for
it to actually respond at `appUrl`. Capture the startup log to
`evidence/playwright/app-startup.log`.

If it will not start, that is a `CRITICAL` defect — not a browser-test blocker.
File it and hand it to `bug-fixer`.

## 3. Enumerate routes from the running app

Navigate to the root, snapshot, and follow real navigation. Cross-check against
the router source, but the running app is the authority — a route that exists
in source and 404s in the browser is a defect.

Record `evidence/playwright/routes.md`.

## 4. Derive scenarios from acceptance criteria

Each scenario names the acceptance criteria it covers. Coverage of a criterion
with a UI surface is mandatory (GATE-PW-4).

Baseline scenario families:

| Family | Must cover |
|---|---|
| Navigation | every route reachable; deep link; browser refresh; back/forward; 404 |
| Authentication | valid login; invalid password; unknown user; empty submit; logout; session persistence; protected route while logged out |
| Authorisation | for each role: one permitted action, one **denied** action |
| CRUD | create, read, update, delete for each managed entity, through the UI |
| Forms | required fields; invalid formats; boundary values; server-side error surfaced; successful submit |
| Lists | pagination, sorting, filtering, search, page-size, last page |
| States | loading, empty, error (force a failure), success |
| Responsive | each declared breakpoint: layout intact, nav usable, no overflow |
| Resilience | offline/failed request handling, double-submit, slow response |

## 5. Drive the real UI

Interact the way a user would: click the button, type in the field, submit the
form, read what appears. Prefer accessible selectors — role, label, text — over
brittle CSS paths.

For every scenario:

1. Navigate to the starting point.
2. Snapshot to understand the page.
3. Perform the actions, one at a time, observing between them.
4. Assert on what is actually rendered.
5. Screenshot: `evidence/playwright/<feature>/<NN>-<slug>.png`.
6. Collect console errors and failed network requests.

A console error on a passing scenario is at minimum a `MEDIUM` finding.

## 6. Record results

`evidence/playwright/results.json`, conforming to
`factory/schemas/test-report.schema.json`. Every scenario carries `executed`,
`status`, the steps actually taken, expected vs actual, and its screenshots.

`executed: false` requires a reason and forbids `PASS`.

## 7. Failures

Each failing scenario becomes a defect record: reproduction steps that another
person could follow, the screenshot, console output, the network failure if
any, and a severity. Hand it to `bug-fixer` — never patch product code from
this role.

After fixes: re-run the failing scenarios, then re-run the whole pack as
regression. A fix that breaks a previously passing scenario is a regression and
blocks release.

## 8. Visual comparison

Where the user supplied a screenshot of a screen, compare the implementation
against it: layout, spacing, typography, colour, component sizing, states.
Record deviations as intentional or defects.

Never claim pixel-perfect accuracy. Say what you compared and what you found.

## 9. Status vocabulary

Every scenario carries exactly one of these. The distinction between the last
three is the whole point — collapsing them is what turns an honest report into
a misleading one.

| Status | Means |
|---|---|
| `PASS` | Playwright MCP executed it in this run, and it passed |
| `PARTIAL` | executed; some steps or assertions did not complete |
| `FAIL` | executed, and failed |
| `NOT_TESTED` | never executed — no scenario was run against this criterion |
| `BLOCKED` | could not execute; the reason is recorded |
| `NOT_APPLICABLE` | no browser surface exists for this criterion |

`NOT_TESTED` is the correct status for a criterion nobody got to — a scenario
that was planned and not run, a route discovered too late, a state left
unexercised. It is not a softer `PASS`, and it is never omitted from the
results file: an absent row reads as "fine" to whoever skims the report.

`BLOCKED` is for work prevented by something external — MCP unavailable, the
app would not start, a dependency down.

Neither becomes `PASS` without a real re-run. See
`factory/rules/status-vocabulary.md`.

## 10. Absolute rules

1. A scenario is `PASS` only if Playwright MCP executed it in this run.
2. No scenario result is ever written for a run that did not happen.
3. No screenshot is ever fabricated or reused from another run.
4. `BLOCKED` and `NOT_TESTED` never become `PASS` without a real re-run.
5. Reading source code is never a substitute for driving the browser.
6. A criterion with no scenario is reported `NOT_TESTED`, never left out.
