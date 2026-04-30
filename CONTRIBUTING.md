<!--
SPDX-License-Identifier: Apache-2.0
Copyright 2026 Lee Powell
-->
# Contributing

`rtfstruct` is pre-alpha infrastructure software. Changes should preserve the
library's core contract: parse RTF into a neutral AST, expose diagnostics for
recoverable problems, and keep JSON output stable before widening Markdown or
writer behavior.

## Development Setup

```bash
python -m pip install -e ".[dev,docs]"
```

## Validation

Run the full validation set before preparing a change:

```bash
python -m pytest -q
sphinx-build -E -b html docs docs/_build/html
python -m pip wheel . --no-deps -w /tmp/rtfstruct-wheel
```

## Test Expectations

- Parser changes need focused unit tests and malformed-input recovery coverage.
- AST or JSON changes need golden JSON coverage where practical.
- Markdown changes need Markdown golden or exact string tests.
- Writer changes need semantic roundtrip tests.
- Public API changes need docs and `tests/test_public_api.py` coverage.

## Documentation

Python modules, classes, and functions must keep Google-style docstrings.
Markdown documentation should use the repository HTML license header.
The static GitHub Pages entry point lives at `docs/index.html`; keep its
Mermaid diagrams aligned with parser, AST, exporter, CLI, and integration
behavior.
