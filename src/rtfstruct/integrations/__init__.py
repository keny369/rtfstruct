# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Optional integration helpers for document-processing ecosystems."""

from rtfstruct.integrations.docling import to_docling_dict
from rtfstruct.integrations.markitdown import RtfstructMarkdownConverter, convert_rtf_to_markdown
from rtfstruct.integrations.unstructured import partition_rtf

__all__ = [
    "RtfstructMarkdownConverter",
    "convert_rtf_to_markdown",
    "partition_rtf",
    "to_docling_dict",
]
