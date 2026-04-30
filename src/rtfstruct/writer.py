# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""RTF writer for the document AST."""

from __future__ import annotations

from pathlib import Path

from rtfstruct.ast import (
    AnnotationRef,
    Block,
    Color,
    Document,
    Field,
    FootnoteRef,
    ImageInline,
    Inline,
    LineBreak,
    Link,
    ListBlock,
    ListItem,
    Paragraph,
    Tab,
    Table,
    TableCell,
    TextRun,
)
from rtfstruct.utils.escaping import escape_rtf_text


class RtfWriter:
    """Write supported AST nodes as deterministic RTF."""

    def __init__(self, document: Document) -> None:
        """Create a writer for a document."""
        self.document = document
        self._font_ids: dict[str, int] = {}
        self._color_ids: dict[Color, int] = {}
        self._list_ids: dict[int, int] = {}

    def export(self) -> str:
        """Return the document as an RTF string."""
        self._collect_resources()
        self._collect_list_ids()
        parts = [r"{\rtf1\ansi"]
        parts.append(self._font_table())
        color_table = self._color_table()
        if color_table:
            parts.append(color_table)
        list_tables = self._list_tables()
        if list_tables:
            parts.append(list_tables)
        info = self._info_group()
        if info:
            parts.append(info)
        for block in self.document.blocks:
            parts.append(self._block(block))
        parts.append("}")
        return "".join(parts)

    def _collect_list_ids(self) -> None:
        """Assign deterministic paragraph-facing ids to list blocks."""
        self._list_ids = {}
        next_id = 1
        for block in self.document.blocks:
            if isinstance(block, ListBlock):
                list_id = block.list_id if block.list_id is not None else next_id
                self._list_ids[id(block)] = list_id
                next_id = max(next_id, list_id + 1)

    def _collect_resources(self) -> None:
        """Collect font and colour resources before writing the header."""
        for block in self.document.blocks:
            self._collect_block_resources(block)
        for footnote in self.document.footnotes.values():
            for block in footnote.blocks:
                self._collect_block_resources(block)
        for annotation in self.document.annotations.values():
            for block in annotation.blocks:
                self._collect_block_resources(block)

    def _collect_block_resources(self, block: Block) -> None:
        """Collect resources used by one block."""
        if isinstance(block, Paragraph):
            for inline in block.children:
                self._collect_inline_resources(inline)
        elif isinstance(block, ListBlock):
            for item in block.items:
                for child in item.blocks:
                    self._collect_block_resources(child)
        elif isinstance(block, Table):
            for cell in block.cells:
                for child in cell.blocks:
                    self._collect_block_resources(child)

    def _collect_inline_resources(self, inline: Inline) -> None:
        """Collect resources used by one inline node."""
        if isinstance(inline, TextRun):
            style = inline.style
            if style.font_family is not None and style.font_family not in self._font_ids:
                self._font_ids[style.font_family] = len(self._font_ids) + 1
            if style.foreground is not None:
                self._ensure_color(style.foreground)
            if style.background is not None:
                self._ensure_color(style.background)
        elif isinstance(inline, (Link, Field)):
            for child in inline.children:
                self._collect_inline_resources(child)

    def _ensure_color(self, color: Color) -> int:
        """Return a deterministic colour-table id for a colour."""
        existing = self._color_ids.get(color)
        if existing is not None:
            return existing
        color_id = len(self._color_ids) + 1
        self._color_ids[color] = color_id
        return color_id

    def _font_table(self) -> str:
        """Emit a font table."""
        entries = [r"{\f0 Times New Roman;}"]
        for font_name, font_id in sorted(self._font_ids.items(), key=lambda item: item[1]):
            entries.append(r"{\f" + str(font_id) + " " + escape_rtf_text(font_name) + ";}")
        return r"{\fonttbl" + "".join(entries) + "}"

    def _color_table(self) -> str:
        """Emit a colour table if non-default colours are used."""
        if not self._color_ids:
            return ""
        entries = [";"]
        for color, _color_id in sorted(self._color_ids.items(), key=lambda item: item[1]):
            entries.append(r"\red" + str(color.red) + r"\green" + str(color.green) + r"\blue" + str(color.blue) + ";")
        return r"{\colortbl" + "".join(entries) + "}"

    def _list_tables(self) -> str:
        """Emit list definition and override tables for list blocks."""
        if not self._list_ids:
            return ""
        list_entries: list[str] = []
        override_entries: list[str] = []
        for block in self.document.blocks:
            if not isinstance(block, ListBlock):
                continue
            list_id = self._list_ids[id(block)]
            level_kind = 0 if block.ordered else 23
            list_entries.append(
                r"{\list{\listlevel\levelnfc"
                + str(level_kind)
                + r"}\listid"
                + str(list_id)
                + "}"
            )
            override_entries.append(
                r"{\listoverride\listid" + str(list_id) + r"\ls" + str(list_id) + "}"
            )
        return r"{\*\listtable" + "".join(list_entries) + "}" + r"{\*\listoverridetable" + "".join(override_entries) + "}"

    def _info_group(self) -> str:
        """Emit document metadata."""
        metadata = self.document.metadata
        fields = [
            ("title", metadata.title),
            ("subject", metadata.subject),
            ("author", metadata.author),
            ("keywords", metadata.keywords),
            ("doccomm", metadata.comment),
            ("company", metadata.company),
        ]
        parts = [r"{\info"]
        for key, value in fields:
            if value:
                parts.append("{\\" + key + " " + escape_rtf_text(value) + "}")
        parts.append("}")
        return "".join(parts) if len(parts) > 2 else ""

    def _block(self, block: Block) -> str:
        """Emit one block."""
        if isinstance(block, Paragraph):
            return self._paragraph(block)
        if isinstance(block, ListBlock):
            return "".join(self._list_item(block, item_index, item) for item_index, item in enumerate(block.items, 1))
        if isinstance(block, Table):
            return self._table(block)
        return ""

    def _paragraph(
        self,
        paragraph: Paragraph,
        *,
        in_table: bool = False,
        list_identity: int | None = None,
        list_level: int | None = None,
    ) -> str:
        """Emit a paragraph."""
        controls = [r"\pard"]
        style = paragraph.style
        resolved_list_identity = list_identity if list_identity is not None else style.list_identity
        resolved_list_level = list_level if list_level is not None else style.list_level
        if resolved_list_identity is not None:
            controls.append(r"\ls" + str(resolved_list_identity))
        if resolved_list_level is not None:
            controls.append(r"\ilvl" + str(resolved_list_level))
        if style.alignment == "center":
            controls.append(r"\qc")
        elif style.alignment == "right":
            controls.append(r"\qr")
        elif style.alignment == "justify":
            controls.append(r"\qj")
        elif style.alignment == "left":
            controls.append(r"\ql")
        if style.left_indent_twips is not None:
            controls.append(r"\li" + str(style.left_indent_twips))
        if style.right_indent_twips is not None:
            controls.append(r"\ri" + str(style.right_indent_twips))
        if style.first_line_indent_twips is not None:
            controls.append(r"\fi" + str(style.first_line_indent_twips))
        if style.space_before_twips is not None:
            controls.append(r"\sb" + str(style.space_before_twips))
        if style.space_after_twips is not None:
            controls.append(r"\sa" + str(style.space_after_twips))
        if in_table:
            controls.append(r"\intbl")
        return "".join(controls) + " " + "".join(self._inline(child) for child in paragraph.children)

    def _list_item(self, block: ListBlock, item_index: int, item: ListItem) -> str:
        """Emit a list item as a stamped paragraph."""
        _ = item_index
        if not item.blocks:
            return ""
        output = []
        list_id = self._list_ids[id(block)]
        for child in item.blocks:
            if isinstance(child, Paragraph):
                output.append(self._paragraph(child, list_identity=list_id, list_level=item.level) + r"\par ")
            else:
                output.append(self._block(child))
        return "".join(output)

    def _inline(self, inline: Inline) -> str:
        """Emit one inline node."""
        if isinstance(inline, TextRun):
            return self._text_run(inline)
        if isinstance(inline, Link):
            text = "".join(self._inline(child) for child in inline.children)
            return r"{\field{\*\fldinst HYPERLINK " + '"' + escape_rtf_text(inline.target) + '"' + r"}{\fldrslt " + text + "}}"
        if isinstance(inline, Field):
            text = "".join(self._inline(child) for child in inline.children)
            return r"{\field{\*\fldinst " + escape_rtf_text(inline.instruction) + r"}{\fldrslt " + text + "}}"
        if isinstance(inline, FootnoteRef):
            footnote = self.document.footnotes.get(inline.id)
            if footnote is None:
                return ""
            return r"{\footnote " + "".join(self._block(block) for block in footnote.blocks) + "}"
        if isinstance(inline, AnnotationRef):
            annotation = self.document.annotations.get(inline.id)
            if annotation is None:
                return ""
            return r"{\annotation " + "".join(self._block(block) for block in annotation.blocks) + "}"
        if isinstance(inline, ImageInline):
            return self._image_inline(inline)
        if isinstance(inline, LineBreak):
            return r"\line "
        if isinstance(inline, Tab):
            return r"\tab "
        return ""

    def _text_run(self, run: TextRun) -> str:
        """Emit a styled text run."""
        controls = []
        style = run.style
        if style.bold:
            controls.append(r"\b")
        if style.italic:
            controls.append(r"\i")
        if style.underline:
            controls.append(r"\ul")
        if style.strikethrough:
            controls.append(r"\strike")
        if style.superscript:
            controls.append(r"\super")
        if style.subscript:
            controls.append(r"\sub")
        if style.font_size_half_points is not None:
            controls.append(r"\fs" + str(style.font_size_half_points))
        if style.font_family is not None:
            controls.append(r"\f" + str(self._font_ids[style.font_family]))
        if style.foreground is not None:
            controls.append(r"\cf" + str(self._color_ids[style.foreground]))
        if style.background is not None:
            controls.append(r"\highlight" + str(self._color_ids[style.background]))
        if not controls:
            return escape_rtf_text(run.text)
        return "{" + "".join(controls) + " " + escape_rtf_text(run.text) + "}"

    def _table(self, table: Table) -> str:
        """Emit an RTF table, including simple merge metadata."""
        rows = []
        for row_index in range(table.row_count):
            rows.append(self._table_row(table, row_index))
        return "".join(rows)

    def _table_row(self, table: Table, row_index: int) -> str:
        """Emit one table row."""
        parts = [r"\trowd"]
        current_boundary = 0
        slots = [self._table_slot(table, row_index, col_index) for col_index in range(table.col_count)]
        for cell, kind in slots:
            width = self._table_slot_width(cell)
            current_boundary += width
            if kind == "anchor" and cell is not None and cell.colspan > 1:
                parts.append(r"\clmgf")
            elif kind == "h_continuation":
                parts.append(r"\clmrg")
            if kind == "anchor" and cell is not None and cell.rowspan > 1:
                parts.append(r"\clvmgf")
            elif kind == "v_continuation":
                parts.append(r"\clvmrg")
            parts.append(r"\cellx" + str(current_boundary))
        for cell, kind in slots:
            cell_content = ""
            if cell is not None and kind == "anchor":
                cell_content = "".join(
                    self._paragraph(block, in_table=True) if isinstance(block, Paragraph) else self._block(block)
                    for block in cell.blocks
                )
            parts.append(cell_content + r"\cell ")
        parts.append(r"\row ")
        return "".join(parts)

    def _table_slot(self, table: Table, row: int, col: int) -> tuple[TableCell | None, str]:
        """Return the cell occupying a coordinate and its writer slot kind."""
        for cell in table.cells:
            if cell.row == row and cell.col == col:
                return cell, "anchor"
        for cell in table.cells:
            in_rows = cell.row <= row < cell.row + cell.rowspan
            in_cols = cell.col <= col < cell.col + cell.colspan
            if not in_rows or not in_cols:
                continue
            if row == cell.row:
                return cell, "h_continuation"
            return cell, "v_continuation"
        return None, "empty"

    def _table_slot_width(self, cell: TableCell | None) -> int:
        """Return a per-column width for a table slot."""
        if cell is None:
            return 1000
        if cell.width_twips is None:
            return 1000
        return max(1, cell.width_twips // max(1, cell.colspan))

    def _image_inline(self, inline: ImageInline) -> str:
        """Emit an image destination for an inline image reference."""
        image = self.document.images.get(inline.id)
        if image is None:
            return ""
        control = {
            "image/png": r"\pngblip",
            "image/jpeg": r"\jpegblip",
            "image/emf": r"\emfblip",
            "image/wmf": r"\wmetafile",
        }.get(image.content_type, "")
        parts = [r"{\pict", control]
        for control_word, value in [
            ("picw", image.width_twips),
            ("pich", image.height_twips),
            ("picwgoal", image.goal_width_twips),
            ("pichgoal", image.goal_height_twips),
            ("picscalex", image.scale_x),
            ("picscaley", image.scale_y),
        ]:
            if value is not None:
                parts.append("\\" + control_word + str(value))
        if image.data:
            parts.append(" " + image.data.hex().upper())
        parts.append("}")
        return "".join(parts)


def to_rtf(document: Document) -> str:
    """Export a document AST to RTF.

    Args:
        document: Document AST to export.

    Returns:
        RTF document text.
    """
    return RtfWriter(document).export()


def write_rtf(document: Document, path: str | Path) -> None:
    """Write a document AST to an RTF file.

    Args:
        document: Document AST to export.
        path: Destination file path.
    """
    Path(path).write_text(to_rtf(document), encoding="utf-8")
