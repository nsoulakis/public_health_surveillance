"""The released notebooks carry no placeholders."""

from pathlib import Path

NOTEBOOKS = Path(__file__).resolve().parents[1] / "python" / "notebooks"


def test_no_placeholders():
    for nb in NOTEBOOKS.glob("*.ipynb"):
        text = nb.read_text(encoding="utf-8")
        assert "PENDING" not in text and "TODO" not in text, nb.name
