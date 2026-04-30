# Documentation and Commenting Standard

## Purpose

All code must be documented well enough for a standard Python documentation engine to generate useful API documentation.

The default documentation standard is Google-style Python docstrings rendered by Sphinx, using Napoleon.

## Required Documentation Engine

Use:

```text
Sphinx
sphinx.ext.autodoc
sphinx.ext.napoleon
sphinx.ext.viewcode
myst-parser
```

Optional later:

```text
sphinx-autodoc-typehints
```

## Required Docstring Style

Use Google-style docstrings.

Example:

```python
def parse_rtf(data: bytes | str, options: ParserOptions | None = None) -> Document:
    """Parse RTF data into a structured document AST.

    Args:
        data: RTF input as bytes or text.
        options: Optional parser configuration.

    Returns:
        A Document AST containing parsed blocks, metadata, notes, images, and diagnostics.

    Raises:
        RtfSyntaxError: Raised only when input is not recognisably RTF or recovery is disabled.
    """
```

## Module Docstrings

Every module must have a module docstring explaining:

- what the module owns
- what it does not own
- key invariants
- relationship to parser pipeline

Example:

```python
"""RTF lexer.

This module converts raw RTF bytes or text into a stream of tokens.
It does not interpret formatting semantics or build AST nodes. Semantic handling
belongs to parser_state.py and control_words.py.
"""
```

## Class Docstrings

Every public class must document:

- purpose
- key fields
- invariants
- mutability
- performance considerations where relevant

Example:

```python
@dataclass(slots=True)
class TableBuilder:
    """Incrementally resolves RTF table rows and merged cells.

    The builder mirrors the behaviour of the reference C++ parser where table
    width and column count may be discovered after earlier rows have already
    been parsed.

    The builder is internal. It emits a resolved Table AST with explicit row,
    column, rowspan, and colspan coordinates.
    """
```

## Function Comments

Prefer clear docstrings over excessive inline comments.

Inline comments should explain why, not what.

Bad:

```python
i += 1  # increment i
```

Good:

```python
# Some RTF writers emit a hex fallback after \u even when \uc is wrong.
# Preserve the reference parser's recovery behaviour.
```

## Public API Documentation

Every public API exported from `rtfstruct.__init__` must have:

- type hints
- docstring
- example in README or docs
- tests

## Internal API Documentation

Internal functions must still be documented when they carry parser behaviour, especially:

- Unicode recovery
- hex decoding
- codepage handling
- table merging
- list post-pass assembly
- field parsing
- diagnostic suppression
- style interning

## Documentation Coverage Requirement

The agent should maintain documentation for:

- all public classes
- all public functions
- all parser options
- all exporter options
- all diagnostics
- all AST node types

## Docs Folder

Recommended docs structure:

```text
docs/
  index.md
  api.md
  ast.md
  parser.md
  markdown.md
  json.md
  writer.md
  diagnostics.md
  performance.md
  contributing.md
```

## Build Command

Recommended command once Sphinx is configured:

```bash
sphinx-build -b html docs docs/_build/html
```

## Agent Instruction

All generated Python code must be fully commented and documented using Google-style Python docstrings suitable for Sphinx autodoc with Napoleon.

This does not mean noisy comments on every line. It means complete documentation for modules, public classes, public methods, parser invariants, edge-case handling, and complex internal logic.
