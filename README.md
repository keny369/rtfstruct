<!--
SPDX-License-Identifier: Apache-2.0
Copyright 2026 Lee Powell
-->
# rtfstruct

`rtfstruct` is a Python 3.11+ RTF reader and writer for structured document
processing.

The parser is designed around explicit recovery and diagnostics, so malformed
or unusual RTF can still produce useful output while preserving warnings for
callers.

## About

`rtfstruct` parses Rich Text Format into a neutral document AST that preserves
paragraphs, inline styles, links, fields, notes, annotations, lists, tables,
images, metadata, source spans, and recoverable diagnostics.

The AST can then be exported to JSON for machines, Markdown for humans, or
deterministic RTF for roundtrip workflows.

`rtfstruct` was written by Lee Powell, who built the production C++ RTF parser
and writer used in Scrivener for Windows and Linux—pressure-tested for more than
a decade across hundreds of thousands of writers and long-form projects. That
engineering was later sold as a white-label engagement to Literature & Latte.

Today he advises executives and boards on structural AI readiness through
[Lumen & Lever](https://lumenandlever.com): establishing control over AI already
in use, clarifying exposure, and deciding whether an organisation is structurally
ready to scale before more capital goes out the door—the same discipline he
applied as architect of Scrivener and Scapple and as an enterprise architect at
Commonwealth Bank and Deutsche Bank.

`rtfstruct` applies that production-informed mindset to document ingestion for AI
pipelines, not only to board-level AI architecture.

Most AI document pipelines fail before retrieval begins. Structure is flattened.
Tables lose meaning. Lists collapse. Comments and notes disappear. Source
traceability is broken. The model is then asked to reason over damaged input.

`rtfstruct` is built for the layer most pipelines underestimate: document
ingestion before chunking, embedding, retrieval, and generation.

It is not a plain-text stripper, a Markdown converter, or a toy parser. It is
an AST-first RTF reader and writer for systems where document structure still
matters: AI ingestion, RAG, legal discovery, banking archives, forensic document
tracing, publishing, and long-form document intelligence.

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
