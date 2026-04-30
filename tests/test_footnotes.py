# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Tests for RTF footnotes."""

from rtfstruct import parse_rtf
from rtfstruct.ast import FootnoteRef, TextRun


def test_footnote_destination_emits_reference_and_document_footnote() -> None:
    document = parse_rtf(r"{\rtf1 Text{\footnote Footnote text} after}")

    children = document.blocks[0].children

    assert [child.text for child in children if isinstance(child, TextRun)] == ["Text", " after"]
    assert isinstance(children[1], FootnoteRef)
    assert children[1].id == "fn1"
    assert list(document.footnotes) == ["fn1"]

    footnote = document.footnotes["fn1"]
    assert [child.text for child in footnote.blocks[0].children if isinstance(child, TextRun)] == [
        "Footnote text"
    ]


def test_footnote_json_export() -> None:
    document = parse_rtf(r"{\rtf1 Text{\footnote Note}}")

    data = document.to_json()

    assert data["blocks"][0]["children"][1] == {"type": "footnote_ref", "id": "fn1", "label": "1"}
    assert data["footnotes"] == {
        "fn1": {
            "type": "footnote",
            "id": "fn1",
            "blocks": [
                {
                    "type": "paragraph",
                    "style": {},
                    "children": [{"type": "text", "text": "Note", "style": {}}],
                }
            ],
        }
    }


def test_footnote_markdown_export() -> None:
    document = parse_rtf(r"{\rtf1 Text{\footnote Note} after}")

    assert document.to_markdown() == "Text[^1] after\n\n[^1]: Note"


def test_semantic_equals_compares_footnote_content() -> None:
    left = parse_rtf(r"{\rtf1 Text{\footnote Note}}")
    right = parse_rtf(r"{\rtf1 Text{\footnote Different}}")

    assert not left.semantic_equals(right)


def test_unclosed_footnote_recovers_at_eof() -> None:
    document = parse_rtf(r"{\rtf1 Text{\footnote Note")

    assert document.to_markdown() == "Text[^1]\n\n[^1]: Note"
    assert any(diagnostic.code == "RTF_UNCLOSED_DESTINATION" for diagnostic in document.diagnostics)
