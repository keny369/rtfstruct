# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Golden export tests for stable JSON and Markdown output."""

import json
from pathlib import Path

from rtfstruct import parse_rtf


ROOT = Path(__file__).resolve().parents[1]


def test_golden_basic_json_export_matches_fixture() -> None:
    document = parse_rtf((ROOT / "tests" / "fixtures" / "golden_basic.rtf").read_bytes())
    expected = json.loads((ROOT / "tests" / "golden" / "golden_basic.json").read_text(encoding="utf-8"))

    assert document.to_json() == expected


def test_golden_basic_markdown_export_matches_fixture() -> None:
    document = parse_rtf((ROOT / "tests" / "fixtures" / "golden_basic.rtf").read_bytes())
    expected = (ROOT / "tests" / "golden" / "golden_basic.md").read_text(encoding="utf-8").rstrip("\n")

    assert document.to_markdown() == expected
