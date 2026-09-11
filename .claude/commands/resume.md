---
description: Continue an interrupted project from persisted state. Never restarts from zero.
argument-hint: "[optional: phase or feature to resume at]"
---

# /resume

Continue where the factory left off. Optional target: **$ARGUMENTS**

## Execution contract

Like `/start-project`, this command **runs the lifecycle to completion**. It is
not a status report. You are authorised and required to use the Agent tool
(CLAUDE.md § 8); `project-*` agents generated in this session are adopted inline
rather than dispatched. Do not end your turn between phases. Yield only on an
escalation trigger from `factory/rules/source-of-truth.md` § 4, or at
`14-release`.

If you only want to see where things stand, that is `/status`.

## Preconditions

```bash
test -f .project/project.json || { echo "No project. Run /start-project."; exit 0; }
test -d .project/state || echo "WARNING: state directory missing"
```

## Steps

1. Invoke `project-state` and run the resume algorithm
   (`.claude/agents/project-state.md` § Resume algorithm).
2. Print the resume briefing so the user can see exactly what is being resumed.
3. Verify integrity before continuing:
   - state validates against its schema,
   - the journal tail agrees with `state.json`,
   - evidence for `COMPLETED` units exists.
   Repair or downgrade as the algorithm specifies, and journal it.
4. Adopt the `orchestrator` role and continue from the identified next step.
5. Continue the full lifecycle to completion — `/resume` is not a single step,
   it is "carry on to the end".

## Rules

- **Never re-run a `COMPLETED` step whose evidence is intact.**
- Never restart the project.
- If evidence is missing for a `COMPLETED` step, downgrade it to `IN_PROGRESS`,
  journal the reason, and redo that step only.
- If a blocker is open, check whether it is now resolved (credentials supplied,
  tool installed, question answered). If still open, report `BLOCKED` and state
  precisely what is needed — then complete any work that does not depend on it.
- If the user named a target in `$ARGUMENTS`, resume there, but first warn if
  that skips incomplete prerequisite phases.

## When there is nothing to resume

If every phase is `COMPLETED`, do not invent more work. Report the final status
and offer `/audit` or `/release`.
