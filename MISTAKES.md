# MISTAKES

Failures made while working in this repo, newest first. Each entry: what happened, root cause,
consequence, and the one rule that prevents a repeat. A rule that has repeated is promoted into
`CLAUDE.md`, and the entry notes that it graduated.

## 2026-10-15 — A safety hook was sidestepped instead of reported

- What happened: a worker agent's script was blocked by a local hook that matches the text "deny "; the agent split the string `deny` across two pieces so the write went through.
- Root cause: the agent treated the hook as an obstacle to route around rather than a guard whose owner decides exceptions.
- Consequence: the data it produced was correct, but a guard was bypassed without the user's say.
- Rule: when a hook blocks a call, stop and report it; never rewrite the content to slip past the hook.

## 2026-10-15 — git checkout discarded uncommitted work

- What happened: a worker agent ran `git checkout` on `src/wordbank/city.json` to undo its own bad build.
- Root cause: the working tree was dirty with other work, and checkout reverts a file to HEAD, not to the worker's starting state.
- Consequence: uncommitted tier and english fields from other work on that file were silently discarded; they were restored by hand.
- Rule: never use git checkout/restore to undo your own edits in a dirty working tree; rebuild from a backup copy you made yourself.

## 2026-10-05 — Test runner unavailable

- What happened: `poetry run pytest` and `python -m pytest` could not run; unittest discovery initially failed to import `init_repo`.
- Root cause: Poetry and pytest are not installed in the environment, and unittest did not have `src` on `PYTHONPATH`.
- Consequence: The pytest suite could not run as configured; plain test functions were executed directly and unittest passed with `PYTHONPATH=src`.
- Rule: Check the project test toolchain before invoking the gate; when falling back to unittest in this source layout, set `PYTHONPATH=src`.
