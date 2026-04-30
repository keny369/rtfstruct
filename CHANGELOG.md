<!--
SPDX-License-Identifier: Apache-2.0
Copyright 2026 Lee Powell
-->
# Changelog

All notable changes to `rtfstruct` will be documented in this file.

## 0.1.0 - Unreleased

Initial pre-alpha library surface:

- RTF lexer and parser state machine with diagnostics and recovery.
- Structured document AST with JSON, Markdown, and RTF writer output.
- Inline styles, metadata, fields, links, footnotes, annotations, lists, tables, images, and source spans.
- Semantic equality for roundtrip-focused comparisons.
- CLI entry point and dependency-free integration helper shapes.
- Sphinx documentation, reference fixture coverage, golden exports, malformed-input coverage, and packaging metadata.
