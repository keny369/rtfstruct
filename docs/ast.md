<!--
SPDX-License-Identifier: Apache-2.0
Copyright 2026 Lee Powell
-->
# Document AST

The AST is the canonical representation between the reader, exporters, and RTF
writer. It is intentionally independent of the original RTF token stream and of
any one output format.

## Core Nodes

Documents contain block nodes such as paragraphs, lists, and tables. Paragraphs
contain inline nodes such as text runs, fields, links, references, tabs, line
breaks, and images.

## Semantic Equality

`Document.semantic_equals()` compares document meaning rather than incidental
source details. It coalesces adjacent compatible text runs and ignores source
spans, while still comparing structure, styles, metadata, notes, images, tables,
lists, and paragraph formatting.

```{eval-rst}
.. automodule:: rtfstruct.ast
   :members:
```
