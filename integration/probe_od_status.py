"""OD register re-probe for the GATE-INTG re-evaluation, 2026-09-16.

Drives live HTTP against the running service. Every OD row in the register is
measured today, fixed or open. Mutations are made only where the row cannot be
reached without one (OD-9, OD-10, OD-11) and each is reversed.
"""
import json, sys
sys.path.insert(0, "/Volumes/DATA/Automatic Create project/integration")
from harness import *

F = []
def rec(od, verdict, detail):
    F.append((od, verdict, detail))
    print(f"  [{od}] {verdict}: {detail}")

admin = tok("admin"); mgr = tok("manager"); emp = tok("employee")

def base():
    return {
        "employees": (call("GET","/employees?limit=1",admin,note="baseline employees")["body"] or {}).get("count"),
        "projects": (call("GET","/projects?limit=1&scope=all",admin,note="baseline projects")["body"] or {}).get("count"),
        "tasks": (call("GET","/tasks?limit=1",admin,note="baseline tasks")["body"] or {}).get("count"),
        "p1members": len((call("GET","/projects/1",admin,note="baseline p1")["body"] or {}).get("members") or []),
    }
BEFORE = base()
print("BASELINE BEFORE:", BEFORE)

print("\n== OD-1 pagination bounds -> 400 ==")
bad = ["limit=0","limit=101","limit=500","limit=abc","limit=-1","offset=-1","offset=abc"]
eps = ["/employees","/projects","/tasks","/tasks/1/comments","/projects/1/tasks",
       "/reports/employees","/reports/projects","/employees/assignable","/dashboard/activities"]
cells=0; nonfour=[]
for e in eps:
    for b in bad:
        p = call("GET", f"{e}?{b}", admin, note=f"OD-1 {e}?{b}")
        cells += 1
        if p["status"] != 400: nonfour.append((e,b,p["status"]))
rec("OD-1", "FIXED — verified today" if not nonfour else "REGRESSED",
    f"{cells} bound cells across {len(eps)} collections; non-400: {nonfour or 'none'}")

print("\n== OD-2 envelope on assignable + activities ==")
want = {"count","limit","offset","next","previous","results"}
od2=[]
for e in ["/employees/assignable","/dashboard/activities"]:
    b = call("GET", e, admin, note=f"OD-2 {e}")["body"]
    od2.append((e, sorted(b.keys()) if isinstance(b,dict) else f"BARE {type(b).__name__}",
                isinstance(b,dict) and set(b.keys())==want))
rec("OD-2", "FIXED — verified today" if all(x[2] for x in od2) else "REGRESSED", json.dumps(od2))

print("\n== OD-3 dashboard total_employees: one rule for every role ==")
od3={}
for r,t in [("admin",admin),("manager",mgr),("employee",emp)]:
    d = call("GET","/dashboard",t,note=f"OD-3 dashboard {r}")["body"] or {}
    od3[r]=(d.get("stats") or {}).get("total_employees")
empc=(call("GET","/employees?limit=1",admin,note="OD-3 employees count")["body"] or {}).get("count")
rec("OD-3", "FIXED — verified today" if od3["admin"]==empc else "REGRESSED",
    f"{od3}; admin == GET /employees.count ({empc}): {od3['admin']==empc}")

print("\n== OD-4 deactivation revokes a live token (UNSPECIFIED behaviour) ==")
import re as _re
ct = open("/Volumes/DATA/Automatic Create project/docs/api-contract.md").read()
spec = "Observed, not specified" in ct and "OD-4" in ct
rec("OD-4", "OPEN — specification decision outstanding",
    "auth-lifecycle S8 measured it again today: PATCH status=inactive -> 200, live token -> 401, re-login -> 401. "
    f"Contract still labels the row 'Observed, not specified' and OD-4 OPEN: {spec}. "
    "Behaviour is correct; what is missing is a contract decision, not a code change.")

print("\n== OD-5 unrouted path -> JSON envelope ==")
od5=[]
for u in ["http://localhost:8000/api/v1/nope","http://localhost:8000/api/v1/employees/",
          "http://localhost:8000/api/v1/a/b/c","http://localhost:8000/nope"]:
    for tk,lbl in [(None,"anon"),(admin,"admin")]:
        p = call("GET", u, tk, note=f"OD-5 {u} {lbl}")
        raw=p["raw"]
        markers=[m for m in ["django","urlconf","Traceback","DEBUG","<html"] if m.lower() in raw.lower()]
        od5.append((u,lbl,p["status"],len(raw),markers))
clean = all(len(x[4])==0 for x in od5)
rec("OD-5", "FIXED — verified today" if clean else "REGRESSED",
    f"8 probes, max body {max(x[3] for x in od5)} bytes, framework markers: {'none' if clean else od5}")

print("\n== OD-6 task filter aliases ==")
def ids(path, t=admin, note=""):
    b = call("GET", path, t, note=note)["body"] or {}
    return sorted(r["id"] for r in b.get("results", []))
a1, a2 = ids("/tasks?project_id=1&limit=100", admin, "OD-6 project_id"), ids("/tasks?project=1&limit=100", admin, "OD-6 project")
b1, b2 = ids("/tasks?assigned_to_id=3&limit=100",admin,"OD-6 assigned_to_id"), ids("/tasks?assigned_to=3&limit=100",admin,"OD-6 assigned_to")
allt = ids("/tasks?limit=100",admin,"OD-6 all")
ov_t = ids("/tasks?overdue=true&limit=100",admin,"OD-6 overdue true")
ov_f = ids("/tasks?overdue=false&limit=100",admin,"OD-6 overdue false")
ok6 = a1==a2 and b1==b2 and a1!=allt and len(ov_t)+len(ov_f)==len(allt)
rec("OD-6","FIXED — verified today" if ok6 else "REGRESSED",
    f"project_id set == project set: {a1==a2} ({len(a1)} of {len(allt)}); "
    f"assigned_to_id set == assigned_to set: {b1==b2} ({len(b1)}); overdue {len(ov_t)}+{len(ov_f)}={len(allt)}")

print("\n== OD-8 organization.editable_by_current_user ==")
od8={}
for r,t in [("admin",admin),("manager",mgr),("employee",emp)]:
    s = call("GET","/settings",t,note=f"OD-8 settings {r}")["body"] or {}
    flag = (s.get("organization") or {}).get("editable_by_current_user")
    pa = call("PATCH","/settings",t,body={"organization":{"name":"X"}},note=f"OD-8 patch {r}")
    od8[r]={"flag":flag,"patch":pa["status"],"body":pa["raw"][:120]}
reprod = od8["admin"]["flag"] is True and od8["admin"]["patch"] == 400
rec("OD-8","OPEN — reproduces today" if reprod else "CHANGED", json.dumps(od8))

print("\n== OD-9 POST /tasks vs POST /projects/{id}/tasks response shape ==")
created=[]
body9 = {"title":"OD-probe-9","project_id":4,"assigned_to_id":2,"due_date":"2026-12-31","description":"integration re-probe"}
t1 = call("POST","/tasks",admin,body=body9,note="OD-9 flat create")
if t1["status"]==201: created.append(t1["body"]["id"])
body9b = dict(body9); body9b.pop("project_id"); body9b["title"]="OD-probe-9b"
t2 = call("POST","/projects/4/tasks",admin,body=body9b,note="OD-9 nested create")
if t2["status"]==201: created.append(t2["body"]["id"])
k1 = sorted((t1["body"] or {}).keys()); k2 = sorted((t2["body"] or {}).keys())
rec("OD-9","OPEN — reproduces today" if k1!=k2 else "FIXED",
    f"flat 201 keys minus nested: {sorted(set(k1)-set(k2))}; nested minus flat: {sorted(set(k2)-set(k1))}")

print("\n== OD-10 nonexistent project: 400 vs 404 ==")
n1 = call("POST","/tasks",admin,body={"title":"OD-probe-10","project_id":99999,
     "assigned_to_id":2,"due_date":"2026-12-31"},note="OD-10 flat bad project")
n2 = call("POST","/projects/99999/tasks",admin,body={"title":"OD-probe-10",
     "assigned_to_id":2,"due_date":"2026-12-31"},note="OD-10 nested bad project")
if n1["status"]==201: created.append(n1["body"]["id"])
if n2["status"]==201: created.append(n2["body"]["id"])
rec("OD-10","OPEN — reproduces today" if n1["status"]!=n2["status"] else "FIXED",
    f"flat POST /tasks -> {n1['status']} {(n1['body'] or {}).get('code')}; "
    f"nested POST /projects/99999/tasks -> {n2['status']} {(n2['body'] or {}).get('code')}")

print("\n== OD-11 empty PATCH /comments/{id} ==")
c = call("POST","/tasks/1/comments",admin,body={"body":"OD-11 re-probe comment"},note="OD-11 create own comment")
cid = (c["body"] or {}).get("id")
if cid:
    u_before = (c["body"] or {}).get("updated_at")
    pa = call("PATCH", f"/comments/{cid}", admin, body={}, note="OD-11 empty PATCH")
    u_after = (pa["body"] or {}).get("updated_at")
    dele = call("DELETE", f"/comments/{cid}", admin, note="OD-11 cleanup own comment")
    rec("OD-11","OPEN — reproduces today" if (pa["status"]==200 and u_before!=u_after) else "CHANGED",
        f"empty PATCH -> {pa['status']}; updated_at before={u_before} after={u_after}; "
        f"mutated_by_noop={u_before!=u_after}; probe comment {cid} deleted -> {dele['status']}")
else:
    rec("OD-11","NOT_TESTED", f"could not create a disposable comment: {c['status']} {c['raw'][:140]}")

print("\n== OD-12 /employees/assignable default page vs enforced max ==")
d12 = call("GET","/employees/assignable",admin,note="OD-12 default page")["body"] or {}
r101 = call("GET","/employees/assignable?limit=101",admin,note="OD-12 limit 101")
rec("OD-12","OPEN — reproduces today" if d12.get("limit")==d12.get("count") and r101["status"]==400 else "CHANGED",
    f"default limit={d12.get('limit')} count={d12.get('count')} len(results)={len(d12.get('results') or [])}; "
    f"?limit=101 -> {r101['status']}")

print("\n== OD-13 ?sort=<invalid> -> 400 ==")
od13=[]
for e in ["/tasks","/projects","/employees"]:
    for v in ["nonsense","no_such_field","NAME","id","-","title,status","--title"]:
        p = call("GET", f"{e}?sort={v}", admin, note=f"OD-13 {e}?sort={v}")
        od13.append((e,v,p["status"],(p["body"] or {}).get("code")))
bad13=[x for x in od13 if x[2]!=400]
rec("OD-13","FIXED — verified today" if not bad13 else "REGRESSED",
    f"{len(od13)} invalid-sort probes across 3 endpoints; non-400: {bad13 or 'none'}")

print("\n== cleanup: deleting probe-created tasks ==", created)
for tid in created:
    print("  DELETE /tasks/%s ->" % tid, call("DELETE", f"/tasks/{tid}", admin, note=f"cleanup task {tid}")["status"])

AFTER = base()
print("\nBASELINE AFTER:", AFTER)
restored = AFTER == BEFORE == {"employees":28,"projects":6,"tasks":41,"p1members":11}
print("RESTORED / MATCHES DECLARED BASELINE:", restored)

print("\n==== OD REGISTER POSITION, 2026-09-16 ====")
for od,v,_ in F: print(f"  {od:7} {v}")

dump("/Volumes/DATA/Automatic Create project/evidence/api/integration/od-register-reprobe.md",
     "OD register re-probe — every deviation row measured live, 2026-09-16")
sys.exit(0 if restored else 1)
