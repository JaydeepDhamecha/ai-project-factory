# {{PROJECT_NAME}} — Offline and Synchronisation

> Owner: `project-offline-sync` · Generated only when the `offline` capability
> is true. Offline behaviour that is not specified here is not built.

## Scope

| Surface | Offline support | Rationale |
|---|---|---|

## Per-feature offline class

| Feature | Class | Reads offline | Writes offline | Conflict risk |
|---|---|---|---|---|

Class: `ONLINE_ONLY` · `OFFLINE_READ` · `OFFLINE_WRITE` · `OFFLINE_CAPABLE` ·
`SYNC_REQUIRED` · `NOT_APPLICABLE`. These mirror
`factory/schemas/features.schema.json`.

## Local storage

| Aspect | Decision |
|---|---|
| Mechanism | |
| What is cached | |
| What is never cached | |
| Encryption at rest | |
| Eviction policy | |
| Size budget | |

Credentials and personal data cached locally are named explicitly, with the
protection applied. "We cache everything" is not an acceptable entry.

## Sync model

| Aspect | Decision |
|---|---|
| Trigger | |
| Direction | |
| Batching | |
| Ordering guarantee | |
| Retry and backoff | |
| Partial failure | |

## Conflict resolution

| Scenario | Strategy | User visible | Rationale |
|---|---|---|---|

Strategies: last-write-wins, server-wins, client-wins, merge, prompt.
Last-write-wins is a decision with data-loss consequences and is justified
here or replaced.

## Queue semantics

| Aspect | Decision |
|---|---|
| Durability across restart | |
| Duplicate suppression | |
| Maximum age | |
| Poison entries | |

## User-visible states

| State | Indicator | Wording |
|---|---|---|
| Online | | |
| Offline | | |
| Pending sync | | |
| Sync failed | | |
| Conflict | | |

## Verification

| Scenario | Method | Result | Evidence |
|---|---|---|---|
| Go offline mid-session | | | `evidence/qa/offline/` |
| Write offline, reconnect | | | |
| Conflicting edits | | | |
| Restart while queued | | | |
| Extended offline period | | | |

Offline behaviour is verified by real interruption. Reasoning about the code
is not verification, and is recorded as `NOT_TESTED` if that is all that
happened.
