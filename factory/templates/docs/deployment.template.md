# {{PROJECT_NAME}} — Deployment

> Owner: `project-devops` · Generated only when the `deployable` capability is
> true. Describes what exists, not an aspiration.

## Environments

| Environment | Purpose | URL | Data | Who can deploy |
|---|---|---|---|---|

## Build

| Area | Command | Artefact | Verified |
|---|---|---|---|
| {{STACK_WEB}} | {{CMD_BUILD}} | | |
| {{STACK_BACKEND}} | | | |
| {{STACK_MOBILE}} | | | |

Evidence: `evidence/release/build-verification.md`

## Configuration

| Variable | Purpose | Required | Default | Secret |
|---|---|---|---|---|

Every variable appears in `.env.example` with a placeholder value.
`.env` is never committed. A secret is never given a real default here.

## Infrastructure

| Component | Technology | Notes |
|---|---|---|
| Hosting | {{STACK_INFRASTRUCTURE}} | |
| Database | {{STACK_DATABASE}} | |
| Storage | | |
| Cache / queue | | |
| TLS | | |

<!-- OMIT IF: NOT database -->
## Migrations

Applied with {{CMD_MIGRATE}}, before the new application version starts.
Rollback procedure and its tested status are recorded here.

## Deployment procedure

1. 
2. 
3. 

Steps are written so a person who has not read this document can follow them.

## Rollback

| Aspect | Value |
|---|---|
| Trigger | |
| Procedure | |
| Data implications | |
| Tested | |

An untested rollback is recorded as `NOT_TESTED`, not assumed to work.

## Health and observability

| Aspect | Endpoint / tool | Configured |
|---|---|---|
| Health check | | |
| Logs | | |
| Errors | | |
| Metrics | | |

## Backup

| Aspect | Value |
|---|---|
| What is backed up | |
| Frequency | |
| Retention | |
| Restore tested | |

## Release checklist

| Item | Status | Evidence |
|---|---|---|
| Build succeeds from a clean checkout | | |
| Configuration documented | | |
| Migrations apply and roll back | | |
| Health check responds | | |
| Rollback rehearsed | | |
| No secret committed | | |
