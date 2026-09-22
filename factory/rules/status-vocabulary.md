# Status Vocabulary

One vocabulary, used identically in every agent, document, manifest, state file
and report. Agents must not invent synonyms ("done", "ok", "working").

---

## 1. Phase / feature / task status

| Value | Meaning | Allowed next |
|---|---|---|
| `NOT_STARTED` | Nothing has begun. | `IN_PROGRESS`, `BLOCKED`, `NOT_APPLICABLE` |
| `IN_PROGRESS` | Active work by a named agent. | `READY_FOR_REVIEW`, `BLOCKED`, `FAILED` |
| `BLOCKED` | Cannot proceed; external dependency or missing input. Requires a blocker record. | `IN_PROGRESS`, `FAILED` |
| `READY_FOR_REVIEW` | Work complete, gate not yet evaluated. | `COMPLETED`, `FAILED`, `IN_PROGRESS` |
| `COMPLETED` | Work complete **and** the quality gate passed **and** evidence exists. | `IN_PROGRESS` (reopened by regression) |
| `FAILED` | Attempted and failed; gate failed or fix attempts exhausted. | `IN_PROGRESS`, `BLOCKED` |
| `NOT_APPLICABLE` | Not required for this project's capability profile. Never assigned for reasons of scale, schedule or pass structure, and never for an empty loop. | terminal |

`COMPLETED` is the only success terminal state, and it has three preconditions
that are checked together, never separately:

1. the work exists,
2. the gate result is `PASS` or an explicitly recorded `WAIVED`,
3. evidence exists at the declared path.

---

## 2. Test / verification status

| Value | Meaning |
|---|---|
| `PASS` | Executed, and every assertion held. |
| `PARTIAL` | Executed; some scenarios passed, some failed. Always accompanied by counts. |
| `FAIL` | Executed, and at least one release-blocking assertion failed. |
| `NOT_TESTED` | Not executed. No opinion is offered on whether it works. |
| `BLOCKED` | Could not be executed; tooling, environment or dependency missing. Requires a reason. |
| `NOT_APPLICABLE` | Meaningless for this project (e.g. browser tests on an API-only project). |

### Forbidden transitions

- `NOT_TESTED` → `PASS` without an execution record.
- `BLOCKED` → `PASS` without the blocker being resolved and the test re-run.
- `FAIL` → `PASS` without a re-run recorded after the fix.
- Any status → `PASS` justified by reading source code rather than executing.

These are the factory's core honesty invariants. `workflow-validator` and
`/audit` check them against `journal.ndjson`.

---

## 3. Gate result

| Value | Meaning |
|---|---|
| `PASS` | All mandatory criteria satisfied. |
| `FAIL` | At least one mandatory criterion unsatisfied. |
| `WAIVED` | Deliberately accepted despite failure. Requires `reason`, `owner`, `expiresAtPhase`. Release-blocking criteria cannot be waived by an agent — only by the user. |
| `NOT_EVALUATED` | Gate has not run yet. |

---

## 4. Severity

Used for defects, security findings and performance findings.

| Value | Release impact |
|---|---|
| `CRITICAL` | Blocks release unconditionally. Data loss, auth bypass, corruption, total feature failure. |
| `HIGH` | Blocks release unless waived by the user. Major workflow broken, significant vulnerability. |
| `MEDIUM` | Does not block release. Recorded in known issues. |
| `LOW` | Cosmetic or minor. Recorded. |
| `INFO` | Observation only. |

`CRITICAL` and `HIGH` are collectively "release-blocking".

---

## 5. Confidence

Used when the factory infers rather than reads a requirement.

| Value | Meaning |
|---|---|
| `EXPLICIT` | Stated directly in user input or a reference document. Cite the source. |
| `DERIVED` | Logically implied by explicit content. Record the inference. |
| `ASSUMED` | Reasonable engineering default. Must appear in `docs/assumptions.md`. |
| `UNKNOWN` | Genuine gap. Must appear in `docs/assumptions.md` as an open question. |

No business rule may be implemented at confidence `UNKNOWN`. `ASSUMED`
business rules are permitted only when safe and reversible; major business
functionality must never be invented.
