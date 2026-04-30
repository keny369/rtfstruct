# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Tests for RTF fields and hyperlinks."""

from rtfstruct import parse_rtf
from rtfstruct.ast import Field, Link, TextRun


def test_hyperlink_field_emits_link_inline() -> None:
    document = parse_rtf(
        r'{\rtf1 Before {\field{\*\fldinst HYPERLINK "https://example.com"}{\fldrslt Example}} after}'
    )

    children = document.blocks[0].children

    assert isinstance(children[1], Link)
    assert children[1].target == "https://example.com"
    assert [child.text for child in children[1].children if isinstance(child, TextRun)] == ["Example"]
    assert [child.text for child in children if isinstance(child, TextRun)] == ["Before ", " after"]


def test_unknown_field_preserves_instruction_and_result() -> None:
    document = parse_rtf(r"{\rtf1 {\field{\*\fldinst PAGE}{\fldrslt 1}}}")

    field = document.blocks[0].children[0]

    assert isinstance(field, Field)
    assert field.instruction == "PAGE"
    assert [child.text for child in field.children if isinstance(child, TextRun)] == ["1"]


def test_json_export_includes_link_and_field_nodes() -> None:
    document = parse_rtf(
        r'{\rtf1 {\field{\*\fldinst HYPERLINK "https://example.com"}{\fldrslt Example}}'
        r" {\field{\*\fldinst PAGE}{\fldrslt 1}}}"
    )

    children = document.to_json()["blocks"][0]["children"]

    assert children[0] == {
        "type": "link",
        "target": "https://example.com",
        "instruction": 'HYPERLINK "https://example.com"',
        "children": [{"type": "text", "text": "Example", "style": {}}],
    }
    assert children[2] == {
        "type": "field",
        "instruction": "PAGE",
        "children": [{"type": "text", "text": "1", "style": {}}],
    }


def test_markdown_export_outputs_links_and_visible_unknown_field_results() -> None:
    document = parse_rtf(
        r'{\rtf1 See {\field{\*\fldinst HYPERLINK "https://example.com"}{\fldrslt Example}}'
        r" page {\field{\*\fldinst PAGE}{\fldrslt 1}}}"
    )

    assert document.to_markdown() == "See [Example](https://example.com) page 1"


def test_unclosed_field_recovers_at_eof() -> None:
    document = parse_rtf(r"{\rtf1 Before {\field{\*\fldinst PAGE}{\fldrslt 1")

    assert document.to_markdown() == "Before 1"
    assert isinstance(document.blocks[0].children[1], Field)
    assert any(diagnostic.code == "RTF_UNCLOSED_DESTINATION" for diagnostic in document.diagnostics)
