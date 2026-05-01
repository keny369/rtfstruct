# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Tests for repository license and source header conventions."""

from pathlib import Path

import pytest

from rtfstruct.cli import cli_version, main


ROOT = Path(__file__).resolve().parents[1]
PYTHON_HEADER = "# SPDX-License-Identifier: Apache-2.0\n# Copyright 2026 Lee Powell\n\n"
MARKDOWN_HEADER = "<!--\nSPDX-License-Identifier: Apache-2.0\nCopyright 2026 Lee Powell\n-->\n"
TOML_HEADER = "# SPDX-License-Identifier: Apache-2.0\n# Copyright 2026 Lee Powell\n\n"
NOTICE_TEXT = """rtfstruct
Copyright 2026 Lee Powell
rtfstruct is a free open-source Python library for reading Rich Text Format as structure, not just text.
rtfstruct converts RTF into a neutral document AST for structured export, including JSON, Markdown, and RTF. It is intended for AI ingestion, archival processing, legal workflows, legacy document conversion, and document-structure inspection.
rtfstruct is part of Sourcetrace by Lumen & Lever.
Sourcetrace is Lumen & Lever's local-first document-structure layer for AI pipelines where privacy, layout, tables, source evidence, and diagnostics matter.
Lumen & Lever:
https://lumenandlever.com
The implementation is informed by Lee Powell's prior experience building production C++ RTF parsing and writing infrastructure, including RTF infrastructure authored for Scrivener for Windows and refined through approximately 15 years of real-world use.
Licensed under the Apache License, Version 2.0.
"""


def _read(path: Path) -> str:
    """Read a repository file as UTF-8 text."""
    return path.read_text(encoding="utf-8")


def test_python_files_have_spdx_header_before_docstring() -> None:
    paths = [
        *sorted((ROOT / "src").rglob("*.py")),
        *sorted((ROOT / "tests").rglob("*.py")),
        *sorted((ROOT / "benchmarks").rglob("*.py")),
        ROOT / "docs" / "conf.py",
    ]

    for path in paths:
        text = _read(path)
        assert text.startswith(PYTHON_HEADER), path
        assert text.splitlines()[3].startswith('"""'), path


def test_markdown_files_have_html_license_header() -> None:
    paths = [
        ROOT / "README.md",
        ROOT / "CHANGELOG.md",
        ROOT / "CONTRIBUTING.md",
        ROOT / "AUTHORS.md",
        ROOT / "TRADEMARKS.md",
        ROOT / "SUPPORT.md",
        ROOT / "SECURITY.md",
        *sorted((ROOT / "docs").glob("*.md")),
    ]

    for path in paths:
        text = _read(path)
        assert text.startswith(MARKDOWN_HEADER), path


def test_pyproject_has_toml_license_header_and_metadata() -> None:
    text = _read(ROOT / "pyproject.toml")

    assert text.startswith(TOML_HEADER)
    assert 'license = "Apache-2.0"' in text
    assert 'license-files = ["LICENSE", "NOTICE"]' in text
    assert "Sourcetrace by Lumen & Lever" in text
    assert "maintainers" in text
    assert "lumen-and-lever" in text
    assert 'Documentation = "https://lumenandlever.com/tools/sourcetrace-rtf"' in text
    assert 'Source = "https://github.com/keny369/rtfstruct"' in text


def test_yaml_files_have_license_header() -> None:
    paths = sorted((ROOT / ".github").rglob("*.yml")) + sorted((ROOT / ".github").rglob("*.yaml"))

    for path in paths:
        assert _read(path).startswith("# SPDX-License-Identifier: Apache-2.0\n# Copyright 2026 Lee Powell\n\n")


def test_notice_matches_expected_attribution() -> None:
    assert _read(ROOT / "NOTICE") == NOTICE_TEXT


def test_notice_has_no_extra_license_restrictions() -> None:
    lowered = _read(ROOT / "NOTICE").lower()
    forbidden = (
        "commercial use requires",
        "must link",
        "must show a logo",
        "must advertise",
        "must not compete",
        "contact us before production",
        "written permission for commercial",
    )
    for phrase in forbidden:
        assert phrase not in lowered, phrase


def test_readme_highlights_sourcetrace_and_open_source() -> None:
    text = _read(ROOT / "README.md")
    assert "Sourcetrace" in text
    assert "Lumen & Lever" in text
    assert "free open-source" in text.lower() or "open-source" in text.lower()


def test_citation_cff_identifies_project() -> None:
    text = _read(ROOT / "CITATION.cff")
    assert text.startswith("# SPDX-License-Identifier: Apache-2.0\n# Copyright 2026 Lee Powell\n\n")
    assert "title: rtfstruct" in text
    assert "license: Apache-2.0" in text
    assert "lumenandlever.com" in text


def test_license_is_standard_apache_text_without_project_boilerplate() -> None:
    text = _read(ROOT / "LICENSE")

    assert text.startswith("Apache License\nVersion 2.0, January 2004\n")
    assert "Copyright [yyyy] [name of copyright owner]" in text
    assert "Copyright 2026 Lee Powell" not in text
    assert "rtfstruct is a standalone Python RTF parser" not in text


def test_cli_version_string_includes_license_and_attribution() -> None:
    banner = cli_version()
    assert banner.startswith("rtfstruct ")
    assert "Apache-2.0" in banner
    assert "Copyright 2026 Lee Powell" in banner
    assert "Sourcetrace" in banner
    assert "lumenandlever.com" in banner


def test_cli_version_flag_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert "rtfstruct" in capsys.readouterr().out
