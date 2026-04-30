# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Tests for the static GitHub Pages documentation site."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_static_docs_site_contains_required_sections_and_diagrams() -> None:
    html = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")

    for anchor in [
        'id="overview"',
        'id="quick-start"',
        'id="flows"',
        'id="parser"',
        'id="ast"',
        'id="conversion"',
        'id="api"',
        'id="cli"',
        'id="testing"',
        'id="release"',
    ]:
        assert anchor in html

    assert html.count('class="mermaid"') >= 6
    assert "parse_rtf" in html
    assert "JsonOptions" in html
    assert "MarkdownOptions" in html
    assert "rtfstruct input.rtf --to json" in html
    assert "GitHub Pages" in html
