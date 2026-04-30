# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Benchmark generated RTF parsing throughput.

This script is intentionally dependency-free. It prints a simple throughput
summary that can be used before adding heavier benchmark tooling.
"""

from __future__ import annotations

import argparse
from time import perf_counter

from rtfstruct import parse_rtf


def main() -> int:
    """Run the generated corpus parsing benchmark."""
    parser = argparse.ArgumentParser(description="Benchmark generated RTF parsing throughput.")
    parser.add_argument("--paragraphs", type=int, default=10_000, help="Number of generated paragraphs.")
    args = parser.parse_args()

    source = "{\\rtf1 " + "".join(f"Paragraph {index}\\par " for index in range(args.paragraphs)) + "}"
    started = perf_counter()
    document = parse_rtf(source)
    elapsed = perf_counter() - started

    print(f"paragraphs={len(document.blocks)}")
    print(f"seconds={elapsed:.6f}")
    print(f"paragraphs_per_second={len(document.blocks) / elapsed:.2f}")
    print(f"diagnostics={len(document.diagnostics)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
