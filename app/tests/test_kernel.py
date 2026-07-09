"""Kernel: path resolution (app/user-data separation) + lifecycle boot/shutdown."""
import os

import paths
import lifecycle
from conftest import note_md


def test_paths_env_overrides(monkeypatch, tmp_path):
    monkeypatch.setenv("ATLAS_VAULT", str(tmp_path / "v"))
    monkeypatch.setenv("ATLAS_CACHE", str(tmp_path / "c"))
    monkeypatch.setenv("ATLAS_LOGS", str(tmp_path / "l"))
    p = paths.resolve()
    assert p.vault == tmp_path / "v"
    assert p.cache == tmp_path / "c"
    assert p.logs == tmp_path / "l"


def test_paths_user_data_separated_from_app(monkeypatch, tmp_path):
    # ATLAS_HOME forces an explicit user-data root distinct from the app
    monkeypatch.setenv("ATLAS_HOME", str(tmp_path / "userdata"))
    monkeypatch.delenv("ATLAS_VAULT", raising=False)
    p = paths.resolve()
    assert p.vault == tmp_path / "userdata" / "vault"
    assert p.cache == tmp_path / "userdata" / "cache"


def test_ensure_dirs_creates_user_data_not_vault(monkeypatch, tmp_path):
    monkeypatch.setenv("ATLAS_HOME", str(tmp_path / "ud"))
    p = paths.resolve()
    paths.ensure_dirs(p)
    assert p.cache.exists() and p.logs.exists() and p.config_dir.exists()
    assert not p.vault.exists()  # vault is seeded by lifecycle, not ensure_dirs


def _fixture_vault(tmp_path):
    v = tmp_path / "vault"
    (v / "400-Knowledge").mkdir(parents=True)
    (v / "a.md").write_text(note_md("question", "Q A", "links [[b]]", **{"tags": "[domain/gtm]"}), encoding="utf-8")
    (v / "b.md").write_text(note_md("decision", "Dec B", "links [[a]]", **{"tags": "[domain/gtm]"}), encoding="utf-8")
    return v


def test_lifecycle_boots_ready(monkeypatch, tmp_path):
    v = _fixture_vault(tmp_path)
    monkeypatch.setenv("ATLAS_HOME", str(tmp_path))
    monkeypatch.setenv("ATLAS_VAULT", str(v))
    p = paths.resolve()
    lifecycle.init_logging(p)
    mgr = lifecycle.LifecycleManager(p)
    report = mgr.boot()
    assert report.ready, report.summary()
    names = [r.name for r in report.results]
    assert names == ["load_config", "validate_env", "locate_vault", "init_dirs",
                     "init_parser", "init_graph", "init_search", "init_governance",
                     "integrity_checks"]
    assert mgr.health()["status"] == "ok"


def test_lifecycle_missing_vault_is_degraded(monkeypatch, tmp_path):
    monkeypatch.setenv("ATLAS_HOME", str(tmp_path))
    monkeypatch.setenv("ATLAS_VAULT", str(tmp_path / "nope"))
    p = paths.resolve()
    lifecycle.init_logging(p)
    report = lifecycle.LifecycleManager(p).boot()
    assert not report.ready
    assert any(r.name == "locate_vault" and not r.ok for r in report.results)


def test_shutdown_runs_hooks_in_reverse(monkeypatch, tmp_path):
    monkeypatch.setenv("ATLAS_HOME", str(tmp_path))
    p = paths.resolve()
    lifecycle.init_logging(p)
    mgr = lifecycle.LifecycleManager(p)
    order = []
    mgr.on_shutdown(lambda: order.append("first"))
    mgr.on_shutdown(lambda: order.append("second"))
    mgr.shutdown()
    assert order == ["second", "first"]
