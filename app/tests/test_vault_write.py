"""Safe writes back to source notes (human-initiated actions)."""
import config
import vault_write
from conftest import note_md


def test_set_frontmatter_field(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "VAULT_PATH", tmp_path)
    (tmp_path / "n.md").write_text(note_md("market-signal", "S", "body", **{"linked-to": '""'}), encoding="utf-8")
    assert vault_write.set_frontmatter_field("n", "linked-to", "[[Q-x]]")
    text = (tmp_path / "n.md").read_text(encoding="utf-8")
    assert 'linked-to: "[[Q-x]]"' in text


def test_append_under_section(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "VAULT_PATH", tmp_path)
    (tmp_path / "n.md").write_text(note_md("market-signal", "S", "## Touches\n"), encoding="utf-8")
    assert vault_write.append_under_section("n", "Touches", "[[Q-x]] (stance: supports)")
    text = (tmp_path / "n.md").read_text(encoding="utf-8")
    assert "- [[Q-x]] (stance: supports)" in text


def test_triage_signal_end_to_end(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "VAULT_PATH", tmp_path)
    (tmp_path / "MS.md").write_text(note_md("market-signal", "S", "## Touches\n", **{"linked-to": '""'}), encoding="utf-8")
    assert vault_write.triage_signal("MS", "Q-x", "supports")
    text = (tmp_path / "MS.md").read_text(encoding="utf-8")
    assert "[[Q-x]]" in text
