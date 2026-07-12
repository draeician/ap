# Git, versioning, and release

Follow `.crules/modes/GIT_POLICY.md` in full for commits and releases.

## Conventional commits

`feat` | `fix` | `docs` | `chore` | `refactor` — imperative subject, ≤72 chars.

## Version sources (must match)

1. `setup.py` — **master**
2. `ap_wrapper/__init__.py` — `__version__`
3. Git tags on release (`vX.Y.Z`)

Bump from the highest observed value (monotonic). Default: feat→minor,
fix/docs/chore/refactor→patch, breaking→major.

## Pre-commit

- Heuristic secret scan on staged files.
- No credentials or private media committed.
- After version edit, verify:

```bash
python3 -c "from ap_wrapper import __version__; print(__version__)"
```

## Shortcuts

User says **commit** / **branch** / **release** → Manager persona + `GIT_POLICY.md`.
