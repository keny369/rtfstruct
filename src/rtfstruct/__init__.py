# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Public API for rtfstruct.

The package exposes a small documented surface for reading RTF into the AST and
exporting supported structures. Internal modules may evolve while the project is
pre-1.0.
"""

from __future__ import annotations

from rtfstruct.ast import (
    Annotation,
    AnnotationRef,
    Color,
    Document,
    Field,
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
    SourceSpan,
    StyleSheet,
    Tab,
    Table,
    TableCell,
    TextRun,
    TextStyle,
)
from rtfstruct.diagnostics import Diagnostic, Severity
from rtfstruct.exceptions import RtfError, RtfSyntaxError
from rtfstruct.options import JsonOptions, MarkdownOptions, ParserOptions
from rtfstruct.reader import parse_rtf, read_rtf
from rtfstruct.writer import to_rtf, write_rtf

__all__ = [
    "Diagnostic",
    "Document",
    "Annotation",
    "AnnotationRef",
    "Color",
    "Field",
    "Footnote",
    "FootnoteRef",
    "Image",
    "ImageInline",
    "JsonOptions",
    "LineBreak",
    "Link",
    "ListBlock",
    "ListItem",
    "MarkdownOptions",
    "Metadata",
    "Paragraph",
    "ParagraphStyle",
    "ParserOptions",
    "RtfError",
    "RtfSyntaxError",
    "Severity",
    "SourceSpan",
    "StyleSheet",
    "Tab",
    "Table",
    "TableCell",
    "TextRun",
    "TextStyle",
    "parse_rtf",
    "read_rtf",
    "to_markdown",
    "to_rtf",
    "write_rtf",
]


def to_markdown(document: Document, options: MarkdownOptions | None = None) -> str:
    """Export a document AST to Markdown.

    Args:
        document: Document AST to export.
        options: Optional Markdown export configuration.

    Returns:
        Markdown string.
    """
    return document.to_markdown(options=options)
