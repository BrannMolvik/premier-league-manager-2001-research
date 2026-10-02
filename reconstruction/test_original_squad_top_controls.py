from __future__ import annotations

from pathlib import Path
import unittest

from ea444_decoder import EA444DecodedImage
from ea_font import EAFont
from original_pmenu_chrome import PMENU_FONT_SOURCE_PATH
from original_squad_top_controls import (
    OriginalSquadTopControlsError,
    OriginalSquadTopResources,
    SQUAD_BUTTON_INITIAL_GROUPS,
    SQUAD_BUTTON_INITIAL_SOURCE_FRAMES,
    SQUAD_BUTTON_TEXT_STYLE,
    build_fresh_squad_top_render,
)


def fixture_resources() -> OriginalSquadTopResources:
    root = Path(__file__).resolve().parents[1] / "original_assets" / "source"
    font = EAFont.from_bytes((root / PMENU_FONT_SOURCE_PATH).read_bytes())
    width, height = 73, 575
    rgba = bytearray(width * height * 4)
    for source_index in range(23):
        pixel = bytes((source_index, source_index, source_index, 255))
        row = pixel * width
        for y in range(source_index * 25, (source_index + 1) * 25):
            start = y * width * 4
            rgba[start:start + width * 4] = row
    return OriginalSquadTopResources(
        EA444DecodedImage(width, height, bytes(rgba), 0, 0),
        font,
    )


class OriginalSquadTopControlsTests(unittest.TestCase):
    def test_fresh_state_uses_native_selected_and_normal_source_frames(self):
        self.assertEqual(SQUAD_BUTTON_TEXT_STYLE, 0)
        self.assertEqual(SQUAD_BUTTON_INITIAL_GROUPS, (1, 0, 0))
        self.assertEqual(SQUAD_BUTTON_INITIAL_SOURCE_FRAMES, (11, 0, 0))

        render = build_fresh_squad_top_render(fixture_resources())
        self.assertEqual(render.panel_rect, (0, 79, 800, 520))
        self.assertEqual(len(render.overlays), 6)

        by_key = {(item.control_id, item.role): item for item in render.overlays}
        selected = by_key[(3, "button")]
        self.assertEqual(
            (selected.x, selected.y, selected.width, selected.height, selected.source_index),
            (37, 171, 73, 25, 11),
        )
        self.assertEqual(by_key[(3, "text")].native_color_16, 0x0000)

        first_form = by_key[(4, "button")]
        reserve_form = by_key[(5, "button")]
        self.assertEqual((first_form.x, first_form.y, first_form.source_index), (113, 171, 0))
        self.assertEqual((reserve_form.x, reserve_form.y, reserve_form.source_index), (189, 171, 0))
        self.assertEqual(by_key[(4, "text")].native_color_16, 0xFFFF)
        self.assertEqual(by_key[(5, "text")].native_color_16, 0xFFFF)

    def test_style_zero_centers_exact_native_captions_inside_each_control(self):
        resources = fixture_resources()
        render = build_fresh_squad_top_render(resources)
        by_key = {(item.control_id, item.role): item for item in render.overlays}
        expected = {
            3: ("1ST & RES", 37),
            4: ("1ST FORM", 113),
            5: ("RES. FORM", 189),
        }
        for control_id, (text, x) in expected.items():
            overlay = by_key[(control_id, "text")]
            measured = resources.font.measure_text(text)
            self.assertEqual(overlay.original_text, text)
            self.assertEqual(overlay.x, x + (73 - measured) // 2)
            self.assertEqual(overlay.y, 174)
            self.assertGreater(overlay.width, 0)
            self.assertLessEqual(overlay.x + overlay.width, x + 73)
            self.assertLessEqual(overlay.y + overlay.height, 196)

    def test_render_rejects_unverified_resource_object(self):
        with self.assertRaisesRegex(
            OriginalSquadTopControlsError,
            "verified original resources",
        ):
            build_fresh_squad_top_render(object())


if __name__ == "__main__":
    unittest.main()
