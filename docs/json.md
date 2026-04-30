<!--
SPDX-License-Identifier: Apache-2.0
Copyright 2026 Lee Powell
-->
# JSON Export

JSON export preserves the structured AST shape for downstream processing. It can
include optional fields and image payloads based on `JsonOptions`.

```python
from rtfstruct import JsonOptions, parse_rtf

document = parse_rtf(r"{\rtf1\ansi Hello}")
data = document.to_json(options=JsonOptions(include_nulls=False))
```

```{eval-rst}
.. autoclass:: rtfstruct.JsonOptions
   :members:

.. automodule:: rtfstruct.json_export
   :members:
```
