#!/usr/bin/env bash
# Check the tools the factory needs before a run.
#
# Exit codes:
#   0  all hard requirements present
#   1  a hard requirement is missing
#
# Optional tools are reported, never fatal. The factory degrades honestly
# when one is absent — it records BLOCKED, it does not pretend.

set -uo pipefail

FAIL=0
pass()  { printf '  \033[32mOK\033[0m       %-22s %s\n' "$1" "${2:-}"; }
warn()  { printf '  \033[33mOPTIONAL\033[0m %-22s %s\n' "$1" "${2:-}"; }
fail()  { printf '  \033[31mMISSING\033[0m  %-22s %s\n' "$1" "${2:-}"; FAIL=1; }

need() {
  local name=$1 hint=$2
  if command -v "$name" >/dev/null 2>&1; then
    pass "$name" "$("$name" --version 2>&1 | head -1)"
  else
    fail "$name" "$hint"
  fi
}

want() {
  local name=$1 hint=$2
  if command -v "$name" >/dev/null 2>&1; then
    pass "$name" "$("$name" --version 2>&1 | head -1)"
  else
    warn "$name" "$hint"
  fi
}

echo
echo "Prerequisites"
echo "-------------"

need git     "required for version control and clean commits"
need node    "required for Playwright MCP (npx) and most generated stacks"
need npx     "ships with node; required to launch @playwright/mcp"
want python3 "used by scripts/validate-factory.sh for JSON checks"
want jq      "convenience only; validate-factory.sh falls back to python3"

echo
echo "Playwright MCP"
echo "--------------"

if [ -f .mcp.json ]; then
  if grep -q '"playwright"' .mcp.json 2>/dev/null; then
    pass ".mcp.json" "playwright server registered"
  else
    fail ".mcp.json" "no playwright server registered — browser testing will be BLOCKED"
  fi
else
  fail ".mcp.json" "absent — browser testing will be BLOCKED"
fi

echo
echo "  Registration is not availability. Claude Code must approve and start"
echo "  the server. Confirm with /test --probe once the session is open —"
echo "  this script cannot verify a live MCP connection from outside it."

echo
echo "Repository"
echo "----------"

if [ -d .git ]; then
  pass "git repository" "$(git rev-list --count HEAD 2>/dev/null || echo 0) commit(s)"
else
  warn "git repository" "not initialised — run: git init"
fi

if [ -f input/project-description.md ]; then
  pass "project description" "input/project-description.md"
else
  warn "project description" "absent — copy factory/templates/project/project-description.template.md"
fi

REFS=0
[ -d input/references ] && REFS=$(find input/references -type f ! -name '.gitkeep' 2>/dev/null | wc -l | tr -d ' ')
if [ "$REFS" -gt 0 ]; then
  pass "reference material" "$REFS file(s) in input/references/"
else
  warn "reference material" "none — the factory will work from the description alone"
fi

echo
if [ "$FAIL" -eq 0 ]; then
  echo "All hard requirements satisfied."
else
  echo "One or more hard requirements are missing. Install them before /start-project."
fi
echo

exit "$FAIL"
