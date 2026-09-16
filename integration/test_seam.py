"""Assertive cross-surface seam tests. Exits non-zero on any failure.

These are the invariants this phase established. They run against the LIVE
services; there is no mock anywhere in this file. Anything that could not be
executed is declared NOT_TESTED explicitly rather than asserted away.
"""
import json, sys
sys.path.insert(0, "/Volumes/DATA/Automatic Create project/integration")
from harness import *

PASSED, FAILED, SKIPPED = [], [], []

def check(name, got, want):
    (PASSED if got == want else FAILED).append((name, got, want))
    print(("  PASS  " if got == want else "  FAIL  ") + name +
          ("" if got == want else f"\n          got={got!r} want={want!r}"))

def skip(name, why):
    SKIPPED.append((name, why))
    print(f"  NOT_TESTED  {name}\n              {why}")

def st(m, p, role, body=None):
    return call(m, p, tok(role), body=body, note=f"{m} {p} as {role}")["status"]

def body(p, role):
    return call("GET", p, tok(role), note=f"GET {p} as {role}")["body"]

print("\n--- baseline fixtures ---")
a = tok("admin")
check("baseline employees == 28", body("/employees?limit=1", "admin")["count"], 28)
check("baseline projects == 6", body("/projects?limit=1&scope=all", "admin")["count"], 6)
check("baseline tasks == 41", body("/tasks?limit=1", "admin")["count"], 41)
check("baseline project 1 members == 11", len(body("/projects/1", "admin")["members"]), 11)

print("\n--- INTG-3 auth lifecycle ---")
check("login manager 200", call("POST", "/auth/login", body={"email": ACCOUNTS["manager"], "password": PASSWORD})["status"], 200)
check("login wrong password 401", call("POST", "/auth/login", body={"email": ACCOUNTS["admin"], "password": "nope"})["status"], 401)
check("login inactive user 401", call("POST", "/auth/login", body={"email": ACCOUNTS["inactive"], "password": PASSWORD})["status"], 401)
check("anonymous /projects 401", st("GET", "/projects", "anon"), 401)
check("malformed bearer 401", call("GET", "/auth/me", "garbage.token.x")["status"], 401)
r = call("POST", "/auth/login", body={"email": ACCOUNTS["admin"], "password": PASSWORD})["body"]
check("refresh with valid token 200", call("POST", "/auth/refresh", body={"refresh": r["refresh"]})["status"], 200)
check("refresh with garbage 401", call("POST", "/auth/refresh", body={"refresh": "x"})["status"], 401)
check("access token rejected as refresh 401", call("POST", "/auth/refresh", body={"refresh": r["access"]})["status"], 401)
skip("natural token expiry (24h access / 7d refresh)",
     "exceeds the run window; the service may not be restarted to shorten the lifetime")

print("\n--- INTG-1/INTG-2 report role gate and scoping (was D-1) ---")
for ep in ("/reports/tasks", "/reports/employees", "/reports/projects"):
    check(f"{ep} employee 403", st("GET", ep, "employee"), 403)
    check(f"{ep} outsider 403", st("GET", ep, "outsider"), 403)
    check(f"{ep} manager 200", st("GET", ep, "manager"), 200)
check("/reports/employees admin count 28", body("/reports/employees", "admin")["count"], 28)
check("/reports/employees manager count 26", body("/reports/employees", "manager")["count"], 26)
check("/reports/projects manager count 4", body("/reports/projects", "manager")["count"], 4)

print("\n--- pagination envelope on reports (was D-9 / C-3 / API-F-1) ---")
ENV = {"count", "limit", "offset", "next", "previous", "results"}
for ep in ("/reports/employees", "/reports/projects"):
    check(f"{ep} envelope complete", ENV <= set(body(ep, "admin").keys()), True)
    check(f"{ep}?limit=1 honoured", len(body(ep + "?limit=1", "admin")["results"]), 1)
    for q, lbl in (("?limit=0", "limit=0"), ("?limit=101", "limit=101"), ("?limit=abc", "limit=abc"),
                   ("?offset=-1", "offset=-1"), ("?offset=abc", "offset=abc")):
        check(f"{ep}{q} -> 400", st("GET", ep + q, "admin"), 400)
    check(f"{ep} offset past end -> 200 []", (st("GET", ep + "?offset=9999", "admin"),
          body(ep + "?offset=9999", "admin")["results"]), (200, []))
walked = []
for off in (0, 2, 4):
    walked += [x["id"] for x in body(f"/reports/projects?limit=2&offset={off}", "admin")["results"]]
check("/reports/projects page walk reconstructs the full list", walked,
      [x["id"] for x in body("/reports/projects?limit=100", "admin")["results"]])

print("\n--- INTG-1 object-level scoping (was D-4) ---")
check("GET /projects/9 as tarun 403", st("GET", "/projects/9", "manager"), 403)
check("GET /projects/9 as employee 403", st("GET", "/projects/9", "employee"), 403)
check("GET /projects/9/tasks as tarun 403", st("GET", "/projects/9/tasks", "manager"), 403)
check("GET /projects/1 as neha 403", st("GET", "/projects/1", "manager2"), 403)
check("GET /tasks/1 as outsider 403", st("GET", "/tasks/1", "outsider"), 403)
for s, want in (("", [1, 2, 3, 4]), ("&scope=owned", [1, 2, 3, 4]),
                ("&scope=member", [1, 2, 3, 4, 10]), ("&scope=all", [1, 2, 3, 4, 10])):
    check(f"tarun /projects{s or ' (default)'}",
          sorted(x["id"] for x in body(f"/projects?limit=100{s}", "manager")["results"]), want)
check("project 9 never visible to tarun in any scope",
      any(9 in sorted(x["id"] for x in body(f"/projects?limit=100{s}", "manager")["results"])
          for s in ("", "&scope=owned", "&scope=member", "&scope=all")), False)
for bad in ("bogus", "OWNED", "owned,member"):
    check(f"?scope={bad} -> 400", st("GET", f"/projects?scope={bad}", "manager"), 400)

print("\n--- INTG-1 owner-gating on writes (was D-5) ---")
d10 = body("/projects/10", "admin")["description"]
check("PATCH /projects/10 as member-not-owner 403",
      st("PATCH", "/projects/10", "manager", {"description": d10}), 403)
check("POST /projects/10/members as member-not-owner 403",
      st("POST", "/projects/10/members", "manager", {"employee_id": 3}), 403)
d4 = body("/projects/4", "manager")["description"]
check("PATCH /projects/4 as owner 200", st("PATCH", "/projects/4", "manager", {"description": d4}), 200)
check("PATCH /projects/4 as employee 403", st("PATCH", "/projects/4", "employee", {"description": "zz"}), 403)

print("\n--- INTG-1 membership error codes (was D-8) ---")
members = [m["id"] for m in body("/projects/4", "manager")["members"]]
check("duplicate member add -> 409",
      st("POST", "/projects/4/members", "manager", {"employee_id": members[0]}), 409)
nonmember = next(i for i in range(3, 40) if i not in members)
check("remove non-member -> 404", st("DELETE", f"/projects/4/members/{nonmember}", "manager"), 404)

print("\n--- INTG-1 task required fields and membership (was D-6 / D-7) ---")
p = call("POST", "/projects/4/tasks", tok("manager"), body={"title": "ZZ assert probe"},
         note="task with title only")
check("task with title only -> 400", p["status"], 400)
check("400 names assigned_to_id and due_date",
      sorted((p["body"].get("details") or {}).keys()), ["assigned_to_id", "due_date"])
check("non-member manager creating a task -> 403",
      st("POST", "/projects/9/tasks", "manager",
         {"title": "ZZ", "assigned_to_id": 3, "due_date": "2026-12-31"}), 403)
check("employee creating a task -> 403",
      st("POST", "/projects/4/tasks", "employee",
         {"title": "ZZ", "assigned_to_id": 3, "due_date": "2026-12-31"}), 403)

print("\n--- INTG-4 documented error envelope ---")
for label, (m, ep, role, b, want) in {
    "401 anon": ("GET", "/projects", "anon", None, ("AUTH_FAILED", 401)),
    "403 employee reports": ("GET", "/reports/employees", "employee", None, ("PERMISSION_DENIED", 403)),
    "404 missing task": ("GET", "/tasks/999999", "admin", None, ("NOT_FOUND", 404)),
    "400 bad scope": ("GET", "/projects?scope=bogus", "manager", None, ("VALIDATION_ERROR", 400)),
    "400 empty login": ("POST", "/auth/login", "anon", {}, ("VALIDATION_ERROR", 400)),
}.items():
    q = call(m, ep, tok(role), body=b, note=f"envelope {label}")
    check(f"{label} code+status", ((q["body"] or {}).get("code"), q["status"]), want)
    check(f"{label} carries error", "error" in (q["body"] or {}), True)

print("\n--- INTG-5 cross-client parity (figures observed on the clients) ---")
s = body("/dashboard", "manager")["stats"]
# F-REG-1, 2026-09-15. total_employees 25 -> 26. THE RULE THIS PINS CHANGED; the
# code did not drift and this is not a red suite being made green.
#
# OD-3 deliberately removed `.exclude(pk=user.pk)` from the dashboard employee
# scope (`backend/apps/dashboard/views.py:346`), because `total_employees` meant
# two things at once: it excluded the caller for a manager and included them for
# an admin and an employee. The contract pins the other two rows as anchors - an
# admin's value equals `GET /employees.count`, an employee's is the people in her
# projects INCLUDING herself - so the only uniform rule that keeps both is
# include-the-caller, and the MANAGER row is the one that had to move.
# `docs/api-contract.md` OD-3 is RESOLVED 2026-09-15 and states the figures
# outright: admin 28, tarun 26, neha 3, priya 25, sanjay 3.
#
# 26 is corroborated from three independent directions, not just from the code:
#   1. `/reports/employees manager count 26` above passes in this same run;
#   2. PW-S57 shows the WEB client rendering 26;
#   3. the admin identity still holds - admin dashboard 28 == GET /employees.count
#      28 - so the rule change did not quietly break the anchor it is pinned to.
# The employee row below stays 25 and still passes: priya was already counted
# include-self, which is exactly the inconsistency OD-3 removed.
check("manager dashboard == web == mobile (26/2/23/3)",
      (s["total_employees"], s["active_projects"], s["open_tasks"], s["completed_tasks"]),
      (26, 2, 23, 3))
s = body("/dashboard", "employee")["stats"]
check("employee dashboard == web == mobile (25/2/4/3)",
      (s["total_employees"], s["active_projects"], s["open_tasks"], s["completed_tasks"]),
      (25, 2, 4, 3))
check("task-form scope=all is the 5 projects both pickers render",
      sorted(x["id"] for x in body("/projects?limit=100&scope=all", "manager")["results"]),
      [1, 2, 3, 4, 10])
check("employee project list is the 3 both clients render",
      sorted(x["id"] for x in body("/projects?limit=100", "employee")["results"]), [1, 2, 3])
# These three are NOT_TESTED because this suite talks to the API and they are
# questions about what two CLIENTS RENDER. body() cannot answer them at any
# status - so they stay NOT_TESTED rather than being asserted green here.
# Their reasons previously read "KNOWN FAIL" and were frozen from before the
# fixes landed, which made this suite report three live parity defects that no
# longer exist. Corrected 2026-09-15; the verdicts are unchanged.
skip("INTG-5 employee report parity",
     "NOT ASSERTABLE AT THIS LAYER - a rendering-parity question, and this suite only "
     "calls the API. INTG-D-001 is FIXED and DEVICE-VERIFIED 2026-09-14: "
     "evidence/qa/mobile/orchestrator-device-verification-20260914T0620Z/"
     "d001-people-report-showing-26-of-26.png. NOT upgraded to PASS here - this run "
     "rendered no mobile screen.")
skip("INTG-5 task assignee requiredness parity",
     "NOT ASSERTABLE AT THIS LAYER - a label-parity question about two clients. "
     "INTG-D-002 is FIXED and DEVICE-VERIFIED 2026-09-14 (the sheet now reads "
     "'Assign to *'). NOT upgraded to PASS here - this run rendered no mobile screen.")
skip("INTG-5 assignable-employee parity",
     "NOT ASSERTABLE AT THIS LAYER - a picker-contents question. INTG-D-003 is FIXED in "
     "both halves and verified 2026-09-14: "
     "evidence/qa/mobile/orchestrator-device-verification-20260914T0620Z/"
     "d003-assignee-picker-27-options-no-inactive.png. NOT upgraded to PASS here.")
skip("iOS client, every criterion", "BLOCKED (BLK-001) — only Xcode CommandLineTools; simctl exits 72")

print("\n--- final fixture restoration ---")
check("employees restored to 28", body("/employees?limit=1", "admin")["count"], 28)
check("projects restored to 6", body("/projects?limit=1&scope=all", "admin")["count"], 6)
check("tasks restored to 41", body("/tasks?limit=1", "admin")["count"], 41)
check("project 1 members restored to 11", len(body("/projects/1", "admin")["members"]), 11)
check("project 10 description unchanged", body("/projects/10", "admin")["description"], d10)

print(f"\n==== {len(PASSED)} PASS · {len(FAILED)} FAIL · {len(SKIPPED)} NOT_TESTED ====")
for n, g, w in FAILED:
    print(f"  FAILED: {n} got={g!r} want={w!r}")
dump("/Volumes/DATA/Automatic Create project/evidence/api/integration/"
     "seam-assertions.md",
     f"Assertive seam tests — {len(PASSED)} PASS / {len(FAILED)} FAIL / {len(SKIPPED)} NOT_TESTED")
sys.exit(1 if FAILED else 0)
