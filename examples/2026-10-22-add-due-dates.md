---
status: in-progress
created: 2026-10-22
repo: /home/me/code/todo-cli
branch: feature/due-dates
commit: 8d41e07
phase: 2/2
executor: sonnet
---
# Plan: add due dates to todo-cli

## Context
`todo-cli` stores tasks in `tasks.json` and prints them with `todo list`. Users want an optional due date per task and overdue tasks shown first. Starts from `main` at `3f9c2ab`, clean working tree.

## Decisions
- Dates are stored as ISO strings (`YYYY-MM-DD`), parsed with `datetime.date.fromisoformat`; no new dependency.
- Tasks without a date sort last; rejected: a fake far-future date (it leaks into the JSON).
- 2026-10-23, phase 2: `Task.due` was named `due_date` in phase 1 (reported deviation, accepted); phase 2 steps use `due_date`.

## Reuse
- `todo/store.py::load_tasks` / `save_tasks` -> read and write, unchanged.
- `todo/cli.py::build_parser` -> add the flag next to `--priority`.

## Out of scope
- Reminders, time of day, recurring tasks.

## Files
- `todo/models.py` -> optional due date on `Task`.
- `todo/cli.py` -> `--due` flag on `add`; ordering in `list`.
- `tests/test_cli.py` -> tests for both.

## Steps
### Phase 1 — store the date
1. `todo/models.py` · anchor `class Task:` → add `due_date: date | None = None`, serialize as ISO string.
2. `todo/cli.py` · anchor `add.add_argument("--priority"` → add `--due YYYY-MM-DD`.

### Phase 2 — show it
1. `todo/cli.py` · anchor `def cmd_list(` → sort overdue first, then by date, undated last; print the date.
2. `tests/test_cli.py` → tests for ordering and for a bad date.

## Risks / do not touch
- `tasks.json` written by old versions must still load (no `due_date` key).
- Do not touch `todo/store.py`.

## Verification
- `python -m pytest -q` -> all tests pass.
- `python -m todo add "x" --due 2000-01-01 && python -m todo list` -> `x` first, marked overdue.

## Prompt for the executor
### Phase 1
```text
You are working in /home/me/code/todo-cli, branch feature/due-dates. Execute phase 1 of 2 of this plan yourself, without subagents.

CONTEXT
todo-cli is a small Python CLI that keeps tasks in tasks.json. We are adding an optional due date per task. This phase only stores it; phase 2 shows it.

WORKING MODE
- Smallest complete change; reuse before writing new code.
- Work in slices: each step below is one slice. Run the tests after each, then continue.
- If something fails, find the root cause before changing code.

BEFORE STARTING
- Set `status: in-progress` in /home/me/code/todo-cli/plans/2026-10-22-add-due-dates.md.
- Base commit is 3f9c2ab. If `git rev-parse --short HEAD` is different, run `git diff 3f9c2ab..HEAD --stat -- todo/models.py todo/cli.py`; if any of them changed, stop and report.
- Read /home/me/code/todo-cli/README.md and /home/me/code/todo-cli/todo/models.py.

STEPS
1. /home/me/code/todo-cli/todo/models.py · anchor `class Task:` → add `due_date: date | None = None`; `to_dict` writes it as an ISO string, `from_dict` reads it back and accepts a missing key.
2. /home/me/code/todo-cli/todo/cli.py · anchor `add.add_argument("--priority"` → add `--due` (help "YYYY-MM-DD"), parsed with `date.fromisoformat`; a bad value exits with a clear error.

DO NOT TOUCH
- /home/me/code/todo-cli/todo/store.py

STOP AND REPORT IF
- A file or anchor above does not exist or looks different from what is described.
- The same check fails twice after a fix.
- A step needs a file from DO NOT TOUCH, or more than the steps describe.
- Old tasks.json files without the new key fail to load.
When you stop, do not improvise: write what you found in the execution report and end.

DONE WHEN
- [ ] `todo add "x" --due 2026-11-01` stores the date in tasks.json.
- [ ] An old tasks.json without dates still loads.

VERIFY
- `python -m pytest -q` -> all tests pass.

WHEN FINISHED
- Append to the "Execution report" section of /home/me/code/todo-cli/plans/2026-10-22-add-due-dates.md: `### Phase 1 — YYYY-MM-DD`, then files changed, commands run and their result, deviations from the plan and why, what is left. Tick the DONE WHEN boxes that hold.
- Set `status: done` if this was the last phase and everything in DONE WHEN holds; `blocked` if you stopped; otherwise leave `in-progress`.
- Do not commit or push unless the user asks.
```

### Phase 2
```text
You are working in /home/me/code/todo-cli, branch feature/due-dates. Execute phase 2 of 2 of this plan yourself, without subagents.

CONTEXT
todo-cli is a small Python CLI that keeps tasks in tasks.json. Phase 1 added `Task.due_date`. This phase shows it in `todo list`, overdue tasks first.

WORKING MODE
- Smallest complete change; reuse before writing new code.
- Work in slices: each step below is one slice. Run the tests after each, then continue.
- If something fails, find the root cause before changing code.

BEFORE STARTING
- Set `status: in-progress` in /home/me/code/todo-cli/plans/2026-10-22-add-due-dates.md.
- Base commit is 8d41e07. If `git rev-parse --short HEAD` is different, run `git diff 8d41e07..HEAD --stat -- todo/cli.py tests/test_cli.py`; if any of them changed, stop and report.
- Read /home/me/code/todo-cli/todo/cli.py.

STEPS
1. /home/me/code/todo-cli/todo/cli.py · anchor `def cmd_list(` → sort by (not overdue, due_date or date.max); print the date after the title and `(overdue)` when it is before today.
2. /home/me/code/todo-cli/tests/test_cli.py · anchor `def test_list_` → add `test_list_overdue_first` and `test_add_bad_due_date`.

DO NOT TOUCH
- /home/me/code/todo-cli/todo/store.py
- /home/me/code/todo-cli/todo/models.py (finished in phase 1)

STOP AND REPORT IF
- A file or anchor above does not exist or looks different from what is described.
- The same check fails twice after a fix.
- A step needs a file from DO NOT TOUCH, or more than the steps describe.
When you stop, do not improvise: write what you found in the execution report and end.

DONE WHEN
- [ ] Overdue tasks print first, undated tasks last.
- [ ] The two new tests pass.

VERIFY
- `python -m pytest -q` -> all tests pass.
- `python -m todo add "x" --due 2000-01-01 && python -m todo list` -> `x` first, marked `(overdue)`.

WHEN FINISHED
- Append to the "Execution report" section of /home/me/code/todo-cli/plans/2026-10-22-add-due-dates.md: `### Phase 2 — YYYY-MM-DD`, then files changed, commands run and their result, deviations from the plan and why, what is left. Tick the DONE WHEN boxes that hold.
- Set `status: done` if this was the last phase and everything in DONE WHEN holds; `blocked` if you stopped; otherwise leave `in-progress`.
- Do not commit or push unless the user asks.
```

## Execution report
### Phase 1 — 2026-10-23
- Files: `todo/models.py`, `todo/cli.py`.
- `python -m pytest -q` -> 14 passed.
- Deviation: the field is `due_date`, not `due`, because `Task` already has a `due()` helper.
- Left: nothing for phase 1.
- [x] `todo add "x" --due 2026-11-01` stores the date in tasks.json.
- [x] An old tasks.json without dates still loads.

## Review — 2026-10-23 (phase 1)
| Item | Verdict | Note |
|---|---|---|
| Step 1 | ⚠️ | Field named `due_date` (clash with `Task.due()`); accepted. |
| Step 2 | ✅ | Bad dates exit with code 2 and a message. |
| DONE WHEN | ✅ | Both hold; the report says the tests passed. |
Unplanned changes: none.
Verdict: accepted. Phase 2 adjusted with `next`.
