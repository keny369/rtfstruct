# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Sphinx configuration for rtfstruct documentation."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

project = "rtfstruct"
copyright = "2026, Lee Powell"
author = "Lee Powell"
release = "0.1.0"

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

source_suffix = {
    ".md": "markdown",
    ".rst": "restructuredtext",
}

master_doc = "index"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "furo"
html_title = "rtfstruct | Sourcetrace RTF Documentation"

html_static_path = ["_static"]
html_css_files = ["lumen.css"]

html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#c4a882",
        "color-brand-content": "#c4a882",
    },
    "dark_css_variables": {
        "color-brand-primary": "#c4a882",
        "color-brand-content": "#c4a882",
    },
}

html_show_sphinx = False

autodoc_typehints = "description"
napoleon_google_docstring = True
napoleon_numpy_docstring = False
