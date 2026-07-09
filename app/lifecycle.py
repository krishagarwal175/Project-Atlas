"""Atlas Application Lifecycle Manager — the "kernel".

Owns the deterministic startup and shutdown of the domain (everything below the
HTTP server and the window). Each boot step is ordered, logged, individually
recoverable, and produces meaningful diagnostics on failure. Health checks verify
every subsystem. Shutdown is graceful — pending writes complete, logs persist.

The launcher (desktop/atlas.py) orchestrates the *processes* (start the API server,
open the window) and delegates domain readiness + graceful shutdown to this manager.
Kept deliberately lightweight: this is a single-user local OS, not a distributed
system — the kernel provides order and diagnostics, not ceremony.
"""
from __future__ import annotations
import logging
import time
import traceback
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Callable

import paths as _paths

log = logging.getLogger("atlas")


@dataclass
class StepResult:
    name: str
    ok: bool
    ms: float
    detail: str = ""
    error: str = ""


@dataclass
class BootReport:
    results: list[StepResult] = field(default_factory=list)
    ready: bool = False

    @property
    def failed(self) -> list[StepResult]:
        return [r for r in self.results if not r.ok]

    def summary(self) -> str:
        total = sum(r.ms for r in self.results)
        state = "READY" if self.ready else "DEGRADED"
        return f"[{state}] {len(self.results)} steps in {total:.0f}ms" + (
            f" — FAILED: {', '.join(r.name for r in self.failed)}" if self.failed else ""
        )


def init_logging(paths: _paths.AtlasPaths) -> Path:
    """Structured logging to logs/atlas-YYYY-MM-DD.log + console."""
    paths.logs.mkdir(parents=True, exist_ok=True)
    logfile = paths.logs / f"atlas-{date.today().isoformat()}.log"
    root = logging.getLogger("atlas")
    root.setLevel(logging.INFO)
    root.handlers.clear()
    fmt = logging.Formatter("%(asctime)s %(levelname)-5s %(name)s: %(message)s", "%H:%M:%S")
    fh = logging.FileHandler(logfile, encoding="utf-8"); fh.setFormatter(fmt)
    sh = logging.StreamHandler(); sh.setFormatter(fmt)
    root.addHandler(fh); root.addHandler(sh)
    return logfile


class LifecycleManager:
    """Orders the domain boot, runs health checks, and shuts down gracefully."""

    def __init__(self, paths: _paths.AtlasPaths | None = None):
        self.paths = paths or _paths.resolve()
        self._shutdown_hooks: list[Callable[[], None]] = []
        self._state: dict[str, object] = {}

    # ---- boot ----------------------------------------------------------
    def boot(self) -> BootReport:
        report = BootReport()
        steps: list[tuple[str, Callable[[], str]]] = [
            ("load_config", self._load_config),
            ("validate_env", self._validate_env),
            ("locate_vault", self._locate_vault),
            ("init_dirs", self._init_dirs),
            ("init_parser", self._init_parser),
            ("init_graph", self._init_graph),
            ("init_search", self._init_search),
            ("init_governance", self._init_governance),
            ("integrity_checks", self._integrity_checks),
        ]
        for name, fn in steps:
            t0 = time.perf_counter()
            try:
                detail = fn() or ""
                ms = (time.perf_counter() - t0) * 1000
                report.results.append(StepResult(name, True, ms, detail))
                log.info("boot ok %-16s %5.0fms  %s", name, ms, detail)
            except Exception as e:  # recoverable: record, keep going in DEGRADED
                ms = (time.perf_counter() - t0) * 1000
                report.results.append(StepResult(name, False, ms, error=str(e)))
                log.error("boot XX %-16s %5.0fms  %s", name, ms, e)
                log.debug(traceback.format_exc())
        # domain is READY if no *required* step failed. All steps here are required
        # except the last two (governance/integrity are advisory, not blocking).
        required = {"load_config", "validate_env", "locate_vault", "init_dirs",
                    "init_parser", "init_search"}
        report.ready = not any((not r.ok and r.name in required) for r in report.results)
        log.info("boot complete: %s", report.summary())
        return report

    # ---- boot steps (each returns a short detail string) ---------------
    def _load_config(self) -> str:
        import config
        self._state["config"] = config
        return f"vault={config.VAULT_PATH.name}"

    def _validate_env(self) -> str:
        import sys
        if sys.version_info < (3, 10):
            raise RuntimeError(f"Python 3.10+ required, found {sys.version_info[:2]}")
        return f"py{sys.version_info.major}.{sys.version_info.minor}, mode={'portable' if self.paths.portable else 'installed'}"

    def _locate_vault(self) -> str:
        v = self.paths.vault
        if not v.exists():
            raise FileNotFoundError(f"vault not found at {v}")
        n = len(list(v.rglob("*.md")))
        if n == 0:
            raise RuntimeError(f"vault at {v} contains no notes")
        return f"{n} files @ {v}"

    def _init_dirs(self) -> str:
        _paths.ensure_dirs(self.paths)
        return "cache/logs/config ready"

    def _init_parser(self) -> str:
        from vault import load_vault
        notes = load_vault(self.paths.vault)
        self._state["notes"] = notes
        return f"{len(notes)} notes parsed"

    def _init_graph(self) -> str:
        import graph as g
        s = g.summary(self._state.get("notes"))
        return f"{s['nodes']} nodes / {s['edges']} edges"

    def _init_search(self) -> str:
        from search import SearchEngine
        eng = SearchEngine(self._state.get("notes"))
        self._state["search"] = eng
        return f"backend={eng.backend}"

    def _init_governance(self) -> str:
        import governance
        findings = governance.audit(self._state.get("notes"))
        highs = sum(1 for f in findings if f.severity == "high")
        return f"{len(findings)} findings ({highs} high)"

    def _integrity_checks(self) -> str:
        notes = self._state.get("notes") or []
        # cheap invariants: source-of-truth reachable, no zero-note vault
        assert self.paths.vault.exists(), "vault path vanished"
        assert len(notes) > 0, "no notes after parse"
        return "ok"

    # ---- health --------------------------------------------------------
    def health(self) -> dict:
        checks = {
            "vault": self.paths.vault.exists(),
            "notes": bool(self._state.get("notes")),
            "search": self._state.get("search") is not None,
            "logs_writable": self.paths.logs.exists(),
        }
        return {"status": "ok" if all(checks.values()) else "degraded", "checks": checks}

    # ---- shutdown ------------------------------------------------------
    def on_shutdown(self, hook: Callable[[], None]):
        self._shutdown_hooks.append(hook)

    def shutdown(self) -> None:
        log.info("shutdown: running %d hook(s)", len(self._shutdown_hooks))
        for hook in reversed(self._shutdown_hooks):  # reverse boot order
            try:
                hook()
            except Exception as e:
                log.error("shutdown hook failed: %s", e)
        # flush logging handlers so nothing is lost
        for h in logging.getLogger("atlas").handlers:
            try:
                h.flush()
            except Exception:
                pass
        log.info("shutdown complete")


if __name__ == "__main__":
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    p = _paths.resolve()
    init_logging(p)
    mgr = LifecycleManager(p)
    report = mgr.boot()
    print("\n" + report.summary())
    print("health:", mgr.health())
    mgr.shutdown()
