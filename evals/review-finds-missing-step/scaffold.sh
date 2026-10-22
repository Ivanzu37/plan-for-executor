#!/usr/bin/env bash
# Toy repos shared by every case (each case copies this file):
#   ./todo         clean tiny Python CLI under git (plan case)
#   ./todo-review  + a plan whose executor did only step 1 of 2 (review case)
#   ./todo-next    + a 2-phase plan, phase 1 done with a reported rename (next case)
set -euo pipefail
W="$PWD"
GIT="git -c user.name=eval -c user.email=eval@example.com"

base_repo() {
R="$W/$1"
mkdir -p "$R/todo" "$R/tests" "$R/plans"
cat > "$R/README.md" <<'MD'
# todo
Tiny task list. Run `python -m todo list`. Tests: `python -m unittest -q`.
MD
cat > "$R/todo/__init__.py" <<'PY'
PY
cat > "$R/todo/store.py" <<'PY'
import json, os

PATH = os.environ.get("TODO_FILE", "tasks.json")


def load_tasks():
    if not os.path.exists(PATH):
        return []
    with open(PATH) as fh:
        return json.load(fh)


def save_tasks(tasks):
    with open(PATH, "w") as fh:
        json.dump(tasks, fh)
PY
cat > "$R/todo/cli.py" <<'PY'
import argparse
from todo.store import load_tasks, save_tasks


def build_parser():
    p = argparse.ArgumentParser(prog="todo")
    sub = p.add_subparsers(dest="cmd", required=True)
    add = sub.add_parser("add")
    add.add_argument("title")
    sub.add_parser("list")
    return p


def cmd_list(args):
    for i, t in enumerate(load_tasks(), 1):
        print(f"{i}. {t['title']}")


def cmd_add(args):
    tasks = load_tasks()
    tasks.append({"title": args.title})
    save_tasks(tasks)


def main(argv=None):
    args = build_parser().parse_args(argv)
    {"list": cmd_list, "add": cmd_add}[args.cmd](args)
PY
cat > "$R/todo/__main__.py" <<'PY'
from todo.cli import main

main()
PY
touch "$R/tests/__init__.py"
cat > "$R/tests/test_cli.py" <<'PY'
import unittest
from todo.cli import build_parser


class ParserTest(unittest.TestCase):
    def test_list(self):
        self.assertEqual(build_parser().parse_args(["list"]).cmd, "list")
PY
cd "$R"
git init -q -b main
$GIT add -A
$GIT commit -qm "todo: initial"
BASE=$(git rev-parse --short HEAD)
}

prompt() { # $1 phase, $2 total, $3 steps, $4 done-when, $5 context
cat <<TXT
\`\`\`text
You are working in $R, branch main. Execute phase $1 of $2 of this plan yourself, without subagents.

CONTEXT
todo is a tiny Python CLI. $5

WORKING MODE
- Smallest complete change; reuse before writing new code.

BEFORE STARTING
- Set \`status: in-progress\` in $R/plans/PLANFILE.
- Base commit is $BASE.

STEPS
$3

DO NOT TOUCH
- $R/todo/store.py

STOP AND REPORT IF
- A file or anchor above does not exist or looks different from what is described.
When you stop, do not improvise: write what you found in the execution report and end.

DONE WHEN
$4

VERIFY
- \`python -m unittest -q\` -> OK

WHEN FINISHED
- Append to the "Execution report" section of $R/plans/PLANFILE.
- Do not commit or push unless the user asks.
\`\`\`
TXT
}

base_repo todo

# review case: two steps planned, only the first one was done, report claims both
base_repo todo-review
cat > plans/2026-10-22-verbose.md <<MD
---
status: in-progress
created: 2026-10-22
repo: $R
branch: main
commit: $BASE
phase: 1/1
executor: sonnet
---
# Plan: verbose list

## Context
Add \`--verbose\` to \`todo list\`, printing the task count at the end.

## Decisions
- Flag on the list subparser only.

## Files
- \`todo/cli.py\` -> flag and output
- \`tests/test_cli.py\` -> a test

## Steps
1. \`todo/cli.py\` · anchor \`sub.add_parser("list")\` → add \`--verbose\`.
2. \`todo/cli.py\` · anchor \`def cmd_list(\` → when verbose, print \`N tasks\` after the list.

## Verification
- \`python -m unittest -q\` -> OK

## Prompt for the executor
$(prompt 1 1 "1. $R/todo/cli.py · anchor \`sub.add_parser(\"list\")\` → add \`--verbose\` (store_true).
2. $R/todo/cli.py · anchor \`def cmd_list(\` → when args.verbose, print \`N tasks\` after the list." "- [ ] \`python -m todo list --verbose\` ends with \`N tasks\`." "We are adding a --verbose flag to list." | sed "s/PLANFILE/2026-10-22-verbose.md/g")

## Execution report
### Phase 1 — 2026-10-22
- Files: todo/cli.py.
- Steps 1 and 2 done. \`python -m unittest -q\` -> OK.
- [x] \`python -m todo list --verbose\` ends with \`N tasks\`.
MD

$GIT add -A
$GIT commit -qm "plan: verbose"
python3 - "$R/todo/cli.py" <<'PY'
import sys
p = sys.argv[1]; s = open(p).read()
s = s.replace('    sub.add_parser("list")\n', '    lst = sub.add_parser("list")\n    lst.add_argument("--verbose", action="store_true")\n')
open(p, "w").write(s)
PY

# next case: phase 1 renamed cmd_list to show_tasks (reported); phase 2 still says cmd_list
base_repo todo-next
cat > plans/2026-10-22-priority.md <<MD
---
status: in-progress
created: 2026-10-22
repo: $R
branch: main
commit: $BASE
phase: 1/2
executor: sonnet
---
# Plan: priorities

## Context
Tasks get an optional priority (phase 1) and list sorts by it (phase 2).

## Decisions
- Priority is an int 1-3, default 2.

## Files
- \`todo/cli.py\` -> flag, storage, sort

## Steps
### Phase 1 — store it
1. \`todo/cli.py\` · anchor \`add.add_argument("title")\` → add \`--priority\` (int, default 2) and store it.

### Phase 2 — sort by it
1. \`todo/cli.py\` · anchor \`def cmd_list(\` → sort by priority before printing.

## Verification
- \`python -m unittest -q\` -> OK

## Prompt for the executor
### Phase 1
$(prompt 1 2 "1. $R/todo/cli.py · anchor \`add.add_argument(\"title\")\` → add \`--priority\` (int, default 2); cmd_add stores it." "- [ ] added tasks carry a priority." "Tasks get an optional priority; this phase stores it." | sed "s/PLANFILE/2026-10-22-priority.md/g")

### Phase 2
$(prompt 2 2 "1. $R/todo/cli.py · anchor \`def cmd_list(\` → sort tasks by priority (missing = 2) before printing." "- [ ] list prints priority 1 first." "Tasks have a priority since phase 1; this phase sorts list by it." | sed "s/PLANFILE/2026-10-22-priority.md/g")

## Execution report
### Phase 1 — 2026-10-22
- Files: todo/cli.py.
- Added \`--priority\` (int, default 2); cmd_add stores it. \`python -m unittest -q\` -> OK.
- Deviation: renamed \`cmd_list\` to \`show_tasks\` (clearer next to the new sort); the dispatch dict uses the new name.
- [x] added tasks carry a priority.
MD
python3 - "$R/todo/cli.py" <<'PY'
import sys
p = sys.argv[1]; s = open(p).read()
s = s.replace('    add.add_argument("title")\n', '    add.add_argument("title")\n    add.add_argument("--priority", type=int, default=2)\n')
s = s.replace('{"title": args.title}', '{"title": args.title, "priority": args.priority}')
s = s.replace("cmd_list", "show_tasks")
open(p, "w").write(s)
PY
$GIT add -A
$GIT commit -qm "priority: phase 1"
