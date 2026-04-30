# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Tests for writing AST documents back to RTF."""

from pathlib import Path

from rtfstruct import (
    Color,
    Annotation,
    AnnotationRef,
    Document,
    Footnote,
    FootnoteRef,
    Image,
    ImageInline,
    LineBreak,
    Link,
    ListBlock,
    ListItem,
    Metadata,
    Paragraph,
    ParagraphStyle,
    Tab,
    Table,
    TableCell,
    TextRun,
    TextStyle,
    parse_rtf,
    to_rtf,
    write_rtf,
)


def test_write_basic_inline_styles_roundtrip() -> None:
    document = Document(
        blocks=[
            Paragraph(
                children=[
                    TextRun("Plain "),
                    TextRun(
                        "styled",
                        TextStyle(
                            bold=True,
                            italic=True,
                            foreground=Color(255, 0, 0),
                            font_size_half_points=28,
                        ),
                    ),
                ]
            )
        ]
    )

    reparsed = parse_rtf(to_rtf(document))

    assert document.semantic_equals(reparsed)


def test_write_extended_inline_styles_roundtrip() -> None:
    document = Document(
        blocks=[
            Paragraph(
                children=[
                    TextRun("under", TextStyle(underline=True)),
                    TextRun(" strike", TextStyle(strikethrough=True)),
                    TextRun(" super", TextStyle(superscript=True)),
                    TextRun(" sub", TextStyle(subscript=True)),
                ]
            )
        ]
    )

    reparsed = parse_rtf(to_rtf(document))

    assert document.semantic_equals(reparsed)


def test_write_tab_and_line_break_roundtrip() -> None:
    document = Document(
        blocks=[
            Paragraph(
                children=[
                    TextRun("A"),
                    Tab(),
                    TextRun("B"),
                    LineBreak(),
                    TextRun("C"),
                ]
            )
        ]
    )

    reparsed = parse_rtf(to_rtf(document))

    assert document.semantic_equals(reparsed)
    assert reparsed.to_markdown() == "A    B<br>C"


def test_write_paragraph_formatting_roundtrip() -> None:
    document = Document(
        blocks=[
            Paragraph(
                children=[TextRun("Formatted")],
                style=ParagraphStyle(
                    alignment="justify",
                    left_indent_twips=720,
                    right_indent_twips=360,
                    first_line_indent_twips=-180,
                    space_before_twips=120,
                    space_after_twips=240,
                ),
            )
        ]
    )

    reparsed = parse_rtf(to_rtf(document))
    paragraph = reparsed.blocks[0]

    assert document.semantic_equals(reparsed)
    assert paragraph.style.alignment == "justify"
    assert paragraph.style.left_indent_twips == 720
    assert paragraph.style.right_indent_twips == 360
    assert paragraph.style.first_line_indent_twips == -180
    assert paragraph.style.space_before_twips == 120
    assert paragraph.style.space_after_twips == 240


def test_write_metadata_roundtrip() -> None:
    document = Document(
        blocks=[Paragraph(children=[TextRun("Body")])],
        metadata=Metadata(
            title="Example",
            subject="Subject",
            author="Lee",
            keywords="rtf,python",
            comment="Comment",
            company="Company",
        ),
    )

    reparsed = parse_rtf(to_rtf(document))

    assert document.semantic_equals(reparsed)
    assert reparsed.metadata.title == "Example"
    assert reparsed.metadata.company == "Company"


def test_write_link_roundtrip() -> None:
    document = Document(
        blocks=[
            Paragraph(
                children=[
                    TextRun("Visit "),
                    Link("https://example.com", children=[TextRun("example")]),
                ]
            )
        ]
    )

    assert document.semantic_equals(parse_rtf(document.to_rtf()))


def test_write_footnote_roundtrip() -> None:
    document = Document(
        blocks=[
            Paragraph(
                children=[
                    TextRun("Text"),
                    FootnoteRef(id="fn1", label="1"),
                    TextRun(" after"),
                ]
            )
        ],
        footnotes={
            "fn1": Footnote(
                id="fn1",
                blocks=[Paragraph(children=[TextRun("Footnote text")])],
            )
        },
    )

    reparsed = parse_rtf(to_rtf(document))

    assert document.semantic_equals(reparsed)
    assert reparsed.to_markdown() == "Text[^1] after\n\n[^1]: Footnote text"


def test_write_annotation_roundtrip() -> None:
    document = Document(
        blocks=[
            Paragraph(
                children=[
                    TextRun("Text"),
                    AnnotationRef(id="ann1", label="1"),
                    TextRun(" after"),
                ]
            )
        ],
        annotations={
            "ann1": Annotation(
                id="ann1",
                blocks=[Paragraph(children=[TextRun("Annotation text")])],
            )
        },
    )

    reparsed = parse_rtf(to_rtf(document))

    assert document.semantic_equals(reparsed)
    assert reparsed.to_markdown() == "Text[note 1] after\n\n> [!NOTE] Annotation 1: Annotation text"


def test_write_list_roundtrip() -> None:
    paragraph = Paragraph(
        children=[TextRun("Item")],
        style=ParagraphStyle(list_identity=1, list_level=0),
    )
    document = Document(blocks=[ListBlock(ordered=False, items=[ListItem(blocks=[paragraph], level=0)], list_id=1)])

    assert document.semantic_equals(parse_rtf(to_rtf(document)))


def test_write_ordered_list_roundtrip() -> None:
    paragraph = Paragraph(
        children=[TextRun("Item")],
        style=ParagraphStyle(list_identity=3, list_level=0),
    )
    document = Document(blocks=[ListBlock(ordered=True, items=[ListItem(blocks=[paragraph], level=0)], list_id=3)])

    reparsed = parse_rtf(to_rtf(document))

    assert document.semantic_equals(reparsed)
    assert reparsed.to_markdown() == "1. Item"


def test_write_list_stamps_unstyled_item_paragraphs() -> None:
    document = Document(
        blocks=[
            ListBlock(
                ordered=True,
                items=[ListItem(blocks=[Paragraph(children=[TextRun("Plain item")])], level=1)],
                list_id=5,
            )
        ]
    )

    reparsed = parse_rtf(to_rtf(document))

    list_block = reparsed.blocks[0]
    assert isinstance(list_block, ListBlock)
    assert list_block.ordered is True
    assert list_block.items[0].level == 1
    assert reparsed.to_markdown() == "  1. Plain item"


def test_write_table_roundtrip() -> None:
    document = Document(
        blocks=[
            Table(
                row_count=1,
                col_count=2,
                cells=[
                    TableCell(row=0, col=0, blocks=[Paragraph(children=[TextRun("A")])], width_twips=1000),
                    TableCell(row=0, col=1, blocks=[Paragraph(children=[TextRun("B")])], width_twips=1000),
                ],
            )
        ]
    )

    assert document.semantic_equals(parse_rtf(to_rtf(document)))


def test_write_table_colspan_roundtrip() -> None:
    document = Document(
        blocks=[
            Table(
                row_count=1,
                col_count=2,
                cells=[
                    TableCell(
                        row=0,
                        col=0,
                        blocks=[Paragraph(children=[TextRun("Wide")])],
                        colspan=2,
                        width_twips=2000,
                    )
                ],
            )
        ]
    )

    reparsed = parse_rtf(to_rtf(document))

    assert document.semantic_equals(reparsed)
    assert reparsed.to_json()["blocks"][0]["cells"][0]["colspan"] == 2


def test_write_table_rowspan_roundtrip() -> None:
    document = Document(
        blocks=[
            Table(
                row_count=2,
                col_count=2,
                cells=[
                    TableCell(
                        row=0,
                        col=0,
                        blocks=[Paragraph(children=[TextRun("Top")])],
                        rowspan=2,
                        width_twips=1000,
                    ),
                    TableCell(
                        row=0,
                        col=1,
                        blocks=[Paragraph(children=[TextRun("Right")])],
                        width_twips=1000,
                    ),
                    TableCell(
                        row=1,
                        col=1,
                        blocks=[Paragraph(children=[TextRun("Bottom")])],
                        width_twips=1000,
                    ),
                ],
            )
        ]
    )

    reparsed = parse_rtf(to_rtf(document))

    assert document.semantic_equals(reparsed)
    assert [(cell.row, cell.col, cell.rowspan, cell.colspan) for cell in reparsed.blocks[0].cells] == [
        (0, 0, 2, 1),
        (0, 1, 1, 1),
        (1, 1, 1, 1),
    ]


def test_write_image_roundtrip() -> None:
    document = Document(
        blocks=[Paragraph(children=[ImageInline(id="img1")])],
        images={
            "img1": Image(
                id="img1",
                content_type="image/png",
                data=bytes.fromhex("89504E47"),
                goal_width_twips=100,
                goal_height_twips=200,
            )
        },
    )

    assert document.semantic_equals(parse_rtf(to_rtf(document)))


def test_write_rtf_file(tmp_path: Path) -> None:
    document = Document(blocks=[Paragraph(children=[TextRun("Saved")])])
    path = tmp_path / "out.rtf"

    write_rtf(document, path)

    assert parse_rtf(path.read_text(encoding="utf-8")).semantic_equals(document)
