---
type: framework
id: F-rice-ice
title: "RICE & ICE Prioritization"
domain: product
confidence-state: institutional
freshness: fresh
last-reviewed: 2026-07-10
tags: [domain/product, domain/decision-science]
created: 2026-07-10
---

# 🧰 RICE & ICE Prioritization

> Cheap, transparent scores for ranking a backlog. **RICE** = (Reach × Impact × Confidence) ÷ Effort. **ICE** = Impact × Confidence × Ease. Same idea, different friction.

## What it is
A way to compare many candidate initiatives on one scale so gut-feel roadmaps become debatable. RICE adds *Reach* (how many, per period) and divides by *Effort* to reward leverage; ICE is the faster, coarser version for quick calls.

## When to use it
Roadmap and backlog prioritization; a lightweight alternative to full [[F-MCDA-weighted-sum|MCDA]] when the decision is "which of these many things next." Atlas uses RICE for its *own* roadmap.

## How to run it
Score each item; rank by the composite. The number is a conversation-starter, not an oracle — the *ranking* and the *disagreements it surfaces* are the value.

## Why it works
Forces the two things intuition hides: **effort** (leverage) and **confidence** (how much you actually know). Confidence as an explicit factor is a built-in humility check.

## Limitations / when NOT to use it
- **False precision.** Inputs are estimates; a 2.3 vs 2.1 gap is noise. Use it to sort into tiers, not to rank to the decimal.
- Doesn't handle strategic alignment or irreversibility — for high-stakes bets use [[F-MCDA-weighted-sum]] + [[MM-margin-of-safety]].
- Reach/Impact double-count if defined sloppily.

## Applies to Acredemia
Use ICE for weekly "what next" calls; reserve the full Decision Engine for strategic bets. Confidence should reflect real evidence in the vault, not optimism ([[MM-calibration]]).

## Related
- [[F-MCDA-weighted-sum]] · [[F-okrs-north-star]] · [[MM-expected-value]]
