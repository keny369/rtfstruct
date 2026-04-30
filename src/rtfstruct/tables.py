# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Table assembly helpers for the RTF parser."""

from __future__ import annotations

from dataclasses import dataclass, field

from rtfstruct.ast import Block, Table, TableCell


@dataclass(slots=True)
class TableCellSpec:
    """Row-definition metadata for one table cell."""

    boundary_twips: int | None = None
    horizontal_merge: str | None = None
    vertical_merge: str | None = None


@dataclass(slots=True)
class TableBuilder:
    """Collect row and cell parser events before emitting a resolved table."""

    cells: list[TableCell] = field(default_factory=list)
    current_row: int = 0
    current_col: int = 0
    max_col_count: int = 0
    cell_specs: list[TableCellSpec] = field(default_factory=list)
    previous_boundary_twips: int = 0
    pending_horizontal_merge: str | None = None
    pending_vertical_merge: str | None = None

    def add_cell_boundary(self, boundary_twips: int) -> None:
        """Record the next cell right-edge boundary for the active row."""
        self.cell_specs.append(
            TableCellSpec(
                boundary_twips=boundary_twips,
                horizontal_merge=self.pending_horizontal_merge,
                vertical_merge=self.pending_vertical_merge,
            )
        )
        self.pending_horizontal_merge = None
        self.pending_vertical_merge = None

    def mark_horizontal_merge_start(self) -> None:
        """Mark the next cell definition as a horizontal merge anchor."""
        self.pending_horizontal_merge = "start"

    def mark_horizontal_merge_continuation(self) -> None:
        """Mark the next cell definition as horizontally merged with the left cell."""
        self.pending_horizontal_merge = "continuation"

    def mark_vertical_merge_start(self) -> None:
        """Mark the next cell definition as a vertical merge anchor."""
        self.pending_vertical_merge = "start"

    def mark_vertical_merge_continuation(self) -> None:
        """Mark the next cell definition as vertically merged with the cell above."""
        self.pending_vertical_merge = "continuation"

    def finish_cell(self, blocks: list[Block]) -> None:
        """Add or merge one resolved cell at the current row and column."""
        spec = self._spec_for_current_cell()
        boundary = spec.boundary_twips
        width = None
        if boundary is not None:
            width = max(0, boundary - self.previous_boundary_twips)
            self.previous_boundary_twips = boundary

        if spec.horizontal_merge == "continuation" and self.cells:
            previous = self.cells[-1]
            if previous.row == self.current_row:
                previous.colspan += 1
                previous.width_twips = _add_optional_twips(previous.width_twips, width)
                previous.blocks.extend(blocks)
                self.current_col += 1
                return

        if spec.vertical_merge == "continuation":
            anchor = self._vertical_anchor(self.current_col)
            if anchor is not None:
                anchor.rowspan += 1
                anchor.blocks.extend(blocks)
                self.current_col += 1
                return

        self.cells.append(
            TableCell(
                row=self.current_row,
                col=self.current_col,
                blocks=blocks,
                width_twips=width,
            )
        )
        self.current_col += 1

    def finish_row(self) -> None:
        """Finish the active row and prepare for another row."""
        self.max_col_count = max(self.max_col_count, self.current_col)
        self.current_row += 1
        self.current_col = 0
        self.cell_specs = []
        self.previous_boundary_twips = 0
        self.pending_horizontal_merge = None
        self.pending_vertical_merge = None

    def to_table(self) -> Table:
        """Return the resolved table represented by this builder."""
        return Table(cells=self.cells, row_count=self.current_row, col_count=self.max_col_count)

    def _spec_for_current_cell(self) -> TableCellSpec:
        """Return row-definition metadata for the active cell."""
        if self.current_col < len(self.cell_specs):
            return self.cell_specs[self.current_col]
        return TableCellSpec(
            horizontal_merge=self.pending_horizontal_merge,
            vertical_merge=self.pending_vertical_merge,
        )

    def _vertical_anchor(self, col: int) -> TableCell | None:
        """Return the active vertical merge anchor for a column."""
        for cell in reversed(self.cells):
            if cell.col <= col < cell.col + cell.colspan and cell.row + cell.rowspan == self.current_row:
                return cell
        return None


def _add_optional_twips(left: int | None, right: int | None) -> int | None:
    """Add optional twip widths, preserving unknown values."""
    if left is None or right is None:
        return left
    return left + right
