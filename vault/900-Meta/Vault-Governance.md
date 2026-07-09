---
type: governance
title: Vault-Governance
updated: 2026-07-09
---

# Vault Governance — how the organizational brain stays healthy

The vault dies without discipline. This document defines **when** the vault updates and **what** the Governance Bot audits. Governance is deterministic and write-only-to-audit — it surfaces rot; **you** decide.

## The Evidence Ledger (shared primitive)
Every claim-bearing note (theory, pattern, assumption, decision, market observation) carries a ledger table:

| date | source | stance | weight | note |
|------|--------|--------|--------|------|
| 2026-07-09 | [[Dropbox-referral]] | supports | high | 3900% signup growth |

`stance = supports | contradicts`. This one structure powers Understanding, Contradiction, Confidence, and Decay.

## Confidence model (explainable — no arbitrary %)
Confidence is a **derived state**, never a stored number. Ladder:

`Speculative → Emerging → Supported → Well-Tested → Institutional`

Two orthogonal flags: `⚑ contested` (unresolved contradicting evidence) · `⌛ decaying` (freshness lapsed).

Rules:
- Promotion needs **both** accumulating supporting weight **and** a documented contradiction search that failed to break it. You **cannot** reach `Well-Tested` on confirming evidence alone.
- A **survived** contradiction search *raises* confidence (it got stronger by not dying).
- A **successful** counterexample *drops* the state and sets `⚑ contested`.
- Decay caps the effective state until re-reviewed.
- Every note renders a one-line derivation, e.g. *"Well-Tested: 5 supporting, 2 contradiction searches survived, last challenged 2026-05."*

## Freshness / Decay
Each note type has a half-life. Freshness state ∈ `Fresh | Aging | Needs-Review | Stale | Historical-Only`. Computed from `last-reviewed` + type half-life + arrival of contradicting evidence. **Nothing is ever deleted — only labelled.**

| type | half-life (guide) |
|------|-------------------|
| market-signal / market-report | ~90 days |
| competitor profile | ~180 days |
| case-study | ~2 years |
| framework | years |
| theory | re-review on new contradicting evidence |
| lesson | near-permanent |

## Decision Quality vs Outcome (never conflate)
- **Quality** is scored at decision time on a fixed rubric (evidence sufficiency, reasoning clarity, alternatives explored, assumptions explicit, risk awareness, experiment quality). Independent of what happens.
- **Outcome** is recorded at retrospective. A good decision can have a bad outcome and vice-versa.

## When the vault updates
**Trigger A — every meaningful build/design change:** append to [[Changelog]]; if architectural, add an ADR in `300-Architecture/Tech-Decisions/`. Template: [[TPL-changelog-entry]].
**Trigger B — every strategic decision/experiment/lesson:** create a permanent note. A decision cannot be marked `concluded` until its retrospective (What happened / What surprised us / linked [[Lesson]]) is filled. The lesson links back into `400-Knowledge/Lessons/`.
**Trigger C — theory strengthened:** the system opens a [[TPL-contradiction|Contradiction]] task. No theory rises without a documented contradiction search.

## Governance Bot audit checklist (writes to `900-Meta/Reviews/Audit-YYYY-MM-DD.md`)
- Orphan notes (no links in/out)
- Decisions stuck in `proposed` > 30 days
- Concluded experiments missing a retrospective
- Theories that rose in support with **no** logged contradiction search
- Patterns with < 2 supporting case studies
- **Stale knowledge** (freshness = Needs-Review / Stale)
- **Confidence drift** (stated `confidence-state` ≠ recomputed ledger state)
- Unanswered strategic questions open > 30 days with no evidence/experiment
- Orphaned observations (no link to a Question or Theory)
- Expired assumptions (assumption freshness lapsed)
- Broken strategic links (a Decision citing a now-`⚑ contested` Theory) — **automated** (`broken-strategic-link`)
- Missing retrospectives · broken wikilinks · untagged notes
- ADR inconsistencies — **manual review** (not auto-detectable deterministically; check during quarterly review)

## Freshness half-life source of truth
`config.HALF_LIFE_DAYS` (by note type) is canonical. A per-note `half-life-days`
frontmatter value **overrides** the type default for that note (honored by the bot).

Until the bot exists, run this checklist by hand weekly and file the note under `Reviews/`.
