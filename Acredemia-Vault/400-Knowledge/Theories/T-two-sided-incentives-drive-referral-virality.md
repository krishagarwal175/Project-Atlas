---
type: theory
id: T-two-sided-incentives-drive-referral-virality
title: "Two-sided referrals drive virality when the referred user has standalone utility"
status: contested
confidence-state: emerging
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
**Emerging, ⚑ contested** — 2 supporting cases ([[Dropbox-referral]], [[PayPal-referral]]), but the only contradiction search so far ([[CON-cash-referrals-that-worked]]) *broke* the original claim; **no search has yet survived the *revised* claim.** Per the strict rule in [[Vault-Governance]], a claim cannot exceed `emerging` without a survived contradiction search — so despite strong supporting weight this stays `emerging` until the follow-up search runs. (The epistemics engine flagged an earlier hand-authored `supported` as an overclaim and it was corrected — the system correcting its author.)

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
- 2026-07-09 — contradiction search refuted "product-native" requirement; claim reframed around **referred-user standalone utility**; briefly hand-set to Supported.
- 2026-07-09 — **epistemics engine flagged the Supported label as drift** (no *survived* contradiction search on the revised claim); corrected back to Emerging/⚑contested pending a fresh search. Follow-up: run a contradiction search on the revised "two-sided + standalone-utility" claim.
