# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Unicode and hex recovery tests."""

from rtfstruct import parse_rtf
from rtfstruct.ast import TextRun


def _plain_text(rtf: str) -> str:
    """Return concatenated text from the first parsed paragraph."""
    document = parse_rtf(rtf)
    return "".join(child.text for child in document.blocks[0].children if isinstance(child, TextRun))


def test_unicode_control_word_skips_plain_fallback_character() -> None:
    assert _plain_text(r"{\rtf1 Caf\u233?}") == "Café"


def test_unicode_control_word_skips_hex_fallback_character() -> None:
    assert _plain_text(r"{\rtf1 quote\u8217\'92}") == "quote’"


def test_unicode_control_word_skips_crlf_then_hex_fallback() -> None:
    assert _plain_text("{\\rtf1 quote\\u8217\r\n\\'92}") == "quote’"


def test_unicode_control_word_skips_cr_then_hex_fallback() -> None:
    assert _plain_text("{\\rtf1 quote\\u8217\r\\'92}") == "quote’"


def test_unicode_control_word_skips_lf_then_hex_fallback() -> None:
    assert _plain_text("{\\rtf1 quote\\u8217\n\\'92}") == "quote’"


def test_unicode_control_word_recovers_negative_signed_value() -> None:
    assert _plain_text(r"{\rtf1 marker\u-3?}") == "marker\ufffd"


def test_wrong_unicode_skip_value_only_skips_configured_fallback() -> None:
    assert _plain_text(r"{\rtf1\uc2 Caf\u233??}") == "Café"


def test_unicode_skip_count_applies_to_plain_characters_only() -> None:
    assert _plain_text(r"{\rtf1\uc1 quote\u8217\'92x}") == "quote’x"


def test_uc_zero_preserves_fallback_text() -> None:
    assert _plain_text(r"{\rtf1\uc0 Caf\u233?}") == "Café?"


def test_hex_character_uses_cp1252_fallback() -> None:
    assert _plain_text(r"{\rtf1 Caf\'e9}") == "Café"


def test_hex_character_uses_document_ansi_codepage() -> None:
    assert _plain_text(r"{\rtf1\ansi\ansicpg1251 \'e0}") == "а"


def test_hex_character_uses_active_font_charset() -> None:
    document = parse_rtf(r"{\rtf1{\fonttbl{\f0\fcharset204 Cyrillic;}}\ansi\ansicpg1252\f0 \'e0}")

    text = "".join(child.text for child in document.blocks[0].children if isinstance(child, TextRun))
    run = document.blocks[0].children[0]

    assert text == "а"
    assert isinstance(run, TextRun)
    assert run.style.font_family == "Cyrillic"


def test_unsupported_codepage_falls_back_with_diagnostic() -> None:
    document = parse_rtf(r"{\rtf1\ansi\ansicpg99999 \'e9}")

    text = "".join(child.text for child in document.blocks[0].children if isinstance(child, TextRun))

    assert text == "é"
    assert any(diagnostic.code == "RTF_UNSUPPORTED_CODEPAGE" for diagnostic in document.diagnostics)


def test_invalid_hex_emits_diagnostic_and_preserves_surrounding_text() -> None:
    document = parse_rtf(r"{\rtf1 a\'zzb}")

    text = "".join(child.text for child in document.blocks[0].children if isinstance(child, TextRun))

    assert text == "ab"
    assert any(diagnostic.code == "RTF_INVALID_HEX" for diagnostic in document.diagnostics)


def test_invalid_unicode_emits_replacement_and_diagnostic() -> None:
    document = parse_rtf(r"{\rtf1 a\u999999?b}")

    text = "".join(child.text for child in document.blocks[0].children if isinstance(child, TextRun))

    assert text == "a\ufffdb"
    assert any(diagnostic.code == "RTF_INVALID_UNICODE" for diagnostic in document.diagnostics)
