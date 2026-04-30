# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Deterministic fuzz-style recovery tests for malformed RTF."""

import pytest

from rtfstruct import Document, ParserOptions, RtfSyntaxError, parse_rtf


MALFORMED_CASES = [
    r"",
    r"plain text without signature",
    r"{\rtf1 unclosed",
    r"{\rtf1 unexpected}}",
    "{\\rtf1 \\u999999? invalid unicode}",
    r"{\rtf1 \'zz invalid hex}",
    r"{\rtf1{\field{\*\fldinst HYPERLINK ""https://example.test""}{\fldrslt missing close}",
    r"{\rtf1{\footnote orphan footnote",
    r"{\rtf1{\annotation orphan annotation",
    r"{\rtf1{\pict\pngblip 89504G invalid image hex}",
    r"{\rtf1\trowd\cellx100 A\cell B}",
    r"{\rtf1{\*\unknown unsupported destination}{visible text}",
]


@pytest.mark.parametrize("source", MALFORMED_CASES)
def test_malformed_inputs_do_not_crash_in_recovery_mode(source: str) -> None:
    document = parse_rtf(source)

    assert isinstance(document, Document)
    assert len(document.diagnostics) <= ParserOptions().max_diagnostics


def test_recovery_mode_respects_diagnostic_cap() -> None:
    source = r"{\rtf1" + ("}" * 100)
    document = parse_rtf(source, ParserOptions(max_diagnostics=5))

    assert len(document.diagnostics) <= 5


def test_repeated_unsupported_control_words_emit_suppression_summary() -> None:
    source = r"{\rtf1" + "".join(r"\unknown " for _ in range(30)) + "}"
    document = parse_rtf(source)

    assert any(diagnostic.code == "RTF_UNSUPPORTED_CONTROL_WORD" for diagnostic in document.diagnostics)
    assert any(diagnostic.code == "RTF_UNSUPPORTED_CONTROL_WORD_SUPPRESSED" for diagnostic in document.diagnostics)


def test_non_recovery_mode_raises_for_missing_signature() -> None:
    with pytest.raises(RtfSyntaxError):
        parse_rtf("not rtf", ParserOptions(recover=False))
