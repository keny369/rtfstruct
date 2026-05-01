# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Tests that exercise bundled reference RTF fixtures."""

from pathlib import Path

import pytest

from rtfstruct import Document, Severity, parse_rtf
from rtfstruct.ast import AnnotationRef, ImageInline, Paragraph, Tab, Table, TextRun


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "reference" / "rtftest" / "test_rtf_files"
RTF_FIXTURES = sorted(FIXTURE_DIR.glob("*.rtf"))
TABLE_FIXTURES = [path for path in RTF_FIXTURES if path.name.startswith("Tables-")]
PROPRIETARY_TERMS = ("Scrivener", "scrivener", "Scrv", "Literature", "Latte")


@pytest.mark.parametrize("path", RTF_FIXTURES, ids=lambda path: path.name)
def test_reference_rtf_fixture_parses_without_fatal_diagnostics(path: Path) -> None:
    document = parse_rtf(path.read_bytes())

    assert isinstance(document, Document)
    assert document.blocks or document.metadata != document.metadata.__class__()
    assert not any(diagnostic.severity is Severity.FATAL for diagnostic in document.diagnostics)


@pytest.mark.parametrize("path", TABLE_FIXTURES, ids=lambda path: path.name)
def test_reference_table_fixtures_produce_table_blocks(path: Path) -> None:
    document = parse_rtf(path.read_bytes())

    assert any(isinstance(block, Table) for block in document.blocks)


@pytest.mark.parametrize("path", RTF_FIXTURES, ids=lambda path: path.name)
def test_reference_rtf_fixtures_do_not_contain_proprietary_product_text(path: Path) -> None:
    source = path.read_text(encoding="latin-1")

    for term in PROPRIETARY_TERMS:
        assert term not in source


def test_sample01_covers_inline_formatting_annotation_and_image() -> None:
    document = _fixture("sample01.rtf")
    runs = _text_runs(document.blocks)

    assert any(isinstance(inline, AnnotationRef) for inline in _inlines(document.blocks))
    assert len(document.annotations) == 1
    assert any(isinstance(inline, ImageInline) for inline in _inlines(document.blocks))
    assert len(document.images) == 1
    assert any(run.style.bold and "Heading of Document" in run.text for run in runs)
    assert any(run.style.italic and "italic" in run.text for run in runs)
    assert any(run.style.underline and "underlined" in run.text for run in runs)
    assert any(run.style.foreground is not None for run in runs)


def test_sample02_covers_paragraph_styles_tabs_colors_fonts_table_and_images() -> None:
    document = _fixture("sample02.rtf")
    text = _document_text(document)
    runs = _text_runs(document.blocks)
    tables = _tables(document.blocks)

    assert "red, blue, green and yellow" in text
    assert "Courier New and Arial fonts" in text
    assert sum(run.style.bold for run in runs) >= 3
    assert sum(run.style.italic for run in runs) >= 2
    assert sum(run.style.underline for run in runs) >= 2
    assert sum(run.style.foreground is not None for run in runs) >= 4
    assert any(isinstance(inline, Tab) for inline in _inlines(document.blocks))
    assert len(document.images) == 2
    assert len(document.annotations) == 1
    assert [(table.row_count, table.col_count) for table in tables] == [(3, 6)]


def test_sample03_preserves_visible_list_markers_and_items() -> None:
    document = _fixture("sample03.rtf")
    text = _document_text(document)

    assert "List of bullets" in text
    assert "List of Empty Circles" in text
    assert "List of filled squares" in text
    assert "List of numbers" in text
    assert "•" in text
    assert "◦" in text
    assert "▪" in text
    assert "Some text three." in text


def test_sample04_preserves_annotation_and_sanitized_inline_markers() -> None:
    document = _fixture("sample04.rtf")
    text = _document_text(document)

    assert len(document.annotations) == 1
    assert "This is a comment message." in text
    assert "rtfstruct_annot" in text
    assert "rtfstruct_fn" in text
    assert "Scrv" not in text


def test_sample05_covers_full_table_layout_and_colored_cell_text() -> None:
    document = _fixture("sample05.rtf")
    tables = _tables(document.blocks)
    text = _document_text(document)

    assert [(table.row_count, table.col_count) for table in tables] == [(10, 3), (1, 3)]
    assert "Row1Col1" in text
    assert "Centered" in text
    assert "Right Just" in text
    assert "Red Cell Text" in text
    assert "Blue Cell Text" in text


def test_sample06_covers_merged_cells_and_annotation() -> None:
    document = _fixture("sample06.rtf")
    tables = _tables(document.blocks)

    assert len(document.annotations) == 1
    assert [(table.row_count, table.col_count) for table in tables] == [(3, 3)]
    assert "Merged cells" in _document_text(document)


def test_sample07_preserves_special_character_examples() -> None:
    text = _document_text(_fixture("sample07.rtf"))

    for expected in ["'", '"', "±", "£", "©", "¼", "½", "¾"]:
        assert expected in text


def test_reference_merge_table_fixtures_preserve_spans() -> None:
    merge_row = _tables(_fixture("Tables-MergeRow.rtf").blocks)[0]
    merge_col = _tables(_fixture("Tables-MergeCol.rtf").blocks)[0]

    assert any(cell.colspan == 2 for cell in merge_row.cells)
    assert any(cell.rowspan == 3 for cell in merge_col.cells)


def _fixture(name: str) -> Document:
    """Parse a named reference fixture."""
    return parse_rtf((FIXTURE_DIR / name).read_bytes())


def _tables(blocks: list[object]) -> list[Table]:
    """Return all tables in a block tree."""
    tables: list[Table] = []
    for block in blocks:
        if isinstance(block, Table):
            tables.append(block)
            for cell in block.cells:
                tables.extend(_tables(cell.blocks))
    return tables


def _inlines(blocks: list[object]) -> list[object]:
    """Return all inline nodes in a block tree."""
    inlines: list[object] = []
    for block in blocks:
        if isinstance(block, Paragraph):
            inlines.extend(block.children)
        elif isinstance(block, Table):
            for cell in block.cells:
                inlines.extend(_inlines(cell.blocks))
    return inlines


def _text_runs(blocks: list[object]) -> list[TextRun]:
    """Return all text runs in a block tree."""
    return [inline for inline in _inlines(blocks) if isinstance(inline, TextRun)]


def _document_text(document: Document) -> str:
    """Return readable text from all text runs in a document."""
    return "".join(run.text for run in _text_runs(document.blocks))
