# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Tests for source documentation coverage."""

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_source_modules_classes_and_functions_have_docstrings() -> None:
    missing: list[str] = []

    for path in sorted((ROOT / "src" / "rtfstruct").rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        if ast.get_docstring(tree) is None:
            missing.append(f"{path.relative_to(ROOT)}:module")
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
                if ast.get_docstring(node) is None:
                    missing.append(f"{path.relative_to(ROOT)}:{node.name}")

    assert missing == []
