---
description: Run the applicable test layers, including real browser testing through Playwright MCP, and record honest results.
argument-hint: "[optional: layer or feature — e.g. 'browser', 'f02', '--probe']"
---

# /test

Scope, if given: **$ARGUMENTS** (`--probe` = check Playwright MCP availability only)

## Preconditions

```bash
test -f .project/project.json || { echo "No project. Run /start-project."; exit 0; }
```

Read the manifest's capabilities to decide which layers apply. A layer that
does not apply is `NOT_APPLICABLE` — recorded, not omitted.

## Layer 0 — Playwright MCP probe (always, when `browserTesting`)

Before any browser work, probe the MCP server. Check whether Playwright MCP
tools (`browser_navigate`, `browser_snapshot`, `browser_click`, …) are actually
available in this session.

Record the result in `.project/project.json` under `mcp.playwright` and in
`evidence/playwright/mcp-availability.md`:

- `AVAILABLE` → proceed with real browser testing.
- `UNAVAILABLE` → every browser scenario is `BLOCKED` with the reason. GATE-PW
  fails. **Do not substitute source-code reading, unit tests, or reasoning
  about the UI for browser testing, and do not describe what the UI "would"
  do.**

With `--probe`, stop after this step and report.

## Layer 1 — Static

Formatter, linter, type check, build, for every platform. Capture real output
to `evidence/implementation/`.

## Layer 2 — Unit

Run the suite. Record counts. A suite with zero tests is `NOT_TESTED`, not
`PASS`.

## Layer 3 — Integration / contract

Where `backend` or `api`. Real requests against a running app. Store
transcripts in `evidence/api/`.

## Layer 4 — Browser (Playwright MCP)

Follow `docs/playwright-strategy.md` and the generated `project-playwright`
agent. In outline:

1. Start the app; confirm it responds at `appUrl`.
2. Enumerate routes from the running app.
3. Derive scenarios from acceptance criteria.
4. Drive the real UI: navigation, auth, CRUD, forms and validation, loading,
   empty and error states, authorisation negatives, and the full responsive and
   orientation pass — every viewport class in portrait **and** landscape, per
   `.claude/skills/playwright-mcp/SKILL.md` §4.1.
5. Screenshot every scenario.
6. Collect console errors and failed network requests.
7. Write `evidence/playwright/results.json` conforming to
   `factory/schemas/test-report.schema.json`.

## Layer 5 — Mobile

Where `mobile`. Simulator/emulator runs. State honestly which of
simulator / emulator / real device was used; never claim device testing that
did not happen.

## Results

Update `.project/state/test-status.json` per layer with status, counts, the
evidence path, and — for `BLOCKED`/`NOT_TESTED` — a reason.

## On failure

Every failure becomes a defect record
(`factory/schemas/defect.schema.json`) and enters the bug-fix loop:

```
REPRODUCE → ROOT CAUSE → FIX → RETEST → REGRESSION
```

Hand fixes to `bug-fixer`; a test agent does not patch product code itself.

## Honesty

- A scenario is `PASS` only if it executed and its assertions held.
- Never disable, skip or delete a test to make a run green.
- Never write a result file for a run that did not happen.
- Report `PARTIAL` with counts rather than rounding up to `PASS`.
