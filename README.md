# Atlas — a Local-First Desktop Research Operating System

Atlas is the personal strategic OS that runs **Acredemia**. It's software you own and open
every morning — like VS Code, Obsidian, or Linear — to turn intuition into structured,
evidence-backed decisions and to keep your organizational intelligence compounding. It runs
as a single desktop window over a local engine (boots itself, checks its own health, shuts
down cleanly) — no server to manage, no browser tab.

**Single-user. Local-first. Offline-first. Yours.** No cloud, no accounts, no SaaS.

> Knowledge → Understanding → Tested Theories → High-quality Decisions — and remembered forever.

## What it is
- A **markdown vault** (`vault/`) that is the permanent, human-readable source of truth.
- A set of **deterministic engines** (`app/`) over it: parser, search, decision engine,
  epistemics (confidence/contradiction), synthesis, graph analytics, market intel, and a
  governance bot that keeps the knowledge base healthy.
- A **local dashboard** (`ui/`) — your morning command center.

Every claim traces to evidence. Confidence is derived, never asserted. AI is optional
(local Ollama only) and can never override a deterministic result.

## Run it (clone → install → one command)
```bash
git clone https://github.com/krishagarwal175/Project-Atlas.git
cd Project-Atlas
pip install -r app/requirements.txt

python desktop/atlas.py    # windowed desktop app (boots the kernel, opens a window)
# —or, engine only—
cd app && python cli.py serve    # local API on http://127.0.0.1:8000; open ui/index.html
```
Build a distributable `.exe`: `python desktop/build.py` → `dist/Atlas.exe` (see `desktop/README.md`).
No cloud setup. No accounts. No deployment. It works offline; the internet only enhances
Market Intelligence.

Also useful:
```bash
python cli.py stats        # vault health snapshot
python cli.py audit        # run the governance bot
python cli.py search "should we launch a referral program"
python -m pytest           # 37 tests over the deterministic core
```

## Repository
```
app/        # the application (engines, parser, governance, decision engine, api, cli, tests)
ui/         # local dashboard (single self-contained HTML, no build step)
vault/      # the knowledge substrate — open it in Obsidian; it works by hand alone
docs/       # local-first development + architecture pointers
archive/    # marketing/landing-page — a FUTURE public release, not part of Atlas v1
```

## Foundations
- **Design system:** [docs/DESIGN-SYSTEM.md](docs/DESIGN-SYSTEM.md) · **Desktop architecture:** [docs/DESKTOP-ARCHITECTURE.md](docs/DESKTOP-ARCHITECTURE.md)
- **ADRs:** [001 substrate](vault/300-Architecture/Tech-Decisions/ADR-001-markdown-substrate.md) · [002 freeze](vault/300-Architecture/Tech-Decisions/ADR-002-atlas-1.0-architecture-freeze.md) · [003 local-first](vault/300-Architecture/Tech-Decisions/ADR-003-local-first-single-user.md) · [004 desktop](vault/300-Architecture/Tech-Decisions/ADR-004-desktop-architecture.md)
- **Dev guide:** [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)

Cloud/multi-user is a *possible* Phase 5 — v1 ignores it entirely and is excellent locally first.
