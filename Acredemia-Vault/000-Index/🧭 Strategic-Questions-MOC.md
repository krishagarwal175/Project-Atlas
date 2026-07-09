---
type: moc
title: Strategic-Questions-MOC
updated: 2026-07-09
---

# 🧭 Strategic Questions

Questions are **first-class, long-lived objects**. They stay alive; evidence accumulates around them; experiments attach; decisions reference them; new evidence can reopen an answered one. This preserves strategic curiosity instead of only recording final answers.

## Open questions
```dataview
TABLE status, confidence-state, freshness, file.mtime AS "updated"
FROM "350-Questions"
WHERE type = "question" AND status = "open"
SORT file.mtime DESC
```

## Dormant / Answered / Reopened
```dataview
TABLE status, file.mtime AS "updated"
FROM "350-Questions"
WHERE type = "question" AND status != "open"
SORT status ASC
```

## Seeds
- [[Q-should-verification-stay-free]]
- [[Q-tier2-before-tier1]]
- [[Q-recruiters-first-or-students-first]]

> If a query block shows nothing, install the **Dataview** community plugin. Until then, link questions here by hand.
