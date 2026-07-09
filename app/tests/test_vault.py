"""Parser: frontmatter, wikilinks, ledger, template forcing, link resolution."""
from conftest import note_md


def test_frontmatter_and_type(make_vault):
    notes = make_vault({"a.md": note_md("theory", "My Theory", **{"confidence-state": "emerging"})})
    n = notes[0]
    assert n.type == "theory"
    assert n.title == "My Theory"
    assert n.confidence_state == "emerging"


def test_wikilink_resolution_and_backlinks(make_vault):
    import vault
    files = {
        "a.md": note_md("question", "Q A", "links to [[b]] here"),
        "b.md": note_md("decision", "Dec B", "no links"),
    }
    notes = make_vault(files)
    by = {n.filename: n for n in notes}
    assert "b" in by["a"].outlinks
    back = vault.build_backlinks(notes)
    assert "a" in back["b"]


def test_unresolved_link_marked(make_vault):
    notes = make_vault({"a.md": note_md("question", "Q", "dangling [[nowhere]]")})
    assert any(o.startswith("__UNRESOLVED__") for o in notes[0].outlinks)


def test_ledger_parsing(make_vault):
    body = (
        "## Evidence Ledger\n"
        "| date | source | stance | weight | note |\n"
        "|------|--------|--------|--------|------|\n"
        "| 2026-01-01 | [[X]] | supports | high | good |\n"
        "| 2026-01-02 | [[Y]] | contradicts | low | bad |\n"
    )
    notes = make_vault({"t.md": note_md("theory", "T", body)})
    led = notes[0].ledger
    assert len(led) == 2
    assert led[0].stance == "supports" and led[0].weight == "high"
    assert led[1].stance == "contradicts"


def test_template_folder_forces_template_type(make_vault):
    notes = make_vault({"900-Meta/Templates/TPL-x.md": note_md("question", "tpl")})
    assert notes[0].type == "template"
