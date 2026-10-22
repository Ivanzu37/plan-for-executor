# Mode: next

Goal: hand out the next phase of a multi-phase plan, adjusted to what really happened in the previous one. Hard rules from `SKILL.md` still apply.

## Steps

1. **Read the plan** given as argument. Take `phase: N/M`. If `N == M`, say there is no next phase and suggest `review` instead.
2. **Check phase N** quickly, as in `modes/review.md` steps 1-3 (report + diff since `commit`). If anything is ❌, stop: write the review with its fix prompt (review mode, step 5) and tell the user to fix phase N first.
3. **Adjust phase N+1** to reality: renamed functions, moved files, decisions the executor reported, new risks. Re-read the files phase N+1 touches; anchors must match the code as it is now. Edit the plan's **Steps** and **Prompt for the executor** for phase N+1 only; never rewrite finished phases.
4. **Move the frontmatter:** `phase: N+1/M`, `commit:` = current `git rev-parse --short HEAD` (the base for this phase), keep `status: in-progress`. In the phase N+1 prompt, update the base commit in BEFORE STARTING.
5. **Note it** under the plan's **Decisions**: `- YYYY-MM-DD, phase N+1: <what changed from the original plan and why>` (or "no changes").
6. **Lint** the plan (`scripts/lint_plan.py`) until it passes.
7. **Hand off** as in `SKILL.md` step 7, with the phase N+1 prompt and `run_plan.py <plan>` (it picks the current phase).
