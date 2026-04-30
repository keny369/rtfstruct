# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Escaping helpers for Markdown and RTF output.

These helpers are pure functions used by exporters and the future writer. They
do not inspect AST structure or parser state.
"""

from __future__ import annotations


_MARKDOWN_REPLACEMENTS = {
    "\\": "\\\\",
    "*": "\\*",
    "_": "\\_",
    "`": "\\`",
    "[": "\\[",
    "]": "\\]",
}


def escape_markdown_text(text: str) -> str:
    """Escape Markdown-sensitive punctuation in plain text.

    Args:
        text: Plain text to escape.

    Returns:
        Text with Markdown punctuation escaped.
    """
    return "".join(_MARKDOWN_REPLACEMENTS.get(char, char) for char in text)


def escape_rtf_text(text: str) -> str:
    """Escape plain text for an RTF document body.

    Args:
        text: Plain text to escape.

    Returns:
        RTF-safe text using Unicode escapes for non-ASCII characters.
    """
    parts: list[str] = []
    for char in text:
        codepoint = ord(char)
        if char == "\\":
            parts.append(r"\\")
        elif char == "{":
            parts.append(r"\{")
        elif char == "}":
            parts.append(r"\}")
        elif char == "\t":
            parts.append(r"\tab ")
        elif char in {"\n", "\r"}:
            parts.append(r"\line ")
        elif 0x20 <= codepoint <= 0x7E:
            parts.append(char)
        else:
            parts.extend(_unicode_escape_units(char))
    return "".join(parts)


def _unicode_escape_units(char: str) -> list[str]:
    """Return RTF Unicode escapes for one Unicode character."""
    encoded = char.encode("utf-16-le")
    escapes: list[str] = []
    for index in range(0, len(encoded), 2):
        unit = int.from_bytes(encoded[index : index + 2], "little")
        signed = unit if unit < 0x8000 else unit - 0x10000
        escapes.append(f"\\u{signed}?")
    return escapes
