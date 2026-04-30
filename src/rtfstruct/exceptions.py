# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Exception types for rtfstruct."""

from __future__ import annotations


class RtfError(Exception):
    """Base exception for rtfstruct errors."""


class RtfSyntaxError(RtfError):
    """Raised when input is not recognisably RTF and recovery is disabled."""
