# AST Contract

## Purpose

The AST is the canonical internal representation of an RTF document.

All readers produce the AST.
All exporters consume the AST.
The writer consumes the AST.

## Design Rules

- AST nodes must be typed.
- AST nodes must be serialisable to JSON.
- AST nodes must not depend on Markdown.
- AST nodes must not depend on Qt.
- AST nodes must preserve more structure than Markdown.
- AST dataclasses should use `slots=True` where practical.
- AST nodes should avoid per-character object creation.
- Source spans should be optional and off by default.

## Root Model

```python
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

    blocks: list[Block]
    metadata: Metadata = field(default_factory=Metadata)
    styles: StyleSheet = field(default_factory=StyleSheet)
    footnotes: dict[str, Footnote] = field(default_factory=dict)
    annotations: dict[str, Annotation] = field(default_factory=dict)
    images: dict[str, Image] = field(default_factory=dict)
    diagnostics: list[Diagnostic] = field(default_factory=list)

    def semantic_equals(self, other: "Document") -> bool:
        """Return whether another document is semantically equivalent."""
        ...
```

## Semantic Equality

`Document.semantic_equals()` must be implemented before roundtrip tests.

It should compare semantic structure, not byte-level or incidental formatting.

It may ignore:

- font table ID ordering
- colour table ID ordering
- adjacent same-style run boundaries after normalisation
- canonical escaping differences
- equivalent Unicode escape forms
- insignificant metadata ordering

It must not ignore:

- lost text
- paragraph boundary changes
- lost inline formatting
- lost links
- lost notes
- lost table cells
- lost list items
- incorrect table spans
- incorrect list nesting
- incorrect image references where images are supported

## Block Nodes

Supported block nodes:

```python
Paragraph
Heading
ListBlock
Table
ImageBlock
HorizontalRule
RawBlock
```

## Inline Nodes

Supported inline nodes:

```python
TextRun
Link
FootnoteRef
AnnotationRef
ImageInline
Field
LineBreak
Tab
```

## Text Style

```python
@dataclass(frozen=True, slots=True)
class TextStyle:
    """Inline text style.

    TextStyle objects should be immutable and interned so repeated styles are
    reused rather than reallocated across large documents.
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
```

Repeated `TextStyle` objects must be interned by tuple key to avoid excessive object churn.

## Paragraph Style

```python
@dataclass(frozen=True, slots=True)
class ParagraphStyle:
    """Paragraph-level formatting and structural metadata."""

    alignment: Alignment | None = None
    left_indent_twips: int | None = None
    right_indent_twips: int | None = None
    first_line_indent_twips: int | None = None
    space_before_twips: int | None = None
    space_after_twips: int | None = None
    style_name: str | None = None
    list_identity: int | None = None
    list_level: int | None = None
    tabs: tuple[TabStop, ...] = ()
    shading: Shading | None = None
    border: BorderSpec | None = None
```

## Carried But Not Necessarily Exported to Markdown

The AST must be able to carry document fidelity that Markdown cannot express.

Examples:

- high-precision colours
- tab definitions
- paragraph borders
- paragraph shading
- list override resolution data
- raw field instructions
- field result text
- image natural width and height
- image goal width and height
- image scale values
- table cell vertical alignment
- table cell background/pattern colour
- table cell borders
- cell merge metadata
- source offsets where enabled
- raw unsupported destination payloads where safe and useful

This data must appear in JSON export where practical.

## Tables

Do not emit raw tables directly from parser events.

Use a `TableBuilder` during parsing. Emit resolved tables only.

Resolved table model:

```python
@dataclass(slots=True)
class Table:
    """Resolved table with explicit coordinate-based cells."""

    cells: list[TableCell]
    row_count: int
    col_count: int
    style: TableStyle | None = None
```

```python
@dataclass(slots=True)
class TableCell:
    """Resolved table cell.

    Attributes:
        row: Zero-based resolved row coordinate.
        col: Zero-based resolved column coordinate.
        rowspan: Number of rows spanned by the cell.
        colspan: Number of columns spanned by the cell.
        blocks: Cell content.
        width_twips: Cell width where known.
        style: Cell-level formatting where known.
    """

    row: int
    col: int
    rowspan: int = 1
    colspan: int = 1
    blocks: list[Block] = field(default_factory=list)
    width_twips: int | None = None
    style: TableCellStyle | None = None
```

This supports retroactive widening, merge-up, merge-left, colspan, and rowspan resolution.

## Lists

Lists should be assembled in a post-pass.

Paragraphs should initially carry list identity and level metadata.

```python
@dataclass(slots=True)
class ListBlock:
    ordered: bool
    items: list[ListItem]
    list_id: int | None = None
```

```python
@dataclass(slots=True)
class ListItem:
    blocks: list[Block]
    level: int = 0
    marker: str | None = None
```

The parser should not assume that final list structure can be built safely during the first pass.

## Notes and Annotations

Footnotes and annotations must be first-class structures.

```python
@dataclass(slots=True)
class Footnote:
    id: str
    blocks: list[Block]
```

```python
@dataclass(slots=True)
class Annotation:
    id: str
    author: str | None
    blocks: list[Block]
```

## Images

Images must be represented even if binary extraction is deferred.

```python
@dataclass(slots=True)
class Image:
    id: str
    content_type: str | None
    data: bytes | None
    path: str | None
    alt_text: str | None
    width_twips: int | None
    height_twips: int | None
    goal_width_twips: int | None = None
    goal_height_twips: int | None = None
    scale_x: int | None = None
    scale_y: int | None = None
```

## Source Spans

Source spans are optional.

```python
@dataclass(frozen=True, slots=True)
class SourceSpan:
    start: int
    end: int
```

Default:

```python
ParserOptions(track_spans=False)
```

If enabled, prefer block-level spans first. Inline spans should be optional because they increase memory use.
