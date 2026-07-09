"""FastAPI service — exposes the Research OS compute layer over REST.

The vault stays the source of truth; this is a read/compute layer plus a
write-only market-intel/governance surface. Auto-generated OpenAPI docs at /docs
double as the internal API reference.

Run:  uvicorn api:app --reload   (from the backend/ folder)
"""
from __future__ import annotations
from datetime import date
from functools import lru_cache

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

import config
import governance
import market_intel
import decision_engine
import epistemics
import graph as graphmod
from search import SearchEngine
from vault import load_vault, build_backlinks

app = FastAPI(
    title="Acredemia Research OS",
    version="0.1.0",
    description="Knowledge → Understanding → Tested Theories → High-quality Decisions. "
                "The Obsidian vault is the source of truth; this is a rebuildable compute layer.",
)


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
