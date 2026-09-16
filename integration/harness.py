"""WorkHub cross-surface integration harness.

Drives REAL HTTP against the running Django service. No mocks, no stubs.
Every probe records method, URL, status, and a redacted body excerpt.

Secrets: the demo password is read from the seed command at run time and is
NEVER written to any transcript. `redact()` scrubs it plus JWTs.
"""
import json, os, re, subprocess, sys, time, urllib.error, urllib.request
from datetime import datetime, timezone

BASE = os.environ.get("WORKHUB_API", "http://localhost:8000/api/v1")
ROOT = "/Volumes/DATA/Automatic Create project"
SEED = f"{ROOT}/backend/apps/common/management/commands/seed_demo.py"

def _password():
    for line in open(SEED):
        if line.startswith("DEMO_PASSWORD"):
            return line.split('"')[1]
    raise SystemExit("DEMO_PASSWORD not found")

PASSWORD = _password()

ACCOUNTS = {
    "admin":    "jaydeep@example.com",
    "manager":  "tarun@example.com",
    "manager2": "neha@example.com",
    "employee": "priya@example.com",
    "outsider": "sanjay@example.com",
    "inactive": "rahul@example.com",
}

_JWT = re.compile(r"eyJ[A-Za-z0-9_\-]{6,}\.[A-Za-z0-9_\-]{6,}\.[A-Za-z0-9_\-]{6,}")

def redact(s):
    if not isinstance(s, str):
        s = json.dumps(s, default=str)
    s = s.replace(PASSWORD, "<DEMO_PASSWORD_REDACTED>")
    s = _JWT.sub("<JWT_REDACTED>", s)
    return s

PROBES = []

def call(method, path, token=None, body=None, headers=None, note=""):
    url = path if path.startswith("http") else BASE + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    t0 = time.time()
    try:
        with urllib.request.urlopen(req) as r:
            status, raw = r.getcode(), r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        status, raw = e.code, e.read().decode("utf-8", "replace")
    except Exception as e:
        status, raw = -1, f"TRANSPORT_ERROR: {e}"
    ms = int((time.time() - t0) * 1000)
    try:
        parsed = json.loads(raw)
    except Exception:
        parsed = None
    p = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
         "method": method, "url": url, "status": status, "ms": ms,
         "note": note, "body": parsed, "raw": raw}
    PROBES.append(p)
    return p

def login(role):
    p = call("POST", "/auth/login", body={"email": ACCOUNTS[role], "password": PASSWORD},
             note=f"login {role}")
    if p["status"] == 200:
        return p["body"]["access"], p["body"].get("refresh"), p["body"].get("user")
    return None, None, p

TOKENS = {}
def tok(role):
    if role == "anon":
        return None
    if role not in TOKENS:
        a, r, u = login(role)
        TOKENS[role] = a
    return TOKENS[role]

RUN_STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def _run_stamped(path):
    """Re-stamp a transcript path with THIS run's UTC time.

    Call sites pass a canonical *name* with no date in it. Writing to a fixed
    name silently destroys the earlier transcript - which is what happened on
    2026-09-15 (DEF-048; see the tombstones in evidence/api/integration/).
    Any stamp already present is stripped first, so a path that has been
    through here before does not accumulate stamps.
    """
    d, base = os.path.split(path)
    stem, ext = os.path.splitext(base)
    stem = re.sub(r"-\d{8}T\d{4,6}Z(-\d+)?$", "", stem)
    return os.path.join(d, f"{stem}-{RUN_STAMP}{ext}")


def _open_new(path):
    """Open THIS run's transcript for writing, creating it exclusively.

    RUN_STAMP is only unique to the second, so two runs that start inside the
    same second would collide. Refusing the second run would still lose its
    evidence - just loudly instead of silently - so the name is made unique
    instead: `-2`, `-3`, ... Mode "x" means an existing file is never
    truncated, even if another process creates it between the check and the
    open. There is no code path here that can overwrite a transcript.
    """
    stamped = _run_stamped(path)
    stem, ext = os.path.splitext(stamped)
    candidate, n = stamped, 1
    while True:
        try:
            return candidate, open(candidate, "x")
        except FileExistsError:
            n += 1
            candidate = f"{stem}-{n}{ext}"


def dump(path, title, extra=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    path, handle = _open_new(path)
    with handle as f:
        f.write(f"# {title}\n\n")
        f.write(f"Agent: `project-integration` · Generated {datetime.now(timezone.utc).isoformat(timespec='seconds')}\n")
        f.write(f"Target: `{BASE}` (live Django service, no mocks)\n\n")
        if extra:
            f.write(extra + "\n\n")
        f.write("---\n\n## Raw transcript\n\n")
        for i, p in enumerate(PROBES, 1):
            f.write(f"### {i}. `{p['method']} {p['url'].replace(BASE,'')}` -> **{p['status']}** ({p['ms']} ms)\n\n")
            if p["note"]:
                f.write(f"_{p['note']}_\n\n")
            body = p["raw"]
            if p["body"] is not None:
                body = json.dumps(p["body"], indent=1)
            if len(body) > 4000:
                body = body[:4000] + f"\n... [truncated, {len(body)} chars total]"
            f.write("```json\n" + redact(body) + "\n```\n\n")
    print(f"WROTE {path} ({len(PROBES)} probes)")
