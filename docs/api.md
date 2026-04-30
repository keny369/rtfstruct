<!--
SPDX-License-Identifier: Apache-2.0
Copyright 2026 Lee Powell
-->
# Public API

The public API is the set of names exported from `rtfstruct.__init__`. Internal
modules may change while the project is pre-1.0.

## Reading

```python
from rtfstruct import ParserOptions, parse_rtf, read_rtf

document = parse_rtf(r"{\rtf1\ansi Hello}")
document_with_spans = parse_rtf(
    r"{\rtf1\ansi Hello}",
    options=ParserOptions(track_spans=True),
)
file_document = read_rtf("input.rtf")
```

## Exporting

```python
from rtfstruct import MarkdownOptions, to_rtf, write_rtf

data = document.to_json()
markdown = document.to_markdown(options=MarkdownOptions(preserve_colors=True))
rtf = to_rtf(document)
write_rtf(document, "output.rtf")
```

## Diagnostics

```python
for diagnostic in document.diagnostics:
    print(diagnostic.severity.value, diagnostic.code, diagnostic.message)
```

## Public Names

The package re-exports the primary document nodes, options, diagnostics, and
entry points from `rtfstruct`:

- AST nodes: `Document`, `Paragraph`, `TextRun`, `TextStyle`,
  `ParagraphStyle`, `ListBlock`, `ListItem`, `Table`, `TableCell`, `Link`,
  `Field`, `Footnote`, `FootnoteRef`, `Annotation`, `AnnotationRef`, `Image`,
  `ImageInline`, `LineBreak`, `Tab`, `Metadata`, `Color`, and `SourceSpan`.
- Options: `ParserOptions`, `JsonOptions`, and `MarkdownOptions`.
- Diagnostics and errors: `Diagnostic`, `Severity`, `RtfError`, and
  `RtfSyntaxError`.
- Functions: `parse_rtf`, `read_rtf`, `to_markdown`, `to_rtf`, and `write_rtf`.

Detailed API reference is split across the AST, parser, JSON, Markdown, writer,
and diagnostics pages.
