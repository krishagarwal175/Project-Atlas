---
type: adr
title: System-Architecture
updated: 2026-07-09
tags: [architecture]
---

# System Architecture (overview)

> Inverted stack: the **vault is the source of truth**; code is a rebuildable layer over it. See [[ADR-001-markdown-substrate]].

```
SUBSTRATE   → Obsidian vault (markdown + YAML + [[wikilinks]]), git-backed. Source of truth.
COMPUTE     → FastAPI services, headless, read/write markdown:
                • Ingestion & Market Intel (feedparser)      [Module 1]
                • Knowledge Extraction (spaCy, KeyBERT)      [Module 2]
                • Retrieval (sentence-transformers + FTS5)   [Module 3]
                • Graph Analytics (NetworkX over wikilinks)  [Module 4]
                • Synthesis / Theory drafting (Ollama, opt.) [Module 5→9]
                • Decision Engine (WSM + trace + DNA filter) [Module 6]
                • Experiment/Execution tracker                [Module 7]
                • Governance/Audit bot                        [Module 8]
                • Confidence & Contradiction (Evidence Ledger)[Module 10]
                • Freshness/Decay                             [Module 11]
                • Strategic DNA guardrail                     [Module 12]
HUMAN       → Obsidian (daily driver) + thin web dashboard (only for graph/matrix/timeline views)
CACHE       → SQLite + numpy embedding index. Disposable; regenerated from the vault.
```

## Load-bearing principles
1. **Vault authoritative, DB disposable.** No lock-in; knowledge outlives the code; works by hand when the backend is down.
2. **Determinism where credibility lives** (scoring, evidence links, confidence derivation); **local LLM only in the draft/narrative layer**, always labelled, always editable.
3. **Evidence Ledger is the shared primitive** powering Understanding, Contradiction, Confidence, and Decay.
4. **No paid APIs, no cloud LLM in production.** Ollama optional and local only.

## Why not a graph DB (Neo4j)?
At Acredemia scale the `[[wikilink]]` graph *is* the knowledge graph, maintained by the act of writing. Extract to NetworkX on demand for computation. Neo4j adds a server + query language + sync problem for a scale problem we don't have. Revisit only at Phase-4 enterprise scale.

Related: [[ADR-001-markdown-substrate]] · [[Roadmap]] · [[Vault-Governance]]
