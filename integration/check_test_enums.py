"""Resolve every Model.Enum.MEMBER referenced by the authored test file.

No database connection: django.setup() loads apps and settings only. This is
the check that would have caught Status.TODO before the file ever entered the
tree, and it checks ALL of them rather than only the one that happened to error.
"""
import os, re, sys, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.accounts.models import User          # noqa: E402
from apps.projects.models import Project       # noqa: E402
from apps.tasks.models import Comment, Task    # noqa: E402

NS = {"User": User, "Project": Project, "Task": Task, "Comment": Comment}
src = open("tests/test_authz_negatives.py").read()
refs = sorted(set(re.findall(r"\b(User|Project|Task|Comment)\.([A-Za-z_]+)\.([A-Z_]+)\b", src)))

bad = 0
for model, enum, member in refs:
    try:
        val = getattr(getattr(NS[model], enum), member)
        print(f"  ok      {model}.{enum}.{member} = {val!r}")
    except AttributeError as e:
        print(f"  MISSING {model}.{enum}.{member}  -> {e}")
        bad += 1

# also: string literals passed as status/priority in request bodies
lits = sorted(set(re.findall(r'"(?:status|priority)":\s*"([a-z_]+)"', src)))
valid = {v for v in Task.Status.values} | {v for v in Task.Priority.values} | {v for v in Project.Status.values}
for l in lits:
    if l in valid:
        print(f"  ok      literal {l!r}")
    else:
        print(f"  INVALID literal {l!r} — not a Status or Priority value")
        bad += 1

print(f"\n{len(refs)} enum refs + {len(lits)} literals checked, {bad} bad")
sys.exit(1 if bad else 0)
