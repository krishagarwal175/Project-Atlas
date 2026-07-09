"""Safe, minimal writes back to source notes — for HUMAN-initiated actions only.

The Governance Bot never mutates source notes; but explicit user actions from the
dashboard (triage a signal, link evidence) legitimately do. These helpers make
surgical edits: update a single frontmatter field, or append a bullet under a
named section. They preserve everything else in the file.
"""
from __future__ import annotations
import re
from pathlib import Path

import config
from vault import _link_key


def _find_note(name: str) -> Path | None:
    key = _link_key(name)
    for p in config.VAULT_PATH.rglob("*.md"):
        if p.stem.lower() == key:
            return p
    return None


def set_frontmatter_field(note_name: str, field: str, value: str) -> bool:
    p = _find_note(note_name)
    if not p:
        return False
    text = p.read_text(encoding="utf-8", errors="replace")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return False
    fm = m.group(1)
    line_re = re.compile(rf"^({re.escape(field)}):.*$", re.MULTILINE)
    new_line = f'{field}: "{value}"'
    if line_re.search(fm):
        fm2 = line_re.sub(new_line, fm)
    else:
        fm2 = fm + f"\n{new_line}"
    p.write_text(text[:m.start()] + f"---\n{fm2}\n---\n" + text[m.end():], encoding="utf-8")
    return True


def append_under_section(note_name: str, heading: str, bullet: str) -> bool:
    """Append `- bullet` immediately under a `## heading` line."""
    p = _find_note(note_name)
    if not p:
        return False
    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    out, inserted = [], False
    for i, line in enumerate(lines):
        out.append(line)
        if not inserted and re.match(rf"^#+\s*{re.escape(heading)}", line.strip()):
            out.append(f"- {bullet}")
            inserted = True
    if not inserted:  # heading not found — append at end
        out.append(f"\n## {heading}\n- {bullet}")
    p.write_text("\n".join(out) + "\n", encoding="utf-8")
    return True


def triage_signal(signal: str, target: str, stance: str = "supports") -> bool:
    """Link a market signal to a Question/Theory: set linked-to + add a Touches bullet."""
    ok1 = set_frontmatter_field(signal, "linked-to", f"[[{target}]]")
    ok2 = append_under_section(signal, "Touches", f"[[{target}]] (stance: {stance})")
    return ok1 or ok2
