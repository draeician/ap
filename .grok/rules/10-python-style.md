# Python coding style (ap)

Apply on any `*.py` edit under this repository.

## Language and packaging

- Target Python 3.6+ compatibility unless a task raises the floor.
- Package lives in flat `ap_wrapper/` (not `src/`).
- Prefer stdlib. Do not add production dependencies without an explicit task.
- Entry point: `ap` → `ap_wrapper.main:main`.

## Style

1. PEP 8 / Ruff-friendly layout; 4-space indent.
2. Type hints on public functions; return types included.
3. Google-style docstrings for public callables.
4. f-strings for formatting.
5. `snake_case` functions and variables; `PascalCase` classes only if introduced.
6. Prefer explicit `is None` checks for singletons.
7. Narrow `except` clauses; preserve causes when re-raising.
8. Use `with` for resources; no bare `open` without context managers.

## Subprocess and safety

- Always pass argv **lists** to `subprocess` — never `shell=True`.
- Do not use `pip install --break-system-packages`.
- Install with `pipx` or a project venv; ad-hoc via `python3 -m ap_wrapper.main`.

## Domain-specific

- Valid extensions: `.mp4`, `.m4v` only.
- In-place writes: AtomicParsley `--overWrite`.
- Mirror-only migration between old/new desc URL layouts.
- Atom map (do not invert):
  - `"ldes"` / `--longdesc` → description (`desc`)
  - `"desc"` / `--description` → URL (`url`)
  - `"xid "` via `--xID` for IMDb / TheTVDB

## Structure preference

Keep changes local to existing modules until size or clarity demands a split.
If splitting, preserve the public CLI flag surface.

## Tests

- Prefer pure-function unit tests for parsers, migration, and command builders.
- Do not weaken tests to pass a bad change.
- Name tests clearly; one concern per test function.
