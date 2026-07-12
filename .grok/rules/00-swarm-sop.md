# Swarm SOP (always on)

You operate in a multi-agent (Skeleton Swarm) repository. Native Grok rules
are loaded; also obey root `AGENTS.md`.

## Priority

`project_spec.md` > `AGENTS.md` > `.crules/modes/*` > this file

## Personas

| Mode | When | File |
|------|------|------|
| Manager | planning, backlog, commit/branch/release | `.crules/modes/MANAGER.md` |
| Coder | implementation and tests | `.crules/modes/CODER.md` |
| Git policy | any VCS mutation | `.crules/modes/GIT_POLICY.md` |

Default for coding requests: **Coder**. Default for “commit” / “release” / roadmap: **Manager**.

## Session checklist

1. Read `AGENTS.md` and `project_spec.md` when starting non-trivial work.
2. For metadata atoms/switches, read `DEV_NOTES.md`.
3. Track non-trivial work as Markdown under `.crules/tasks/wip/` with acceptance criteria.
4. Do not implement speculative features outside the request or active task.
5. Never use `--break-system-packages`. Prefer `pipx`, venv, or `python3 -m ap_wrapper.main`.

## Important files

| File | Use |
|------|-----|
| `project_spec.md` | Scope, stack, conventions |
| `DEV_NOTES.md` | Atom ↔ CLI mapping |
| `AGENTS.md` | Hard boundaries and coding rules |
| `GROK.md` | Grok entrypoint |
| `.grok/agents/` | Optional named agent profiles |

## Verification

Before claiming done:

- Smoke: `python3 -m ap_wrapper.main --help`
- If version touched: import `__version__` matches `setup.py`
- If metadata touched: raw AtomicParsley `-t` vs wrapper view still make sense
