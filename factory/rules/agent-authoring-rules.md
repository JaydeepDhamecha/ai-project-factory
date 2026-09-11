# Agent Authoring Rules

Every agent definition — factory agent or generated project agent — obeys this
contract. `workflow-validator` enforces it mechanically.

---

## 1. File format

```markdown
---
name: <kebab-case-id>
description: <one line; when the orchestrator should invoke this agent>
tools: <comma-separated tool list, or omit for all>
model: inherit
---

# <Agent Title>

## 1. Purpose
## 2. Responsibilities
## 3. Inputs
## 4. Required documents
## 5. Files it can modify
## 6. Outputs
## 7. Validation
## 8. Completion criteria
## 9. Failure handling
```

All nine numbered sections are mandatory and must appear in this order with
these exact headings. A missing or reordered section is a validation failure.

Generated agents additionally carry:

```yaml
generated_from: factory/templates/agents/<template>.md
generated_at: <ISO-8601>
capability_condition: <the expression that selected this agent>
```

---

## 2. Section requirements

**Purpose** — one paragraph. What this agent is for and, equally important,
what it is *not* for.

**Responsibilities** — a numbered list of concrete actions. Each is observable
and checkable. "Understand the domain" is not a responsibility; "produce
`docs/requirements.md` with a cited requirement per feature" is.

**Inputs** — every file, state key and prior-agent output consumed. If an input
is missing at run time, the agent reports `BLOCKED`; it does not proceed on
guesswork.

**Required documents** — the subset of inputs that must exist before the agent
may start. This is the agent's own precondition gate.

**Files it can modify** — explicit allow-list of paths and globs, plus an
explicit deny-list where confusion is likely. An agent that writes outside its
scope is a protocol violation.

**Outputs** — every artefact produced, with its exact path, plus the evidence
path and the state keys updated.

**Validation** — the commands or checks the agent runs on its own output before
reporting. Must be executable, not aspirational.

**Completion criteria** — the conditions under which the agent may report
`COMPLETED`, and the gate that will be evaluated afterwards.

**Failure handling** — what the agent does on each failure class: retry policy,
what it reports, what it must never do (typically: never fabricate, never mark
`PASS`, never silently narrow scope).

---

## 3. Universal constraints

Every agent, without exception:

1. Reads `CLAUDE.md` and `factory/rules/status-vocabulary.md` before acting.
2. Uses only the canonical status vocabulary.
3. Reports outcomes to the orchestrator; never escalates directly to the user.
4. Never writes to `.project/state/` directly — that is `project-state`'s job.
5. Never changes `currentPhase` — that is the orchestrator's job.
6. Never edits anything under `input/`.
7. Never claims execution that did not happen.
8. Records evidence at the declared path, from real output.
9. Stops and reports `BLOCKED` rather than inventing a missing input.
10. Never marks its own work `COMPLETED` when its self-validation failed.

---

## 4. Template placeholders

Templates in `factory/templates/agents/` and `factory/templates/docs/` use
`{{DOUBLE_BRACE}}` placeholders. Every placeholder in use must appear in one
of the two tables below — `scripts/validate-factory.sh` §11 enforces it.

### 4.1 Manifest-resolved

Substituted by `agent-generator` from `.project/project.json`, resolving in
this order: explicit `commands` and `paths` entries, then `stack` defaults,
then `NOT_APPLICABLE`.

| Placeholder | Substituted with |
|---|---|
| `{{PROJECT_NAME}}` | manifest `name` |
| `{{PROJECT_TYPE}}` | manifest `projectType` |
| `{{PLATFORMS}}` | manifest `platforms`, comma-separated |
| `{{PLATFORMS_MOBILE}}` | the mobile subset (`ios`, `android`), else `NOT_APPLICABLE` |
| `{{CAPABILITIES}}` | the capability flags that are true |
| `{{CAP_<FLAG>}}` | one capability flag as `true`/`false`. In use: `CAP_WEB`, `CAP_MOBILE`, `CAP_BACKEND`, `CAP_DATABASE`, `CAP_API`, `CAP_AUTH`, `CAP_AUTHZ`, `CAP_OFFLINE`, `CAP_BROWSER`, `CAP_RESPONSIVE`, `CAP_FILEUPLOAD`, `CAP_MULTITENANT`, `CAP_EXISTING` |
| `{{STACK_<AREA>}}` | chosen technology for that area — `WEB`, `MOBILE`, `BACKEND`, `DATABASE`, `INFRASTRUCTURE` |
| `{{PATH_<AREA>}}` | source root for that area — `WEB`, `MOBILE`, `BACKEND`, `DATABASE` |
| `{{CMD_INSTALL}}` `{{CMD_DEV}}` `{{CMD_BUILD}}` `{{CMD_TEST}}` `{{CMD_LINT}}` `{{CMD_TYPECHECK}}` `{{CMD_MIGRATE}}` | resolved project commands |
| `{{APP_URL}}` | local dev URL |
| `{{BREAKPOINTS}}` | responsive breakpoints |
| `{{ORIENTATIONS}}` | supported orientations, from manifest `orientations`; default `portrait, landscape` |
| `{{VIEWPORT_MATRIX}}` | the viewport classes actually tested — manifest `breakpoints` expanded to width × height per orientation, defaulting to the matrix in `factory/rules/responsive-rules.md` §2 |
| `{{DOC_LIST}}` | the documents this project generates |
| `{{AGENT_SCOPE}}` | write scope for a multi-instance agent |
| `{{AGENT_VARIANT}}` | variant suffix for a multi-instance agent, e.g. `admin` |
| `{{AGENT_VARIANT_LABEL}}` | human label for that variant, e.g. `Admin portal` |
| `{{GENERATED_AT}}` | ISO-8601 timestamp of generation |

A placeholder with no resolvable value is replaced with `NOT_APPLICABLE` and
the surrounding clause is marked accordingly — never left blank and never
guessed. A command that does not exist yet is `TBD`; the generator re-runs
after the technology phase rather than inventing one.

### 4.2 Exemplar

These mark the *shape* of an entry rather than a value. The generator leaves
them in place; the agent that owns the document replaces each with real
content as it writes. An exemplar surviving into a document marked `COMPLETED`
is a defect, caught by the owning agent's §7 validation.

| Placeholder | Marks |
|---|---|
| `{{FEATURE_AREA}}` | a functional grouping heading |
| `{{FEATURE_SLUG}}` | a feature id slug |
| `{{FEATURE_STEPS}}` | the vertical-slice steps this project uses |
| `{{REQUIREMENT_TITLE}}` | a requirement heading |
| `{{ROLE}}` | a user-role heading |
| `{{ROLE_COLUMNS}}` | one table column per role |
| `{{ONE_PARAGRAPH_PLAIN_LANGUAGE}}` | a prose summary |
| `{{ONE_LINE_WHEN_TO_INVOKE}}` | an agent's `description` frontmatter |
| `{{AGENT_TITLE}}` | an agent's H1 |
| `{{TEMPLATE_ID}}` `{{CONDITION}}` `{{PLACEHOLDER}}` | used inside `_TEMPLATE.md` only |

---

## 5. Write-scope discipline

| Agent class | May write | Must not write |
|---|---|---|
| Document agents | their `docs/*.md`, their `evidence/<phase>/` | source code |
| Implementation agents | their platform tree, their tests | other platforms, docs owned by others |
| Test agents | test files, `evidence/<phase>/` | product source code |
| `bug-fixer` | any product source, `evidence/qa/defects/` | tests, to make them pass falsely |
| `reviewer` | `evidence/*/review-*.md` | anything else |

A test agent that finds a defect hands it to `bug-fixer`. A bug-fixer that
wants to weaken a test must instead prove the test was wrong, and record that
argument in the defect file.

---

## 6. Definition-of-done reference

Every agent's completion criteria must reference the applicable clauses of
`factory/rules/definition-of-done.md` and the gate it feeds in
`factory/rules/quality-gates.md`. An agent with no gate linkage is a
validation failure.
