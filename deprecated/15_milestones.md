# Milestones

## Milestone 0: Reference Audit

- confirm reference folder exists
- confirm C++ parser/writer files are present
- confirm C++ test harness files are present
- confirm sample RTF test files are present
- write source mapping notes
- identify dropped code paths

## Milestone 1: Core Skeleton

- project skeleton
- AST core
- lexer
- parser state
- plain text
- paragraphs
- escaped braces
- bold
- italic
- underline
- basic pytest fixtures
- Google-style docstrings in all modules/classes/functions

## Milestone 1b: Unicode and Codepages

- Unicode escapes
- malformed Unicode fallback recovery
- hex decoding
- codepage handling
- branch-specific fixtures from C++ logic

## Milestone 2: JSON and Diagnostics

- JSON export
- diagnostics model
- diagnostic caps
- diagnostic deduplication
- semantic_equals

## Milestone 3: Inline Formatting

- strikethrough
- superscript
- subscript
- fonts
- font sizes
- colours
- highlights

## Milestone 4: Fields and Links

- field instructions
- field results
- hyperlink detection
- unknown Field nodes

## Milestone 5: Footnotes and Annotations

- footnote destinations
- annotation/comment destinations
- references in inline flow
- JSON export

## Milestone 6: Tables

- TableBuilder
- cell boundaries
- row finalisation
- merge-up
- merge-left
- resolved coordinate table AST
- table fixtures from reference/rtftest/test_rtf_files

## Milestone 7: Lists

- list table parsing
- list override parsing
- paragraph list identity stamping
- post-pass list assembly
- nested list tests

## Milestone 8: Markdown Exporter

- inline Markdown
- HTML fallback for unsupported inline features
- simple table GFM output
- complex table HTML output
- footnotes
- annotations

## Milestone 9: Images

- image metadata
- placeholders
- payload extraction where practical
- JSON and Markdown output

## Milestone 10: RTF Writer

- AST walker
- font table
- colour table
- text escaping
- inline styles
- paragraphs
- links
- notes
- simple tables
- lists

## Milestone 11: Roundtrip and Fuzzing Expansion

- semantic roundtrip tests
- fuzz corpus
- malformed RTF suite
- performance benchmarks

## Milestone 12: Packaging and Integrations

- README
- pyproject
- public API polish
- Sphinx documentation
- MarkItDown plugin
- Docling adapter exploration
- Unstructured integration exploration
