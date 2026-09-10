# Definition of Done

Applies to a **feature slice**. Every clause is either satisfied, or
`NOT_APPLICABLE` because the project's capability profile excludes it. A clause
is never simply skipped.

A feature moves to `COMPLETED` only when the orchestrator has checked this list
against real artefacts — not against an agent's claim.

---

## 1. Product

- [ ] Every requirement mapped to this feature is implemented.
- [ ] Every acceptance criterion is satisfied and individually verified.
- [ ] Scope creep excluded: nothing built that no requirement asked for.
- [ ] Assumptions made during implementation are recorded in `docs/assumptions.md`.

## 2. Backend — if `backend`

- [ ] Endpoints implemented per `docs/api-contract.md`.
- [ ] Server-side validation on every write path.
- [ ] Authorisation enforced server-side, not only in the UI.
- [ ] Error responses use the documented error format.
- [ ] Pagination, filtering and sorting where the contract specifies them.
- [ ] Unit tests pass.
- [ ] Integration tests pass.

## 3. Database — if `database`

- [ ] Schema matches `docs/database-schema.md`.
- [ ] Migration written, applied and verified on a clean database.
- [ ] Indexes and constraints present.
- [ ] Audit/timestamp fields populated.
- [ ] No destructive migration without an explicit, recorded decision.

## 4. API — if `api`

- [ ] Contract updated before the client consumed it.
- [ ] Request and response schemas verified against real traffic.
- [ ] Status codes correct.
- [ ] Contract tests pass.

## 5. Web — if `web` or `adminPortal`

- [ ] UI implemented and consistent with `docs/design-system.md`.
- [ ] Matches the supplied visual reference where one exists, with deviations documented.
- [ ] Real API integration — no mock data on the production path.
- [ ] Loading state implemented and observed.
- [ ] Empty state implemented and observed.
- [ ] Error state implemented and observed.
- [ ] Form validation: required, invalid, boundary.
- [ ] Navigation, browser refresh and deep-link behaviour correct.
- [ ] Responsive behaviour verified at declared breakpoints — if `responsive`.
- [ ] Accessible: labels, focus order, keyboard operation of primary flows.
- [ ] **Playwright MCP browser validation executed and `PASS`.**

## 6. Mobile — if `mobile`

- [ ] Implemented for each required platform (iOS / Android).
- [ ] Real API integration.
- [ ] Loading, empty and error states.
- [ ] Navigation and back-behaviour correct.
- [ ] Permissions handled and denied-permission path tested.
- [ ] Session persistence across app restart.
- [ ] Network-failure behaviour.
- [ ] Offline behaviour and synchronisation — if `offline`.
- [ ] Simulator/emulator validation executed; real-device status stated honestly.

## 7. Integration — if ≥2 of {backend, web, mobile}

- [ ] End-to-end flow works across the platforms involved.
- [ ] Shared domain behaviour is consistent across clients.
- [ ] Auth token lifecycle works in every client.
- [ ] Failure propagation is correct: server error → client message.

## 8. Quality

- [ ] Formatter clean.
- [ ] Linter clean.
- [ ] Type check clean — if the stack is typed.
- [ ] Build succeeds for every affected platform.
- [ ] No placeholder, stub, mock or fake data on a production path.
- [ ] No `TODO`/`FIXME` on a release-blocking path.
- [ ] Dead code from this feature removed.

## 9. Testing

- [ ] Unit tests written and passing.
- [ ] Integration tests where applicable.
- [ ] Browser tests where applicable — actually executed.
- [ ] Each defect found in this feature has a regression test.
- [ ] Regression suite passes: this feature broke nothing earlier.
- [ ] No test disabled or deleted to achieve green.

## 10. Security

- [ ] Feature-level security review done.
- [ ] Access control verified with a negative test.
- [ ] Input validated and output encoded.
- [ ] No secret introduced into the repository.
- [ ] No sensitive data in logs or error responses.

## 11. Documentation

- [ ] `docs/development-status.md` updated.
- [ ] Any changed contract, schema or design document updated **in the same slice**.
- [ ] Decisions recorded in `.project/state/decisions.md`.

## 12. Evidence

- [ ] `evidence/implementation/<feature>/` — build, lint, type-check, unit output.
- [ ] `evidence/playwright/<feature>/` — screenshots and results — if `browserTesting`.
- [ ] `evidence/qa/<feature>/` — test output.
- [ ] `evidence/api/<feature>/` — request/response transcripts — if `api`.
- [ ] Every evidence file is real output, never composed by hand.

---

## The honesty clause

A feature is **not** done if any of the following is true:

- A required test was not executed but the feature is being reported as working.
- A browser check was inferred from reading code rather than driving a browser.
- A failing test was disabled, skipped or deleted rather than fixed.
- Evidence was written by an agent describing what it believes would happen.
- `NOT_TESTED` or `BLOCKED` was reported as `PASS`.

Any of these is a protocol violation. The orchestrator must revert the feature
to `IN_PROGRESS`, journal the violation, and re-run the affected step.

---

## Definition of Done — project level

The project is done when:

- [ ] Every planned feature is `COMPLETED`, or deferred and listed with a reason.
- [ ] Every mandatory gate is `PASS` or user-`WAIVED`.
- [ ] Full regression `PASS`.
- [ ] Zero open `CRITICAL`/`HIGH` defects or security findings.
- [ ] Production build succeeds everywhere.
- [ ] Deployment documentation complete — if `deployable`.
- [ ] Final report published with explicit statuses and evidence links.
