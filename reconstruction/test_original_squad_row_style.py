from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import unittest

from original_squad_row_style import (
    OriginalSquadRowStyleError,
    SQUAD_NAME_DEFAULT_RGB,
    SQUAD_NAME_FIRST_TEAM_ACTIVE_RGB,
    SQUAD_NAME_FIRST_TEAM_SUBSTITUTE_RGB,
    SQUAD_NAME_RESERVE_ACTIVE_RGB,
    SQUAD_NAME_RESERVE_SUBSTITUTE_RGB,
    SQUAD_ROLE_OUT_OF_POSITION_RGB,
    SQUAD_ROLE_PREFERRED_RGB,
    SQUAD_ROW_FONT_ATLAS_SIZE,
    SQUAD_ROW_FONT_SOURCE_PATH,
    build_first_roster_name_overlays,
    format_squad_display_name,
    load_verified_squad_row_text_resources,
    squad_name_rgb,
    squad_role_is_preferred,
    squad_role_rgb,
)


class OriginalSquadRowStyleTests(unittest.TestCase):
    def test_native_style_zero_display_name_formatter(self):
        self.assertEqual(format_squad_display_name("David", "Beckham"), "D. Beckham")
        self.assertEqual(format_squad_display_name("-Alias", "Ronaldo"), "Ronaldo")
        with self.assertRaises(OriginalSquadRowStyleError):
            format_squad_display_name("", "Surname")

    def test_role_color_uses_low_five_bit_selected_code_and_three_source_bytes(self):
        self.assertTrue(squad_role_is_preferred(0x24, (4, 7, 9)))
        self.assertEqual(squad_role_rgb(0x24, (4, 7, 9)), SQUAD_ROLE_PREFERRED_RGB)
        self.assertEqual(squad_role_rgb(5, (4, 7, 9)), SQUAD_ROLE_OUT_OF_POSITION_RGB)
        with self.assertRaises(OriginalSquadRowStyleError):
            squad_role_is_preferred(4, (4, 7))

    def test_name_color_preserves_native_predicate_precedence(self):
        cases = (
            ((True, True, True, True), SQUAD_NAME_FIRST_TEAM_ACTIVE_RGB),
            ((False, True, True, True), SQUAD_NAME_FIRST_TEAM_SUBSTITUTE_RGB),
            ((False, False, True, True), SQUAD_NAME_RESERVE_ACTIVE_RGB),
            ((False, False, False, True), SQUAD_NAME_RESERVE_SUBSTITUTE_RGB),
            ((False, False, False, False), SQUAD_NAME_DEFAULT_RGB),
        )
        for states, expected in cases:
            with self.subTest(states=states):
                self.assertEqual(
                    squad_name_rgb(
                        first_team_active=states[0],
                        first_team_substitute=states[1],
                        reserve_active=states[2],
                        reserve_substitute=states[3],
                    ),
                    expected,
                )

    def test_exact_imported_18px_squad_font_is_verified(self):
        source_root = Path(__file__).resolve().parents[1] / "original_assets" / "source"
        resources = load_verified_squad_row_text_resources(source_root)
        self.assertEqual(
            (resources.font.atlas_width, resources.font.atlas_height),
            SQUAD_ROW_FONT_ATLAS_SIZE,
        )
        self.assertTrue((source_root / SQUAD_ROW_FONT_SOURCE_PATH).is_file())

    def test_first_roster_name_raster_stays_inside_native_name_control(self):
        source_root = Path(__file__).resolve().parents[1] / "original_assets" / "source"
        resources = load_verified_squad_row_text_resources(source_root)
        rows = (
            SimpleNamespace(
                y=154,
                display_name="D. Beckham",
                display_name_rgb=(217, 210, 62),
            ),
        )
        overlays = build_first_roster_name_overlays(rows, resources)
        self.assertEqual(len(overlays), 1)
        overlay = overlays[0]
        self.assertEqual(overlay.text, "D. Beckham")
        self.assertEqual(overlay.source_rgb, (217, 210, 62))
        self.assertGreaterEqual(overlay.x, 113)
        self.assertGreaterEqual(overlay.y, 234)
        self.assertLessEqual(overlay.x + overlay.width, 113 + 144)
        self.assertLessEqual(overlay.y + overlay.height, 234 + 14)


if __name__ == "__main__":
    unittest.main()
