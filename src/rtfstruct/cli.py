# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Command-line entry point for rtfstruct."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO

from rtfstruct.options import JsonOptions, MarkdownOptions, ParserOptions
from rtfstruct.reader import read_rtf
from rtfstruct.writer import to_rtf


def cli_version() -> str:
    """Return multi-line ``--version`` text for the CLI."""
    try:
        from importlib.metadata import version

        ver = version("rtfstruct")
    except Exception:
        ver = "0.1.0"
    return (
        f"rtfstruct {ver}\n"
        "Apache-2.0\n"
        "Copyright 2026 Lee Powell\n"
        "Part of Sourcetrace by Lumen & Lever\n"
        "https://lumenandlever.com"
    )


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser.

    Returns:
        Configured argument parser for the `rtfstruct` command.
    """
    parser = argparse.ArgumentParser(
        prog="rtfstruct",
        description="Convert RTF files to JSON, Markdown, diagnostics, or normalized RTF.",
    )
    parser.add_argument("input", type=Path, help="Input RTF file path.")
    parser.add_argument(
        "--to",
        choices=("json", "markdown", "rtf", "diagnostics"),
        default="markdown",
        help="Output format. Defaults to markdown.",
    )
    parser.add_argument("-o", "--output", type=Path, help="Optional output file. Defaults to stdout.")
    parser.add_argument(
        "--track-spans",
        action="store_true",
        help="Attach source offsets to supported AST nodes before exporting.",
    )
    parser.add_argument(
        "--include-image-data",
        action="store_true",
        help="Include base64 image payloads in JSON output.",
    )
    parser.add_argument(
        "--no-recover",
        action="store_true",
        help="Raise on unrecoverable syntax issues instead of returning diagnostics.",
    )
    parser.add_argument(
        "--max-diagnostics",
        type=int,
        default=10_000,
        help="Maximum diagnostics retained while parsing.",
    )
    parser.add_argument("--version", action="version", version=cli_version())
    return parser


def main(argv: list[str] | None = None, stdout: TextIO | None = None, stderr: TextIO | None = None) -> int:
    """Run the rtfstruct command-line interface.

    Args:
        argv: Optional argument list. Defaults to `sys.argv[1:]`.
        stdout: Optional text stream for standard output.
        stderr: Optional text stream for standard error.

    Returns:
        Process exit code.
    """
    output_stream = stdout or sys.stdout
    error_stream = stderr or sys.stderr
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        document = read_rtf(
            args.input,
            options=ParserOptions(
                recover=not args.no_recover,
                track_spans=args.track_spans,
                max_diagnostics=args.max_diagnostics,
            ),
        )
        rendered = _render_document(args.to, document, include_image_data=args.include_image_data)
    except Exception as exc:  # pragma: no cover - exact argparse display is enough for users.
        print(f"rtfstruct: {exc}", file=error_stream)
        return 1

    if args.output is not None:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, file=output_stream, end="" if rendered.endswith("\n") else "\n")
    return 0


def _render_document(output_format: str, document: object, *, include_image_data: bool = False) -> str:
    """Render a parsed document for CLI output."""
    from rtfstruct.ast import Document

    if not isinstance(document, Document):
        raise TypeError("Expected a rtfstruct Document.")

    if output_format == "json":
        return json.dumps(
            document.to_json(options=JsonOptions(include_image_data=include_image_data)),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    if output_format == "markdown":
        return document.to_markdown(options=MarkdownOptions())
    if output_format == "rtf":
        return to_rtf(document)
    if output_format == "diagnostics":
        return json.dumps(
            [
                {
                    "code": item.code,
                    "message": item.message,
                    "severity": item.severity.value,
                    "offset": item.offset,
                    "control_word": item.control_word,
                    "destination": item.destination,
                }
                for item in document.diagnostics
            ],
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    raise ValueError(f"Unsupported output format: {output_format!r}.")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
