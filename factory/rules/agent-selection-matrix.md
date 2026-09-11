# Agent Selection Matrix

`agent-generator` reads the capability profile from `.project/project.json` and
instantiates exactly the templates whose condition is true. This file is the
authority; the generator must not select agents on intuition.

---

## 1. Capability flags

Produced by `discovery`, stored under `capabilities` in the manifest.

| Flag | True when |
|---|---|
| `web` | A browser-based UI is required |
| `adminPortal` | A separate admin/back-office UI is required |
| `mobile` | iOS and/or Android app required |
| `desktop` | Native desktop app required |
| `backend` | Server-side application logic required |
| `api` | A network API surface exists (implied by `backend` + any client) |
| `database` | Persistent structured storage required |
| `auth` | Users authenticate |
| `authzRoles` | More than one role/permission level |
| `offline` | Any client must work without connectivity |
| `realtime` | Push, websockets, live updates |
| `fileUpload` | Users upload files or media |
| `notifications` | Email, push or in-app notifications |
| `backgroundJobs` | Scheduled or queued work |
| `reporting` | Dashboards, analytics, exports |
| `payments` | Money movement |
| `i18n` | Multiple languages/locales |
| `multiTenant` | Data isolation between organisations |
| `responsive` | Derived: `web` OR `adminPortal` OR `mobile` OR `desktop` — a UI is responsive unless the user explicitly and citably requires a single fixed viewport |
| `browserTesting` | Derived: `web` OR `adminPortal` |
| `deployable` | The project is expected to be deployed, not just built |
| `existingCodebase` | The repository already contains product code |

Derived flags are computed, never asked for:

```
api            = backend AND (web OR mobile OR desktop OR adminPortal OR apiOnly)
browserTesting = web OR adminPortal
responsive     = web OR adminPortal OR mobile OR desktop
integration    = count(backend, web, mobile, desktop, adminPortal) >= 2
```

`responsive` is derived rather than asked because "should it work on a phone?"
is not a real question — a UI that only works at one width is broken, not
minimal. Setting it `false` requires an explicit user statement cited in
`docs/assumptions.md`. See `factory/rules/responsive-rules.md` §1.

---

## 2. Selection table

| Template | Condition | Notes |
|---|---|---|
| `product` | always | |
| `requirements` | always | |
| `planner` | always | |
| `architect` | always | |
| `technology` | always | |
| `designer` | `web OR mobile OR adminPortal OR desktop` | Skipped for API-only |
| `database` | `database` | |
| `api` | `api` | |
| `backend` | `backend` | |
| `web` | `web OR adminPortal` | Two instances if both, see §4 |
| `mobile` | `mobile` | |
| `integration` | `integration` (derived) | |
| `offline-sync` | `offline` | |
| `qa` | always | |
| `playwright` | `browserTesting` | |
| `bug-fixer` | always | |
| `regression` | always | |
| `security` | always | |
| `performance` | `backend OR web OR mobile OR desktop` | |
| `devops` | `deployable` | |
| `reviewer` | always | |
| `release` | always | |

---

## 3. Worked project types

### Web only (static/SPA, no server)
```
capabilities: web, responsive, browserTesting, deployable
agents: product, requirements, planner, architect, technology, designer,
        web, qa, playwright, bug-fixer, regression, security, performance,
        devops, reviewer, release
NOT generated: database, api, backend, mobile, integration, offline-sync
docs skipped: database-schema.md, api-contract.md, offline-sync.md
```

### Web + Backend + Database
```
capabilities: web, backend, database, api, auth, authzRoles, responsive,
              browserTesting, integration, deployable
agents: + database, api, backend, integration
docs: full set minus mobile/offline
```

### Mobile only
```
capabilities: mobile, deployable
agents: product, requirements, planner, architect, technology, designer,
        mobile, qa, bug-fixer, regression, security, performance, devops,
        reviewer, release
NOT generated: web, playwright, backend, database, integration
GATE-PW: NOT_APPLICABLE — recorded explicitly, not silently omitted
```

### Web + Mobile + Backend
```
capabilities: web, mobile, backend, api, database, auth, authzRoles,
              integration, browserTesting, deployable
agents: near-full set; integration is mandatory
extra: mobile testing requirements, cross-client domain consistency checks
```

### API only
```
capabilities: backend, api, database, auth, deployable
agents: product, requirements, planner, architect, technology, database, api,
        backend, qa, bug-fixer, regression, security, performance, devops,
        reviewer, release
NOT generated: designer, web, mobile, playwright, integration
GATE-PW: NOT_APPLICABLE. Contract tests carry the verification burden.
```

### Admin portal (on an existing backend)
```
capabilities: adminPortal, web, api, auth, authzRoles, browserTesting,
              existingCodebase
agents: + integration (portal ↔ existing API)
note: discovery must read the existing API before the contract is written;
      the existing contract is source-of-truth level 4.
```

---

## 4. Multiple instances of one template

When a project needs two distinct surfaces from one template (for example a
customer web app *and* an admin portal), the generator emits two agents with
disambiguated ids:

```
project-web-customer.md    scope: apps/customer
project-web-admin.md       scope: apps/admin
```

Each declares its own write scope. The manifest records both ids.

---

## 5. Document selection

This file governs **agents**. Documents are governed by the selection table in
`factory/templates/docs/README.md`, which lists every template, the condition
that generates it, and its owning agent. The two are read together: an agent
that owns a document must be selected whenever that document is generated, and
`workflow-validator` checks that pairing.

---

## 6. Rules for the generator

1. Never generate an agent whose condition is false.
2. Never omit an agent whose condition is true — if it cannot be generated,
   that is a blocker, not a silent skip.
3. Record every selection **and** every rejection with the reason in
   `evidence/discovery/agent-selection.md`. The rejections matter: they are how
   a reader confirms the factory did not simply forget.
4. Write the resulting ids to `selectedAgents` in the manifest.
5. Hand the roster to `workflow-validator` before the orchestrator uses it.
