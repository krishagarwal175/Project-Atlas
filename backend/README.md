# Acredemia Research OS — Backend (Phase 1)

The compute layer over the [Obsidian vault](../Acredemia-Vault). The **vault is the source of truth** (see `ADR-001`); this backend is a rebuildable layer that reads markdown and writes only to the market-signal inbox and the governance audit note.

**Zero paid APIs. No cloud LLM.** Core runs on stdlib + PyYAML; search uses local scikit-learn TF-IDF today and upgrades to local embeddings if you install them.

## Install
```bash
pip install -r requirements.txt          # core: fastapi, uvicorn, pyyaml
# optional upgrades (local, free):
pip install scikit-learn numpy           # already used for TF-IDF search
pip install sentence-transformers        # → semantic embedding search
```

## CLI (works offline except `ingest`)
```bash
python cli.py parse                  # parse & summarize the vault
python cli.py search "referral program virality"
python cli.py audit --write          # run Governance Bot, write audit note to vault
python cli.py ingest                 # pull free RSS market signals into the vault
python cli.py stats                  # vault health snapshot
python cli.py serve                  # start API on :8000 (docs at /docs)
```

## Modules (map to the architecture spec)
| file | module | what |
|------|--------|------|
| `vault.py` | substrate parser | markdown + YAML + wikilinks + Evidence Ledger → `Note` objects |
| `search.py` | Retrieval (3) | TF-IDF / embeddings / keyword, confidence+freshness aware |
| `governance.py` | Governance Bot (8) | deterministic health audit → `900-Meta/Reviews/` |
| `market_intel.py` | Market Intel (1) | stdlib RSS ingest → relevance-routed signal notes |
| `api.py` | REST surface | FastAPI; `/search /audit /ingest /notes /note/{id} /health` |
| `config.py` | — | vault path, RSS feeds, half-lives, confidence ladder |

## Design guarantees
- **Vault authoritative, cache disposable.** Delete anything here; re-run to rebuild. Nothing important lives only in code.
- **Determinism where credibility lives.** Governance, relevance routing, and confidence checks are deterministic and explainable. No opaque model decides anything that matters.
- **Graceful degradation.** A dead RSS feed is skipped and logged; the rest works. Missing optional libs fall back a tier.
- **Signals never auto-score.** Market intel can *link* to a decision as context; it never modifies a weighted total.

## Not yet built (Phase 2–3)
Decision Engine (WSM + DNA guardrail), NetworkX graph analytics, the Confidence/Contradiction engine computing states from ledgers, decay recomputation, optional Ollama theory-drafting. The vault already models all of these by hand; these services will read the same files.
