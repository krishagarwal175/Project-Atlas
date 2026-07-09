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
    elif cmd == "serve":
        _serve()
    else:
        print(f"Unknown command: {cmd}\n")
        print(__doc__)


if __name__ == "__main__":
    main()
