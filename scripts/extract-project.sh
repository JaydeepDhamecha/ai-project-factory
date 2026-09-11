#!/usr/bin/env bash
# Lift a generated project out of the factory into its own directory and its
# own git repository.
#
# The factory repo and the product repo are separate (CLAUDE.md § 9). Generated
# output is ignored inside the factory clone; this script is how that output
# becomes a real, versioned project.
#
# It copies. It never moves or deletes anything in the factory, so the run
# stays resumable in place.
#
# Exit codes:
#   0  project extracted
#   1  refused (no project, bad target, or the target already has content)
#
# Usage: ./scripts/extract-project.sh <target-dir> [--no-git]

set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
FACTORY="$PWD"

ok()   { printf '  \033[32mOK\033[0m    %s\n' "$1"; }
err()  { printf '  \033[31mERROR\033[0m %s\n' "$1"; }
info() { printf '        %s\n' "$1"; }

TARGET="${1:-}"
NOGIT=0
[ "${2:-}" = "--no-git" ] && NOGIT=1

if [ -z "$TARGET" ]; then
  err "No target directory given."
  info "Usage: ./scripts/extract-project.sh ../my-project [--no-git]"
  exit 1
fi

# ------------------------------------------------------------ preconditions

if [ ! -f .project/project.json ]; then
  err "No generated project here (.project/project.json is missing)."
  info "Run /start-project first."
  exit 1
fi

if [ -e "$TARGET" ] && [ -n "$(ls -A "$TARGET" 2>/dev/null)" ]; then
  err "Target '$TARGET' exists and is not empty. Refusing to overwrite."
  exit 1
fi

case "$(cd "$(dirname "$TARGET")" 2>/dev/null && pwd)/$(basename "$TARGET")" in
  "$FACTORY"|"$FACTORY"/*)
    err "Target is inside the factory. Extract to a sibling directory instead."
    info "Example: ./scripts/extract-project.sh ../my-project"
    exit 1 ;;
esac

NAME="$(basename "$TARGET")"
printf '\n\033[1mExtracting generated project → %s\033[0m\n' "$TARGET"

mkdir -p "$TARGET" || { err "Could not create '$TARGET'."; exit 1; }

# ------------------------------------------------------------------- copy

# Dependency trees, build output, caches and secrets are never copied — they
# are regenerable, enormous, or must not leave the machine.
EXCLUDES="node_modules .venv venv __pycache__ .pytest_cache .mypy_cache \
.ruff_cache dist build out .next .nuxt .svelte-kit coverage target Pods \
.gradle playwright-report test-results blob-report .playwright-mcp .git \
.DS_Store .env *.log *.pyc *.apk *.ipa"

copy_path() {
  [ -e "$1" ] || return 0
  mkdir -p "$TARGET/$(dirname "$1")"
  if command -v rsync >/dev/null 2>&1; then
    # shellcheck disable=SC2086
    rsync -a $(for e in $EXCLUDES; do printf -- '--exclude=%s ' "$e"; done) \
      "$1" "$TARGET/$(dirname "$1")/" || { err "copy failed: $1"; return 1; }
  else
    # shellcheck disable=SC2086
    ( tar -cf - $(for e in $EXCLUDES; do printf -- '--exclude=%s ' "$e"; done) "$1" \
      | ( cd "$TARGET" && tar -xf - ) ) || { err "copy failed: $1"; return 1; }
  fi
  ok "$1 ($(du -sh "$TARGET/$1" 2>/dev/null | cut -f1 | tr -d ' '))"
}

# Manifest, state, inputs, evidence.
copy_path .project
copy_path input
copy_path evidence

# Platform source trees, whichever the manifest produced.
for d in backend web mobile shared api desktop admin; do copy_path "$d"; done

# Generated product documentation. Factory documentation stays in the factory.
mkdir -p "$TARGET/docs"
DOC_COUNT=0
for t in factory/templates/docs/*.template.md; do
  [ -e "$t" ] || continue
  d="docs/$(basename "$t" .template.md).md"
  if [ -f "$d" ]; then cp "$d" "$TARGET/$d" && DOC_COUNT=$((DOC_COUNT+1)); fi
done
[ -f docs/capability-profile.md ] && cp docs/capability-profile.md "$TARGET/docs/" && DOC_COUNT=$((DOC_COUNT+1))
ok "docs/ ($DOC_COUNT generated documents)"

# The project's own agents, plus the state custodian it needs to resume.
mkdir -p "$TARGET/.claude/agents"
AGENT_COUNT=0
for a in .claude/agents/project-*.md; do
  [ -e "$a" ] || continue
  cp "$a" "$TARGET/.claude/agents/" && AGENT_COUNT=$((AGENT_COUNT+1))
done
ok ".claude/agents/ ($AGENT_COUNT project agents)"

# ------------------------------------------------------------- project .gitignore

if [ ! -f "$TARGET/.gitignore" ]; then
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
PROJGI
  ok ".gitignore (project)"
fi

# --------------------------------------------------------------- git init

if [ "$NOGIT" -eq 0 ] && command -v git >/dev/null 2>&1; then
  if [ -d "$TARGET/.git" ]; then
    info "Target already a git repository — leaving history alone."
  else
    ( cd "$TARGET" \
      && git init -q \
      && git add -A \
      && git -c user.name= -c user.email= commit -q \
           -m "feat: import ${NAME} generated by ai-project-factory" \
      ) && ok "git repository initialised with one commit" \
        || info "git init/commit skipped (configure user.name and user.email, then commit manually)"
  fi
fi

# ----------------------------------------------------------------- summary

cat <<SUMMARY

Done. The factory is untouched and the run here is still resumable.

  cd $TARGET
  git remote add origin <your-project-remote>
  git push -u origin main        # you push; the factory never does

Secrets: .env is ignored, .env.example is committed. Check the diff before
your first push — especially input/references/ if your source material is
confidential.
SUMMARY
exit 0
