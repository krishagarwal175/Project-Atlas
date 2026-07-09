# Atlas — Desktop Architecture

Atlas is a **Local-First Desktop Research Operating System**. Launch it and it feels like
Obsidian/VS Code/Linear — a single window, always warm, entirely local. The `.exe` is a
distribution format; the architecture below is what makes producing one trivial.

Authoritative decision record: **`vault/300-Architecture/Tech-Decisions/ADR-004-desktop-architecture.md`**.

## Layers (dependencies flow down only)
```
APPLICATION  window shell + launcher      desktop/atlas.py, ui/
   ↓
SERVICE      HTTP + lifecycle + config     app/api.py, lifecycle.py, paths.py, config.py
   ↓
DOMAIN       engines                       app/{decision_engine,epistemics,synthesis,
   ↓                                             governance,graph,search,market_intel}.py
KNOWLEDGE    parser + Evidence Ledger      app/vault.py
   ↓
VAULT        markdown source of truth      vault/
```

## The kernel (`app/lifecycle.py`)
- **Boot:** ordered, timed, logged, recoverable steps → `BootReport` (`READY`/`DEGRADED`).
- **Health:** every subsystem checked.
- **Shutdown:** reverse-order hooks, log flush, no data loss.
- **Logging:** structured, to `logs/atlas-YYYY-MM-DD.log` + console.

## Configuration & user data (`app/paths.py`)
Application (binaries) is separated from user data (vault/cache/logs/config). **Portable**
mode keeps data beside the app; **installed** mode uses the OS user area
(`Documents/Atlas`). All env-overridable (`ATLAS_HOME/VAULT/CACHE/LOGS/CONFIG`); no
hardcoded paths. Reinstall the app without losing your organizational intelligence.

## Run
```bash
python desktop/atlas.py      # windowed app (boots via the kernel)
# or
cd app && python cli.py serve   # engine only; open ui/index.html
```

## Packaging
- Dev: `python desktop/build.py` → `dist/Atlas.exe` (PyInstaller).
- Production (preferred): **Tauri** sidecars the built server and points its OS webview at
  `127.0.0.1` — small installer, no coupling. Electron is an acceptable alternative.

## Extension points (designed, not built)
AI providers (local, `narrative.py`), importers/exporters (`vault_write.py` pattern),
knowledge sources (`market_intel` feeds in `config.py`), new engines (add a module + a row
in the service table), visualizations (graph endpoints). Add via new modules — never by
coupling into the core.
