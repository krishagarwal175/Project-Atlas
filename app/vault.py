"""Vault parser — reads the markdown vault into structured Note objects.

Pure stdlib + PyYAML. This is the bridge between the human-authored substrate
(markdown) and every computational service. It NEVER writes to source notes
(except the governance audit note, which lives in its own Reviews/ folder).
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

import config

WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


@dataclass
class LedgerEntry:
    date: str = ""
    source: str = ""      # may contain a wikilink target
    stance: str = ""      # supports | contradicts
    weight: str = ""
    note: str = ""


@dataclass
class Note:
    path: Path
    rel_path: str
    filename: str          # stem, no extension
    frontmatter: dict[str, Any]
    body: str
    outlinks: list[str] = field(default_factory=list)   # resolved note keys
    raw_links: list[str] = field(default_factory=list)  # as written
    ledger: list[LedgerEntry] = field(default_factory=list)

    # convenience accessors -------------------------------------------------
    @property
    def type(self) -> str:
        return str(self.frontmatter.get("type", "")).strip().lower()

    @property
    def title(self) -> str:
        return str(self.frontmatter.get("title") or self.filename)

    @property
    def id(self) -> str:
        return str(self.frontmatter.get("id", "")).strip()

    @property
    def status(self) -> str:
        return str(self.frontmatter.get("status", "")).strip().lower()

    @property
    def confidence_state(self) -> str:
        return str(self.frontmatter.get("confidence-state", "")).strip().lower()

    @property
    def freshness(self) -> str:
        return str(self.frontmatter.get("freshness", "")).strip().lower()

    def fm_date(self, key: str) -> date | None:
        v = self.frontmatter.get(key)
        return _coerce_date(v)


def _coerce_date(v: Any) -> date | None:
    if v is None or v == "":
        return None
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(str(v).strip(), fmt).date()
        except ValueError:
            continue
    return None


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    try:
        fm = yaml.safe_load(m.group(1)) or {}
        if not isinstance(fm, dict):
            fm = {}
    except yaml.YAMLError:
        fm = {}
    return fm, text[m.end():]


def _parse_ledger(body: str) -> list[LedgerEntry]:
    """Extract markdown table rows that contain a 'stance' column."""
    entries: list[LedgerEntry] = []
    lines = body.splitlines()
    header_idx = None
    cols: list[str] = []
    for i, line in enumerate(lines):
        if "|" in line and "stance" in line.lower() and "---" not in line:
            cols = [c.strip().lower() for c in line.strip().strip("|").split("|")]
            if "stance" in cols:
                header_idx = i
                break
    if header_idx is None:
        return entries
    for line in lines[header_idx + 1:]:
        s = line.strip()
        if not s.startswith("|"):
            break
        if set(s) <= set("|-: "):  # separator row
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) != len(cols):
            continue
        row = dict(zip(cols, cells))
        stance = row.get("stance", "")
        if not stance or stance in ("supports | contradicts",):
            continue
        entries.append(
            LedgerEntry(
                date=row.get("date", ""),
                source=row.get("source", ""),
                stance=_norm_stance(stance),
                weight=row.get("weight", ""),
                note=row.get("note", ""),
            )
        )
    return entries


def _norm_stance(s: str) -> str:
    s = s.lower()
    if s.startswith("support"):
        return "supports"
    if s.startswith("contradict"):
        return "contradicts"
    return s


def _link_key(raw: str) -> str:
    """Normalize a wikilink target to a matching key (filename stem, lowercased)."""
    return raw.strip().split("/")[-1].removesuffix(".md").strip().lower()


def load_vault(vault_path: Path | None = None) -> list[Note]:
    vault_path = vault_path or config.VAULT_PATH
    notes: list[Note] = []
    for p in sorted(vault_path.rglob("*.md")):
        if any(part in config.IGNORE_DIRS for part in p.parts):
            continue
        if p.name == ".folder-note.md":
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        fm, body = _parse_frontmatter(text)
        rel = str(p.relative_to(vault_path)).replace("\\", "/")
        # Files under Templates/ are templates regardless of their sample frontmatter,
        # so a TPL-question doesn't masquerade as a real question in governance/search.
        if "/Templates/" in f"/{rel}":
            fm["type"] = "template"
        if str(fm.get("type", "")).strip().lower() in config.IGNORE_NOTE_TYPES:
            continue
        raw_links = WIKILINK_RE.findall(text)
        note = Note(
            path=p,
            rel_path=rel,
            filename=p.stem,
            frontmatter=fm,
            body=body,
            raw_links=[r.strip() for r in raw_links],
            ledger=_parse_ledger(body),
        )
        notes.append(note)

    # Resolve outlinks against known note keys (by filename stem, title, id).
    index: dict[str, str] = {}
    for n in notes:
        index[n.filename.lower()] = n.filename
        if n.title:
            index[n.title.strip().lower()] = n.filename
        if n.id:
            index[n.id.strip().lower()] = n.filename
    for n in notes:
        resolved = []
        for raw in n.raw_links:
            key = _link_key(raw)
            resolved.append(index.get(key, f"__UNRESOLVED__{raw.strip()}"))
        n.outlinks = resolved
    return notes


def build_backlinks(notes: list[Note]) -> dict[str, list[str]]:
    back: dict[str, list[str]] = {n.filename: [] for n in notes}
    for n in notes:
        for target in n.outlinks:
            if not target.startswith("__UNRESOLVED__") and target in back:
                back[target].append(n.filename)
    return back


if __name__ == "__main__":
    ns = load_vault()
    print(f"Parsed {len(ns)} notes from {config.VAULT_PATH}")
    by_type: dict[str, int] = {}
    for n in ns:
        by_type[n.type or "(none)"] = by_type.get(n.type or "(none)", 0) + 1
    for t, c in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"  {c:3d}  {t}")
    ledgers = sum(len(n.ledger) for n in ns)
    print(f"Ledger entries parsed: {ledgers}")
