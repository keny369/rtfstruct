# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""RTF destination identifiers used by parser state."""

from __future__ import annotations

from enum import StrEnum


class Destination(StrEnum):
    """Supported parser destinations for early milestones."""

    NORMAL = "normal"
    FONT_TABLE = "font_table"
    COLOR_TABLE = "color_table"
    INFO = "info"
    METADATA = "metadata"
    FIELD = "field"
    FIELD_INSTRUCTION = "field_instruction"
    FIELD_RESULT = "field_result"
    FOOTNOTE = "footnote"
    ANNOTATION = "annotation"
    PICT = "pict"
    LIST_TABLE = "list_table"
    LIST = "list"
    LIST_LEVEL = "list_level"
    LIST_OVERRIDE_TABLE = "list_override_table"
    LIST_OVERRIDE = "list_override"
