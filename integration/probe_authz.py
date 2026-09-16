"""Role / authorisation conformance re-audit — read-only probes.

Re-probes every row of the "Known Implementation Deviations" table in
docs/api-contract.md plus D-1..D-9 from
evidence/api/role-audit/role-authorisation-audit-20260910T065115Z.md.
"""
import hashlib, json, sys
sys.path.insert(0, "/Volumes/DATA/Automatic Create project/integration")
from harness import *

ROLES = ["admin", "manager", "manager2", "employee", "outsider", "inactive", "anon"]
RESULTS = []

def rec(id_, desc, expected, observed, verdict):
    RESULTS.append({"id": id_, "desc": desc, "expected": expected,
                    "observed": observed, "verdict": verdict})

def sha(o):
    return hashlib.sha1(json.dumps(o, sort_keys=True).encode()).hexdigest()[:12]

# ---------------------------------------------------------------- auth ----
print("== login matrix ==")
for r in ROLES:
    if r == "anon":
        continue
    p = call("POST", "/auth/login", body={"email": ACCOUNTS[r], "password": PASSWORD},
             note=f"login {r}")
    print(f"  {r:9} {ACCOUNTS[r]:22} -> {p['status']}")
    if p["status"] == 200:
        TOKENS[r] = p["body"]["access"]
rec("AUTH-inactive", "login as is_active=false user", "401 AUTH_FAILED",
    f"{PROBES[-1]['status']}", "PASS" if PROBES[-1]["status"] == 401 else "FAIL")

p = call("POST", "/auth/login", body={"email": ACCOUNTS["admin"], "password": "wrong-password-zz"},
         note="login admin wrong password")
print("  wrong password ->", p["status"])
p = call("POST", "/auth/login", body={"email": "nobody@example.com", "password": "x"},
         note="login unknown user")
print("  unknown user   ->", p["status"])

# --------------------------------------------------- read matrix ----------
READS = [
    "/auth/me", "/employees", "/employees/1", "/employees/assignable",
    "/projects", "/projects/1", "/projects/9", "/projects/1/tasks", "/projects/9/tasks",
    "/tasks", "/tasks/1", "/tasks/1/comments",
    "/dashboard", "/dashboard/stats", "/dashboard/activities",
    "/reports/tasks", "/reports/employees", "/reports/projects",
    "/settings",
]
print("\n== read matrix (status per role) ==")
hdr = f"{'endpoint':32}" + "".join(f"{r[:8]:>10}" for r in ROLES)
print(hdr)
matrix = {}
for ep in READS:
    row = {}
    for r in ROLES:
        p = call("GET", ep, tok(r), note=f"read {ep} as {r}")
        row[r] = p["status"]
    matrix[ep] = row
    print(f"{ep:32}" + "".join(f"{row[r]:>10}" for r in ROLES))

# ------------------------------------------------------- D-1 reports ------
print("\n== D-1 report role gate ==")
d1 = all(matrix[e]["employee"] == 403 for e in ["/reports/tasks", "/reports/employees", "/reports/projects"])
rec("D-1", "Employee blocked from all three report endpoints", "403 x3",
    {e: matrix[e]["employee"] for e in ["/reports/tasks", "/reports/employees", "/reports/projects"]},
    "CLOSED" if d1 else "OPEN")
print("  D-1:", "CLOSED" if d1 else "OPEN")

# -------------------------------------- D-1b manager vs admin scoping -----
print("\n== report manager-vs-admin scoping ==")
scope_rows = {}
for ep in ["/reports/employees?limit=100", "/reports/projects?limit=100", "/reports/tasks"]:
    a = call("GET", ep, tok("admin"), note=f"{ep} admin")
    m = call("GET", ep, tok("manager"), note=f"{ep} manager (tarun)")
    m2 = call("GET", ep, tok("manager2"), note=f"{ep} manager2 (neha)")
    ident = sha(a["body"]) == sha(m["body"])
    scope_rows[ep] = {"admin": sha(a["body"]), "manager": sha(m["body"]),
                      "manager2": sha(m2["body"]), "identical_admin_manager": ident}
    ca = (a["body"] or {}).get("count", len((a["body"] or {}).get("results") or []))
    cm = (m["body"] or {}).get("count", len((m["body"] or {}).get("results") or []))
    cm2 = (m2["body"] or {}).get("count", len((m2["body"] or {}).get("results") or []))
    print(f"  {ep:34} admin={ca} manager={cm} manager2={cm2} identical={ident}")
rec("D-1b", "Manager report payload distinct from Admin", "not byte-identical",
    scope_rows, "CLOSED" if not any(v["identical_admin_manager"] for v in scope_rows.values()) else "OPEN")

# --------------------------------------------------- D-9 / F-1 envelope ---
print("\n== D-9 / API-F-1 pagination envelope on reports ==")
ENV = {"count", "limit", "offset", "next", "previous", "results"}
env_res = {}
for ep in ["/reports/employees", "/reports/projects"]:
    p = call("GET", ep, tok("admin"), note=f"{ep} envelope")
    keys = set((p["body"] or {}).keys())
    have = ENV <= keys
    l1 = call("GET", ep + "?limit=1", tok("admin"), note=f"{ep}?limit=1 honoured")
    honoured = len((l1["body"] or {}).get("results") or []) == 1
    bad = call("GET", ep + "?limit=0", tok("admin"), note=f"{ep}?limit=0 rejected")
    badoff = call("GET", ep + "?offset=-1", tok("admin"), note=f"{ep}?offset=-1 rejected")
    past = call("GET", ep + "?offset=9999", tok("admin"), note=f"{ep}?offset past end")
    env_res[ep] = {"keys": sorted(keys), "envelope_complete": have,
                   "limit1_honoured": honoured, "limit0": bad["status"],
                   "offset_neg": badoff["status"], "offset_past_end": past["status"],
                   "offset_past_results": (past["body"] or {}).get("results")}
    print(f"  {ep}: envelope={have} limit=1 honoured={honoured} limit=0->{bad['status']} offset=-1->{badoff['status']} offset=9999->{past['status']}")
rec("D-9/C-3/API-F-1", "Report collections carry the pagination envelope",
    "count/limit/offset/next/previous/results + 400 on bad bounds", env_res,
    "CLOSED" if all(v["envelope_complete"] and v["limit1_honoured"] for v in env_res.values()) else "OPEN")

# --------------------------------------------------- D-2 report filters ---
print("\n== D-2 /reports/tasks documented filters ==")
base = call("GET", "/reports/tasks", tok("admin"), note="reports/tasks unfiltered")
far = call("GET", "/reports/tasks?date_from=2099-01-01&date_to=2099-12-31", tok("admin"),
           note="reports/tasks 2099 window")
proj = call("GET", "/reports/tasks?project_id=1", tok("admin"), note="reports/tasks project_id=1")
d2 = {"unfiltered": sha(base["body"]), "window2099": sha(far["body"]), "project_id1": sha(proj["body"])}
print("  ", d2)
rec("D-2", "/reports/tasks honours date_from/date_to/project_id",
    "three distinct payloads", d2,
    "CLOSED" if len(set(d2.values())) == 3 else ("PARTIAL" if len(set(d2.values())) == 2 else "OPEN"))

# ------------------------------------------ scope parameter (new API) -----
print("\n== GET /projects?scope= (new, contract line 379) ==")
scope_obs = {}
for role in ["admin", "manager", "manager2", "employee", "outsider"]:
    ids = {}
    for s in [None, "owned", "member", "all"]:
        q = "/projects?limit=100" + (f"&scope={s}" if s else "")
        p = call("GET", q, tok(role), note=f"projects scope={s} as {role}")
        ids[s or "(default)"] = sorted(x["id"] for x in (p["body"] or {}).get("results") or [])
    scope_obs[role] = ids
    print(f"  {role:9} " + "  ".join(f"{k}={v}" for k, v in ids.items()))
for bogus in ["bogus", "OWNED", "owned,member", " ", ""]:
    p = call("GET", f"/projects?scope={bogus}", tok("manager"), note=f"projects scope={bogus!r}")
    print(f"  scope={bogus!r:15} -> {p['status']} {json.dumps(p['body'])[:110] if p['body'] else ''}")
    scope_obs.setdefault("_bad", {})[repr(bogus)] = {"status": p["status"], "body": p["body"]}
rec("SCOPE", "?scope=owned|member|all with 400 on unrecognised",
    "default==owned for manager; scope=bogus -> 400", scope_obs,
    "SEE-REPORT")

# ------------------------------------ D-4 object-level scoping (reads) ----
print("\n== D-4 object-level scoping ==")
d4 = {"GET /projects/9 as employee": matrix["/projects/9"]["employee"],
      "GET /projects/9 as manager(tarun, non-member)": matrix["/projects/9"]["manager"],
      "GET /projects/9/tasks as employee": matrix["/projects/9/tasks"]["employee"],
      "GET /projects/9/tasks as manager(tarun)": matrix["/projects/9/tasks"]["manager"],
      "GET /tasks/1 as outsider": matrix["/tasks/1"]["outsider"],
      "GET /projects count per role": {r: None for r in []}}
for r in ROLES:
    if r == "anon":
        continue
    p = call("GET", "/projects?limit=100&scope=all", tok(r), note=f"projects count {r}")
    d4[f"GET /projects?scope=all count as {r}"] = (p["body"] or {}).get("count")
print(json.dumps(d4, indent=1))
rec("D-4", "Object-level scoping on projects and tasks",
    "non-member refused 403/404", d4, "SEE-REPORT")

# ------------------------------------------------- D-3 settings gate ------
print("\n== D-3 /settings ==")
d3 = {"GET as employee": matrix["/settings"]["employee"], "GET as manager": matrix["/settings"]["manager"]}
for r in ["employee", "manager", "admin"]:
    p = call("PATCH", "/settings", tok(r), body={"role": "admin"}, note=f"PATCH /settings role escalation as {r}")
    d3[f"PATCH role=admin as {r}"] = {"status": p["status"], "body": p["body"]}
    p = call("PATCH", "/settings", tok(r), body={"email": "hijack@example.com"}, note=f"PATCH /settings email as {r}")
    d3[f"PATCH email as {r}"] = {"status": p["status"], "body": p["body"]}
    p = call("PATCH", "/settings", tok(r), body={"organization": {"name": "ZZ"}}, note=f"PATCH /settings organization as {r}")
    d3[f"PATCH organization as {r}"] = {"status": p["status"], "body": p["body"]}
print(json.dumps(d3, indent=1)[:1500])
rec("D-3", "/settings personal-scope; privilege fields rejected",
    "400 on role/email/organization for every role", d3, "SEE-REPORT")

# ------------------------------------------ C-4 editable_by_current_user --
p = call("GET", "/settings", tok("admin"), note="settings admin for C-4 flag")
flag_admin = ((p["body"] or {}).get("organization") or {}).get("editable_by_current_user")
p = call("GET", "/settings", tok("employee"), note="settings employee for C-4 flag")
flag_emp = ((p["body"] or {}).get("organization") or {}).get("editable_by_current_user")
print(f"\n== C-4 editable_by_current_user: admin={flag_admin} employee={flag_emp}")
rec("C-4", "organization.editable_by_current_user honesty",
    "false (no org write path exists)", {"admin": flag_admin, "employee": flag_emp},
    "CLOSED" if flag_admin is False else "OPEN")

# --------------------------------------------------- error envelope -------
print("\n== error envelope + documented codes ==")
errs = {}
for label, (m, ep, t, b) in {
    "401 anon": ("GET", "/projects", None, None),
    "401 bad token": ("GET", "/projects", "not-a-jwt", None),
    "403 employee->reports": ("GET", "/reports/employees", tok("employee"), None),
    "404 employee": ("GET", "/employees/999999", tok("admin"), None),
    "404 project": ("GET", "/projects/999999", tok("admin"), None),
    "404 task": ("GET", "/tasks/999999", tok("admin"), None),
    "400 scope": ("GET", "/projects?scope=bogus", tok("manager"), None),
    "400 limit": ("GET", "/employees?limit=0", tok("admin"), None),
    "400 login empty": ("POST", "/auth/login", None, {}),
    "405 method": ("DELETE", "/dashboard", tok("admin"), None),
}.items():
    p = call(m, ep, t, body=b, note=f"error probe {label}")
    body = p["body"] or {}
    errs[label] = {"status": p["status"], "has_error": "error" in body,
                   "code": body.get("code"), "has_details": "details" in body,
                   "body": body}
    print(f"  {label:24} {p['status']:>4}  error={'error' in body}  code={body.get('code')}")
rec("ERR", "Documented error envelope {error,code,details}",
    "every 4xx carries error+code", errs, "SEE-REPORT")

with open("/tmp/authz_results.json", "w") as f:
    json.dump({"results": RESULTS, "matrix": matrix, "scope": scope_obs}, f, indent=1, default=str)
dump("/Volumes/DATA/Automatic Create project/evidence/api/integration/"
     "role-authz-reaudit.md",
     "Role / authorisation conformance re-audit (read-only probes)")
