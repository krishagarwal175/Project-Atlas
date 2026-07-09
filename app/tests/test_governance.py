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


def test_broken_strategic_link_to_contested_theory(make_vault):
    notes = make_vault({
        "600-Decisions/d.md": note_md("decision", "D", "cites [[t]]", **{"tags": "[domain/gtm]"}),
        "400-Knowledge/Theories/t.md": note_md("theory", "T", "claim", **{"contested": "true", "tags": "[domain/gtm]"}),
    })
    assert "broken-strategic-link" in _cats(audit(notes))


def test_per_note_half_life_override_makes_field_live(make_vault):
    # a 1-day half-life + old review date must trigger a freshness finding,
    # proving the per-note half-life-days field is honored (not dead)
    notes = make_vault({
        "400-Knowledge/Case-Studies/c.md": note_md(
            "case-study", "C", "body",
            **{"tags": "[domain/gtm]", "half-life-days": "1", "last-reviewed": "2020-01-01"}),
    })
    cats = _cats(audit(notes))
    assert "stale-knowledge" in cats or "needs-review" in cats


def test_clean_note_no_findings(make_vault):
    notes = make_vault({
        "a.md": note_md("question", "Q", "links [[b]]", **{"tags": "[domain/gtm]", "status": "open", "created": "2026-07-01"}),
        "b.md": note_md("decision", "D", "links [[a]]", **{"tags": "[domain/gtm]"}),
    })
    # no high/medium severity issues expected
    assert not [f for f in audit(notes) if f.severity in ("high", "medium")]
