# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Mutable parser state for the RTF reader.

This module owns the compact state object used by the parser state machine. It
does not tokenize input or decide control-word semantics; lexer tokens come from
`lexer.py`, and semantic dispatch lives in `control_words.py`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, replace

from rtfstruct.ast import (
    Annotation,
    AnnotationRef,
    Block,
    Color,
    Field,
    Footnote,
    FootnoteRef,
    Image,
    ImageInline,
    Inline,
    Link,
    Metadata,
    Paragraph,
    ParagraphStyle,
    SourceSpan,
    TextRun,
    TextStyle,
    TextStyleInterner,
)
from rtfstruct.diagnostics import Diagnostics, Severity
from rtfstruct.destinations import Destination
from rtfstruct.options import ParserOptions
from rtfstruct.tables import TableBuilder
from rtfstruct.tokens import Token


_HYPERLINK_RE = re.compile(r'^\s*HYPERLINK\s+"([^"]*)"', re.IGNORECASE)
_CHARSET_CODEPAGES = {
    0: None,
    1: None,
    2: None,
    77: "mac_roman",
    128: "shift_jis",
    129: "cp949",
    134: "gbk",
    136: "big5",
    161: "cp1253",
    162: "cp1254",
    163: "cp1258",
    177: "cp1255",
    178: "cp1256",
    186: "cp1257",
    204: "cp1251",
    222: "cp874",
    238: "cp1250",
    255: "cp437",
}


@dataclass(slots=True)
class FieldContext:
    """Parser-local state for an active RTF field."""

    result_start_index: int
    instruction_parts: list[str] = field(default_factory=list)

    @property
    def instruction(self) -> str:
        """Return the accumulated field instruction."""
        return "".join(self.instruction_parts).strip()


@dataclass(slots=True)
class OutputContext:
    """Parser output buffers to restore after nested destinations."""

    current_inlines: list[Inline]
    text_parts: list[str]
    paragraph_style_for_current: ParagraphStyle | None
    paragraph_span_start: int | None
    paragraph_span_end: int | None
    text_span_start: int | None
    text_span_end: int | None
    active_blocks: list[Block]
    force_text_run_boundary: bool


@dataclass(slots=True)
class FootnoteContext:
    """Parser-local state for an active footnote destination."""

    id: str
    blocks: list[Block]
    parent_output: OutputContext


@dataclass(slots=True)
class AnnotationContext:
    """Parser-local state for an active annotation destination."""

    id: str
    blocks: list[Block]
    parent_output: OutputContext


@dataclass(slots=True)
class ImageContext:
    """Parser-local state for an active RTF picture destination."""

    id: str
    content_type: str | None = None
    width_twips: int | None = None
    height_twips: int | None = None
    goal_width_twips: int | None = None
    goal_height_twips: int | None = None
    scale_x: int | None = None
    scale_y: int | None = None
    hex_parts: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ParserState:
    """Mutable state for the initial RTF parser state machine.

    Attributes:
        options: Parser configuration.
        diagnostics: Capped diagnostic collector.
        style_interner: Shared `TextStyle` cache.
        current_style: Active inline style.
        style_stack: Group-scoped style stack.
        current_paragraph_style: Active paragraph style.
        paragraph_style_stack: Group-scoped paragraph style stack.
        paragraph_style_for_current: Paragraph style snapshot for active content.
        blocks: Emitted top-level paragraph blocks.
        active_blocks: Blocks receiving finished paragraphs for the active output.
        current_inlines: Inline nodes for the active paragraph.
        text_parts: Buffered plain text for the active run.
        skip_depth: Current unsupported destination skip depth.
        current_destination: Active RTF destination.
        destination_stack: Group-scoped destination stack.
        font_table: Parsed font table keyed by RTF font number.
        color_table: Parsed colour table indexed by RTF colour number.
        field_stack: Active field contexts.
        unicode_skip_bytes: Current `\\ucN` fallback length.
        fallback_chars_to_skip: Remaining fallback characters after `\\uN`.
        emitted_chars: Count of emitted document characters for safety limits.
    """

    options: ParserOptions
    diagnostics: Diagnostics
    style_interner: TextStyleInterner = field(default_factory=TextStyleInterner)
    current_style: TextStyle = field(default_factory=TextStyle)
    style_stack: list[TextStyle] = field(default_factory=list)
    current_paragraph_style: ParagraphStyle = field(default_factory=ParagraphStyle)
    paragraph_style_stack: list[ParagraphStyle] = field(default_factory=list)
    paragraph_style_for_current: ParagraphStyle | None = None
    blocks: list[Block] = field(default_factory=list)
    active_blocks: list[Block] = field(init=False)
    footnotes: dict[str, Footnote] = field(default_factory=dict)
    footnote_stack: list[FootnoteContext] = field(default_factory=list)
    next_footnote_number: int = 1
    annotations: dict[str, Annotation] = field(default_factory=dict)
    annotation_stack: list[AnnotationContext] = field(default_factory=list)
    next_annotation_number: int = 1
    images: dict[str, Image] = field(default_factory=dict)
    image_stack: list[ImageContext] = field(default_factory=list)
    next_image_number: int = 1
    metadata: Metadata = field(default_factory=Metadata)
    current_metadata_key: str | None = None
    current_metadata_parts: list[str] = field(default_factory=list)
    table_builder: TableBuilder | None = None
    table_parent_output: OutputContext | None = None
    table_row_active: bool = False
    list_definitions_ordered: dict[int, bool] = field(default_factory=dict)
    list_overrides: dict[int, int] = field(default_factory=dict)
    current_list_id: int | None = None
    current_list_ordered: bool = False
    current_override_list_id: int | None = None
    current_override_number: int | None = None
    current_inlines: list[Inline] = field(default_factory=list)
    text_parts: list[str] = field(default_factory=list)
    text_span_start: int | None = None
    text_span_end: int | None = None
    paragraph_span_start: int | None = None
    paragraph_span_end: int | None = None
    skip_depth: int = 0
    current_destination: Destination = Destination.NORMAL
    destination_stack: list[Destination] = field(default_factory=list)
    ansi_codepage: int = 1252
    font_table: dict[int, str] = field(default_factory=dict)
    font_charsets: dict[int, int] = field(default_factory=dict)
    color_table: list[Color | None] = field(default_factory=list)
    current_font_id: int | None = None
    current_font_charset: int | None = None
    active_font_charset: int | None = None
    current_font_name_parts: list[str] = field(default_factory=list)
    current_color_red: int | None = None
    current_color_green: int | None = None
    current_color_blue: int | None = None
    field_stack: list[FieldContext] = field(default_factory=list)
    force_text_run_boundary: bool = False
    unicode_skip_bytes: int = 1
    fallback_chars_to_skip: int = 0
    emitted_chars: int = 0

    def __post_init__(self) -> None:
        """Intern the initial text style."""
        self.current_style = self.style_interner.intern(self.current_style)
        self.active_blocks = self.blocks

    def push_group(self, token: Token) -> None:
        """Push group-scoped state.

        Args:
            token: Group-start token that caused the push.
        """
        if len(self.style_stack) >= self.options.max_group_depth:
            self.diagnostics.add(
                "RTF_MAX_GROUP_DEPTH",
                "Maximum RTF group depth exceeded.",
                Severity.FATAL,
                offset=token.start,
            )
            return
        self.style_stack.append(self.current_style)
        self.paragraph_style_stack.append(self.current_paragraph_style)
        self.destination_stack.append(self.current_destination)
        if self.skip_depth:
            self.skip_depth += 1

    def pop_group(self, token: Token) -> None:
        """Pop group-scoped state.

        Args:
            token: Group-end token that caused the pop.
        """
        self.flush_text()
        if self.skip_depth:
            self.skip_depth -= 1
        if not self.style_stack or not self.paragraph_style_stack or not self.destination_stack:
            self.diagnostics.add(
                "RTF_UNEXPECTED_GROUP_END",
                "Encountered an unmatched closing brace.",
                Severity.WARNING,
                offset=token.start,
            )
            return
        self.finalize_destination()
        self.current_style = self.style_stack.pop()
        self.current_paragraph_style = self.paragraph_style_stack.pop()
        self.current_destination = self.destination_stack.pop()

    def flush_text(self) -> None:
        """Flush buffered text to the active paragraph."""
        if not self.text_parts:
            return
        text = "".join(self.text_parts)
        self.text_parts.clear()
        span = self._consume_text_span()
        if not text:
            return
        self.emitted_chars += len(text)
        if self.emitted_chars > self.options.max_document_chars:
            self.diagnostics.add(
                "RTF_MAX_DOCUMENT_CHARS",
                "Maximum emitted document character limit exceeded.",
                Severity.FATAL,
            )
            return
        if (
            not self.force_text_run_boundary
            and self.current_inlines
            and isinstance(self.current_inlines[-1], TextRun)
        ):
            previous = self.current_inlines[-1]
            if previous.style == self.current_style:
                previous.text += text
                previous.span = _merge_spans(previous.span, span)
                return
        self.current_inlines.append(TextRun(text=text, style=self.current_style, span=span))
        self.force_text_run_boundary = False

    def finish_paragraph(self) -> None:
        """Finish the active paragraph if it has content."""
        self.flush_text()
        if self.current_inlines:
            style = self.paragraph_style_for_current or self.current_paragraph_style
            span = self._paragraph_span()
            self.active_blocks.append(Paragraph(children=self.current_inlines, style=style, span=span))
            self.current_inlines = []
            self.paragraph_style_for_current = None
            self.paragraph_span_start = None
            self.paragraph_span_end = None

    def add_text(self, text: str, start: int | None = None, end: int | None = None) -> None:
        """Append text after applying Unicode fallback skipping.

        Args:
            text: Text to append to the active text buffer.
            start: Optional source start offset.
            end: Optional source end offset.
        """
        if self.skip_depth:
            return
        text = text.replace("\r", "").replace("\n", "")
        if self.fallback_chars_to_skip:
            skip = min(self.fallback_chars_to_skip, len(text))
            text = text[skip:]
            self.fallback_chars_to_skip -= skip
            if start is not None:
                start += skip
        if (
            text
            and self.current_destination is Destination.NORMAL
            and self.table_builder is not None
            and not self.table_row_active
        ):
            self.finalize_pending_table()
        if self.current_destination is Destination.FONT_TABLE:
            self._add_font_table_text(text)
            return
        if self.current_destination is Destination.COLOR_TABLE:
            self._add_color_table_text(text)
            return
        if self.current_destination is Destination.FIELD_INSTRUCTION:
            self._add_field_instruction_text(text)
            return
        if self.current_destination is Destination.FIELD:
            return
        if self.current_destination is Destination.INFO:
            return
        if self.current_destination is Destination.METADATA:
            self._add_metadata_text(text)
            return
        if self.current_destination is Destination.PICT:
            self._add_image_hex_text(text)
            return
        if self.current_destination in {
            Destination.LIST_TABLE,
            Destination.LIST,
            Destination.LIST_LEVEL,
            Destination.LIST_OVERRIDE_TABLE,
            Destination.LIST_OVERRIDE,
        }:
            return
        if text:
            self._ensure_paragraph_style_snapshot()
            self._extend_text_span(start, end)
            self.text_parts.append(text)

    def add_inline(self, inline: Inline) -> None:
        """Flush pending text and append a non-text inline node."""
        if self.skip_depth:
            return
        if (
            self.current_destination is Destination.NORMAL
            and self.table_builder is not None
            and not self.table_row_active
        ):
            self.finalize_pending_table()
        self._ensure_paragraph_style_snapshot()
        self.flush_text()
        self._extend_paragraph_span_from_span(inline.span)
        self.current_inlines.append(inline)

    def set_style(self, **changes: object) -> None:
        """Apply style changes to the current interned inline style."""
        self.flush_text()
        self.current_style = self.style_interner.with_changes(self.current_style, **changes)

    def reset_style(self) -> None:
        """Reset the current inline style to the default style."""
        self.flush_text()
        self.current_style = self.style_interner.intern(TextStyle())

    def set_paragraph_style(self, **changes: object) -> None:
        """Apply changes to the active paragraph style."""
        self.current_paragraph_style = replace(self.current_paragraph_style, **changes)
        if self.current_inlines or self.text_parts:
            self.paragraph_style_for_current = self.current_paragraph_style

    def reset_paragraph_style(self) -> None:
        """Reset active paragraph formatting for subsequent text."""
        self.current_paragraph_style = ParagraphStyle()
        if self.current_inlines or self.text_parts:
            self.paragraph_style_for_current = self.current_paragraph_style

    def _ensure_paragraph_style_snapshot(self) -> None:
        """Snapshot paragraph style when the active paragraph first receives content."""
        if self.paragraph_style_for_current is None:
            self.paragraph_style_for_current = self.current_paragraph_style

    def _extend_text_span(self, start: int | None, end: int | None) -> None:
        """Extend pending text and paragraph spans when span tracking is enabled."""
        if not self.options.track_spans or start is None or end is None:
            return
        if self.text_span_start is None or start < self.text_span_start:
            self.text_span_start = start
        if self.text_span_end is None or end > self.text_span_end:
            self.text_span_end = end
        self._extend_paragraph_span(start, end)

    def _extend_paragraph_span(self, start: int, end: int) -> None:
        """Extend the active paragraph source span."""
        if not self.options.track_spans:
            return
        if self.paragraph_span_start is None or start < self.paragraph_span_start:
            self.paragraph_span_start = start
        if self.paragraph_span_end is None or end > self.paragraph_span_end:
            self.paragraph_span_end = end

    def _extend_paragraph_span_from_span(self, span: SourceSpan | None) -> None:
        """Extend the active paragraph source span from an inline span."""
        if span is not None:
            self._extend_paragraph_span(span.start, span.end)

    def _consume_text_span(self) -> SourceSpan | None:
        """Return and reset the active text span."""
        if not self.options.track_spans or self.text_span_start is None or self.text_span_end is None:
            self.text_span_start = None
            self.text_span_end = None
            return None
        span = SourceSpan(self.text_span_start, self.text_span_end)
        self.text_span_start = None
        self.text_span_end = None
        return span

    def _paragraph_span(self) -> SourceSpan | None:
        """Return the active paragraph span, if one was tracked."""
        if (
            not self.options.track_spans
            or self.paragraph_span_start is None
            or self.paragraph_span_end is None
        ):
            return None
        return SourceSpan(self.paragraph_span_start, self.paragraph_span_end)

    def set_destination(self, destination: Destination) -> None:
        """Switch to an RTF destination."""
        self.flush_text()
        self.current_destination = destination

    def set_current_font_id(self, font_id: int) -> None:
        """Set the active font number for table parsing or text styling."""
        if self.current_destination is Destination.FONT_TABLE:
            self._commit_font_if_ready()
            self.current_font_id = font_id
            self.current_font_charset = None
            self.current_font_name_parts = []
            return
        font_family = self.font_table.get(font_id)
        if font_family is None:
            self.diagnostics.add(
                "RTF_MISSING_FONT",
                f"Font table entry {font_id} is not available.",
                Severity.WARNING,
                control_word="f",
            )
            return
        self.active_font_charset = self.font_charsets.get(font_id)
        self.set_style(font_family=font_family)

    def set_current_font_charset(self, charset: int) -> None:
        """Set the charset for the active font-table entry."""
        if self.current_destination is Destination.FONT_TABLE and self.current_font_id is not None:
            self.current_font_charset = charset

    def set_ansi_codepage(self, codepage: int) -> None:
        """Set the document ANSI codepage used for hex decoding."""
        self.ansi_codepage = codepage

    def decode_hex_char(self, hex_text: str, *, offset: int) -> str | None:
        """Decode one hex escape using the active codepage."""
        try:
            raw = bytes.fromhex(hex_text)
        except ValueError:
            self.diagnostics.add(
                "RTF_INVALID_HEX",
                f"Invalid hex escape: {hex_text!r}.",
                Severity.WARNING,
                offset=offset,
            )
            return None

        encoding = self._active_hex_encoding()
        try:
            return raw.decode(encoding)
        except LookupError:
            self.diagnostics.add(
                "RTF_UNSUPPORTED_CODEPAGE",
                f"Unsupported RTF codepage for hex decoding: {encoding}.",
                Severity.WARNING,
                offset=offset,
            )
            return raw.decode("cp1252", errors="replace")
        except UnicodeDecodeError:
            self.diagnostics.add(
                "RTF_INVALID_HEX",
                f"Hex escape {hex_text!r} is invalid for codepage {encoding}.",
                Severity.WARNING,
                offset=offset,
            )
            return "\ufffd"

    def _active_hex_encoding(self) -> str:
        """Return the codec name for the current hex decoding context."""
        if self.active_font_charset is not None:
            charset_encoding = _CHARSET_CODEPAGES.get(self.active_font_charset)
            if charset_encoding is not None:
                return charset_encoding
        return f"cp{self.ansi_codepage}"

    def set_color_component(self, component: str, value: int) -> None:
        """Set a component of the current colour-table entry."""
        if self.current_destination is not Destination.COLOR_TABLE:
            return
        clamped = max(0, min(255, value))
        if component == "red":
            self.current_color_red = clamped
        elif component == "green":
            self.current_color_green = clamped
        elif component == "blue":
            self.current_color_blue = clamped

    def apply_foreground_color(self, index: int) -> None:
        """Apply a colour-table entry as the current foreground colour."""
        color = self._color_at(index, control_word="cf")
        if index == 0:
            self.set_style(foreground=None)
        elif color is not None:
            self.set_style(foreground=color)

    def apply_background_color(self, index: int, control_word: str) -> None:
        """Apply a colour-table entry as the current background/highlight colour."""
        color = self._color_at(index, control_word=control_word)
        if index == 0:
            self.set_style(background=None)
        elif color is not None:
            self.set_style(background=color)

    def finalize_destination(self) -> None:
        """Finalize destination-local buffered state before leaving a group."""
        if self.current_destination is Destination.FONT_TABLE:
            self._commit_font_if_ready()
        elif self.current_destination is Destination.COLOR_TABLE:
            self._commit_color_if_ready()
        elif self.current_destination is Destination.FIELD:
            self._finalize_field()
        elif self.current_destination is Destination.FOOTNOTE:
            self._finalize_footnote()
        elif self.current_destination is Destination.ANNOTATION:
            self._finalize_annotation()
        elif self.current_destination is Destination.METADATA:
            self._commit_metadata_if_ready()
        elif self.current_destination is Destination.PICT:
            self._finalize_image()
        elif self.current_destination is Destination.LIST:
            self._commit_list_definition_if_ready()
        elif self.current_destination is Destination.LIST_OVERRIDE:
            self._commit_list_override_if_ready()

    def finalize_open_contexts(self) -> None:
        """Recover open destinations at EOF and restore output targets."""
        if self.current_metadata_key is not None:
            self.diagnostics.add(
                "RTF_UNCLOSED_DESTINATION",
                "Recovered an unclosed metadata destination at end of file.",
                Severity.WARNING,
                destination=Destination.METADATA,
            )
            self._commit_metadata_if_ready()
        if self.current_list_id is not None:
            self.diagnostics.add(
                "RTF_UNCLOSED_DESTINATION",
                "Recovered an unclosed list definition at end of file.",
                Severity.WARNING,
                destination=Destination.LIST,
            )
            self._commit_list_definition_if_ready()
        if self.current_override_number is not None or self.current_override_list_id is not None:
            self.diagnostics.add(
                "RTF_UNCLOSED_DESTINATION",
                "Recovered an unclosed list override at end of file.",
                Severity.WARNING,
                destination=Destination.LIST_OVERRIDE,
            )
            self._commit_list_override_if_ready()
        while self.image_stack:
            self.diagnostics.add(
                "RTF_UNCLOSED_DESTINATION",
                "Recovered an unclosed image destination at end of file.",
                Severity.WARNING,
                destination=Destination.PICT,
            )
            self._finalize_image()
        if self.field_stack:
            self.diagnostics.add(
                "RTF_UNCLOSED_DESTINATION",
                "Recovered an unclosed field destination at end of file.",
                Severity.WARNING,
                destination=Destination.FIELD,
            )
            self.flush_text()
            while self.field_stack:
                self._finalize_field()
        while self.footnote_stack:
            self.diagnostics.add(
                "RTF_UNCLOSED_DESTINATION",
                "Recovered an unclosed footnote destination at end of file.",
                Severity.WARNING,
                destination=Destination.FOOTNOTE,
            )
            self._finalize_footnote()
        while self.annotation_stack:
            self.diagnostics.add(
                "RTF_UNCLOSED_DESTINATION",
                "Recovered an unclosed annotation destination at end of file.",
                Severity.WARNING,
                destination=Destination.ANNOTATION,
            )
            self._finalize_annotation()

    def start_table_row(self) -> None:
        """Start collecting a table row."""
        if self.table_builder is None:
            self.finish_paragraph()
            self.table_builder = TableBuilder()
            self.table_parent_output = OutputContext(
                current_inlines=self.current_inlines,
                text_parts=self.text_parts,
                paragraph_style_for_current=self.paragraph_style_for_current,
                paragraph_span_start=self.paragraph_span_start,
                paragraph_span_end=self.paragraph_span_end,
                text_span_start=self.text_span_start,
                text_span_end=self.text_span_end,
                active_blocks=self.active_blocks,
                force_text_run_boundary=self.force_text_run_boundary,
            )
        elif self.table_row_active:
            self.finish_table_row()

        self.table_row_active = True
        self.current_inlines = []
        self.text_parts = []
        self.paragraph_style_for_current = None
        self.paragraph_span_start = None
        self.paragraph_span_end = None
        self.text_span_start = None
        self.text_span_end = None
        self.active_blocks = []
        self.force_text_run_boundary = False

    def add_table_cell_boundary(self, boundary_twips: int) -> None:
        """Record a table cell right-edge boundary."""
        if self.table_builder is not None and self.table_row_active:
            self.table_builder.add_cell_boundary(boundary_twips)
            return
        self.diagnostics.add(
            "RTF_TABLE_PROPERTY_OUTSIDE_ROW",
            "Encountered a table cell boundary outside an active row.",
            Severity.WARNING,
            control_word="cellx",
        )

    def mark_table_horizontal_merge_start(self) -> None:
        """Mark the next table cell as a horizontal merge anchor."""
        if self.table_builder is not None and self.table_row_active:
            self.table_builder.mark_horizontal_merge_start()
            return
        self._add_table_property_outside_row_diagnostic("clmgf")

    def mark_table_horizontal_merge_continuation(self) -> None:
        """Mark the next table cell as horizontally merged with the left cell."""
        if self.table_builder is not None and self.table_row_active:
            self.table_builder.mark_horizontal_merge_continuation()
            return
        self._add_table_property_outside_row_diagnostic("clmrg")

    def mark_table_vertical_merge_start(self) -> None:
        """Mark the next table cell as a vertical merge anchor."""
        if self.table_builder is not None and self.table_row_active:
            self.table_builder.mark_vertical_merge_start()
            return
        self._add_table_property_outside_row_diagnostic("clvmgf")

    def mark_table_vertical_merge_continuation(self) -> None:
        """Mark the next table cell as vertically merged with the cell above."""
        if self.table_builder is not None and self.table_row_active:
            self.table_builder.mark_vertical_merge_continuation()
            return
        self._add_table_property_outside_row_diagnostic("clvmrg")

    def finish_table_cell(self) -> None:
        """Finish the active table cell."""
        if self.table_builder is None or not self.table_row_active:
            self.diagnostics.add(
                "RTF_TABLE_CELL_OUTSIDE_ROW",
                "Encountered a table cell boundary outside an active row.",
                Severity.WARNING,
                control_word="cell",
            )
            return
        self.finish_paragraph()
        self.table_builder.finish_cell(self.active_blocks)
        self.current_inlines = []
        self.text_parts = []
        self.paragraph_style_for_current = None
        self.active_blocks = []
        self.force_text_run_boundary = False

    def finish_table_row(self) -> None:
        """Finish the active table row and restore parent output buffers."""
        if self.table_builder is None or not self.table_row_active:
            self.diagnostics.add(
                "RTF_TABLE_ROW_OUTSIDE_TABLE",
                "Encountered a table row boundary outside an active row.",
                Severity.WARNING,
                control_word="row",
            )
            return
        self.finish_paragraph()
        if self.active_blocks or self.table_builder.current_col == 0:
            if self.active_blocks:
                self.diagnostics.add(
                    "RTF_TABLE_MISSING_CELL",
                    "Recovered table cell content that was not closed with a cell marker.",
                    Severity.WARNING,
                    control_word="row",
                )
            self.table_builder.finish_cell(self.active_blocks)
        self.table_builder.finish_row()
        self.table_row_active = False
        self._restore_table_parent_output()

    def finalize_pending_table(self) -> None:
        """Emit a pending table after its rows have been collected."""
        if self.table_builder is None:
            return
        if self.table_row_active:
            self.diagnostics.add(
                "RTF_TABLE_MISSING_ROW",
                "Recovered table row that was not closed with a row marker.",
                Severity.WARNING,
                control_word="row",
            )
            self.finish_table_row()
        table = self.table_builder.to_table()
        self._restore_table_parent_output()
        if table.cells:
            self.active_blocks.append(table)
        self.table_builder = None
        self.table_parent_output = None

    def _restore_table_parent_output(self) -> None:
        """Restore the output target saved before table parsing."""
        if self.table_parent_output is None:
            return
        self.current_inlines = self.table_parent_output.current_inlines
        self.text_parts = self.table_parent_output.text_parts
        self.paragraph_style_for_current = self.table_parent_output.paragraph_style_for_current
        self.paragraph_span_start = self.table_parent_output.paragraph_span_start
        self.paragraph_span_end = self.table_parent_output.paragraph_span_end
        self.text_span_start = self.table_parent_output.text_span_start
        self.text_span_end = self.table_parent_output.text_span_end
        self.active_blocks = self.table_parent_output.active_blocks
        self.force_text_run_boundary = self.table_parent_output.force_text_run_boundary

    def _add_table_property_outside_row_diagnostic(self, control_word: str) -> None:
        """Record a table property encountered outside an active row."""
        self.diagnostics.add(
            "RTF_TABLE_PROPERTY_OUTSIDE_ROW",
            "Encountered a table property outside an active row.",
            Severity.WARNING,
            control_word=control_word,
        )

    def start_list_table(self) -> None:
        """Start parsing an RTF list table destination."""
        self.flush_text()
        self.set_destination(Destination.LIST_TABLE)

    def start_list_definition(self) -> None:
        """Start parsing one list definition."""
        self._commit_list_definition_if_ready()
        self.current_list_id = None
        self.current_list_ordered = False
        self.set_destination(Destination.LIST)

    def start_list_level(self) -> None:
        """Start parsing one list level definition."""
        self.set_destination(Destination.LIST_LEVEL)

    def set_current_list_id(self, list_id: int) -> None:
        """Set the active list-definition identifier."""
        if self.current_destination in {Destination.LIST, Destination.LIST_LEVEL}:
            self.current_list_id = list_id
        elif self.current_destination is Destination.LIST_OVERRIDE:
            self.current_override_list_id = list_id

    def set_current_list_level_kind(self, level_kind: int) -> None:
        """Record whether a list level is ordered.

        RTF `\\levelnfc23` is the common bullet marker. Numbering formats such as
        decimal, roman, and alphabetic are treated as ordered for this initial pass.
        """
        if self.current_destination is Destination.LIST_LEVEL and level_kind != 23:
            self.current_list_ordered = True

    def start_list_override_table(self) -> None:
        """Start parsing a list override table destination."""
        self.flush_text()
        self.set_destination(Destination.LIST_OVERRIDE_TABLE)

    def start_list_override(self) -> None:
        """Start parsing one list override."""
        self._commit_list_override_if_ready()
        self.current_override_list_id = None
        self.current_override_number = None
        self.set_destination(Destination.LIST_OVERRIDE)

    def set_current_list_override_number(self, number: int) -> None:
        """Set the paragraph-facing list override number (`\\lsN`)."""
        if self.current_destination is Destination.LIST_OVERRIDE:
            self.current_override_number = number

    def list_ordering_by_override(self) -> dict[int, bool]:
        """Return ordered/unordered status keyed by paragraph list identity."""
        return {
            override_number: self.list_definitions_ordered.get(list_id, False)
            for override_number, list_id in self.list_overrides.items()
        }

    def _commit_list_definition_if_ready(self) -> None:
        """Commit the current list definition."""
        if self.current_list_id is not None:
            self.list_definitions_ordered[self.current_list_id] = self.current_list_ordered
        self.current_list_id = None
        self.current_list_ordered = False

    def _commit_list_override_if_ready(self) -> None:
        """Commit the current list override."""
        if self.current_override_number is not None and self.current_override_list_id is not None:
            self.list_overrides[self.current_override_number] = self.current_override_list_id
        self.current_override_list_id = None
        self.current_override_number = None

    def start_image(self) -> None:
        """Start collecting an RTF picture destination."""
        self.flush_text()
        image_id = f"img{self.next_image_number}"
        self.next_image_number += 1
        self.image_stack.append(ImageContext(id=image_id))
        self.set_destination(Destination.PICT)

    def set_image_content_type(self, content_type: str) -> None:
        """Set the active image content type."""
        if self.image_stack:
            self.image_stack[-1].content_type = content_type

    def set_image_dimension(self, field_name: str, value: int) -> None:
        """Set an active image dimension or scale field."""
        if self.image_stack:
            setattr(self.image_stack[-1], field_name, value)

    def add_image_hex_payload(self, hex_text: str) -> None:
        """Append image payload hex text."""
        self._add_image_hex_text(hex_text)

    def _add_image_hex_text(self, text: str) -> None:
        """Collect hexadecimal image payload text."""
        if not self.image_stack:
            return
        hex_text = "".join(char for char in text if char in "0123456789abcdefABCDEF")
        if hex_text:
            self.image_stack[-1].hex_parts.append(hex_text)

    def _finalize_image(self) -> None:
        """Finalize an image and emit an inline reference."""
        if not self.image_stack:
            return
        context = self.image_stack.pop()
        data = None
        hex_text = "".join(context.hex_parts)
        if self.options.extract_images and hex_text:
            try:
                data = bytes.fromhex(hex_text[: len(hex_text) - (len(hex_text) % 2)])
            except ValueError:
                self.diagnostics.add(
                    "RTF_INVALID_IMAGE_DATA",
                    "RTF picture payload contained invalid hexadecimal data.",
                    Severity.WARNING,
                    control_word="pict",
                )
        self.images[context.id] = Image(
            id=context.id,
            content_type=context.content_type,
            data=data,
            width_twips=context.width_twips,
            height_twips=context.height_twips,
            goal_width_twips=context.goal_width_twips,
            goal_height_twips=context.goal_height_twips,
            scale_x=context.scale_x,
            scale_y=context.scale_y,
        )
        self.add_inline(ImageInline(id=context.id))

    def _add_font_table_text(self, text: str) -> None:
        """Collect font name text and commit on semicolon."""
        for char in text:
            if char == ";":
                self._commit_font_if_ready()
            else:
                self.current_font_name_parts.append(char)

    def _add_color_table_text(self, text: str) -> None:
        """Commit colour-table entries on semicolon separators."""
        for char in text:
            if char == ";":
                self._commit_color_entry()

    def _commit_font_if_ready(self) -> None:
        """Commit the current font table entry if it has an ID and name."""
        if self.current_font_id is None:
            self.current_font_name_parts.clear()
            return
        name = "".join(self.current_font_name_parts).strip()
        if name:
            self.font_table[self.current_font_id] = name
            if self.current_font_charset is not None:
                self.font_charsets[self.current_font_id] = self.current_font_charset
        self.current_font_name_parts = []
        self.current_font_charset = None

    def _commit_color_if_ready(self) -> None:
        """Commit a trailing colour entry if components were seen without `;`."""
        if any(
            component is not None
            for component in (self.current_color_red, self.current_color_green, self.current_color_blue)
        ):
            self._commit_color_entry()

    def _commit_color_entry(self) -> None:
        """Commit the current colour table entry and reset component state."""
        if all(
            component is None
            for component in (self.current_color_red, self.current_color_green, self.current_color_blue)
        ):
            self.color_table.append(None)
        else:
            self.color_table.append(
                Color(
                    self.current_color_red or 0,
                    self.current_color_green or 0,
                    self.current_color_blue or 0,
                )
            )
        self.current_color_red = None
        self.current_color_green = None
        self.current_color_blue = None

    def _color_at(self, index: int, *, control_word: str) -> Color | None:
        """Return a colour-table entry or emit a missing-colour diagnostic."""
        if 0 <= index < len(self.color_table):
            return self.color_table[index]
        self.diagnostics.add(
            "RTF_MISSING_COLOR",
            f"Colour table entry {index} is not available.",
            Severity.WARNING,
            control_word=control_word,
        )
        return None

    def start_metadata(self, key: str) -> None:
        """Start collecting a document metadata field."""
        self.flush_text()
        self._commit_metadata_if_ready()
        self.current_metadata_key = key
        self.current_metadata_parts = []
        self.set_destination(Destination.METADATA)

    def _add_metadata_text(self, text: str) -> None:
        """Append text to the active metadata field."""
        self.current_metadata_parts.append(text)

    def _commit_metadata_if_ready(self) -> None:
        """Commit the active metadata field if one is being collected."""
        if self.current_metadata_key is None:
            return
        value = "".join(self.current_metadata_parts).strip()
        if value:
            setattr(self.metadata, self.current_metadata_key, value)
        self.current_metadata_key = None
        self.current_metadata_parts = []

    def start_field(self) -> None:
        """Start collecting an RTF field."""
        self.flush_text()
        self.field_stack.append(FieldContext(result_start_index=len(self.current_inlines)))
        self.set_destination(Destination.FIELD)

    def start_field_instruction(self) -> None:
        """Switch to field instruction collection."""
        if not self.field_stack:
            self.start_field()
        self.set_destination(Destination.FIELD_INSTRUCTION)

    def start_field_result(self) -> None:
        """Switch to field result emission."""
        if not self.field_stack:
            self.start_field()
        self.force_text_run_boundary = True
        self.set_destination(Destination.FIELD_RESULT)

    def _add_field_instruction_text(self, text: str) -> None:
        """Append text to the active field instruction."""
        if self.field_stack:
            self.field_stack[-1].instruction_parts.append(text)

    def _finalize_field(self) -> None:
        """Replace emitted field result inlines with a structural field node."""
        if not self.field_stack:
            return
        context = self.field_stack.pop()
        result_children = self.current_inlines[context.result_start_index :]
        del self.current_inlines[context.result_start_index :]

        instruction = context.instruction
        match = _HYPERLINK_RE.match(instruction)
        if match:
            self.current_inlines.append(
                Link(target=match.group(1), children=result_children, instruction=instruction)
            )
            return

        self.current_inlines.append(Field(instruction=instruction, children=result_children))

    def start_footnote(self) -> None:
        """Start a footnote destination and emit a reference in the main flow."""
        self.flush_text()
        footnote_id = f"fn{self.next_footnote_number}"
        self.next_footnote_number += 1
        self.add_inline(FootnoteRef(id=footnote_id, label=str(self.next_footnote_number - 1)))

        context = FootnoteContext(
            id=footnote_id,
            blocks=[],
            parent_output=OutputContext(
                current_inlines=self.current_inlines,
                text_parts=self.text_parts,
                paragraph_style_for_current=self.paragraph_style_for_current,
                paragraph_span_start=self.paragraph_span_start,
                paragraph_span_end=self.paragraph_span_end,
                text_span_start=self.text_span_start,
                text_span_end=self.text_span_end,
                active_blocks=self.active_blocks,
                force_text_run_boundary=self.force_text_run_boundary,
            ),
        )
        self.footnote_stack.append(context)
        self.current_inlines = []
        self.text_parts = []
        self.paragraph_style_for_current = None
        self.paragraph_span_start = None
        self.paragraph_span_end = None
        self.text_span_start = None
        self.text_span_end = None
        self.active_blocks = context.blocks
        self.force_text_run_boundary = False
        self.set_destination(Destination.FOOTNOTE)

    def _finalize_footnote(self) -> None:
        """Finalize the active footnote and restore the parent output target."""
        if not self.footnote_stack:
            return
        context = self.footnote_stack.pop()
        self.finish_paragraph()
        self.footnotes[context.id] = Footnote(id=context.id, blocks=context.blocks)
        self.current_inlines = context.parent_output.current_inlines
        self.text_parts = context.parent_output.text_parts
        self.paragraph_style_for_current = context.parent_output.paragraph_style_for_current
        self.paragraph_span_start = context.parent_output.paragraph_span_start
        self.paragraph_span_end = context.parent_output.paragraph_span_end
        self.text_span_start = context.parent_output.text_span_start
        self.text_span_end = context.parent_output.text_span_end
        self.active_blocks = context.parent_output.active_blocks
        self.force_text_run_boundary = context.parent_output.force_text_run_boundary

    def start_annotation(self) -> None:
        """Start an annotation destination and emit a reference in the main flow."""
        self.flush_text()
        annotation_id = f"ann{self.next_annotation_number}"
        self.next_annotation_number += 1
        self.add_inline(AnnotationRef(id=annotation_id, label=str(self.next_annotation_number - 1)))

        context = AnnotationContext(
            id=annotation_id,
            blocks=[],
            parent_output=OutputContext(
                current_inlines=self.current_inlines,
                text_parts=self.text_parts,
                paragraph_style_for_current=self.paragraph_style_for_current,
                paragraph_span_start=self.paragraph_span_start,
                paragraph_span_end=self.paragraph_span_end,
                text_span_start=self.text_span_start,
                text_span_end=self.text_span_end,
                active_blocks=self.active_blocks,
                force_text_run_boundary=self.force_text_run_boundary,
            ),
        )
        self.annotation_stack.append(context)
        self.current_inlines = []
        self.text_parts = []
        self.paragraph_style_for_current = None
        self.paragraph_span_start = None
        self.paragraph_span_end = None
        self.text_span_start = None
        self.text_span_end = None
        self.active_blocks = context.blocks
        self.force_text_run_boundary = False
        self.set_destination(Destination.ANNOTATION)

    def _finalize_annotation(self) -> None:
        """Finalize the active annotation and restore the parent output target."""
        if not self.annotation_stack:
            return
        context = self.annotation_stack.pop()
        self.finish_paragraph()
        self.annotations[context.id] = Annotation(id=context.id, blocks=context.blocks)
        self.current_inlines = context.parent_output.current_inlines
        self.text_parts = context.parent_output.text_parts
        self.paragraph_style_for_current = context.parent_output.paragraph_style_for_current
        self.paragraph_span_start = context.parent_output.paragraph_span_start
        self.paragraph_span_end = context.parent_output.paragraph_span_end
        self.text_span_start = context.parent_output.text_span_start
        self.text_span_end = context.parent_output.text_span_end
        self.active_blocks = context.parent_output.active_blocks
        self.force_text_run_boundary = context.parent_output.force_text_run_boundary


def _merge_spans(left: SourceSpan | None, right: SourceSpan | None) -> SourceSpan | None:
    """Return the smallest span covering two optional spans."""
    if left is None:
        return right
    if right is None:
        return left
    return SourceSpan(min(left.start, right.start), max(left.end, right.end))
