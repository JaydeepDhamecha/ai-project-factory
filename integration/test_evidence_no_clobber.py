#!/usr/bin/env python3
"""Regression guard for DEF-048 — an evidence transcript must never be
destroyed by a later run.

What went wrong (2026-09-15): every probe passed `harness.dump()` a *canonical*
filename carrying the stamp of the run that first produced it
(`...-20260911T1240Z.md`), and `dump()` opened that name `"w"`. Re-running the
suite truncated the earlier transcript in place. Three 2026-09-11 transcripts
were lost that way and are unrecoverable; tombstones stand in their place in
`evidence/api/integration/`. Nothing here reconstructs them.

Three independent properties are asserted, because the defect had three parts
and any one of them coming back reopens it:

  A. Two runs in the same wall-clock second both keep their transcript.
     A stamp is only unique to the second, so "stamp the filename" alone turns
     the clobber into an abort — the second run's evidence is still lost, just
     more loudly. The name must be made unique, not the run refused.
  B. An existing file is never truncated, whatever name is asked for.
     Asserted through the real `dump()`, against a file this test wrote first.
  C. No probe hard-codes a date stamp in the path it passes to `dump()`.
     A literal stamp in the source is what made (A) and (B) reachable, and it
     also dates today's output with a date that is not today's.

Run against a different harness with WORKHUB_HARNESS=/path/to/harness.py --
that is how the RED direction is demonstrated, against a reconstruction of the
pre-fix `dump()`.

    python3 integration/test_evidence_no_clobber.py

Exit 0 = all properties hold. Exit 1 = at least one does not.
No server, no database, no network: it writes only into a temp directory.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HARNESS = os.environ.get("WORKHUB_HARNESS", os.path.join(ROOT, "integration", "harness.py"))
PROBES = [
    "probe_authz.py",
    "probe_contract.py",
    "probe_pagination_order.py",
    "probe_auth_lifecycle.py",
    "probe_writes.py",
    "probe_od_status.py",
    "probe_token_expiry.py",
    "test_seam.py",
]

# A run that imports the harness, seeds one probe record and dumps it to the
# canonical (stamp-bearing) name the probes historically used.
CHILD = r"""
import importlib.util, sys
spec = importlib.util.spec_from_file_location("harness_under_test", %(harness)r)
h = importlib.util.module_from_spec(spec)
sys.modules["harness_under_test"] = h
spec.loader.exec_module(h)
h.PROBES.append({"ts": "x", "method": "GET", "url": h.BASE + "/ping", "status": 200,
                 "ms": 1, "note": %(note)r, "body": None, "raw": %(note)r})
h.dump(%(path)r, "no-clobber probe run")
"""

FAILURES = []


def check(name, condition, detail=""):
    print(("  PASS  " if condition else "  FAIL  ") + name + (f"\n          {detail}" if detail else ""))
    if not condition:
        FAILURES.append(name)


def run_child(harness, path, note, cwd):
    src = CHILD % {"harness": harness, "path": path, "note": note}
    return subprocess.run([sys.executable, "-c", src], cwd=cwd,
                          capture_output=True, text=True)


def main():
    print(f"harness under test: {HARNESS}")
    tmp = tempfile.mkdtemp(prefix="def048-")
    try:
        # ---- A. two runs in the same second, both transcripts survive -------
        canonical = os.path.join(tmp, "A", "contract-conformance-20260911T1240Z.md")
        r1 = run_child(HARNESS, canonical, "RUN-ONE", ROOT)
        r2 = run_child(HARNESS, canonical, "RUN-TWO", ROOT)
        produced = sorted(os.listdir(os.path.join(tmp, "A"))) if os.path.isdir(os.path.join(tmp, "A")) else []
        bodies = {}
        for fname in produced:
            bodies[fname] = open(os.path.join(tmp, "A", fname)).read()
        kept_one = [f for f, b in bodies.items() if "RUN-ONE" in b]
        kept_two = [f for f, b in bodies.items() if "RUN-TWO" in b]

        check("A1. both runs exited 0",
              r1.returncode == 0 and r2.returncode == 0,
              f"rc={r1.returncode},{r2.returncode} stderr2={r2.stderr.strip()[-300:]}")
        check("A2. two distinct transcripts on disk",
              len(produced) == 2, f"found {produced}")
        check("A3. the first run's transcript still holds the first run's probe",
              len(kept_one) == 1, f"files containing RUN-ONE: {kept_one}")
        check("A4. the second run's transcript holds the second run's probe",
              len(kept_two) == 1, f"files containing RUN-TWO: {kept_two}")
        check("A5. no file carries the hard-coded 2026-09-11 stamp as its whole name",
              "contract-conformance-20260911T1240Z.md" not in produced,
              f"found {produced}")

        # ---- B. an existing file is never truncated -------------------------
        bdir = os.path.join(tmp, "B")
        os.makedirs(bdir)
        victim = os.path.join(bdir, "role-authz-reaudit-20260911T1230Z.md")
        sentinel = "IRREPLACEABLE EVIDENCE FROM AN EARLIER RUN\n"
        with open(victim, "w") as f:
            f.write(sentinel)
        r3 = run_child(HARNESS, victim, "RUN-THREE", ROOT)
        survived = open(victim).read() if os.path.exists(victim) else ""
        check("B1. the pre-existing transcript is byte-for-byte intact",
              survived == sentinel,
              f"rc={r3.returncode}; file is now {len(survived)} bytes")
        holders = [f for f in os.listdir(bdir)
                   if "RUN-THREE" in open(os.path.join(bdir, f)).read()]
        check("B2. the new run's output landed in a file of its own, not on top of the victim",
              holders == [f for f in holders if f != os.path.basename(victim)] and len(holders) == 1,
              f"RUN-THREE is in {holders}; dir holds {sorted(os.listdir(bdir))}; "
              f"stderr={r3.stderr.strip()[-300:]}")

        # ---- C. no probe hard-codes a date stamp in a dump() path ----------
        stamp = re.compile(r"\d{8}T\d{4,6}Z")
        for probe in PROBES:
            path = os.path.join(ROOT, "integration", probe)
            if not os.path.exists(path):
                check(f"C. {probe} exists", False, "missing")
                continue
            source = open(path).read()
            offenders = []
            for match in re.finditer(r"dump\(\s*(?P<args>(?:[^()]|\([^()]*\))*?)\)", source):
                args = match.group("args")
                first = args.split(",")[0] if "," in args else args
                # the path argument is everything up to the first top-level comma
                head = args.split('",\n')[0]
                if stamp.search(head) or stamp.search(first):
                    offenders.append(head.strip()[:120])
            check(f"C. {probe} passes dump() a path with no literal date stamp",
                  not offenders, "; ".join(offenders))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    if FAILURES:
        print(f"DEF-048 GUARD: FAIL ({len(FAILURES)} failing properties)")
        for f in FAILURES:
            print(f"  - {f}")
        return 1
    print("DEF-048 GUARD: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
