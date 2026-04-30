<!--
SPDX-License-Identifier: Apache-2.0
Copyright 2026 Lee Powell
-->
# rtfstruct

`rtfstruct` is a Python 3.11+ RTF reader and writer for structured document
processing. It parses RTF into a neutral document AST, exports that structure to
JSON or Markdown, and writes deterministic RTF from the AST.

The parser is designed around explicit recovery and diagnostics, so malformed
or unusual RTF can still produce useful output while preserving warnings for
callers.

## About

rtfstruct is a standalone Python RTF parser and writer for structured document
processing.

Its primary purpose is to convert RTF into a granular, AI-ready document AST
that preserves document structure, formatting, tables, lists, links,
annotations, footnotes, images, metadata, and recoverable source detail before
exporting to JSON, Markdown, or RTF.

The implementation is informed by Lee Powell’s experience building production
C++ RTF parsing and writing infrastructure, including the mature parser and
writer he authored for Scrivener for Windows and refined through approximately
15 years of real-world use by hundreds of thousands of users.

## Current Status

This project is pre-alpha. The core reader, AST, JSON exporter, Markdown
exporter, and RTF writer are in active development, with tests covering inline
formatting, metadata, fields and links, footnotes, annotations, lists, tables,
images, Unicode/codepage recovery, diagnostics, source spans, and semantic
roundtrips.

## Installation

For local development:

```bash
python -m pip install -e ".[dev]"
```

To build the Sphinx documentation locally:

```bash
python -m pip install -e ".[docs]"
sphinx-build -b html docs docs/_build/html
```

Run the generated parsing benchmark:

```bash
python benchmarks/parse_generated.py --paragraphs 10000
```

## Basic Usage

```python
from rtfstruct import parse_rtf

document = parse_rtf(r"{\rtf1\ansi Hello, \b world\b0!}")

print(document.to_json())
print(document.to_markdown())
print(document.to_rtf())
```

Read from and write to files:

```python
from rtfstruct import read_rtf, write_rtf

document = read_rtf("input.rtf")
write_rtf(document, "output.rtf")
```

## Command Line

```bash
rtfstruct input.rtf --to markdown > output.md
rtfstruct input.rtf --to json --output output.json
rtfstruct input.rtf --to diagnostics
rtfstruct input.rtf --to rtf --output normalized.rtf
```

## Integrations

The core package includes dependency-free helpers for integration experiments:

```python
from rtfstruct.integrations import (
    convert_rtf_to_markdown,
    partition_rtf,
    to_docling_dict,
)

markdown = convert_rtf_to_markdown(r"{\rtf1\ansi Hello}")
docling_shape = to_docling_dict(r"{\rtf1\ansi Hello}")
elements = partition_rtf(r"{\rtf1\ansi Hello}")
```

## Diagnostics

Diagnostics are attached to the returned document rather than hidden in logs:

```python
from rtfstruct import parse_rtf

document = parse_rtf(r"{\rtf1\u999999?}")

for diagnostic in document.diagnostics:
    print(diagnostic.severity.value, diagnostic.code, diagnostic.message)
```

## Source Spans

Source spans are optional and can be enabled for tools that need to map AST
nodes back to source offsets:

```python
from rtfstruct import ParserOptions, parse_rtf

document = parse_rtf(
    r"{\rtf1 Hello}",
    options=ParserOptions(track_spans=True),
)
```

## Documentation

The `docs/` directory contains both the static GitHub Pages entry point and
Sphinx source documentation:

- `docs/index.html` is the standalone static documentation site for GitHub Pages.
- `docs/index.md` starts the generated Sphinx documentation.
- `docs/api.md` documents the public API.
- `docs/cli.md`, `docs/integrations.md`, and `docs/performance.md` cover the
  command line, adapter helpers, and performance guardrails.

## License

rtfstruct is licensed under the Apache License, Version 2.0. See `LICENSE` for
details.

Generated files are covered by the repository `LICENSE` unless otherwise stated.
