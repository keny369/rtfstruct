# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Tests for optional integration adapter helpers."""

from pathlib import Path

from rtfstruct.integrations import (
    RtfstructMarkdownConverter,
    convert_rtf_to_markdown,
    partition_rtf,
    to_docling_dict,
)


def test_markitdown_helper_converts_rtf_to_markdown() -> None:
    markdown = convert_rtf_to_markdown(r"{\rtf1\ansi Hello \b world\b0}")

    assert markdown == "Hello **world**"


def test_markitdown_converter_reads_path(tmp_path: Path) -> None:
    input_path = tmp_path / "input.rtf"
    input_path.write_text(r"{\rtf1\ansi Path text}", encoding="utf-8")

    assert RtfstructMarkdownConverter().convert(input_path) == "Path text"


def test_markitdown_helper_treats_invalid_path_string_as_input() -> None:
    markdown = convert_rtf_to_markdown("invalid\0path")

    assert markdown == "invalid\0path"


def test_docling_adapter_returns_dependency_free_shape() -> None:
    data = to_docling_dict(r"{\rtf1{\info{\title Example}}\ansi Body}")

    assert data["schema_name"] == "rtfstruct.docling"
    assert data["metadata"]["title"] == "Example"
    assert data["texts"] == [{"index": 0, "type": "paragraph", "text": "Body"}]


def test_unstructured_adapter_partitions_blocks() -> None:
    elements = partition_rtf(r"{\rtf1\ansi First\par Second}")

    assert elements == [
        {"type": "NarrativeText", "text": "First", "metadata": {"category_depth": None, "index": 0}},
        {"type": "NarrativeText", "text": "Second", "metadata": {"category_depth": None, "index": 1}},
    ]
