# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Tests for simple RTF table parsing."""

from rtfstruct import parse_rtf
from rtfstruct.ast import Paragraph, Table, TextRun


def _paragraph_text(paragraph: Paragraph) -> str:
    """Return paragraph text for tests."""
    return "".join(child.text for child in paragraph.children if isinstance(child, TextRun))


def test_parse_simple_table_and_following_paragraph() -> None:
    document = parse_rtf(r"{\rtf1\trowd\cellx1000\cellx2000 A\cell B\cell\row After}")

    table = document.blocks[0]

    assert isinstance(table, Table)
    assert table.row_count == 1
    assert table.col_count == 2
    assert [(cell.row, cell.col, cell.width_twips) for cell in table.cells] == [
        (0, 0, 1000),
        (0, 1, 1000),
    ]
    assert [_paragraph_text(cell.blocks[0]) for cell in table.cells] == ["A", "B"]
    assert isinstance(document.blocks[1], Paragraph)
    assert _paragraph_text(document.blocks[1]) == "After"


def test_consecutive_rows_form_one_table() -> None:
    document = parse_rtf(
        r"{\rtf1\trowd\cellx1000 H1\cell H2\cell\row"
        r"\trowd\cellx1000 A\cell B\cell\row}"
    )

    table = document.blocks[0]

    assert isinstance(table, Table)
    assert table.row_count == 2
    assert table.col_count == 2
    assert [_paragraph_text(cell.blocks[0]) for cell in table.cells] == ["H1", "H2", "A", "B"]


def test_table_json_export_uses_resolved_coordinates() -> None:
    document = parse_rtf(r"{\rtf1\trowd\cellx1000 A\cell B\cell\row}")

    assert document.to_json()["blocks"] == [
        {
            "type": "table",
            "row_count": 1,
            "col_count": 2,
            "cells": [
                {
                    "row": 0,
                    "col": 0,
                    "rowspan": 1,
                    "colspan": 1,
                    "width_twips": 1000,
                    "blocks": [
                        {
                            "type": "paragraph",
                            "style": {},
                            "children": [{"type": "text", "text": "A", "style": {}}],
                        }
                    ],
                },
                {
                    "row": 0,
                    "col": 1,
                    "rowspan": 1,
                    "colspan": 1,
                    "blocks": [
                        {
                            "type": "paragraph",
                            "style": {},
                            "children": [{"type": "text", "text": "B", "style": {}}],
                        }
                    ],
                },
            ],
        }
    ]


def test_table_markdown_export() -> None:
    document = parse_rtf(
        r"{\rtf1\trowd H1\cell H2\cell\row"
        r"\trowd A\cell B\cell\row}"
    )

    assert document.to_markdown() == "| H1 | H2 |\n| --- | --- |\n| A | B |"


def test_horizontal_merge_resolves_colspan_and_width() -> None:
    document = parse_rtf(r"{\rtf1\trowd\clmgf\cellx1000\clmrg\cellx2000 Wide\cell\cell\row}")

    table = document.blocks[0]

    assert isinstance(table, Table)
    assert table.row_count == 1
    assert table.col_count == 2
    assert len(table.cells) == 1
    assert table.cells[0].colspan == 2
    assert table.cells[0].width_twips == 2000
    assert _paragraph_text(table.cells[0].blocks[0]) == "Wide"


def test_vertical_merge_resolves_rowspan() -> None:
    document = parse_rtf(
        r"{\rtf1\trowd\clvmgf\cellx1000 Top\cell Right\cell\row"
        r"\trowd\clvmrg\cellx1000\cell Bottom\cell\row}"
    )

    table = document.blocks[0]

    assert isinstance(table, Table)
    assert table.row_count == 2
    assert table.col_count == 2
    assert [(cell.row, cell.col, cell.rowspan, cell.colspan) for cell in table.cells] == [
        (0, 0, 2, 1),
        (0, 1, 1, 1),
        (1, 1, 1, 1),
    ]


def test_merged_table_json_export_preserves_spans() -> None:
    document = parse_rtf(r"{\rtf1\trowd\clmgf\cellx1000\clmrg\cellx2000 Wide\cell\cell\row}")

    table_data = document.to_json()["blocks"][0]

    assert table_data["cells"][0]["colspan"] == 2
    assert table_data["cells"][0]["width_twips"] == 2000


def test_merged_table_markdown_uses_html() -> None:
    document = parse_rtf(r"{\rtf1\trowd\clmgf\cellx1000\clmrg\cellx2000 Wide\cell\cell\row}")

    assert document.to_markdown() == (
        "<table>\n"
        "  <tr>\n"
        '    <td colspan="2">Wide</td>\n'
        "  </tr>\n"
        "</table>"
    )


def test_missing_cell_marker_recovers_trailing_cell_with_diagnostic() -> None:
    document = parse_rtf(r"{\rtf1\trowd A\row}")

    table = document.blocks[0]

    assert isinstance(table, Table)
    assert table.row_count == 1
    assert len(table.cells) == 1
    assert _paragraph_text(table.cells[0].blocks[0]) == "A"
    assert any(diagnostic.code == "RTF_TABLE_MISSING_CELL" for diagnostic in document.diagnostics)


def test_missing_row_marker_recovers_open_row_with_diagnostic() -> None:
    document = parse_rtf(r"{\rtf1\trowd A\cell}")

    table = document.blocks[0]

    assert isinstance(table, Table)
    assert table.row_count == 1
    assert len(table.cells) == 1
    assert any(diagnostic.code == "RTF_TABLE_MISSING_ROW" for diagnostic in document.diagnostics)


def test_table_property_outside_row_emits_diagnostic() -> None:
    document = parse_rtf(r"{\rtf1\cellx1000 Text}")

    assert any(diagnostic.code == "RTF_TABLE_PROPERTY_OUTSIDE_ROW" for diagnostic in document.diagnostics)


def test_cell_outside_row_emits_diagnostic_and_preserves_text() -> None:
    document = parse_rtf(r"{\rtf1 Text\cell}")

    paragraph = document.blocks[0]

    assert isinstance(paragraph, Paragraph)
    assert _paragraph_text(paragraph) == "Text"
    assert any(diagnostic.code == "RTF_TABLE_CELL_OUTSIDE_ROW" for diagnostic in document.diagnostics)


def test_semantic_equals_compares_table_cells() -> None:
    left = parse_rtf(r"{\rtf1\trowd A\cell\row}")
    right = parse_rtf(r"{\rtf1\trowd B\cell\row}")

    assert not left.semantic_equals(right)


def test_semantic_equals_compares_table_spans() -> None:
    left = parse_rtf(r"{\rtf1\trowd\clmgf\cellx1000\clmrg\cellx2000 A\cell\cell\row}")
    right = parse_rtf(r"{\rtf1\trowd A\cell B\cell\row}")

    assert not left.semantic_equals(right)
