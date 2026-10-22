#!/usr/bin/env python3
"""Open a new executor session with the prompt of a plan file.

Usage: python3 run_plan.py <plan.md> [--phase N] [--review-fix] [--model M]
                           [--cwd DIR] [--print] [--force]

Picks the prompt of the current phase (frontmatter `phase: N/M`, or --phase),
or the fix prompt of the last review with --review-fix. Runs the plan's lint
first and refuses to start on errors unless --force. Then starts
`claude --model <M> "<prompt>"` in the plan's repo. The model comes from
--model, the plan's `executor`, $PLAN_EXECUTOR_MODEL, or "sonnet".
--print only prints the prompt (to pipe it or copy it by hand).
"""
import argparse
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lint_plan  # noqa: E402
import planlib  # noqa: E402


def pick_prompt(text, phase=None, review_fix=False):
    if review_fix:
        prompt = planlib.review_fix_prompt(text)
        if not prompt:
            raise SystemExit("no fix prompt in the last review section")
        return prompt
    fields, _ = planlib.split_frontmatter(text)
    if phase is None:
        current = planlib.parse_phase(fields.get("phase") or fields.get("fase"))
        phase = current[0] if current else 1
    blocks = planlib.prompt_blocks(text)
    if phase not in blocks:
        raise SystemExit("no prompt block for phase %d" % phase)
    return blocks[phase]


def main(argv):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Start the executor session for a plan.")
    ap.add_argument("plan")
    ap.add_argument("--phase", type=int)
    ap.add_argument("--review-fix", action="store_true")
    ap.add_argument("--model")
    ap.add_argument("--cwd")
    ap.add_argument("--print", action="store_true", dest="print_only")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args(argv)

    with open(args.plan, encoding="utf-8") as fh:
        text = fh.read()
    prompt = pick_prompt(text, args.phase, args.review_fix)
    if args.print_only:
        print(prompt)
        return 0

    errors, _ = lint_plan.lint(args.plan)
    if errors and not args.force:
        for e in errors:
            print("ERROR: %s" % e, file=sys.stderr)
        print("The plan does not pass the lint; fix it or use --force.", file=sys.stderr)
        return 1

    fields, _ = planlib.split_frontmatter(text)
    cwd = os.path.expanduser(args.cwd or fields.get("repo", ""))
    if not os.path.isdir(cwd):
        print("repo `%s` is not a folder on this machine; pass --cwd" % cwd, file=sys.stderr)
        return 1
    model = args.model or fields.get("executor") or os.environ.get("PLAN_EXECUTOR_MODEL") or "sonnet"
    claude = shutil.which("claude")
    if not claude:
        print("`claude` is not on PATH; use --print and paste the prompt by hand", file=sys.stderr)
        return 1
    print("Starting %s in %s ..." % (model, cwd), file=sys.stderr)
    return subprocess.call([claude, "--model", model, prompt], cwd=cwd)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
