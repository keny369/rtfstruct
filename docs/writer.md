<!--
SPDX-License-Identifier: Apache-2.0
Copyright 2026 Lee Powell
-->
# RTF Writer

The writer emits deterministic RTF from the AST. It collects document resources
such as fonts, colors, and list metadata, then walks blocks and inline nodes.

```python
from rtfstruct import parse_rtf, to_rtf, write_rtf

document = parse_rtf(r"{\rtf1\ansi Hello}")
rtf = to_rtf(document)
write_rtf(document, "output.rtf")
```

```{eval-rst}
.. autofunction:: rtfstruct.to_rtf
.. autofunction:: rtfstruct.write_rtf

.. automodule:: rtfstruct.writer
   :members:
```
