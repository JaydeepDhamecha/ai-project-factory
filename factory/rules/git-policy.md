# Git / GitHub Policy

## 1. Authorisation

| Operation | Authorisation |
|---|---|
| `git init`, `git add`, `git commit` in the local project | Allowed as part of normal work |
| `git branch`, `git checkout -b` | Allowed |
| `git push` | **Requires explicit user instruction, every time** |
| Creating a remote repository (`gh repo create`) | **Requires explicit user instruction** |
| Opening a pull request | **Requires explicit user instruction** |
| `git push --force`, history rewrite | **Requires explicit user instruction and confirmation** |
| Deleting branches or tags on a remote | **Requires explicit user instruction and confirmation** |

Authorisation is per-request. "Yes, push" for one commit does not authorise
future pushes.

Never commit directly to a default branch (`main`/`master`) in a repository
that already has history — create a branch.

---

## 2. Secrets

- `.env` is never committed. `.env.example` always is, with placeholder values.
- Before any commit, scan the staged diff for: API keys, tokens, private keys,
  connection strings with credentials, `.pem`/`.p12`/`.keystore` files,
  hard-coded passwords.
- If a secret is found in history, stop and report it. Do not rewrite shared
  history unilaterally.
- The factory itself contains no credentials and no machine-specific absolute
  paths.

---

## 3. Commit granularity for generated projects

Commit at meaningful boundaries, not per file:

| Boundary | Example message |
|---|---|
| Factory generation | `chore(factory): generate project agents and documentation` |
| Requirements/architecture docs | `docs: add PRD, requirements and architecture` |
| Feature slice complete | `feat(auth): implement authentication end to end` |
| Defect fix | `fix(records): correct pagination off-by-one on last page` |
| Test additions | `test(records): add browser regression pack` |
| Gate pass | `chore(release): pass GATE-SEC with zero high findings` |

Conventional Commits format: `type(scope): summary`.

Do not commit a broken build. If a slice cannot be completed, commit the
working portion behind a clear boundary and record the state.

---

## 4. What gets committed in a generated project

Committed:
- source, tests, configuration, migrations
- `docs/` — the generated documentation
- `.project/project.json` and `.project/state/**` — **the resume mechanism**
- `evidence/` markdown, JSON, logs and useful screenshots
- `input/` — the sources of truth, so a future run can re-read them

Not committed:
- `.env`, credentials, keys
- `node_modules/`, build output, caches
- videos, traces, large binaries
- `.claude/settings.local.json`

---

## 5. Factory repository hygiene

Because this repository is intended to be forked and shared:

- no client names, product names or domain nouns in factory files,
- no absolute paths from the author's machine,
- no OS-specific assumptions beyond POSIX shell in `scripts/`,
- scripts degrade gracefully when an optional tool is missing,
- `.gitignore` covers the toolchains the factory can generate.

`./scripts/validate-factory.sh` checks the first two mechanically.
