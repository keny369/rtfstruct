<!--
SPDX-License-Identifier: Apache-2.0
Copyright 2026 Lee Powell
-->
# Markdown Export

Markdown export is intentionally lossy where Markdown cannot represent RTF
semantics directly. Options allow selected formatting to be preserved with HTML,
including colors, fonts, annotation rendering, and complex tables.

```python
from rtfstruct import MarkdownOptions, parse_rtf

document = parse_rtf(r"{\rtf1\ansi Hello}")
markdown = document.to_markdown(options=MarkdownOptions(preserve_colors=True))
```

```{eval-rst}
.. autoclass:: rtfstruct.MarkdownOptions
   :members:

.. autofunction:: rtfstruct.to_markdown

.. automodule:: rtfstruct.markdown
   :members:
```
