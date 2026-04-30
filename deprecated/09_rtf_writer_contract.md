# RTF Writer Contract

## Purpose

The RTF writer converts the neutral AST back into valid RTF.

The writer does not need to reproduce the original source byte-for-byte. It must produce clean, valid, readable RTF representing the AST.

## Design Rules

- Write from AST only.
- Do not depend on Qt.
- Do not depend on Markdown.
- Emit deterministic RTF.
- Escape text correctly.
- Emit font table and colour table when needed.
- Prefer simple valid RTF over complex visual fidelity.
- Emit diagnostics for unsupported writer features.

## Scope Warning

The original writer walks `QTextDocument` and related Qt structures.

The new writer must walk the AST.

This is a structural rebuild, not a direct port.

## Reusable Concepts From the C++ Writer

- text escaping
- Unicode escaping
- font table emission
- colour table emission
- list template emission
- metadata/info group emission
- paragraph reset logic
- table emission patterns

## Rebuild Required

- AST block walker
- inline run walker
- table walker
- list walker
- note writer
- image writer
- block-format diffing against AST styles
- deterministic ID allocation

## Required Output Features

- document header
- font table
- colour table
- metadata where available
- paragraphs
- bold
- italic
- underline
- strikethrough
- superscript
- subscript
- font family
- font size
- foreground colour
- background/highlight colour
- links
- footnotes
- annotations/comments where feasible
- lists
- tables
- images where supported

## Text Escaping

Required escaping:

- backslash
- opening brace
- closing brace
- non-ASCII Unicode
- control characters

## Unicode

Use valid RTF Unicode escape sequences.

```text
\u8217?
```

## Links

Emit links as RTF fields where possible.

## Tables

Emit simple valid RTF tables.

Complex AST tables may be simplified, but the output must remain valid and diagnostics must record simplification.

## Roundtrip Contract

RTF -> AST -> RTF -> AST should preserve core semantic structure.

Required preservation:

- text
- paragraph boundaries
- inline formatting
- lists
- tables
- links
- notes
