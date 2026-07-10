---
type: moc
title: Knowledge-MOC
updated: 2026-07-09
---

# 📚 Knowledge

The compounding asset. Flows upward: **Case Studies → Patterns → Theories**, with **Contradictions** attacking theories to make them stronger. The **reference library** (curated textbooks) sits alongside, feeding better decisions.

## 🧭 Domain maps (primary navigation)
- [[Decision-Science-MOC]] — the reasoning toolkit (mental models)
- [[Frameworks-MOC]] — structured business methods
- [[Product-Growth-MOC]] — how value is built and spreads
- [[Finance-MOC]] — the numbers that decide build vs. burn
- [[Research-Methods-MOC]] — how Atlas knows things
- [[Startup-History-MOC]] — curated company histories
- [[Learning-Paths]] 🎓 — guided reading sequences
- [[Knowledge-Expansion-Roadmap]] · [[Research-Backlog]] — what to add next (curated, not encyclopedic)

## Theories (explanatory, falsifiable, confidence-tracked)
```dataview
TABLE confidence-state, contested, freshness, last-reviewed
FROM "400-Knowledge/Theories"
WHERE type = "theory"
SORT confidence-state DESC
```

## Patterns (descriptive: what recurs across cases)
```dataview
TABLE derived-from, confidence-state
FROM "400-Knowledge/Patterns"
WHERE type = "pattern"
```

## Case Studies (atomic: one company-move each)
```dataview
TABLE company, move, outcome
FROM "400-Knowledge/Case-Studies"
WHERE type = "case-study"
SORT company ASC
```

## Frameworks
- Reusable thinking tools (RICE, JTBD, Five Forces, MCDA…) → `400-Knowledge/Frameworks/`

## Contradictions (active anti-confirmation-bias)
- Every strengthened theory triggers a counterexample search → `400-Knowledge/Contradictions/`

## Seeds
- Case study: [[Dropbox-referral]]
- Theory: [[T-two-sided-incentives-drive-referral-virality]]
- Framework: [[F-MCDA-weighted-sum]]
