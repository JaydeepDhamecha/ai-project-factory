# Quality Gates

A gate is a checklist evaluated by the orchestrator at a phase boundary. A
phase cannot be marked `COMPLETED` while its gate result is `FAIL` or
`NOT_EVALUATED`.

Gate results are written to `.project/state/state.json` under `gates` and
journalled. Every gate evaluation must name the evidence path it inspected.

```
gate criteria
  ├── MANDATORY  — must pass; failure = gate FAIL
  ├── CONDITIONAL — mandatory only when a capability flag is set
  └── ADVISORY   — recorded, never blocks
```

A criterion whose capability flag is false evaluates to `NOT_APPLICABLE` and
does not affect the result.

---

## GATE-REQ — Requirements

Phase: `01-understand` → `02-plan`

| # | Criterion | Type |
|---|---|---|
| REQ-1 | `docs/project-overview.md` and `docs/source-analysis.md` exist | MANDATORY |
| REQ-2 | Every reference file in `input/references/` is accounted for: analysed, or recorded as unreadable with a reason | MANDATORY |
| REQ-3 | `docs/requirements.md` exists and every requirement has a stable id, a source citation and a confidence level | MANDATORY |
| REQ-4 | Every functional requirement has at least one acceptance criterion in `docs/acceptance-criteria.md` | MANDATORY |
| REQ-5 | `docs/assumptions.md` exists and lists every `ASSUMED` and `UNKNOWN` item | MANDATORY |
| REQ-6 | No requirement is at confidence `UNKNOWN` and simultaneously scheduled for implementation | MANDATORY |
| REQ-7 | User roles and permissions enumerated | CONDITIONAL (`auth`) |
| REQ-8 | `docs/user-stories.md` exists | ADVISORY |
| REQ-9 | Out-of-scope list recorded | MANDATORY |

---

## GATE-ARCH — Architecture

Phase: `02-plan` / `04-generate-structure`

| # | Criterion | Type |
|---|---|---|
| ARCH-1 | `docs/architecture.md` exists and covers boundaries, modules, error handling, configuration, logging | MANDATORY |
| ARCH-2 | `docs/technology-stack.md` exists; every choice has a rationale; no unused technology is introduced | MANDATORY |
| ARCH-3 | `docs/platform-requirements.md` matches `platforms` in the manifest | MANDATORY |
| ARCH-4 | `docs/database-schema.md` exists: entities, keys, relationships, indexes, constraints, audit fields | CONDITIONAL (`database`) |
| ARCH-5 | `docs/api-contract.md` exists: auth, endpoints, schemas, errors, pagination, status codes | CONDITIONAL (`api`) |
| ARCH-6 | `docs/design-system.md` exists and is derived from supplied visual references where any exist | CONDITIONAL (`web` or `mobile`) |
| ARCH-6a | `docs/design-system.md` states the layout at every viewport class in the matrix, in both orientations, and the narrow/short-landscape behaviour of navigation, tables and modals — `factory/rules/responsive-rules.md` §2, §3, §4 | CONDITIONAL (`responsive`) |
| ARCH-7 | `docs/offline-sync.md` exists and classifies each feature | CONDITIONAL (`offline`) |
| ARCH-8 | Authentication and authorisation model specified | CONDITIONAL (`auth`) |
| ARCH-9 | Every requirement maps to at least one architectural element | MANDATORY |
| ARCH-10 | `docs/development-plan.md` slices work vertically and orders features by dependency | MANDATORY |

---

## GATE-IMPL — Implementation (per feature slice)

Phase: `05-implement`

| # | Criterion | Type |
|---|---|---|
| IMPL-1 | Every acceptance criterion for the feature has implementing code | MANDATORY |
| IMPL-2 | Formatter and linter pass | MANDATORY |
| IMPL-3 | Type checking passes | CONDITIONAL (typed stack) |
| IMPL-4 | Build succeeds for every affected platform | MANDATORY |
| IMPL-5 | Unit tests for the feature exist and pass | MANDATORY |
| IMPL-6 | No placeholder, mock, stub or fake data on a production path | MANDATORY |
| IMPL-7 | No `TODO`/`FIXME` introduced on a release-blocking path | MANDATORY |
| IMPL-8 | Migrations exist, apply cleanly, and are reversible or explicitly one-way | CONDITIONAL (`database`) |
| IMPL-9 | Loading, empty and error states implemented | CONDITIONAL (`web` or `mobile`) |
| IMPL-9a | Responsive layout implemented per `factory/rules/responsive-rules.md` §3, and observed by the implementing agent at every viewport class × orientation, recorded in `responsive-check.md` | CONDITIONAL (`responsive`) |
| IMPL-9b | Both orientations supported on every screen, or the lock is recorded with a reason in `docs/platform-requirements.md`; rotation preserves state — §4 | CONDITIONAL (`responsive`) |
| IMPL-10 | Server-side validation present for every write path | CONDITIONAL (`backend`) |
| IMPL-11 | Secrets read from environment; nothing hard-coded | MANDATORY |
| IMPL-12 | `evidence/implementation/<feature>/` contains the command output | MANDATORY |

---

## GATE-INTG — Integration

Phase: `06-integrate`

| # | Criterion | Type |
|---|---|---|
| INTG-1 | Client requests conform to `docs/api-contract.md` | CONDITIONAL (`api`) |
| INTG-2 | Response shapes match the contract; no client-side shape guessing | CONDITIONAL (`api`) |
| INTG-3 | Auth token lifecycle verified end to end: obtain, use, refresh, expire, log out | CONDITIONAL (`auth`) |
| INTG-4 | Error responses surfaced correctly in every client | CONDITIONAL (≥1 client) |
| INTG-5 | Web and mobile share domain behaviour where both exist | CONDITIONAL (`web` and `mobile`) |
| INTG-6 | Integration tests exist and pass | MANDATORY |
| INTG-7 | No client bypasses the documented API surface | CONDITIONAL (`api`) |
| INTG-8 | `evidence/api/` contains real request/response transcripts | CONDITIONAL (`api`) |

---

## GATE-TEST — Testing

Phase: `07-test`

| # | Criterion | Type |
|---|---|---|
| TEST-1 | `docs/testing-strategy.md` exists and declares which layers apply | MANDATORY |
| TEST-2 | Unit suite executed; result recorded with counts | MANDATORY |
| TEST-3 | Integration suite executed; result recorded | CONDITIONAL (`backend` or `api`) |
| TEST-4 | Every acceptance criterion maps to ≥1 executed test, or is explicitly `NOT_TESTED` with a reason | MANDATORY |
| TEST-5 | Coverage of release-blocking paths recorded | ADVISORY |
| TEST-6 | No test was skipped, disabled or deleted to make the suite green | MANDATORY |
| TEST-7 | Raw test output stored in `evidence/qa/`, and summarised in that directory's `index.md` with counts, exit code and distinct failures | MANDATORY |

---

## GATE-PW — Playwright / browser validation

Phase: `08-playwright`

Applies only when `browserTesting` is true. Otherwise the whole gate is
`NOT_APPLICABLE`.

| # | Criterion | Type |
|---|---|---|
| PW-1 | Playwright MCP availability probed and the result recorded | MANDATORY |
| PW-2 | Application actually started and reachable | MANDATORY |
| PW-3 | Routes enumerated from the running app, not from source alone | MANDATORY |
| PW-4 | Every acceptance criterion with a UI surface has a browser scenario | MANDATORY |
| PW-5 | Authentication flow exercised in the browser | CONDITIONAL (`auth`) |
| PW-6 | Authorisation checked: at least one negative case per role | CONDITIONAL (`authzRoles`) |
| PW-7 | CRUD exercised through the real UI for each managed entity | CONDITIONAL (`database`) |
| PW-8 | Form validation exercised: valid, invalid, boundary, required | MANDATORY |
| PW-9 | Loading, empty and error states observed | MANDATORY |
| PW-10 | Navigation and deep-link/refresh behaviour verified | MANDATORY |
| PW-11 | Responsive layouts checked at every viewport class in the matrix — not only at the breakpoint boundaries | CONDITIONAL (`responsive`) |
| PW-11a | Every primary screen exercised in **landscape** as well as portrait, at phone and tablet dimensions | CONDITIONAL (`responsive`) |
| PW-11b | No horizontal page scroll at any supported width, measured not eyeballed | CONDITIONAL (`responsive`) |
| PW-11c | Collapsed navigation opens, operates and closes below the navigation breakpoint | CONDITIONAL (`responsive`) |
| PW-11d | Modal/dialog actions reachable in short landscape; focused form field and submit control visible with the keyboard open | CONDITIONAL (`responsive`) |
| PW-11e | `evidence/playwright/responsive-matrix.md` complete: a cell per screen × viewport × orientation, each with an artefact; no cell inferred from another | CONDITIONAL (`responsive`) |
| PW-12 | Screenshot captured for every scenario | MANDATORY |
| PW-13 | `evidence/playwright/results.json` conforms to `factory/schemas/test-report.schema.json` | MANDATORY |
| PW-14 | Zero `CRITICAL` or `HIGH` browser defects open | MANDATORY |
| PW-15 | No scenario is `PASS` without a corresponding MCP execution record | MANDATORY |

**If Playwright MCP is unavailable:** every scenario is `BLOCKED`, the gate
result is `FAIL`, and `releaseReadiness` cannot be `READY`. The reason is
recorded in `evidence/playwright/mcp-availability.md`. This gate is never
waived by an agent.

---

## GATE-SEC — Security

Phase: `12-security`

| # | Criterion | Type |
|---|---|---|
| SEC-1 | `docs/security.md` exists | MANDATORY |
| SEC-2 | No secret, key or credential committed anywhere in the tree | MANDATORY |
| SEC-3 | Authentication reviewed: password storage, session/JWT handling, expiry, logout | CONDITIONAL (`auth`) |
| SEC-4 | Authorisation reviewed: every protected endpoint enforces server-side checks | CONDITIONAL (`authzRoles`) |
| SEC-5 | Input validation and injection risks reviewed (SQL/NoSQL/command/template) | CONDITIONAL (`backend`) |
| SEC-6 | XSS, CSRF and CORS reviewed | CONDITIONAL (`web`) |
| SEC-7 | File upload handling reviewed: type, size, path, storage location | CONDITIONAL (`fileUpload`) |
| SEC-8 | Dependency vulnerability scan executed; output recorded | MANDATORY |
| SEC-9 | Sensitive data exposure in logs, errors and API responses reviewed | MANDATORY |
| SEC-10 | Insecure defaults removed (debug mode, default credentials, permissive CORS) | MANDATORY |
| SEC-11 | Zero unresolved `CRITICAL`/`HIGH` findings | MANDATORY |
| SEC-12 | `evidence/security/security-report.md` exists | MANDATORY |

---

## GATE-PERF — Performance

Phase: `13-performance`

| # | Criterion | Type |
|---|---|---|
| PERF-1 | Critical user journeys measured, not estimated | MANDATORY |
| PERF-2 | No N+1 query pattern on a listed path | CONDITIONAL (`database`) |
| PERF-3 | List endpoints paginated | CONDITIONAL (`api`) |
| PERF-4 | Bundle size recorded and justified | CONDITIONAL (`web`) |
| PERF-5 | No redundant duplicate requests on load | CONDITIONAL (`web` or `mobile`) |
| PERF-6 | Startup time recorded | CONDITIONAL (`mobile`) |
| PERF-7 | Findings above the declared budget are fixed or explicitly accepted | MANDATORY |
| PERF-8 | `evidence/performance/` contains the measurements | MANDATORY |

---

## GATE-REG — Regression

Phase: `11-regression` (and re-run before release)

| # | Criterion | Type |
|---|---|---|
| REG-1 | Full suite re-executed after the last code change | MANDATORY |
| REG-2 | Every previously `COMPLETED` feature re-verified | MANDATORY |
| REG-3 | Every fixed defect has a test that fails before the fix and passes after | MANDATORY |
| REG-4 | Browser regression pack re-run | CONDITIONAL (`browserTesting`) |
| REG-5 | No previously passing scenario now fails | MANDATORY |
| REG-6 | `evidence/regression/final-regression-report.md` exists | MANDATORY |

---

## GATE-REL — Release

Phase: `14-release`

| # | Criterion | Type |
|---|---|---|
| REL-1 | All prior mandatory gates `PASS` (or user-`WAIVED`) | MANDATORY |
| REL-2 | Every feature is `COMPLETED` or explicitly deferred and listed | MANDATORY |
| REL-3 | Zero open `CRITICAL`/`HIGH` defects | MANDATORY |
| REL-4 | Production build succeeds for every platform | MANDATORY |
| REL-5 | `docs/deployment.md` exists with environment variables documented | CONDITIONAL (`deployable`) |
| REL-6 | `.env.example` complete; no real secret present | MANDATORY |
| REL-7 | Migrations verified against a clean database | CONDITIONAL (`database`) |
| REL-8 | Health check / readiness endpoint exists | CONDITIONAL (`backend`) |
| REL-9 | Known limitations and risks documented | MANDATORY |
| REL-10 | Final report uses explicit statuses; no `NOT_TESTED` reported as `PASS` | MANDATORY |
| REL-11 | Evidence exists for every claim in the final report | MANDATORY |

---

## Gate ↔ phase map

| Phase | Gate |
|---|---|
| `00-discover` | — |
| `01-understand` | GATE-REQ |
| `02-plan` | GATE-ARCH |
| `03-select-agents` | — (validated by `workflow-validator`) |
| `04-generate-structure` | GATE-ARCH (re-check) |
| `05-implement` | GATE-IMPL (per feature) |
| `06-integrate` | GATE-INTG (per feature) |
| `07-test` | GATE-TEST |
| `08-playwright` | GATE-PW |
| `09-fix` | — (loop) |
| `10-retest` | GATE-TEST + GATE-PW re-evaluation |
| `11-regression` | GATE-REG |
| `12-security` | GATE-SEC |
| `13-performance` | GATE-PERF |
| `14-release` | GATE-REL |

---

## Waivers

A waiver record:

```json
{
  "gate": "GATE-PERF",
  "criterion": "PERF-4",
  "result": "WAIVED",
  "reason": "Bundle budget exceeded by 40KB due to required charting library.",
  "owner": "user",
  "grantedAtPhase": "13-performance",
  "expiresAtPhase": "14-release"
}
```

Agents may waive `ADVISORY` criteria only. `MANDATORY` criteria require the
user. GATE-PW-1, PW-15, SEC-2, SEC-11, REL-3, REL-10 and REL-11 are **never
waivable** — they are the honesty invariants.
