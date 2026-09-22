#!/usr/bin/env bash
# Create a project workspace OUTSIDE the factory, with the factory runtime
# installed into it.
#
# This is the recommended way to start a project. The alternative — running
# /start-project inside the factory clone and extracting afterwards — still
# works and is still supported, but it builds the product inside the factory
# and needs scripts/extract-project.sh to separate them later.
#
# What this gives you that in-place generation does not:
#   * the factory clone stays clean; `git status` there never shows a product
#   * the project has /start-project, /resume, /test and /audit from day one,
#     because the runtime was installed, not left behind
#   * no extraction step, ever
#   * the project keeps the factory rules AS THEY WERE the day it started,
#     so a run stays reproducible while the factory moves on
#
# Exit codes:
#   0  workspace created
#   1  refused (bad target, target not empty, or target inside the factory)
#
# Usage: ./scripts/new-project.sh <target-dir> [project-name]

set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
FACTORY="$PWD"

ok()   { printf '  \033[32mOK\033[0m    %s\n' "$1"; }
err()  { printf '  \033[31mERROR\033[0m %s\n' "$1"; }
info() { printf '        %s\n' "$1"; }

TARGET="${1:-}"
if [ -z "$TARGET" ]; then
  err "No target directory given."
  info "Usage: ./scripts/new-project.sh ../my-project [\"My Project\"]"
  exit 1
fi

if [ -e "$TARGET" ] && [ -n "$(ls -A "$TARGET" 2>/dev/null)" ]; then
  err "Target '$TARGET' exists and is not empty. Refusing to overwrite."
  exit 1
fi

# The whole point is that the product does not live in the factory.
case "$(cd "$(dirname "$TARGET")" 2>/dev/null && pwd)/$(basename "$TARGET")" in
  "$FACTORY"|"$FACTORY"/*)
    err "Target is inside the factory. That is the model this script exists to avoid."
    info "Example: ./scripts/new-project.sh ../my-project"
    exit 1 ;;
esac

NAME="${2:-$(basename "$TARGET")}"
CREATED="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
VERSION="$(git -C "$FACTORY" rev-parse --short HEAD 2>/dev/null || echo unknown)"

printf '\n\033[1mCreating project workspace → %s\033[0m\n' "$TARGET"
mkdir -p "$TARGET" || { err "Could not create '$TARGET'."; exit 1; }
TARGET="$(cd "$TARGET" && pwd)"

# ------------------------------------------------------- runtime install

# The five permanent factory agents. Generated project-*.md agents are written
# into the workspace by agent-generator during the run, not copied from here.
mkdir -p "$TARGET/.claude/agents"
for a in orchestrator discovery agent-generator workflow-validator project-state; do
  cp ".claude/agents/$a.md" "$TARGET/.claude/agents/" \
    || { err "could not copy agent $a"; exit 1; }
done
ok ".claude/agents/ (5 factory agents)"

cp -R .claude/commands "$TARGET/.claude/" && ok ".claude/commands/ ($(ls .claude/commands/*.md | wc -l | tr -d ' ') commands)"
cp -R .claude/skills   "$TARGET/.claude/" && ok ".claude/skills/ ($(ls .claude/skills | wc -l | tr -d ' ') skills)"

# Rules, schemas and templates travel as a snapshot: this project keeps the
# factory it was born with.
cp -R factory "$TARGET/" && ok "factory/ (rules, schemas, templates — snapshot $VERSION)"

# The phase machine and the agent roster the commands reference.
mkdir -p "$TARGET/docs"
for d in orchestration project-state agent-system evidence-strategy \
         playwright-strategy project-generation factory-architecture; do
  [ -f "docs/$d.md" ] && cp "docs/$d.md" "$TARGET/docs/"
done
ok "docs/ (factory reference documents)"
cp AGENTS.md "$TARGET/" && ok "AGENTS.md"
cp .mcp.json "$TARGET/" && ok ".mcp.json (Playwright MCP, version-pinned)"

# --------------------------------------------------------- workspace skeleton

mkdir -p "$TARGET/input/references" "$TARGET/.project/state" "$TARGET/evidence"
touch "$TARGET/input/references/.gitkeep"
# The template is left AS a template. Copying it to project-description.md
# would make it non-empty, and /start-project's bootstrap treats a non-empty
# description as input — it would begin a run on a file of blank placeholders
# instead of telling the user there is nothing to build from.
cp factory/templates/project/project-description.template.md \
   "$TARGET/input/project-description.template.md"
ok "input/ (description template + references/)"

# The mode marker. A session here is in PROJECT MODE from the first turn,
# before any manifest exists.
cat > "$TARGET/.project/workspace.json" <<WS
{
  "kind": "factory-workspace",
  "projectName": "$NAME",
  "createdAt": "$CREATED",
  "factoryVersion": "$VERSION",
  "factoryOrigin": "$(git -C "$FACTORY" remote get-url origin 2>/dev/null || echo local)"
}
WS
ok ".project/workspace.json (mode marker)"

sed -e "s|{{PROJECT_NAME}}|$NAME|g" \
    -e "s|{{CREATED_AT}}|$CREATED|g" \
    -e "s|{{FACTORY_VERSION}}|$VERSION|g" \
    factory/templates/project/CLAUDE.workspace.template.md > "$TARGET/CLAUDE.md"
ok "CLAUDE.md (project workspace — PROJECT MODE)"

# --------------------------------------------------------------- gitignore

cat > "$TARGET/.gitignore" <<'PROJGI'
# Secrets
.env
.env.*
!.env.example
*.pem
*.key
*.p12
*.keystore
*.jks
secrets.json
credentials.json
service-account*.json

# OS / editor
.DS_Store
Thumbs.db
.idea/
.vscode/*
!.vscode/extensions.json
*.swp

# Dependencies and build output
node_modules/
dist/
build/
out/
.next/
.nuxt/
.svelte-kit/
coverage/
.venv/
venv/
__pycache__/
*.py[cod]
.pytest_cache/
.mypy_cache/
.ruff_cache/
target/
Pods/
.gradle/
*.apk
*.ipa
*.xcuserstate

# Test and tool output
playwright-report/
test-results/
blob-report/
.playwright-mcp/
*.log
logs/

# Heavy, regenerable evidence binaries. The reports themselves are committed.
evidence/**/*.zip
evidence/**/*.webm
evidence/**/*.mp4
evidence/**/videos/

# Local Claude Code state
.claude/settings.local.json

# User-supplied source material — NOT committed by default.
# These may be confidential (client PDFs, internal screenshots). They stay on
# disk so a later run can re-read them; they are simply not published.
# .project/source-manifest.json records name, size and SHA-256 of each one.
# Delete these two lines if your references are yours to publish.
input/references/*
!input/references/.gitkeep
PROJGI
ok ".gitignore (privacy default: references excluded)"

# ------------------------------------------------------------------ summary

cat <<SUMMARY

Workspace ready. The factory clone was not modified.

  1. Put your material in:
       $TARGET/input/project-description.md
       $TARGET/input/references/          (PDFs, screenshots, wireframes)

  2. Then:
       cd $TARGET
       claude
       /start-project

Everything the run produces — source, docs, evidence, state, generated agents —
stays in that directory. There is no extraction step.

SUMMARY
exit 0
