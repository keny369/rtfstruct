# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Unit conversion helpers used by RTF parsing and writing."""

from __future__ import annotations


TWIPS_PER_POINT = 20


def twips_to_points(twips: int) -> float:
    """Convert twips to typographic points."""
    return twips / TWIPS_PER_POINT


def points_to_twips(points: float) -> int:
    """Convert typographic points to twips using deterministic rounding."""
    return round(points * TWIPS_PER_POINT)


def half_points_to_points(half_points: int) -> float:
    """Convert RTF half-point font size units to points."""
    return half_points / 2


def points_to_half_points(points: float) -> int:
    """Convert points to RTF half-point font size units."""
    return round(points * 2)
