# Public API

## Purpose

The public API must be small, stable, documented, and obvious.

## Basic Reading

```python
from rtfstruct import read_rtf

doc = read_rtf("example.rtf")
```

## Reading from Bytes

```python
from rtfstruct import parse_rtf

doc = parse_rtf(rtf_bytes)
```

## JSON Export

```python
data = doc.to_json()
```

## Markdown Export

```python
markdown = doc.to_markdown()
```

Or:

```python
from rtfstruct import to_markdown

markdown = to_markdown(doc)
```

## RTF Writing

```python
from rtfstruct import write_rtf

write_rtf(doc, "out.rtf")
```

## Options

```python
doc = read_rtf(
    "example.rtf",
    options=ParserOptions(
        recover=True,
        preserve_unknown_destinations=False,
        extract_images=True,
        track_spans=False,
    ),
)
```

```python
markdown = doc.to_markdown(
    options=MarkdownOptions(
        preserve_colors=True,
        preserve_fonts=False,
        annotations="blockquote",
        complex_tables="html",
    )
)
```

## Diagnostics

```python
for diagnostic in doc.diagnostics:
    print(diagnostic.severity, diagnostic.code, diagnostic.message)
```

## Semantic Equality

```python
assert doc1.semantic_equals(doc2)
```

## Documentation Requirement

Every public API exported from `rtfstruct.__init__` must have:

- type hints
- Google-style docstring
- README example or docs example
- unit or integration test

## Stability

Anything exported from `rtfstruct.__init__` is public API.

Internal modules may change until v1.0.
