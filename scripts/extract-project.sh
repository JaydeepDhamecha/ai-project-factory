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
# Usage: ./scripts/extract-project.sh <target-dir> [--no-git] [--include-inputs]

set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
FACTORY="$PWD"

ok()   { printf '  \033[32mOK\033[0m    %s\n' "$1"; }
err()  { printf '  \033[31mERROR\033[0m %s\n' "$1"; }
info() { printf '        %s\n' "$1"; }

TARGET=""
NOGIT=0
INCLUDE_INPUTS=0
for arg in "$@"; do
  case "$arg" in
    --no-git)         NOGIT=1 ;;
    --include-inputs) INCLUDE_INPUTS=1 ;;
    -*)               err "Unknown option: $arg"
                      info "Usage: ./scripts/extract-project.sh ../my-project [--no-git] [--include-inputs]"
                      exit 1 ;;
    *)                if [ -z "$TARGET" ]; then TARGET="$arg"
                      else err "Unexpected argument: $arg"; exit 1; fi ;;
  esac
done

if [ -z "$TARGET" ]; then
  err "No target directory given."
  info "Usage: ./scripts/extract-project.sh ../my-project [--no-git] [--include-inputs]"
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

# --------------------------------------------- source manifest (privacy)
#
# The user's references may be confidential: a client PDF, an internal
# screenshot, a customer's wireframe. They are COPIED into the project tree so
# a later run can re-read them, but by default they are NOT COMMITTED.
#
# What is committed instead is a manifest — name, size and SHA-256 of each
# reference. A future reader can then tell whether the file they hold is the
# file the project was built from, without the factory having published it.
#
# --include-inputs opts back in.

SHA=""
if   command -v shasum   >/dev/null 2>&1; then SHA="shasum -a 256"
elif command -v sha256sum >/dev/null 2>&1; then SHA="sha256sum"
fi

json_escape() { printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'; }

if [ -d input/references ]; then
  mkdir -p "$TARGET/.project"
  MF="$TARGET/.project/source-manifest.json"
  REFN=0
  {
    printf '{\n'
    printf '  "generatedAt": "%s",\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf '  "committed": %s,\n' "$([ "$INCLUDE_INPUTS" -eq 1 ] && echo true || echo false)"
    printf '  "algorithm": "%s",\n' "$([ -n "$SHA" ] && echo sha256 || echo none)"
    printf '  "references": ['
    FIRST=1
    while IFS= read -r f; do
      [ -z "$f" ] && continue
      NM="$(json_escape "${f#input/references/}")"
      SZ="$(wc -c < "$f" 2>/dev/null | tr -d ' ')"
      H=""
      [ -n "$SHA" ] && H="$($SHA "$f" 2>/dev/null | awk '{print $1}')"
      [ "$FIRST" -eq 0 ] && printf ','
      FIRST=0
      printf '\n    {"name": "%s", "bytes": %s, "sha256": "%s"}' "$NM" "${SZ:-0}" "$H"
      REFN=$((REFN+1))
    done <<REFS
$(find input/references -type f ! -name '.gitkeep' ! -name '.DS_Store' 2>/dev/null | sort)
REFS
    [ "$FIRST" -eq 0 ] && printf '\n  '
    printf ']\n}\n'
  } > "$MF"
  REFN=$(grep -c '"name":' "$MF" 2>/dev/null | tr -d ' ')
  if [ -z "$SHA" ]; then
    info ".project/source-manifest.json (${REFN:-0} references; no sha256 tool found, hashes empty)"
  else
    ok ".project/source-manifest.json (${REFN:-0} references catalogued)"
  fi
fi

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

# The privacy default. References are on disk and re-readable by a later run,
# but they are not published unless the user asked for that.
if [ "$INCLUDE_INPUTS" -eq 0 ]; then
  if ! grep -q '^input/references/\*' "$TARGET/.gitignore" 2>/dev/null; then
    cat >> "$TARGET/.gitignore" <<'PROJGI2'

# User-supplied source material — NOT committed by default.
# These may be confidential (client PDFs, internal screenshots). They are
# present on disk, so `/resume` can still re-read them; they are simply not
# published. .project/source-manifest.json records the name, size and SHA-256
# of each one, so the project can still prove which sources it was built from.
# To commit them, re-extract with --include-inputs, or delete these two lines.
input/references/*
!input/references/.gitkeep
PROJGI2
    ok ".gitignore: input/references/ excluded (privacy default)"
  fi
else
  info "input/references/ WILL be committed (--include-inputs)"
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

Secrets: .env is ignored, .env.example is committed.
SUMMARY

if [ "$INCLUDE_INPUTS" -eq 0 ]; then
  cat <<'SRCOFF'
Source material: input/references/ is on disk but NOT committed. Its names,
sizes and SHA-256 hashes are in .project/source-manifest.json. Re-extract with
--include-inputs if you want the originals in the repository.
SRCOFF
else
  cat <<'SRCON'
Source material: input/references/ WILL be committed, because you passed
--include-inputs. Check that none of it is confidential before you push.
SRCON
fi

exit 0
