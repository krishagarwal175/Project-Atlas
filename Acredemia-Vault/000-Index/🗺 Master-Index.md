---
type: moc
title: Master-Index
updated: 2026-07-09
---

# 🗺 Master Index

The full map of the vault. Folders are storage; **links are the graph**.

## 000-Index — entry points
- [[Home]] · [[🧭 Strategic-Questions-MOC]] · [[📚 Knowledge-MOC]] · [[🏢 Acredemia-MOC]]

## 100-Project — building this system
- [[Roadmap]] · [[Milestones]] · [[Backlog]] · [[Changelog]]

## 200-Product — spec of this system
- [[Vision]] · [[PRD]]

## 300-Architecture
- [[System-Architecture]] · Tech-Decisions (ADRs) → `300-Architecture/Tech-Decisions/`

## 350-Questions — first-class strategic questions
- Long-lived. `status: open | dormant | answered | reopened`. See [[🧭 Strategic-Questions-MOC]].

## 400-Knowledge — the compounding asset
- `Case-Studies/` · `Patterns/` · `Theories/` · `Contradictions/` · `Frameworks/`

## 500-Acredemia — the company's operating memory
- [[Company-Profile]] · `Strategic-DNA/` · `Experiments/` · `Postmortems/`

## 600-Decisions — Strategic Memory
- One note per decision. Quality scored at decision time; Outcome recorded at retrospective.

## 700-Market-Signals — ambient intelligence
- Ingest lands here, gets triaged out to Knowledge / Acredemia.

## 900-Meta
- [[Tag-Taxonomy]] · [[Vault-Governance]] · [[Glossary]] · `Templates/` · `Reviews/`

## Live queries (require Dataview plugin)
```dataview
TABLE type, confidence-state, freshness, status
FROM "350-Questions" OR "400-Knowledge" OR "600-Decisions"
WHERE type
SORT file.mtime DESC
LIMIT 30
```
