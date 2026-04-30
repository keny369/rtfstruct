# Parser Porting Plan

## Purpose

This document defines how to port the hardened C++ parser into Python without carrying over Qt dependencies.

## Core Rule

Do not transliterate Qt mutation.

Convert this:

```text
RTF control word -> QTextCursor/QTextDocument mutation
```

into this:

```text
RTF control word -> ParserState mutation -> AST node emission
```

## Phase 0: Source Reading

Read and annotate:

- parse loop
- keyword/control-word handling
- destination handling
- property stack
- text drawing/output
- paragraph finalisation
- table finalisation
- list handling
- field handling
- footnote handling
- annotation handling
- Unicode handling
- hex handling
- codepage handling

Produce source-mapping notes before implementation.

## Phase 1: Lexer

Create a lexer that yields tokens:

```python
GroupStart
GroupEnd
ControlWord
ControlSymbol
Text
HexChar
EOF
```

The lexer must track source offsets.

The lexer must avoid recursion.

## Phase 2: Parser State

Create explicit parser state:

```python
class ParserState:
    """Mutable state for the RTF parser state machine.

    ParserState owns the active destination stack, property stack, style state,
    table builders, list metadata, font tables, colour tables, diagnostics, and
    active AST emission target.
    """

    destination_stack: list[DestinationState]
    property_stack: list[PropertyState]
    current_text_style: TextStyle
    current_paragraph_style: ParagraphStyle
    current_paragraph_runs: list[Inline]
    table_builder_stack: list[TableBuilder]
    font_table: dict[int, FontSpec]
    codepage_table: dict[int, str]
    color_table: dict[int, Color]
    list_table: dict[int, ListDefinition]
    list_override_table: dict[int, ListOverride]
    diagnostics: Diagnostics
```

The actual state should be expanded according to the C++ mapping, not constrained by this sketch.

## Phase 3: Control Word Dispatch

Create explicit dispatch:

```python
CONTROL_WORDS = {
    "b": handle_bold,
    "i": handle_italic,
    "ul": handle_underline,
    "strike": handle_strike,
    "super": handle_superscript,
    "sub": handle_subscript,
    "fs": handle_font_size,
    "f": handle_font_family,
    "cf": handle_foreground_color,
    "highlight": handle_background_color,
    "par": handle_paragraph_break,
    "tab": handle_tab,
    "line": handle_line_break,
    "footnote": handle_footnote_destination,
    "field": handle_field_destination,
    "pict": handle_picture_destination,
}
```

Handlers should be small and testable.

Do not collapse hundreds of control words into vague generic handling unless tests prove safe.

## Phase 4: Text Emission

Text emission must append styled runs to the current paragraph or active container.

Rules:

- do not concatenate strings repeatedly
- use list append and join
- intern repeated styles
- coalesce adjacent same-style runs at emission time
- drop empty runs
- avoid per-character AST node creation

## Phase 5: Paragraph Finalisation

When paragraph boundary is reached:

- flush pending text
- create Paragraph node
- attach paragraph style
- attach list identity and level if present
- add to active container
- reset paragraph buffer

## Phase 6: Unicode, Hex, and Codepages

Treat this as a distinct milestone.

Required:

- standard `\uN?` handling
- Unicode fallback skip
- malformed Unicode fallback recovery copied conceptually from the C++ branches
- hex `\'xx` decoding
- font/codepage-aware decoding
- invalid Unicode diagnostics
- invalid hex diagnostics
- tests for every recovery branch

Do not simplify this from memory.

## Phase 7: Tables

Use `TableBuilder`.

Required behaviours:

- detect row start/end
- detect cell boundaries
- collect blocks into cells
- resolve merge-up and merge-left
- support retroactive column widening
- preserve row and cell style where possible
- finalise resolved coordinate table
- recover if row/cell markers are malformed
- emit diagnostics for inconsistent table structure

## Phase 8: Lists

Lists should be built in a post-pass.

First pass:

- stamp paragraphs with list identity
- stamp paragraphs with list level
- preserve list metadata

Post-pass:

- group paragraphs into ListBlock structures
- preserve nested levels
- avoid breaking lists inside table cells
- degrade to paragraphs if list metadata is insufficient

## Phase 9: Fields and Links

Required behaviours:

- parse field instruction
- parse field result
- detect HYPERLINK fields
- emit Link inline nodes
- preserve unknown fields as Field nodes
- preserve raw instruction in JSON

## Phase 10: Footnotes and Annotations

Footnotes and annotations must become first-class AST nodes.

They must not be discarded.

## Phase 11: Images

Parse image destinations enough to represent:

- image type
- dimensions
- goal dimensions
- scale values
- binary payload where available
- placeholder if extraction is not yet implemented

## Phase 12: Malformed RTF Recovery

Parser should recover from:

- unbalanced groups
- unknown control words
- invalid hex escapes
- incomplete destinations
- missing font or colour table entries
- malformed tables
- malformed fields
- excessive group depth

Recovery must produce diagnostics.

## Phase 13: Post-Passes

Required post-passes:

- list assembly
- run coalescing if not already done
- table resolution if not finalised during parsing
- semantic normalisation for tests
- diagnostic suppression rollups
