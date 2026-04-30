<!--
SPDX-License-Identifier: Apache-2.0
Copyright 2026 Lee Powell
-->
# Performance

`rtfstruct` uses streaming tokenization, list-backed text buffering, capped
diagnostics, and parser safety limits to avoid common malformed-input blowups.

## Guardrails

- `ParserOptions.max_group_depth` caps nested RTF groups.
- `ParserOptions.max_document_chars` caps emitted document text.
- `ParserOptions.max_diagnostics` caps retained diagnostics.
- Image payloads are captured only through explicit parser state and can be
  omitted from JSON output.

## Benchmark

A dependency-free generated corpus benchmark is available:

```bash
python benchmarks/parse_generated.py --paragraphs 10000
```

The benchmark is intentionally simple. It is meant for local regression checks
before adopting heavier benchmark tooling.
