# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Token model for the RTF lexer.

The lexer produces these lightweight tokens from raw RTF text. Tokens carry
source offsets but do not interpret formatting semantics.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class TokenKind(StrEnum):
    """RTF token categories."""

    GROUP_START = "group_start"
    GROUP_END = "group_end"
    CONTROL_WORD = "control_word"
    CONTROL_SYMBOL = "control_symbol"
    HEX_CHAR = "hex_char"
    TEXT = "text"
    EOF = "eof"


@dataclass(frozen=True, slots=True)
class Token:
    """A token emitted by the RTF lexer.

    Attributes:
        kind: Token category.
        start: Inclusive source offset.
        end: Exclusive source offset.
        text: Token text or control word name.
        parameter: Optional numeric control-word parameter.
        has_parameter: Whether the control word explicitly included a parameter.
    """

    kind: TokenKind
    start: int
    end: int
    text: str = ""
    parameter: int | None = None
    has_parameter: bool = False
