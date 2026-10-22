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
- Plugin manifest and marketplace (`/plugin install plan-for-executor --marketplace Ivanzu37/plan-sonnet`).
- `examples/`, unit tests for the scripts, `claude plugin eval` cases, CI.
- Spanish labels for plans written in Spanish.

### Changed
- Plugin icon, issue templates and an "Issues and ideas" section in the README.
- Skill moved to `skills/plan-for-executor/`; layout and prompt template moved to `template.md`.
- Fixed `status` values: `draft · approved · in-progress · blocked · done · dropped`; progress goes in `phase: N/M`.
- `allowed-tools` made read-only for real: removed `find`, `cat`, `head`, `tail` and `git branch*`; added `Edit` (plan file only) and the lint.

## 0.1.0 — 2026-10-22
- First version: read-only planner, plan file and copy-paste prompt.
