# Extra Considerations

## Security

RTF is an untrusted input format in many environments.

Even without OLE, PDF, and MathML support, the parser must protect against:

- deep nesting
- huge claimed binary payloads
- pathological control-word streams
- memory blowups
- decompression-style amplification patterns
- enormous image payloads
- excessive diagnostics
- untrusted filenames or paths inside image metadata

## CLI Tool

A CLI should be added after the library API stabilises.

Example:

```bash
rtfstruct input.rtf --to json > out.json
rtfstruct input.rtf --to markdown > out.md
rtfstruct input.rtf --diagnostics
```

## Corpus Strategy

Build a private and public fixture corpus.

Public corpus:

- hand-written minimal fixtures
- generated RTF fixtures
- non-sensitive sample files

Private corpus:

- real-world ugly RTF
- legal samples
- medical samples
- old Word samples
- WordPad-generated RTF
- Outlook-generated RTF
- LibreOffice-generated RTF
- TextEdit-generated RTF
- Scrivener-generated RTF if appropriate

## Compatibility Matrix

Test output against:

- Microsoft Word
- LibreOffice
- Apple TextEdit where relevant
- WordPad legacy output where available
- Pandoc as comparison, not dependency

## Documentation Examples

Every supported feature should have:

- RTF input
- AST/JSON output
- Markdown output
- RTF writer note if supported

## Versioning

Before 1.0:

- AST may change
- public API may change
- JSON shape may change

After 1.0:

- public API stable
- JSON contract versioned
- AST migrations documented

## Integration Path

Best sequence:

1. standalone library
2. CLI
3. MarkItDown plugin
4. Docling adapter or PR
5. Unstructured partitioner exploration
6. LangChain/LlamaIndex loaders only if demand appears

## Strategic Use

This library can function as infrastructure for legal document intelligence, DataVac-style local pipelines, AI ingestion systems, and general document conversion.

It should remain general-purpose enough for open source, but the test suite should include legal/forensic document behaviours.
