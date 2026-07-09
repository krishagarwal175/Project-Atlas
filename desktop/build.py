"""Build Atlas.exe with PyInstaller — a single, self-contained desktop app.

Usage (from the repo root):
    pip install -r desktop/requirements-desktop.txt
    python desktop/build.py

Produces: dist/Atlas.exe  (Windows). No cloud, no installer, just an executable.
The bundled vault/ is a SEED; on first run the .exe copies it next to itself as
your working vault (writable). Move Atlas.exe wherever you like; a `vault/` folder
appears beside it and is yours.
"""
from __future__ import annotations
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEP = ";" if os.name == "nt" else ":"


def main():
    try:
        import PyInstaller.__main__ as pyi
    except ImportError:
        sys.exit("PyInstaller not installed. Run: pip install -r desktop/requirements-desktop.txt")

    args = [
        str(ROOT / "desktop" / "atlas.py"),
        "--name", "Atlas",
        "--onefile",
        "--noconsole",
        "--clean",
        "--noconfirm",
        # bundle the dashboard and a seed vault
        "--add-data", f"{ROOT/'ui'}{SEP}ui",
        "--add-data", f"{ROOT/'vault'}{SEP}vault",
        # make the app engine modules importable inside the bundle
        "--paths", str(ROOT / "app"),
        # heavy scientific deps need explicit collection
        "--collect-submodules", "sklearn",
        "--collect-submodules", "scipy",
        "--collect-submodules", "uvicorn",
        "--collect-data", "sklearn",
        # engine modules (flat package in app/)
        *sum(( ["--hidden-import", m] for m in [
            "api", "cli", "config", "vault", "search", "governance", "epistemics",
            "graph", "decision_engine", "synthesis", "narrative", "vault_write",
            "market_intel", "sklearn.utils._typedefs", "sklearn.neighbors._partition_nodes",
        ]), []),
        "--distpath", str(ROOT / "dist"),
        "--workpath", str(ROOT / "build"),
        "--specpath", str(ROOT / "build"),
    ]
    print("[build] running PyInstaller… (first build can take several minutes)")
    pyi.run(args)
    exe = ROOT / "dist" / ("Atlas.exe" if os.name == "nt" else "Atlas")
    print(f"\n[build] done → {exe}" if exe.exists() else "\n[build] finished (check dist/)")


if __name__ == "__main__":
    main()
