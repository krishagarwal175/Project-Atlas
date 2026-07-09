---
type: project
title: Roadmap
updated: 2026-07-09
---

# Roadmap

Guiding rule: **every phase is independently useful.** Nothing built speculatively. Atlas is a **Local-First, single-user** Strategic OS ([[ADR-003-local-first-single-user]]) — optimize for daily solo work, never for deployment.

## ✅ Phase 0 — The vault, by hand (DONE 2026-07-09)
Folder tree, templates, governance, taxonomy, Strategic-DNA stubs, worked seed loop. Usable today in Obsidian. Delivers institutional memory before any code.

## ✅ Phase 1 — Retrieval + Ingestion (DONE 2026-07-09) — `app/`
- FastAPI service + CLI parse the vault (markdown+YAML+wikilinks+Evidence Ledger).
- Search across the whole vault (TF-IDF now; sentence-transformers-ready), confidence+freshness aware.
- Governance Bot: deterministic health audit → `900-Meta/Reviews/`.
- Market Intel ingestion (stdlib RSS, no deps) → `700-Market-Signals/` with relevance-routing vs [[Company-Profile]] keywords; degrades gracefully on dead feeds.
- Still fully usable by hand if the service is off. See `app/README.md`.

## ✅ Phase 2 — Decision Engine (DONE 2026-07-09) — `app/decision_engine.py`
- WSM scoring ([[F-MCDA-weighted-sum]]) with direction-aware normalization + editable weight presets; **renders the full arithmetic** and outputs a decision *note*, reasoning-trace-first.
- Decision Quality rubric + empty outcome baked into every generated note (Quality ≠ Outcome).
- **Strategic DNA guardrail**: a Non-Negotiable-violating alternative cannot be ranked #1.
- Deterministic **sensitivity/fragility** flag naming the responsible dimension.
- `POST /decide`, `GET /decision/presets`, `cli.py decide`.
- *Remaining for the experiment loop:* forced-retrospective enforcement is modelled in the template + governance; wiring a generated decision straight into its Question ledger is a follow-up.

## 🚧 Phase 3 — Graph Analytics + Understanding/Contradiction/Confidence
- ✅ NetworkX over parsed wikilinks (centrality, pathfinding, neighborhoods, clusters) — `app/graph.py`, `/graph/*`.
- ✅ Confidence & Contradiction Engine over the Evidence Ledger (derived, self-correcting states) — `app/epistemics.py`, `/epistemics`; drift folded into the Governance Bot.
- ✅ Freshness/Decay recomputation (caps confidence when lapsed).
- ✅ Thin web dashboard over `/graph` + `/epistemics` (`ui/index.html`) with Save-decision-note + signal-triage actions.
- ✅ Optional local Ollama narrative layer with deterministic fallback (`app/narrative.py`) — narrative only, never alters scores/confidence.
- Phase 3 complete. (Ollama-assisted *Theory drafting* remains an optional future enhancement, distinct from the narrative summaries now shipped.)

## Phase 4 — Local polish (the daily-driver phase)
Being *excellent to use every morning*, not going public:
- Deeper daily-use ergonomics in the dashboard; keyboard-first flows.
- (Optional durability) API-layer tests + a local test-runner script.
- (Optional) desktop packaging exploration (Electron/Tauri) — architecture already kept compatible (invariant I16); not built yet.

## Phase 5 — Possible future: multi-user / cloud (explicitly out of scope for v1)
Only if Atlas is ever offered beyond personal use: multi-vault/tenant, roles, a hosted tier. The vault-per-org model (ADR-002 §38) keeps this *possible*, but v1 ignores it entirely and gets excellent locally first. Revive the archived marketing page (`archive/marketing/`) via a new ADR if that day ever comes.

See [[Milestones]] · [[Backlog]].
