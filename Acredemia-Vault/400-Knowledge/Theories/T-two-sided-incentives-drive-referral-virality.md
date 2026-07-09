---
type: theory
id: T-two-sided-incentives-drive-referral-virality
title: "Two-sided referrals drive virality when the referred user has standalone utility"
status: contested
confidence-state: supported
contested: true
freshness: fresh
last-reviewed: 2026-07-09
scale: theory
derived-from: ["[[P-two-sided-incentive-loop]]", "[[Dropbox-referral]]", "[[PayPal-referral]]"]
tags: [domain/gtm]
created: 2026-07-09
---

# 🧠 Two-sided referrals drive virality when the referred user has standalone utility

> **Evolved 2026-07-09** after contradiction search [[CON-cash-referrals-that-worked]] refuted the original "product-native reward" requirement.

## The claim (revised)
A referral program produces self-sustaining viral growth when it is **two-sided** AND **the referred user has an immediate standalone reason to use the product.** Reward *type* (product-native vs cash) is a **boundary condition**, not the driver.

## Confidence derivation (explainable)
**Supported, ⚑ contested** — 2 supporting cases ([[Dropbox-referral]], [[PayPal-referral]]) and **one contradiction search survived by the revised core claim** (no counterexample to "two-sided + standalone utility" found). Not yet **Well-Tested**: only 2 cases and one search; the reframed claim needs a fresh contradiction attempt. `contested` flag retained because the split is recent and the original combined claim was broken.

## Evidence Ledger
| date | source | stance | weight | note |
|------|--------|--------|--------|------|
| 2026-07-09 | [[Dropbox-referral]] | supports | high | product-native, two-sided, standalone utility (storage) |
| 2026-07-09 | [[PayPal-referral]] | supports | high | cash, two-sided, standalone utility (payments) |
| 2026-07-09 | [[CON-cash-referrals-that-worked]] | contradicts (original) | high | refuted "product-native" requirement → drove the revision |

## Boundary conditions (when does this FAIL?)
- Referred user has **no standalone reason** to use the product → referral brings dead signups (the risk [[A-referral-currency-exists]] flags for Acredemia).
- Cash rewards require **funding to sustain the burn** ([[PayPal-referral]] caveat) — "cash works" ≠ "cash is affordable for us."

## Assumptions this rests on
- [[A-referral-currency-exists]] — now reframed: the real question is *standalone utility for the referred student*, not reward currency.

## Applicability to Acredemia
For a referred student, is there immediate standalone value (get verified, get seen by recruiters) *independent of who referred them*? If yes, the theory transfers. Checked against [[DNA-Non-Negotiables]]. Feeds [[Q-should-verification-stay-free]].

## Contradiction searches run
- [[CON-cash-referrals-that-worked]] — outcome: **broke the original**, revised claim survived. A fresh search on the revised claim is a follow-up.

## Evolution history
- 2026-07-09 — created as candidate (Emerging) from [[P-two-sided-incentive-loop]].
- 2026-07-09 — contradiction search refuted "product-native" requirement; claim reframed around **referred-user standalone utility**; promoted Emerging→Supported (survived a search) but flagged `contested` pending a fresh search on the new claim.
