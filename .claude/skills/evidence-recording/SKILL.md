---
name: evidence-recording
description: How to capture, name, index and reference evidence so that every claim the factory makes is checkable. Use whenever an agent runs a command, a test, a scan or a browser scenario.
---

# Evidence Recording

## 1. Capture real output

Evidence is what a command produced, not what an agent expected it to produce.

```bash
mkdir -p evidence/implementation/f01-authentication
npm run build 2>&1 | tee evidence/implementation/f01-authentication/01-build.log
echo "exit=${PIPESTATUS[0]}" >> evidence/implementation/f01-authentication/01-build.log
```

Always record the exit code. A log without one cannot be audited.

## 2. Where it goes

`factory/rules/evidence-rules.md` §3 defines the directories. Per-feature
evidence nests one level under the phase directory.

## 3. Naming

`<NN>-<slug>.<ext>` — ordered, readable:

```
evidence/implementation/f01-authentication/
  01-lint.log
  02-typecheck.log
  03-build.log
  04-unit.log
  index.md
```

## 4. Index every directory

`index.md` in each evidence directory:

```markdown
# f01-authentication — implementation evidence
Agent: project-backend, project-web
Phase: 05-implement
Run:   2026-09-08T12:04Z → 12:19Z

| # | Artefact | Command | Exit | Result |
|---|----------|---------|------|--------|
| 01 | 01-lint.log | npm run lint | 0 | PASS |
| 02 | 02-typecheck.log | npm run typecheck | 0 | PASS |
| 03 | 03-build.log | npm run build | 0 | PASS |
| 04 | 04-unit.log | npm test | 0 | PASS 31/31 |
```

## 5. Structured results

Test runs also produce a JSON report conforming to
`factory/schemas/test-report.schema.json`. The markdown is for humans; the JSON
is what gates and audits read.

## 6. Register it

Ask `project-state` to add each artefact to `evidenceIndex` and journal
`evidence_written`. Unregistered evidence is invisible to `/status` and
`/audit`.

## 7. Recording absence

When something could not run, write the absence down — see
`factory/rules/evidence-rules.md` §6. A gate criterion whose evidence is a
clear `BLOCKED` record is auditable; a criterion with nothing at all is a
validation failure.

## 8. Never

- Compose an evidence file by hand describing what a command would print.
- Reuse an artefact from an earlier run as though it were current.
- Delete evidence that makes a report look worse. Mark it superseded instead.
- Claim an evidence path that does not exist — `/audit` checks every one.
