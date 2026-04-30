# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""RTF lexer.

This module converts RTF text into a stream of tokens with source offsets. It
does not interpret control word semantics or build AST nodes. Semantic handling
belongs to `reader.py` and later `control_words.py`.
"""

from __future__ import annotations

from collections.abc import Iterator

from rtfstruct.tokens import Token, TokenKind


class RtfLexer:
    """Iterative lexer for RTF input.

    The lexer avoids recursion and yields group, control, hex, text, and EOF
    tokens. It intentionally leaves malformed semantic recovery to the parser,
    while keeping tokenization predictable for large inputs.
    """

    def __init__(self, text: str) -> None:
        """Create a lexer.

        Args:
            text: RTF input decoded to text.
        """
        self._text = text
        self._length = len(text)
        self._pos = 0

    def __iter__(self) -> Iterator[Token]:
        """Yield tokens until EOF."""
        while self._pos < self._length:
            char = self._text[self._pos]
            if char == "{":
                start = self._pos
                self._pos += 1
                yield Token(TokenKind.GROUP_START, start, self._pos, char)
            elif char == "}":
                start = self._pos
                self._pos += 1
                yield Token(TokenKind.GROUP_END, start, self._pos, char)
            elif char == "\\":
                yield self._read_control()
            else:
                yield self._read_text()
        yield Token(TokenKind.EOF, self._pos, self._pos)

    def _read_text(self) -> Token:
        """Read a run of plain text up to the next structural character."""
        start = self._pos
        while self._pos < self._length and self._text[self._pos] not in "{}\\":
            self._pos += 1
        return Token(TokenKind.TEXT, start, self._pos, self._text[start : self._pos])

    def _read_control(self) -> Token:
        """Read a control word, control symbol, or hex character token."""
        start = self._pos
        self._pos += 1
        if self._pos >= self._length:
            return Token(TokenKind.CONTROL_SYMBOL, start, self._pos, "")

        char = self._text[self._pos]
        if not char.isalpha():
            self._pos += 1
            if char == "'" and self._pos + 1 <= self._length:
                hex_start = self._pos
                hex_text = self._text[hex_start : hex_start + 2]
                self._pos = min(self._pos + 2, self._length)
                return Token(TokenKind.HEX_CHAR, start, self._pos, hex_text)
            return Token(TokenKind.CONTROL_SYMBOL, start, self._pos, char)

        word_start = self._pos
        while self._pos < self._length and self._text[self._pos].isalpha():
            self._pos += 1
        word = self._text[word_start : self._pos]

        negative = False
        if self._pos < self._length and self._text[self._pos] == "-":
            negative = True
            self._pos += 1

        number_start = self._pos
        while self._pos < self._length and self._text[self._pos].isdigit():
            self._pos += 1

        has_parameter = self._pos > number_start
        parameter: int | None = None
        if has_parameter:
            parameter = int(self._text[number_start : self._pos])
            if negative:
                parameter = -parameter

        if self._pos < self._length and self._text[self._pos] == " ":
            self._pos += 1

        return Token(
            TokenKind.CONTROL_WORD,
            start,
            self._pos,
            word,
            parameter=parameter,
            has_parameter=has_parameter,
        )
