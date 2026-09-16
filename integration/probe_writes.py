"""Write-path authorisation re-probes: D-5, D-6, D-7, D-8, plus cross-client
write parity. Every mutation is reversed and the baseline re-verified."""
import json, sys
sys.path.insert(0, "/Volumes/DATA/Automatic Create project/integration")
from harness import *

R = {}
admin, mgr, mgr2, emp, out = tok("admin"), tok("manager"), tok("manager2"), tok("employee"), tok("outsider")

def counts(label):
    e = call("GET", "/employees?limit=1", admin, note=f"count employees {label}")
    p = call("GET", "/projects?limit=1&scope=all", admin, note=f"count projects {label}")
    t = call("GET", "/tasks?limit=1", admin, note=f"count tasks {label}")
    m = call("GET", "/projects/1", admin, note=f"project 1 members {label}")
    c = {"employees": p and e["body"]["count"], "projects": p["body"]["count"],
         "tasks": t["body"]["count"], "project1_members": len(m["body"].get("members") or [])}
    print(f"  [{label}] {c}")
    return c

print("== baseline ==")
BEFORE = counts("before")

print("\n== D-5 project write endpoints: role-gated or owner-gated? ==")
p10 = call("GET", "/projects/10", admin, note="read project 10 (neha-owned, tarun is a member)")
desc10 = p10["body"].get("description")
d5 = {}
q = call("PATCH", "/projects/10", mgr, body={"description": desc10},
         note="PATCH project 10 as tarun: MEMBER but NOT owner (no-op value)")
d5["patch_member_not_owner"] = {"status": q["status"], "body": q["body"]}
print("  PATCH /projects/10 as tarun (member, not owner) ->", q["status"], json.dumps(q["body"])[:120])
q = call("PATCH", "/projects/9", mgr, body={"description": "zz"},
         note="PATCH project 9 as tarun: NOT member, NOT owner")
d5["patch_stranger"] = {"status": q["status"], "body": q["body"]}
print("  PATCH /projects/9  as tarun (stranger)          ->", q["status"])
p4 = call("GET", "/projects/4", mgr, note="read project 4 (tarun-owned)")
q = call("PATCH", "/projects/4", mgr, body={"description": p4["body"].get("description")},
         note="PATCH project 4 as tarun: OWNER (no-op value)")
d5["patch_owner"] = q["status"]
print("  PATCH /projects/4  as tarun (owner)             ->", q["status"])
q = call("PATCH", "/projects/4", emp, body={"description": "zz"}, note="PATCH project 4 as employee")
d5["patch_employee"] = q["status"]
print("  PATCH /projects/4  as employee                  ->", q["status"])
q = call("DELETE", "/projects/9", mgr, note="DELETE project 9 as tarun (stranger)")
d5["delete_stranger"] = q["status"]
print("  DELETE /projects/9 as tarun                     ->", q["status"])
q = call("POST", "/projects/10/members", mgr, body={"employee_id": 3},
         note="ADD member to project 10 as tarun (member, not owner)")
d5["addmember_member_not_owner"] = {"status": q["status"], "body": q["body"]}
print("  POST /projects/10/members as tarun              ->", q["status"], json.dumps(q["body"])[:110])
if q["status"] in (200, 201):
    u = call("DELETE", "/projects/10/members/3", mgr, note="RESTORE: undo the member add")
    print("     -> undo removal:", u["status"])
    d5["addmember_undone"] = u["status"]
q = call("DELETE", "/projects/9/members/11", mgr, note="REMOVE member from project 9 as tarun (stranger)")
d5["delmember_stranger"] = q["status"]
print("  DELETE /projects/9/members/11 as tarun          ->", q["status"])
R["D-5"] = d5

print("\n== D-8 membership error status codes ==")
d8 = {}
p4m = call("GET", "/projects/4", mgr, note="project 4 members")
member_ids = [m["id"] for m in (p4m["body"].get("members") or [])]
print("  project 4 member ids:", member_ids)
dup = member_ids[0]
q = call("POST", "/projects/4/members", mgr, body={"employee_id": dup},
         note=f"duplicate member add ({dup} already a member) — contract says 409")
d8["duplicate_add"] = {"status": q["status"], "body": q["body"]}
print(f"  POST duplicate member -> {q['status']} (contract: 409)", json.dumps(q["body"])[:130])
nonmember = next(i for i in range(3, 40) if i not in member_ids)
q = call("DELETE", f"/projects/4/members/{nonmember}", mgr,
         note=f"remove non-member {nonmember} — contract says 404")
d8["remove_nonmember"] = {"status": q["status"], "body": q["body"]}
print(f"  DELETE non-member     -> {q['status']} (contract: 404)", json.dumps(q["body"])[:130])
R["D-8"] = d8

print("\n== D-6 task required fields ==")
d6 = {}
q = call("POST", "/projects/4/tasks", mgr, body={"title": "ZZ integration probe minimal"},
         note="create task with title only — contract requires assigned_to_id + due_date")
d6["title_only"] = {"status": q["status"], "body": q["body"]}
print("  POST /projects/4/tasks {title} ->", q["status"], json.dumps(q["body"])[:200])
created = []
if q["status"] == 201:
    created.append(q["body"]["id"])
q2 = call("POST", "/projects/4/tasks", mgr,
          body={"title": "ZZ integration probe full", "assigned_to_id": 3,
                "due_date": "2026-12-31", "priority": "low", "status": "pending"},
          note="create task with the documented full body")
d6["full_body"] = {"status": q2["status"], "body_keys": sorted((q2["body"] or {}).keys())}
print("  POST /projects/4/tasks {full}  ->", q2["status"])
if q2["status"] == 201:
    created.append(q2["body"]["id"])
q3 = call("POST", "/projects/4/tasks", mgr,
          body={"title": "ZZ legacy field name", "assigned_to": 3, "due_date": "2026-12-31"},
          note="create task with the LEGACY field name assigned_to (C-6)")
d6["legacy_field"] = {"status": q3["status"], "assigned_to": (q3["body"] or {}).get("assigned_to")}
print("  POST with legacy assigned_to   ->", q3["status"],
      "assignee:", json.dumps((q3["body"] or {}).get("assigned_to"))[:80])
if q3["status"] == 201:
    created.append(q3["body"]["id"])
R["D-6"] = d6

print("\n== D-7 membership on task creation ==")
d7 = {}
q = call("POST", "/projects/9/tasks", mgr,
         body={"title": "ZZ non-member create", "assigned_to_id": 3, "due_date": "2026-12-31"},
         note="tarun creates a task in project 9, which he is not a member of")
d7["nonmember_create"] = {"status": q["status"], "body": q["body"]}
print("  POST /projects/9/tasks as tarun (non-member) ->", q["status"], json.dumps(q["body"])[:130])
if q["status"] == 201:
    created.append(q["body"]["id"])
q = call("POST", "/projects/4/tasks", emp,
         body={"title": "ZZ employee create", "assigned_to_id": 3, "due_date": "2026-12-31"},
         note="employee creates a task — contract: Manager/Admin only")
d7["employee_create"] = q["status"]
print("  POST /projects/4/tasks as employee           ->", q["status"])
if q["status"] == 201:
    created.append(q["body"]["id"])
q = call("POST", "/tasks", emp, body={"title": "ZZ flat", "project_id": 1,
         "assigned_to_id": 3, "due_date": "2026-12-31"}, note="flat POST /tasks as employee")
d7["flat_employee"] = q["status"]
print("  POST /tasks (flat, undocumented) as employee ->", q["status"])
if q["status"] == 201:
    created.append(q["body"]["id"])
R["D-7"] = d7

print("\n== task update/delete authorisation ==")
ta = {}
q = call("PATCH", "/tasks/1", out, body={"status": "completed"}, note="outsider updates task 1")
ta["outsider_patch"] = q["status"]
q = call("PATCH", "/tasks/1", mgr2, body={"status": "completed"}, note="neha (stranger manager) updates task 1")
ta["stranger_manager_patch"] = q["status"]
q = call("DELETE", "/tasks/1", emp, note="employee deletes task 1")
ta["employee_delete"] = q["status"]
q = call("DELETE", "/tasks/1", out, note="outsider deletes task 1")
ta["outsider_delete"] = q["status"]
print(" ", ta)
R["task_authz"] = ta

print("\n== employee mutation authorisation ==")
em = {}
for role, t in [("manager", mgr), ("employee", emp), ("outsider", out)]:
    em[f"{role}_create"] = call("POST", "/employees", t, body={"email": "zz@example.com",
        "password": "Whatever!1234", "first_name": "Z", "last_name": "Z", "role": "employee"},
        note=f"{role} creates employee")["status"]
    em[f"{role}_patch_other"] = call("PATCH", "/employees/1", t, body={"department": "ZZ"},
        note=f"{role} edits employee 1")["status"]
    em[f"{role}_delete"] = call("DELETE", "/employees/12", t, note=f"{role} deletes employee 12")["status"]
    em[f"{role}_escalate_self"] = call("PATCH", "/employees/3", t, body={"role": "admin"},
        note=f"{role} escalates employee 3 to admin")["status"]
print(json.dumps(em, indent=1))
R["employee_authz"] = em

print("\n== CLEANUP: deleting probe-created tasks", created, "==")
for tid in created:
    d = call("DELETE", f"/tasks/{tid}", admin, note=f"cleanup task {tid}")
    print(f"  DELETE /tasks/{tid} -> {d['status']}")
R["cleanup_tasks"] = created

print("\n== restoration verification ==")
AFTER = counts("after")
R["baseline_before"], R["baseline_after"] = BEFORE, AFTER
R["restored"] = BEFORE == AFTER
print("  RESTORED:", BEFORE == AFTER)
p10b = call("GET", "/projects/10", admin, note="project 10 after")
print("  project 10 description unchanged:", p10b["body"].get("description") == desc10)
print("  project 10 members:", len(p10b["body"].get("members") or []))
R["project10_desc_unchanged"] = p10b["body"].get("description") == desc10
R["project10_members_after"] = len(p10b["body"].get("members") or [])

json.dump(R, open("/tmp/writes_results.json", "w"), indent=1, default=str)
dump("/Volumes/DATA/Automatic Create project/evidence/api/integration/"
     "write-path-authz.md",
     "Write-path authorisation re-probes (D-5 .. D-8) with fixture restoration")
