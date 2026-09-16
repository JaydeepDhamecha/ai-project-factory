"""The ordering assertion docs/api-contract.md requires for /reports/projects:
concatenating ?limit=2&offset=0|2|4 must reproduce the unpaginated list."""
import json, sys
sys.path.insert(0, "/Volumes/DATA/Automatic Create project/integration")
from harness import *

a = tok("admin")
full = call("GET", "/reports/projects?limit=100", a, note="reports/projects full")["body"]
ids_full = [r["id"] for r in full["results"]]
walked = []
for off in (0, 2, 4):
    p = call("GET", f"/reports/projects?limit=2&offset={off}", a, note=f"reports/projects limit=2 offset={off}")
    walked += [r["id"] for r in p["body"]["results"]]
    print(f"  offset={off}: ids={[r['id'] for r in p['body']['results']]} next={p['body']['next']} previous={p['body']['previous']}")
print("  full      :", ids_full)
print("  walked    :", walked)
print("  ORDER STABLE / PAGES RECONSTRUCT FULL LIST:", walked == ids_full)

e = call("GET", "/reports/employees?limit=10&offset=10", a, note="reports/employees middle page")["body"]
print("\n  /reports/employees?limit=10&offset=10 -> count=%s next=%s previous=%s" % (e["count"], e["next"], e["previous"]))
ids = []
for off in range(0, 30, 10):
    p = call("GET", f"/reports/employees?limit=10&offset={off}", a, note=f"employees report page offset={off}")
    ids += [r["id"] for r in p["body"]["results"]]
fullE = call("GET", "/reports/employees?limit=100", a, note="reports/employees full")["body"]
print("  employees walked == full:", ids == [r["id"] for r in fullE["results"]], f"({len(ids)} vs {len(fullE['results'])})")

print("\n== manager scoping proof: project 9 must never appear for tarun ==")
seen = set()
for q in ["/projects?limit=100", "/projects?limit=100&scope=owned", "/projects?limit=100&scope=member",
          "/projects?limit=100&scope=all", "/reports/projects?limit=100", "/tasks?limit=100"]:
    p = call("GET", q, tok("manager"), note=f"tarun {q}")
    b = p["body"]
    if "reports" in q or "projects" in q:
        got = {r["id"] for r in b["results"]}
    else:
        got = {(r.get("project") or {}).get("id") for r in b["results"]}
    seen |= got
    print(f"  {q:42} -> {sorted(x for x in got if x)}")
print("  PROJECT 9 PRESENT ANYWHERE FOR TARUN:", 9 in seen)
dump("/Volumes/DATA/Automatic Create project/evidence/api/integration/"
     "pagination-ordering-and-scope-leak.md",
     "Pagination ordering stability and project-9 leak check")
