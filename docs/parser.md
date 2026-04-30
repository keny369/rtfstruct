<!--
SPDX-License-Identifier: Apache-2.0
Copyright 2026 Lee Powell
-->
# Parser

The parser pipeline is split into a lexer, control word dispatch, and explicit
parser state. The lexer emits structural tokens, while parser state owns style
stacks, destinations, tables, lists, images, metadata, notes, diagnostics, and
output buffering.

Use `parse_rtf()` for bytes or strings and `read_rtf()` for files.

```{eval-rst}
.. autofunction:: rtfstruct.parse_rtf
.. autofunction:: rtfstruct.read_rtf
.. autoclass:: rtfstruct.ParserOptions
   :members:
```

## Internal Pipeline

```{eval-rst}
.. automodule:: rtfstruct.lexer
   :members:

.. automodule:: rtfstruct.parser_state
   :members:

.. automodule:: rtfstruct.control_words
   :members:
```
