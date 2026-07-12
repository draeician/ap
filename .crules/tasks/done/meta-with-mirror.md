# Task: --meta with -m applies mirror first, then per-file meta

## Goal

When `--meta` is given together with `-m` / `--mirror`, update all mirrored
fields from the source first, then apply filename-derived title / show /
season / episode so each target keeps its own season and episode numbers
(not the source file’s values duplicated across all targets).

## Acceptance criteria

- [x] `ap -m source.mp4 --meta a-s01e01.mp4 b-s01e02.mp4` mirrors shared
      fields from source, then sets season/episode from each filename
- [x] `--meta` alone still tags from filename only (existing behavior)
- [x] `-m` alone still mirrors fully (existing behavior)
- [x] Invalid / unparseable filenames still skip with a clear message
- [x] Docs mention the combined `-m` + `--meta` order

## Coder Notes

- Changed only the `args.meta` branch in `main()`: when `-m` is also valid,
  call `build_command` (mirror) then `build_meta_command` (filename meta).
- Two AtomicParsley writes per file when both flags are set (mirror, then meta).
- Help text, README, DEV_NOTES, and project_spec updated.
- Verified with mock: mirror uses source episode `99`, then meta applies `01` / `02`
  per target filename.
