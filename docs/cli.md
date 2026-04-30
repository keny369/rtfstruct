<!--
SPDX-License-Identifier: Apache-2.0
Copyright 2026 Lee Powell
-->
# Command Line

The `rtfstruct` command converts RTF files to Markdown, JSON, diagnostics, or
normalized RTF.

```bash
rtfstruct input.rtf --to markdown > output.md
rtfstruct input.rtf --to json --output output.json
rtfstruct input.rtf --to diagnostics
rtfstruct input.rtf --to rtf --output normalized.rtf
```

Use `--track-spans` when JSON output should include source offsets for supported
AST nodes.

```bash
rtfstruct input.rtf --to json --track-spans
```

```{eval-rst}
.. automodule:: rtfstruct.cli
   :members:
```
