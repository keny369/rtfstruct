# Markdown Export Contract

## Purpose

The Markdown exporter converts the AST into readable Markdown suitable for AI ingestion, documentation workflows, and RAG pipelines.

Markdown export is lossy. Loss must be controlled, explicit, and configurable.

## Design Rules

- Export from AST only.
- Do not parse RTF during Markdown export.
- Preserve readability by default.
- Use GitHub-Flavoured Markdown where possible.
- Use inline HTML where Markdown lacks native representation.
- Do not silently discard major structures.
- Preserve unsupported details in JSON export.

## Inline Formatting

| AST Feature | Markdown Output |
|---|---|
| Bold | `**text**` |
| Italic | `*text*` |
| Bold + Italic | `***text***` |
| Strikethrough | `~~text~~` |
| Underline | `<u>text</u>` |
| Superscript | `<sup>text</sup>` |
| Subscript | `<sub>text</sub>` |
| Link | `[text](url)` |
| Line break | `<br>` or Markdown hard break |
| Tab | configurable spaces |

## Colours and Fonts

Colours and fonts are not native Markdown.

Default behaviour:

```html
<span style="color: #RRGGBB;">text</span>
<span style="background-color: #RRGGBB;">text</span>
<span style="font-family: ...;">text</span>
```

Exporter options:

```python
MarkdownOptions(
    preserve_colors=True,
    preserve_fonts=False,
    preserve_font_sizes=False,
)
```

## Footnotes

Use Markdown footnote syntax where enabled:

```markdown
Text with footnote.[^1]

[^1]: Footnote content.
```

If the footnote contains complex blocks, emit a readable block footnote.

## Annotations

Default annotation output:

```markdown
> [!NOTE]
> Annotation content
```

Alternative modes:

- HTML comments
- inline bracketed notes
- omit from Markdown but preserve in JSON

## Tables

Simple tables may use GitHub-Flavoured Markdown.

A table is simple only if:

- no rowspan
- no colspan
- every cell contains plain paragraph-compatible inline content
- no nested blocks
- no nested tables
- no multi-paragraph cells

Complex tables must use HTML table output.

This decision rule must be pinned before golden Markdown tests are written.

## Images

If image has a path:

```markdown
![alt text](path)
```

If image has extracted payload but no path:

```markdown
![image](images/image-001.png)
```

If image cannot be extracted:

```markdown
[Image: type=image/png, width=..., height=...]
```

## Lists

Support:

- ordered lists
- unordered lists
- nested lists

Maintain indentation deterministically.

## Escaping

Escape Markdown-sensitive characters in text runs unless they are deliberately emitted by the exporter.

## Determinism

The same AST and options must always produce the same Markdown.
