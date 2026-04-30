# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Tests for RTF annotations/comments."""

from rtfstruct import MarkdownOptions, parse_rtf
from rtfstruct.ast import AnnotationRef, TextRun


def test_annotation_destination_emits_reference_and_document_annotation() -> None:
    document = parse_rtf(r"{\rtf1 Text{\annotation Comment text} after}")

    children = document.blocks[0].children

    assert [child.text for child in children if isinstance(child, TextRun)] == ["Text", " after"]
    assert isinstance(children[1], AnnotationRef)
    assert children[1].id == "ann1"
    assert list(document.annotations) == ["ann1"]

    annotation = document.annotations["ann1"]
    assert [child.text for child in annotation.blocks[0].children if isinstance(child, TextRun)] == [
        "Comment text"
    ]


def test_annotation_json_export() -> None:
    document = parse_rtf(r"{\rtf1 Text{\annotation Note}}")

    data = document.to_json()

    assert data["blocks"][0]["children"][1] == {"type": "annotation_ref", "id": "ann1", "label": "1"}
    assert data["annotations"] == {
        "ann1": {
            "type": "annotation",
            "id": "ann1",
            "blocks": [
                {
                    "type": "paragraph",
                    "style": {},
                    "children": [{"type": "text", "text": "Note", "style": {}}],
                }
            ],
        }
    }


def test_annotation_markdown_export() -> None:
    document = parse_rtf(r"{\rtf1 Text{\annotation Note} after}")

    assert document.to_markdown() == "Text[note 1] after\n\n> [!NOTE] Annotation 1: Note"


def test_annotation_markdown_inline_mode() -> None:
    document = parse_rtf(r"{\rtf1 Text{\annotation Note} after}")

    assert document.to_markdown(MarkdownOptions(annotations="inline")) == "Text[note: Note] after"


def test_annotation_markdown_html_comment_mode() -> None:
    document = parse_rtf(r"{\rtf1 Text{\annotation Note <x>} after}")

    assert document.to_markdown(MarkdownOptions(annotations="html_comment")) == (
        "Text after\n\n<!-- Annotation 1: Note &lt;x&gt; -->"
    )


def test_annotation_markdown_omit_mode() -> None:
    document = parse_rtf(r"{\rtf1 Text{\annotation Note} after}")

    assert document.to_markdown(MarkdownOptions(annotations="omit")) == "Text after"


def test_semantic_equals_compares_annotation_content() -> None:
    left = parse_rtf(r"{\rtf1 Text{\annotation Note}}")
    right = parse_rtf(r"{\rtf1 Text{\annotation Different}}")

    assert not left.semantic_equals(right)


def test_unclosed_annotation_recovers_at_eof() -> None:
    document = parse_rtf(r"{\rtf1 Text{\annotation Note")

    assert document.to_markdown() == "Text[note 1]\n\n> [!NOTE] Annotation 1: Note"
    assert any(diagnostic.code == "RTF_UNCLOSED_DESTINATION" for diagnostic in document.diagnostics)
