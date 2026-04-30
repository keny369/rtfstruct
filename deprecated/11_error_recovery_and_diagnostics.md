# Error Recovery and Diagnostics

## Purpose

Real-world RTF is often malformed. `rtfstruct` must recover where possible while reporting what happened.

## Design Rules

- Do not crash on recoverable malformed input.
- Do not silently corrupt structure.
- Emit diagnostics for suspicious or unsupported constructs.
- Preserve partial content where possible.
- Make diagnostics machine-readable.
- Deduplicate diagnostics by code.
- Cap diagnostics.
- Emit suppression summaries.

## Diagnostic Model

```python
@dataclass(slots=True)
class Diagnostic:
    """Parser, writer, or exporter diagnostic.

    Diagnostics are machine-readable records of recoverable parser behaviour,
    unsupported features, malformed input, or writer simplifications.
    """

    code: str
    message: str
    severity: Severity
    offset: int | None = None
    control_word: str | None = None
    destination: str | None = None
```

## Severity Levels

```python
INFO
WARNING
ERROR
FATAL
```

## Recoverable Conditions

- unknown control word
- missing optional font table entry
- missing optional colour table entry
- unclosed group at EOF
- unexpected group close
- invalid hex escape
- unsupported destination
- malformed table structure
- incomplete field
- unsupported image type

## Fatal Conditions

- input is not recognisably RTF
- binary corruption prevents tokenisation
- memory safety threshold exceeded
- nesting depth exceeds configured safety limit

## Safety Limits

```python
ParserOptions(
    max_group_depth=1000,
    max_document_chars=100_000_000,
    max_diagnostics=10_000,
)
```

## Diagnostic Deduplication

Do not allow one repeated defect to flood diagnostics.

Required behaviour:

- emit first N diagnostics per code
- suppress later duplicates
- record suppressed count per code
- emit summary diagnostic at end

Example:

```text
WARNING RTF_UNKNOWN_CONTROL_WORD: suppressed 842 further occurrences
```

## Unknown Destinations

Unknown destinations should be skipped or captured according to options.

Default:

- skip unsupported binary/object destinations
- preserve readable text destinations where safe
- emit diagnostic

## Malformed Tables

If table reconstruction fails:

- preserve cell text as paragraphs where possible
- emit warning
- do not discard text

## Malformed Fields

If link field fails:

- preserve visible field result text
- emit warning
- store raw field data where possible
