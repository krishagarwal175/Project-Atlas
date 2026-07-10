---
type: mental-model
id: MM-network-effects
title: "Network Effects"
domain: product
confidence-state: institutional
freshness: fresh
last-reviewed: 2026-07-10
tags: [domain/product, domain/marketplace, domain/growth]
created: 2026-07-10
---

# 🧠 Network Effects

> A product gets *more valuable to each user as more users join*. This is the strongest, most durable moat in software — but it's a reinforcing loop that runs in reverse just as fast.

## The idea
Value scales with the network, not just the feature set. Types: **direct** (more users of the same side — messaging), **two-sided/marketplace** (more of the *other* side — buyers↔sellers, students↔recruiters), **data** (more usage → better product), **social/identity**. Because value compounds with size, an early lead can become unassailable.

## When to reach for it
Marketplaces, platforms, communities — anything where users benefit from other users. Central to Acredemia's thesis.

## Why it works (and why it's fragile)
Reinforcing loop ([[MM-systems-thinking]]): growth → more value → more growth. But below **critical mass** the loop is too weak to self-sustain (the [[MM-marketplace-cold-start|cold-start problem]]), and above saturation it slows. The same loop can collapse if quality/trust erodes.

## Failure modes / where it misleads
- **Claiming network effects you don't have.** Many "network effect" pitches are just growth. Test: does user N+1 make the product better for user N?
- **Multi-tenanting / low switching costs** let a competitor peel off a side.
- **Leakage** drains two-sided effects ([[P-marketplace-leakage-kills-unit-economics]]).

## Applies to Acredemia
The moat: more verified students → more recruiter trust/demand → more reason to get verified. Design for **critical mass in a beachhead** (a few colleges) before breadth, and for **switching costs** (owned verified history) so the loop can't be peeled off. See [[Marketplace-Dynamics]].

## Related
- [[MM-marketplace-cold-start]] · [[MM-growth-loops]] · [[MM-systems-thinking]] · [[F-porters-five-forces]] · [[Marketplace-Dynamics]]
