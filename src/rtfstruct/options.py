# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Configuration objects for parsing and exporting.

The options in this module are intentionally small at the skeleton stage. They
define public API shape and safety defaults used by the reader and future
exporters.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ParserOptions:
    """Parser configuration.

    Attributes:
        recover: Whether recoverable malformed input should produce diagnostics
            instead of raising.
        preserve_unknown_destinations: Whether readable unknown destinations may
            be preserved later as raw AST payloads.
        extract_images: Whether image payload extraction is requested.
        track_spans: Whether source spans should be attached where practical.
        max_group_depth: Maximum allowed RTF group nesting depth.
        max_document_chars: Maximum emitted document characters.
        max_diagnostics: Maximum diagnostics retained on the document.
    """

    recover: bool = True
    preserve_unknown_destinations: bool = False
    extract_images: bool = True
    track_spans: bool = False
    max_group_depth: int = 1000
    max_document_chars: int = 100_000_000
    max_diagnostics: int = 10_000


@dataclass(frozen=True, slots=True)
class JsonOptions:
    """JSON export configuration."""

    include_nulls: bool = False
    include_diagnostics: bool = True
    include_image_data: bool = False


@dataclass(frozen=True, slots=True)
class MarkdownOptions:
    """Markdown export configuration placeholder."""

    preserve_colors: bool = True
    preserve_fonts: bool = False
    preserve_font_sizes: bool = False
    annotations: str = "blockquote"
    complex_tables: str = "html"
