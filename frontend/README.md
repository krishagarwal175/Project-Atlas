# Acredemia Research OS — Dashboard

A single self-contained `index.html` — **no build step, no npm, no dependencies**. It's the daily operating environment ("morning brief") over the [backend](../backend) API: market signals to triage, confidence drifts, audit issues, search, the confidence board, the knowledge graph, and the decision engine.

## Run
```bash
# 1. start the API (from backend/)
cd ../backend && python cli.py serve       # http://127.0.0.1:8000

# 2. open the dashboard — either way works:
#    a) just open frontend/index.html in a browser, or
#    b) serve it:
cd ../frontend && python -m http.server 5173
#    then visit http://127.0.0.1:5173
```
If the API runs on a different host/port, edit the **API** box in the header.

## What it shows
- **Morning brief** — notes, confidence drifts, untriaged signals, audit issues by severity.
- **Ask the vault** — semantic/keyword search, each hit tagged with confidence + freshness.
- **Confidence board** — derived confidence states per claim (⚑ contested, ⌛ decaying, drift alerts).
- **Market signals** — the untriaged inbox.
- **Knowledge graph** — most-central ideas + a path finder between any two notes.
- **Decision engine** — edit alternatives/scores, pick a weight preset, get the ranked table with the DNA guardrail and fragility flag. (Use the API `/decide` with `write_note=true` to persist a decision note.)

Why a single HTML file instead of a React app: at single-user scale this is instantly usable, has zero recurring cost, and needs no toolchain — consistent with the whole project's constraints. A React/TS/Tailwind rebuild is a Phase-4 concern if/when this becomes multi-tenant.
