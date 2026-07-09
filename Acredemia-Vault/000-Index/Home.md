---
type: moc
title: Home
updated: 2026-07-09
---

# 🏠 Acredemia Research OS — Home

> The founder's second brain for Acredemia. Knowledge → Understanding → Tested Theories → High-quality Decisions → remembered forever.

## Start here every morning
1. **[[700-Market-Signals]]** — what changed in the world?
2. **[[🧭 Strategic-Questions-MOC]]** — what open questions is evidence accumulating around?
3. **[[Changelog]]** — what changed in the vault / the build?
4. **Latest audit** → `900-Meta/Reviews/` — what does the Governance Bot say needs attention?

## Maps of Content
- [[🗺 Master-Index]] — the full vault map
- [[🧭 Strategic-Questions-MOC]] — long-lived strategic questions
- [[📚 Knowledge-MOC]] — case studies, patterns, theories, frameworks
- [[🏢 Acredemia-MOC]] — company profile, Strategic DNA, experiments, decisions

## The core loop
`Question → Evidence → Understanding → Theory (survives contradiction) → Decision (quality-scored) → Experiment → Outcome → back into Evidence`

## 🧊 Architecture is frozen at 1.0
Read [[ADR-002-atlas-1.0-architecture-freeze]] before proposing any architectural change. Features are added only to solve problems found through real usage.

## What this vault is
The **source of truth**. Plain markdown you own. Every backend service reads and writes these files; nothing important lives only in a database. If every tool we build dies, this vault still works by hand.

## Conventions
- Every note declares a `type:` in frontmatter — see [[Tag-Taxonomy]].
- Claim-bearing notes carry `confidence-state`, `freshness`, `last-reviewed` — see [[Vault-Governance]].
- Ideas are **atomic** (one note per idea) and connected by `[[wikilinks]]`. No walls of text.
