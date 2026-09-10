---
name: project-{{TEMPLATE_ID}}
description: {{ONE_LINE_WHEN_TO_INVOKE}}
model: inherit
generated_from: factory/templates/agents/{{TEMPLATE_ID}}.md
generated_at: {{GENERATED_AT}}
capability_condition: {{CONDITION}}
---

# {{AGENT_TITLE}} — {{PROJECT_NAME}}

> Skeleton for new agent templates. Copy this file, keep all nine sections in
> this order, and register the new template in
> `factory/rules/agent-selection-matrix.md` §2.

## 1. Purpose

What this agent is for, in one paragraph — and explicitly what it is not for.

## 2. Responsibilities

Numbered, concrete, observable actions. Not "understand X"; "produce Y at path Z".

## 3. Inputs

Every file, state key and prior-agent output consumed.

## 4. Required documents

The subset of inputs that must exist before this agent may start. Missing one
means `BLOCKED`, never improvisation.

## 5. Files it can modify

Explicit allow-list of paths and globs, and an explicit deny-list.

## 6. Outputs

Every artefact produced, with its exact path, plus evidence paths and state keys.

## 7. Validation

Executable checks the agent runs on its own output before reporting.

## 8. Completion criteria

Conditions for reporting `COMPLETED`, and the gate this work feeds.

## 9. Failure handling

A table of failure classes → action, plus an explicit "never" list.
