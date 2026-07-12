# Fix: Ctrl+C leaves AtomicParsley temp file

## Goal

When the user interrupts `ap` with Ctrl+C during a metadata write,
exit cleanly (no traceback) and remove AtomicParsley’s leftover
`--overWrite` temp file (`{stem}-temp-{random}{ext}`).

## Acceptance criteria

- [x] Ctrl+C during write does not print a Python traceback
- [x] Exit code is 130 on interrupt
- [x] Leftover `{name}-temp-*.mp4` / `.m4v` beside the target is removed
- [x] Original media file is left intact on interrupt
- [x] Successful writes still complete with `--overWrite` as before
- [x] Unit tests cover temp pattern and interrupt cleanup helpers

## Coder Notes

- AtomicParsley names temps with `rand() % 100000`, **not** the process PID.
- Cleanup uses glob `{stem}-temp-*{ext}` after overwrite runs (or interrupt).
- All AP subprocess calls go through `run_atomicparsley()`.
