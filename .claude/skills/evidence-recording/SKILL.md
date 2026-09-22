---
name: evidence-recording
description: How to capture, name, index and reference evidence so that every claim the factory makes is checkable. Use whenever an agent runs a command, a test, a scan or a browser scenario.
---

# Evidence Recording

## 1. Capture real output — write it all, read a slice

Evidence is what a command produced, not what an agent expected it to produce.
Capture is therefore total: the whole of stdout and stderr goes to disk, always.

**Reading it back is a separate decision, and the answer is almost always "a
bounded slice".** Write the raw artefact, then read only enough to describe it
honestly.

```bash
mkdir -p evidence/implementation/f01-authentication
D=evidence/implementation/f01-authentication

# 1. Capture everything — redirect, never `tee`.
npm run build > "$D/01-build.raw.log" 2>&1
echo "exit=$?" >> "$D/01-build.raw.log"

# 2. Read a bounded slice — never the whole file.
tail -n 30 "$D/01-build.raw.log"
grep -cE '^(FAILED|ERROR)' "$D/01-build.raw.log"
```

**Never pipe command output through `tee`.** `tee` writes to the file *and* to
stdout, which puts the entire log into the agent's context. A test suite that
fails at setup can repeat one root cause hundreds of times; one such log in this
factory's history was 73,748 lines of which 2,472 were unique, and it bought
nothing that `tail` and `grep -c` would not have shown.

Always record the exit code. A log without one cannot be audited.

Large artefacts are named `<NN>-<slug>.raw.log`. The `.raw` infix is a contract:
it is written by the command, it is never edited, and **no agent reads it whole.**
What downstream agents read is the index of §4, which summarises it and cites its
path.

## 2. Where it goes

`factory/rules/evidence-rules.md` §3 defines the directories. Per-feature
evidence nests one level under the phase directory.

## 3. Naming

`<NN>-<slug>.<ext>` — ordered, readable:

```
evidence/implementation/f01-authentication/
  01-lint.raw.log
  02-typecheck.raw.log
  03-build.raw.log
  04-unit.raw.log
  index.md
```

## 4. Index every directory

`index.md` is the **readable face** of the directory. Every artefact it lists is
summarised here and read here; the `.raw.log` beside it is proof, not reading
material.

```markdown
# f01-authentication — implementation evidence
Agent: project-backend, project-web
Phase: 05-implement
Run:   2026-09-08T12:04Z → 12:19Z

| # | Artefact | Command | Exit | Counts | Result |
|---|----------|---------|------|--------|--------|
| 01 | 01-lint.raw.log | npm run lint | 0 | 0 errors, 0 warnings | PASS |
| 02 | 02-typecheck.raw.log | npm run typecheck | 0 | 0 errors | PASS |
| 03 | 03-build.raw.log | npm run build | 0 | — | PASS |
| 04 | 04-unit.raw.log | npm test | 0 | 31 passed, 0 failed | PASS 31/31 |
```

Each row carries the artefact path, the command, the **exit code**, the **counts
the runner reported**, and the verdict. When anything failed, add a **distinct**
failure list beneath the table — the unique causes, not every occurrence:

```markdown
## Failures — 04-unit.raw.log

603 errors, 0 passed. **1 distinct cause:**

- `CREATE DATABASE test_workhub_od` — permission denied at test-db setup,
  which aborted every test before it ran. 603 identical `ERROR at setup`.

Raw: `./04-unit.raw.log` (73,748 lines)
```

Three rules make this honest rather than lossy:

1. **Derive, never compose.** Every number in the index comes from the raw file
   — `grep -c`, the runner's own summary line, the recorded exit code. An index
   describing output that was not produced is the unrecoverable error of
   `factory/rules/evidence-rules.md` §2.
2. **Cite the artefact, and make sure it exists.** Every row names a path on
   disk. `/audit` checks every one.
3. **Collapse repetition, never severity.** Summarising 603 identical errors as
   one distinct cause is accurate. Summarising 603 errors as "some failures" is
   not, and a `FAIL` never softens into a `PASS` on its way into the index.

**Downstream agents read this index, not the raw logs.** The raw file stays on
disk permanently and is opened only when a discrepancy needs settling — by
`/audit`, or by `project-reviewer`, whose job is precisely to distrust the
summary.

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
