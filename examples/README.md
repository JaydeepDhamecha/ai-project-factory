# Worked Examples

Four project shapes, each with the description a user would write and the
manifest the factory is expected to produce from it.

They exist so you can see the factory's *selection* behaviour without running
it — in particular what it decides **not** to build, which is the part that is
easy to get wrong and hard to notice.

| Example | Type | Agents | Rejected | Docs | Skipped |
|---|---|---|---|---|---|
| `web-only/` | `web-only` | 16 | 6 | 16 | 3 |
| `web-backend-database/` | `web-backend-database` | 20 | 2 | 18 | 1 |
| `web-mobile-backend/` | `web-mobile-backend` | 22 | 0 | 19 | 0 |
| `api-only/` | `api-only` | 16 | 6 | 17 | 2 |

Each directory holds:

| File | |
|---|---|
| `project-description.md` | what the user supplies, in the shape of `factory/templates/project/project-description.template.md` |
| `expected-manifest.json` | the manifest the factory should produce, conforming to `factory/schemas/project.schema.json` |

## What to look at

**`web-only`** — no `database`, `api`, `backend`, `mobile` or `integration`
agent, and no `database-schema.md` or `api-contract.md`. Storage is browser
storage, which is not a database in the sense that selects a database agent.
Every rejection carries its condition in `rejectedAgents`.

**`api-only`** — no `designer`, `web`, `playwright` or `integration` agent.
GATE-PW is `NOT_APPLICABLE`, recorded rather than omitted, and contract tests
carry the verification burden.

**`web-mobile-backend`** — the full roster. `integration` is derived from
having more than one surface, and `offline-sync` from the offline
requirement. Browser testing covers the web surface only; the mobile surface
is verified separately, and never by Playwright.

**`web-backend-database`** — the common shape. Two roles make `authzRoles`
true, which is what pulls the authorisation matrix into
`docs/security.md`.

## Using one

```bash
cp examples/web-only/project-description.md input/project-description.md
```

Then run `/start-project`. The manifest the factory produces should match
`expected-manifest.json` in its capabilities, roster and document set — the
stack and commands may legitimately differ, since those are choices the
factory justifies rather than facts it derives.

These are illustrations, not fixtures. The descriptions are invented products
used to exercise the selection logic; nothing here is a real client or a real
requirement.
