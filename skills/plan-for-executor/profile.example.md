---
# Copy to ~/.claude/plan-for-executor.profile.md (or point $PLAN_PROFILE at it).
# Every key is optional.
plans_dir: ~/notes/plans          # default: $PLANS_DIR, else <repo>/plans/
language: en                      # en | es | ... (headings and prompt labels)
status_key: status                # status | estado
executor: sonnet                  # sonnet | haiku | <other agent>
---

# Planner extras
Extra things the planner does in Orient and Explore, e.g.:
- Before grepping, query the code map: `my-code-map query "<q>"`.

# Plan frontmatter extras
Extra frontmatter lines for every plan, e.g.:
- `tags: [plan]`

# Plan footer
Text appended at the end of every plan, e.g. a "Related" section with links.

# Prompt: working mode
Lines added to WORKING MODE in every prompt, e.g.:
- Use the project's formatter: `make fmt` after each step.

# Prompt: review before verify
Lines added as a REVIEW block before VERIFY, e.g.:
- Run `/my-review` on the files you changed and fix what it finds.

# Prompt: when finished
Lines added to WHEN FINISHED, e.g.:
- Add an entry to ~/notes/log.md (done / left / files).

# Project rules
Rules per repo that every plan must respect, e.g.:
- my-game: only one run of the expensive test, at the end.
