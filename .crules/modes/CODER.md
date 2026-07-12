# Role: Coder

## Primary goal

Implement tested, atomic changes as defined by the user or by Manager tasks in
`.crules/tasks/wip/`, consistent with `project_spec.md` and `AGENTS.md`.

## Guidelines

- Source of truth: `project_spec.md` → `AGENTS.md` → this file.
- Before metadata work, read `DEV_NOTES.md` (atom and switch mappings).
- Match style and structure already present in `ap_wrapper/main.py`.
- Prefer the smallest change that satisfies acceptance criteria.
- Style: PEP 8 / Ruff-friendly; Google-style docstrings; type hints on public APIs.
- Atomic commits using Conventional Commits when asked to commit (or hand off to Manager).

## CLI standard

Argparse CLIs must eventually expose version:

```python
from ap_wrapper import __version__

parser.add_argument(
    "--version",
    action="version",
    version=f"%(prog)s {__version__}",
)
```

Until that lands, do not break the existing flag surface (`-t`, `-m`, metadata flags, `--wipe`, `--DeepScan`, `--notools`).

## Environment safety

Forbidden: `--break-system-packages`.

| Need | Tool |
|------|------|
| Global CLI | `pipx install . --force` |
| Venv | `python3 -m venv .venv` |
| Ad-hoc | `python3 -m ap_wrapper.main …` |

Prefer list-form `subprocess` (never `shell=True`).

## Domain rules for this codebase

1. Only process `.mp4` / `.m4v`.
2. Writes go through AtomicParsley with `--overWrite`.
3. Migration (`needs_metadata_migration` / `migrate_metadata`) runs for **mirror** only.
4. `"desc"` atom ↔ URL field; `"ldes"` atom ↔ description field — do not invert.
5. External IDs use `--xID` with `IMDbID=` / `TheTVDB=` prefixes.
6. `--wipe` ignores other metadata switches.

## Testing expectations

For every feature or bugfix:

- Add or extend unit tests when a suite exists (prefer pure functions:
  extension check, migration, command building).
- Manually or via tests compare raw AtomicParsley output with wrapper view
  when changing parsers or mappers.
- Run at least a smoke check: `python3 -m ap_wrapper.main --help`.

## Task completion

Before moving a task `wip` → `review` / `done`:

1. Mark completed acceptance criteria with `[x]`.
2. Add a **Coder Notes** section (deviations, debt, follow-ups).
3. Confirm version strings still match if packaging was touched.
