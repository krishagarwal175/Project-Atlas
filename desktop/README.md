# Atlas — Desktop App

Turn Atlas into a double-click desktop application. Local-first: it uses your OS's
built-in webview (Edge WebView2 on Windows) — **no Electron, no Node, no bundled
browser, no cloud.** One executable that boots the engine and opens the dashboard.

## Two ways to run

### A) Zero build — just double-click (fastest)
Requires Python installed (you already have it). Double-click **`Atlas.bat`**, or:
```powershell
python desktop/atlas.py
```
A native window opens with the dashboard. Done.

### B) Build a real `.exe` (portable, no Python needed to run)
```powershell
pip install -r desktop/requirements-desktop.txt
python desktop/build.py
```
→ produces **`dist/Atlas.exe`**. Double-click it. Move it anywhere; a writable
`vault/` folder appears next to it (seeded on first run) and is yours.

> First build takes a few minutes and the exe is large (~150–250 MB) because it
> bundles Python + scikit-learn/scipy. That's the price of "no install needed to run."

## What the launcher does
1. Finds/creates your local `vault/` (source of truth), sets `ATLAS_VAULT`.
2. Starts the engine (FastAPI) on `127.0.0.1` (auto-picks a free port).
3. Opens a native window at that address (falls back to your browser if no webview).

## Which vault does it use?
- **`Atlas.bat` / `python desktop/atlas.py`** → your **repo `vault/`** (your real, live data). Best for daily use.
- **`dist/Atlas.exe`** → a `vault/` **next to the exe** (seeded on first run) — portable/distributable.
- **Override anytime:** set the `ATLAS_VAULT` env var to point at any vault. e.g. to make the exe use your repo vault:
  ```powershell
  $env:ATLAS_VAULT = "D:\OneDrive\Desktop\Miniature-Projects\Project Atlas\vault"; .\dist\Atlas.exe
  ```
  (Or simply move `Atlas.exe` into the project root and run it there.)

## Notes
- Fully offline except Market Intel (`ingest`), which merely enhances.
- `dist/` and `build/` are git-ignored — the binary isn't committed (it's rebuildable).
- Desktop-packaging-friendly by design (invariant I16). If you later prefer Tauri, the
  same static `ui/` + localhost API works unchanged.
