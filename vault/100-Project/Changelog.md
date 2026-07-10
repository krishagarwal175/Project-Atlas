---
type: governance
title: Changelog
updated: 2026-07-09
---

# Changelog

Newest first. Every meaningful build/design change gets an entry (template: [[TPL-changelog-entry]]). Architectural changes also get an ADR in `300-Architecture/Tech-Decisions/`.

## 2026-07-10 — 📚 Knowledge Gen-2: sourced company histories
- **What:** Added four **sourced** company histories — [[Stripe]] (developer-experience-as-distribution), [[Airbnb]] (trust/quality as product; near-death survival), [[Amazon]] (the flywheel; Prime; long-term orientation), [[Zerodha]] (bootstrapped, trust, pricing disruption — India) — plus the [[Airbnb-photography-experiment]] as an atomic case study. Each carries `source-urls` (web-researched, cited); every note focuses on *strategic decisions and lessons for Acredemia*, not encyclopedia recall.
- **Discipline held:** metrics are cited to sources; nothing invented. Histories cross-link into the Gen-1 mental models/frameworks (flywheel→systems-thinking, DX→JTBD, bootstrapping→margin-of-safety, photography→marketplace cold-start & do-things-that-don't-scale).
- **Result:** vault 104→109 notes, graph links 575→623; governance clean (1 pre-existing signal), 43 tests green. Startup-History-MOC + Research-Backlog updated; remaining histories (GitHub, Notion/Canva, Razorpay, Zoho) queued.

## 2026-07-10 — 📚 Knowledge foundation, Generation 1 (Phase 0)
- **What:** Curated the initial intellectual foundation — the "textbooks," not slides. ~30 deep, cross-linked notes: **12 decision-science mental models** (expected value, base rates/Bayesian, first-principles, second-order, systems, inversion, scenario planning, margin-of-safety, calibration, cognitive biases, decision-quality-vs-outcome), **8 frameworks** (JTBD, RICE/ICE, OKRs/North-Star, Porter's Five Forces, Lean Startup, unit economics, positioning, hypotheses/experiments, source evaluation), **product/growth mechanics** (network effects, growth loops, marketplace cold-start, MVP), and **Acredemia's constitution** (User-Personas, Competitors, Marketplace-Dynamics, Long-Term-Vision).
- **Ecosystem:** 6 domain MOCs + [[Learning-Paths]] (4 guided sequences) + [[Knowledge-Expansion-Roadmap]] + [[Research-Backlog]]; new templates (mental-model, framework, company, learning-path); taxonomy + config half-lives updated for the new reference types.
- **Curation discipline (deliberate):** prioritized conceptual foundations over new company histories with unverifiable metrics — histories go in Gen-2 with sources. Every note answers "why does this help us think better?"; nothing is filler.
- **The graph emerged:** the vault grew 63→104 notes and the knowledge graph from 48/152 to **85 nodes / 448 edges** — the reference library densely cross-links into the existing case studies, theories, and questions. Governance clean (1 low finding), 43 tests green.

## 2026-07-10 — 🧭 Research OS visual identity (UI rebuilt from the design system)
- **What:** Replaced the generic 2-column dashboard with an actual **Research Operating System shell** — app title bar (red mark, mono `RESEARCH-OS · V1.0`, live `[SYSTEM ACTIVE]`, `⌘K`), a mono **left rail** with bracketed workspace indices (`[00] BRIEF … [04] SIGNALS`), editorial huge display titles per workspace, and **engineered panels** (`.panel` primitive with accent corner-ticks + mono `[ SECTION ]` headers).
- **Make thinking visible:** the KNOWLEDGE-MAP renders the vault as a live **force-directed relationship graph** (nodes colored/sized by type + degree, hover highlights neighbors, click → inspector with links/backlinks). New `/graph/data` endpoint + `graph.data()`.
- **Command surface:** `⌘K`/`Ctrl-K` palette (global search + jump-to-workspace), keyboard-first (`0–4` switch views, `Esc`).
- **Every screen composed from primitives** (design system extended: domain-semantic accents, `.panel`/`.tagm`/`.cross`/`.display`); no one-off UI, no raw values in-screen. Passes the logo-removed identity test.
- **Verified in-browser:** SYSTEM ACTIVE, brief tiles, confidence ledger, graph 48 nodes/152 edges with hover highlighting, command palette, decision engine — all functional, no console errors. 43 tests green.

## 2026-07-09 — 🎨🖥 Design system + Desktop-first architecture ([[ADR-004-desktop-architecture]])
- **Design system ("Command Surface"):** `docs/DESIGN-SYSTEM.md` (color/type/spacing/motion tokens, component primitives, interaction + a11y rules, iconography, grids, workspace philosophy) + `ui/tokens.css` (canonical tokens + primitives, offline-first). Dashboard now consumes the system (no raw values in-screen). Charcoal base · red primary · neon-green/neon-red signal colors.
- **Desktop-first architecture:** added a **lifecycle kernel** (`app/lifecycle.py` — ordered boot, per-step logging, health checks, graceful shutdown) and a **path authority** (`app/paths.py` — application vs user-data separation, portable/installed modes, env overrides, no hardcoded paths). `config.py` sources locations from paths; `desktop/atlas.py` boots via the kernel and shuts down gracefully; structured logging to `logs/`.
- **Deliberate non-change:** did **not** fragment the 13 frozen engine modules into a 14-folder tree — layers are a dependency rule + mental model, not a directory explosion (would violate I10 / "no unnecessary abstraction"). Rationale in [[ADR-004-desktop-architecture]].
- **New invariants I17–I21:** app/user-data separation, single path authority, deterministic recoverable lifecycle, framework-agnostic desktop shell, layered dependency direction.
- **Verified:** 43 tests green; kernel boots READY in ~3s with health all-green; graceful shutdown confirmed. `cache/logs/config` git-ignored (user data).

## 2026-07-09 — 🖥 Local-First pivot + repository migration ([[ADR-003-local-first-single-user]])
- **What:** Deliberate product-level decision — Atlas is a **Local-First, single-user** Strategic OS, not a SaaS. Removed all cloud/SaaS assumptions from v1 (landing page archived; no waitlist/signups/auth/hosting). Added 6 invariants (I11–I16: Local-First, Offline-First, User-Ownership, Zero-Lock-in, Deterministic-Core/Optional-AI, Desktop-packaging-friendly). Cloud/multi-user pushed to Phase 5 "possible future."
- **Repository migration:** `backend/ → app/`, `frontend/ → ui/`, `Acredemia-Vault/ → vault/`, `landing/ → archive/marketing/landing-page/` (kept, marked future-only). New root `README.md` + `docs/` (DEVELOPMENT, ARCHITECTURE). Config vault path → `vault/`; env var `ACREDEMIA_VAULT → ATLAS_VAULT`; launch/gitignore updated; landing removed from dev workflow.
- **Kept the engines as one flat package** (did not split into engines/parser/governance/… top-level packages) — that would break the frozen clean-DAG simplicity (I10) for zero single-user benefit. Rationale in [[ADR-003-local-first-single-user]].
- **Verified:** 37 tests green from `app/`; vault resolves at `vault/`; all engines functional after the move.
- **Why:** Atlas is the software I open every morning to run Acredemia — optimize for daily solo work, never for deployment.

## 2026-07-09 — 🧊 Atlas 1.0 Architecture Freeze (RC-1 audit)
- **What:** Full RC-1 release audit → [[ADR-002-atlas-1.0-architecture-freeze]], the permanent foundational document (module responsibilities, clean-DAG dependency map, entity model, knowledge-flow verification, technical-debt ranking, release checklist, 10 architectural invariants, and the four philosophies). Architecture formally frozen at 1.0.
- **Consistency fixes bound during the freeze (not new features):** made the per-note `half-life-days` field live (`governance._half_life` honors it); implemented the documented-but-missing `broken-strategic-link` check (decision citing a contested theory) and reclassified "ADR inconsistencies" as manual review; split the tag taxonomy into Active vs Reserved types; declared the SQLite cache deferred (YAGNI) and marked `config.CACHE_DB` reserved; added `.gitattributes` to stop CRLF churn. Tests: 35→37, all green.
- **Verdict:** Atlas 1.0 is internally complete and release-ready; no critical blockers. Important items (API-layer tests, CI, founder-authored DNA) gate *external* release only.
- **Why:** Shift from building to preserving — optimize Atlas to survive ten years of evolution without losing coherence.
- **Follow-ups:** [ ] D1 API-layer tests · [ ] D2 CI (GitHub Actions) · [ ] founder fills Strategic-DNA.

## 2026-07-09 — Test suite (durability)
- **What:** 35 pytest tests in `backend/tests/` covering every deterministic engine — parser (frontmatter/wikilinks/ledger/template-forcing), Decision Engine (WSM ranking, cost inversion, DNA demotion, sensitivity), Epistemics (the confidence-derivation rules incl. "no promotion without a survived contradiction search", decay cap, drift), Governance (weak-pattern, broken-link, untriaged-signal, clean-note), Market Intel (RSS+Atom parsing, relevance routing), Synthesis (clustering separation, ≥2-case rule), Graph (pathfinding), and safe vault writes — plus smoke tests on the real vault. All green in ~3s, no network.
- **Why:** This system is meant to be maintained for years by one person; tests lock in the behavior of the reasoning engines so refactors can't silently break the epistemics/decision logic the whole product's credibility rests on.
- **Tradeoffs:** tests build their own fixture vaults (independent of real content) so they stay stable as the vault grows; a few smoke tests assert on the real vault for gross-regression coverage.
- **Impacted modules:** all deterministic engines now have a safety net.
- **Follow-ups:** [ ] CI (GitHub Actions) to run pytest on push — a natural Phase-4 addition.

## 2026-07-09 — Understanding / Synthesis engine (Module 5→9)
- **What:** `backend/synthesis.py` — clusters case studies (agglomerative, cosine, move+tag-weighted with generic-growth-word stopwording to avoid spurious "*-driven-growth" links) and drafts **candidate patterns** ("across these cases, X recurs"), deduped against existing patterns (NEW vs covered). Optional local-Ollama prose, deterministic fallback. Human promotes a candidate → draft pattern note (`status: candidate`); never auto-promoted. Endpoints `/synthesize`, `/synthesize/promote`; `cli.py synthesize`; dashboard **Synthesis panel** with promote buttons.
- **Loop demonstrated end to end:** added a real 2nd marketplace case ([[Groupon-discount-growth]]); synthesis surfaced a **NEW {Groupon, Homejoy}** candidate; accepted it by strengthening [[P-marketplace-leakage-kills-unit-economics]] to 2 cases → the Governance Bot's weak-pattern finding cleared → re-synthesis now marks the cluster **covered** (dedup working). Synthesis proposed → human accepted → governance cleared.
- **Why:** This is the "synthesis, not storage" capability — the system now drafts *understanding* from accumulated cases, the highest-leverage part of the Understanding Layer.
- **Tradeoffs:** at tiny N text clustering is coarse and can propose spurious clusters (documented) — which is exactly why candidates are human-reviewed, never auto-promoted.
- **Impacted modules:** Understanding(5→9); consumes case studies, dedups vs Patterns(4-adjacent).
- **Follow-ups:** [ ] run a contradiction search on the strengthened marketplace pattern before promoting it to a theory · [ ] richer clustering once the case library grows (embeddings).

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
