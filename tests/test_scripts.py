"""Tests for lint_plan.py, run_plan.py and planlib.py. Run: python3 -m unittest -v"""
import os
import stat
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "plan-for-executor", "scripts")
EXAMPLE = os.path.join(ROOT, "examples", "2026-10-22-add-due-dates.md")
sys.path.insert(0, SCRIPTS)

import lint_plan  # noqa: E402
import planlib  # noqa: E402
import run_plan  # noqa: E402

with open(EXAMPLE, encoding="utf-8") as fh:
    EXAMPLE_TEXT = fh.read()

SPANISH = """---
estado: aprobado
created: 2026-10-22
repo: {repo}
rama: main
commit: abc1234
fase: 1/1
---
# Plan · prueba

## Contexto
Algo.

## Decisiones
- Una.

## Archivos
- `{repo}/a.txt` -> cambia

## Pasos
1. `{repo}/a.txt` · ancla `hola` → adiós.

## Verificación
- `cat a.txt` -> adiós

## Prompt para el ejecutor
```text
Trabajas en {repo}, rama main.

CONTEXTO
Algo.

PASOS
1. {repo}/a.txt · ancla `hola` → adiós.

NO TOQUES
- nada

PARA Y AVISA SI
- falta el archivo.

HECHO CUANDO
- [ ] dice adiós

VERIFICA
- cat a.txt -> adiós

AL TERMINAR
- Informe.
```

## Informe de ejecución
"""


def lint_text(text):
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as fh:
        fh.write(text)
    try:
        return lint_plan.lint(fh.name)
    finally:
        os.unlink(fh.name)


class LintTest(unittest.TestCase):
    def test_example_passes(self):
        errors, _ = lint_plan.lint(EXAMPLE)
        self.assertEqual(errors, [])

    def test_spanish_plan_passes(self):
        with tempfile.TemporaryDirectory() as repo:
            open(os.path.join(repo, "a.txt"), "w").close()
            errors, warnings = lint_text(SPANISH.format(repo=repo))
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_free_form_status_fails(self):
        errors, _ = lint_text(EXAMPLE_TEXT.replace("status: in-progress", "status: c1-hecho"))
        self.assertTrue(any("not allowed" in e for e in errors))

    def test_missing_stop_block_fails(self):
        errors, _ = lint_text(EXAMPLE_TEXT.replace("STOP AND REPORT IF", "NOTES", 1))
        self.assertTrue(any("phase 1 prompt has no STOP AND REPORT IF" in e for e in errors))

    def test_conversation_reference_fails(self):
        errors, _ = lint_text(EXAMPLE_TEXT.replace("Smallest complete change", "As we discussed, smallest change", 1))
        self.assertTrue(any("planning conversation" in e for e in errors))

    def test_phase_count_mismatch_fails(self):
        errors, _ = lint_text(EXAMPLE_TEXT.replace("phase: 2/2", "phase: 2/3"))
        self.assertTrue(any("no prompt block for phase 3" in e for e in errors))

    def test_missing_section_fails(self):
        errors, _ = lint_text(EXAMPLE_TEXT.replace("## Verification", "## Checks"))
        self.assertIn("missing section: ## Verification", errors)

    def test_missing_path_is_warning_unless_strict(self):
        with tempfile.TemporaryDirectory() as repo:
            text = SPANISH.format(repo=repo).replace("/a.txt", "/nope/a.txt")
            errors, warnings = lint_text(text)
            self.assertEqual(errors, [])
            self.assertTrue(any("path not found" in w for w in warnings))


class PlanlibTest(unittest.TestCase):
    def test_prompt_blocks_by_phase(self):
        blocks = planlib.prompt_blocks(EXAMPLE_TEXT)
        self.assertEqual(sorted(blocks), [1, 2])
        self.assertIn("phase 2 of 2", blocks[2])

    def test_labels_do_not_collide(self):
        found = planlib.label_lines("VERIFICA\nx\nCONTEXTO\n")
        self.assertEqual(set(found), {"verify", "context"})


class RunPlanTest(unittest.TestCase):
    def test_picks_current_phase(self):
        self.assertIn("phase 2 of 2", run_plan.pick_prompt(EXAMPLE_TEXT))
        self.assertIn("phase 1 of 2", run_plan.pick_prompt(EXAMPLE_TEXT, phase=1))

    def test_review_fix_requires_a_block(self):
        with self.assertRaises(SystemExit):
            run_plan.pick_prompt(EXAMPLE_TEXT, review_fix=True)

    def test_launches_claude_in_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = os.path.join(tmp, "repo")
            bindir = os.path.join(tmp, "bin")
            os.makedirs(repo)
            os.makedirs(bindir)
            open(os.path.join(repo, "a.txt"), "w").close()
            plan = os.path.join(tmp, "plan.md")
            with open(plan, "w", encoding="utf-8") as fh:
                fh.write(SPANISH.format(repo=repo))
            log = os.path.join(tmp, "args.txt")
            fake = os.path.join(bindir, "claude")
            with open(fake, "w") as fh:
                fh.write('#!/bin/sh\npwd > "%s"\nprintf "%%s\\n" "$@" >> "%s"\n' % (log, log))
            os.chmod(fake, os.stat(fake).st_mode | stat.S_IEXEC)
            env = dict(os.environ, PATH=bindir + os.pathsep + os.environ["PATH"])
            code = subprocess.call(
                [sys.executable, os.path.join(SCRIPTS, "run_plan.py"), plan, "--model", "haiku"],
                env=env,
                stderr=subprocess.DEVNULL,
            )
            self.assertEqual(code, 0)
            with open(log) as fh:
                out = fh.read().splitlines()
            self.assertEqual(os.path.realpath(out[0]), os.path.realpath(repo))
            self.assertEqual(out[1:3], ["--model", "haiku"])
            self.assertIn("PARA Y AVISA SI", "\n".join(out))


if __name__ == "__main__":
    unittest.main()
