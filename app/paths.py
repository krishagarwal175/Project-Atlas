"""Atlas path resolution — the single authority for *where things live*.

Separates the **application** (binaries, read-only) from **user data** (vault, cache,
logs, config — external, portable, survives reinstall). No hardcoded paths anywhere
else in the codebase; everything resolves through here.

Resolution (highest priority first):
  • explicit env vars: ATLAS_HOME, ATLAS_VAULT, ATLAS_CACHE, ATLAS_LOGS, ATLAS_CONFIG
  • PORTABLE mode: if a `vault/` (or an `atlas.portable` marker) sits next to the app,
    all user data lives beside the app — move the folder anywhere, it travels with you.
  • INSTALLED mode: user data lives in the OS user area
    (Windows: %USERPROFILE%\Documents\Atlas · macOS: ~/Documents/Atlas · Linux: ~/.local/share/atlas).

This module NEVER creates directories on import (keeps it pure/testable). Call
`ensure_dirs()` from the lifecycle boot sequence to materialize them.
"""
from __future__ import annotations
import os
import sys
from dataclasses import dataclass
from pathlib import Path


def _frozen() -> bool:
    return getattr(sys, "frozen", False)


def app_root() -> Path:
    """Where the application/binary lives (read-only in an installed layout)."""
    if _frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent  # repo root


def _os_user_data() -> Path:
    home = Path.home()
    if os.name == "nt":
        return home / "Documents" / "Atlas"
    if sys.platform == "darwin":
        return home / "Documents" / "Atlas"
    return Path(os.environ.get("XDG_DATA_HOME", home / ".local" / "share")) / "atlas"


def _is_portable(root: Path) -> bool:
    return (root / "atlas.portable").exists() or (root / "vault").exists()


def data_dir() -> Path:
    """Root of all USER DATA (never inside the executable)."""
    if os.environ.get("ATLAS_HOME"):
        return Path(os.environ["ATLAS_HOME"]).expanduser()
    root = app_root()
    return root if _is_portable(root) else _os_user_data()


@dataclass(frozen=True)
class AtlasPaths:
    app_root: Path
    data_dir: Path
    vault: Path
    cache: Path
    logs: Path
    config_dir: Path
    portable: bool

    def as_dict(self) -> dict[str, str]:
        return {k: str(v) for k, v in self.__dict__.items() if isinstance(v, Path)} | {
            "portable": str(self.portable)
        }


def _env_or(default: Path, *names: str) -> Path:
    for n in names:
        if os.environ.get(n):
            return Path(os.environ[n]).expanduser()
    return default


def resolve() -> AtlasPaths:
    root = app_root()
    dd = data_dir()
    return AtlasPaths(
        app_root=root,
        data_dir=dd,
        vault=_env_or(dd / "vault", "ATLAS_VAULT"),
        cache=_env_or(dd / "cache", "ATLAS_CACHE"),
        logs=_env_or(dd / "logs", "ATLAS_LOGS"),
        config_dir=_env_or(dd / "config", "ATLAS_CONFIG"),
        portable=_is_portable(root) and not os.environ.get("ATLAS_HOME"),
    )


def ensure_dirs(paths: AtlasPaths | None = None) -> AtlasPaths:
    """Create the user-data directories (never the vault — that's seeded by lifecycle)."""
    paths = paths or resolve()
    for d in (paths.data_dir, paths.cache, paths.logs, paths.config_dir):
        d.mkdir(parents=True, exist_ok=True)
    return paths


if __name__ == "__main__":
    p = resolve()
    print(f"mode: {'PORTABLE' if p.portable else 'INSTALLED'}")
    for k, v in p.as_dict().items():
        print(f"  {k:10} {v}")
