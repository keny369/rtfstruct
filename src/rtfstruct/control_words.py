# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Control-word dispatch for the RTF parser.

This module maps lexer tokens to parser-state mutations. The dispatch table is
small for Milestone 1 but intentionally explicit so each supported RTF control
word can gain focused tests as behavior is ported from the C++ reference.
"""

from __future__ import annotations

from rtfstruct.ast import LineBreak, Tab
from rtfstruct.diagnostics import Severity
from rtfstruct.destinations import Destination
from rtfstruct.parser_state import ParserState
from rtfstruct.tokens import Token


SKIPPED_DESTINATIONS = {
    "stylesheet",
    "object",
    "header",
    "footer",
}

LIST_DESTINATIONS = {
    Destination.LIST_TABLE,
    Destination.LIST,
    Destination.LIST_LEVEL,
    Destination.LIST_OVERRIDE_TABLE,
    Destination.LIST_OVERRIDE,
}


def handle_control_symbol(state: ParserState, token: Token) -> None:
    """Handle non-alphabetic RTF control symbols.

    Args:
        state: Active parser state.
        token: Control-symbol token.
    """
    if token.text == "{":
        state.add_text("{", token.start, token.end)
    elif token.text == "}":
        state.add_text("}", token.start, token.end)
    elif token.text == "\\":
        state.add_text("\\", token.start, token.end)
    elif token.text == "~":
        state.add_text("\u00a0", token.start, token.end)
    elif token.text == "-":
        state.add_text("-", token.start, token.end)
    elif token.text == "*":
        return
    else:
        state.diagnostics.add(
            "RTF_UNSUPPORTED_CONTROL_SYMBOL",
            f"Unsupported RTF control symbol: {token.text!r}.",
            Severity.INFO,
            offset=token.start,
            control_word=token.text,
        )


def handle_hex_char(state: ParserState, token: Token) -> None:
    """Decode a hex character using the active RTF codepage.

    Args:
        state: Active parser state.
        token: Hex-character token whose text is two hexadecimal digits.
    """
    if state.skip_depth:
        return
    if state.current_destination is Destination.PICT:
        state.add_image_hex_payload(token.text)
        return
    if state.fallback_chars_to_skip:
        state.fallback_chars_to_skip -= 1
        return
    value = state.decode_hex_char(token.text, offset=token.start)
    if value is not None:
        state.add_text(value, token.start, token.end)


def handle_control_word(state: ParserState, token: Token) -> None:
    """Handle the Milestone 1 subset of RTF control words.

    Args:
        state: Active parser state.
        token: Control-word token.
    """
    word = token.text
    value = token.parameter
    is_set = (not token.has_parameter) or value != 0

    if state.skip_depth:
        return

    if word in SKIPPED_DESTINATIONS:
        state.skip_depth = 1
        return

    if word == "fonttbl":
        state.set_destination(Destination.FONT_TABLE)
        return
    if word == "colortbl":
        state.set_destination(Destination.COLOR_TABLE)
        state.color_table.clear()
        return
    if word == "listtable":
        state.start_list_table()
        return
    if word == "list":
        state.start_list_definition()
        return
    if word == "listlevel":
        state.start_list_level()
        return
    if word == "listid" and value is not None:
        state.set_current_list_id(value)
        return
    if word == "levelnfc" and value is not None:
        state.set_current_list_level_kind(value)
        return
    if word == "listoverridetable":
        state.start_list_override_table()
        return
    if word == "listoverride":
        state.start_list_override()
        return
    if word == "ls" and value is not None and state.current_destination is Destination.LIST_OVERRIDE:
        state.set_current_list_override_number(value)
        return
    if word == "info":
        state.set_destination(Destination.INFO)
        return
    if word == "pict":
        state.start_image()
        return
    if word == "pngblip":
        state.set_image_content_type("image/png")
        return
    if word in {"jpegblip", "jpgblip"}:
        state.set_image_content_type("image/jpeg")
        return
    if word == "emfblip":
        state.set_image_content_type("image/emf")
        return
    if word == "wmetafile":
        state.set_image_content_type("image/wmf")
        return
    if word == "picw" and value is not None:
        state.set_image_dimension("width_twips", value)
        return
    if word == "pich" and value is not None:
        state.set_image_dimension("height_twips", value)
        return
    if word == "picwgoal" and value is not None:
        state.set_image_dimension("goal_width_twips", value)
        return
    if word == "pichgoal" and value is not None:
        state.set_image_dimension("goal_height_twips", value)
        return
    if word == "picscalex" and value is not None:
        state.set_image_dimension("scale_x", value)
        return
    if word == "picscaley" and value is not None:
        state.set_image_dimension("scale_y", value)
        return
    if word in {"title", "subject", "author", "keywords"}:
        state.start_metadata(word)
        return
    if word == "doccomm":
        state.start_metadata("comment")
        return
    if word == "company":
        state.start_metadata("company")
        return
    if word == "field":
        state.start_field()
        return
    if word == "fldinst":
        state.start_field_instruction()
        return
    if word == "fldrslt":
        state.start_field_result()
        return
    if word == "footnote":
        state.start_footnote()
        return
    if word in {"annotation", "comment"}:
        state.start_annotation()
        return

    if word in {"rtf", "ansi", "deff", "deflang", "viewkind", "uc"}:
        if word == "uc" and value is not None:
            state.unicode_skip_bytes = max(0, value)
        return
    if word == "ansicpg" and value is not None:
        state.set_ansi_codepage(value)
        return
    if word == "u":
        append_unicode_value(state, token)
    elif word == "par":
        state.finish_paragraph()
    elif word == "trowd":
        state.start_table_row()
    elif word == "cellx" and value is not None:
        state.add_table_cell_boundary(value)
    elif word == "clmgf":
        state.mark_table_horizontal_merge_start()
    elif word == "clmrg":
        state.mark_table_horizontal_merge_continuation()
    elif word == "clvmgf":
        state.mark_table_vertical_merge_start()
    elif word == "clvmrg":
        state.mark_table_vertical_merge_continuation()
    elif word == "cell":
        state.finish_table_cell()
    elif word == "row":
        state.finish_table_row()
    elif word == "intbl":
        return
    elif word == "tab":
        state.add_inline(Tab())
    elif word == "line":
        state.add_inline(LineBreak())
    elif word == "b":
        state.set_style(bold=is_set)
    elif word == "i":
        state.set_style(italic=is_set)
    elif word in {"ul", "ulw", "uldb"}:
        state.set_style(underline=is_set)
    elif word in {"ulnone", "ul0"}:
        state.set_style(underline=False)
    elif word in {"strike", "striked"}:
        state.set_style(strikethrough=is_set)
    elif word == "super":
        state.set_style(superscript=is_set, subscript=False)
    elif word == "sub":
        state.set_style(subscript=is_set, superscript=False)
    elif word == "nosupersub":
        state.set_style(superscript=False, subscript=False)
    elif word == "plain":
        state.reset_style()
    elif word == "fs" and value is not None:
        state.set_style(font_size_half_points=value if value > 2 else 20)
    elif word == "f" and value is not None:
        state.set_current_font_id(value)
    elif word == "fcharset" and value is not None:
        state.set_current_font_charset(value)
    elif word == "red" and value is not None:
        state.set_color_component("red", value)
    elif word == "green" and value is not None:
        state.set_color_component("green", value)
    elif word == "blue" and value is not None:
        state.set_color_component("blue", value)
    elif word == "cf" and value is not None:
        state.apply_foreground_color(value)
    elif word in {"highlight", "cb"} and value is not None:
        state.apply_background_color(value, control_word=word)
    elif word == "ql":
        state.set_paragraph_style(alignment="left")
    elif word == "qc":
        state.set_paragraph_style(alignment="center")
    elif word == "qr":
        state.set_paragraph_style(alignment="right")
    elif word == "qj":
        state.set_paragraph_style(alignment="justify")
    elif word == "li" and value is not None:
        state.set_paragraph_style(left_indent_twips=value)
    elif word == "ri" and value is not None:
        state.set_paragraph_style(right_indent_twips=value)
    elif word == "fi" and value is not None:
        state.set_paragraph_style(first_line_indent_twips=value)
    elif word == "sb" and value is not None:
        state.set_paragraph_style(space_before_twips=value)
    elif word == "sa" and value is not None:
        state.set_paragraph_style(space_after_twips=value)
    elif word == "ls" and value is not None:
        state.set_paragraph_style(list_identity=value)
    elif word == "ilvl" and value is not None:
        state.set_paragraph_style(list_level=value)
    elif word == "pard":
        state.reset_paragraph_style()
    elif word == "sectd":
        return
    elif state.current_destination in LIST_DESTINATIONS:
        return
    else:
        state.diagnostics.add(
            "RTF_UNSUPPORTED_CONTROL_WORD",
            f"Unsupported RTF control word: {word}.",
            Severity.INFO,
            offset=token.start,
            control_word=word,
        )


def append_unicode_value(state: ParserState, token: Token) -> None:
    """Append a Unicode control-word value and skip fallback text.

    The C++ reference treats negative `\\u` values as signed 16-bit code units.
    This implementation preserves that early behavior while recording invalid
    scalar values as diagnostics.
    """
    value = token.parameter if token.has_parameter else ord("?")
    if value is None:
        value = ord("?")
    original_value = value
    if value < -32768 or value > 65535:
        state.diagnostics.add(
            "RTF_INVALID_UNICODE",
            f"Invalid RTF Unicode control-word value: {original_value!r}.",
            Severity.WARNING,
            offset=token.start,
            control_word=token.text,
        )
        state.add_text("\ufffd", token.start, token.end)
        state.fallback_chars_to_skip = state.unicode_skip_bytes
        return
    if value < 0:
        value += 65536
    try:
        state.add_text(chr(value), token.start, token.end)
    except ValueError:
        state.diagnostics.add(
            "RTF_INVALID_UNICODE",
            f"Invalid Unicode scalar value: {token.parameter!r}.",
            Severity.WARNING,
            offset=token.start,
            control_word=token.text,
        )
        state.add_text("\ufffd", token.start, token.end)
    state.fallback_chars_to_skip = state.unicode_skip_bytes
