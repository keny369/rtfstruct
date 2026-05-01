# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Markdown exporter.

Markdown is a lossy backend and must not shape the AST. This skeleton exporter
exists for API completeness while JSON and parser behavior are still stabilizing.
"""

from __future__ import annotations

from html import escape as escape_html

from rtfstruct.ast import (
    AnnotationRef,
    Color,
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
    TableCell,
    TextRun,
)
from rtfstruct.options import MarkdownOptions
from rtfstruct.utils.escaping import escape_markdown_text


class MarkdownExporter:
    """Export supported AST nodes to readable Markdown."""

    def __init__(self, options: MarkdownOptions | None = None) -> None:
        """Create a Markdown exporter."""
        self.options = options or MarkdownOptions()
        self._images = {}
        self._document_annotations = {}

    def export(self, document: Document) -> str:
        """Export a document to Markdown text."""
        self._images = document.images
        self._document_annotations = document.annotations
        paragraphs: list[str] = []
        for block in document.blocks:
            if isinstance(block, Paragraph):
                paragraphs.append("".join(self._inline(child) for child in block.children))
            elif isinstance(block, ListBlock):
                paragraphs.append(self._list(block))
            elif isinstance(block, Table):
                paragraphs.append(self._table(block))
        footnotes = self._footnotes(document)
        if footnotes:
            paragraphs.extend(footnotes)
        annotations = self._annotations(document)
        if annotations:
            paragraphs.extend(annotations)
        return "\n\n".join(paragraphs)

    def _inline(self, inline: object) -> str:
        """Export a supported inline node."""
        if isinstance(inline, TextRun):
            return self._text_run(inline)
        if isinstance(inline, Link):
            text = "".join(self._inline(child) for child in inline.children)
            target = inline.target.replace(")", "%29")
            return f"[{text}]({target})"
        if isinstance(inline, Field):
            return "".join(self._inline(child) for child in inline.children)
        if isinstance(inline, FootnoteRef):
            label = inline.label or inline.id
            return f"[^{label}]"
        if isinstance(inline, AnnotationRef):
            if self.options.annotations == "omit":
                return ""
            if self.options.annotations == "inline":
                text = self._annotation_text(inline.id)
                return f"[note: {text}]" if text else ""
            if self.options.annotations == "html_comment":
                return ""
            label = inline.label or inline.id
            return f"[note {label}]"
        if isinstance(inline, ImageInline):
            image = self._images.get(inline.id)
            if image is not None and image.path:
                alt_text = escape_markdown_text(inline.alt_text or image.alt_text or "image")
                return f"![{alt_text}]({image.path})"
            if image is not None:
                parts = [f"Image: {image.content_type or 'unknown'}"]
                if image.goal_width_twips is not None:
                    parts.append(f"width={image.goal_width_twips}twips")
                if image.goal_height_twips is not None:
                    parts.append(f"height={image.goal_height_twips}twips")
                return "[" + ", ".join(parts) + "]"
            return f"[Image: {inline.id}]"
        if isinstance(inline, LineBreak):
            return "<br>"
        if isinstance(inline, Tab):
            return "    "
        return ""

    def _text_run(self, run: TextRun) -> str:
        """Export a text run with basic Markdown formatting."""
        text = escape_markdown_text(run.text)
        style = run.style
        if style.bold and style.italic:
            text = f"***{text}***"
        elif style.bold:
            text = f"**{text}**"
        elif style.italic:
            text = f"*{text}*"
        if style.strikethrough:
            text = f"~~{text}~~"
        if style.underline:
            text = f"<u>{text}</u>"
        if style.superscript:
            text = f"<sup>{text}</sup>"
        if style.subscript:
            text = f"<sub>{text}</sub>"
        text = self._style_span(text, run)
        return text

    def _style_span(self, text: str, run: TextRun) -> str:
        """Wrap text in a CSS span for style details Markdown cannot express."""
        declarations: list[str] = []
        style = run.style
        if self.options.preserve_colors and style.foreground is not None:
            declarations.append(f"color: {self._css_color(style.foreground)};")
        if self.options.preserve_colors and style.background is not None:
            declarations.append(f"background-color: {self._css_color(style.background)};")
        if self.options.preserve_fonts and style.font_family is not None:
            font_family = escape_html(style.font_family, quote=True)
            declarations.append(f"font-family: {font_family};")
        if self.options.preserve_font_sizes and style.font_size_half_points is not None:
            declarations.append(f"font-size: {self._half_points_to_css_points(style.font_size_half_points)};")
        if not declarations:
            return text
        return f'<span style="{" ".join(declarations)}">{text}</span>'

    def _css_color(self, color: Color) -> str:
        """Return a CSS hex color string."""
        return f"#{color.red:02x}{color.green:02x}{color.blue:02x}"

    def _half_points_to_css_points(self, value: int) -> str:
        """Return a CSS point value from RTF half-points."""
        points = value / 2
        if points.is_integer():
            return f"{int(points)}pt"
        return f"{points:g}pt"

    def _list(self, block: ListBlock) -> str:
        """Export a list block to deterministic Markdown."""
        lines: list[str] = []
        for index, item in enumerate(block.items, start=1):
            marker = f"{index}." if block.ordered else "-"
            indent = "  " * item.level
            text = " ".join(
                "".join(self._inline(child) for child in child_block.children)
                for child_block in item.blocks
                if isinstance(child_block, Paragraph)
            )
            lines.append(f"{indent}{marker} {text}")
        return "\n".join(lines)

    def _table(self, table: Table) -> str:
        """Export a simple table as GitHub-Flavoured Markdown."""
        if not self._is_simple_table(table):
            if self.options.complex_tables == "omit":
                return ""
            if self.options.complex_tables == "gfm":
                return self._gfm_table(table)
            if self.options.complex_tables != "html":
                raise ValueError(f"Unsupported complex table mode: {self.options.complex_tables!r}.")
            return self._html_table(table)
        return self._gfm_table(table)

    def _gfm_table(self, table: Table) -> str:
        """Export a table as flattened GitHub-Flavoured Markdown."""
        rows: list[list[str]] = [["" for _ in range(table.col_count)] for _ in range(table.row_count)]
        for cell in table.cells:
            rows[cell.row][cell.col] = self._cell_markdown_text(cell)
        if not rows:
            return ""
        header = rows[0]
        separator = ["---" for _ in header]
        body = rows[1:]
        return "\n".join(
            [
                self._table_row(header),
                self._table_row(separator),
                *(self._table_row(row) for row in body),
            ]
        )

    def _is_simple_table(self, table: Table) -> bool:
        """Return whether a table can be represented as GFM."""
        return all(self._is_simple_cell(cell) for cell in table.cells)

    def _is_simple_cell(self, cell: TableCell) -> bool:
        """Return whether a cell can be represented in GFM table syntax."""
        return cell.rowspan == 1 and cell.colspan == 1 and len(cell.blocks) <= 1 and all(
            isinstance(block, Paragraph) for block in cell.blocks
        )

    def _cell_markdown_text(self, cell: TableCell) -> str:
        """Return escaped Markdown text for a simple table cell."""
        return self._cell_plain_text(cell).replace("|", "\\|").replace("\n", " ")

    def _cell_plain_text(self, cell: TableCell) -> str:
        """Return readable cell text."""
        if not cell.blocks:
            return ""
        return "\n\n".join(
            "".join(self._inline(child) for child in block.children)
            for block in cell.blocks
            if isinstance(block, Paragraph)
        )

    def _table_row(self, values: list[str]) -> str:
        """Format one Markdown table row."""
        return "| " + " | ".join(values) + " |"

    def _html_table(self, table: Table) -> str:
        """Export a complex table as minimal HTML."""
        by_position = {(cell.row, cell.col): cell for cell in table.cells}
        covered: set[tuple[int, int]] = set()
        rows = ["<table>"]
        for row in range(table.row_count):
            rows.append("  <tr>")
            for col in range(table.col_count):
                if (row, col) in covered:
                    continue
                cell = by_position.get((row, col))
                if cell is None:
                    rows.append("    <td></td>")
                    continue
                for covered_row in range(row, row + cell.rowspan):
                    for covered_col in range(col, col + cell.colspan):
                        if (covered_row, covered_col) != (row, col):
                            covered.add((covered_row, covered_col))
                attrs = []
                if cell.rowspan > 1:
                    attrs.append(f'rowspan="{cell.rowspan}"')
                if cell.colspan > 1:
                    attrs.append(f'colspan="{cell.colspan}"')
                attr_text = " " + " ".join(attrs) if attrs else ""
                rows.append(f"    <td{attr_text}>{escape_html(self._cell_plain_text(cell))}</td>")
            rows.append("  </tr>")
        rows.append("</table>")
        return "\n".join(rows)

    def _annotations(self, document: Document) -> list[str]:
        """Export annotations according to configured annotation mode."""
        if self.options.annotations in {"omit", "inline"}:
            return []
        definitions: list[str] = []
        for annotation_id, annotation in sorted(document.annotations.items()):
            label = annotation_id.removeprefix("ann") or annotation_id
            text = self._annotation_text(annotation_id)
            if self.options.annotations == "html_comment":
                definitions.append(f"<!-- Annotation {label}: {escape_html(text)} -->")
            else:
                definitions.append(f"> [!NOTE] Annotation {label}: {text}")
        return definitions

    def _annotation_text(self, annotation_id: str) -> str:
        """Return readable annotation text for configured annotation output."""
        annotation = self._document_annotations.get(annotation_id)
        if annotation is None:
            return ""
        return "\n\n".join(
            "".join(self._inline(child) for child in block.children)
            for block in annotation.blocks
            if isinstance(block, Paragraph)
        )

    def _footnotes(self, document: Document) -> list[str]:
        """Export Markdown footnote definitions."""
        definitions: list[str] = []
        for footnote_id, footnote in sorted(document.footnotes.items()):
            label = footnote_id.removeprefix("fn") or footnote_id
            text = "\n\n".join(
                "".join(self._inline(child) for child in block.children)
                for block in footnote.blocks
                if isinstance(block, Paragraph)
            )
            definitions.append(f"[^{label}]: {text}")
        return definitions

