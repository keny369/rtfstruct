# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Document AST for parsed RTF.

The AST is the canonical internal representation of an RTF document. It is
independent of Markdown, Qt, and the original source byte layout. Reader modules
produce these nodes; JSON, Markdown, and RTF writer modules consume them.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import TypeAlias

from rtfstruct.diagnostics import Diagnostic
from rtfstruct.options import JsonOptions, MarkdownOptions


@dataclass(frozen=True, slots=True)
class SourceSpan:
    """Source range in the original input.

    Attributes:
        start: Inclusive source offset.
        end: Exclusive source offset.
    """

    start: int
    end: int


@dataclass(frozen=True, slots=True)
class Color:
    """RGB color value.

    Attributes:
        red: Red channel from 0 to 255.
        green: Green channel from 0 to 255.
        blue: Blue channel from 0 to 255.
        alpha: Optional alpha channel from 0 to 255.
    """

    red: int
    green: int
    blue: int
    alpha: int | None = None


@dataclass(frozen=True, slots=True)
class TextStyle:
    """Inline text style.

    TextStyle objects are immutable and are intended to be interned by parser
    state so repeated style combinations share identity in large documents.
    """

    bold: bool = False
    italic: bool = False
    underline: bool = False
    strikethrough: bool = False
    superscript: bool = False
    subscript: bool = False
    font_family: str | None = None
    font_size_half_points: int | None = None
    foreground: Color | None = None
    background: Color | None = None


class TextStyleInterner:
    """Intern immutable `TextStyle` values by field tuple."""

    def __init__(self) -> None:
        """Create an empty style interner with the default style preloaded."""
        self._cache: dict[TextStyle, TextStyle] = {}
        self.intern(TextStyle())

    def intern(self, style: TextStyle) -> TextStyle:
        """Return a shared instance equivalent to `style`.

        Args:
            style: Style value to intern.

        Returns:
            The canonical style instance.
        """
        existing = self._cache.get(style)
        if existing is not None:
            return existing
        self._cache[style] = style
        return style

    def with_changes(self, style: TextStyle, **changes: object) -> TextStyle:
        """Return an interned copy of `style` with dataclass field changes."""
        return self.intern(replace(style, **changes))


@dataclass(frozen=True, slots=True)
class ParagraphStyle:
    """Paragraph-level formatting and structural metadata."""

    alignment: str | None = None
    left_indent_twips: int | None = None
    right_indent_twips: int | None = None
    first_line_indent_twips: int | None = None
    space_before_twips: int | None = None
    space_after_twips: int | None = None
    style_name: str | None = None
    list_identity: int | None = None
    list_level: int | None = None


@dataclass(slots=True)
class TextRun:
    """Styled text segment.

    Attributes:
        text: Text content.
        style: Inline style applied to the text.
        span: Optional source span.
    """

    text: str
    style: TextStyle = field(default_factory=TextStyle)
    span: SourceSpan | None = None


@dataclass(slots=True)
class Link:
    """Hyperlink inline node.

    Attributes:
        target: Link target URL.
        children: Visible link content.
        instruction: Raw RTF field instruction where available.
        span: Optional source span.
    """

    target: str
    children: list[Inline] = field(default_factory=list)
    instruction: str | None = None
    span: SourceSpan | None = None


@dataclass(slots=True)
class Field:
    """Unknown or unsupported RTF field inline node.

    Attributes:
        instruction: Raw field instruction.
        children: Visible field result content.
        span: Optional source span.
    """

    instruction: str
    children: list[Inline] = field(default_factory=list)
    span: SourceSpan | None = None


@dataclass(slots=True)
class FootnoteRef:
    """Inline reference to a footnote stored on the document.

    Attributes:
        id: Stable internal footnote identifier.
        label: Optional visible label.
        span: Optional source span.
    """

    id: str
    label: str | None = None
    span: SourceSpan | None = None


@dataclass(slots=True)
class AnnotationRef:
    """Inline reference to an annotation stored on the document.

    Attributes:
        id: Stable internal annotation identifier.
        label: Optional visible label.
        span: Optional source span.
    """

    id: str
    label: str | None = None
    span: SourceSpan | None = None


@dataclass(slots=True)
class Image:
    """Image metadata and optional payload extracted from an RTF picture."""

    id: str
    content_type: str | None = None
    data: bytes | None = None
    path: str | None = None
    alt_text: str | None = None
    width_twips: int | None = None
    height_twips: int | None = None
    goal_width_twips: int | None = None
    goal_height_twips: int | None = None
    scale_x: int | None = None
    scale_y: int | None = None


@dataclass(slots=True)
class ImageInline:
    """Inline reference to an image stored on the document."""

    id: str
    alt_text: str | None = None
    span: SourceSpan | None = None


@dataclass(slots=True)
class LineBreak:
    """Inline line break."""

    span: SourceSpan | None = None


@dataclass(slots=True)
class Tab:
    """Inline tab."""

    span: SourceSpan | None = None


Inline: TypeAlias = TextRun | Link | Field | FootnoteRef | AnnotationRef | ImageInline | LineBreak | Tab


@dataclass(slots=True)
class Paragraph:
    """Paragraph block containing inline children."""

    children: list[Inline] = field(default_factory=list)
    style: ParagraphStyle = field(default_factory=ParagraphStyle)
    span: SourceSpan | None = None


@dataclass(slots=True)
class ListItem:
    """A list item containing one or more block nodes.

    Attributes:
        blocks: Blocks belonging to this list item.
        level: Zero-based nesting level.
        marker: Optional visible marker text where known.
    """

    blocks: list[Block] = field(default_factory=list)
    level: int = 0
    marker: str | None = None


@dataclass(slots=True)
class ListBlock:
    """Resolved list block assembled after parsing paragraphs."""

    ordered: bool
    items: list[ListItem] = field(default_factory=list)
    list_id: int | None = None


@dataclass(slots=True)
class TableCell:
    """Resolved table cell with explicit coordinates.

    Attributes:
        row: Zero-based row coordinate.
        col: Zero-based column coordinate.
        blocks: Cell content.
        rowspan: Number of rows spanned by the cell.
        colspan: Number of columns spanned by the cell.
        width_twips: Cell width where known.
    """

    row: int
    col: int
    blocks: list[Block] = field(default_factory=list)
    rowspan: int = 1
    colspan: int = 1
    width_twips: int | None = None


@dataclass(slots=True)
class Table:
    """Resolved coordinate-based table."""

    cells: list[TableCell] = field(default_factory=list)
    row_count: int = 0
    col_count: int = 0


Block: TypeAlias = Paragraph | ListBlock | Table


@dataclass(slots=True)
class Footnote:
    """Footnote content stored separately from inline flow."""

    id: str
    blocks: list[Block] = field(default_factory=list)


@dataclass(slots=True)
class Annotation:
    """Annotation or comment content stored separately from inline flow."""

    id: str
    blocks: list[Block] = field(default_factory=list)
    author: str | None = None


@dataclass(slots=True)
class Metadata:
    """Document metadata extracted from RTF info groups."""

    title: str | None = None
    subject: str | None = None
    author: str | None = None
    keywords: str | None = None
    comment: str | None = None
    company: str | None = None


@dataclass(slots=True)
class StyleSheet:
    """Document stylesheet placeholder for parsed styles."""

    paragraph_styles: dict[str, ParagraphStyle] = field(default_factory=dict)
    text_styles: dict[str, TextStyle] = field(default_factory=dict)


@dataclass(slots=True)
class Document:
    """Structured representation of a parsed RTF document.

    Attributes:
        blocks: Top-level document blocks in reading order.
        metadata: Document metadata extracted from RTF info groups.
        styles: Style definitions detected or inferred during parsing.
        footnotes: Footnotes keyed by stable internal identifier.
        annotations: Comments or annotations keyed by stable internal identifier.
        images: Extracted or represented images keyed by stable internal identifier.
        diagnostics: Recoverable parser warnings and errors.
    """

    blocks: list[Block] = field(default_factory=list)
    metadata: Metadata = field(default_factory=Metadata)
    styles: StyleSheet = field(default_factory=StyleSheet)
    footnotes: dict[str, Footnote] = field(default_factory=dict)
    annotations: dict[str, Annotation] = field(default_factory=dict)
    images: dict[str, Image] = field(default_factory=dict)
    diagnostics: list[Diagnostic] = field(default_factory=list)

    def semantic_equals(self, other: Document) -> bool:
        """Return whether another document is semantically equivalent.

        The initial implementation normalizes adjacent same-style text runs and
        compares supported Milestone 1 structure.
        """
        return _normalise_blocks(self.blocks) == _normalise_blocks(other.blocks) and _normalise_footnotes(
            self.footnotes
        ) == _normalise_footnotes(other.footnotes) and _normalise_annotations(
            self.annotations
        ) == _normalise_annotations(other.annotations) and _normalise_images(self.images) == _normalise_images(
            other.images
        ) and _normalise_metadata(self.metadata) == _normalise_metadata(
            other.metadata
        ) and _normalise_styles(self.styles) == _normalise_styles(other.styles)

    def to_json(self, options: JsonOptions | None = None) -> dict[str, object]:
        """Export this document to deterministic JSON-compatible data."""
        from rtfstruct.json_export import JsonExporter

        return JsonExporter(options=options).export(self)

    def to_markdown(self, options: MarkdownOptions | None = None) -> str:
        """Export this document to Markdown.

        Markdown export is intentionally minimal until JSON and AST behavior are
        stable.
        """
        from rtfstruct.markdown import MarkdownExporter

        return MarkdownExporter(options=options).export(self)

    def to_rtf(self) -> str:
        """Export this document to RTF."""
        from rtfstruct.writer import to_rtf

        return to_rtf(self)


def _normalise_blocks(blocks: list[Block]) -> list[tuple[str, tuple[object, ...]]]:
    """Return a compact semantic representation for supported blocks."""
    normalised: list[tuple[str, tuple[object, ...]]] = []
    for block in blocks:
        if isinstance(block, Paragraph):
            normalised.append(
                (
                    "paragraph",
                    (
                        _normalise_paragraph_style(block.style),
                        tuple(_normalise_inlines(block.children)),
                    ),
                )
            )
        elif isinstance(block, ListBlock):
            normalised.append(
                (
                    "list",
                    (
                        block.ordered,
                        block.list_id,
                        tuple(
                            (
                                item.level,
                                item.marker,
                                tuple(_normalise_blocks(item.blocks)),
                            )
                            for item in block.items
                        ),
                    ),
                )
            )
        elif isinstance(block, Table):
            normalised.append(
                (
                    "table",
                    (
                        block.row_count,
                        block.col_count,
                        tuple(
                            (
                                cell.row,
                                cell.col,
                                cell.rowspan,
                                cell.colspan,
                                cell.width_twips,
                                tuple(_normalise_blocks(cell.blocks)),
                            )
                            for cell in block.cells
                        ),
                    ),
                )
            )
    return normalised


def _normalise_paragraph_style(style: ParagraphStyle) -> tuple[object, ...]:
    """Return semantic paragraph style data for comparison."""
    return (
        style.alignment,
        style.left_indent_twips,
        style.right_indent_twips,
        style.first_line_indent_twips,
        style.space_before_twips,
        style.space_after_twips,
        style.style_name,
        style.list_identity,
        style.list_level,
    )


def _normalise_inlines(inlines: list[Inline]) -> list[object]:
    """Coalesce adjacent same-style runs for semantic comparison."""
    result: list[object] = []
    pending_text = ""
    pending_style: TextStyle | None = None

    def flush() -> None:
        """Flush pending coalesced text into the normalized inline list."""
        nonlocal pending_text, pending_style
        if pending_text:
            result.append(("text", pending_text, pending_style))
            pending_text = ""
            pending_style = None

    for inline in inlines:
        if isinstance(inline, TextRun):
            if pending_style == inline.style:
                pending_text += inline.text
            else:
                flush()
                pending_text = inline.text
                pending_style = inline.style
        elif isinstance(inline, LineBreak):
            flush()
            result.append(("line_break",))
        elif isinstance(inline, Tab):
            flush()
            result.append(("tab",))
        elif isinstance(inline, Link):
            flush()
            result.append(("link", inline.target, tuple(_normalise_inlines(inline.children))))
        elif isinstance(inline, Field):
            flush()
            result.append(("field", inline.instruction, tuple(_normalise_inlines(inline.children))))
        elif isinstance(inline, FootnoteRef):
            flush()
            result.append(("footnote_ref", inline.id, inline.label))
        elif isinstance(inline, AnnotationRef):
            flush()
            result.append(("annotation_ref", inline.id, inline.label))
        elif isinstance(inline, ImageInline):
            flush()
            result.append(("image", inline.id, inline.alt_text))
    flush()
    return result


def _normalise_footnotes(footnotes: dict[str, Footnote]) -> dict[str, list[tuple[str, tuple[object, ...]]]]:
    """Return semantic footnote content for comparison."""
    return {key: _normalise_blocks(value.blocks) for key, value in sorted(footnotes.items())}


def _normalise_annotations(annotations: dict[str, Annotation]) -> dict[str, list[tuple[str, tuple[object, ...]]]]:
    """Return semantic annotation content for comparison."""
    return {key: _normalise_blocks(value.blocks) for key, value in sorted(annotations.items())}


def _normalise_images(images: dict[str, Image]) -> dict[str, tuple[object, ...]]:
    """Return semantic image metadata for comparison."""
    return {
        key: (
            value.content_type,
            value.data,
            value.path,
            value.alt_text,
            value.width_twips,
            value.height_twips,
            value.goal_width_twips,
            value.goal_height_twips,
            value.scale_x,
            value.scale_y,
        )
        for key, value in sorted(images.items())
    }


def _normalise_metadata(metadata: Metadata) -> tuple[object, ...]:
    """Return semantic document metadata for comparison."""
    return (
        metadata.title,
        metadata.subject,
        metadata.author,
        metadata.keywords,
        metadata.comment,
        metadata.company,
    )


def _normalise_styles(styles: StyleSheet) -> tuple[object, ...]:
    """Return semantic stylesheet data for comparison."""
    return (
        tuple(sorted((key, _normalise_paragraph_style(value)) for key, value in styles.paragraph_styles.items())),
        tuple(sorted(styles.text_styles.items())),
    )
