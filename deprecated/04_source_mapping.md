# Source Mapping

## Purpose

This document maps the original Qt/C++ parser and writer concepts onto the new Python architecture.

The goal is behaviour-preserving redesign, not line-by-line translation.

## Primary Reader Files

- `SCRTextRtfReader.cpp`
- `SCRTextRtfReader.h`
- `SCRTextRtfReader_p.h`

## Primary Writer Files

- `SCRTextRtfWriter.cpp`
- `SCRTextRtfWriter.h`
- `SCRTextRtfWriter_p.h`

## Shared Files

- `SCRTextRtfCommon.cpp`
- `SCRTextRtfCommon_base.cpp`
- `SCRTextRtfCommon_p.h`
- `SCRRtfFormatting.cpp`
- `SCRRtfFormatting.h`
- `SCRTextRtf.cpp`
- `SCRTextRtf.h`

## Support Files

- `SCRFontFileParser.cpp`
- `SCRFontFileParser.h`
- `SCRFontPostScriptNameManager.cpp`
- `SCRFontPostScriptNameManager.h`
- `SCRMacRgbHelper.cpp`
- `SCRMacRgbHelper.h`

## C++ to Python Mapping

| C++ / Qt Concept | Python Replacement | Notes |
|---|---|---|
| QTextDocument | Document | Neutral AST root |
| QTextCursor | ASTBuilder / ParserState emitter | No cursor mutation |
| QTextCharFormat | TextStyle | Inline style state |
| QTextBlockFormat | ParagraphStyle | Paragraph-level state |
| QTextTable | Table | Resolved AST table |
| QTextTableCell | TableCell | Coordinate-aware AST cell |
| QTextList | ListBlock / ListItem | Built in post-pass |
| QColor | Color | Simple value object |
| QFont | FontSpec | Simple value object |
| QString | str | Native Python text |
| QByteArray | bytes | Native Python bytes |
| QIODevice | InputSource | bytes/string abstraction |
| QStack | list | Explicit stack operations |
| QHash / QMap | dict | Typed dictionaries where useful |
| SCR formatting helpers | styles.py / utils | Preserve behaviour, remove Qt |
| RTF destinations | Destination enum/class | Parser state |
| Control word dispatch | control_words.py | Explicit mapping |
| Writer escaping | utils/escaping.py | Pure functions |

## Behaviour-Preservation Rule

When C++ logic conflicts with an intuitive Python rewrite, preserve the proven parser behaviour unless the old logic relates to deliberately dropped scope.

## Critical Parser Concepts to Preserve

- destination stack
- property stack
- character format stack
- block/paragraph format stack
- table format stack
- list format stack
- text-buffer stack
- font-codepage stack
- expected-format stack
- table-row stack
- Unicode-skip stack
- font table
- codepage table
- colour table
- high-precision colour handling where present
- list table
- list override table
- current field instruction and result
- image metadata
- note/comment destinations
- source offset tracking where enabled
- malformed input recovery

## Unicode Behaviour to Preserve

The original reader contains subtle Unicode fallback handling for malformed `\u` sequences. Preserve this behaviour with dedicated fixtures.

Required cases include:

- normal `\uN?` fallback skip
- `\uN\'xx` immediately after Unicode control word
- `\uN\r\n\'xx`
- `\uN\r\'xx`
- `\uN\n\'xx`
- missing or incorrect `\uc` fallback length
- invalid Unicode values
- negative Unicode values
- mixed codepage and Unicode input

This is not optional. This is one of the areas where the hardened C++ parser contains real-world bug tolerance.

## Writer Mapping

The writer cannot be ported as a shallow refactor.

The original writer walks `QTextDocument`, `QTextBlock`, `QTextFragment`, `QTextTable`, and `QTextList`.

The new writer must walk the neutral AST.

Reusable concepts:

- text escaping
- Unicode escaping
- font table emission
- colour table emission
- list template emission
- metadata/info group emission
- paragraph reset rules
- table emission patterns

Rebuild required:

- AST block traversal
- inline run traversal
- table traversal
- list traversal
- note traversal
- image traversal
- block-format diffing against AST styles
