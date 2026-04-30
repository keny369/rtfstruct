# Performance Strategy

## Purpose

The original parser is fast and production-hardened. The Python implementation must preserve practical performance.

## Hard Rules

- Use `slots=True` on AST dataclasses where practical.
- Intern repeated `TextStyle` objects.
- Avoid per-character AST object creation.
- Coalesce adjacent same-style runs during emission.
- Avoid quadratic string concatenation.
- Make source spans optional.
- Cap and deduplicate diagnostics.
- Avoid recursive parsing for nested groups.
- Avoid regex-heavy logic in tight parser loops.
- Benchmark large documents.

## Text Accumulation

Do not do this:

```python
text += char
```

Use:

```python
parts.append(char)
"".join(parts)
```

## Style Interning

Repeated style objects should share identity.

Example:

```python
style = style_interner.get_or_create(
    bold=True,
    italic=False,
    font_family="Times New Roman",
)
```

## Source Spans

Default:

```python
ParserOptions(track_spans=False)
```

Spans should not be stored on every inline node unless explicitly requested.

## Parser State

Parser state should be explicit and compact.

Do not create a new style object for every character.

Only create a new run when style changes or a boundary occurs.

## Large Documents

Benchmark targets:

- 100 KB
- 1 MB
- 10 MB
- 50 MB where practical

## Streaming

Full streaming is not required for MVP, but design should not prevent future streaming.

## Profiling

Use:

- `pytest-benchmark` where useful
- `cProfile`
- `tracemalloc`
- memory profiling on large fixtures

## Performance Acceptance

The parser does not need to match C++ speed. It must avoid pathological slowness and be fast enough for AI ingestion workflows.
