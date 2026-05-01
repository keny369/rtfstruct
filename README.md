<!--
SPDX-License-Identifier: Apache-2.0
Copyright 2026 Lee Powell
-->
# rtfstruct

## rtfstruct

Read RTF as structure, not just text.

`rtfstruct` is a free open-source Python library for converting Rich Text Format
into a neutral document AST for structured export, including JSON, Markdown, and
RTF. It is part of **Sourcetrace by Lumen & Lever**, a local-first
document-structure layer for AI pipelines where privacy, layout, tables, source
evidence, and diagnostics matter.

Lumen & Lever: https://lumenandlever.com

`rtfstruct` is part of **Sourcetrace by Lumen & Lever**. Lumen & Lever helps
organizations establish structural control over AI exposure, including the
documents those systems ingest.

https://lumenandlever.com

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
in use, clarifying exposure, and deciding whether an organization is structurally
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

Install the latest `main` branch directly from GitHub (requires Python 3.11+):

```bash
python -m pip install "git+https://github.com/keny369/rtfstruct.git"
```

Pin a release tag (for example `v0.1.0`):

```bash
python -m pip install "git+https://github.com/keny369/rtfstruct.git@v0.1.0"
```

Or clone the repository and install from the checkout root:

```bash
git clone https://github.com/keny369/rtfstruct.git
cd rtfstruct
python -m pip install .
```

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

Published documentation is built with **Sphinx** using the [Furo](https://github.com/pradyunsg/furo) theme and a **Lumen & Lever** visual layer (`docs/_static/lumen.css`). Sources live under `docs/*.md` starting from `docs/index.md`.

**GitHub Pages:** the site is produced by the **Deploy documentation** workflow (`.github/workflows/pages.yml`), which runs `sphinx-build` and publishes `docs/_build/html`. In the repository **Settings → Pages**, set the source to **GitHub Actions** (not “Deploy from branch `/docs`”).

**Local build:**

```bash
python -m pip install -e ".[docs]"
sphinx-build -E -b html docs docs/_build/html
```

Then open `docs/_build/html/index.html`. See also `docs/api.md`, `docs/cli.md`, `docs/integrations.md`, and `docs/performance.md`.

### Published site (GitHub Pages)

The **Deploy documentation to GitHub Pages** workflow uploads the Sphinx `docs/_build/html` output. In the repository **Settings → Pages**, the **source must be GitHub Actions**, not *Deploy from a branch* `/docs`. If the source is `/docs`, GitHub runs **Jekyll** on Markdown; MyST directives such as a fenced `{toctree}` block are shown as plain code and the Lumen/Furo theme is not applied.

Under **Pages**, ensure the **GitHub Actions** workflow selected for deployment is **Deploy documentation to GitHub Pages** (not another workflow).

**First deploy:** If **Settings → Environments → `github-pages`** has required reviewers, open the **Actions** run and **approve** the deployment so the new site replaces the old one.

**Sanity check (should mention Sphinx/Furo, not Jekyll):**

```bash
curl -sS "https://keny369.github.io/rtfstruct/" | head -20
```

If you see `jekyll` in the generator meta tag, Pages is still serving a branch/Jekyll build, not this workflow’s artifact.

You can re-run the workflow manually: **Actions → Deploy documentation to GitHub Pages → Run workflow**.

## Commercial context

`rtfstruct` is free open-source software.

For organizations using RTF, PDF, or other document formats inside AI ingestion,
RAG, legal discovery, financial tracing, or internal knowledge systems,
Lumen & Lever provides document-structure review and AI control advisory work.

https://lumenandlever.com

## License

`rtfstruct` is released under the Apache License, Version 2.0.

Copyright 2026 Lee Powell.

See `LICENSE` and `NOTICE`.

Generated files are covered by the repository `LICENSE` unless otherwise stated.
