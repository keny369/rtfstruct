# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Tests for the initial RTF reader skeleton."""

from rtfstruct import Document, ParserOptions, SourceSpan, parse_rtf
from rtfstruct.ast import Paragraph, ParagraphStyle, TextRun


def test_parse_plain_text_and_paragraphs() -> None:
    document = parse_rtf(r"{\rtf1\ansi Hello\par World}")

    assert len(document.blocks) == 2
    assert isinstance(document.blocks[0], Paragraph)
    assert [child.text for child in document.blocks[0].children if isinstance(child, TextRun)] == ["Hello"]
    assert [child.text for child in document.blocks[1].children if isinstance(child, TextRun)] == ["World"]


def test_parse_basic_inline_styles() -> None:
    document = parse_rtf(r"{\rtf1 normal \b bold\b0  \i italic\i0}")

    runs = [child for child in document.blocks[0].children if isinstance(child, TextRun)]

    assert runs[0].text == "normal "
    assert runs[0].style.bold is False
    assert runs[1].text == "bold"
    assert runs[1].style.bold is True
    assert runs[2].text == " "
    assert runs[3].text == "italic"
    assert runs[3].style.italic is True


def test_skips_font_table_destination() -> None:
    document = parse_rtf(r"{\rtf1{\fonttbl{\f0 Times New Roman;}}Body}")

    runs = [child for child in document.blocks[0].children if isinstance(child, TextRun)]

    assert [run.text for run in runs] == ["Body"]


def test_parse_font_family_and_font_size() -> None:
    document = parse_rtf(r"{\rtf1{\fonttbl{\f0 Times New Roman;}{\f1 Courier New;}}\f1\fs28 Mono}")

    run = next(child for child in document.blocks[0].children if isinstance(child, TextRun))

    assert run.text == "Mono"
    assert run.style.font_family == "Courier New"
    assert run.style.font_size_half_points == 28


def test_parse_foreground_and_highlight_colours() -> None:
    document = parse_rtf(
        r"{\rtf1{\colortbl;\red255\green0\blue0;\red255\green255\blue0;}"
        r"\cf1\highlight2 Styled}"
    )

    run = next(child for child in document.blocks[0].children if isinstance(child, TextRun))

    assert run.text == "Styled"
    assert run.style.foreground is not None
    assert run.style.foreground.red == 255
    assert run.style.foreground.green == 0
    assert run.style.foreground.blue == 0
    assert run.style.background is not None
    assert run.style.background.red == 255
    assert run.style.background.green == 255
    assert run.style.background.blue == 0


def test_missing_font_and_colour_entries_emit_diagnostics() -> None:
    document = parse_rtf(r"{\rtf1\f9\cf3 Text}")

    assert any(diagnostic.code == "RTF_MISSING_FONT" for diagnostic in document.diagnostics)
    assert any(diagnostic.code == "RTF_MISSING_COLOR" for diagnostic in document.diagnostics)


def test_parse_paragraph_alignment_indents_and_spacing() -> None:
    document = parse_rtf(r"{\rtf1\qc\li720\ri1440\fi-360\sb120\sa240 Styled paragraph}")

    paragraph = document.blocks[0]

    assert isinstance(paragraph, Paragraph)
    assert paragraph.style.alignment == "center"
    assert paragraph.style.left_indent_twips == 720
    assert paragraph.style.right_indent_twips == 1440
    assert paragraph.style.first_line_indent_twips == -360
    assert paragraph.style.space_before_twips == 120
    assert paragraph.style.space_after_twips == 240


def test_paragraph_style_resets_with_pard() -> None:
    document = parse_rtf(r"{\rtf1\qr Right\par\pard Plain}")

    assert document.blocks[0].style.alignment == "right"
    assert document.blocks[1].style.alignment is None


def test_paragraph_style_is_group_scoped() -> None:
    document = parse_rtf(r"{\rtf1{\qc Center}\par Plain}")

    assert document.blocks[0].style.alignment == "center"
    assert document.blocks[1].style.alignment is None


def test_json_export_uses_ast_shape() -> None:
    document = parse_rtf(r"{\rtf1\ansi Hello}")

    assert document.to_json()["blocks"] == [
        {
            "type": "paragraph",
            "style": {},
            "children": [{"type": "text", "text": "Hello", "style": {}}],
        }
    ]


def test_json_export_includes_font_and_colour_style() -> None:
    document = parse_rtf(
        r"{\rtf1{\fonttbl{\f0 Arial;}}{\colortbl;\red1\green2\blue3;}\f0\cf1 Text}"
    )

    style = document.to_json()["blocks"][0]["children"][0]["style"]

    assert style == {
        "font_family": "Arial",
        "foreground": {"red": 1, "green": 2, "blue": 3},
    }


def test_json_export_includes_paragraph_style() -> None:
    document = parse_rtf(r"{\rtf1\qj\li360 Text}")

    style = document.to_json()["blocks"][0]["style"]

    assert style == {"alignment": "justify", "left_indent_twips": 360}


def test_source_spans_are_disabled_by_default() -> None:
    document = parse_rtf(r"{\rtf1\ansi Hello}")
    paragraph = document.blocks[0]
    run = paragraph.children[0]

    assert isinstance(paragraph, Paragraph)
    assert isinstance(run, TextRun)
    assert paragraph.span is None
    assert run.span is None


def test_track_spans_attaches_text_and_paragraph_spans() -> None:
    source = r"{\rtf1\ansi Hello\par World}"
    document = parse_rtf(source, ParserOptions(track_spans=True))

    first_paragraph = document.blocks[0]
    second_paragraph = document.blocks[1]
    first_run = first_paragraph.children[0]
    second_run = second_paragraph.children[0]

    assert isinstance(first_paragraph, Paragraph)
    assert isinstance(second_paragraph, Paragraph)
    assert isinstance(first_run, TextRun)
    assert isinstance(second_run, TextRun)
    assert first_run.span is not None
    assert second_run.span is not None
    assert source[first_run.span.start : first_run.span.end] == "Hello"
    assert source[second_run.span.start : second_run.span.end] == "World"
    assert first_paragraph.span == first_run.span
    assert second_paragraph.span == second_run.span


def test_track_spans_merges_adjacent_same_style_runs() -> None:
    source = r"{\rtf1 Hello\'e9}"
    document = parse_rtf(source, ParserOptions(track_spans=True))
    run = document.blocks[0].children[0]

    assert isinstance(run, TextRun)
    assert run.text == "Helloé"
    assert run.span is not None
    assert source[run.span.start : run.span.end] == r"Hello\'e9"


def test_json_export_includes_source_spans_when_tracked() -> None:
    source = r"{\rtf1\ansi Hello}"
    document = parse_rtf(source, ParserOptions(track_spans=True))

    block = document.to_json()["blocks"][0]
    child = block["children"][0]

    assert block["span"] == {"start": source.index("Hello"), "end": source.index("Hello") + 5}
    assert child["span"] == {"start": source.index("Hello"), "end": source.index("Hello") + 5}


def test_semantic_equals_compares_paragraph_style() -> None:
    left = parse_rtf(r"{\rtf1\qc Text}")
    right = parse_rtf(r"{\rtf1\qr Text}")

    assert not left.semantic_equals(right)


def test_semantic_equals_ignores_source_spans() -> None:
    left = parse_rtf(r"{\rtf1 Text}")
    right = parse_rtf(r"{\rtf1 Text}")

    assert isinstance(right.blocks[0], Paragraph)
    right.blocks[0].span = SourceSpan(1, 2)

    assert left.semantic_equals(right)


def test_semantic_equals_compares_manual_paragraph_style() -> None:
    left = Paragraph(children=[TextRun("Text")], style=ParagraphStyle(space_after_twips=120))
    right = Paragraph(children=[TextRun("Text")], style=ParagraphStyle(space_after_twips=240))

    assert not Document(blocks=[left]).semantic_equals(Document(blocks=[right]))
