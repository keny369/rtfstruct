# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""JSON exporter for the document AST.

The exporter consumes AST nodes only. It does not inspect RTF source text or
perform parser recovery.
"""

from __future__ import annotations

from base64 import b64encode
from dataclasses import asdict, is_dataclass
from typing import Any

from rtfstruct.ast import (
    Annotation,
    AnnotationRef,
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
    Paragraph,
    SourceSpan,
    Tab,
    Table,
    TableCell,
    TextRun,
    TextStyle,
)
from rtfstruct.diagnostics import Diagnostic
from rtfstruct.options import JsonOptions


class JsonExporter:
    """Export a `Document` to deterministic JSON-compatible dictionaries."""

    def __init__(self, options: JsonOptions | None = None) -> None:
        """Create a JSON exporter."""
        self.options = options or JsonOptions()

    def export(self, document: Document) -> dict[str, object]:
        """Export `document` to JSON-compatible data."""
        data: dict[str, object] = {
            "type": "document",
            "metadata": self._clean(asdict(document.metadata)),
            "styles": self._stylesheet(document),
            "blocks": [self._block(block) for block in document.blocks],
            "footnotes": {key: self._footnote(value) for key, value in sorted(document.footnotes.items())},
            "annotations": {
                key: self._annotation(value) for key, value in sorted(document.annotations.items())
            },
            "images": {key: self._image(value) for key, value in sorted(document.images.items())},
        }
        if self.options.include_diagnostics:
            data["diagnostics"] = [self._diagnostic(item) for item in document.diagnostics]
        return self._clean(data)

    def _stylesheet(self, document: Document) -> dict[str, object]:
        """Export stylesheet definitions."""
        return {
            "paragraph_styles": {
                key: self._clean(asdict(value)) for key, value in sorted(document.styles.paragraph_styles.items())
            },
            "text_styles": {
                key: self._style(value) for key, value in sorted(document.styles.text_styles.items())
            },
        }

    def _block(self, block: object) -> dict[str, object]:
        """Export a block node."""
        if isinstance(block, Paragraph):
            return self._clean(
                {
                    "type": "paragraph",
                    "span": self._span(block.span),
                    "style": self._clean(asdict(block.style)),
                    "children": [self._inline(child) for child in block.children],
                }
            )
        if isinstance(block, ListBlock):
            return self._clean(
                {
                    "type": "list",
                    "ordered": block.ordered,
                    "list_id": block.list_id,
                    "items": [self._list_item(item) for item in block.items],
                }
            )
        if isinstance(block, Table):
            return self._clean(
                {
                    "type": "table",
                    "row_count": block.row_count,
                    "col_count": block.col_count,
                    "cells": [self._table_cell(cell) for cell in block.cells],
                }
            )
        raise TypeError(f"Unsupported block type: {type(block)!r}")

    def _table_cell(self, cell: TableCell) -> dict[str, object]:
        """Export a resolved table cell."""
        return self._clean(
            {
                "row": cell.row,
                "col": cell.col,
                "rowspan": cell.rowspan,
                "colspan": cell.colspan,
                "width_twips": cell.width_twips,
                "blocks": [self._block(block) for block in cell.blocks],
            }
        )

    def _list_item(self, item: ListItem) -> dict[str, object]:
        """Export a list item."""
        return self._clean(
            {
                "type": "list_item",
                "level": item.level,
                "marker": item.marker,
                "blocks": [self._block(block) for block in item.blocks],
            }
        )

    def _inline(self, inline: object) -> dict[str, object]:
        """Export an inline node."""
        if isinstance(inline, TextRun):
            return self._clean(
                {
                    "type": "text",
                    "text": inline.text,
                    "span": self._span(inline.span),
                    "style": self._style(inline.style),
                }
            )
        if isinstance(inline, Link):
            return self._clean(
                {
                    "type": "link",
                    "target": inline.target,
                    "span": self._span(inline.span),
                    "instruction": inline.instruction,
                    "children": [self._inline(child) for child in inline.children],
                }
            )
        if isinstance(inline, Field):
            return self._clean(
                {
                    "type": "field",
                    "instruction": inline.instruction,
                    "span": self._span(inline.span),
                    "children": [self._inline(child) for child in inline.children],
                }
            )
        if isinstance(inline, FootnoteRef):
            return self._clean(
                {"type": "footnote_ref", "id": inline.id, "label": inline.label, "span": self._span(inline.span)}
            )
        if isinstance(inline, AnnotationRef):
            return self._clean(
                {
                    "type": "annotation_ref",
                    "id": inline.id,
                    "label": inline.label,
                    "span": self._span(inline.span),
                }
            )
        if isinstance(inline, ImageInline):
            return self._clean(
                {"type": "image", "id": inline.id, "alt_text": inline.alt_text, "span": self._span(inline.span)}
            )
        if isinstance(inline, LineBreak):
            return self._clean({"type": "line_break", "span": self._span(inline.span)})
        if isinstance(inline, Tab):
            return self._clean({"type": "tab", "span": self._span(inline.span)})
        raise TypeError(f"Unsupported inline type: {type(inline)!r}")

    def _diagnostic(self, diagnostic: Diagnostic) -> dict[str, object]:
        """Export a diagnostic record."""
        return self._clean(asdict(diagnostic))

    def _footnote(self, footnote: Footnote) -> dict[str, object]:
        """Export a footnote."""
        return {
            "type": "footnote",
            "id": footnote.id,
            "blocks": [self._block(block) for block in footnote.blocks],
        }

    def _annotation(self, annotation: Annotation) -> dict[str, object]:
        """Export an annotation."""
        return self._clean(
            {
                "type": "annotation",
                "id": annotation.id,
                "author": annotation.author,
                "blocks": [self._block(block) for block in annotation.blocks],
            }
        )

    def _image(self, image: Image) -> dict[str, object]:
        """Export image metadata and optional payload."""
        data = {
            "type": "image",
            "id": image.id,
            "content_type": image.content_type,
            "path": image.path,
            "alt_text": image.alt_text,
            "width_twips": image.width_twips,
            "height_twips": image.height_twips,
            "goal_width_twips": image.goal_width_twips,
            "goal_height_twips": image.goal_height_twips,
            "scale_x": image.scale_x,
            "scale_y": image.scale_y,
        }
        if self.options.include_image_data and image.data is not None:
            data["data_base64"] = b64encode(image.data).decode("ascii")
        return self._clean(data)

    def _style(self, style: TextStyle) -> dict[str, object]:
        """Export compact inline style data.

        Default false booleans are omitted so an unstyled run serializes as an
        empty style object while active formatting remains explicit.
        """
        data = asdict(style)
        if self.options.include_nulls:
            return data
        return {
            key: self._clean(value)
            for key, value in data.items()
            if value is not None and value is not False
        }

    def _span(self, span: SourceSpan | None) -> dict[str, int] | None:
        """Export a source span if present."""
        if span is None:
            return None
        return {"start": span.start, "end": span.end}

    def _clean(self, value: Any) -> Any:
        """Remove null values unless configured otherwise."""
        if self.options.include_nulls:
            return value
        if is_dataclass(value):
            value = asdict(value)
        if isinstance(value, dict):
            return {key: self._clean(item) for key, item in value.items() if item is not None}
        if isinstance(value, list):
            return [self._clean(item) for item in value]
        return value
