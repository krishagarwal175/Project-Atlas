"""Governance Bot: the audit checks that keep the vault healthy."""
from governance import audit
from conftest import note_md


def _cats(findings):
    return {f.category for f in findings}


def test_weak_pattern_flagged(make_vault):
    notes = make_vault({
        "400-Knowledge/Patterns/P-x.md": note_md("pattern", "P", **{"derived-from": '["[[c1]]"]', "tags": "[domain/gtm]"}),
        "c1.md": note_md("case-study", "C1", **{"tags": "[domain/gtm]"}),
    })
    assert "weak-pattern" in _cats(audit(notes))


def test_broken_link_flagged(make_vault):
    notes = make_vault({
        "400-Knowledge/Case-Studies/c.md": note_md("case-study", "C", "see [[ghost]]", **{"tags": "[domain/gtm]"}),
    })
    assert "broken-link" in _cats(audit(notes))


def test_untriaged_signal_flagged(make_vault):
    notes = make_vault({
        "700-Market-Signals/MS-x.md": note_md("market-signal", "Sig", "no links", **{"tags": "[domain/gtm]"}),
    })
    assert "untriaged-signal" in _cats(audit(notes))


def test_templates_and_readme_not_audited(make_vault):
    notes = make_vault({
        "900-Meta/Templates/TPL-x.md": note_md("question", "tpl", "placeholder [[A-...]]"),
        "README.md": "# readme\n[[whatever]]",
    })
    # neither should produce broken-link findings
    assert "broken-link" not in _cats(audit(notes))


def test_clean_note_no_findings(make_vault):
    notes = make_vault({
        "a.md": note_md("question", "Q", "links [[b]]", **{"tags": "[domain/gtm]", "status": "open", "created": "2026-07-01"}),
        "b.md": note_md("decision", "D", "links [[a]]", **{"tags": "[domain/gtm]"}),
    })
    # no high/medium severity issues expected
    assert not [f for f in audit(notes) if f.severity in ("high", "medium")]
