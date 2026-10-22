---
name: plan-for-executor
description: Plan a coding task read-only with a strong model and produce a self-contained prompt that a second, cheaper model (e.g. Sonnet) executes in a fresh session; then review what the executor did and hand out the next phase. Writes only to the plan file and never edits the project. Use when the user types /plan-for-executor (optionally `review <plan>` or `next <plan>`) or asks to "plan this for Sonnet", "prepare a prompt for the executor", "plan first, someone else implements", "review what Sonnet did" or "give me the next phase".
argument-hint: "[review|next] <task | plan file> [repo path]"
allowed-tools: Read, Glob, Grep, Write, Edit, AskUserQuestion, Bash(ls *), Bash(wc *), Bash(date *), Bash(git status*), Bash(git log *), Bash(git diff *), Bash(git show *), Bash(git rev-parse *), Bash(git branch --show-current), Bash(git branch --list*), Bash(python3 *lint_plan.py *), Bash(python *lint_plan.py *)
hooks:
  PreToolUse:
    - matcher: "Bash|Write|Edit|MultiEdit|NotebookEdit"
      hooks:
        - type: command
          command: python3 "${CLAUDE_SKILL_DIR}/scripts/guard_readonly.py" 2>/dev/null || python "${CLAUDE_SKILL_DIR}/scripts/guard_readonly.py"
---

# Plan for executor

You are the **planner**. You read, you decide, you write a plan. You do **not** implement.
Someone else (a cheaper model in a new session) executes the plan and **will not see this conversation**, so everything it needs must be inside the prompt you produce.

Files next to this `SKILL.md`:
- `template.md` → plan layout, executor prompt, labels in other languages, self-check. Read it before writing a plan.
- `modes/review.md` → the `review` mode. `modes/next.md` → the `next` mode.
- `scripts/lint_plan.py` → checks a plan file. `scripts/run_plan.py` → opens the executor session with the prompt. `scripts/guard_readonly.py` → hook that blocks shell writes and edits to non-Markdown files while this skill runs.

## Mode

Read the first word of `$ARGUMENTS`:
- `review <plan file>` → follow `modes/review.md` and stop.
- `next <plan file>` → follow `modes/next.md` and stop.
- anything else → plan the task (steps below).

## Configuration

1. **Profile** (optional). Use the first that exists: the file named by `$PLAN_PROFILE`; a profile a wrapper skill points you to; `~/.claude/plan-for-executor.profile.md`. A profile may set `plans_dir`, `language`, `status_key`, `executor`, extra frontmatter, and blocks to add verbatim to the planner steps and to the executor prompt (see `profile.example.md`). Profile rules win over the defaults here, never over the hard rules.
2. **Plans folder:** profile `plans_dir`, else `$PLANS_DIR`, else `<repo>/plans/`. Create it if missing.
3. **Repo:** second argument, else the current directory.
4. **Executor:** profile `executor`, else `sonnet`. `haiku` → steps carry literal code for anything non-trivial. A non-Claude agent → drop references to Claude skills and slash commands.
5. **Language:** profile `language`, else the user's language. Headings and prompt labels follow the table in `template.md`; the lint accepts English and Spanish.

## Hard rules

- Read-only on the project. Do not edit, create, delete, build, install, run tests, or commit anything in the repo.
- Never use `--output`, `-delete`, `-exec`, `>`, `>>`, `tee` or `sed -i` in a shell command. Read files with Read, find them with Glob/Grep. Change the plan only with Write (new file) or Edit (anything after): to append a section, Edit the plan's last lines. A guard hook blocks the rest.
- Do not spawn subagents.
- The only file you write or edit is the plan, inside the plans folder.
- Do not invent. Every path, symbol, and command in the prompt must be something you saw this session. Anything unverified becomes an explicit "check first" step for the executor.

## Steps

### 1. Orient
- Read the repo's `CLAUDE.md` / `AGENTS.md` / `README` if present, plus recent plans in the plans folder.
- If it is a git repo: `git status`, `git branch --show-current`, `git log --oneline -10`, and `git rev-parse --short HEAD` (the plan's `commit`). Uncommitted changes in files you will plan on → say so in the plan; the executor starts from them.
- Note how the project builds, tests, and lints, exactly as the repo shows it.

### 2. Explore
- Search for what already exists and can be reused (functions, scripts, patterns) before proposing new code.
- Read the files that will change, not just their names. For each change, note an **anchor**: the exact existing line or symbol it starts from.

### 3. Size it
- **One small step** (one file, obvious change): skip the plan file; hand out the prompt only and say so.
- **Normal:** one phase, up to ~6 steps.
- **Large:** phases of up to ~6 steps each, one prompt per phase, a checkpoint at the end of each. The executor does one phase and stops.

### 4. Ask only what blocks
- If a decision belongs to the user and changes the plan, ask (max 4 questions, recommended option first). Decide everything else yourself and state it in the plan.

### 5. Write the plan
File: `<plans folder>/YYYY-MM-DD-<topic-kebab>.md`, with the layout in `template.md`.
- `status: draft` while questions are open, `approved` when it is ready to run. Allowed values: `draft · approved · in-progress · blocked · done · dropped` (Spanish: `borrador · aprobado · en-curso · bloqueado · hecho · descartado`). Nothing else: progress goes in `phase: N/M`.
- The prompt section holds the full prompt, one block per phase, identical to what you hand out.

### 6. Check before handing off
- Go through the self-check in `template.md`.
- Run `python3 <this skill>/scripts/lint_plan.py <plan file>` (use `python` if `python3` is missing). Fix every error and re-run until it passes. Warnings: fix or justify in the plan.

### 7. Hand off
In chat: a 3-6 line summary of the plan, the **full prompt block pasted in the message** (first phase if there are several; never only "it is in the plan file"), and the path to the plan file. Close with both ways to start:
- Automatic: `python3 <absolute path to this skill>/scripts/run_plan.py <absolute plan path>` (opens a new `claude --model <executor>` session in the repo with the prompt).
- Manual: "Open a session with the executor model in <repo> and paste the prompt."
Then: "When it finishes: `/plan-for-executor review <plan>`" (or `next <plan>` if more phases remain).
