#!/usr/bin/env python3
"""PreToolUse hook: keeps the planner read-only while this skill is active.

Blocks (exit 2, reason on stderr for Claude):
- Bash commands that write: redirections (except to /dev/null and 2>&1),
  tee, sed -i, rm/mv/cp/mkdir/touch, find -delete/-exec, --output, and
  git commands that change state.
- Write/Edit on anything that is not a Markdown file (the plan is the only
  file the planner writes).
"""
import json
import re
import sys

REDIRECT = re.compile(r"\d?>>?(&\d)?\s*(\S*)")

BASH_WRITES = [
    (re.compile(r"\btee\b"), "tee"),
    (re.compile(r"\bsed\b[^|;&]*\s-i"), "sed -i"),
    (re.compile(r"(?:^|[;&|(]\s*|\s)(?:rm|mv|cp|mkdir|touch|chmod|ln)\s"), "a file-changing command"),
    (re.compile(r"\s-(?:delete|exec|execdir)\b"), "find -delete/-exec"),
    (re.compile(r"--output\b"), "--output"),
    (re.compile(r"\bgit\s+(?:commit|push|add|rm|mv|reset|checkout|switch|restore|stash|merge|rebase|tag|clean|apply|am|cherry-pick|revert|branch\s+-[dDmM])\b"), "a git command that changes the repo"),
]

HELP = (
    "plan-for-executor is read-only: the planner writes only the plan (a .md file) "
    "with Write or Edit, and never changes the project. To append to the plan, use "
    "Edit on its last lines. If the user asked you to implement it yourself, tell them "
    "this session is in planner mode and offer run_plan.py or a new session."
)


def check(event):
    tool = event.get("tool_name", "")
    data = event.get("tool_input") or {}
    if tool == "Bash":
        cmd = data.get("command", "")
        stripped = re.sub(r"'[^']*'|\"[^\"]*\"", "''", cmd)  # ignore quoted text
        for m in REDIRECT.finditer(stripped):
            if not m.group(1) and not m.group(2).startswith("/dev/null"):
                return "Blocked output redirection (> or >>) in `%s`. %s" % (cmd[:120], HELP)
        for pattern, what in BASH_WRITES:
            if pattern.search(stripped):
                return "Blocked %s in `%s`. %s" % (what, cmd[:120], HELP)
    elif tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        path = data.get("file_path") or data.get("notebook_path") or ""
        if not path.lower().endswith(".md"):
            return "Blocked %s on `%s`. %s" % (tool, path, HELP)
    return None


def main():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0
    reason = check(event)
    if reason:
        print(reason, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
