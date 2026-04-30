# JSON Export Contract

## Purpose

The JSON exporter converts the AST into a machine-readable representation for AI document pipelines, legal tracing, tests, and downstream tooling.

JSON export must land before Markdown export.

## Design Rules

- Export from AST only.
- Do not parse RTF during JSON export.
- Preserve structure Markdown cannot express.
- Keep output deterministic.
- Use stable type names.
- Do not leak Python object internals.
- Include diagnostics where configured.
- Include source spans only when present.

## Basic Shape

```json
{
  "type": "document",
  "metadata": {},
  "blocks": [],
  "footnotes": {},
  "annotations": {},
  "images": {},
  "diagnostics": []
}
```

## Node Shape

Every node should include:

```json
{
  "type": "paragraph",
  "style": {},
  "children": []
}
```

## Style Output

Styles should be explicit but compact.

Omit null values unless `include_nulls=True`.

## Tables

Resolved table JSON should expose explicit cell coordinates:

```json
{
  "type": "table",
  "row_count": 2,
  "col_count": 3,
  "cells": [
    {
      "row": 0,
      "col": 0,
      "rowspan": 1,
      "colspan": 2,
      "blocks": []
    }
  ]
}
```

## Lists

List JSON should preserve:

- ordered/unordered
- item nesting
- original list identity where available
- marker where available

## Fields and Links

Known hyperlink fields should produce Link nodes.

Unknown fields should produce Field nodes with:

- raw instruction
- visible result
- diagnostics where needed

## Images

Images should include metadata even when payload is omitted.

Binary payload should be configurable:

```python
JsonOptions(include_image_data=False)
```

## Diagnostics

Diagnostics should include:

- code
- message
- severity
- offset where available
- control word where available
- destination where available

## Determinism

Same AST and same options must always produce byte-equivalent JSON after stable serialisation.
