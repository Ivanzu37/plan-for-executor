# Mode: review

Goal: compare what the executor did with what the plan asked, without touching the project. Hard rules from `SKILL.md` still apply.

## Steps

1. **Read the plan** given as argument (absolute or relative to the plans folder). Take `repo`, `branch`, `commit`, `phase` and the steps and DONE WHEN of the current phase. Read its **Execution report**; no entry for the current phase → say the executor has not reported, review the diff anyway, and mark every item as "unreported".
2. **Read what changed** in the repo:
   - `git status` and `git diff <commit>..HEAD --stat`, then `git diff <commit>..HEAD -- <file>` for each file (committed work).
   - `git diff --stat` and `git diff -- <file>` (uncommitted work).
   - Not a git repo → read the files listed in the report and the plan.
3. **Compare, step by step.** For each step and each DONE WHEN item: ✅ done as planned · ⚠️ done differently (say how, and whether it is acceptable) · ❌ missing or wrong. Also list changes to files the plan did not mention and anything touching DO NOT TOUCH.
4. **Verification.** You do not run commands. Say which VERIFY commands the report claims passed, which are missing, and what the user should run to confirm.
5. **Write the review** at the end of the plan file:

   ```markdown
   ## Review — YYYY-MM-DD (phase N)
   | Item | Verdict | Note |
   |---|---|---|
   | Step 1 | ✅ | ... |
   Unplanned changes: ...
   Verdict: accepted | fixes needed | blocked
   ```

   - All ✅ (or acceptable ⚠️) and this was the last phase → `status: done`.
   - All ✅ and more phases remain → leave `in-progress` and point to `next`.
   - Any ❌ → write a **fix prompt** in the review: one `text` block with the same labels as the executor prompt (template.md), only the missing work as STEPS, the same DO NOT TOUCH and STOP AND REPORT IF, and WHEN FINISHED asking for a `### Phase N fix — YYYY-MM-DD` report entry. Leave `in-progress` (or `blocked` if it needs a user decision).
6. **Run the lint** on the plan (`scripts/lint_plan.py`) and fix what it reports in your own additions.
7. **Hand off** in chat: the table, the verdict, and if there is one, the fix prompt plus the `run_plan.py <plan> --review-fix` command to launch it.
