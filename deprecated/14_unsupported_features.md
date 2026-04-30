# Unsupported Features

## Purpose

This document records deliberately unsupported features so they do not creep back into scope.

## Dropped Permanently

The following are not supported:

- Scrivener project styles
- Scrivener inline annotation behaviour
- Qt-specific object formats
- embedded PDF handling
- MathML
- OLE object extraction
- platform-specific colour helpers
- exact QTextDocument fidelity

## Supported in Generic Form

Some original Scrivener-specific behaviour should be replaced by generic structures.

| Original Concept | New Generic Support |
|---|---|
| Scrivener inline note | Annotation |
| Scrivener footnote handling | Footnote |
| QTextCharFormat | TextStyle |
| QTextBlockFormat | ParagraphStyle |
| QTextTable | Table |

## Deferred Features

The following may be added later:

- advanced image extraction
- revision tracking
- headers and footers
- page layout fidelity
- stylesheet roundtripping
- advanced table border rendering
- bidirectional text
- complex script shaping
- embedded object metadata

## Unsupported Feature Rule

Unsupported features must produce diagnostics where detected.

They must not crash the parser.
