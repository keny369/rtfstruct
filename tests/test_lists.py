# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Tests for list metadata and post-pass assembly."""

from rtfstruct import parse_rtf
from rtfstruct.ast import ListBlock, Paragraph, TextRun


def _paragraph_text(paragraph: Paragraph) -> str:
    """Return paragraph text for tests."""
    return "".join(child.text for child in paragraph.children if isinstance(child, TextRun))


def test_list_metadata_paragraphs_are_grouped_in_postpass() -> None:
    document = parse_rtf(r"{\rtf1\ls1\ilvl0 First\par\ls1\ilvl1 Second\par\pard Plain}")

    list_block = document.blocks[0]

    assert isinstance(list_block, ListBlock)
    assert list_block.list_id == 1
    assert list_block.ordered is False
    assert [item.level for item in list_block.items] == [0, 1]
    assert [_paragraph_text(item.blocks[0]) for item in list_block.items] == ["First", "Second"]
    assert isinstance(document.blocks[1], Paragraph)
    assert _paragraph_text(document.blocks[1]) == "Plain"


def test_distinct_list_id_starts_new_list_block() -> None:
    document = parse_rtf(r"{\rtf1\ls1 One\par\ls2 Two}")

    assert len(document.blocks) == 2
    assert all(isinstance(block, ListBlock) for block in document.blocks)
    assert [block.list_id for block in document.blocks if isinstance(block, ListBlock)] == [1, 2]


def test_list_json_export() -> None:
    document = parse_rtf(r"{\rtf1\ls1\ilvl0 First\par\ls1\ilvl1 Second}")

    assert document.to_json()["blocks"] == [
        {
            "type": "list",
            "ordered": False,
            "list_id": 1,
            "items": [
                {
                    "type": "list_item",
                    "level": 0,
                    "blocks": [
                        {
                            "type": "paragraph",
                            "style": {"list_identity": 1, "list_level": 0},
                            "children": [{"type": "text", "text": "First", "style": {}}],
                        }
                    ],
                },
                {
                    "type": "list_item",
                    "level": 1,
                    "blocks": [
                        {
                            "type": "paragraph",
                            "style": {"list_identity": 1, "list_level": 1},
                            "children": [{"type": "text", "text": "Second", "style": {}}],
                        }
                    ],
                },
            ],
        }
    ]


def test_list_markdown_export() -> None:
    document = parse_rtf(r"{\rtf1\ls1\ilvl0 First\par\ls1\ilvl1 Second}")

    assert document.to_markdown() == "- First\n  - Second"


def test_list_table_resolves_ordered_list() -> None:
    document = parse_rtf(
        r"{\rtf1"
        r"{\*\listtable{\list{\listlevel\levelnfc0}\listid42}}"
        r"{\*\listoverridetable{\listoverride\listid42\ls7}}"
        r"\ls7\ilvl0 First\par\ls7\ilvl0 Second}"
    )

    list_block = document.blocks[0]

    assert isinstance(list_block, ListBlock)
    assert list_block.ordered is True
    assert list_block.list_id == 7
    assert document.to_markdown() == "1. First\n2. Second"


def test_list_table_resolves_bullet_list_as_unordered() -> None:
    document = parse_rtf(
        r"{\rtf1"
        r"{\*\listtable{\list{\listlevel\levelnfc23}\listid99}}"
        r"{\*\listoverridetable{\listoverride\listid99\ls4}}"
        r"\ls4\ilvl0 Bullet}"
    )

    list_block = document.blocks[0]

    assert isinstance(list_block, ListBlock)
    assert list_block.ordered is False
    assert list_block.list_id == 4
    assert document.to_markdown() == "- Bullet"


def test_list_json_export_preserves_ordered_flag_from_list_table() -> None:
    document = parse_rtf(
        r"{\rtf1"
        r"{\*\listtable{\list{\listlevel\levelnfc0}\listid42}}"
        r"{\*\listoverridetable{\listoverride\listid42\ls7}}"
        r"\ls7\ilvl0 First}"
    )

    assert document.to_json()["blocks"][0]["ordered"] is True


def test_semantic_equals_compares_list_content() -> None:
    left = parse_rtf(r"{\rtf1\ls1 First}")
    right = parse_rtf(r"{\rtf1\ls1 Different}")

    assert not left.semantic_equals(right)
