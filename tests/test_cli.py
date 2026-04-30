# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Tests for the rtfstruct command-line interface."""

import json
from pathlib import Path

from rtfstruct.cli import main


def test_cli_exports_markdown_to_stdout(tmp_path: Path, capsys) -> None:
    input_path = tmp_path / "input.rtf"
    input_path.write_text(r"{\rtf1\ansi Hello \b world\b0}", encoding="utf-8")

    exit_code = main([str(input_path), "--to", "markdown"])

    assert exit_code == 0
    assert capsys.readouterr().out == "Hello **world**\n"


def test_cli_exports_json_to_file(tmp_path: Path) -> None:
    input_path = tmp_path / "input.rtf"
    output_path = tmp_path / "output.json"
    input_path.write_text(r"{\rtf1\ansi Hello}", encoding="utf-8")

    exit_code = main([str(input_path), "--to", "json", "--track-spans", "--output", str(output_path)])

    assert exit_code == 0
    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert data["blocks"][0]["children"][0]["text"] == "Hello"
    assert data["blocks"][0]["span"] == {"start": 12, "end": 17}


def test_cli_exports_diagnostics(tmp_path: Path, capsys) -> None:
    input_path = tmp_path / "input.rtf"
    input_path.write_text("not rtf", encoding="utf-8")

    exit_code = main([str(input_path), "--to", "diagnostics"])

    assert exit_code == 0
    diagnostics = json.loads(capsys.readouterr().out)
    assert diagnostics[0]["code"] == "RTF_MISSING_SIGNATURE"


def test_cli_returns_error_for_missing_file(tmp_path: Path, capsys) -> None:
    exit_code = main([str(tmp_path / "missing.rtf")])

    assert exit_code == 1
    assert "rtfstruct:" in capsys.readouterr().err
