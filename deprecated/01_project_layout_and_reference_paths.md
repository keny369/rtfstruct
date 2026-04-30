# Project Layout and Reference Paths

## Purpose

This document records the intended local development layout and reference source locations.

## Root Project Folder

```text
/Users/leepowell/apps/rtfstruct
```

## Reference Folder

```text
/Users/leepowell/apps/rtfstruct/reference
```

## C++ Reference Source

```text
/Users/leepowell/apps/rtfstruct/reference/cpp_src
```

Expected C++ reference files:

```text
/Users/leepowell/apps/rtfstruct/reference/cpp_src/SCRFontFileParser.cpp
/Users/leepowell/apps/rtfstruct/reference/cpp_src/SCRFontFileParser.h
/Users/leepowell/apps/rtfstruct/reference/cpp_src/SCRFontPostScriptNameManager.cpp
/Users/leepowell/apps/rtfstruct/reference/cpp_src/SCRFontPostScriptNameManager.h
/Users/leepowell/apps/rtfstruct/reference/cpp_src/SCRMacRgbHelper.cpp
/Users/leepowell/apps/rtfstruct/reference/cpp_src/SCRMacRgbHelper.h
/Users/leepowell/apps/rtfstruct/reference/cpp_src/ScrRtf.pro
/Users/leepowell/apps/rtfstruct/reference/cpp_src/SCRRtfFormatting.cpp
/Users/leepowell/apps/rtfstruct/reference/cpp_src/SCRRtfFormatting.h
/Users/leepowell/apps/rtfstruct/reference/cpp_src/SCRTextRtf.cpp
/Users/leepowell/apps/rtfstruct/reference/cpp_src/SCRTextRtf.h
/Users/leepowell/apps/rtfstruct/reference/cpp_src/SCRTextRtfCommon_base.cpp
/Users/leepowell/apps/rtfstruct/reference/cpp_src/SCRTextRtfCommon_p.h
/Users/leepowell/apps/rtfstruct/reference/cpp_src/SCRTextRtfCommon_win.cpp
/Users/leepowell/apps/rtfstruct/reference/cpp_src/SCRTextRtfCommon.cpp
/Users/leepowell/apps/rtfstruct/reference/cpp_src/SCRTextRtfReader_p.h
/Users/leepowell/apps/rtfstruct/reference/cpp_src/SCRTextRtfReader.cpp
/Users/leepowell/apps/rtfstruct/reference/cpp_src/SCRTextRtfReader.h
/Users/leepowell/apps/rtfstruct/reference/cpp_src/SCRTextRtfWriter_p.h
/Users/leepowell/apps/rtfstruct/reference/cpp_src/SCRTextRtfWriter.cpp
/Users/leepowell/apps/rtfstruct/reference/cpp_src/SCRTextRtfWriter.h
```

## C++ Test Harness

```text
/Users/leepowell/apps/rtfstruct/reference/rtftest
```

Expected C++ test harness files:

```text
/Users/leepowell/apps/rtfstruct/reference/rtftest/main.cpp
/Users/leepowell/apps/rtfstruct/reference/rtftest/rtffile.cpp
/Users/leepowell/apps/rtfstruct/reference/rtftest/rtffile.h
/Users/leepowell/apps/rtfstruct/reference/rtftest/rtftest.cpp
/Users/leepowell/apps/rtfstruct/reference/rtftest/rtftest.h
/Users/leepowell/apps/rtfstruct/reference/rtftest/rtftest.pro
```

## Reference RTF Test Files

```text
/Users/leepowell/apps/rtfstruct/reference/rtftest/test_rtf_files/sample01.rtf
/Users/leepowell/apps/rtfstruct/reference/rtftest/test_rtf_files/sample02.rtf
/Users/leepowell/apps/rtfstruct/reference/rtftest/test_rtf_files/sample03.rtf
/Users/leepowell/apps/rtfstruct/reference/rtftest/test_rtf_files/sample04.rtf
/Users/leepowell/apps/rtfstruct/reference/rtftest/test_rtf_files/sample05.rtf
/Users/leepowell/apps/rtfstruct/reference/rtftest/test_rtf_files/sample06.rtf
/Users/leepowell/apps/rtfstruct/reference/rtftest/test_rtf_files/sample07.rtf
/Users/leepowell/apps/rtfstruct/reference/rtftest/test_rtf_files/Tables-Full-Word.rtf
/Users/leepowell/apps/rtfstruct/reference/rtftest/test_rtf_files/Tables-Full.rtf
/Users/leepowell/apps/rtfstruct/reference/rtftest/test_rtf_files/Tables-MergeCol-Word.rtf
/Users/leepowell/apps/rtfstruct/reference/rtftest/test_rtf_files/Tables-MergeCol.rtf
/Users/leepowell/apps/rtfstruct/reference/rtftest/test_rtf_files/Tables-MergeRow-Word.rtf
/Users/leepowell/apps/rtfstruct/reference/rtftest/test_rtf_files/Tables-MergeRow.rtf
```

## New Python Project Structure

Recommended target layout:

```text
/Users/leepowell/apps/rtfstruct
  pyproject.toml
  README.md
  LICENSE
  NOTICE
  CONTRIBUTING.md
  docs/
  reference/
    cpp_src/
    rtftest/
  src/
    rtfstruct/
      __init__.py
      ast.py
      reader.py
      writer.py
      lexer.py
      tokens.py
      parser_state.py
      control_words.py
      destinations.py
      styles.py
      tables.py
      lists.py
      fields.py
      notes.py
      images.py
      markdown.py
      json_export.py
      diagnostics.py
      exceptions.py
      options.py
      utils/
        __init__.py
        escaping.py
        unicode.py
        colors.py
        units.py
  tests/
    fixtures/
    golden/
    test_*.py
```

## Reference Rule

The C++ files are behavioural reference material.

The Python project should extract parser concepts and tested behaviour, not preserve Qt architecture.
