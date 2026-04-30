# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""List assembly post-pass.

RTF list structure is assembled after initial paragraph parsing. This module
implements the first conservative pass: consecutive paragraphs stamped with list
identity and level are grouped into `ListBlock` nodes. Full list-table semantics
remain a later milestone.
"""

from __future__ import annotations

from rtfstruct.ast import Block, ListBlock, ListItem, Paragraph, Table


def assemble_lists(blocks: list[Block], list_ordering: dict[int, bool] | None = None) -> list[Block]:
    """Group consecutive list-stamped paragraphs into list blocks.

    Args:
        blocks: Parsed top-level blocks before list assembly.
        list_ordering: Ordered/unordered status keyed by paragraph list identity.

    Returns:
        Blocks with consecutive list paragraphs grouped into `ListBlock` nodes.
    """
    ordering = list_ordering or {}
    assembled: list[Block] = []
    active_list: ListBlock | None = None

    for block in blocks:
        if isinstance(block, Paragraph) and block.style.list_identity is not None:
            list_id = block.style.list_identity
            if active_list is None or active_list.list_id != list_id:
                active_list = ListBlock(ordered=ordering.get(list_id, False), list_id=list_id)
                assembled.append(active_list)
            level = block.style.list_level or 0
            active_list.items.append(ListItem(blocks=[block], level=level))
        else:
            active_list = None
            if isinstance(block, Table):
                for cell in block.cells:
                    cell.blocks = assemble_lists(cell.blocks, ordering)
            assembled.append(block)

    return assembled
