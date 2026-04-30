# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Tests for Markdown export behavior."""

from rtfstruct import Color, Document, MarkdownOptions, Paragraph, Table, TableCell, TextRun, TextStyle


def test_markdown_preserves_colors_by_default() -> None:
    document = Document(
        blocks=[
            Paragraph(
                children=[
                    TextRun(
                        "colored",
                        TextStyle(
                            foreground=Color(255, 0, 16),
                            background=Color(1, 2, 3),
                        ),
                    )
                ]
            )
        ]
    )

    assert document.to_markdown() == (
        '<span style="color: #ff0010; background-color: #010203;">colored</span>'
    )


def test_markdown_can_omit_colors() -> None:
    document = Document(
        blocks=[
            Paragraph(
                children=[
                    TextRun(
                        "colored",
                        TextStyle(foreground=Color(255, 0, 16)),
                    )
                ]
            )
        ]
    )

    assert document.to_markdown(MarkdownOptions(preserve_colors=False)) == "colored"


def test_markdown_font_and_size_options() -> None:
    document = Document(
        blocks=[
            Paragraph(
                children=[
                    TextRun(
                        "fonted",
                        TextStyle(font_family="Source Serif", font_size_half_points=25),
                    )
                ]
            )
        ]
    )

    assert document.to_markdown(
        MarkdownOptions(preserve_fonts=True, preserve_font_sizes=True)
    ) == '<span style="font-family: Source Serif; font-size: 12.5pt;">fonted</span>'


def test_markdown_combines_markdown_and_html_styles() -> None:
    document = Document(
        blocks=[
            Paragraph(
                children=[
                    TextRun(
                        "both",
                        TextStyle(bold=True, foreground=Color(0, 0, 255)),
                    )
                ]
            )
        ]
    )

    assert document.to_markdown() == '<span style="color: #0000ff;">**both**</span>'


def test_markdown_complex_table_can_be_flattened_to_gfm() -> None:
    document = Document(
        blocks=[
            Table(
                row_count=1,
                col_count=2,
                cells=[
                    TableCell(
                        row=0,
                        col=0,
                        colspan=2,
                        blocks=[Paragraph(children=[TextRun("Wide")])],
                    )
                ],
            )
        ]
    )

    assert document.to_markdown(MarkdownOptions(complex_tables="gfm")) == "| Wide |  |\n| --- | --- |"


def test_markdown_complex_table_can_be_omitted() -> None:
    document = Document(
        blocks=[
            Paragraph(children=[TextRun("Before")]),
            Table(row_count=1, col_count=2, cells=[TableCell(row=0, col=0, colspan=2)]),
            Paragraph(children=[TextRun("After")]),
        ]
    )

    assert document.to_markdown(MarkdownOptions(complex_tables="omit")) == "Before\n\n\n\nAfter"
