"""Epistemics: the confidence-derivation rules that are the anti-bias core."""
from epistemics import _derive_state, assess_all
from conftest import note_md


def test_cannot_exceed_emerging_without_survived_search():
    level, contested, _ = _derive_state(support_w=3, contra=0, survived=0, broken=0, decaying=False)
    assert level == "emerging"  # strong support but no survived search -> capped


def test_survived_search_reaches_well_tested():
    level, contested, _ = _derive_state(support_w=2, contra=0, survived=1, broken=0, decaying=False)
    assert level == "well-tested"
    assert contested is False


def test_broken_search_sets_contested():
    level, contested, _ = _derive_state(support_w=1, contra=1, survived=0, broken=1, decaying=False)
    assert contested is True


def test_decay_caps_one_rung_down():
    fresh, _, _ = _derive_state(2, 0, 1, 0, decaying=False)
    decayed, _, _ = _derive_state(2, 0, 1, 0, decaying=True)
    assert fresh == "well-tested" and decayed == "supported"


def test_assess_detects_drift(make_vault):
    # a theory claiming 'supported' with no survived search should read as drift
    body = (
        "## Evidence Ledger\n"
        "| date | source | stance | weight | note |\n"
        "|---|---|---|---|---|\n"
        "| 2026-01-01 | [[X]] | supports | high | ok |\n"
    )
    notes = make_vault({"t.md": note_md("theory", "T", body,
                                        **{"confidence-state": "supported"})})
    a = next(x for x in assess_all(notes) if x.note == "t")
    assert a.drift is True
    assert a.derived == "emerging"
