<!--
SPDX-License-Identifier: Apache-2.0
Copyright 2026 Lee Powell
-->
# Diagnostics

Diagnostics are part of the `Document` result. They are machine-readable and
designed for callers that need to surface recoverable parser warnings or errors.

```python
from rtfstruct import parse_rtf

document = parse_rtf(r"{\rtf1\u999999?}")

for diagnostic in document.diagnostics:
    print(diagnostic.severity.value, diagnostic.code, diagnostic.message)
```

```{eval-rst}
.. automodule:: rtfstruct.diagnostics
   :members:
```
