---
type: moc
title: Acredemia-MOC
updated: 2026-07-09
---

# 🏢 Acredemia

The company's own operating memory — internal, not external knowledge.

## Strategic DNA (the guardrail every recommendation is checked against)
- [[DNA-Mission]] · [[DNA-Values]] · [[DNA-Non-Negotiables]] · [[DNA-Decision-Principles]] · [[DNA-Founder-Beliefs]]

> The system must never recommend a strategy that violates a Non-Negotiable simply because it maximizes growth.

## Company
- [[Company-Profile]]

## Multi-scale spine
`Vision → Mission → Strategic-Theme → Objective → Question → Decision → Experiment → Project → Task → Observation → Lesson → Knowledge`
- [[DNA-Mission]] anchors the top; [[🧭 Strategic-Questions-MOC]] is the pivot.

## Decisions (Strategic Memory)
```dataview
TABLE status, decision-quality, outcome, date
FROM "600-Decisions"
WHERE type = "decision"
SORT date DESC
```

## Experiments
```dataview
TABLE status, question, concluded
FROM "500-Acredemia/Experiments"
WHERE type = "experiment"
SORT status ASC
```

## Postmortems
- `500-Acredemia/Postmortems/`
