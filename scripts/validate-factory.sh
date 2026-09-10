#!/usr/bin/env bash
# Structural self-check of the factory.
#
# Checks only what a machine can check: presence, structure, and agreement
# between files. It cannot judge whether a rule is wise — only whether the
# factory contradicts itself.
#
# Exit codes:
#   0  no errors (warnings may be present)
#   1  at least one error
#
# Usage: ./scripts/validate-factory.sh [--quiet]

set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

QUIET=0
[ "${1:-}" = "--quiet" ] && QUIET=1

ERRORS=0
WARNINGS=0
CHECKS=0

section() { [ "$QUIET" -eq 1 ] || printf '\n\033[1m%s\033[0m\n%s\n' "$1" "$(printf '%.0s-' $(seq ${#1}))"; }
ok()      { CHECKS=$((CHECKS+1)); [ "$QUIET" -eq 1 ] || printf '  \033[32mOK\033[0m    %s\n' "$1"; }
err()     { CHECKS=$((CHECKS+1)); ERRORS=$((ERRORS+1));   printf '  \033[31mERROR\033[0m %s\n' "$1"; }
warn()    { CHECKS=$((CHECKS+1)); WARNINGS=$((WARNINGS+1)); [ "$QUIET" -eq 1 ] || printf '  \033[33mWARN\033[0m  %s\n' "$1"; }

# ---------------------------------------------------------------- 1. layout

section "1. Required layout"

for d in .claude/agents .claude/commands .claude/skills \
         factory/templates/agents factory/templates/docs \
         factory/templates/project factory/templates/features \
         factory/schemas factory/rules docs evidence examples \
         input/references scripts; do
  [ -d "$d" ] && ok "dir $d" || err "dir $d is missing"
done

for f in CLAUDE.md AGENTS.md README.md .gitignore .mcp.json; do
  [ -f "$f" ] && ok "file $f" || err "file $f is missing"
done

# ------------------------------------------------------- 2. factory agents

section "2. Factory agents"

for a in orchestrator discovery agent-generator workflow-validator project-state; do
  f=".claude/agents/$a.md"
  if [ ! -f "$f" ]; then
    err "agent $a is missing"
  elif ! head -1 "$f" | grep -q '^---$'; then
    err "agent $a has no YAML frontmatter"
  elif ! grep -q "^name: $a$" "$f"; then
    err "agent $a frontmatter name does not match its filename"
  else
    ok "agent $a"
  fi
done

# ------------------------------------------------------------- 3. commands

section "3. Commands"

for c in start-project status resume plan test audit release; do
  f=".claude/commands/$c.md"
  [ -f "$f" ] && ok "/$c" || err "/$c is missing ($f)"
done

# --------------------------------------------------------------- 4. skills

section "4. Skills"

for s in bug-fix-loop evidence-recording playwright-mcp reference-ingestion; do
  f=".claude/skills/$s/SKILL.md"
  [ -f "$f" ] && ok "skill $s" || err "skill $s is missing ($f)"
done

# ---------------------------------------------------------------- 5. rules

section "5. Rules"

for r in quality-gates definition-of-done source-of-truth agent-selection-matrix \
         status-vocabulary git-policy evidence-rules naming-conventions \
         agent-authoring-rules; do
  f="factory/rules/$r.md"
  [ -f "$f" ] && ok "rule $r" || err "rule $r is missing ($f)"
done

# -------------------------------------------------------------- 6. schemas

section "6. Schemas"

for s in project state features journal-event defect test-report; do
  f="factory/schemas/$s.schema.json"
  if [ ! -f "$f" ]; then
    err "schema $s is missing"
  elif python3 -c "import json,sys; json.load(open('$f'))" 2>/dev/null; then
    ok "schema $s parses"
  else
    err "schema $s is not valid JSON"
  fi
done

# ------------------------------------------------- 7. seed manifest conforms

section "7. Seed manifest"

SEED=factory/templates/project/project.template.json
if [ ! -f "$SEED" ]; then
  err "seed manifest is missing ($SEED)"
else
  OUT=$(python3 - "$SEED" factory/schemas/project.schema.json <<'PY'
import json,re,sys
seed,schema=sys.argv[1],sys.argv[2]
s=json.load(open(schema)); d=json.load(open(seed)); e=[]
for k in s['required']:
    if k not in d: e.append(f"missing required key: {k}")
if s.get('additionalProperties') is False:
    for k in d:
        if k not in s['properties']: e.append(f"key not allowed by schema: {k}")
for k,v in d.items():
    p=s['properties'].get(k,{})
    if 'enum'  in p and v not in p['enum']:  e.append(f"{k}={v!r} outside enum")
    if 'const' in p and v!=p['const']:       e.append(f"{k} does not equal const {p['const']!r}")
    if 'pattern' in p and isinstance(v,str) and not re.match(p['pattern'],v):
        e.append(f"{k}={v!r} fails pattern")
cap=s['properties']['capabilities']
for k in cap['required']:
    if k not in d.get('capabilities',{}): e.append(f"capabilities.{k} missing")
for k in d.get('capabilities',{}):
    if k not in cap['properties']: e.append(f"capabilities.{k} not allowed")
print("\n".join(e))
PY
)
  if [ -z "$OUT" ]; then ok "seed manifest conforms to project.schema.json"
  else while IFS= read -r l; do err "seed manifest: $l"; done <<< "$OUT"; fi
fi

# ------------------------------------------------------- 8. agent templates

section "8. Agent templates"

SECTIONS=("1. Purpose" "2. Responsibilities" "3. Inputs" "4. Required documents" \
          "5. Files it can modify" "6. Outputs" "7. Validation" \
          "8. Completion criteria" "9. Failure handling")

TPL_COUNT=0
for f in factory/templates/agents/*.md; do
  b=$(basename "$f")
  [ "$b" = "_TEMPLATE.md" ] && continue
  TPL_COUNT=$((TPL_COUNT+1))
  problems=""
  head -1 "$f" | grep -q '^---$' || problems="$problems no-frontmatter"
  for s in "${SECTIONS[@]}"; do
    grep -q "^## $s" "$f" || problems="$problems missing:'$s'"
  done
  if [ -n "$problems" ]; then err "template $b —$problems"; fi
done
[ "$TPL_COUNT" -gt 0 ] && ok "$TPL_COUNT agent templates have frontmatter and all 9 sections"

# Every template named by the selection matrix §2 must exist. Scope the scan to
# that section — §1 is the capability-flag table and its rows are not templates.
MATRIX_TPLS=$(awk '/^## 2\. Selection table/{f=1;next} /^## /{f=0} f' \
              factory/rules/agent-selection-matrix.md \
              | grep -oE '^\| `[a-z-]+` \|' | tr -d '|` ' | sort -u)
for t in $MATRIX_TPLS; do
  [ -f "factory/templates/agents/$t.md" ] \
    && ok "matrix template $t exists" \
    || err "selection matrix names '$t' but factory/templates/agents/$t.md is missing"
done

# --------------------------------------------------------- 9. doc templates

section "9. Document templates"

for t in $(grep -oE '`[a-z-]+\.template\.md`' factory/templates/docs/README.md \
           | tr -d '`' | sort -u); do
  [ -f "factory/templates/docs/$t" ] \
    && ok "doc template $t" \
    || err "factory/templates/docs/README.md lists '$t' but the file is missing"
done

# ------------------------------------------------------- 10. quality gates

section "10. Quality gates"

DEF=$(grep -ohE 'GATE-[A-Z]+' factory/rules/quality-gates.md | sort -u)
REF=$(grep -rhoE 'GATE-[A-Z]+' --include='*.md' --include='*.json' \
      .claude factory docs README.md AGENTS.md CLAUDE.md 2>/dev/null \
      | grep -v 'docs/reference' | sort -u)
for g in $REF; do
  echo "$DEF" | grep -qx "$g" && ok "$g defined" \
    || err "$g is referenced but not defined in quality-gates.md"
done
for g in $DEF; do
  echo "$REF" | grep -qx "$g" || warn "$g is defined but never referenced"
done

# -------------------------------------------------------- 11. placeholders

section "11. Template placeholders"

# Both template families are substituted at generation, so both are checked.
USED=$(grep -rhoE '\{\{[A-Z_0-9]+\}\}' \
       factory/templates/agents/*.md factory/templates/docs/*.template.md \
       --exclude=_TEMPLATE.md 2>/dev/null | sort -u)
DOCD=$(grep -oE '\{\{[A-Z_0-9<>]+\}\}' factory/rules/agent-authoring-rules.md | sort -u)

for p in $USED; do
  name=${p//[\{\}]/}
  hit=0
  echo "$DOCD" | grep -qx "$p" && hit=1
  # wildcard rows such as {{STACK_<AREA>}} stand for their whole family
  if [ "$hit" -eq 0 ]; then
    case "$name" in
      STACK_*) echo "$DOCD" | grep -q 'STACK_<AREA>' && hit=1 ;;
      PATH_*)  echo "$DOCD" | grep -q 'PATH_<AREA>'  && hit=1 ;;
      CAP_*)   echo "$DOCD" | grep -q 'CAP_<FLAG>'   \
               && grep -q "\`$name\`" factory/rules/agent-authoring-rules.md && hit=1 ;;
    esac
  fi
  [ "$hit" -eq 1 ] && ok "placeholder $p documented" \
    || err "placeholder $p is used but absent from agent-authoring-rules.md \u00a74"
done

# The meta-placeholders belong to _TEMPLATE.md alone.
for m in PLACEHOLDER TEMPLATE_ID CONDITION; do
  leak=$(grep -rl "{{$m}}" factory/templates/agents/*.md factory/templates/docs/*.template.md \
         --exclude=_TEMPLATE.md 2>/dev/null)
  [ -z "$leak" ] && ok "meta-placeholder {{$m}} confined to _TEMPLATE.md" \
    || err "meta-placeholder {{$m}} leaked into: $(echo $leak | tr '\n' ' ')"
done

# ---------------------------------------------- 12. factory documentation

section "12. Factory documentation"

# factory-testing-strategy is prefixed to avoid colliding with the generated
# product document docs/testing-strategy.md.
for d in factory-architecture agent-system orchestration project-state \
         evidence-strategy factory-testing-strategy playwright-strategy \
         project-generation; do
  f="docs/$d.md"
  [ -f "$f" ] && ok "doc $f" || err "doc $f is missing (README.md links it)"
done

# ------------------------------------------------------- 13. evidence tree

section "13. Evidence tree"

for d in discovery requirements architecture design database api implementation \
         playwright qa security performance regression release; do
  p="evidence/$d"
  if [ ! -d "$p" ]; then
    err "evidence/$d is missing"
  elif [ -z "$(ls -A "$p" 2>/dev/null)" ]; then
    err "evidence/$d is empty and has no .gitkeep — it will not survive a clone"
  else
    ok "evidence/$d"
  fi
done

# ----------------------------------------------------- 14. empty dirs / git

section "14. Clone integrity"

EMPTY=$(find . -path ./.git -prune -o -type d -empty -print 2>/dev/null | sed 's|^\./||')
if [ -z "$EMPTY" ]; then
  ok "no empty directories — the layout survives a clone"
else
  while IFS= read -r d; do
    err "empty directory '$d' will not survive a clone — add a .gitkeep"
  done <<< "$EMPTY"
fi

# ------------------------------------------------------ 15. honesty checks

section "15. Honesty invariants"

if grep -rn 'NOT_TESTED.*=.*PASS\|BLOCKED.*=.*PASS' --include='*.md' \
     .claude factory 2>/dev/null | grep -qv 'never'; then
  err "a factory file appears to equate NOT_TESTED or BLOCKED with PASS"
else
  ok "no file equates NOT_TESTED or BLOCKED with PASS"
fi

for f in CLAUDE.md factory/rules/quality-gates.md .claude/skills/playwright-mcp/SKILL.md; do
  grep -q 'NOT_TESTED' "$f" 2>/dev/null && ok "$f states the NOT_TESTED rule" \
    || warn "$f does not mention NOT_TESTED"
done

# --------------------------------------------------------------- summary

printf '\n\033[1mSummary\033[0m\n-------\n'
printf '  checks:   %s\n  errors:   %s\n  warnings: %s\n\n' "$CHECKS" "$ERRORS" "$WARNINGS"

if [ "$ERRORS" -eq 0 ]; then
  echo "Factory is structurally consistent."
  exit 0
else
  echo "Factory has $ERRORS structural error(s). Fix before running /start-project."
  exit 1
fi
