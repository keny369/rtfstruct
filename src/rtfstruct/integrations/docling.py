# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Docling-style dictionary adapter for rtfstruct documents.

The returned dictionary is intentionally dependency-free. It preserves enough
shape for downstream Docling integration experiments without importing Docling.
"""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from rtfstruct.ast import Document, ListBlock, Paragraph, Table
from rtfstruct.integrations._shared import block_text, document_from_input
from rtfstruct.options import ParserOptions


def to_docling_dict(data: bytes | str | Path | Document, options: ParserOptions | None = None) -> dict[str, object]:
    """Convert RTF input or a document AST to a Docling-style dictionary."""
    document = document_from_input(data, options=options)
    return {
        "schema_name": "rtfstruct.docling",
        "schema_version": "0.1",
        "metadata": asdict(document.metadata),
        "texts": [_text_block(block, index) for index, block in enumerate(document.blocks)],
        "diagnostics": [
            {
                "code": diagnostic.code,
                "message": diagnostic.message,
                "severity": diagnostic.severity.value,
                "offset": diagnostic.offset,
            }
            for diagnostic in document.diagnostics
        ],
    }


def _text_block(block: object, index: int) -> dict[str, object]:
    """Return a compact text block representation for Docling experiments."""
    block_type = "text"
    if isinstance(block, Paragraph):
        block_type = "paragraph"
    elif isinstance(block, ListBlock):
        block_type = "list"
    elif isinstance(block, Table):
        block_type = "table"
    return {
        "index": index,
        "type": block_type,
        "text": block_text(block),
    }
