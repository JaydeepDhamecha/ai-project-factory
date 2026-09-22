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
.DS_Store *.pyc *.apk *.ipa \
.env .env.* *.env *.env.* .envrc"

# Every .env variant is excluded except the placeholder template, which must
# travel with the project. A backup like .env.before-x.bak is still a secret.
KEEP=".env.example"

# Build logs are noise; logs under evidence/ are the evidence itself, and the
# factory's honesty model rests on them. So *.log is excluded everywhere except
# the evidence tree, which is copied with the log exclusion lifted.
NOISE_LOGS="*.log"

copy_path() {
  [ -e "$1" ] || return 0
  mkdir -p "$TARGET/$(dirname "$1")"
  # evidence/ keeps its logs; everything else drops build noise.
  case "$1" in
    evidence|evidence/*) EX="$EXCLUDES" ;;
    *)                   EX="$EXCLUDES $NOISE_LOGS" ;;
  esac
  if command -v rsync >/dev/null 2>&1; then
    # shellcheck disable=SC2086
    rsync -a --include="$KEEP" $(for e in $EX; do printf -- '--exclude=%s ' "$e"; done) \
      "$1" "$TARGET/$(dirname "$1")/" || { err "copy failed: $1"; return 1; }
  else
    # shellcheck disable=SC2086
    ( tar -cf - $(for e in $EX; do printf -- '--exclude=%s ' "$e"; done) "$1" \
      | ( cd "$TARGET" && tar -xf - ) ) || { err "copy failed: $1"; return 1; }
  fi
  ok "$1 ($(du -sh "$TARGET/$1" 2>/dev/null | cut -f1 | tr -d ' '))"
}

# Manifest, state, inputs, evidence.
copy_path .project
copy_path input
copy_path evidence

# Platform source trees, whichever the manifest produced.
for d in backend web mobile shared api desktop admin integration tests; do copy_path "$d"; done

# Generated product documentation. Factory documentation stays in the factory.
#
# This EXCLUDES the factory's own documents and carries everything else. It used
# to do the opposite -- copy only docs whose name matched a
# factory/templates/docs/*.template.md template -- which silently dropped every
# product document an agent created beyond the template set. That is not a
# hypothetical: docs/user-manual.md (763 lines, the REQ-036 deliverable) had no
# template and was lost by every extraction until 2026-09-18.
#
# The list below names FACTORY files only. Adding a product name here would
# breach CLAUDE.md section 1. When a new factory document is added, add it here;
# anything not named is treated as the project's and travels with it.
FACTORY_DOCS="
agent-system.md
evidence-strategy.md
factory-architecture.md
factory-testing-strategy.md
orchestration.md
playwright-strategy.md
project-generation.md
project-state.md
"

mkdir -p "$TARGET/docs"
DOC_COUNT=0
DOC_SKIPPED=0
for d in docs/*.md; do
  [ -e "$d" ] || continue
  base="$(basename "$d")"
  if printf '%s\n' "$FACTORY_DOCS" | grep -qx "$base"; then
    DOC_SKIPPED=$((DOC_SKIPPED+1))
    continue
  fi
  cp "$d" "$TARGET/docs/" && DOC_COUNT=$((DOC_COUNT+1))
done
# docs/reference/ is factory material (agent prompts), never the project's.
ok "docs/ ($DOC_COUNT product documents carried, $DOC_SKIPPED factory documents left behind)"

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

# ------------------------------------------------------- secret sweep

# Belt and braces: the exclude list is a filter, not a guarantee. Anything
# env-shaped that survived the copy is deleted and reported, because this tree
# is about to become a git repository.
SWEPT=0
while IFS= read -r f; do
  [ -z "$f" ] && continue
  case "$(basename "$f")" in .env.example) continue ;; esac
  rm -f "$f" && SWEPT=$((SWEPT+1))
  printf '  \033[33mREMOVED\033[0m %s (env file — never leaves the factory)\n' "${f#"$TARGET"/}"
done <<SWEEP
$(find "$TARGET" -type f \( -name '.env' -o -name '.env.*' -o -name '*.env' -o -name '*.env.*' \) 2>/dev/null)
SWEEP
[ "$SWEPT" -eq 0 ] && ok "secret sweep: no env files in the extracted tree"

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
