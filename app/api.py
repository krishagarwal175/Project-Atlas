"""FastAPI service — exposes the Atlas compute layer over REST (localhost only).

Local-first: binds to 127.0.0.1, no auth, single user. The vault stays the source
of truth; this is a read/compute layer plus a write-only market-intel/governance
surface. Auto-generated OpenAPI docs at /docs double as the internal API reference.

Run:  uvicorn api:app --reload   (from the app/ folder)  — or:  python cli.py serve
"""
from __future__ import annotations
import sys
from datetime import date
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import config
import governance
import market_intel
import decision_engine
import epistemics
import graph as graphmod
import narrative
import vault_write
import synthesis
from search import SearchEngine
from vault import load_vault, build_backlinks

app = FastAPI(
    title="Acredemia Research OS",
    version="0.1.0",
    description="Knowledge → Understanding → Tested Theories → High-quality Decisions. "
                "The Obsidian vault is the source of truth; this is a rebuildable compute layer.",
)


# Local dev only: the dashboard is a static file opened from disk, so allow all
# origins. This backend is single-user and localhost-bound; no auth needed yet.
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)


# --- serve the local dashboard so a single process is self-contained -------
def _ui_dir() -> Path:
    """Locate ui/ in dev and inside a PyInstaller bundle (desktop .exe)."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "ui"          # type: ignore[attr-defined]
    return Path(__file__).resolve().parent.parent / "ui"


@app.get("/", include_in_schema=False)
def dashboard():
    idx = _ui_dir() / "index.html"
    if idx.exists():
        return FileResponse(str(idx))
    return {"atlas": "ok", "ui": "not bundled — open ui/index.html manually"}


@app.get("/tokens.css", include_in_schema=False)
def design_tokens():
    css = _ui_dir() / "tokens.css"
    if css.exists():
        return FileResponse(str(css), media_type="text/css")
    return JSONResponse(status_code=404, content={"error": "tokens.css not found"})


@lru_cache(maxsize=1)
def _engine() -> SearchEngine:
    return SearchEngine()


def _reset_cache():
    _engine.cache_clear()


@app.get("/health")
def health():
    notes = load_vault()
    return {
        "status": "ok",
        "vault": str(config.VAULT_PATH),
        "notes": len(notes),
        "search_backend": _engine().backend,
    }


@app.get("/search")
def search(q: str = Query(..., description="natural-language query"),
           k: int = Query(8, ge=1, le=30)):
    hits = _engine().search(q, k=k)
    return {"query": q, "backend": _engine().backend, "results": [h.__dict__ for h in hits]}


@app.get("/notes")
def notes(type: str | None = Query(None, description="filter by note type"),
          status: str | None = None):
    ns = load_vault()
    out = []
    for n in ns:
        if type and n.type != type.lower():
            continue
        if status and n.status != status.lower():
            continue
        out.append({
            "note": n.filename, "title": n.title, "type": n.type,
            "status": n.status, "confidence": n.confidence_state,
            "freshness": n.freshness, "rel_path": n.rel_path,
        })
    return {"count": len(out), "notes": out}


@app.get("/note/{filename}")
def note_detail(filename: str):
    ns = load_vault()
    back = build_backlinks(ns)
    for n in ns:
        if n.filename.lower() == filename.lower():
            return {
                "note": n.filename, "title": n.title, "type": n.type,
                "frontmatter": n.frontmatter,
                "outlinks": [o for o in n.outlinks if not o.startswith("__UNRESOLVED__")],
                "backlinks": back.get(n.filename, []),
                "ledger": [l.__dict__ for l in n.ledger],
                "body": n.body,
            }
    return JSONResponse(status_code=404, content={"error": f"note '{filename}' not found"})


@app.get("/audit")
def audit(write: bool = Query(False, description="also write the audit note to the vault")):
    ns = load_vault()
    findings = governance.audit(ns)
    if write:
        governance.run(write=True)
    sev = {}
    for f in findings:
        sev[f.severity] = sev.get(f.severity, 0) + 1
    return {"date": date.today().isoformat(), "summary": sev,
            "findings": [f.__dict__ for f in findings]}


class AltIn(BaseModel):
    name: str
    description: str = ""
    scores: dict[str, float] = Field(default_factory=dict)
    dna_conflict: str = ""


class DecideIn(BaseModel):
    question: str
    alternatives: list[AltIn]
    decision_type: str = "default"
    question_link: str = ""
    write_note: bool = False


@app.get("/decision/presets")
def decision_presets():
    return {"dimensions": config.DECISION_DIMENSIONS,
            "weight_presets": config.WEIGHT_PRESETS,
            "sensitivity_delta": config.SENSITIVITY_DELTA}


@app.post("/decide")
def decide(body: DecideIn):
    alts = [decision_engine.Alternative(a.name, a.description, a.scores, a.dna_conflict)
            for a in body.alternatives]
    res = decision_engine.evaluate(body.question, alts, body.decision_type)
    payload = {
        "question": res.question, "decision_type": res.decision_type,
        "winner": res.winner, "is_fragile": res.is_fragile,
        "fragile_reason": res.fragile_reason, "dna_flags": res.dna_flags,
        "weights": res.weights,
        "ranked": [{"rank": s.rank, "name": s.name, "total": s.weighted_total,
                    "contributions": s.contributions, "dna_conflict": s.dna_conflict}
                   for s in res.scored],
    }
    if body.write_note:
        path, dec_id = decision_engine.create_decision_note(res, body.question_link)
        _reset_cache()
        payload["note"] = {"id": dec_id, "path": str(path)}
    return payload


@app.get("/epistemics")
def epistemics_assess():
    items = epistemics.assess_all()
    return {"count": len(items), "drift": sum(1 for a in items if a.drift),
            "assessments": [a.__dict__ for a in items]}


@app.get("/graph/summary")
def graph_summary():
    return graphmod.summary()


@app.get("/graph/data")
def graph_data(max_nodes: int = Query(120, ge=10, le=400)):
    return graphmod.data(max_nodes=max_nodes)


class TriageIn(BaseModel):
    signal: str
    target: str
    stance: str = "supports"


@app.post("/triage")
def triage(body: TriageIn):
    ok = vault_write.triage_signal(body.signal, body.target, body.stance)
    _reset_cache()
    return {"ok": ok, "signal": body.signal, "target": body.target}


@app.get("/synthesize")
def synthesize(use_ollama: bool = Query(False)):
    cands = synthesis.synthesize(use_ollama=use_ollama)
    return {"count": len(cands), "candidates": [c.__dict__ for c in cands]}


class PromoteIn(BaseModel):
    members: list[str]


@app.post("/synthesize/promote")
def synthesize_promote(body: PromoteIn):
    cands = synthesis.synthesize()
    match = next((c for c in cands if set(c.members) == set(body.members)), None)
    if not match:
        return JSONResponse(status_code=404, content={"error": "no current candidate with those members"})
    path, pid = synthesis.promote_candidate(match)
    _reset_cache()
    return {"ok": True, "id": pid, "path": str(path)}


@app.get("/summarize")
def summarize(note: str, ollama: bool = Query(True, description="use local Ollama if available")):
    # ollama flag lets the UI force the deterministic fallback for reproducibility
    if not ollama:
        n = next((x for x in load_vault() if x.filename.lower() == note.lower()), None)
        if not n:
            return {"error": f"note '{note}' not found"}
        return {"note": n.filename, "engine": "extractive (forced)",
                "summary": narrative._extractive(n),
                "disclaimer": "Narrative only — does not alter any score or confidence."}
    return narrative.summarize_note(note)


@app.get("/graph/path")
def graph_path(a: str, b: str):
    p = graphmod.path(a, b)
    return {"a": a, "b": b, "path": p, "found": p is not None}


@app.get("/graph/neighbors")
def graph_neighbors(node: str, radius: int = Query(1, ge=1, le=3)):
    return {"node": node, "radius": radius, "neighbors": graphmod.neighbors(node, radius=radius)}


@app.post("/ingest")
def ingest(write: bool = Query(True, description="write signal notes to the vault"),
           dry_run: bool = False):
    items = market_intel.run(write=write and not dry_run)
    _reset_cache()  # new notes → rebuild search corpus next call
    return {"count": len(items), "items": [i.__dict__ for i in items]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=False)
