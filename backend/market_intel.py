"""Market Intelligence (Module 1) — ingest free public RSS/Atom feeds.

Pure stdlib (urllib + ElementTree): no paid APIs, no extra deps, no login-walls.
Pipeline: fetch → parse → dedup → relevance-score vs Company-Profile keywords →
route {ignore|log|flag-for-review} → write market-signal notes into 700-Market-Signals/.

Hard rule (see §13/§18 of the spec): a signal may LINK to a decision as context,
but NEVER auto-modifies a score. Interpretation is always routed to a human.
Failure mode: any feed that errors is skipped and logged; the app is fine without it.
"""
from __future__ import annotations
import re
import urllib.request
import urllib.error
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from xml.etree import ElementTree as ET

import config

_WORD_RE = re.compile(r"[a-z0-9][a-z0-9\-]+")
_TAG_RE = re.compile(r"\{[^}]+\}")   # strip XML namespaces
USER_AGENT = "AcredemiaResearchOS/0.1 (+local; free RSS reader)"


@dataclass
class SignalItem:
    source: str
    title: str
    link: str
    summary: str
    published: str
    matched: list[str]
    relevance: str   # ignore | log | flag-for-review


def load_relevance_keywords() -> list[str]:
    """Read the backticked keyword list from Company-Profile.md; fallback to defaults."""
    profile = config.VAULT_PATH / "500-Acredemia" / "Company-Profile.md"
    defaults = ["verification", "hiring", "recruiter", "credential", "ed-tech",
                "edtech", "campus", "student", "background check", "college"]
    if not profile.exists():
        return defaults
    text = profile.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"Relevance keywords.*?\n`([^`]+)`", text, re.DOTALL)
    if not m:
        return defaults
    kws = [k.strip().lower() for k in m.group(1).split(",") if k.strip()]
    return kws or defaults


def _fetch(url: str, timeout: int = 15) -> bytes | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except Exception as e:  # network down, 404, timeout — skip gracefully
        print(f"  ! skipped feed {url}: {e}")
        return None


def _localname(tag: str) -> str:
    return _TAG_RE.sub("", tag)


def _parse_feed(raw: bytes, source: str) -> list[dict]:
    items: list[dict] = []
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return items
    # RSS: channel/item ; Atom: entry
    nodes = [e for e in root.iter() if _localname(e.tag) in ("item", "entry")]
    for node in nodes:
        rec = {"title": "", "link": "", "summary": "", "published": ""}
        for child in node:
            name = _localname(child.tag).lower()
            if name == "title":
                rec["title"] = (child.text or "").strip()
            elif name == "link":
                rec["link"] = (child.text or child.attrib.get("href", "")).strip()
            elif name in ("description", "summary", "content"):
                rec["summary"] = re.sub(r"<[^>]+>", "", (child.text or "")).strip()[:400]
            elif name in ("pubdate", "published", "updated"):
                rec["published"] = (child.text or "").strip()
        if rec["title"]:
            items.append(rec)
    return items


def _score_relevance(text: str, keywords: list[str]) -> list[str]:
    low = text.lower()
    return sorted({kw for kw in keywords if kw in low})


def _route(n_matches: int) -> str:
    if n_matches >= config.RELEVANCE_FLAG_KEYWORDS:
        return "flag-for-review"
    if n_matches >= config.RELEVANCE_MIN_KEYWORDS:
        return "log"
    return "ignore"


def collect(max_per_feed: int = 15) -> list[SignalItem]:
    keywords = load_relevance_keywords()
    seen_links: set[str] = set()
    out: list[SignalItem] = []
    for source, url in config.RSS_FEEDS:
        raw = _fetch(url)
        if not raw:
            continue
        for rec in _parse_feed(raw, source)[:max_per_feed]:
            link = rec["link"]
            if link and link in seen_links:
                continue
            seen_links.add(link)
            blob = f"{rec['title']} {rec['summary']}"
            matched = _score_relevance(blob, keywords)
            relevance = _route(len(matched))
            if relevance == "ignore":
                continue
            out.append(SignalItem(
                source=source, title=rec["title"], link=link,
                summary=rec["summary"], published=rec["published"],
                matched=matched, relevance=relevance,
            ))
    return out


def _slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:60] or "signal"


def write_signals(items: list[SignalItem]) -> list[Path]:
    out_dir = config.VAULT_PATH / "700-Market-Signals"
    out_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    written: list[Path] = []
    for it in items:
        fname = f"MS-{today}-{_slug(it.title)}.md"
        path = out_dir / fname
        if path.exists():
            continue
        tags = " ".join(f"domain/{m.replace(' ', '-')}" for m in it.matched[:4])
        content = f"""---
type: market-signal
source-name: "{it.source}"
source-url: "{it.link}"
published: "{it.published}"
ingested: {today}
relevance: {it.relevance}
matched-keywords: [{", ".join(repr(m) for m in it.matched)}]
linked-to: ""
freshness: fresh
half-life-days: 90
tags: [{', '.join(f'"{t}"' for t in tags.split()) if tags else ''}]
---

# 📡 {it.title}

**Source:** {it.source} · [link]({it.link}) · published {it.published or 'n/a'}
**Matched keywords:** {', '.join(it.matched)}
**Relevance:** `{it.relevance}`

## Summary (as ingested)
{it.summary or '(no summary provided by feed)'}

## Why it might matter to Acredemia
<Human triage: does this touch an assumption or theory? Link it below or delete this note.>

## Touches
- [[...]] (stance: supports | contradicts)

> A signal may LINK to a decision as context. It must never auto-modify a score.
"""
        path.write_text(content, encoding="utf-8")
        written.append(path)
    return written


def run(write: bool = True) -> list[SignalItem]:
    print(f"Ingesting {len(config.RSS_FEEDS)} feeds; relevance vs Company-Profile keywords…")
    items = collect()
    print(f"  {len(items)} relevant items after routing "
          f"({sum(1 for i in items if i.relevance=='flag-for-review')} flagged for review).")
    if write and items:
        paths = write_signals(items)
        print(f"  Wrote {len(paths)} new signal notes to 700-Market-Signals/.")
    return items


if __name__ == "__main__":
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    write = "--dry-run" not in sys.argv
    items = run(write=write)
    for it in items[:15]:
        print(f"  [{it.relevance:15}] ({it.source}) {it.title[:70]}  «{','.join(it.matched)}»")
