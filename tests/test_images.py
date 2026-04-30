# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Lee Powell

"""Tests for RTF picture parsing."""

from rtfstruct import JsonOptions, parse_rtf
from rtfstruct.ast import ImageInline, Paragraph


def test_parse_png_picture_metadata_and_inline_reference() -> None:
    document = parse_rtf(
        r"{\rtf1 Before {\pict\pngblip\picw10\pich20\picwgoal100\pichgoal200"
        r"\picscalex50\picscaley60 89504E47} After}"
    )

    paragraph = document.blocks[0]

    assert isinstance(paragraph, Paragraph)
    assert any(isinstance(child, ImageInline) and child.id == "img1" for child in paragraph.children)
    assert list(document.images) == ["img1"]
    image = document.images["img1"]
    assert image.content_type == "image/png"
    assert image.width_twips == 10
    assert image.height_twips == 20
    assert image.goal_width_twips == 100
    assert image.goal_height_twips == 200
    assert image.scale_x == 50
    assert image.scale_y == 60
    assert image.data == bytes.fromhex("89504E47")


def test_image_json_omits_payload_by_default() -> None:
    document = parse_rtf(r"{\rtf1{\pict\jpegblip FFD8FF}}")

    data = document.to_json()

    assert data["blocks"][0]["children"] == [{"type": "image", "id": "img1"}]
    assert data["images"]["img1"] == {
        "type": "image",
        "id": "img1",
        "content_type": "image/jpeg",
    }


def test_image_json_can_include_payload() -> None:
    document = parse_rtf(r"{\rtf1{\pict\pngblip 89504E47}}")

    assert document.to_json(JsonOptions(include_image_data=True))["images"]["img1"]["data_base64"] == "iVBORw=="


def test_image_markdown_placeholder() -> None:
    document = parse_rtf(r"{\rtf1{\pict\pngblip\picwgoal100\pichgoal200 89504E47}}")

    assert document.to_markdown() == "[Image: image/png, width=100twips, height=200twips]"


def test_semantic_equals_compares_image_metadata() -> None:
    left = parse_rtf(r"{\rtf1{\pict\pngblip 89504E47}}")
    right = parse_rtf(r"{\rtf1{\pict\jpegblip FFD8FF}}")

    assert not left.semantic_equals(right)


def test_unclosed_image_recovers_at_eof() -> None:
    document = parse_rtf(r"{\rtf1 Before {\pict\pngblip 89504E47")

    assert document.to_markdown() == "Before [Image: image/png]"
    assert document.images["img1"].data == bytes.fromhex("89504E47")
    assert any(diagnostic.code == "RTF_UNCLOSED_DESTINATION" for diagnostic in document.diagnostics)
