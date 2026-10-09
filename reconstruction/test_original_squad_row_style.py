from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import unittest

from original_squad_row_style import (
    build_first_roster_column_heading_overlays, _rotate_heading_mask,
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
    SQUAD_SCF_FONT_ATLAS_SIZE,
    SQUAD_SCF_FONT_SOURCE_PATH,
    SQUAD_CONDITION_HIGH_RGB,
    SQUAD_CONDITION_LOW_RGB,
    SQUAD_SCF_NUMERIC_RGB,
    build_first_roster_name_overlays,
    build_first_roster_role_overlays,
    build_first_roster_scf_numeric_overlays,
    build_first_roster_shirt_number_overlays,
    select_squad_shirt_number,
    format_squad_display_name,
    format_squad_recent_form,
    format_squad_whole_number,
    load_verified_squad_row_text_resources,
    squad_condition_rgb,
    squad_name_rgb,
    squad_name_rgb_from_available_state,
    squad_role_is_preferred,
    squad_role_rgb,
)


class OriginalSquadRowStyleTests(unittest.TestCase):
    def test_direct_scf_font_owner_does_not_use_adjacent_18px_font(self):
        # 6044AC/6044F4/6044F9 bind 16px to 8CAB80; 18px binds 8BD970.
        self.assertEqual(SQUAD_SCF_FONT_SOURCE_PATH, 'Fonts/Zurich_XCn_BT_16pixel.fnt')
        self.assertEqual(SQUAD_SCF_FONT_ATLAS_SIZE, (1261, 17))
        resources = load_verified_squad_row_text_resources(
            Path(__file__).resolve().parents[1] / 'original_assets/source')
        self.assertEqual((resources.scf_font.atlas_width, resources.scf_font.atlas_height),
                         (1261, 17))

    def test_shirt_selector_preserves_primary_and_alternate_native_context(self):
        self.assertEqual(select_squad_shirt_number(registered_club_id=5,
            represented_club_id=5, primary_number=12, alternate_number=29), 12)
        self.assertEqual(select_squad_shirt_number(registered_club_id=5,
            represented_club_id=7, primary_number=12, alternate_number=29), 29)
        self.assertIsNone(select_squad_shirt_number(registered_club_id=5,
            represented_club_id=7, primary_number=12))
        for byte in (0, 40, 255):
            self.assertEqual(select_squad_shirt_number(registered_club_id=-1,
                represented_club_id=-1, primary_number=byte), byte)
        for value in (-1, 256, True, 12.0, '12'):
            with self.assertRaises(OriginalSquadRowStyleError):
                select_squad_shirt_number(registered_club_id=5,
                    represented_club_id=5, primary_number=value)
        with self.assertRaises(OriginalSquadRowStyleError):
            select_squad_shirt_number(registered_club_id=65535,
                represented_club_id=-1, primary_number=12)

    def test_shirt_number_raster_uses_original_font_centering_and_clip(self):
        from original_squad_row_style import _clip_mask, _rgb_rgba
        resources = load_verified_squad_row_text_resources(
            Path(__file__).resolve().parents[1] / 'original_assets/source')
        for value in (0, 9, 40, 255):
            with self.subTest(value=value):
                actual, = build_first_roster_shirt_number_overlays(
                    (SimpleNamespace(y=154, club_relative_assignment=value),), resources)
                text = str(value)
                font = resources.font
                x = 38 + 22 // 2 - font.measure_text(text) // 2
                y = 234 + 14 // 2 - font.native_line_height() // 2
                clipped = _clip_mask(font.render_text_alpha(text), line_x=x,
                    line_y=y, rect=(38, 234, 22, 14))
                self.assertEqual((actual.x, actual.y, actual.width, actual.height), clipped[:4])
                self.assertEqual(actual.rgba, _rgb_rgba(clipped[4], (255, 255, 255)))
                self.assertEqual(actual.text, text)
                self.assertEqual(actual.font_source_path, SQUAD_ROW_FONT_SOURCE_PATH)

    def test_shirt_numbers_withhold_unknown_context_and_reject_invalid_bytes(self):
        resources = load_verified_squad_row_text_resources(
            Path(__file__).resolve().parents[1] / 'original_assets/source')
        self.assertEqual(build_first_roster_shirt_number_overlays(
            (SimpleNamespace(y=154), SimpleNamespace(y=171, club_relative_assignment=None)),
            resources), ())
        for value in (True, -1, 256, 12.0):
            with self.assertRaises(OriginalSquadRowStyleError):
                build_first_roster_shirt_number_overlays(
                    (SimpleNamespace(y=154, club_relative_assignment=value),), resources)

    def test_rotated_heading_pixels_follow_native_decreasing_y(self):
        from ea_font import EATextMask
        rotated = _rotate_heading_mask(EATextMask(3, 2, bytes((1,2,3,4,5,6))))
        self.assertEqual((rotated.width, rotated.height, rotated.alpha),
                         (2, 3, bytes((3,6,2,5,1,4))))

    def test_native_headings_use_exact_language_font_owner_and_clipping(self):
        root = Path(__file__).resolve().parents[1] / 'original_assets/source'
        resources = load_verified_squad_row_text_resources(root)
        headings = build_first_roster_column_heading_overlays(resources)
        self.assertEqual([h.text for h in headings], ['Status','Condition','Form','Skill'])
        for local_x, heading in zip((0,23,46,69), headings):
            self.assertEqual(heading.font_source_path, SQUAD_SCF_FONT_SOURCE_PATH)
            self.assertEqual(heading.source_rgb, (255,255,255))
            self.assertGreaterEqual(heading.x, 275 + local_x)
            self.assertLessEqual(heading.x + heading.width, 297 + local_x)
            self.assertGreaterEqual(heading.y, 101)
            self.assertEqual(heading.y + heading.height,
                             200 - resources.scf_font.glyph_for_byte(32).width)
        with self.assertRaises(OriginalSquadRowStyleError):
            build_first_roster_column_heading_overlays(None)

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

    def test_partial_name_color_never_fabricates_unknown_reserve_state(self):
        self.assertEqual(
            squad_name_rgb_from_available_state(
                first_team_active=True,
                first_team_substitute=False,
            ),
            SQUAD_NAME_FIRST_TEAM_ACTIVE_RGB,
        )
        self.assertEqual(
            squad_name_rgb_from_available_state(
                first_team_active=False,
                first_team_substitute=True,
            ),
            SQUAD_NAME_FIRST_TEAM_SUBSTITUTE_RGB,
        )
        self.assertIsNone(
            squad_name_rgb_from_available_state(
                first_team_active=False,
                first_team_substitute=False,
            )
        )
        self.assertEqual(
            squad_name_rgb_from_available_state(
                first_team_active=False,
                first_team_substitute=False,
                reserve_active=False,
                reserve_substitute=False,
            ),
            SQUAD_NAME_DEFAULT_RGB,
        )

    def test_distinct_18px_name_and_16px_scf_fonts_are_verified(self):
        source_root = Path(__file__).resolve().parents[1] / "original_assets" / "source"
        resources = load_verified_squad_row_text_resources(source_root)
        self.assertEqual(
            (resources.font.atlas_width, resources.font.atlas_height),
            SQUAD_ROW_FONT_ATLAS_SIZE,
        )
        self.assertEqual(
            (resources.scf_font.atlas_width, resources.scf_font.atlas_height),
            SQUAD_SCF_FONT_ATLAS_SIZE,
        )
        self.assertTrue((source_root / SQUAD_ROW_FONT_SOURCE_PATH).is_file())
        self.assertTrue((source_root / SQUAD_SCF_FONT_SOURCE_PATH).is_file())

    def test_pscf_numeric_formats_and_condition_threshold_are_source_exact(self):
        self.assertEqual(format_squad_whole_number(75), "75")
        self.assertEqual(format_squad_recent_form(7.34), "7.3")
        self.assertEqual(format_squad_recent_form(7.35), "7.4")
        self.assertEqual(format_squad_recent_form(-1.25), "-1.3")
        self.assertEqual(squad_condition_rgb(75), SQUAD_CONDITION_LOW_RGB)
        self.assertEqual(squad_condition_rgb(76), SQUAD_CONDITION_HIGH_RGB)
        self.assertEqual(SQUAD_SCF_NUMERIC_RGB, (255, 255, 255))

    def test_first_roster_scf_numeric_raster_uses_native_side_list_geometry(self):
        source_root = Path(__file__).resolve().parents[1] / "original_assets" / "source"
        resources = load_verified_squad_row_text_resources(source_root)
        rows = (
            SimpleNamespace(
                y=154,
                condition=75,
                recent_form_average=7.35,
                current_role_rating=63,
            ),
        )
        overlays = build_first_roster_scf_numeric_overlays(rows, resources)

        self.assertEqual(tuple(item.text for item in overlays), ("75", "7.4", "63"))
        self.assertEqual(
            tuple(item.source_rgb for item in overlays),
            (SQUAD_CONDITION_LOW_RGB, SQUAD_SCF_NUMERIC_RGB, SQUAD_SCF_NUMERIC_RGB),
        )
        self.assertTrue(
            all(item.font_source_path == SQUAD_SCF_FONT_SOURCE_PATH for item in overlays)
        )
        # PSquadList first roster starts at screen x=37. Its paired CSquadSCFList
        # starts at local x=239; the three controls are x=24/47/70, width 19.
        for item, left in zip(overlays, (300, 323, 346)):
            self.assertGreaterEqual(item.x, left)
            self.assertGreaterEqual(item.y, 234)
            self.assertLessEqual(item.x + item.width, left + 19)
            self.assertLessEqual(item.y + item.height, 234 + 14)

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


    def test_first_roster_role_raster_centers_original_abbreviation(self):
        source_root = Path(__file__).resolve().parents[1] / "original_assets" / "source"
        resources = load_verified_squad_row_text_resources(source_root)
        rows = (
            SimpleNamespace(
                y=154,
                assigned_role_abbreviation="FC",
                assigned_role_rgb=(0, 0, 125),
            ),
        )
        overlays = build_first_roster_role_overlays(rows, resources)
        self.assertEqual(len(overlays), 1)
        overlay = overlays[0]
        self.assertEqual(overlay.text, "FC")
        self.assertEqual(overlay.source_rgb, (0, 0, 125))
        # First-roster role control: x=37+28, y=79+154+1, 38x14.
        self.assertGreaterEqual(overlay.x, 65)
        self.assertGreaterEqual(overlay.y, 234)
        self.assertLessEqual(overlay.x + overlay.width, 65 + 38)
        self.assertLessEqual(overlay.y + overlay.height, 234 + 14)

    def test_unknown_reserve_color_withholds_name_pixels(self):
        source_root = Path(__file__).resolve().parents[1] / "original_assets" / "source"
        resources = load_verified_squad_row_text_resources(source_root)
        rows = (
            SimpleNamespace(
                y=154,
                display_name="D. Beckham",
                display_name_rgb=None,
            ),
        )
        self.assertEqual(build_first_roster_name_overlays(rows, resources), ())


if __name__ == "__main__":
    unittest.main()
