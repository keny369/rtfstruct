# Seed Prompt for GPT-5.5 / Copilot Agent

You are a senior Python systems engineer and parser engineer. Your task is to port a hardened, production-tested Qt/C++ RTF reader and writer into a high-quality Python library.

The original C++ parser and writer have been used in production for approximately 15 years and have been exercised by hundreds of thousands of real users. Treat the existing parser logic as the behavioural authority. Do not improvise parser behaviour unless the source is incomplete or a deliberate design change is documented.

Project name: rtfstruct.

Primary goal:
Create a standalone Python library that reads RTF into a neutral structured document AST, exports that AST to JSON and Markdown, and writes valid RTF back from the AST.

Critical principle:
Do not build a direct RTF-to-Markdown converter. Markdown must be an output backend. The internal representation must preserve more document structure than Markdown can express.

Pipeline:
RTF bytes/string
-> lexer/tokenizer
-> parser state machine
-> Document AST
-> JSON exporter
-> Markdown exporter
-> RTF writer

JSON export must be built before Markdown export.

Required supported features:
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
- spans where detectable
- Unicode handling
- escaped characters
- hex decoding
- codepage handling
- document metadata where available
- safe recovery from malformed or partial RTF
- source position tracking where practical and enabled

Drop these entirely:
- Scrivener project styles
- Scrivener inline annotation behaviour
- Qt-specific object formats
- embedded PDF handling
- MathML
- OLE objects
- platform-specific colour helpers
- exact QTextDocument fidelity

Quality requirements:
- Python 3.11+
- strong typing throughout
- dataclasses with slots where practical
- Google-style Python docstrings throughout
- Sphinx-compatible documentation
- pytest
- fixture-driven tests
- golden JSON tests before golden Markdown tests
- fuzz testing from early milestones
- deterministic output
- explicit diagnostics
- no silent data corruption
- robust against malformed RTF
- fast enough for large legal, medical, publishing, and enterprise documents

Documentation requirement:
All generated Python code must be fully documented using Google-style Python docstrings suitable for Sphinx autodoc with Napoleon. Public APIs, public classes, parser options, exporter options, AST nodes, diagnostics, and complex internal parser logic must be documented. Inline comments should explain why, not restate obvious code.

Architectural preference:
Use object-oriented design for:
- AST model
- parser state
- reader class
- writer class
- exporter classes
- diagnostics
- document tree manipulation

Use pure functions for:
- escaping and unescaping
- unit conversions
- colour conversion
- Markdown escaping
- RTF escaping
- Unicode decoding
- token classification
- small transformations

Do not force everything into either OO or functional style. The parser itself is a state machine and should remain an explicit stateful object. Keep helper logic pure and testable.

Reference source paths:
- /Users/leepowell/apps/rtfstruct/reference/cpp_src
- /Users/leepowell/apps/rtfstruct/reference/rtftest
- /Users/leepowell/apps/rtfstruct/reference/rtftest/test_rtf_files

Important source files to study:
- SCRTextRtfReader.cpp
- SCRTextRtfReader.h
- SCRTextRtfReader_p.h
- SCRTextRtfWriter.cpp
- SCRTextRtfWriter.h
- SCRTextRtfWriter_p.h
- SCRTextRtfCommon.cpp
- SCRTextRtfCommon_base.cpp
- SCRTextRtfCommon_p.h
- SCRRtfFormatting.cpp
- SCRRtfFormatting.h
- SCRTextRtf.cpp
- SCRTextRtf.h
- rtftest source and sample RTF files

Porting rule:
For each major C++ parser concept, create a Python equivalent and document the mapping.

Examples:
QTextCharFormat -> TextStyle
QTextBlockFormat -> ParagraphStyle
QTextTable -> Table
QTextTableCell -> TableCell
QColor -> Color
QFont -> FontSpec
QTextCursor mutation -> AST node emission
QStack parser state -> explicit Python list stack
QHash/QMap -> dict
QString -> str
QIODevice -> bytes/text reader abstraction

Required repository structure:
rtfstruct/
  pyproject.toml
  README.md
  LICENSE
  NOTICE
  CONTRIBUTING.md
  docs/
  reference/
  src/
    rtfstruct/
      __init__.py
      ast.py
      reader.py
      writer.py
      lexer.py
      tokens.py
      parser_state.py
      control_words.py
      destinations.py
      styles.py
      tables.py
      lists.py
      fields.py
      notes.py
      images.py
      markdown.py
      json_export.py
      diagnostics.py
      exceptions.py
      options.py
      utils/
        escaping.py
        unicode.py
        colors.py
        units.py
  tests/
    fixtures/
    golden/

Development rules:
1. Read the documentation in /docs first.
2. Read the C++ reader and writer files.
3. Read the C++ test harness and sample files.
4. Implement the AST first.
5. Implement a minimal lexer/tokenizer.
6. Implement the reader incrementally with tests.
7. Implement Unicode and codepage behaviour as a separate milestone.
8. Implement JSON export before Markdown export.
9. Implement semantic_equals before roundtrip tests.
10. Implement Markdown export only after JSON and AST stabilise.
11. Implement RTF writer after reader/exporter baseline is stable.
12. Keep all unsupported legacy features explicitly documented.

Specific validation-derived requirements:
- Tables must be built through a TableBuilder and emitted as resolved coordinate/spanning structures.
- List assembly must follow the C++ post-pass model.
- Unicode recovery must be isolated and ported with branch-specific fixtures.
- AST dataclasses must use slots where practical.
- Repeated style objects must be interned.
- Source spans must be optional.
- Diagnostics must be deduplicated and capped.
- The writer must be treated as an AST traversal rebuild, not a direct QTextDocument port.
