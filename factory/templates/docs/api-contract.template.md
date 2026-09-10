# {{PROJECT_NAME}} — API Contract

> Owner: `project-api` · The contract is authoritative for both server and
> clients. A client that needs something absent here changes the contract
> first — it does not improvise against an undocumented shape.

## Conventions

| Aspect | Convention |
|---|---|
| Base URL | |
| Versioning | |
| Content type | |
| Naming | |
| Pagination | |
| Filtering / sorting | |
| Idempotency | |

<!-- OMIT IF: NOT auth -->
## Authentication

| Aspect | Value |
|---|---|
| Scheme | |
| Header | |
| Token lifetime | |
| Refresh | |
| Failure response | |

## Errors

| HTTP | Meaning | Body shape | When |
|---|---|---|---|

One error shape for the whole API. Endpoint-specific error bodies are a
defect, not a feature.

## Endpoints

### `<METHOD> /path`

| Field | Value |
|---|---|
| Purpose | |
| Requirement | REQ-NNN |
| Auth required | |
| Roles permitted | |
| Idempotent | |

Request:

| Param | In | Type | Required | Validation |
|---|---|---|---|---|

Responses:

| Status | Meaning | Body |
|---|---|---|

Verification:

| Check | Result | Evidence |
|---|---|---|
| Contract test | | `evidence/api/contract-conformance.md` |
| Transcript captured | | `evidence/api/<NN>-<slug>.txt` |

<!-- OMIT IF: NOT realtime -->
## Realtime channels

| Channel | Event | Payload | Who receives it | Auth |
|---|---|---|---|---|

<!-- OMIT IF: NOT fileUpload -->
## File upload

| Aspect | Value |
|---|---|
| Endpoint | |
| Max size | |
| Accepted types | |
| Validation | |
| Storage | |
| Access control | |

Type is validated by content, not by file extension alone.

## Coverage

| REQ | Endpoint(s) | Contract tested |
|---|---|---|

Every API-bearing requirement appears. Gaps are listed, not omitted.
