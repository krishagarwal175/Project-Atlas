"""Governance Bot (Module 8) — audits the health of the organizational brain.

Deterministic, explainable, write-only to its own audit note. It never edits
source notes. It surfaces rot; the founder decides. Implements the checklist in
900-Meta/Vault-Governance.md.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import config
from vault import Note, load_vault, build_backlinks, _link_key, _coerce_date


@dataclass
class Finding:
    severity: str      # high | medium | low
    category: str
    note: str          # filename or "-"
    message: str


def _half_life(note: Note) -> int | None:
    return config.HALF_LIFE_DAYS.get(note.type, config.DEFAULT_HALF_LIFE)


def _conf_rank(state: str) -> int:
    try:
        return config.CONFIDENCE_LADDER.index(state)
    except ValueError:
        return -1


def audit(notes: list[Note], today: date | None = None) -> list[Finding]:
    today = today or date.today()
    findings: list[Finding] = []
    # Backlinks must ignore the bot's own audit notes and templates as sources,
    # otherwise generating an audit note would "rescue" the orphans it reports.
    link_sources = [n for n in notes
                    if n.type != "template" and "/Reviews/" not in f"/{n.rel_path}"]
    backlinks = build_backlinks(link_sources)
    for n in notes:  # ensure every note has a (possibly empty) entry
        backlinks.setdefault(n.filename, [])
    by_key = {n.filename.lower(): n for n in notes}

    # Precompute: contradiction notes and what theory each targets.
    contradiction_targets: set[str] = set()
    for n in notes:
        if n.type == "contradiction":
            tgt = n.frontmatter.get("targets", "")
            if isinstance(tgt, str) and tgt:
                contradiction_targets.add(_link_key(tgt.strip("[]")))

    for n in notes:
        t = n.type
        # Templates, README, and the bot's own audit output are scaffolding — never audited.
        if t == "template" or n.filename.lower() == "readme" or "/Reviews/" in f"/{n.rel_path}":
            continue
        skip_structural = t in config.STRUCTURAL_TYPES

        # 1. Broken wikilinks (ignore template-style placeholders like [[T-...]])
        if not skip_structural:
            for raw, resolved in zip(n.raw_links, n.outlinks):
                if resolved.startswith("__UNRESOLVED__") and "..." not in raw:
                    findings.append(Finding("medium", "broken-link", n.filename,
                                            f"links to [[{raw}]] which resolves to no note"))

        # 2. Missing type
        if not t:
            findings.append(Finding("medium", "missing-type", n.filename,
                                    "note has no `type:` in frontmatter"))
            continue

        # 3. Orphan notes (no inbound and no outbound resolved links)
        has_out = any(not o.startswith("__UNRESOLVED__") for o in n.outlinks)
        has_in = bool(backlinks.get(n.filename))
        if not skip_structural and not has_out and not has_in:
            if t == "market-signal":
                findings.append(Finding("low", "untriaged-signal", n.filename,
                                        "ingested signal awaiting human triage — link it to a Q/Theory or delete"))
            else:
                findings.append(Finding("low", "orphan", n.filename,
                                        "no links in or out — not connected to the graph"))

        # 4. Untagged (non-structural)
        if not skip_structural and not n.frontmatter.get("tags"):
            findings.append(Finding("low", "untagged", n.filename, "no tags"))

        # 5. Decisions stuck in 'proposed' > 30 days
        if t == "decision" and n.status == "proposed":
            d = n.fm_date("date")
            if d and (today - d).days > 30:
                findings.append(Finding("medium", "stale-decision", n.filename,
                                        f"proposed {(today - d).days}d ago, still not active/concluded"))

        # 6. Concluded decisions missing an outcome
        if t == "decision" and n.status == "concluded":
            if not str(n.frontmatter.get("outcome", "")).strip():
                findings.append(Finding("high", "missing-outcome", n.filename,
                                        "marked concluded but Decision OUTCOME is empty"))

        # 7. Concluded experiments missing a result
        if t == "experiment" and n.status == "concluded":
            if "Actual outcome:" in n.body and n.body.split("Actual outcome:")[-1].strip()[:1] in ("", "\n"):
                findings.append(Finding("high", "missing-retrospective", n.filename,
                                        "concluded experiment has no result recorded"))

        # 8. Patterns with < 2 supporting case studies
        if t == "pattern":
            derived = n.frontmatter.get("derived-from") or []
            real = [d for d in derived if isinstance(d, str) and d.strip()]
            if len(real) < 2:
                findings.append(Finding("low", "weak-pattern", n.filename,
                                        f"derived from {len(real)} case(s); patterns need >=2"))

        # 9. Theories that rose past 'emerging' with no contradiction search
        if t == "theory":
            rank = _conf_rank(n.confidence_state)
            searched = n.filename.lower() in contradiction_targets or _has_contradiction_ledger(n)
            if rank >= _conf_rank("supported") and not searched:
                findings.append(Finding("high", "unchallenged-theory", n.filename,
                                        f"confidence '{n.confidence_state}' but no contradiction search found"))
            # 9b. Confidence drift: claims a state but ledger has no supporting evidence
            if rank >= _conf_rank("supported") and not any(l.stance == "supports" for l in n.ledger):
                findings.append(Finding("medium", "confidence-drift", n.filename,
                                        f"claims '{n.confidence_state}' but ledger has no supporting evidence"))

        # 10. Unanswered questions open > 30 days with no evidence & no experiment
        if t == "question" and n.status == "open":
            d = n.fm_date("created")
            old = d and (today - d).days > 30
            no_evidence = not any(l.stance for l in n.ledger)
            has_exp = bool(str(n.frontmatter.get("experiment", "")).strip()) or \
                any("exp-" in o.lower() for o in n.outlinks)
            if old and no_evidence and not has_exp:
                findings.append(Finding("medium", "stalled-question", n.filename,
                                        f"open {(today - d).days}d, no evidence and no experiment attached"))

        # 11. Orphaned observations (no link to a Question or Theory)
        if t == "observation":
            links_to_qt = any(
                (o in by_key and by_key[o].type in ("question", "theory"))
                for o in n.outlinks if not o.startswith("__UNRESOLVED__")
            )
            if not links_to_qt:
                findings.append(Finding("medium", "orphan-observation", n.filename,
                                        "observation not linked to any Question or Theory"))

        # 12. Freshness / decay + expired assumptions
        hl = _half_life(n)
        lr = n.fm_date("last-reviewed")
        if hl and lr:
            age = (today - lr).days
            if age > 2 * hl:
                sev = "high" if t == "assumption" else "medium"
                cat = "expired-assumption" if t == "assumption" else "stale-knowledge"
                findings.append(Finding(sev, cat, n.filename,
                                        f"last reviewed {age}d ago (half-life {hl}d) — {'expired' if age>2*hl else 'stale'}"))
            elif age > hl:
                findings.append(Finding("low", "needs-review", n.filename,
                                        f"last reviewed {age}d ago (half-life {hl}d) — due for review"))

        # 13. Explicit freshness flags set by a human
        if n.freshness in ("stale", "needs-review", "historical-only") and t not in config.STRUCTURAL_TYPES:
            findings.append(Finding("low", "flagged-freshness", n.filename,
                                    f"freshness set to '{n.freshness}'"))

    sev_order = {"high": 0, "medium": 1, "low": 2}
    findings.sort(key=lambda f: (sev_order.get(f.severity, 9), f.category, f.note))
    return findings


def _has_contradiction_ledger(n: Note) -> bool:
    return any(l.stance == "contradicts" for l in n.ledger)


def render_report(findings: list[Finding], today: date | None = None) -> str:
    today = today or date.today()
    counts: dict[str, int] = {}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1
    lines = [
        "---",
        "type: knowledge-review",
        f"title: Audit-{today.isoformat()}",
        f"date: {today.isoformat()}",
        "reviewer: [governance-bot]",
        "---",
        "",
        f"# 🔎 Governance Audit — {today.isoformat()}",
        "",
        "> Auto-generated by the Governance Bot. It surfaces rot; **you decide**. "
        "This note is safe to delete; re-run to regenerate.",
        "",
        f"**Summary:** {len(findings)} findings — "
        f"{counts.get('high',0)} high · {counts.get('medium',0)} medium · {counts.get('low',0)} low",
        "",
    ]
    if not findings:
        lines.append("✅ No issues found. The organizational brain is healthy.")
        return "\n".join(lines)

    by_cat: dict[str, list[Finding]] = {}
    for f in findings:
        by_cat.setdefault(f.category, []).append(f)

    for sev in ("high", "medium", "low"):
        sev_findings = [f for f in findings if f.severity == sev]
        if not sev_findings:
            continue
        icon = {"high": "🔴", "medium": "🟠", "low": "🟡"}[sev]
        lines.append(f"## {icon} {sev.title()} ({len(sev_findings)})")
        lines.append("")
        lines.append("| category | note | issue |")
        lines.append("|----------|------|-------|")
        for f in sev_findings:
            link = f"[[{f.note}]]" if f.note != "-" else "-"
            lines.append(f"| {f.category} | {link} | {f.message} |")
        lines.append("")
    return "\n".join(lines)


def run(write: bool = True) -> tuple[list[Finding], Path | None]:
    notes = load_vault()
    findings = audit(notes)
    out_path = None
    if write:
        today = date.today()
        out_dir = config.VAULT_PATH / "900-Meta" / "Reviews"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"Audit-{today.isoformat()}.md"
        out_path.write_text(render_report(findings, today), encoding="utf-8")
    return findings, out_path


if __name__ == "__main__":
    findings, path = run(write=True)
    print(f"Audit complete: {len(findings)} findings.")
    for f in findings[:40]:
        print(f"  [{f.severity:6}] {f.category:22} {f.note:45} {f.message}")
    if path:
        print(f"\nReport written to: {path}")
