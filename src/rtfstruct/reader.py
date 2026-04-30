# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""RTF reader.

This module owns the public parsing entry points and the first parser state
skeleton. The implementation is intentionally small: it establishes the
state-machine shape from the C++ reference and supports Milestone 1 text,
paragraphs, escaped braces, and basic inline styles.
"""

from __future__ import annotations

from pathlib import Path

from rtfstruct.ast import Document
from rtfstruct.control_words import handle_control_symbol, handle_control_word, handle_hex_char
from rtfstruct.diagnostics import Diagnostics, Severity
from rtfstruct.exceptions import RtfSyntaxError
from rtfstruct.lexer import RtfLexer
from rtfstruct.lists import assemble_lists
from rtfstruct.options import ParserOptions
from rtfstruct.parser_state import ParserState
from rtfstruct.tokens import TokenKind


def parse_rtf(data: bytes | str, options: ParserOptions | None = None) -> Document:
    """Parse RTF data into a structured document AST.

    Args:
        data: RTF input as bytes or text. Bytes are decoded as Latin-1 for the
            skeleton reader so source bytes are preserved one-to-one.
        options: Optional parser configuration.

    Returns:
        A Document AST containing parsed blocks and diagnostics.

    Raises:
        RtfSyntaxError: Raised when input is not recognisably RTF and recovery is
            disabled.
    """
    parser_options = options or ParserOptions()
    text = data.decode("latin-1") if isinstance(data, bytes) else data
    diagnostics = Diagnostics(max_diagnostics=parser_options.max_diagnostics)
    state = ParserState(options=parser_options, diagnostics=diagnostics)

    if not text.startswith("{\\rtf"):
        message = "Input does not start with an RTF signature."
        if not parser_options.recover:
            raise RtfSyntaxError(message)
        diagnostics.add("RTF_MISSING_SIGNATURE", message, Severity.ERROR, offset=0)
        state.add_text(text, 0, len(text))
        state.finish_paragraph()
        list_ordering = state.list_ordering_by_override()
        return Document(
            blocks=assemble_lists(state.blocks, list_ordering),
            metadata=state.metadata,
            footnotes=state.footnotes,
            annotations=state.annotations,
            images=state.images,
            diagnostics=diagnostics.finalize(),
        )

    for token in RtfLexer(text):
        if token.kind is TokenKind.EOF:
            break
        if token.kind is TokenKind.GROUP_START:
            state.push_group(token)
        elif token.kind is TokenKind.GROUP_END:
            state.pop_group(token)
        elif token.kind is TokenKind.TEXT:
            state.add_text(token.text, token.start, token.end)
        elif token.kind is TokenKind.CONTROL_SYMBOL:
            handle_control_symbol(state, token)
        elif token.kind is TokenKind.HEX_CHAR:
            handle_hex_char(state, token)
        elif token.kind is TokenKind.CONTROL_WORD:
            handle_control_word(state, token)

    state.finalize_pending_table()
    state.finalize_open_contexts()
    state.finish_paragraph()
    list_ordering = state.list_ordering_by_override()
    if state.style_stack:
        diagnostics.add(
            "RTF_UNCLOSED_GROUP",
            "RTF ended before all groups were closed.",
            Severity.WARNING,
        )
    return Document(
        blocks=assemble_lists(state.blocks, list_ordering),
        metadata=state.metadata,
        footnotes=state.footnotes,
        annotations=state.annotations,
        images=state.images,
        diagnostics=diagnostics.finalize(),
    )


def read_rtf(path: str | Path, options: ParserOptions | None = None) -> Document:
    """Read an RTF file and parse it into a structured document AST.

    Args:
        path: File path to read.
        options: Optional parser configuration.

    Returns:
        Parsed Document AST.
    """
    return parse_rtf(Path(path).read_bytes(), options=options)
