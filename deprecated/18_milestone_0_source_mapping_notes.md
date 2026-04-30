# Milestone 0 Source Mapping Notes

## Purpose

These notes record the first implementation-oriented audit of the reference C++
RTF reader, writer, shared keyword structures, and test harness. They supplement
`docs/04_source_mapping.md` with concrete entry points and behaviours to preserve
when building the Python implementation.

## Reference Inventory

The expected reference files are present under `reference/cpp_src/`, including
the primary reader, writer, shared common, formatting, and support files.

The expected Qt test harness files are present under `reference/rtftest/`.

The expected sample RTF files are present under
`reference/rtftest/test_rtf_files/`, including the simple samples and table merge
fixtures.

There is no Python package skeleton yet under `src/rtfstruct/`.

## Reader Entry Points

Primary reader files:

- `SCRTextRtfReader.h`
- `SCRTextRtfReader_p.h`
- `SCRTextRtfReader.cpp`

Important C++ entry points:

- `SCRTextRtfReader::read(...)` prepares the `QTextDocument`, reader options,
  default character format, and then calls `SCRTextRtfReaderPrivate::parseFile()`.
- `SCRTextRtfReaderPrivate::parseFile()` owns the main parse loop.
- `SCRTextRtfReaderPrivate::parseKeyword()` reads RTF control words and symbols.
- `SCRTextRtfReaderPrivate::translateControlWord(...)` performs semantic dispatch.
- `SCRTextRtfReaderPrivate::drawText()` flushes accumulated text according to the
  active destination.
- `SCRTextRtfReaderPrivate::pushProperties()` and `popProperties()` mirror RTF
  group scoping.
- `SCRTextRtfReaderPrivate::finalizeDestination()` closes destination-specific
  state.
- `SCRTextRtfReaderPrivate::initializeTables(...)`, `finalizeRow()`, and
  `finalizeTables(...)` contain the table-building logic.

Python mapping:

- `Reader` should prepare options and input normalization.
- `Lexer` should replace byte-by-byte control word recognition with explicit
  tokens while preserving source offsets.
- `ParserState` should own destination, formatting, table, list, font, codepage,
  field, note, image, and diagnostic state.
- `control_words.py` should hold explicit handlers equivalent to
  `translateControlWord(...)`.
- AST emission should replace `QTextCursor` mutation.

## Main Parse Loop

The C++ `parseFile()` loop reads one byte at a time and dispatches on:

- `{` to flush text, push scoped properties, and consume the group start.
- `}` to flush text, pop scoped properties, and consume the group end.
- `\` to flush text and parse a control word or control symbol.
- CR/LF to ignore line separators outside explicit text handling.
- other bytes to append printable characters or hex payload bytes depending on
  `mExpectedFormat`.

It checks for a `{\rtf` signature at the start. If the signature is missing, the
C++ reader inserts the local 8-bit buffer into the document and returns without a
hard error. The Python port should make this behaviour an explicit recovery
choice controlled by parser options and diagnostics.

After the main loop, the C++ reader performs list assembly as a post-pass over
document blocks. The Python reader must keep this post-pass model: first stamp
paragraphs with list identity and level, then assemble `ListBlock` structures.

## Scoped State

The private reader carries these important stacks:

- character format stack
- destination stack
- Unicode skip-byte stack
- current font codepage stack
- expected-format stack
- text-buffer stack
- table rows and active text tables

Python mapping:

- Use explicit Python lists as stacks.
- Store immutable, interned `TextStyle` and `ParagraphStyle` values for emitted
  AST nodes.
- Keep mutable parser-local property state separate from emitted immutable style
  objects.
- Preserve `mDestinationSkipStack` as a skip-depth counter for unsupported or
  optional destinations.

## Destinations

The C++ destination enum includes:

- normal content
- font table
- colour table
- expanded colour table
- list table
- list level text and marker
- list override table and item
- image and image name
- PDF and PDF filename
- MathML
- field, field instruction, and field result
- annotation anchors and annotation body
- footnote body
- styles table

Python mapping:

- Implement a `Destination` enum or equivalent value class.
- Preserve generic destinations needed for AST structure.
- Treat PDF, MathML, OLE-like, Qt-specific, and Scrivener-specific behaviours as
  unsupported or dropped with diagnostics.

## Text Emission

`drawText()` is responsible for destination-aware buffered text handling.

Important behaviours:

- Normal text and field-result text are inserted into the active document unless
  reading an annotation or footnote.
- Font table text is deferred until destination finalization so multi-byte font
  names are handled as a whole.
- Colour table text commits colours when `;` is encountered.
- Field instruction text is accumulated separately from field result text.
- List level text and marker destinations accumulate list metadata.
- Annotation and footnote destinations write into note-specific content.
- Unsupported or skipped destinations clear text without emitting it.

Python mapping:

- Buffer plain text in lists, not repeated string concatenation.
- Flush text into coalesced `TextRun` nodes using the current interned style.
- Route destination text to font table, colour table, field state, list metadata,
  notes, images, or diagnostics as appropriate.

## Unicode, Hex, and Codepages

Critical C++ behaviours are in `translateControlWord(...)`:

- `\ucN` sets the fallback skip byte count.
- `\uN` appends the Unicode value and skips fallback bytes.
- The reader has special recovery for malformed fallback patterns:
  - `\uN\'xx`
  - `\uN\r\n\'xx`
  - `\uN\r\'xx`
  - `\uN\n\'xx`
- `\'xx` reads one or more bytes using the current font codepage or document
  codepage.
- Font table `\cpgN` and `\fcharsetN` populate font-specific codepage state.
- Invalid or non-positive `\ansicpg` values fall back to Windows-1252.

Python mapping:

- Keep Unicode recovery isolated in `utils/unicode.py` or equivalent parser
  helpers with branch-specific fixtures.
- Implement hex decoding with font-codepage awareness.
- Emit diagnostics for invalid Unicode and hex data instead of silent loss.

## Formatting

The C++ reader maps common character controls into `QTextCharFormat`:

- bold
- italic
- underline variants
- strikethrough
- superscript and subscript
- font family and font size
- foreground, background, highlight, and expanded colour tables

Python mapping:

- Map supported inline features to `TextStyle`.
- Preserve font size as half-points in the AST.
- Preserve colours as value objects.
- Avoid Scrivener revision-level behaviour except as explicitly unsupported
  diagnostic metadata if encountered.

Paragraph controls map into `QTextBlockFormat`, with special handling around list
indentation and tables. Python should map the supported subset into
`ParagraphStyle`.

## Fields and Links

The C++ reader uses separate field destinations for instruction and result text.
On field finalization it detects `HYPERLINK "..."` instructions and applies link
formatting to the result.

Python mapping:

- Accumulate field instruction and field result separately.
- Emit `Link` inline nodes for recognised `HYPERLINK` fields.
- Emit `Field` inline nodes for unknown fields, preserving raw instruction and
  visible result in JSON.
- Do not preserve Scrivener `scrivlnk://` or `scrivcmt://` special handling as
  Scrivener-specific semantics.

## Tables

The C++ table logic is behavioural reference for the Python `TableBuilder`.

Important behaviours:

- `\intbl` and `\itapN` establish table nesting.
- `\cell` and `\nestcell` close the current cell and move the cursor to a new
  temporary cell document.
- `\row` and `\nestrow` finalize the current row.
- `\lastrow` marks the final row.
- Cell right borders define column positions.
- Later rows may retroactively widen the table or force merges of existing
  cells.
- `\clmgf`, `\clmrg`, `\clvmgf`, and `\clvmrg` drive horizontal and vertical
  merge handling.
- Malformed rows try to preserve cell content rather than discard it.

Python mapping:

- Implement `TableBuilder` before emitting `Table` AST nodes.
- Store row/cell content in temporary block containers.
- Resolve final `TableCell` coordinates, `rowspan`, `colspan`, and widths after
  enough row data is known.
- Emit malformed table diagnostics and preserve recovered text.

## Lists

The C++ reader records list table and override table definitions during parsing,
then performs a late pass over document blocks to create `QTextList` objects.

Important behaviours:

- `\listtable` creates list definitions.
- `\listoverride` maps override IDs to list IDs.
- `\lsN` stamps a paragraph with list identity in normal content.
- `\ilvlN` stamps a paragraph with list level.
- List level text and marker destinations preserve marker patterns.
- Mac-generated RTF sometimes omits paragraph indent values when they match list
  table values, so the reader backfills from list definitions.

Python mapping:

- Preserve list definitions and overrides in parser state.
- Stamp paragraphs first, assemble `ListBlock` structures in a post-pass.
- Keep table-cell list assembly isolated from top-level list assembly.

## Notes and Annotations

The C++ reader supports annotation and footnote destinations but routes much of
the behaviour through Scrivener-specific inline or inspector-note formatting.

Python mapping:

- Treat footnotes and annotations as first-class AST structures.
- Preserve author/date/id metadata where generic RTF data is available.
- Drop Scrivener inline annotation and inspector-note behaviours.

## Images

The C++ reader handles picture destinations and metadata:

- picture format: PNG, JPEG, WMF
- picture name
- source width and height
- goal width and height
- scale X/Y
- hex or binary payload

It also contains PDF and MathML-specific paths that are out of scope.

Python mapping:

- Represent images even when payload extraction is deferred.
- Preserve image metadata in JSON.
- Emit diagnostics for unsupported PDF, MathML, OLE, or unextractable image
  variants.

## Writer Mapping

Primary writer files:

- `SCRTextRtfWriter.h`
- `SCRTextRtfWriter_p.h`
- `SCRTextRtfWriter.cpp`

Important C++ writer concepts:

- `SCRTextRtfWriter::write(...)` prepares document state, builds font/colour/list
  tables, writes header groups, then processes the root frame.
- `processBlock(...)` writes paragraph boundaries, paragraph formatting, list
  metadata, then walks each `QTextFragment`.
- The writer tracks previous block and character format to emit formatting diffs.
- Links, notes, annotations, tables, images, lists, and metadata are emitted from
  Qt document structures.

Python mapping:

- Rebuild the writer as an AST traversal.
- Reuse concepts for escaping, deterministic font and colour tables, paragraph
  reset rules, list template emission, and table emission patterns.
- Do not port Qt document cloning, frame traversal, Scrivener compile/export
  modes, headers/footers, inspector note routing, or platform font substitutions.

## Test Harness Mapping

The `reference/rtftest` harness is a Qt GUI utility that loads RTF into a
`QTextDocument`, dumps block/fragment properties, and writes RTF back out.

Python mapping:

- Use its sample files as fixture seed material, not as an architecture model.
- Replace GUI inspection with pytest fixture assertions over AST, JSON, and later
  semantic roundtrips.
- Start with simple sample files, then add table merge fixtures once
  `TableBuilder` exists.

## Dropped or Deferred Paths

Drop entirely:

- Scrivener project styles as application-specific style identity.
- Scrivener inline annotation behaviour and inspector-note routing.
- Qt object/image resource handling.
- embedded PDF rendering.
- MathML.
- platform-specific colour and font helpers.
- exact `QTextDocument` fidelity.

Defer:

- advanced image extraction.
- headers and footers.
- revision tracking.
- page layout fidelity.
- stylesheet roundtripping.

## Initial Implementation Implications

The first Python implementation should proceed in this order:

1. Project skeleton and public package.
2. AST value types with `slots=True`, style interning, and semantic equality
   scaffolding.
3. Token classes and iterative lexer with offsets.
4. Parser options and diagnostics.
5. Minimal reader/parser state for plain text, paragraphs, escaped braces, bold,
   italic, and underline.
6. Fixture tests for lexer and minimal parser behaviour.

Unicode/codepage recovery should be a separate early milestone and should not be
simplified from memory.
