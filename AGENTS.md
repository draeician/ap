# Agent System Status: [CUSTOMIZED]

Canonical instruction file for Grok Build, Codex, Claude Code, Cursor, and human contributors.

Read this file completely before changing code. When instructions conflict:

`project_spec.md` > `AGENTS.md` > `.crules/modes/*` > tool-specific entrypoints (`GROK.md`, `CLAUDE.md`, `CODEX.md`)

## Project identity

This repository is **ap** (`ap-wrapper`): a Python CLI wrapper around
[AtomicParsley](https://github.com/wez/atomicparsley) for viewing and editing
MP4/M4V metadata.

- Package: `ap_wrapper`
- CLI entry point: `ap` → `ap_wrapper.main:main`
- Packaging: `setup.py` (setuptools) + `ap_wrapper/__init__.py` (`__version__`)
- External dependency: `AtomicParsley` must be on `PATH`
- Authoritative metadata mapping notes: `DEV_NOTES.md`

## Required reading before implementation

1. `AGENTS.md` (this file)
2. `project_spec.md`
3. `DEV_NOTES.md` for atom / switch mappings
4. Active task under `.crules/tasks/wip/` (if present)
5. Relevant swarm mode under `.crules/modes/` when acting as Manager or Coder

## Swarm SOP (crules)

This repo uses the **Skeleton Swarm** workflow from crules.

| Path | Role |
|------|------|
| `.crules/modes/MANAGER.md` | Orchestrate, version, task pipeline — do not implement product code |
| `.crules/modes/CODER.md` | Implement atomic, tested changes from tasks / user request |
| `.crules/modes/GIT_POLICY.md` | Conventional commits, branching, secret scan, release |
| `.crules/modes/BOOTSTRAPPER.md` | Only when `AGENTS.md` status is `[TEMPLATE]` |
| `.crules/tasks/{wip,review,done}/` | Markdown task files with acceptance criteria |
| `project_spec.md` | Single source of truth for scope and conventions |
| `.grok/rules/` | Always-on Grok project rules (SOP + style) |
| `.grok/agents/` | Optional Grok agent profiles (manager / coder / swarm) |

Default persona for implementation work: **Coder**.
Default persona for planning, commits, releases, backlog: **Manager**.

Shortcut keywords (act as Manager, then follow `GIT_POLICY.md`):

- **commit** — secret scan, version bump, verify CLI version, conventional commit
- **branch** — create `feat/` / `fix/` / `docs/` / `chore/` / `refactor/` branch
- **release** — verify version, changelog summary, tag, push tags

## Hard boundaries

1. Do not invent AtomicParsley atoms or switches. Prefer `DEV_NOTES.md` and
   real `AtomicParsley --help` / `-t` output.
2. Supported media extensions only: `.mp4`, `.m4v`.
3. Metadata writes always use AtomicParsley’s in-place overwrite behavior
   (`--overWrite`). Do not introduce a “write to new file” path unless the
   user explicitly asks and acceptance criteria cover it.
4. Migration of old `desc`/`longdesc` layouts applies in **mirror** mode only —
   never rewrite fields during pure view.
5. Never use `pip install --break-system-packages`.
6. Never commit secrets, credentials, or sample media with private content.
7. Do not expand scope into a media library manager, GUI, or network client.

## Coding style (Python)

- Python 3.6+ compatible unless a task explicitly raises the floor.
- Type hints on public functions; Google-style docstrings.
- Prefer stdlib only (`argparse`, `subprocess`, `re`, `typing`, …).
- No `shell=True` in `subprocess` — pass argv lists.
- snake_case functions/vars; PascalCase only if classes are introduced.
- Keep CLI surface stable: document any flag rename/removal as breaking.
- Match existing `ap_wrapper/main.py` patterns before introducing modules.

## Versioning and packaging

- Version strings must agree across:
  - `setup.py` (`version=...`)
  - `ap_wrapper/__init__.py` (`__version__`)
  - Git tags when releasing
- `setup.py` is master until a `pyproject.toml` migration lands.
- CLI must expose `--version` via argparse `action="version"` once added;
  until then, prefer `python3 -c "from ap_wrapper import __version__; print(__version__)"`.
- Bump rules: `feat` → minor, `fix`/`docs`/`chore`/`refactor` → patch,
  `BREAKING CHANGE` / `!` → major. Versions only increase.

## Testing discipline

- Prefer the smallest test that proves the change (pytest when a suite exists).
- For metadata behavior, verify with both:
  - raw: `AtomicParsley file.mp4 -t`
  - wrapper: `python3 -m ap_wrapper.main …` or installed `ap`
- Do not weaken assertions to green a bad implementation.
- Manual check list for atom work is in `DEV_NOTES.md`.

## Git discipline

- Follow `.crules/modes/GIT_POLICY.md`.
- Conventional commits; imperative subject; max ~72 chars.
- Prefer feature branches; do not force-push `main`.
- Track `.crules/`, `AGENTS.md`, `project_spec.md`, and `.grok/` in git.

## Work discipline

- Minimum code that solves the stated problem. Nothing speculative.
- Touch only what you must. Clean up only your own mess.
- Surface tradeoffs; do not hide confusion.
- Define success criteria; loop until verified.
- When a task file exists, update acceptance criteria and Coder Notes before
  moving it `wip` → `review` → `done`.

## Grok-specific layout

| Path | Purpose |
|------|---------|
| `GROK.md` | Thin Grok entrypoint → points here |
| `.grok/rules/*.md` | Auto-loaded project rules |
| `.grok/agents/*.md` | Named agent profiles (`manager`, `coder`, `swarm`) |

Use `grok inspect` to confirm rules and agents load.
