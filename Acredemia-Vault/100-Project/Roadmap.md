---
type: project
title: Roadmap
updated: 2026-07-09
---

# Roadmap

Guiding rule: **every phase is independently useful and shippable.** Nothing built speculatively.

## ✅ Phase 0 — The vault, by hand (DONE 2026-07-09)
Folder tree, templates, governance, taxonomy, Strategic-DNA stubs, worked seed loop. Usable today in Obsidian. Delivers institutional memory before any code.

## ✅ Phase 1 — Retrieval + Ingestion (DONE 2026-07-09) — `backend/`
- FastAPI service + CLI parse the vault (markdown+YAML+wikilinks+Evidence Ledger).
- Search across the whole vault (TF-IDF now; sentence-transformers-ready), confidence+freshness aware.
- Governance Bot: deterministic health audit → `900-Meta/Reviews/`.
- Market Intel ingestion (stdlib RSS, no deps) → `700-Market-Signals/` with relevance-routing vs [[Company-Profile]] keywords; degrades gracefully on dead feeds.
- Still fully usable by hand if the service is off. See `backend/README.md`.

## ✅ Phase 2 — Decision Engine (DONE 2026-07-09) — `backend/decision_engine.py`
- WSM scoring ([[F-MCDA-weighted-sum]]) with direction-aware normalization + editable weight presets; **renders the full arithmetic** and outputs a decision *note*, reasoning-trace-first.
- Decision Quality rubric + empty outcome baked into every generated note (Quality ≠ Outcome).
- **Strategic DNA guardrail**: a Non-Negotiable-violating alternative cannot be ranked #1.
- Deterministic **sensitivity/fragility** flag naming the responsible dimension.
- `POST /decide`, `GET /decision/presets`, `cli.py decide`.
- *Remaining for the experiment loop:* forced-retrospective enforcement is modelled in the template + governance; wiring a generated decision straight into its Question ledger is a follow-up.

## 🚧 Phase 3 — Graph Analytics + Understanding/Contradiction/Confidence
- ✅ NetworkX over parsed wikilinks (centrality, pathfinding, neighborhoods, clusters) — `backend/graph.py`, `/graph/*`.
- ✅ Confidence & Contradiction Engine over the Evidence Ledger (derived, self-correcting states) — `backend/epistemics.py`, `/epistemics`; drift folded into the Governance Bot.
- ✅ Freshness/Decay recomputation (caps confidence when lapsed).
- ✅ Thin web dashboard over `/graph` + `/epistemics` (`frontend/index.html`) with Save-decision-note + signal-triage actions.
- ✅ Optional local Ollama narrative layer with deterministic fallback (`backend/narrative.py`) — narrative only, never alters scores/confidence.
- Phase 3 complete. (Ollama-assisted *Theory drafting* remains an optional future enhancement, distinct from the narrative summaries now shipped.)

## Phase 4 — Enterprise extensibility
- Multi-vault/tenant, roles, hosted tier. "Your knowledge is portable markdown you own" becomes the sales pitch.

See [[Milestones]] · [[Backlog]].
