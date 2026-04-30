# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""MarkItDown-style Markdown conversion helpers.

This module does not import MarkItDown directly. It provides a tiny adapter
surface that can be wrapped by a MarkItDown plugin without making MarkItDown a
runtime dependency of the core library.
"""

from __future__ import annotations

from pathlib import Path

from rtfstruct.ast import Document
from rtfstruct.integrations._shared import document_from_input
from rtfstruct.options import MarkdownOptions, ParserOptions


def convert_rtf_to_markdown(
    data: bytes | str | Path | Document,
    *,
    parser_options: ParserOptions | None = None,
    markdown_options: MarkdownOptions | None = None,
) -> str:
    """Convert RTF input or an existing document AST to Markdown."""
    document = document_from_input(data, options=parser_options)
    return document.to_markdown(options=markdown_options)


class RtfstructMarkdownConverter:
    """Small converter object suitable for wrapping in a MarkItDown plugin."""

    def __init__(
        self,
        *,
        parser_options: ParserOptions | None = None,
        markdown_options: MarkdownOptions | None = None,
    ) -> None:
        """Create a converter with reusable parser and Markdown options."""
        self.parser_options = parser_options
        self.markdown_options = markdown_options

    def convert(self, data: bytes | str | Path | Document) -> str:
        """Convert supported RTF input to Markdown."""
        return convert_rtf_to_markdown(
            data,
            parser_options=self.parser_options,
            markdown_options=self.markdown_options,
        )
