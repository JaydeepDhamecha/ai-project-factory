# {{PROJECT_NAME}} — Security

> Owner: `project-security` · Scope is this application. Findings are recorded
> whether or not they are fixed; a finding with no fix carries an accepted-risk
> owner.

## Threat model

| Asset | Threat | Impact | Likelihood | Mitigation | Status |
|---|---|---|---|---|---|

<!-- OMIT IF: NOT auth -->
## Authentication

| Control | Requirement | Implemented | Verified | Evidence |
|---|---|---|---|---|
| Password storage | | | | |
| Credential transmission | | | | |
| Session expiry | | | | |
| Logout invalidation | | | | |
| Brute-force protection | | | | |
| Account enumeration resistance | | | | |

<!-- OMIT IF: NOT authzRoles -->
## Authorisation

| Resource | Action | {{ROLE_COLUMNS}} | Enforced server-side | Verified |
|---|---|---|---|---|

Every allow/deny is verified by an executed test. A matrix filled in by
reading the code is `NOT_TESTED`.

### Object-level access

Tested by attempting to access another user's records directly by id. This is
the most commonly missed check in generated applications, and it is mandatory.

## Input handling

| Vector | Control | Verified | Evidence |
|---|---|---|---|
| Injection (SQL/NoSQL/command) | | | |
| Cross-site scripting | | | |
| Cross-site request forgery | | | |
| Mass assignment | | | |
| Path traversal | | | |
| Unsafe deserialisation | | | |
| Server-side request forgery | | | |

<!-- OMIT IF: NOT fileUpload -->
## Upload handling

| Control | Requirement | Verified |
|---|---|---|
| Content-based type validation | | |
| Size limit | | |
| Stored outside the web root | | |
| Filename sanitisation | | |
| Access control on retrieval | | |

## Data protection

| Data class | Examples | At rest | In transit | Retention | Logged |
|---|---|---|---|---|---|

No secret, token or personal datum is written to a log, an error message, or
`evidence/`.

## Secrets

| Aspect | Rule |
|---|---|
| Storage | environment variables; `.env.example` is committed, `.env` never is |
| In source | forbidden |
| In evidence | forbidden — redact before capture |
| Rotation | |

## Dependencies

| Check | Command | Result | Evidence |
|---|---|---|---|
| Vulnerability audit | | | `evidence/security/dependency-scan.log` |

## Findings

| Id | Severity | Description | Status | Owner | Evidence |
|---|---|---|---|---|---|
| SEC-F-001 | | | | | |

Severity: `CRITICAL` · `HIGH` · `MEDIUM` · `LOW` · `INFO`.
Open `CRITICAL` or `HIGH` findings block release. An accepted risk names a
person, not a team.

## Not assessed

What this review did not cover, so nobody mistakes silence for a clean bill.
