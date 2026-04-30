# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Diagnostics for parser, exporter, and writer recovery.

This module owns machine-readable diagnostic records and capped diagnostic
collection. It does not decide parser recovery policy; parser and writer modules
create diagnostics when they recover from malformed or unsupported input.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Severity(StrEnum):
    """Diagnostic severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    FATAL = "fatal"


@dataclass(slots=True)
class Diagnostic:
    """Machine-readable parser, exporter, or writer diagnostic.

    Attributes:
        code: Stable diagnostic code.
        message: Human-readable explanation.
        severity: Severity of the condition.
        offset: Optional byte or character offset where the condition occurred.
        control_word: Optional RTF control word associated with the diagnostic.
        destination: Optional RTF destination associated with the diagnostic.
    """

    code: str
    message: str
    severity: Severity
    offset: int | None = None
    control_word: str | None = None
    destination: str | None = None


class Diagnostics:
    """Capped and deduplicated diagnostic collector.

    The collector records the first few diagnostics for each code and suppresses
    repeated duplicates. Suppression summaries can be emitted at the end of a
    parse so repeated defects do not overwhelm downstream tooling.
    """

    def __init__(self, max_diagnostics: int = 10_000, per_code_limit: int = 20) -> None:
        """Create a diagnostics collector.

        Args:
            max_diagnostics: Maximum diagnostics to retain.
            per_code_limit: Maximum diagnostics retained for any single code.
        """
        self._max_diagnostics = max_diagnostics
        self._per_code_limit = per_code_limit
        self._items: list[Diagnostic] = []
        self._seen_by_code: dict[str, int] = {}
        self._suppressed_by_code: dict[str, int] = {}

    @property
    def items(self) -> list[Diagnostic]:
        """Return retained diagnostics in insertion order."""
        return self._items

    def add(
        self,
        code: str,
        message: str,
        severity: Severity = Severity.WARNING,
        *,
        offset: int | None = None,
        control_word: str | None = None,
        destination: str | None = None,
    ) -> None:
        """Add a diagnostic if collection limits allow it.

        Args:
            code: Stable diagnostic code.
            message: Human-readable diagnostic text.
            severity: Severity level.
            offset: Optional source offset.
            control_word: Optional related control word.
            destination: Optional active destination.
        """
        if len(self._items) >= self._max_diagnostics:
            self._suppressed_by_code[code] = self._suppressed_by_code.get(code, 0) + 1
            return

        count = self._seen_by_code.get(code, 0)
        self._seen_by_code[code] = count + 1
        if count >= self._per_code_limit:
            self._suppressed_by_code[code] = self._suppressed_by_code.get(code, 0) + 1
            return

        self._items.append(
            Diagnostic(
                code=code,
                message=message,
                severity=severity,
                offset=offset,
                control_word=control_word,
                destination=destination,
            )
        )

    def finalize(self) -> list[Diagnostic]:
        """Append suppression summaries and return retained diagnostics."""
        for code, count in sorted(self._suppressed_by_code.items()):
            if len(self._items) >= self._max_diagnostics:
                break
            self._items.append(
                Diagnostic(
                    code=f"{code}_SUPPRESSED",
                    message=f"Suppressed {count} further occurrences of {code}.",
                    severity=Severity.WARNING,
                )
            )
        return self._items
