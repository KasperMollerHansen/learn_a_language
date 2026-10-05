# MISTAKES

Failures made while working in this repo, newest first. Each entry: what happened, root cause,
consequence, and the one rule that prevents a repeat. A rule that has repeated is promoted into
`CLAUDE.md`, and the entry notes that it graduated.

No entries yet.

## 2026-10-05 — Test runner unavailable

- What happened: `poetry run pytest` and `python -m pytest` could not run; unittest discovery initially failed to import `init_repo`.
- Root cause: Poetry and pytest are not installed in the environment, and unittest did not have `src` on `PYTHONPATH`.
- Consequence: The pytest suite could not run as configured; plain test functions were executed directly and unittest passed with `PYTHONPATH=src`.
- Rule: Check the project test toolchain before invoking the gate; when falling back to unittest in this source layout, set `PYTHONPATH=src`.
