# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Tests for repository license and source header conventions."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON_HEADER = "# SPDX-License-Identifier: Apache-2.0\n# Copyright 2026 Lee Powell\n\n"
MARKDOWN_HEADER = "<!--\nSPDX-License-Identifier: Apache-2.0\nCopyright 2026 Lee Powell\n-->\n"
TOML_HEADER = "# SPDX-License-Identifier: Apache-2.0\n# Copyright 2026 Lee Powell\n\n"
NOTICE_TEXT = """rtfstruct
Copyright 2026 Lee Powell
This product includes software developed by Lee Powell.
rtfstruct is a standalone Python RTF parser and writer for structured document processing. It converts RTF into a document AST for structured export, including JSON, Markdown, and RTF.
The implementation is informed by Lee Powell’s prior experience building production C++ RTF parsing and writing infrastructure, including RTF infrastructure authored for Scrivener for Windows and refined through approximately 15 years of real-world use.
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


def test_yaml_files_have_license_header() -> None:
    paths = sorted((ROOT / ".github").rglob("*.yml")) + sorted((ROOT / ".github").rglob("*.yaml"))

    for path in paths:
        assert _read(path).startswith("# SPDX-License-Identifier: Apache-2.0\n# Copyright 2026 Lee Powell\n\n")


def test_notice_is_short_attribution_text() -> None:
    assert _read(ROOT / "NOTICE") == NOTICE_TEXT


def test_license_is_standard_apache_text_without_project_boilerplate() -> None:
    text = _read(ROOT / "LICENSE")

    assert text.startswith("Apache License\nVersion 2.0, January 2004\n")
    assert "Copyright [yyyy] [name of copyright owner]" in text
    assert "Copyright 2026 Lee Powell" not in text
    assert "rtfstruct is a standalone Python RTF parser" not in text
