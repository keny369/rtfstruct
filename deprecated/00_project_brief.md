# rtfstruct Project Brief

## Purpose

`rtfstruct` is a standalone Python RTF parser and writer for structured document processing.

Its primary purpose is to convert RTF into a granular, AI-ready document AST that preserves document structure, formatting, tables, lists, links, annotations, footnotes, images, metadata, and recoverable source detail before exporting to JSON, Markdown, or RTF.

The implementation is informed by Lee Powell's experience building production C++ RTF parsing and writing infrastructure, including the mature parser and writer he authored for Scrivener for Windows and refined through approximately 15 years of real-world use by hundreds of thousands of users.

## Core Principle

The AST is the product.

Markdown is an output format, not the internal representation.

The parser must not be designed as:

```text
RTF -> Markdown
```

It must be designed as:

```text
RTF bytes/string
-> lexer/tokenizer
-> parser state machine
-> neutral Document AST
-> JSON exporter
-> Markdown exporter
-> RTF writer
```

JSON export must be implemented before Markdown export. JSON forces the AST to stay complete and serialisable. Markdown is lossy and must not shape the internal model.

## Primary Use Case

The primary use case is AI document infrastructure.

The library should preserve enough structure for:

- RAG pipelines
- legal discovery
- forensic document tracing
- document intelligence
- AI ingestion
- long-form document analysis
- structured conversion workflows
- publishing and archival workflows

## Supported Scope

`rtfstruct` must support:

- plain text
- paragraphs
- headings where detectable
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
- URL links and fields
- annotations/comments
- footnotes
- images where extractable or representable
- ordered lists
- unordered lists
- nested lists
- tables
- table rows
- table cells
- rowspan and colspan where detectable
- Unicode handling
- escaped characters
- hex decoding
- codepage handling
- document metadata where available
- malformed RTF recovery
- diagnostics
- JSON export
- Markdown export
- RTF writing

## Explicitly Dropped Scope

Do not port these:

- Scrivener project styles
- Scrivener inline annotation behaviour
- Qt-specific object formats
- embedded PDF handling
- MathML
- OLE objects
- platform-specific colour helpers
- exact QTextDocument fidelity

## Product Positioning

Recommended public positioning:

```text
A production-informed Python RTF parser and writer for AI document pipelines.
Converts RTF into a structured document AST, JSON, Markdown, and RTF.
Designed for RAG, legal discovery, document intelligence, and long-form writing systems.
```

## Non-Goals

`rtfstruct` is not:

- a GUI editor
- a Word clone
- a Qt compatibility layer
- a perfect visual layout engine
- a Pandoc wrapper
- a plain-text stripper
- a Scrivener project parser

## Quality Bar

The library must be:

- typed
- tested
- deterministic
- robust against malformed input
- fast enough for large real-world RTF files
- minimal in dependencies
- clear in public API
- explicit about unsupported features
- safe against pathological input
- documented through standard Python docstrings
