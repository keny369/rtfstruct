# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Shared helpers for optional integration adapters."""

from __future__ import annotations

from pathlib import Path

from rtfstruct.ast import (
    AnnotationRef,
    Document,
    Field,
    FootnoteRef,
    ImageInline,
    LineBreak,
    Link,
    ListBlock,
    Paragraph,
    Tab,
    Table,
    TextRun,
)
from rtfstruct.options import ParserOptions
from rtfstruct.reader import parse_rtf, read_rtf


def document_from_input(data: bytes | str | Path | Document, options: ParserOptions | None = None) -> Document:
    """Convert common integration input types into a document AST."""
    if isinstance(data, Document):
        return data
    if isinstance(data, Path):
        return read_rtf(data, options=options)
    if isinstance(data, str) and not data.lstrip().startswith("{\\rtf") and _is_existing_path(data):
        return read_rtf(data, options=options)
    return parse_rtf(data, options=options)


def _is_existing_path(value: str) -> bool:
    """Return whether `value` safely names an existing filesystem path."""
    try:
        return Path(value).exists()
    except OSError:
        return False


def inline_text(inline: object) -> str:
    """Extract readable text from an inline AST node."""
    if isinstance(inline, TextRun):
        return inline.text
    if isinstance(inline, Link):
        return "".join(inline_text(child) for child in inline.children)
    if isinstance(inline, Field):
        return "".join(inline_text(child) for child in inline.children)
    if isinstance(inline, FootnoteRef):
        return inline.label or inline.id
    if isinstance(inline, AnnotationRef):
        return inline.label or inline.id
    if isinstance(inline, ImageInline):
        return inline.alt_text or inline.id
    if isinstance(inline, LineBreak):
        return "\n"
    if isinstance(inline, Tab):
        return "\t"
    return ""


def block_text(block: object) -> str:
    """Extract readable text from a block AST node."""
    if isinstance(block, Paragraph):
        return "".join(inline_text(child) for child in block.children)
    if isinstance(block, ListBlock):
        return "\n".join(block_text(child_block) for item in block.items for child_block in item.blocks)
    if isinstance(block, Table):
        rows: list[list[str]] = [["" for _ in range(block.col_count)] for _ in range(block.row_count)]
        for cell in block.cells:
            if cell.row < block.row_count and cell.col < block.col_count:
                rows[cell.row][cell.col] = " ".join(block_text(child) for child in cell.blocks)
        return "\n".join("\t".join(row) for row in rows)
    return ""
