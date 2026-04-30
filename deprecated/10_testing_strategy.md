# Testing Strategy

## Purpose

The parser is a port of hardened production logic. Tests must protect behaviour during porting and prevent regression.

## Reference Test Corpus

Use the existing C++ test files and sample RTF files as reference material:

```text
reference/rtftest/main.cpp
reference/rtftest/rtffile.cpp
reference/rtftest/rtffile.h
reference/rtftest/rtftest.cpp
reference/rtftest/rtftest.h
reference/rtftest/rtftest.pro
reference/rtftest/test_rtf_files/
```

These files should be studied before writing equivalent Python tests.

## Test Types

### 1. Unit Tests

For pure functions:

- RTF escaping
- Markdown escaping
- Unicode decoding
- colour conversion
- twip conversion
- control word parsing
- codepage resolution

### 2. Lexer Tests

Validate tokenisation of:

- plain text
- control words
- control symbols
- nested groups
- escaped braces
- hex escapes
- Unicode escapes

### 3. Parser Fixture Tests

Each fixture should assert:

- AST structure
- text content
- inline styles
- diagnostics where expected

### 4. JSON Golden Tests

For core fixtures:

- parse RTF
- export JSON
- compare to expected JSON

JSON golden tests must come before Markdown golden tests.

### 5. Markdown Golden Tests

For each fixture:

- parse RTF
- export Markdown
- compare to expected Markdown

### 6. Writer Tests

For writer:

- construct AST manually
- write RTF
- parse output
- assert semantic equivalence

### 7. Roundtrip Tests

For selected fixtures:

```text
RTF -> AST -> RTF -> AST
```

Assert semantic equivalence, not byte equivalence.

`Document.semantic_equals()` must exist before roundtrip tests.

### 8. Malformed Input Tests

Parser must not crash on:

- unbalanced groups
- unknown control words
- invalid hex
- invalid Unicode
- missing font table
- missing colour table
- malformed table
- incomplete field
- incomplete footnote
- excessive group depth

### 9. Fuzz Tests

Fuzzing should begin from milestone 1.

Use `atheris` or another Python fuzzing tool against the reader.

Target classes:

- deeply nested groups
- invalid Unicode values
- negative `\uc`
- huge `\uc`
- invalid hex
- binary destination length mismatches
- malformed control words
- random group termination

### 10. Performance Tests

Use large generated and real-world fixtures.

Track:

- parse time
- memory usage
- output size
- pathological slowdowns

## Property-Based Testing

Use property-based tests for narrow pure logic:

- Unicode roundtrip
- hex decoding
- RTF escaping
- Markdown escaping
- twips/points/half-points conversion
- colour serialisation

Do not start with property tests over whole documents.

## Fixture Categories

```text
tests/fixtures/simple
tests/fixtures/formatting
tests/fixtures/unicode
tests/fixtures/codepages
tests/fixtures/lists
tests/fixtures/tables
tests/fixtures/notes
tests/fixtures/links
tests/fixtures/images
tests/fixtures/malformed
tests/fixtures/writer
```

## Golden File Rule

Golden files should be reviewed manually before being accepted.

Never update golden files blindly.

## Regression Rule

Every bug fix must add a fixture.
