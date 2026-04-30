<!--
SPDX-License-Identifier: Apache-2.0
Copyright 2026 Lee Powell
-->
# Contributing

See the repository-level `CONTRIBUTING.md` for setup, validation, test, and
documentation expectations.

The short version:

```bash
python -m pytest -q
sphinx-build -E -b html docs docs/_build/html
python -m pip wheel . --no-deps -w /tmp/rtfstruct-wheel
```
