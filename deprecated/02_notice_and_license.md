# Notice and Licence

## Recommended Licence

Use Apache License 2.0.

Apache 2.0 is the recommended licence because `rtfstruct` is infrastructure software intended for adoption by commercial and open-source AI/document-processing systems.

Do not use GPL, AGPL, or a custom licence.

## NOTICE File

Use this exact text:

```text
rtfstruct
Copyright 2026 Lee Powell

rtfstruct is a standalone Python RTF parser and writer for structured document processing.

Its primary purpose is to convert RTF into a granular, AI-ready document AST that preserves document structure, formatting, tables, lists, links, annotations, footnotes, images, metadata, and recoverable source detail before exporting to JSON, Markdown, or RTF.

The implementation is informed by Lee Powell’s experience building production C++ RTF parsing and writing infrastructure, including the mature parser and writer he authored for Scrivener for Windows and refined through approximately 15 years of real-world use by hundreds of thousands of users.
```

## Source File Header

Every Python source file should include:

```python
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell
```

## pyproject.toml Licence Field

```toml
[project]
name = "rtfstruct"
license = "Apache-2.0"
```

## README Licence Section

```markdown
## Licence

rtfstruct is released under the Apache License 2.0.

rtfstruct is a standalone Python RTF parser and writer for structured document processing. Its primary purpose is to convert RTF into a granular, AI-ready document AST that preserves document structure before exporting to JSON, Markdown, or RTF.

The implementation is informed by Lee Powell's experience building production C++ RTF parsing and writing infrastructure, including the mature parser and writer he authored for Scrivener for Windows and refined through approximately 15 years of real-world use by hundreds of thousands of users.
```
