# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Unstructured-style partitioning helper for RTF documents.

This module returns plain dictionaries rather than importing `unstructured`.
That keeps the core package dependency-free while documenting the shape needed
for a future first-class partitioner.
"""

from __future__ import annotations

from pathlib import Path

from rtfstruct.ast import Document, ListBlock, Paragraph, Table
from rtfstruct.integrations._shared import block_text, document_from_input
from rtfstruct.options import ParserOptions


def partition_rtf(data: bytes | str | Path | Document, options: ParserOptions | None = None) -> list[dict[str, object]]:
    """Partition RTF input into Unstructured-style element dictionaries."""
    document = document_from_input(data, options=options)
    elements: list[dict[str, object]] = []
    for index, block in enumerate(document.blocks):
        text = block_text(block)
        if not text:
            continue
        elements.append(
            {
                "type": _element_type(block),
                "text": text,
                "metadata": {"category_depth": getattr(block, "level", None), "index": index},
            }
        )
    return elements


def _element_type(block: object) -> str:
    """Map rtfstruct block nodes to Unstructured-style element types."""
    if isinstance(block, Paragraph):
        return "NarrativeText"
    if isinstance(block, ListBlock):
        return "ListItem"
    if isinstance(block, Table):
        return "Table"
    return "Text"
