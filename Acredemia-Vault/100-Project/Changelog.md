---
type: governance
title: Changelog
updated: 2026-07-09
---

# Changelog

Newest first. Every meaningful build/design change gets an entry (template: [[TPL-changelog-entry]]). Architectural changes also get an ADR in `300-Architecture/Tech-Decisions/`.

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
