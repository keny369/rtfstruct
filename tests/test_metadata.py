# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Tests for RTF document metadata."""

from rtfstruct import Document, Metadata, ParagraphStyle, StyleSheet, TextStyle, parse_rtf


def test_info_group_populates_document_metadata() -> None:
    document = parse_rtf(
        r"{\rtf1{\info"
        r"{\title Example Title}"
        r"{\subject Example Subject}"
        r"{\author Lee Powell}"
        r"{\keywords rtf,parser}"
        r"{\doccomm Example comment}"
        r"{\*\company Example Company}"
        r"}Body}"
    )

    assert document.metadata.title == "Example Title"
    assert document.metadata.subject == "Example Subject"
    assert document.metadata.author == "Lee Powell"
    assert document.metadata.keywords == "rtf,parser"
    assert document.metadata.comment == "Example comment"
    assert document.metadata.company == "Example Company"


def test_metadata_supports_unicode_and_hex_text() -> None:
    document = parse_rtf(r"{\rtf1{\info{\title Caf\'e9 \u8217?}}Body}")

    assert document.metadata.title == "Café ’"


def test_json_export_includes_metadata() -> None:
    document = parse_rtf(r"{\rtf1{\info{\title Example}{\author Lee}}Body}")

    assert document.to_json()["metadata"] == {"title": "Example", "author": "Lee"}


def test_info_group_does_not_emit_visible_body_text() -> None:
    document = parse_rtf(r"{\rtf1{\info{\title Hidden}}Visible}")

    assert document.to_markdown() == "Visible"


def test_semantic_equals_compares_metadata() -> None:
    left = Document(metadata=Metadata(title="One"))
    right = Document(metadata=Metadata(title="Two"))

    assert not left.semantic_equals(right)


def test_json_export_includes_stylesheet() -> None:
    document = Document(
        styles=StyleSheet(
            paragraph_styles={"Body": ParagraphStyle(alignment="justify")},
            text_styles={"Strong": TextStyle(bold=True)},
        )
    )

    assert document.to_json()["styles"] == {
        "paragraph_styles": {"Body": {"alignment": "justify"}},
        "text_styles": {"Strong": {"bold": True}},
    }


def test_semantic_equals_compares_stylesheet() -> None:
    left = Document(styles=StyleSheet(text_styles={"Strong": TextStyle(bold=True)}))
    right = Document(styles=StyleSheet(text_styles={"Strong": TextStyle(italic=True)}))

    assert not left.semantic_equals(right)
