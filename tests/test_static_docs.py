# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Tests for Sphinx documentation and Lumen & Lever themed site assets."""

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_lumen_theme_static_assets_and_sphinx_config() -> None:
    """Ensure Furo + Lumen CSS wiring is present for GitHub Pages builds."""
    css = (ROOT / "docs" / "_static" / "lumen.css").read_text(encoding="utf-8")
    assert "--ll-bg:" in css
    assert "DM Serif Display" in css

    conf = (ROOT / "docs" / "conf.py").read_text(encoding="utf-8")
    assert 'html_theme = "furo"' in conf
    assert 'html_css_files = ["lumen.css"]' in conf
    assert "Sourcetrace RTF Documentation" in conf

    index = (ROOT / "docs" / "index.md").read_text(encoding="utf-8")
    assert "Sourcetrace RTF" in index
    assert "lumenandlever.com" in index
    assert "keny369.github.io" not in index  # avoid stale self-URLs in source

    assert not (ROOT / "docs" / "index.html").exists()
    assert not (ROOT / "docs" / "_templates" / "layout.html").exists()


def test_sphinx_html_build_succeeds(tmp_path: Path) -> None:
    """Smoke-test a full HTML build (Furo + MyST + autodoc paths)."""
    out = tmp_path / "html"
    env = {**dict(**__import__("os").environ), "PYTHONPATH": str(ROOT / "src")}
    result = subprocess.run(
        [sys.executable, "-m", "sphinx", "-E", "-b", "html", str(ROOT / "docs"), str(out)],
        cwd=str(ROOT),
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(result.stdout + "\n" + result.stderr)

    index_html = (out / "index.html").read_text(encoding="utf-8")
    assert "lumen.css" in index_html
    assert "furo" in index_html or "_static" in index_html
