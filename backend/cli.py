"""Unified CLI for the Acredemia Research OS backend.

    python cli.py parse                 # parse & summarize the vault
    python cli.py search "your query"   # semantic/keyword search
    python cli.py audit [--write]       # run the governance bot
    python cli.py ingest [--dry-run]    # pull market signals
    python cli.py stats                 # vault health snapshot
    python cli.py serve                 # start the FastAPI server

Works fully offline except `ingest`. No paid APIs anywhere.
"""
from __future__ import annotations
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def _parse():
    from vault import load_vault
    ns = load_vault()
    by_type: dict[str, int] = {}
    for n in ns:
        by_type[n.type or "(none)"] = by_type.get(n.type or "(none)", 0) + 1
    print(f"Parsed {len(ns)} notes.")
    for t, c in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"  {c:3d}  {t}")


def _search(args):
    from search import SearchEngine
    eng = SearchEngine()
    q = " ".join(args) or "referral growth"
    print(f"[{eng.backend}] {q!r}\n")
    for h in eng.search(q):
        print(f"  {h.score:6.3f} [{h.type:12}] {h.title}  (conf={h.confidence}, fresh={h.freshness})")


def _audit(args):
    from governance import run
    findings, path = run(write="--write" in args)
    sev = {}
    for f in findings:
        sev[f.severity] = sev.get(f.severity, 0) + 1
    print(f"{len(findings)} findings — " + " · ".join(f"{k}:{v}" for k, v in sev.items()) or "none")
    for f in findings:
        print(f"  [{f.severity:6}] {f.category:20} {f.note:40} {f.message}")
    if path:
        print(f"\nReport: {path}")


def _ingest(args):
    from market_intel import run
    run(write="--dry-run" not in args)


def _demo_decision():
    from decision_engine import Alternative, evaluate
    alts = [
        Alternative("Tier-2 colleges first", "acute credibility gap, low competition",
                    {"impact": 8, "confidence": 5, "alignment": 8, "cost": 4, "risk": 5, "effort": 5, "time": 4}),
        Alternative("Tier-1 colleges first", "prestige, crowded, weaker pull",
                    {"impact": 6, "confidence": 6, "alignment": 5, "cost": 6, "risk": 6, "effort": 6, "time": 6}),
    ]
    res = evaluate("Which college tier should we target as the beachhead?", alts, "channel-choice")
    print(f"Winner: {res.winner}  |  fragile={res.is_fragile} {res.fragile_reason}")
    for s in res.scored:
        flag = " ⚠DNA" if s.dna_conflict else ""
        print(f"  #{s.rank} {s.name}{flag}: {s.weighted_total}")
    if res.dna_flags:
        print("DNA flags:", res.dna_flags)
    print("(run the API POST /decide with write_note=true to emit a decision note)")


def _stats():
    from vault import load_vault, build_backlinks
    from governance import audit
    ns = load_vault()
    back = build_backlinks(ns)
    findings = audit(ns)
    orphans = [f for f in findings if f.category in ("orphan", "untriaged-signal")]
    total_links = sum(len(back[k]) for k in back)
    sev = {}
    for f in findings:
        sev[f.severity] = sev.get(f.severity, 0) + 1
    print(f"Notes:          {len(ns)}")
    print(f"Resolved links: {total_links}")
    print(f"Orphans/untriaged: {len(orphans)}")
    print(f"Audit issues:   {len(findings)}  ({', '.join(f'{k}:{v}' for k,v in sev.items()) or 'none'})")


def _serve():
    import uvicorn
    print("Serving on http://127.0.0.1:8000  (docs at /docs)")
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=False)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd, rest = sys.argv[1], sys.argv[2:]
    if cmd == "parse":
        _parse()
    elif cmd == "search":
        _search(rest)
    elif cmd == "audit":
        _audit(rest)
    elif cmd == "ingest":
        _ingest(rest)
    elif cmd == "stats":
        _stats()
    elif cmd == "decide":
        _demo_decision()
    elif cmd == "epistemics":
        from epistemics import assess_all
        for a in assess_all():
            badge = ("⚑" if a.contested else " ") + ("⌛" if a.decaying else " ")
            drift = "  <<< DRIFT" if a.drift else ""
            print(f"{badge} {a.note[:50]:50} {a.stated:12}→ derived {a.derived:12}{drift}")
            print(f"      {a.derivation}")
    elif cmd == "synthesize":
        from synthesis import synthesize
        cands = synthesize(use_ollama="--ollama" in rest)
        print(f"{len(cands)} candidate pattern(s):\n")
        for i, c in enumerate(cands, 1):
            tag = "NEW" if c.novelty == "new" else f"covered by {c.existing_pattern}"
            print(f"[{i}] ({tag}) {', '.join(c.companies)}  tags={c.shared_tags or '—'}")
            print(f"    {c.draft}\n")
    elif cmd == "graph":
        from graph import summary
        s = summary()
        print(f"{s['nodes']} nodes, {s['edges']} edges, {s['components']} component(s), "
              f"largest={s['largest_component']}, {s['isolates']} isolate(s)\n")
        print("Most central ideas:")
        for name, score in s["top_central"]:
            print(f"  {score:.3f}  {name}")
    elif cmd == "serve":
        _serve()
    else:
        print(f"Unknown command: {cmd}\n")
        print(__doc__)


if __name__ == "__main__":
    main()
