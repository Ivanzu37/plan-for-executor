"""Shared parsing for plan files: frontmatter, sections and prompt blocks.

Standard library only. Plans may be written in English or Spanish; every
name below lists both spellings.
"""
import re

STATUS = {
    "status": ["draft", "approved", "in-progress", "blocked", "done", "dropped"],
    "estado": ["borrador", "aprobado", "en-curso", "bloqueado", "hecho", "descartado"],
}

# section key -> accepted H2 titles (lowercase, compared by prefix)
SECTIONS = {
    "context": ["context", "contexto"],
    "decisions": ["decisions", "decisiones"],
    "files": ["files", "archivos"],
    "steps": ["steps", "pasos"],
    "verification": ["verification", "verificación", "verificacion"],
    "prompt": ["prompt"],
}
REPORT_TITLES = ["execution report", "informe de ejecución", "informe de ejecucion", "informe"]
REVIEW_TITLES = ["review", "revisión", "revision"]

# prompt label key -> accepted spellings (a line must start with one of them)
LABELS = {
    "context": ["CONTEXT", "CONTEXTO"],
    "steps": ["STEPS", "PASOS"],
    "do_not_touch": ["DO NOT TOUCH", "NO TOQUES"],
    "stop_if": ["STOP AND REPORT IF", "PARA Y AVISA SI"],
    "done_when": ["DONE WHEN", "HECHO CUANDO"],
    "verify": ["VERIFY", "VERIFICA"],
    "when_finished": ["WHEN FINISHED", "AL TERMINAR"],
}

PHASE_HEADING = re.compile(r"^###\s+(?:phase|fase)\s+(\d+)\b", re.IGNORECASE)
FENCE = re.compile(r"^(`{3,}|~{3,})\s*([\w-]*)\s*$")


def split_frontmatter(text):
    """Return (fields, body_start_index). Fields keep their raw string value."""
    if not text.startswith("---"):
        return {}, 0
    end = text.find("\n---", 3)
    if end == -1:
        return {}, 0
    fields = {}
    for line in text[3:end].splitlines():
        m = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", line)
        if m:
            fields[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    close = text.find("\n", end + 1)
    return fields, (len(text) if close == -1 else close + 1)


def status_key(fields):
    for key in STATUS:
        if key in fields:
            return key
    return None


def parse_phase(value):
    m = re.match(r"^\s*(\d+)\s*/\s*(\d+)\s*$", value or "")
    return (int(m.group(1)), int(m.group(2))) if m else None


def lines_outside_fences(lines):
    """Yield (index, line, inside_fence) for every line."""
    fence = None
    for i, line in enumerate(lines):
        m = FENCE.match(line)
        if fence is None and m:
            fence = m.group(1)
            yield i, line, True
            continue
        if fence is not None:
            if line.strip().startswith(fence) and line.strip() == fence[0] * len(line.strip()):
                fence = None
            yield i, line, True
            continue
        yield i, line, False


def h2_sections(text):
    """List of (title_lowercase, start_line, end_line) for every ## heading."""
    lines = text.splitlines()
    heads = [
        (i, line[3:].strip())
        for i, line, fenced in lines_outside_fences(lines)
        if not fenced and line.startswith("## ")
    ]
    out = []
    for n, (i, title) in enumerate(heads):
        end = heads[n + 1][0] if n + 1 < len(heads) else len(lines)
        out.append((title.lower(), i, end))
    return out


def find_section(text, prefixes, last=False):
    hits = [s for s in h2_sections(text) if any(s[0].startswith(p) for p in prefixes)]
    if not hits:
        return None
    return hits[-1] if last else hits[0]


def fenced_blocks(lines):
    """List of (start_line, lang, content) for fenced blocks in lines."""
    out, fence, lang, buf, start = [], None, "", [], 0
    for i, line in enumerate(lines):
        m = FENCE.match(line)
        if fence is None:
            if m:
                fence, lang, buf, start = m.group(1), m.group(2), [], i
        elif line.strip() == fence[0] * len(line.strip()) and len(line.strip()) >= len(fence):
            out.append((start, lang, "\n".join(buf)))
            fence = None
        else:
            buf.append(line)
    return out


def prompt_blocks(text):
    """Return {phase_number: prompt_text} from the prompt section.

    With `### Phase N` headings each phase takes the first fenced block under
    its heading; without them the first fenced block is phase 1.
    """
    sec = find_section(text, SECTIONS["prompt"])
    if not sec:
        return {}
    lines = text.splitlines()[sec[1] + 1 : sec[2]]
    phases, current = {}, None
    heading_seen = False
    for start, _lang, content in fenced_blocks(lines):
        current = None
        for j in range(start, -1, -1):
            m = PHASE_HEADING.match(lines[j])
            if m:
                current = int(m.group(1))
                heading_seen = True
                break
        key = current if current is not None else (1 if not heading_seen else None)
        if key is not None and key not in phases:
            phases[key] = content
    return phases


def review_fix_prompt(text):
    """The first fenced block in the last Review section, if any."""
    sec = find_section(text, REVIEW_TITLES, last=True)
    if not sec:
        return None
    blocks = fenced_blocks(text.splitlines()[sec[1] + 1 : sec[2]])
    return blocks[0][2] if blocks else None


def label_lines(prompt):
    """{label_key: line_index} for the labels found at the start of a line."""
    found = {}
    for i, line in enumerate(prompt.splitlines()):
        stripped = line.strip()
        for key, spellings in LABELS.items():
            if key in found:
                continue
            for s in spellings:
                if stripped == s or re.match(r"^%s\b" % re.escape(s), stripped):
                    # "VERIFY" must not swallow "VERIFICA" and vice versa
                    rest = stripped[len(s):]
                    if not rest or not rest[0].isalpha():
                        found[key] = i
    return found
