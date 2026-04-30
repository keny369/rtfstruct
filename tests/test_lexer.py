# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Tests for the RTF lexer."""

from rtfstruct.lexer import RtfLexer
from rtfstruct.tokens import TokenKind


def test_lexer_emits_groups_control_words_hex_and_text() -> None:
    tokens = list(RtfLexer(r"{\rtf1\ansi hello \'e9}"))

    assert [token.kind for token in tokens] == [
        TokenKind.GROUP_START,
        TokenKind.CONTROL_WORD,
        TokenKind.CONTROL_WORD,
        TokenKind.TEXT,
        TokenKind.HEX_CHAR,
        TokenKind.GROUP_END,
        TokenKind.EOF,
    ]
    assert tokens[1].text == "rtf"
    assert tokens[1].parameter == 1
    assert tokens[1].has_parameter is True
    assert tokens[4].text == "e9"
