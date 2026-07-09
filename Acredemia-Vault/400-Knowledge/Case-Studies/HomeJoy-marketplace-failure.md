---
type: case-study
company: Homejoy
move: marketplace-scaling
outcome: failure
scale: knowledge
patterns: ["[[P-marketplace-leakage-kills-unit-economics]]"]
tags: [domain/marketplace, domain/gtm]
confidence-state: supported
freshness: fresh
last-reviewed: 2026-07-09
source-urls: []
created: 2026-07-09
---

# 📄 Homejoy — Marketplace Collapse (failure)

## Problem
On-demand home-cleaning marketplace matching customers with cleaners.

## Strategy
Grow aggressively via deep discounts to acquire customers and scale supply fast across many cities.

## Execution
Heavy promo-driven acquisition; rapid multi-city expansion before retention/unit-economics were proven.

## Outcome (metrics)
Shut down in 2015. Post-mortems cited: customers acquired via discounts didn't retain; **platform leakage** (customers and cleaners took the relationship off-platform after the first match); worker-classification legal costs; expansion outran fundamentals.

## Why it failed
- Discount-acquired demand had **no loyalty** once discounts stopped.
- **Leakage**: once a customer trusts a specific cleaner, the marketplace's ongoing value evaporates — repeat transactions bypass the platform.
- Scaled *before* proving the core loop retained.

## Transferability to Acredemia
Critical cautionary case. Boundary conditions this exposes:
- Discount-driven growth ≠ retained growth (challenges naive incentive theories).
- **Leakage risk**: does Acredemia have ongoing value after the first student↔recruiter match, or do they connect off-platform? This is an existential design question for [[Q-recruiters-first-or-students-first]].
Feeds [[P-marketplace-leakage-kills-unit-economics]] and is a *contradiction source* for any "just subsidize growth" theory.
