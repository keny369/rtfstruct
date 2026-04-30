<!--
SPDX-License-Identifier: Apache-2.0
Copyright 2026 Lee Powell
-->
# Integrations

`rtfstruct` keeps integrations dependency-free in the core package. The adapter
modules expose simple Python shapes that can be wrapped by MarkItDown, Docling,
or Unstructured without forcing those packages on every user.

## MarkItDown-Style Markdown

```python
from rtfstruct.integrations import convert_rtf_to_markdown

markdown = convert_rtf_to_markdown(r"{\rtf1\ansi Hello}")
```

## Docling-Style Dictionary

```python
from rtfstruct.integrations import to_docling_dict

document = to_docling_dict(r"{\rtf1\ansi Hello}")
```

## Unstructured-Style Partitioning

```python
from rtfstruct.integrations import partition_rtf

elements = partition_rtf(r"{\rtf1\ansi First\par Second}")
```

```{eval-rst}
.. automodule:: rtfstruct.integrations.markitdown
   :members:

.. automodule:: rtfstruct.integrations.docling
   :members:

.. automodule:: rtfstruct.integrations.unstructured
   :members:
```
