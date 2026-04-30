# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Tests for parser safety limits and generated corpus guardrails."""

from rtfstruct import ParserOptions, parse_rtf


def test_max_document_chars_emits_fatal_diagnostic_and_truncates_output() -> None:
    document = parse_rtf(r"{\rtf1 abcdef}", ParserOptions(max_document_chars=3))

    assert any(diagnostic.code == "RTF_MAX_DOCUMENT_CHARS" for diagnostic in document.diagnostics)
    assert document.blocks == []


def test_max_group_depth_emits_fatal_diagnostic() -> None:
    document = parse_rtf(r"{\rtf1{{{{deep}}}}}", ParserOptions(max_group_depth=2))

    assert any(diagnostic.code == "RTF_MAX_GROUP_DEPTH" for diagnostic in document.diagnostics)


def test_generated_large_paragraph_corpus_parses_to_expected_shape() -> None:
    body = "".join(f"Paragraph {index}\\par " for index in range(250))
    document = parse_rtf("{\\rtf1 " + body + "}")

    assert len(document.blocks) == 250
    assert not any(diagnostic.severity.value == "fatal" for diagnostic in document.diagnostics)
