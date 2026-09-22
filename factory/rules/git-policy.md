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

## 4. Two repositories

The factory and the products it builds live in **separate repositories**. A
generated project is never committed into the factory repo.

```
GitHub
├── ai-project-factory     the reusable factory — this repository
├── my-project             a generated project
├── crm-project            another generated project
└── ecommerce-project      another generated project
```

### Two ways a project comes into being

| | Workspace (recommended) | In place (legacy, still supported) |
|---|---|---|
| Started by | `./scripts/new-project.sh ../my-project` | `/start-project` inside the factory clone |
| Product lives in | its own directory from the first turn | the factory working tree |
| Factory clone | untouched — `git status` stays clean | holds the product until extraction |
| Has `/resume`, `/test`, `/audit` | yes, installed at scaffold time | only while inside the factory clone |
| Separation step | none | `./scripts/extract-project.sh` |
| Marker | `.project/workspace.json` | none |

**In a workspace there is no two-repository problem to manage.** The directory
is the project repository; everything below about ignoring generated paths
applies to the factory clone only. A workspace ships with its own `.gitignore`
already written, and `git init` there is the user's call.

The rest of this section describes the in-place model.

### Inside a factory clone

Generation happens in place, but the factory's `.gitignore` excludes every
generated path, so `git add .` stages factory files only.

| Ignored (belongs to the product) | Committed (belongs to the factory) |
|---|---|
| `.project/` | `.claude/agents/{orchestrator,discovery,agent-generator,workflow-validator,project-state}.md` |
| `.claude/agents/project-*.md` | `.claude/commands/`, `.claude/skills/` |
| `backend/`, `web/`, `mobile/`, `shared/` | `factory/` |
| `evidence/**` (the `.gitkeep` skeleton stays) | factory `docs/`, `docs/reference/` |
| generated `docs/*.md` | `examples/`, `scripts/` |
| `input/project-description.md`, `input/references/*` | `AGENTS.md`, `CLAUDE.md`, `README.md`, `.gitignore` |

The project is still fully present and resumable — `.project/state/` is read
from the filesystem, never from git.

If you are about to `git add` a path from the left column, stop. It belongs to
the project.

### Giving an in-place project its own repository

Only needed for the in-place model. A workspace is already there.

```bash
./scripts/extract-project.sh ../my-project
```

This copies — never moves — the manifest, state, inputs, evidence, generated
documents, project agents and platform source trees into a new directory,
writes a project `.gitignore`, and makes one local commit. Dependency trees,
build output, caches and `.env` are excluded. Pushing remains the user's call.

---

## 5. What gets committed in a generated project repository

Committed:
- source, tests, configuration, migrations
- `docs/` — the generated documentation
- `.project/project.json` and `.project/state/**` — **the resume mechanism**
- `.project/source-manifest.json` — name, size and SHA-256 of every reference
- `evidence/` markdown, JSON, logs and useful screenshots
- `.claude/agents/project-*.md` — the project's own agents
- `input/project-description.md` — the brief, which the user wrote

Not committed:
- `.env`, credentials, keys
- `node_modules/`, virtual environments, build output, caches
- videos, traces, large binaries
- `.claude/settings.local.json`
- **`input/references/**` — the user's source material**

### Why references are excluded by default

A reference is the one artefact in a generated project the factory did not
write and cannot vouch for. It is a client's PDF, an internal screenshot, a
customer's wireframe. The old default committed it and told the user to opt out
before pushing — which fails in the direction that cannot be undone, because a
push is public the moment it lands and deleting the file later does not unpublish
it.

So the default is inverted. The references stay **on disk**, so `/resume` and
`/audit` can still re-read them; they are simply not published. What *is*
committed is `.project/source-manifest.json`:

```json
{
  "generatedAt": "2026-09-22T13:30:06Z",
  "committed": false,
  "algorithm": "sha256",
  "references": [
    {"name": "requirements.pdf", "bytes": 10155, "sha256": "c0b53b28…"}
  ]
}
```

That is enough for a reader to confirm the PDF in their hand is the PDF the
project was built from, without the factory having distributed it.

To publish the originals — your own material, an open brief, a public spec:

```bash
./scripts/extract-project.sh ../my-project --include-inputs
```

`committed` in the manifest records which way it went, so the choice is
auditable rather than inferred from what happens to be in the tree.

---

## 6. Factory repository hygiene

Because this repository is intended to be forked and shared:

- no client names, product names or domain nouns in factory files,
- no absolute paths from the author's machine,
- no OS-specific assumptions beyond POSIX shell in `scripts/`,
- scripts degrade gracefully when an optional tool is missing,
- `.gitignore` covers the toolchains the factory can generate,
- no generated product output is ever staged.

`./scripts/validate-factory.sh` checks the first two mechanically.
