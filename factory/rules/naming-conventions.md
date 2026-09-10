# Naming Conventions

Consistency here is what makes cross-references checkable by a script.

| Thing | Convention | Example |
|---|---|---|
| Factory agent file | `.claude/agents/<id>.md` | `orchestrator.md` |
| Generated agent file | `.claude/agents/project-<template>[-<variant>].md` | `project-web-admin.md` |
| Agent id | kebab-case, matches filename stem | `project-playwright` |
| Agent template | `factory/templates/agents/<template>.md` | `backend.md` |
| Command | `.claude/commands/<name>.md` → `/<name>` | `start-project.md` |
| Skill | `.claude/skills/<name>/SKILL.md` | `playwright-mcp/SKILL.md` |
| Doc template | `factory/templates/docs/<doc>.template.md` | `PRD.template.md` |
| Generated doc | `docs/<doc>.md` | `docs/api-contract.md` |
| Schema | `factory/schemas/<thing>.schema.json` | `project.schema.json` |
| Phase id | `<NN>-<verb>` | `08-playwright` |
| Gate id | `GATE-<AREA>` | `GATE-PW` |
| Gate criterion | `<AREA>-<n>` | `PW-13` |
| Feature id | `f<NN>-<slug>` | `f01-authentication` |
| Requirement id | `REQ-<NNN>` | `REQ-014` |
| Acceptance criterion | `AC-<REQ>-<n>` | `AC-014-2` |
| User story | `US-<NNN>` | `US-007` |
| Defect id | `BUG-<NNN>` | `BUG-021` |
| Security finding | `SEC-F-<NNN>` | `SEC-F-003` |
| Performance finding | `PERF-F-<NNN>` | `PERF-F-002` |
| Decision record | `ADR-<NNN>` | `ADR-005` |
| Test scenario | `<feature>-<NN>-<slug>` | `auth-03-invalid-password` |
| Evidence file | `<NN>-<slug>.<ext>` | `02-typecheck.log` |
| Blocker | `BLK-<NNN>` | `BLK-001` |

Ids are stable once assigned. When something is dropped, its id is retired,
never reused — traceability across a long run depends on it.
