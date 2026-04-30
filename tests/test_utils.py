# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Tests for pure utility helpers."""

from rtfstruct.utils.escaping import escape_markdown_text, escape_rtf_text
from rtfstruct.utils.units import (
    half_points_to_points,
    points_to_half_points,
    points_to_twips,
    twips_to_points,
)


def test_escape_markdown_text() -> None:
    assert escape_markdown_text(r"a*b_[x]\y") == r"a\*b\_\[x\]\\y"


def test_escape_rtf_text_escapes_structural_characters() -> None:
    assert escape_rtf_text(r"{\}") == r"\{\\\}"


def test_escape_rtf_text_emits_unicode_escapes() -> None:
    assert escape_rtf_text("é") == r"\u233?"
    assert escape_rtf_text("’") == r"\u8217?"


def test_unit_conversions() -> None:
    assert twips_to_points(240) == 12
    assert points_to_twips(12) == 240
    assert half_points_to_points(24) == 12
    assert points_to_half_points(12) == 24
