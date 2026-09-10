---
name: bug-fix-loop
description: The reproduce → root-cause → fix → retest → regression procedure applied to every defect the factory finds. Use whenever a test, browser scenario, review or scan produces a failure.
---

# Bug-Fix Loop

```
TEST ─fail─▶ REPRODUCE ─▶ ROOT CAUSE ─▶ FIX ─▶ RETEST ─▶ REGRESSION ─▶ CLOSE
                 │                                │
          not reproducible                      fail
                 ▼                                │
        record + keep the scenario ◀──────────────┘ (bounded retries)
```

## 1. Record the defect

`evidence/qa/defects/BUG-NNN.json`, per `factory/schemas/defect.schema.json`.
Severity from `factory/rules/status-vocabulary.md` §4.

State `REPORTED`.

## 2. Reproduce — before touching any code

Reproduce it deliberately, capturing evidence. Write reproduction steps a
different person could follow without context.

If it will not reproduce after a genuine attempt: state `NOT_REPRODUCIBLE`,
record what was tried, and **keep the failing scenario in the suite**. An
intermittent failure is a defect, not noise.

## 3. Root cause

Find the actual cause, not the nearest symptom. Record the file and line, and
the category (logic, validation, state, contract mismatch, configuration, race,
UI, data, security, performance, environment).

Ask whether the same cause exists elsewhere. One root cause frequently explains
several open defects — link them.

## 4. Fix

- Fix the cause.
- Smallest change that genuinely resolves it.
- No workaround that hides the symptom.
- No widening of scope into unrelated refactoring.
- Never modify, skip or delete a test to make it pass. If a test is genuinely
  wrong, prove it in the defect record and change it deliberately, with the
  argument written down.

Record the files changed and the attempt number.

## 5. Write the regression test

Every fix gets a test that:

- **fails** against the pre-fix code, and
- **passes** against the fixed code.

Verify both directions and record both. A test that passes before the fix was
not testing the defect.

## 6. Retest

Re-run the exact scenario that failed. Then re-run the layer it belongs to.

## 7. Regression

Re-run the full applicable suite, including the browser pack. A fix that breaks
something previously passing is itself a defect — file it and loop.

## 8. Close

`CLOSED` requires all of: reproduced (or explicitly not reproducible),
root-caused, fixed, regression test present and verified both ways, retest
passed, regression passed. Anything less stays open.

## 9. Budgets

Defaults in `state.json.fixLoop`: 3 attempts per defect, 5 cycles per phase.

On exhaustion: stop looping, record `DEFERRED` with everything learned, and
escalate. If severity is `CRITICAL` or `HIGH`, release readiness becomes
`NOT_READY` — an unfixed blocker is reported, never quietly downgraded.

## 10. Never

- Close a defect without a re-run.
- Mark a scenario `PASS` because the fix "should" work.
- Weaken an assertion to achieve green.
- Fix the test instead of the code, absent a written argument.
- Batch a dozen fixes and retest once — you lose the causal link.
