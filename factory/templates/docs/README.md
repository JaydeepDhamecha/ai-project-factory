# Document Templates

Instantiated by `agent-generator` into `docs/` — **only those the project's
capability profile requires**. Every skipped document is recorded in the
manifest's `skippedDocuments` with a reason.

| Template | Generated when | Owner agent |
|---|---|---|
| `project-overview.template.md` | always | `discovery` → `product` |
| `source-analysis.template.md` | always | `discovery` |
| `PRD.template.md` | always | `product` |
| `requirements.template.md` | always | `requirements` |
| `user-stories.template.md` | always | `requirements` |
| `acceptance-criteria.template.md` | always | `requirements` |
| `assumptions.template.md` | always | all (append-only) |
| `platform-requirements.template.md` | always | `architect` |
| `technology-stack.template.md` | always | `technology` |
| `architecture.template.md` | always | `architect` |
| `database-schema.template.md` | `database` | `database` |
| `api-contract.template.md` | `api` | `api` |
| `design-system.template.md` | `web`/`mobile`/`adminPortal`/`desktop` | `designer` |
| `offline-sync.template.md` | `offline` | `offline-sync` |
| `development-plan.template.md` | always | `planner` |
| `development-status.template.md` | always | `planner` → `orchestrator` |
| `testing-strategy.template.md` | always | `qa` |
| `security.template.md` | always | `security` |
| `deployment.template.md` | `deployable` | `devops` |

## Conventions

- `{{PLACEHOLDER}}` — substituted at generation; never left in a generated file.
- `<!-- OMIT IF: capability -->` — the whole section is dropped when that
  capability is false.
- Every id follows `factory/rules/naming-conventions.md`.
- Every extracted fact carries a source citation and a confidence level.
