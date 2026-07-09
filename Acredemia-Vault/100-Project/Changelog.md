---
type: governance
title: Changelog
updated: 2026-07-09
---

# Changelog

Newest first. Every meaningful build/design change gets an entry (template: [[TPL-changelog-entry]]). Architectural changes also get an ADR in `300-Architecture/Tech-Decisions/`.

## 2026-07-09 — Phase 3 (part 3): UI actions + optional local narrative layer
- **What:** `backend/vault_write.py` (safe, surgical, human-initiated writes back to source notes — frontmatter field + section append), `backend/narrative.py` (optional **local Ollama** summaries with a deterministic extractive fallback when Ollama is absent — narrative only, never alters a score/confidence). New endpoints `POST /triage`, `GET /summarize`. Dashboard gained a **💾 Save decision note** button (writes a real decision note to `600-Decisions/`) and **per-signal triage** controls (link a signal to a Question/Theory, sourced from the live governance audit). All verified live in-browser: saved a decision note and triaged signals, watching the untriaged count drop 4→1.
- **Why:** Closes the loop from the dashboard — you can now act (decide, triage) without leaving the daily environment, and get plain-English summaries with zero cloud dependency.
- **Tradeoffs:** Ollama not installed here, so summaries use the deterministic fallback (by design); triage writes are intentionally minimal-surface to avoid corrupting notes.
- **Impacted modules:** new vault-write + narrative; API + dashboard.
- **Notable:** triaged 3 market signals via the UI/API during verification (inbox 4→1), demonstrating the human-in-the-loop signal flow end to end.
- **Follow-ups:** [ ] install Ollama for richer summaries (optional) · [ ] Phase 4 (multi-tenant / React) only if this goes beyond internal use.

## 2026-07-09 — Phase 3 (part 2): Web dashboard (daily operating environment)
- **What:** `frontend/index.html` — a single self-contained dashboard (no build step, no npm) over the API, plus CORS on the backend and a `.claude/launch.json`. Implements the "morning brief" (notes, confidence drifts, untriaged signals, audit issues), vault search, the confidence board (derived states + drift alerts), the market-signal inbox, the knowledge graph (centrality + path finder), and the decision engine (editable alternatives → ranked table with DNA guardrail + fragility). Verified live in-browser: header "60 notes · vault ok", all sections populated, search/decide/graph/epistemics all functional.
- **Why:** Turns the system into the daily environment the vision calls for — open it in the morning, see what changed, decide, all in one place — at zero cost and zero toolchain.
- **Tradeoffs:** vanilla single-file HTML rather than React/TS/Tailwind — instantly usable at single-user scale; a framework rebuild is deferred to Phase 4 (multi-tenant).
- **Impacted modules:** new frontend surface; backend gained CORS.
- **Follow-ups:** [ ] "write decision note" button in the UI · [ ] triage-signal action (link a signal to a Q/Theory from the UI) · [ ] optional Ollama narrative summaries (last Phase-3 piece).

## 2026-07-09 — Phase 3 (part 1): Epistemics + Graph Analytics
- **What:** `backend/epistemics.py` — **Confidence & Contradiction engine** (Module 10): recomputes each claim's confidence state from its Evidence Ledger + contradiction-search outcomes + freshness, enforcing the strict rule that a claim can't exceed `emerging` without a *survived* contradiction search; reports drift, contested, and decaying. `backend/graph.py` — **Graph Analytics** (Module 4): NetworkX over the wikilink graph for centrality, pathfinding, neighborhoods, clusters. Folded drift detection into the Governance Bot; added `/epistemics`, `/graph/*` API endpoints and `cli.py epistemics|graph`.
- **Why:** Confidence stops being a hand-set label and becomes a derived, explainable, self-correcting state; the graph exposes structure (most-central ideas, how concepts connect) Obsidian can't compute.
- **Notable:** the engine caught a hand-authored `supported` on [[T-two-sided-incentives-drive-referral-virality]] as an overclaim (no *survived* contradiction search on the revised claim) — **the system corrected its author**; the theory was set back to `emerging`/⚑contested with the reason logged in its evolution history.
- **Tradeoffs:** confidence weights/thresholds are heuristic (documented in `epistemics.py`), tuned for explainability over precision; patterns cap at `emerging` by design (to rise they must become theories).
- **Impacted modules:** Epistemics(10,11), Graph(4), Governance(8).
- **Future implications:** a thin web dashboard (Phase 3 part 2) can render the graph + confidence states directly from these endpoints; optional Ollama theory-drafting remains the last Phase-3 piece.
- **Follow-ups:** [ ] run the follow-up contradiction search on the revised referral theory · [ ] thin web dashboard over `/graph` + `/epistemics`.

## 2026-07-09 — Phase 2 Decision Engine built
- **What:** `backend/decision_engine.py` — Weighted Sum Model with min-max normalization (direction-aware: cost/risk/effort/time inverted), editable weight presets per decision type (config, not code), a **Strategic DNA guardrail** that demotes any alternative violating a Non-Negotiable below all clean options, a deterministic **sensitivity/fragility** pass that names the dimension whose ±20% move flips the winner, auto-pulled supporting evidence via retrieval, and **decision-note emission** (full arithmetic table + quality rubric + empty outcome). Exposed via `POST /decide`, `GET /decision/presets`, and `cli.py decide`. Generated [[DEC-2026-002-tier-2-colleges-first]] as a live example.
- **Why:** Turns a strategic choice into an explainable, DNA-checked, fragility-aware comparison that lands as a permanent decision note — the reasoning trace, not the score, is the asset.
- **Tradeoffs:** WSM only for now (AHP/TOPSIS deferred to an advanced mode); DNA conflicts are declared per-alternative by the user rather than auto-detected (auto-detection needs NLP against Non-Negotiables — a later refinement).
- **Impacted modules:** Decision Engine(6), consumes Retrieval(3) and Strategic-DNA(12).
- **Future implications:** Phase 3 confidence/contradiction compute and graph analytics build on the same notes; the decision note already carries the quality-vs-outcome split the calibration view will read.
- **Follow-ups:** [ ] auto-detect DNA conflicts via keyword/embedding match against Non-Negotiables · [ ] wire the generated decision back to its Question's evidence ledger.
- **Open questions:** should weight presets be per-decision editable in a UI, or stay config-level for now.

## 2026-07-09 — Phase 1 backend built (substrate gets a brain)
- **What:** Built the compute layer in `backend/` — vault parser (markdown+YAML+wikilinks+Evidence Ledger), Retrieval (TF-IDF now, embeddings-ready), Governance Bot (deterministic health audit), Market Intel (stdlib RSS ingest, relevance-routed), FastAPI REST surface, unified CLI. Also filled Strategic-DNA + Company-Profile with review-ready drafts; added case studies (PayPal, Slack, Figma, Homejoy failure) and two patterns; **evolved theory [[T-two-sided-incentives-drive-referral-virality]] via contradiction search [[CON-cash-referrals-that-worked]]** (refuted the "product-native" requirement, reframed around referred-user standalone utility).
- **Why:** Makes the vault searchable, auditable, and fed by market signals — while keeping every service reading/writing the same markdown files. Demonstrates the epistemic loop working on real content.
- **Tradeoffs:** Search is TF-IDF until `sentence-transformers` is installed; two RSS feeds currently fail (expired SSL / redirect) and are skipped gracefully; ingested 4 real EdSurge signals now sitting untriaged (bot flags them).
- **Impacted modules:** Retrieval(3), Governance(8), Market Intel(1), substrate parser. Decision Engine / graph analytics / confidence-contradiction compute still Phase 2–3.
- **Future implications:** Phase 2 Decision Engine and Phase 3 graph/confidence engines read these same files; the parser + Evidence Ledger extraction are the foundation they build on.
- **Follow-ups:** [ ] triage the 4 market signals · [ ] install sentence-transformers for semantic search · [ ] add 2nd supporting case to [[P-marketplace-leakage-kills-unit-economics]] (bot-flagged) · [ ] fix/replace the 2 failing RSS feeds.
- **Open questions:** which additional India-relevant free feeds to add for ed-tech/hiring signal.

## 2026-07-09 — Phase 0 vault scaffolded
- **What:** Created the full Acredemia Research OS vault — folder structure (000–900), all note templates (question, theory, contradiction, decision, case-study, pattern, experiment, observation, assumption, adr, market-signal, lesson, review, changelog), governance + taxonomy + glossary, Strategic-DNA stubs, and a worked end-to-end seed loop (Dropbox case → pattern → theory → contradiction search → question → decision (quality-scored) → experiment).
- **Why:** Phase 0 delivers the core "institutional memory" value by hand, before any backend exists, and de-risks the whole project (if the vault isn't used by hand, no app saves it).
- **Tradeoffs:** Manual upkeep until the Governance Bot and Dataview queries are wired; templates assume the Templater + Dataview plugins for full power.
- **Impacted modules:** all (this is the substrate).
- **Future implications:** every backend service (Phase 1+) reads/writes these files; nothing important lives only in a DB.
- **Follow-ups:** [ ] Founder to fill Strategic-DNA notes · [ ] install Dataview + Templater + Git plugins · [ ] write ADR-001.
- **Open questions:** which free RSS sources to seed Market Intel with (Phase 1).
