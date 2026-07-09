# Atlas — Development (Local-First)

There is no deployment. There is no cloud. The whole workflow is:

```
clone → install → run → use Atlas → improve Atlas
```

## Prerequisites
- Python 3.10+
- (Optional) [Obsidian](https://obsidian.md) to browse/edit the `vault/` by hand
- (Optional) [Ollama](https://ollama.com) for local LLM narrative summaries — never required

## Setup
```bash
git clone https://github.com/krishagarwal175/Project-Atlas.git
cd Project-Atlas/app
pip install -r requirements.txt
```

## Run
```bash
# Windowed desktop app (boots via the lifecycle kernel, opens a native window):
python desktop/atlas.py

# —or, engine only—
cd app && python cli.py serve     # local API @ http://127.0.0.1:8000  (docs at /docs)
```
For engine-only mode, open `ui/index.html` or serve it: `cd ui && python -m http.server 5173`.
Boot diagnostics are logged to `logs/atlas-<date>.log`. Architecture: `docs/DESKTOP-ARCHITECTURE.md`.

## Everyday commands (all offline)
```bash
python cli.py stats          # vault health snapshot
python cli.py audit --write  # governance bot → writes an audit note into the vault
python cli.py search "..."   # semantic/keyword search over the vault
python cli.py decide         # decision engine demo
python cli.py synthesize     # cluster case studies into candidate patterns
python cli.py epistemics     # derived confidence states + drift
python cli.py graph          # knowledge-graph centrality
python cli.py ingest         # (needs internet) pull free RSS market signals
```

## Tests
```bash
cd app && python -m pytest    # 37 tests, ~3s, no network
```
The deterministic core is protected by tests. Add a test with every change to it.

## Configuration
Everything tunable lives in `app/config.py` (RSS feeds, dimension weights, half-lives,
confidence ladder). Override the vault location with the `ATLAS_VAULT` env var if needed.

## Where things live
- `app/` — engines + api + cli + tests (a flat, clean-DAG Python package; see ADR-002 §2)
- `ui/` — the local dashboard (single HTML file)
- `vault/` — the source of truth (markdown); works by hand in Obsidian even if `app/` is off

## Architecture
The authoritative architecture lives in the vault (single source, no duplication):
- Overview: `vault/300-Architecture/System-Architecture.md`
- Freeze + invariants: `ADR-002`; Local-First pivot: `ADR-003`; substrate: `ADR-001`
- Governance rules: `vault/900-Meta/Vault-Governance.md`

## Golden rule
When "easier to deploy" conflicts with "more useful for daily solo work," choose the latter.
