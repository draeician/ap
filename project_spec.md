# Project Specification — ap (ap-wrapper)

## Purpose

Provide a small, user-friendly CLI (`ap`) over AtomicParsley so media metadata
can be viewed, set, wiped, or mirrored without memorizing AtomicParsley flags
and MP4 atom names.

## Tech stack

- **Primary language**: Python 3
- **Minimum Python**: 3.6+ (`setup.py` / classifiers)
- **Packaging**: setuptools via `setup.py` (not yet migrated to `pyproject.toml`)
- **Package layout**: flat `ap_wrapper/` (not `src/`)
- **CLI**: `argparse` in `ap_wrapper/main.py`
- **External binary**: `AtomicParsley` on `PATH`
- **Install**: `pipx install .` (preferred) or `pip install .` in a venv
- **Lint/format target**: Ruff-compatible PEP 8 style (Ruff not yet wired in CI)
- **Tests**: none checked in yet; add `tests/` + pytest when features land

## Repository map

```text
ap/
├── AGENTS.md                 # Canonical agent rules
├── GROK.md                   # Grok entrypoint
├── project_spec.md           # This file
├── DEV_NOTES.md              # Atom / switch mapping reference
├── README.md
├── setup.py
├── ap_wrapper/
│   ├── __init__.py           # __version__
│   └── main.py               # CLI + AtomicParsley orchestration
├── .crules/
│   ├── modes/                # Swarm personas
│   └── tasks/{wip,review,done}/
└── .grok/
    ├── rules/                # Always-on Grok rules
    └── agents/               # Grok agent profiles
```

## Core behaviors

| Mode | Trigger | Behavior |
|------|---------|----------|
| View (friendly) | files only, no modify flags | Parse `-t` output; print fields |
| View (raw) | `-t` | Pass through AtomicParsley `-t` |
| Modify | metadata flags | Build argv + `--overWrite` |
| Mirror | `-m SOURCE` | Copy fields from source; migrate old format if needed |
| Meta | `--meta` | Title/show/season/episode from filename; with `-m`, mirror first then per-file meta |
| Wipe | `--wipe` | `--metaEnema --overWrite` (ignores other meta flags) |
| DeepScan | `--DeepScan` | Forward to AtomicParsley |
| No tools | any metadata write; `--notools` alone | Clear encoding tool atom (`--encodingTool ""`). Default on Modify/`--meta`; view-only never clears. `--notools` alone clears tools without other field changes |

Supported extensions: `.mp4`, `.m4v`.

## Metadata mapping (summary)

Authoritative table: `DEV_NOTES.md`.

Critical pairs:

- wrapper `--desc` / field `desc` ↔ AtomicParsley `--longdesc` ↔ atom `"ldes"`
- wrapper `--url` / field `url` ↔ AtomicParsley `--description` ↔ atom `"desc"`
- wrapper `--imdb` / `--thetvdb` ↔ `--xID` forms `IMDbID=…` / `TheTVDB=…`

## Architecture and conventions

- Keep orchestration in `ap_wrapper/main.py` until a task justifies splitting
  modules (parse / migrate / build_command / display).
- Prefer list-form `subprocess` calls; never `shell=True`.
- Migration helpers (`needs_metadata_migration`, `migrate_metadata`) only on mirror.
- User-facing messages stay concise; errors for missing AtomicParsley exit non-zero.
- Version consistency: `setup.py` and `ap_wrapper/__init__.py` must match.

### Known drift (fix when touching versioning)

As of bootstrap scan:

- `setup.py` → `1.2.0`
- `ap_wrapper/__init__.py` → `1.1.0`

Manager/Coder must reconcile to the **highest** version before the next
version-bump commit (monotonically: base is at least `1.2.0`).

## Environment safety

- Forbidden: `pip install --break-system-packages`
- Global CLI tools: `pipx`
- Local dev: `python3 -m venv .venv`
- Ad-hoc runs: `python3 -m ap_wrapper.main …`

## Testing commands

```bash
# Module help / smoke
python3 -m ap_wrapper.main --help

# Version (until argparse --version exists)
python3 -c "from ap_wrapper import __version__; print(__version__)"

# Raw vs wrapper view (requires sample media + AtomicParsley)
AtomicParsley sample.mp4 -t
python3 -m ap_wrapper.main sample.mp4

# Future suite
pytest
```

## Roadmap (seed backlog themes)

Tasks should be materialised under `.crules/tasks/wip/` when work starts:

1. Reconcile package version strings and add CLI `--version`.
2. Add pytest suite for extension checks, migration, and command building.
3. Optional: migrate packaging to `pyproject.toml` while keeping `ap` entry point.
4. Optional: split `main.py` into parse/display/command modules without CLI breaks.

## Status

- [x] Swarm bootstrap customized for this repository
- [x] Grok rules and agents installed under `.grok/`
- [ ] Version strings reconciled
- [ ] Automated tests present
