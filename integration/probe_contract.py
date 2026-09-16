"""Contract conformance: pagination convention, collection scoping, response
shapes, and the undocumented-endpoint list. Read-only."""
import json, sys
sys.path.insert(0, "/Volumes/DATA/Automatic Create project/integration")
from harness import *

ENV = ["count", "limit", "offset", "next", "previous", "results"]
COLLECTIONS = ["/employees", "/projects", "/tasks", "/tasks/1/comments",
               "/projects/1/tasks", "/reports/employees", "/reports/projects",
               "/employees/assignable", "/dashboard/activities"]

print("== pagination convention: envelope + bounds validation ==")
print(f"{'collection':26}{'env':>6}{'lim=0':>7}{'lim=101':>9}{'lim=abc':>9}{'off=-1':>8}{'off=abc':>9}{'lim=1':>7}{'cap500':>8}")
pag = {}
for c in COLLECTIONS:
    a = tok("admin")
    base = call("GET", c, a, note=f"{c} base")
    bb = base["body"]
    keys = list(bb.keys()) if isinstance(bb, dict) else ["<BARE LIST len=%d>" % len(bb or [])]
    env = isinstance(bb, dict) and all(k in keys for k in ENV)
    r = {}
    for label, q in [("lim0", "?limit=0"), ("lim101", "?limit=101"), ("limabc", "?limit=abc"),
                     ("offneg", "?offset=-1"), ("offabc", "?offset=abc")]:
        p = call("GET", c + q, a, note=f"{c}{q}")
        r[label] = p["status"]
    p = call("GET", c + "?limit=1", a, note=f"{c}?limit=1")
    n1 = len((p["body"] or {}).get("results") or []) if isinstance(p["body"], dict) else "bare%d" % len(p["body"] or [])
    p = call("GET", c + "?limit=500", a, note=f"{c}?limit=500 cap")
    cap = (p["body"] or {}).get("limit") if isinstance(p["body"], dict) else "n/a"
    pag[c] = {"envelope": env, "keys": keys, **r, "limit1_len": n1, "limit500_echo": cap}
    print(f"{c:26}{str(env):>6}{r['lim0']:>7}{r['lim101']:>9}{r['limabc']:>9}{r['offneg']:>8}{r['offabc']:>9}{str(n1):>7}{str(cap):>8}")

print("\n== GET /tasks scoping per role (D-4 collection half) ==")
tsc = {}
for role in ["admin", "manager", "manager2", "employee", "outsider"]:
    p = call("GET", "/tasks?limit=100", tok(role), note=f"/tasks as {role}")
    ids = sorted(x["id"] for x in (p["body"] or {}).get("results") or [])
    projs = sorted({(x.get("project") or {}).get("id") if isinstance(x.get("project"), dict) else x.get("project")
                    for x in (p["body"] or {}).get("results") or []})
    tsc[role] = {"count": (p["body"] or {}).get("count"), "projects_present": projs}
    print(f"  {role:9} count={tsc[role]['count']:>4}  projects={projs}")

print("\n== undocumented endpoints: still present? ==")
UNDOC = [("GET", "/auth/me"), ("GET", "/employees/assignable"), ("GET", "/tasks"),
         ("GET", "/dashboard/stats"), ("GET", "/dashboard/activities")]
und = {}
for m, ep in UNDOC:
    p = call(m, ep, tok("admin"), note=f"undocumented {m} {ep}")
    und[f"{m} {ep}"] = p["status"]
    print(f"  {m} {ep:26} -> {p['status']}")

print("\n== response shape spot-checks vs contract ==")
shapes = {}
p = call("GET", "/reports/employees?limit=2", tok("admin"), note="reports/employees shape")
b = p["body"]
shapes["/reports/employees"] = {"top": sorted(b.keys()), "period": b.get("period"),
                                "row": sorted(b["results"][0].keys()) if b.get("results") else None,
                                "completion_rate_sample": [r.get("completion_rate") for r in b.get("results", [])]}
p = call("GET", "/reports/projects?limit=2", tok("admin"), note="reports/projects shape")
b = p["body"]
shapes["/reports/projects"] = {"top": sorted(b.keys()),
                               "row": sorted(b["results"][0].keys()) if b.get("results") else None,
                               "completion_rate_sample": [r.get("completion_rate") for r in b.get("results", [])]}
p = call("GET", "/reports/tasks", tok("admin"), note="reports/tasks shape")
shapes["/reports/tasks"] = {"top": sorted((p["body"] or {}).keys())}
p = call("GET", "/dashboard", tok("admin"), note="dashboard shape")
shapes["/dashboard"] = {"top": sorted((p["body"] or {}).keys())}
p = call("GET", "/tasks/1", tok("admin"), note="task shape")
shapes["/tasks/{id}"] = {"keys": sorted((p["body"] or {}).keys())}
p = call("GET", "/projects/1", tok("admin"), note="project shape")
shapes["/projects/{id}"] = {"keys": sorted((p["body"] or {}).keys())}
p = call("GET", "/employees/1", tok("admin"), note="employee shape")
shapes["/employees/{id}"] = {"keys": sorted((p["body"] or {}).keys())}
print(json.dumps(shapes, indent=1))

print("\n== date-window echo (period) honoured ==")
w = call("GET", "/reports/employees?limit=100&date_from=2099-01-01&date_to=2099-12-31", tok("admin"),
         note="reports/employees 2099 window")
print("  period echo:", (w["body"] or {}).get("period"),
      " totals:", sum(r.get("assigned_tasks_total", 0) for r in (w["body"] or {}).get("results") or []))
w2 = call("GET", "/reports/employees?limit=100", tok("admin"), note="reports/employees unwindowed")
print("  unwindowed totals:", sum(r.get("assigned_tasks_total", 0) for r in (w2["body"] or {}).get("results") or []))
bad = call("GET", "/reports/employees?date_from=not-a-date", tok("admin"), note="reports/employees bad date")
print("  date_from=not-a-date ->", bad["status"], json.dumps(bad["body"])[:120])

json.dump({"pagination": pag, "tasks_scoping": tsc, "undocumented": und, "shapes": shapes},
          open("/tmp/contract_results.json", "w"), indent=1, default=str)
dump("/Volumes/DATA/Automatic Create project/evidence/api/integration/"
     "contract-conformance.md",
     "Contract conformance re-verification — pagination, scoping, shapes")
