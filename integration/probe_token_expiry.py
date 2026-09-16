"""Token expiry across the seam — the one auth stage that had never been observed.

METHOD A (this file): a SEPARATE backend process on :8001 started with
JWT_ACCESS_MINUTES=1 and JWT_REFRESH_DAYS=0. Real wall-clock expiry, observed
over real HTTP. The :8000 process serving the committed configuration is NOT
touched and NOT reconfigured.

Nothing here back-dates or hand-crafts a token: every token measured was issued
by the server's own POST /auth/login.
"""
import json, os, sys, time
os.environ["WORKHUB_API"] = "http://localhost:8001/api/v1"
sys.path.insert(0, "/Volumes/DATA/Automatic Create project/integration")
from harness import *

FAIL = []
def check(name, got, want):
    ok = got == want
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: got={got!r} want={want!r}")
    if not ok: FAIL.append((name, got, want))

def envelope(p):
    b = p["body"] if isinstance(p["body"], dict) else {}
    return p["status"], b.get("code"), b.get("error")

print("== lifetimes this process was started with ==")
print("  JWT_ACCESS_MINUTES=1  JWT_REFRESH_DAYS=0  (port 8001, separate process)")

print("\n== T0: obtain ==")
p = call("POST", "/auth/login", body={"email": ACCOUNTS["admin"], "password": PASSWORD}, note="login on :8001")
check("login 200", p["status"], 200)
acc, ref = p["body"]["access"], p["body"]["refresh"]
t0 = time.time()

print("\n== T0: the ACCESS token is alive right now ==")
me = call("GET", "/auth/me", acc, note="T0 access on /auth/me")
check("fresh access /auth/me 200", me["status"], 200)
v = call("POST", "/auth/verify", body={"token": acc}, note="T0 verify fresh access")
check("fresh access /auth/verify 200", v["status"], 200)

print("\n== T0: the REFRESH token is already past its lifetime (REFRESH_DAYS=0) ==")
r = call("POST", "/auth/refresh", body={"refresh": ref}, note="T0 expired refresh -> /auth/refresh")
s, c, e = envelope(r)
print(f"  /auth/refresh with expired refresh -> {s} code={c!r} error={e!r}")
check("expired refresh rejected 401", s, 401)
check("expired refresh carries a documented code", c in ("AUTH_FAILED", "TOKEN_EXPIRED"), True)
rv = call("POST", "/auth/verify", body={"token": ref}, note="T0 verify expired refresh")
s2, c2, e2 = envelope(rv)
print(f"  /auth/verify with expired refresh -> {s2} code={c2!r}")
check("/auth/verify AGREES the expired refresh is invalid (SEC-F-014)", s2, 401)
R_REFRESH = {"refresh_endpoint": (s, c, e), "verify_endpoint": (s2, c2, e2)}

print("\n== waiting out the 60s access lifetime (real clock, no back-dating) ==")
while time.time() - t0 < 68:
    time.sleep(4)
    print(f"  +{int(time.time()-t0)}s", flush=True)
print(f"  elapsed {int(time.time()-t0)}s — the access token minted at T0 is now past its 60s lifetime")

print("\n== T0+68s: the SAME access token, re-presented ==")
me2 = call("GET", "/auth/me", acc, note="expired access on /auth/me")
s3, c3, e3 = envelope(me2)
print(f"  /auth/me            -> {s3} code={c3!r} error={e3!r}")
check("expired access rejected 401", s3, 401)
check("expired access carries a documented code", c3 in ("AUTH_FAILED", "TOKEN_EXPIRED"), True)

for ep in ["/employees?limit=1", "/projects?limit=1", "/dashboard"]:
    q = call("GET", ep, acc, note=f"expired access on {ep}")
    check(f"expired access rejected on {ep}", (q["status"], (q["body"] or {}).get("code")), (s3, c3))

print("\n== T0+68s: /auth/verify must AGREE about the expired access token (SEC-F-014) ==")
v2 = call("POST", "/auth/verify", body={"token": acc}, note="verify expired access")
s4, c4, e4 = envelope(v2)
print(f"  /auth/verify        -> {s4} code={c4!r} error={e4!r}")
check("/auth/verify AGREES the expired access is invalid", s4, 401)
check("/auth/verify does NOT answer 200 for a token /auth/me refused", s4 == me2["status"], True)

print("\n== T0+68s: the expired access token is not accepted as a refresh either ==")
r2 = call("POST", "/auth/refresh", body={"refresh": acc}, note="expired access presented as refresh")
check("expired access as refresh -> 401", r2["status"], 401)

print("\n== a FRESH login on this process still works (expiry, not breakage) ==")
p2 = call("POST", "/auth/login", body={"email": ACCOUNTS["admin"], "password": PASSWORD}, note="fresh login after expiry")
check("re-login 200", p2["status"], 200)
check("fresh access works", call("GET", "/auth/me", p2["body"]["access"], note="fresh access after expiry")["status"], 200)

print("\n== which code is actually emitted ==")
codes = {"expired access /auth/me": c3, "expired access /auth/verify": c4,
         "expired refresh /auth/refresh": R_REFRESH["refresh_endpoint"][1],
         "expired refresh /auth/verify": R_REFRESH["verify_endpoint"][1]}
print(json.dumps(codes, indent=1))
print("  TOKEN_EXPIRED emitted anywhere:", "TOKEN_EXPIRED" in codes.values())

print("\n== fixture untouched (this probe is read-only apart from logins) ==")
a = tok("admin")
for lbl, ep, want in [("employees","/employees?limit=1",28),("projects","/projects?limit=1&scope=all",6),("tasks","/tasks?limit=1",41)]:
    check(f"{lbl} still {want}", (call("GET", ep, a, note=f"baseline {lbl}")["body"] or {}).get("count"), want)

print(f"\n==== {len(FAIL)} FAILED ASSERTION(S) ====")
for n,g,w in FAIL: print(f"  FAILED: {n} got={g!r} want={w!r}")
dump("/Volumes/DATA/Automatic Create project/evidence/api/integration/token-expiry.md",
     "Token expiry observed on a real clock — access and refresh, plus /auth/verify agreement (SEC-F-014)")
sys.exit(1 if FAIL else 0)
