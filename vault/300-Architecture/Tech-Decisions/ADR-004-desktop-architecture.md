---
type: adr
id: ADR-004
title: "Desktop-first architecture — lifecycle kernel, layers, services, packaging"
status: accepted
date: 2026-07-09
supersedes: ""
amends: "[[ADR-003-local-first-single-user]]"
tags: [architecture, desktop, freeze]
---

# 🖥 ADR-004 — Desktop-First Architecture Blueprint

> Amends the freeze. Atlas becomes a **desktop-first Research OS** — launch it and it
> feels like Obsidian/VS Code/Linear, not a website. The executable is a *distribution
> format*, not the architecture. This document is the required RC blueprint.
>
> **Scope decision (load-bearing):** I built the parts that make Atlas a better long-term
> OS — a **lifecycle kernel**, **path authority with app/user-data separation**, and
> **structured logging** — and I deliberately did **not** shatter the 13 frozen, tested
> engine modules into a 14-folder tree. That fragmentation would add import ceremony and
> break invariant I10 (clean DAG) for zero single-user benefit — the exact "unnecessary
> abstraction" our final rule forbids. Layers are a *mental model + dependency rule*, not
> a directory explosion. See §2.

---

## 1. Desktop Architecture Blueprint
```
┌──────────────────────────────────────────────────────────────┐
│ APPLICATION  — window shell (pywebview today; Tauri/Electron   │
│               later) + launcher orchestration (desktop/atlas)  │
├──────────────────────────────────────────────────────────────┤
│ SERVICE      — HTTP surface (app/api.py) + Lifecycle kernel     │
│               (app/lifecycle.py) + Config/Paths/Logging         │
├──────────────────────────────────────────────────────────────┤
│ DOMAIN       — engines: decision, epistemics, synthesis,        │
│               governance, graph, search, market_intel           │
├──────────────────────────────────────────────────────────────┤
│ KNOWLEDGE    — parser (app/vault.py) + Evidence Ledger model    │
├──────────────────────────────────────────────────────────────┤
│ VAULT        — markdown files (source of truth)                 │
└──────────────────────────────────────────────────────────────┘
Dependencies flow DOWN only (Application→…→Vault). Never up, never sideways-hidden.
```

## 2. Repository structure (what exists, and why not more)
```
Atlas/
├── app/            # the application (flat, clean-DAG package)
│   ├── paths.py        · path authority (app vs user-data)      [Service]
│   ├── config.py       · tunables, sources locations from paths [Service]
│   ├── lifecycle.py    · the KERNEL: boot/health/shutdown/log   [Service]
│   ├── api.py, cli.py  · surfaces                                [Service]
│   ├── vault.py        · parser + Evidence Ledger               [Knowledge]
│   ├── search/graph/decision_engine/epistemics/synthesis/
│   │   governance/narrative/market_intel/vault_write  · engines [Domain]
│   └── tests/          · 43 tests over the deterministic core
├── ui/             # window content (static; tokens.css + index.html)
├── vault/          # source of truth (tracked)
├── desktop/        # launcher + PyInstaller build + Atlas.bat
├── docs/           # DESIGN-SYSTEM, DESKTOP-ARCHITECTURE, DEVELOPMENT…
├── archive/        # marketing/landing-page (future-only)
└── (cache/ logs/ config/  — user data, git-ignored, created at runtime)
```
The layers of §1 are **conceptual**, enforced by the import DAG and this ADR — not by a
folder per layer. A `services/` package with a redundant registry over already-clean
modules would be ceremony; it's **deferred until a second UI/consumer exists** (YAGNI).

## 3. Application Lifecycle Design — `app/lifecycle.py`
The kernel owns domain startup/shutdown. `LifecycleManager.boot()` runs ordered,
timed, logged, individually-recoverable steps and returns a `BootReport` (`READY` vs
`DEGRADED` with per-step diagnostics). `health()` verifies every subsystem.
`shutdown()` runs hooks in reverse boot order and flushes logs.

## 4. Service Architecture (facade over engines — boundaries, not rewrites)
| Service | Module | Responsibility | Depends on | Failure → Recovery |
|---|---|---|---|---|
| Config/Paths | `config`,`paths` | locations, tunables | — | bad path → DEGRADED, diagnostic |
| Logging | `lifecycle.init_logging` | structured logs | paths | unwritable logs → console only |
| Lifecycle | `lifecycle` | boot/health/shutdown | all below | step fails → DEGRADED, continue |
| Vault | `vault` | parse → Notes + ledger | files | parse error → skip file, log |
| Search | `search` | retrieval | vault, sklearn(opt) | no sklearn → keyword fallback |
| Decision | `decision_engine` | WSM + DNA + sensitivity | config, search | — deterministic |
| Governance | `governance` | health audit | vault, epistemics | epistemics missing → skip drift |
| Graph | `graph` | centrality/paths | vault, networkx | — |
| Synthesis | `synthesis` | pattern drafting | vault, narrative(opt) | tiny-N → human review |
| Epistemics | `epistemics` | confidence/contradiction | vault | — |
| Market Intel | `market_intel` | RSS ingest | network(opt) | offline → skip, app fine |

Each engine already has a single responsibility (audited in ADR-002 §2); "service" is the
role name for the layer boundary.

## 5. Startup sequence (deterministic)
`ensure vault → add app to path → init logging → boot: [load_config · validate_env ·
locate_vault · init_dirs · init_parser · init_graph · init_search · init_governance ·
integrity_checks] → free port → start server → verify /health → open window → READY.`
Every step is logged with timing; a failure in a *required* step aborts with diagnostics.

## 6. Shutdown sequence (graceful)
`window closes → mgr.shutdown() → run shutdown hooks (reverse boot order: flush pending
writes, persist governance/cache) → flush + close log handlers → server thread (daemon)
exits with the process.` No data loss: the vault is written synchronously per-action
already (writes complete before the call returns), so there are no buffered writes to lose.

## 7. Configuration Architecture — `app/paths.py`
Single authority. **Application/User-Data separation (I17):** the binary never contains
vault/cache/logs/config. Two modes: **portable** (data beside the app — move the folder,
it travels) and **installed** (data in the OS user area). Everything env-overridable
(`ATLAS_HOME/VAULT/CACHE/LOGS/CONFIG`). No hardcoded paths (I18).

## 8. Desktop Packaging Strategy
- **Dev build:** PyInstaller onefile (`desktop/build.py`) → `Atlas.exe`. Works today.
- **Production (preferred): Tauri.** Because the UI is *static files* + a *localhost API*,
  Tauri bundles the PyInstaller-built server as a **sidecar** and points its native webview
  at `127.0.0.1` — tiny installer, OS webview, no code coupling. **Electron** is the same
  shape, acceptable, heavier. The app is coupled to **no** framework (I20).
- **Never:** the dev environment is not the artifact; the executable is.

## 9. Repository Migration (this ADR)
Added `app/paths.py`, `app/lifecycle.py`; `config.py` now sources paths; `desktop/atlas.py`
boots via the kernel; user-data dirs git-ignored; design system (`ui/tokens.css` +
`docs/DESIGN-SYSTEM.md`) applied. No engine module moved or rewritten (freeze respected).

## 10. Documentation
New: `docs/DESIGN-SYSTEM.md`, `docs/DESKTOP-ARCHITECTURE.md`. Updated: README,
`docs/DEVELOPMENT.md`, System-Architecture, Changelog, Home — all describe Atlas as a
**Local-First Desktop Research OS**.

## 11. Developer Workflow
`clone → cd app → pip install → python cli.py serve` (or `python desktop/atlas.py` for the
windowed app). `python -m pytest` (43). `python desktop/build.py` → `dist/Atlas.exe`. Every
module independently testable; boot is observable via logs.

## 12. Architecture Consistency Audit
- Dependency DAG intact, one-way, no cycles (I10 upheld; extended by I21).
- No hardcoded paths remain (all via `paths.py`).
- No new abstraction without a consumer (services registry deferred, documented).
- 43 tests green; boot READY in ~3s; health all-green; graceful shutdown verified.
- All prior invariants I1–I16 hold; adds I17–I21 below.

---

## New invariants (join ADR-002/003)
- **I17 — App/User-Data separation.** The executable never contains vault/knowledge/cache/logs/config. User data is external and survives reinstall.
- **I18 — Single path authority.** All locations resolve through `paths.py`. No hardcoded paths.
- **I19 — Deterministic, recoverable lifecycle.** Startup/shutdown are ordered, logged, and recoverable; graceful shutdown never loses data.
- **I20 — Framework-agnostic desktop shell.** The window layer is swappable (pywebview→Tauri/Electron); the app is a localhost server + static UI, coupled to no framework.
- **I21 — Layered dependency direction.** Application → Service → Domain → Knowledge → Vault. No upward or hidden cross-layer dependencies.

Links: [[ADR-003-local-first-single-user]] · [[ADR-002-atlas-1.0-architecture-freeze]] · [[System-Architecture]]
