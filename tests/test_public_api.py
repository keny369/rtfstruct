# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Tests for public package exports."""

import rtfstruct
from rtfstruct import ParserOptions, SourceSpan, parse_rtf


def test_source_span_is_public_api() -> None:
    span = SourceSpan(1, 3)

    assert span.start == 1
    assert span.end == 3
    assert "SourceSpan" in rtfstruct.__all__


def test_tracked_spans_use_public_source_span_type() -> None:
    document = parse_rtf(r"{\rtf1 Hello}", ParserOptions(track_spans=True))

    assert isinstance(document.blocks[0].span, SourceSpan)
