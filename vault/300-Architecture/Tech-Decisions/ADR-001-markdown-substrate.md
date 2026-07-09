---
type: adr
id: ADR-001
title: "Markdown vault is the source of truth; DB is a rebuildable cache"
status: accepted
date: 2026-07-09
supersedes: ""
tags: [architecture]
---

# 🏛 ADR-001: Markdown vault as source of truth

## Context
The product's primary asset is *knowledge that compounds*. Longevity, portability, linkability, and low daily-capture friction dominate all other concerns. A bespoke web-app + SQLite store is inferior on every one of these axes to plain markdown files.

## Decision
The Obsidian markdown vault is the **authoritative source of truth**. All backend services read and write these files. SQLite + embedding index is a **disposable cache**, regenerated from the vault; deleting it loses nothing.

## Alternatives considered
- **SQLite/Postgres as source of truth (previous plan)** — rejected: schema lock-in, not greppable/portable, dies with the app, worse knowledge store than files.
- **Neo4j graph DB** — rejected at this scale: wikilinks already are the graph; adds ops burden. Revisit at Phase 4.
- **Notion / SaaS PKM** — rejected: lock-in, not offline, not automatable without paid API.

## Tradeoffs
- (+) Zero lock-in, works by hand offline, trivially versioned via git, enterprise-friendly ("you own your files").
- (−) Services must parse markdown/YAML (cheap); concurrent multi-writer editing is weaker than a DB (irrelevant at single-user scale).

## Impacted modules
All — this defines [[System-Architecture]].

## Future implications
Multi-tenant Phase 4 = one vault per org; migration between phases is additive (new note types/fields), never a rewrite.

## Follow-ups
- [ ] Build the vault parser in Phase 1.
