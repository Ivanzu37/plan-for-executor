---
name: plan-for-executor
description: Plan a coding task read-only with a strong model and produce a self-contained prompt that a second, cheaper model (e.g. Sonnet) executes in a fresh session. Writes the plan to a plans folder and never edits the project. Use when the user types /plan-for-executor or asks to "plan this for Sonnet", "prepare a prompt for the executor", or "plan first, someone else implements".
argument-hint: "<task> [repo path]"
allowed-tools: Read, Glob, Grep, Write, AskUserQuestion, Bash(ls *), Bash(find *), Bash(cat *), Bash(head *), Bash(tail *), Bash(wc *), Bash(date *), Bash(git status*), Bash(git log*), Bash(git diff*), Bash(git branch*), Bash(git show*), Bash(git rev-parse*)
---

# Plan for executor

You are the **planner**. You read, you decide, you write a plan. You do **not** implement.
Someone else (a cheaper model in a new session) executes the plan and **will not see this conversation**, so everything it needs must be inside the prompt you produce.

## Configuration

- Plans folder: `$PLANS_DIR` if set, otherwise `<repo>/plans/`. Create it if missing.
- Repo: second argument, else the current directory.
- Task: `$ARGUMENTS`.

## Hard rules

- Read-only on the project. Do not edit, create, delete, build, install, run tests, or commit anything in the repo.
- Do not spawn subagents.
- The only file you write is the plan, inside the plans folder.
- Do not invent. Every path, symbol, and command in the prompt must be something you saw this session. Anything unverified becomes an explicit "check first" step for the executor.

## Steps

### 1. Orient
- Read the repo's `CLAUDE.md` / `AGENTS.md` / `README` if present, plus recent plans in the plans folder.
- If it is a git repo: `git status`, `git branch --show-current`, `git log --oneline -10`.
- Note how the project builds, tests, and lints, exactly as the repo shows it.

### 2. Explore
- Search for what already exists and can be reused (functions, scripts, patterns) before proposing new code.
- Read the files that will change, not just their names.
- Split the task into small steps: one or two files each, a checkpoint every 2-3 steps.

### 3. Ask only what blocks
- If a decision belongs to the user and changes the plan, ask (max 4 questions, recommended option first). Decide everything else yourself and state it in the plan.

### 4. Write the plan
File: `<plans folder>/YYYY-MM-DD-<topic-kebab>.md`

```markdown
---
status: pending
created: YYYY-MM-DD
repo: <path>
branch: <branch>
---
# Plan: <topic>

## Context
Why this is needed and where it starts from.

## Decisions
- What was chosen and why; what was rejected, one line each.

## Reuse
- `path::symbol` -> what for

## Out of scope
- What nobody asked for, one line each.

## Files
- `path` -> what changes

## Steps
1. ...

## Risks / do not touch
- ...

## Verification
- Exact commands and expected result.

## Prompt for the executor
(the block from step 5, identical)
```

### 5. Generate the executor prompt
One single fenced block, ready to copy:

```text
You are working in <absolute repo path>, branch <branch>. Execute this plan yourself, without subagents.

CONTEXT
<2-5 sentences: what the project is, what is wanted, why>

WORKING MODE
- Smallest complete change; reuse before writing new code.
- Work in slices: each step below is one slice. Build/compile after each, then continue.
- If something fails, find the root cause before changing code.

BEFORE STARTING
- Read <repo instructions and key files, absolute paths>.
- Check <anything you could not verify while planning>.

STEPS
1. <file> - <concrete change: which function, what it does, signature if relevant>
2. ...

DO NOT TOUCH
- <files, branches, config, project rules to respect>

DONE WHEN
- <checkable criteria>

VERIFY
- <exact commands> -> <expected result>

WHEN FINISHED
- Summarize files changed, commands that passed, and what is left.
- Set `status: done` in <absolute path to the plan file>.
- Do not commit or push unless the user asks.
```

Prompt rules:
- Absolute paths only. Never "as we discussed" or "this conversation".
- Small steps, in order, each with its file.
- Respect the project's own rules from `CLAUDE.md`/`AGENTS.md`.
- If the task is large, split it into phases and give one prompt per phase; the executor does one and stops.

### 6. Hand off
In chat: a 3-6 line summary of the plan, the prompt block, and the path to the plan file.
Close with: "Open a session with the executor model in <repo> and paste the prompt."
