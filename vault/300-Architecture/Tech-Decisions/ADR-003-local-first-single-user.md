---
type: adr
id: ADR-003
title: "Atlas is a Local-First, single-user Strategic Operating System"
status: accepted
date: 2026-07-09
supersedes: ""
amends: "[[ADR-002-atlas-1.0-architecture-freeze]]"
tags: [architecture, local-first, freeze]
---

# 🖥 ADR-003 — Local-First, Single-User Strategic OS

> Amends the freeze ([[ADR-002-atlas-1.0-architecture-freeze]]). This is a deliberate
> product-level decision, not an implementation detail. It **tightens** the frozen
> invariants rather than breaking them.

## Context
Atlas was briefly framed with SaaS/cloud optionality (multi-tenant Phase 4, a marketing
landing page, a hosted waitlist). That framing is wrong for what Atlas actually is: the
**personal Strategic Operating System that runs Acredemia**, used by exactly **one user**.
It should feel like VS Code / Obsidian / Linear / Raycast — desktop-first software you
own, open every morning, and trust with your organizational intelligence.

## Decision
Atlas 1.0 is **Local-First and single-user.** All SaaS assumptions are removed from v1:
no landing page in the product, no waitlist/signups, no auth, no accounts, no multi-tenant,
no billing, no hosted database, no cloud deployment (Vercel/Render/Railway/Supabase).
Cloud/multi-user is pushed to **Phase 5 "possible future,"** explicitly out of scope for v1.

Optimize every decision for one thing: **making Atlas more useful for daily solo work.**
When "easier to deploy" conflicts with "more useful for my daily work," choose the latter.

## New architectural principles (added to the freeze as invariants)
- **I11 — Local-First.** Atlas never *requires* cloud infrastructure. It runs on your machine.
- **I12 — Offline-First.** Everything works without internet *except* external knowledge
  acquisition (Market Intel / news / external datasets), which only *enhances* and must
  degrade gracefully. A dropped connection never breaks the core.
- **I13 — User Ownership.** Every byte is yours: portable, human-readable markdown, version-controllable. No proprietary formats.
- **I14 — Zero Vendor Lock-in.** No proprietary services, no paid APIs, no hosted storage, no mandatory accounts.
- **I15 — Deterministic Core, Optional AI.** The deterministic engines are the foundation; any LLM (local Ollama only) is optional, never mandatory (reaffirms I2).
- **I16 — Desktop-packaging-friendly.** Avoid choices that would block a future Electron/Tauri wrapper (no server-only assumptions, no absolute cloud URLs, localhost-bound API, static UI). Do **not** build Electron/Tauri now.

These join I1–I10 from ADR-002. All prior invariants still hold; I1 (vault is source of
truth), I3 (no paid APIs / no cloud-LLM), and I9 are reinforced.

## Repository restructuring (this ADR)
```
Atlas/
├── app/        # the application: engines, parser, governance, decision, api, cli, tests
├── ui/         # the local dashboard (static, no build step)
├── vault/      # the knowledge substrate — the permanent, human-readable database
├── docs/       # local-first dev + architecture pointers
├── archive/
│   └── marketing/landing-page/   # the old landing page — FUTURE public release only, not part of v1
└── README.md   # "this is software"
```
`backend/ → app/`, `frontend/ → ui/`, `Acredemia-Vault/ → vault/`, `landing/ → archive/marketing/landing-page/`.

### Why the Python engines stay one flat package (not split into engines/parser/governance/…)
The example tree suggested separate top-level packages per engine. **Rejected**, deliberately:
the modules form a clean, tested, frozen DAG (invariant I10) with flat imports (`import
governance`, `import epistemics`). Fragmenting them into nested packages would add import
ceremony and break the freeze's simplicity for zero benefit to a single-user tool — which
would violate the "usefulness over ease, no unnecessary abstraction" ethos. The engines
live together in `app/`, cleanly separated by file, exactly as audited in ADR-002.

## Deployment model (the defining characteristic)
`clone → install deps → one command → Atlas opens → everything works.` No cloud setup,
no accounts, no hosting, no external services. See `docs/DEVELOPMENT.md`.

## Consequences
- The marketing landing page is archived (not deleted) under `archive/marketing/` and
  removed from the dev workflow.
- Docs (README, Roadmap, Vision, PRD, System-Architecture) reframed from "hosted SaaS" to
  "Local-First Research OS."
- The freeze's "Important (before external release)" items (API tests, CI) become
  *durability nice-to-haves*, not release gates — there is no external release in v1.
- Cloud/multi-user remains *architecturally possible* (the vault-per-org model in ADR-002
  §38) but is **Phase 5**, ignored by v1.

Links: [[ADR-002-atlas-1.0-architecture-freeze]] · [[ADR-001-markdown-substrate]] · [[System-Architecture]] · [[Roadmap]]
