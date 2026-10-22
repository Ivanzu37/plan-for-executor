# Plan template

## Plan file

```markdown
---
status: approved
created: YYYY-MM-DD
repo: <absolute repo path>
branch: <branch>
commit: <short sha from git rev-parse --short HEAD, or "none">
phase: 1/1
executor: sonnet
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
### Phase 1 — <name>
1. `path` · anchor `<existing line or symbol>` → change.
2. ...

## Risks / do not touch
- ...

## Verification
- Exact commands and expected result.

## Prompt for the executor
### Phase 1
(the block below, filled in; one block per phase)

## Execution report
(the executor appends one entry per phase here)
```

Single-phase plans may drop the `### Phase` headings. Multi-phase plans keep one `### Phase N` heading per phase in **Steps** and in **Prompt for the executor**.

## Executor prompt

One fenced `text` block per phase, ready to copy:

```text
You are working in <absolute repo path>, branch <branch>. Execute phase <N> of <M> of this plan yourself, without subagents.

CONTEXT
<2-5 sentences: what the project is, what is wanted, why>

WORKING MODE
- Smallest complete change; reuse before writing new code.
- Work in slices: each step below is one slice. Build/compile after each, then continue.
- If something fails, find the root cause before changing code.
<profile extras for working mode>

BEFORE STARTING
- Set `status: in-progress` in <absolute plan path>.
- Base commit is <sha>. If `git rev-parse --short HEAD` is different, run `git diff <sha>..HEAD --stat -- <files from STEPS>`; if any of them changed, stop and report.
- Read <repo instructions and key files, absolute paths>.
- Check <anything that could not be verified while planning>.

STEPS
1. <absolute path> · anchor `<existing line or symbol>` → <concrete change: which function, what it does, signature if relevant>
2. ...

DO NOT TOUCH
- <files, branches, config, project rules to respect>

STOP AND REPORT IF
- A file or anchor above does not exist or looks different from what is described.
- The same check fails twice after a fix.
- A step needs a file from DO NOT TOUCH, or more than the steps describe.
- <task-specific assumptions that, if wrong, make the plan wrong>
When you stop, do not improvise: write what you found in the execution report and end.

DONE WHEN
- [ ] <checkable criterion>
- [ ] ...

VERIFY
- <exact commands> -> <expected result>

WHEN FINISHED
- Append to the "Execution report" section of <absolute plan path>: `### Phase <N> — YYYY-MM-DD`, then files changed, commands run and their result, deviations from the plan and why, what is left. Tick the DONE WHEN boxes that hold.
- Set `status: done` if this was the last phase and everything in DONE WHEN holds; `blocked` if you stopped; otherwise leave `in-progress`.
<profile extras for when finished>
- Do not commit or push unless the user asks.
```

Prompt rules:
- Absolute paths only. Never "as we discussed", "above", "this conversation".
- Small steps, in order, each with its file and its anchor.
- Respect the project's own rules from `CLAUDE.md`/`AGENTS.md`.
- Every label above appears in every phase block (`STOP AND REPORT IF` included).

## Labels in other languages

| English | Español |
|---|---|
| Context | Contexto |
| Decisions | Decisiones |
| Reuse | Reutiliza |
| Out of scope | Se omite |
| Files | Archivos |
| Steps | Pasos |
| Phase | Fase |
| Risks / do not touch | Riesgos y qué no tocar |
| Verification | Verificación |
| Prompt for the executor | Prompt para el ejecutor |
| Execution report | Informe de ejecución |
| CONTEXT | CONTEXTO |
| WORKING MODE | MODO |
| BEFORE STARTING | ANTES DE EMPEZAR |
| STEPS | PASOS |
| DO NOT TOUCH | NO TOQUES |
| STOP AND REPORT IF | PARA Y AVISA SI |
| DONE WHEN | HECHO CUANDO |
| VERIFY | VERIFICA |
| WHEN FINISHED | AL TERMINAR |
| `status` | `estado` |
| `phase` / `branch` | `fase` / `rama` |

## Self-check before handing off

- [ ] Every path, symbol and command in the prompt was seen this session, or sits in BEFORE STARTING as "check".
- [ ] Every step has a file, an anchor and a concrete change.
- [ ] VERIFY uses the project's own commands, with the expected result.
- [ ] STOP AND REPORT IF names the assumptions this plan depends on.
- [ ] DONE WHEN items are checkable by someone who did not plan it.
- [ ] No reference to this conversation; absolute paths only.
- [ ] The prompt in the plan file is the one handed out, word for word.
- [ ] `lint_plan.py` passes.
