# {{PROJECT_NAME}} — Architecture

> Owner: `project-architect` · Describes what is being built, not what could
> be built. Every component here maps to a requirement.

## Context

What the system is, what sits outside it, and what crosses the boundary.

| External party | Direction | What crosses | Protocol |
|---|---|---|---|

## Components

| Component | Responsibility | Area | Depends on | Requirements |
|---|---|---|---|---|

Every component names at least one `REQ-NNN`. A component that satisfies no
requirement is scope creep and must be removed or justified.

## Structure

```
{{PATH_WEB}}
{{PATH_BACKEND}}
{{PATH_MOBILE}}
{{PATH_DATABASE}}
```

Only the paths this project actually uses appear.

<!-- OMIT IF: NOT backend -->
## Request lifecycle

Entry → validation → authorisation → domain logic → persistence → response.
State where each concern lives and what owns it.

<!-- OMIT IF: NOT auth -->
## Authentication and session model

| Aspect | Decision | Rationale |
|---|---|---|
| Mechanism | | |
| Token/session storage | | |
| Expiry and refresh | | |
| Logout semantics | | |

<!-- OMIT IF: NOT authzRoles -->
## Authorisation model

| Role | Scope | Enforced where |
|---|---|---|

Authorisation is enforced server-side. A UI that merely hides a control is
not an authorisation mechanism, and this document must not describe it as one.

<!-- OMIT IF: NOT integration -->
## Cross-surface consistency

How web, mobile and backend stay in agreement on domain rules, validation and
error semantics — and which one is authoritative when they diverge.

<!-- OMIT IF: NOT multiTenant -->
## Tenancy and isolation

Where the tenant boundary is enforced, and what prevents a query crossing it.

## Error handling

| Class | Surfaced as | Logged | Retried |
|---|---|---|---|

## Decision records

| Id | Decision | Status | Evidence |
|---|---|---|---|
| ADR-001 | | | `evidence/architecture/adr/ADR-001-<slug>.md` |

## Requirement coverage

| REQ | Component(s) |
|---|---|

Unmapped requirements are listed explicitly. Silence is not coverage.
