# {{PROJECT_NAME}} — Database Schema

> Owner: `project-database` · Generated only when the `database` capability is
> true. Engine: {{STACK_DATABASE}}

## Conventions

| Aspect | Convention |
|---|---|
| Table naming | |
| Primary keys | |
| Timestamps | |
| Soft delete | |
| Enums | |

## Entities

### <Entity>

| Column | Type | Null | Default | Constraint | Source |
|---|---|---|---|---|---|

Indexes:

| Name | Columns | Type | Why |
|---|---|---|---|

An index with no stated reason is removed. Indexes are added for a known
access pattern, not in case.

## Relationships

| From | To | Cardinality | On delete | Enforced by |
|---|---|---|---|---|

## Constraints and invariants

| Invariant | Enforced where | Rationale |
|---|---|---|

State whether each invariant is enforced by the database, the application, or
both. "Both" is the honest answer more often than teams admit; "application
only" is a risk worth naming.

<!-- OMIT IF: NOT multiTenant -->
## Tenant isolation

Which column carries the tenant boundary, and what stops a query omitting it.

## Migrations

| Id | Description | Applied | Reversible | Evidence |
|---|---|---|---|---|

Migration command: {{CMD_MIGRATE}}
Evidence: `evidence/database/migration-<NN>.log`

## Seed and fixture data

| Dataset | Purpose | Environment | Contains real data |
|---|---|---|---|

No production or personal data is used as a fixture.

## Verification

| Check | Method | Result | Evidence |
|---|---|---|---|
| Schema matches this document | | | `evidence/database/schema-verification.md` |
| Migrations apply cleanly | | | |
| Migrations roll back | | | |
| Constraints reject bad data | | | |

A row is `PASS` only when the command actually ran.
