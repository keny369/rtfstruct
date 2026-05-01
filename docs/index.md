<!--
SPDX-License-Identifier: Apache-2.0
Copyright 2026 Lee Powell
-->
# rtfstruct

RTF structure extraction for Sourcetrace RTF.

`rtfstruct` reads RTF into a neutral document AST, exports that structure to JSON
and Markdown, and writes deterministic RTF from the AST.

Part of [Sourcetrace](https://lumenandlever.com/tools) by [Lumen & Lever](https://lumenandlever.com).
Sourcetrace RTF is the public product line; `rtfstruct` is the Apache-2.0 Python library behind it.

Product page: [Sourcetrace RTF](https://lumenandlever.com/tools/sourcetrace-rtf) · Source: [GitHub](https://github.com/keny369/rtfstruct)

```{toctree}
:maxdepth: 2
:caption: User Guide

api
cli
ast
parser
json
markdown
writer
diagnostics
integrations
performance
contributing
```
