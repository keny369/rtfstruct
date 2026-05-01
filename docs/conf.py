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

# Furo emits these on `body { }` / dark selectors in an inline stylesheet *after*
# `lumen.css`, so brand/background overrides must live here—not only in `lumen.css`.
_LUMEN_FURO_VARS: dict[str, str] = {
    "color-foreground-primary": "#e7e9ec",
    "color-foreground-secondary": "#bcc3cb",
    "color-foreground-muted": "#8e98a3",
    "color-foreground-border": "#5a6570",
    "color-background-primary": "#0b0d10",
    "color-background-secondary": "#11151a",
    "color-background-hover": "#18202a",
    "color-background-hover--transparent": "#18202a00",
    "color-background-border": "#232a33",
    "color-background-item": "#444444",
    "color-brand-primary": "#c4a882",
    "color-brand-content": "#c4a882",
    "color-brand-visited": "#9a846d",
    "color-api-background": "#141a20",
    "color-api-background-hover": "#18202a",
    "color-api-overall": "#232a33",
    "color-api-keyword": "#bcc3cb",
    "color-highlight-on-target": "rgba(196, 168, 130, 0.18)",
    "color-inline-code-background": "#141a20",
    "color-highlighted-background": "#1a222c",
    "color-highlighted-text": "#e7e9ec",
    "color-guilabel-background": "rgba(196, 168, 130, 0.12)",
    "color-guilabel-border": "rgba(196, 168, 130, 0.3)",
    "color-guilabel-text": "#e7e9ec",
    "color-admonition-background": "#141a20",
    "color-card-border": "#11151a",
    "color-card-background": "transparent",
    "color-card-marginals-background": "#18202a",
    "color-code-background": "#080a0d",
    "color-code-foreground": "#e7e9ec",
}

html_theme_options = {
    "light_css_variables": dict(_LUMEN_FURO_VARS),
    "dark_css_variables": dict(_LUMEN_FURO_VARS),
}

# Dark-friendly highlighting for both Furo “light” and dark chains (see pygments below).
pygments_style = "monokai"
pygments_dark_style = "monokai"

html_show_sphinx = False

autodoc_typehints = "description"
napoleon_google_docstring = True
napoleon_numpy_docstring = False
