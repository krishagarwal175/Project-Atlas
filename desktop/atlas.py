"""Atlas desktop launcher — one entry point that boots everything.

Double-click the built .exe (or run this file) and Atlas:
  1. locates/creates your local `vault/` (the source of truth),
  2. starts the local engine (FastAPI) on 127.0.0.1,
  3. opens a native window showing the dashboard.

Fully local. No cloud, no accounts, no internet required (except Market Intel).
Falls back to the default browser if a native webview isn't available.
"""
from __future__ import annotations
import os
import socket
import sys
import threading
import time
from pathlib import Path


def _frozen() -> bool:
    return getattr(sys, "frozen", False)


def _ensure_std_streams():
    """In a windowed (--noconsole) build, sys.stdout/stderr are None. Give them real
    streams so libraries that touch them (uvicorn's isatty check, stray prints) don't crash."""
    devnull = open(os.devnull, "w")
    if sys.stdout is None:
        sys.stdout = devnull
    if sys.stderr is None:
        sys.stderr = devnull


def app_base() -> Path:
    """Where the user's data lives (writable). Next to the .exe when frozen."""
    if _frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent  # repo root


def bundle_base() -> Path:
    """Where bundled read-only resources live (ui/, seed vault/)."""
    if _frozen():
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parent.parent


def ensure_vault() -> Path:
    """Pick the vault, in priority order:
    1. an explicit ATLAS_VAULT env var (point Atlas at any vault you like),
    2. a `vault/` next to the app/exe (seeded from the bundle on first run)."""
    env = os.environ.get("ATLAS_VAULT")
    if env:
        return Path(env)
    vault = app_base() / "vault"
    if not vault.exists():
        seed = bundle_base() / "vault"
        if seed.exists():
            import shutil
            shutil.copytree(seed, vault)
        else:
            vault.mkdir(parents=True, exist_ok=True)
    os.environ["ATLAS_VAULT"] = str(vault)
    return vault


def free_port(preferred: int = 8000) -> int:
    for port in (preferred, 8001, 8010, 8123, 8765, 0):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return s.getsockname()[1]
            except OSError:
                continue
    return preferred


def wait_for(port: int, timeout: float = 30.0) -> bool:
    end = time.time() + timeout
    while time.time() < end:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) == 0:
                return True
        time.sleep(0.15)
    return False


def _add_app_to_path():
    """Make the app/ engine modules importable (dev + frozen)."""
    app_dir = bundle_base() / "app"
    if app_dir.exists() and str(app_dir) not in sys.path:
        sys.path.insert(0, str(app_dir))


def start_engine(port: int):
    _add_app_to_path()
    import uvicorn
    # log_config=None: don't let uvicorn reconfigure logging. Its default formatter
    # calls sys.stdout.isatty(), which crashes in a windowed (--noconsole) build where
    # stdout is None. The lifecycle kernel already owns logging (→ logs/).
    config = uvicorn.Config("api:app", host="127.0.0.1", port=port,
                            log_level="warning", log_config=None)
    server = uvicorn.Server(config)
    server.install_signal_handlers = lambda: None  # allow running off the main thread
    threading.Thread(target=server.run, daemon=True).start()


def open_window(url: str):
    try:
        import webview  # pywebview → native Edge WebView2 on Windows
        webview.create_window("Atlas — Decision OS", url, width=1320, height=880,
                              min_size=(960, 640))
        webview.start()
    except Exception:
        import webbrowser
        webbrowser.open(url)
        print(f"[atlas] running at {url} — close this window to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass


def main():
    # 0. windowed builds have no console — make stdout/stderr safe first of all
    _ensure_std_streams()
    # 1. locate/seed the vault, then bring the app modules into scope
    ensure_vault()
    _add_app_to_path()

    # 2. deterministic domain boot through the lifecycle kernel (logs + health)
    import paths, lifecycle
    P = paths.resolve()
    logfile = lifecycle.init_logging(P)
    mgr = lifecycle.LifecycleManager(P)
    report = mgr.boot()
    if not report.ready:
        print(f"[atlas] boot DEGRADED — see {logfile}", file=sys.stderr)
        for r in report.failed:
            print(f"  - {r.name}: {r.error}", file=sys.stderr)
        sys.exit(1)

    # 3. launch the local server, verify it, open the window
    port = free_port(8000)
    start_engine(port)
    url = f"http://127.0.0.1:{port}/"
    if not wait_for(port):
        print("[atlas] engine failed to start", file=sys.stderr)
        mgr.shutdown()
        sys.exit(1)

    try:
        open_window(url)          # blocks until the window closes
    finally:
        mgr.shutdown()            # 4. graceful shutdown — flush logs, run hooks


if __name__ == "__main__":
    main()
