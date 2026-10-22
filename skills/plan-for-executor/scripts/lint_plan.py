#!/usr/bin/env python3
"""Check a plan file written by plan-for-executor.

Usage: python3 lint_plan.py <plan.md> [more plans...] [--strict-paths] [--json]

Errors (exit 1): broken frontmatter, missing sections, prompt blocks without
the required labels, references to the planning conversation.
Warnings: paths that do not exist on this machine, relative paths in steps,
missing commit or branch.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import planlib  # noqa: E402

FORBIDDEN = re.compile(
    r"as we discussed|as discussed|this conversation|earlier in (?:the )?chat|"
    r"como hablamos|como dijimos|esta conversaci[oó]n|lo que hablamos",
    re.IGNORECASE,
)
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ABS_PATH = re.compile(r"(?:(?<=[\s`'\"(])|^)((?:~|/(?!/))[^\s`'\")]*|[A-Za-z]:\\[^\s`'\")]*)")
REL_PATH = re.compile(r"(?:^|[\s`(])((?:[\w.-]+/)+[\w.-]+\.\w+)")


def lint(path, strict_paths=False):
    errors, warnings = [], []
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        return [str(exc)], []

    # frontmatter
    fields, start = planlib.split_frontmatter(text)
    if not start:
        errors.append("no frontmatter (--- block at the top)")
    key = planlib.status_key(fields)
    if not key:
        errors.append("frontmatter has no `status` (or `estado`)")
    elif fields[key] not in planlib.STATUS[key]:
        errors.append(
            "`%s: %s` is not allowed; use one of: %s"
            % (key, fields[key], ", ".join(planlib.STATUS[key]))
        )
    if not DATE.match(fields.get("created", "")):
        errors.append("`created` must be YYYY-MM-DD")
    if not fields.get("repo"):
        errors.append("frontmatter has no `repo`")
    if not fields.get("commit"):
        warnings.append("no `commit`: the executor cannot tell whether the plan is stale")
    if not (fields.get("branch") or fields.get("rama")):
        warnings.append("no `branch` (or `rama`)")
    phase_value = fields.get("phase") or fields.get("fase")
    phase = planlib.parse_phase(phase_value)
    if phase_value and not phase:
        errors.append("`phase` must look like N/M, got `%s`" % phase_value)
    elif phase and not 1 <= phase[0] <= phase[1]:
        errors.append("`phase: %s` is out of range" % phase_value)

    # sections
    titles = [t for t, _, _ in planlib.h2_sections(text)]
    for sec, prefixes in planlib.SECTIONS.items():
        if not any(t.startswith(p) for t in titles for p in prefixes):
            errors.append("missing section: ## %s" % prefixes[0].capitalize())

    # prompt blocks
    blocks = planlib.prompt_blocks(text)
    if not blocks:
        errors.append("the prompt section has no fenced prompt block")
    total = phase[1] if phase else 1
    missing = [n for n in range(1, total + 1) if n not in blocks]
    if blocks and missing:
        errors.append(
            "phase count is %d but there is no prompt block for phase %s"
            % (total, ", ".join(map(str, missing)))
        )
    check_paths = True
    repo = os.path.expanduser(fields.get("repo", ""))
    if repo and not os.path.isdir(repo):
        warnings.append("repo `%s` is not on this machine; path checks skipped" % fields["repo"])
        check_paths = False
    for n, prompt in sorted(blocks.items()):
        errors.extend(lint_prompt(prompt, "phase %d prompt" % n, warnings, strict_paths, check_paths))

    fix = planlib.review_fix_prompt(text)
    if fix:
        errors.extend(lint_prompt(fix, "review fix prompt", warnings, strict_paths, check_paths))

    for i, line in enumerate(text.splitlines(), 1):
        if FORBIDDEN.search(line):
            errors.append("line %d refers to the planning conversation: %s" % (i, line.strip()[:80]))
    return errors, warnings


def lint_prompt(prompt, where, warnings, strict_paths, check_paths=True):
    errors = []
    found = planlib.label_lines(prompt)
    for key, spellings in planlib.LABELS.items():
        if key not in found:
            errors.append("%s has no %s block" % (where, " / ".join(spellings)))
    lines = prompt.splitlines()
    if "steps" in found:
        after = [k for k in found.values() if k > found["steps"]]
        end = min(after) if after else len(lines)
        steps = [l for l in lines[found["steps"] + 1 : end] if re.match(r"^\s*\d+\.", l)]
        if not steps:
            errors.append("%s: STEPS has no numbered step" % where)
        for step in steps:
            for rel in REL_PATH.findall(step):
                if not rel.startswith(("~", "/")) and "://" not in step:
                    warnings.append("%s: relative path in a step: %s" % (where, rel))
    seen = set()
    for line in lines if check_paths else []:
        if "://" in line:
            continue
        for raw in ABS_PATH.findall(line):
            p = raw.rstrip(".,;:")
            if len(p) < 3 or p in seen or "<" in p:
                continue
            seen.add(p)
            full = os.path.expanduser(p)
            if not os.path.exists(full) and not os.path.isdir(os.path.dirname(full.rstrip("/\\"))):
                msg = "%s: path not found on this machine: %s" % (where, p)
                (errors if strict_paths else warnings).append(msg)
    return errors


def main(argv):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    args = [a for a in argv if not a.startswith("--")]
    strict = "--strict-paths" in argv
    as_json = "--json" in argv
    if not args:
        print(__doc__.strip())
        return 2
    results, failed = {}, False
    for path in args:
        errors, warnings = lint(path, strict)
        results[path] = {"errors": errors, "warnings": warnings}
        failed = failed or bool(errors)
    if as_json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        for path, r in results.items():
            for e in r["errors"]:
                print("%s: ERROR: %s" % (path, e))
            for w in r["warnings"]:
                print("%s: WARN: %s" % (path, w))
            state = "FAIL" if r["errors"] else "OK"
            print("%s: %s (%d errors, %d warnings)" % (path, state, len(r["errors"]), len(r["warnings"])))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
