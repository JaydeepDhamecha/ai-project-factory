# WorkHub cross-surface integration suite

Owner: `project-integration`. Phase `06-integrate`.

These scripts drive the **running** services. They are not unit tests and they
do not mock the other side of any seam. Run them with Django on `:8000` and,
for the client observations, Vite on `:5173` and an Android emulator on Metro.

```
python3 integration/probe_authz.py             # roles, scopes, error envelope
python3 integration/probe_contract.py          # pagination, shapes, collection scoping
python3 integration/probe_writes.py            # write-path authz; reverses every mutation
python3 integration/probe_auth_lifecycle.py    # obtain/attach/refresh/revoke/deactivate
python3 integration/probe_pagination_order.py  # page-walk order stability; scope-leak check
```

Each writes a transcript under `evidence/api/integration/`, named for this
run's own UTC time. **A transcript is never overwritten** (DEF-048): call sites
pass a date-free canonical name, `harness.dump()` stamps it, and it creates the
file with mode `"x"` — two runs inside the same second get `-2`, `-3` rather
than one of them losing its evidence. The invariant is guarded by

```
python3 integration/test_evidence_no_clobber.py   # no server needed
```

**Secrets.** `harness.py` reads the demo password from the seed command at run
time into memory and `redact()` scrubs it — plus every JWT — from every
transcript. No script writes a credential to disk. Verified:
`grep -rlF "$DEMO_PASSWORD" evidence/api/integration` returns nothing.

**Fixtures.** `probe_writes.py` and `probe_auth_lifecycle.py` mutate data. Both
reverse every mutation and re-assert the baseline (28 employees, 6 projects,
41 tasks, project 1 at 11 members) before exiting. Deletes are soft (PAS-021),
so row counts do not return to baseline even though visible counts do — that is
expected. Activity-log rows are append-only and are not reversed.

The web and mobile halves of the suite are driven interactively (Playwright MCP,
`adb` + `uiautomator`) and are recorded in
`evidence/api/integration/cross-client-consistency-20260911T1320Z.md` rather
than scripted here.
