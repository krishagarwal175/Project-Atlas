"""Smoke tests against the REAL vault — catch gross regressions in real data."""
import governance
import epistemics
from vault import load_vault


def test_real_vault_parses():
    notes = load_vault()
    assert len(notes) > 20
    # ledgers are being extracted somewhere
    assert sum(len(n.ledger) for n in notes) > 0


def test_real_audit_runs_and_is_clean_ish():
    notes = load_vault()
    findings = governance.audit(notes)
    # no HIGH severity issues should exist in the curated vault
    assert not [f for f in findings if f.severity == "high"]


def test_real_epistemics_no_uncaught_drift_on_theories():
    notes = load_vault()
    # theories present and assessable without error
    assessed = epistemics.assess_all(notes)
    assert any(a for a in assessed)
