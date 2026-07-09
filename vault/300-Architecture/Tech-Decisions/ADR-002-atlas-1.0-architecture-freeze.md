---
type: adr
id: ADR-002
title: "Atlas 1.0 — Architecture Freeze & RC-1 Release Audit"
status: accepted
date: 2026-07-09
supersedes: ""
tags: [architecture, freeze, release]
---

# 🧊 ADR-002 — Atlas 1.0 Architecture Freeze & RC-1 Release Audit

> **This is the permanent foundational document for Atlas.** Read it before proposing
> any architectural change. The architecture is frozen at 1.0; from here, features are
> added only to solve problems discovered through real usage. Optimize Atlas for
> surviving ten years of evolution without losing coherence — not for adding features.

Grounded in a real audit of the codebase (`backend/`, 13 modules, 37 tests) and the
vault (`Acredemia-Vault/`, ~60 notes) on 2026-07-09.

---

## 1. Release Candidate Audit — verdict

**Atlas 1.0 is internally complete and release-ready as an internal tool.** The full
knowledge loop runs end to end on real data; the deterministic core is tested; the
Governance Bot reports the vault healthy (0 high/medium findings; 1 low: one untriaged
signal). No **critical** blockers remain. Remaining items are Important/Optional (see §8).

---

## 2. Architecture Health Report

### 2.1 Dependency graph — clean DAG, no cycles (verified)
```
L0  config, vault                         ← roots (config = data; vault = substrate parser)
L1  search, epistemics, graph,            ← engines: depend only on L0
    decision_engine, synthesis,
    narrative, market_intel, vault_write
L2  governance                            ← composes L1 (lazily imports epistemics)
L3  api, cli                              ← surfaces: compose everything
UI  frontend/index.html                   ← depends on api (HTTP only)
```
Nothing imports `governance`, `api`, or `cli` except the layer above. No circular
dependencies. `narrative` and `search` are imported lazily where optional. **Healthy.**

### 2.2 Module responsibilities (single-responsibility, no overlap)
| Module | Single responsibility | Consumes | Produces | Extension point |
|--------|----------------------|----------|----------|-----------------|
| `config` | all tunables (feeds, half-lives, ladder, dimensions, weights) | — | constants | edit data, not code |
| `vault` | parse markdown → `Note` (frontmatter, wikilinks, Evidence Ledger) | files | `Note[]`, backlinks | new frontmatter fields |
| `search` | retrieval over the vault | vault | ranked hits | swap TF-IDF→embeddings |
| `epistemics` | derive confidence/contested/decay from ledgers | vault | assessments | new confidence rules |
| `graph` | NetworkX centrality/paths/clusters | vault | graph metrics | new graph queries |
| `decision_engine` | WSM + DNA guardrail + sensitivity → decision note | config, search, DNA | decision note | AHP/TOPSIS mode |
| `synthesis` | cluster case studies → candidate patterns | vault, narrative | candidates | embeddings clustering |
| `narrative` | optional local-LLM prose (never alters data) | vault | text | swap Ollama model |
| `market_intel` | ingest free RSS → relevance-routed signals | config, profile | signal notes | new sources |
| `vault_write` | safe human-initiated writes back to notes | config | file edits | new write actions |
| `governance` | deterministic health audit (Module 8) | vault, epistemics | audit note | new checks |
| `api` / `cli` | REST / terminal surfaces | all | responses | new endpoints |

No two modules own the same responsibility. The only cross-engine composition is
`governance → epistemics` (drift), which is intentional and one-directional.

### 2.3 Canonical module map (resolves naming from the design phase)
The redesign used several names for the same thing. **Canonical (frozen):**
- "Understanding Layer" / "Theory Engine" / "Synthesis engine" ⇒ **`synthesis` + the `theory`/`pattern` note types**.
- "Confidence Engine" / "Contradiction Engine" ⇒ **`epistemics`** (one module, both facets, over the Evidence Ledger).
- "Freshness / Decay service" ⇒ **`epistemics` + `governance`** (derivation + reporting).
- "Strategic DNA guardrail" ⇒ **`decision_engine.load_non_negotiables()` + the `dna` notes**.

---

## 3. Technical Debt Report (ranked)

| # | Item | Severity | Effort | Timeline |
|---|------|----------|--------|----------|
| D1 | No API-layer tests (endpoints, write paths: `write_signals`, `render_note`, `promote_candidate`, `narrative`, `graph.neighbors`) | Medium | Medium | before any external use |
| D2 | No CI (tests run manually) | Medium | Low | soon |
| D3 | Search is TF-IDF only; `sentence-transformers` optional/uninstalled | Low | Low | when corpus grows / recall complaints |
| D4 | Synthesis clustering coarse at tiny N (can propose spurious clusters) | Low | — | inherent; mitigated by human approval |
| D5 | Reserved empty folders + template-less reserved note types | Low | Low | add template on first real use |
| D6 | Filename/field casing: `HomeJoy-...md` vs `company: Homejoy` | Low | Low | leave (renaming breaks links); enforce convention going forward |
| D7 | `config.CACHE_DB` reserved but cache not built | Info | — | **deferred on purpose** (live parse is sub-second); build only if measured |

No **High** technical debt. None of the above blocks internal 1.0.

---

## 4. Consistency Report (findings + resolutions)

Resolved during this freeze:
- **Dead `half-life-days` field** → now honored by `governance._half_life` (per-note override, else `config` by type). Field is live. *(fixed + test)*
- **Documented-but-unimplemented governance checks** → `broken-strategic-link` (decision citing a contested theory) implemented; "ADR inconsistencies" reclassified as manual quarterly review. *(fixed + test)*
- **Tag taxonomy** → split into Active vs Reserved types; `placeholder` documented.
- **SQLite cache doc/impl gap** → declared deferred (YAGNI); `config.CACHE_DB` marked reserved.
- **CRLF churn** → `.gitattributes` normalizes line endings.

Standing (accepted): D4, D6 above. No duplicate objects, no duplicate workflows, no
contradictory modules found. The confidence ladder is defined once in `config` and
mirrored (consistently) in `Vault-Governance` and `Tag-Taxonomy`.

---

## 5. Entity Relationships (frozen object model)

**Pivot:** `question` (long-lived; open→dormant→answered→reopened).

```
DNA ──guards──▶ Decision ──answers──▶ Question ◀──attaches── Experiment ──▶ Outcome ──▶ Lesson ──▶ Knowledge
                    │(quality≠outcome)     ▲ evidence            │                                    │
                    ▼                       │                    ▼                              feeds Questions
Case-study ─▶ Pattern ─▶ Theory ◀──cites── Decision        Observation
   (synthesis drafts)      │  ▲
                    Evidence Ledger (supports/contradicts)
                           │  │
             Confidence ◀──┘  └──▶ Contradiction        Freshness/Decay labels all claim-bearing notes
             (derived ladder)         (active search)
```

Every object has: **lifecycle** (frontmatter `status`), **confidence** (derived for
claim-bearing types), **freshness** (half-life), **review workflow** (governance +
`*-review` notes), **versioning** (git + `last-reviewed`; theories keep an evolution
history). Reserved objects (`hypothesis`, `strategic-principle`, `competitor`,
`market-report`, `meeting-note`, `postmortem`) are defined but await first use — no
orphan concepts.

---

## 6. Information Architecture Audit

Folders `000–900` map to the scale spine; every folder has a reason (documented in
`🗺 Master-Index`). MOCs are entry points, not storage. Templates exist for all 14
**active** note types. Naming: ID prefixes are canonical — `Q- T- P- A- CON- DEC- EXP-
L- O- MS- ADR- DNA-`; case studies use `Company-move` (no prefix, by convention).
Frontmatter, tag taxonomy, and scale hierarchy are internally consistent (§4). **Healthy.**

---

## 7. Knowledge Flow — loop verified, no dead ends

`Question → (search / market-intel) Evidence → Evidence Ledger → epistemics
(Understanding/Confidence) → Theory (synthesis drafts, contradiction tests) → Decision
(engine, DNA-checked, quality-scored) → Experiment → Outcome (forced retrospective) →
Lesson → Knowledge → feeds future Questions.`

Every arrow is realized by a template link and/or an engine. The single **intentional**
human-only hop is Lesson→Knowledge→new Question (curation is a judgment act, not
automatable). Governance watches the whole loop for breaks. **Knowledge compounds.**

---

## 8. Version 1.0 Release Checklist

**Critical (block 1.0) — NONE outstanding.** ✅
- [x] Deterministic core tested (37 tests, green, no network)
- [x] Governance reports vault healthy (0 high/medium)
- [x] Knowledge loop closed end to end (demonstrated: theory evolved via contradiction; synthesis→accept→govern)
- [x] Vault-first, zero paid APIs, offline-capable core
- [x] Dependency DAG, no cycles

**Important (before external/multi-user use)**
- [ ] D1 API-layer tests · [ ] D2 CI (GitHub Actions running pytest)
- [ ] Founder fills Strategic-DNA with real convictions (drafts today)

**Optional**
- [ ] D3 install `sentence-transformers` · [ ] Ollama for richer narrative/synthesis prose

**Future (only if Atlas goes beyond internal use — not 1.0)**
- Multi-tenant, auth, React rebuild, hosted tier.

**Verdict: Atlas 1.0 ships internally now.** The Important items gate *external* release, not internal daily use.

---

## 9. Future Development Guidelines

1. **No feature without a real, observed problem.** Log the problem as a `question` or `observation` first; let evidence justify the build.
2. **New tunables go in `config`, not code.** Weights, feeds, half-lives, thresholds are data.
3. **New behavior must be deterministic and testable**, unless it lives strictly in the `narrative` (LLM) layer, which may never alter a score/confidence/ranking.
4. **Every new note type** needs: a taxonomy entry, a template, and (if claim-bearing) an Evidence Ledger + confidence/freshness fields.
5. **Every architectural change** gets an ADR that references this freeze and states which invariant (§10) it touches. If it violates an invariant, it does not ship.
6. **The vault stays the source of truth.** No feature may make a database authoritative over the markdown.
7. **Add a test with the change.** The deterministic core is protected forever.

---

## 10. Architecture Freeze Report — Atlas 1.0

### Core Principles
1. **Knowledge compounds or it's worthless** — no orphan notes; everything links.
2. **Provenance over prediction** — Atlas never forecasts; it shows what's known, from where, how strongly, and what would change our mind.
3. **Understanding, not storage** — case studies become patterns become tested theories.
4. **Friction is the enemy** — capture is near-zero-cost markdown; the machine organizes.

### Architectural Invariants (future development must NEVER violate)
- **I1 — Vault is the source of truth.** Any cache/DB is disposable and rebuildable.
- **I2 — Determinism where credibility lives.** Scoring, confidence, governance, routing are deterministic and explainable. LLMs live only in the `narrative` layer and never alter data.
- **I3 — No paid APIs, no cloud-LLM dependency in production.** Free/open-source/local only.
- **I4 — Confidence is derived, never hand-set as truth.** It comes from the Evidence Ledger; no claim exceeds `emerging` without a *survived* contradiction search.
- **I5 — Decision Quality ≠ Decision Outcome.** Never conflate them.
- **I6 — Strategic DNA is a hard guardrail.** A Non-Negotiable-violating option can never be silently ranked #1.
- **I7 — Signals inform, never auto-score.** Market intelligence may link to a decision; it may never modify a weighted total.
- **I8 — The Evidence Ledger is the one shared primitive** for Understanding, Contradiction, Confidence, and Decay. Do not fork it.
- **I9 — Governance is write-only-to-audit.** The bot surfaces rot; humans decide and edit.
- **I10 — Dependencies flow one way** (config/vault → engines → surfaces). No cycles.

### Design Philosophy
Fewer, deeper, genuinely-useful capabilities over many shallow ones. Every module earns
its place or is removed. Boring, inspectable, deterministic beats clever and opaque.

### Engineering Philosophy
Small pure functions; data-driven config; graceful degradation (a dead feed, a missing
model, a down backend never breaks the core); test the deterministic core; the vault
works by hand even if all code dies.

### Knowledge Philosophy
Theories get stronger by surviving contradiction, not by accumulating agreement.
Nothing is trusted forever (decay). Every belief is falsifiable and revisitable.

### Governance Philosophy
The organizational brain must be actively maintained: orphans, drift, staleness, and
unchallenged theories are surfaced continuously so knowledge stays healthy for years.

---

**Atlas Architecture is hereby frozen at Version 1.0.** Supersede this document only
with a new ADR that explicitly justifies touching an invariant above.

Links: [[System-Architecture]] · [[ADR-001-markdown-substrate]] · [[Vault-Governance]] · [[Home]]
