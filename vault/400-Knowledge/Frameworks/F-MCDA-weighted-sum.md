---
type: framework
id: F-MCDA-weighted-sum
title: "MCDA — Weighted Sum Model"
freshness: fresh
last-reviewed: 2026-07-09
scale: knowledge
tags: [domain/product, decision-science]
created: 2026-07-09
---

# 🧰 MCDA — Weighted Sum Model (WSM)

## What it is
`score = Σ(normalized_valueᵢ × weightᵢ)`, with cost/risk/time dimensions inverted before weighting.

## When to use
Comparing ≥2 alternatives across multiple weighted dimensions when you want a **fully transparent** ranking (the arithmetic is inspectable row by row).

## Honest limitations
- Garbage-in-garbage-out on subjective 1–10 inputs; the *number can be reverse-engineered* by nudging weights.
- Therefore the **reasoning trace matters more than the score** (see [[TPL-decision]]).
- Always pair with a sensitivity check: if a ±20% perturbation flips the ranking, the decision is *fragile*.

## Alternatives (deferred)
- **AHP** — derives weights from pairwise comparisons; more rigorous, higher friction.
- **TOPSIS** — distance-from-ideal; robust to scale but harder to explain.

Used by: the Decision Engine (Module 6).
