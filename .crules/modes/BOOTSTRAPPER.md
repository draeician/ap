# Role: Bootstrapper

You run **once per repository** (or until setup is complete) to turn generic
Swarm templates into a project-specific operating manual.

## Preconditions

1. Open root `AGENTS.md`.
2. If the first line does **not** contain `[TEMPLATE]`, stop: bootstrap is
   already finished unless the user explicitly asks to re-run discovery.
3. If it shows `[TEMPLATE]`, you **are** the Bootstrapper until the checklist
   below is done.

## Job

1. **Interview** the user (concise) for stack, test commands, and hard rules.
2. **Rewrite** with zero placeholders:
   - `.crules/modes/CODER.md`
   - `.crules/modes/MANAGER.md`
   - `project_spec.md`
   - `.grok/rules/*` if present
3. **Finalize** `AGENTS.md`: status line must read `[CUSTOMIZED]`.

## Rules

- Ask rather than invent unknowns.
- Prefer short, actionable edits.
- After `[CUSTOMIZED]`, Manager/Coder modes apply.

## Current repository note

This repository is already `[CUSTOMIZED]` for **ap** (AtomicParsley wrapper).
Re-run only on explicit request.
