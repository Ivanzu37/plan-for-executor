# Changelog

## 0.2.0 — 2026-10-22

### Added
- `review <plan>` mode: compares the executor's report and the git diff with the plan, step by step (✅ ⚠️ ❌), writes the review into the plan and a fix prompt when something is missing.
- `next <plan>` mode: moves a multi-phase plan to the next phase, re-anchoring its steps to the code as it is now.
- Execution report section that the executor fills in, with DONE WHEN checkboxes.
- `STOP AND REPORT IF` block and per-step anchors in the executor prompt.
- Base commit in the frontmatter and a stale-plan check before the executor starts.
- Size triage: prompt-only for tiny tasks, phases of up to ~6 steps for large ones.
- Profiles (`$PLAN_PROFILE` or `~/.claude/plan-for-executor.profile.md`): plans folder, language, executor model and extra prompt blocks. `profile.example.md`.
- `scripts/lint_plan.py` and `scripts/run_plan.py` (Python 3, standard library only).
- Plugin manifest and marketplace (`/plugin install plan-for-executor --marketplace Ivanzu37/plan-for-executor`).
- `examples/`, unit tests for the scripts, `claude plugin eval` cases, CI.
- Spanish labels for plans written in Spanish.
- `guard_readonly.py`: a skill-scoped PreToolUse hook that blocks shell writes (`>`, `>>`, `tee`, `sed -i`, `rm`, state-changing git…) and Write/Edit on non-Markdown files.
- CI on Linux, macOS and Windows (Python 3.9 and 3.13).

### Changed
- The lint requires every prompt label (WORKING MODE and BEFORE STARTING too), also in review fix prompts; the full prompt is always pasted in chat at hand-off.
- New icon (double chevron, `#B85C38`, readable at 16 px), cycle diagram for light and dark mode, social preview image, and a README rewritten around install-first and plain language.
- Plugin icon, issue templates and an "Issues and ideas" section in the README.
- `run_plan.py` and `lint_plan.py` print UTF-8 on any console; the guard hook falls back to `python` when `python3` is missing.
- On Windows, `run_plan.py` starts node with the script behind npm's `claude.cmd`, because cmd.exe cut multi-line prompts at the first line.
- Skill moved to `skills/plan-for-executor/`; layout and prompt template moved to `template.md`.
- Fixed `status` values: `draft · approved · in-progress · blocked · done · dropped`; progress goes in `phase: N/M`.
- `allowed-tools` made read-only for real: removed `find`, `cat`, `head`, `tail` and `git branch*`; added `Edit` (plan file only) and the lint.

## 0.1.0 — 2026-10-22
- First version: read-only planner, plan file and copy-paste prompt.
