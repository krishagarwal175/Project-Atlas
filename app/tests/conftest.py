"""Shared test fixtures. Tests build their own tiny fixture vaults so they stay
stable as the real vault grows."""
import sys
from pathlib import Path

import pytest

# make app/ importable when running pytest from anywhere
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import vault  # noqa: E402


@pytest.fixture
def make_vault(tmp_path):
    """Write {relpath: content} markdown files into a temp dir and load them."""
    def _make(files: dict[str, str]):
        for rel, content in files.items():
            p = tmp_path / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
        return vault.load_vault(tmp_path)
    _make.path = tmp_path
    return _make


def note_md(type_, title, body="body text", **fm):
    fm_lines = [f"type: {type_}", f'title: "{title}"']
    for k, v in fm.items():
        fm_lines.append(f"{k}: {v}")
    return "---\n" + "\n".join(fm_lines) + "\n---\n\n" + body
