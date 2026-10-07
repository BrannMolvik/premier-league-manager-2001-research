"""Gate-13 modernization Settings state/visual contract tests."""
from __future__ import annotations

from pathlib import Path
import unittest

from front_end_settings import (
    FrontEndSettings,
    SETTINGS_BACK_RECT,
    SETTINGS_FULLSCREEN_RECT,
    SETTINGS_MENU_RECT,
    SETTINGS_PROFILE_RECT,
    candidate_settings_event,
    load_source_styled_settings_resources,
    settings_surface_actions,
    start_menu_settings_action,
)
from front_end_state import (
    FrontEndScreen,
    ModernStartMenuControl,
    SettingsControl,
)
from original_pstartmenu_resources import ZURICH_FONT20_SHA256
from hashlib import sha256


class FrontEndSettingsTests(unittest.TestCase):
    def test_default_is_original_baseline_and_reset_is_idempotent(self):
        settings = FrontEndSettings()
        self.assertTrue(settings.fullscreen)
        self.assertTrue(settings.original_baseline)
        self.assertEqual(settings.profile_name, "Original")

        settings.toggle_fullscreen()
        self.assertFalse(settings.fullscreen)
        self.assertFalse(settings.original_baseline)
        self.assertEqual(settings.profile_name, "Custom")

        settings.reset_original()
        self.assertTrue(settings.fullscreen)
        self.assertTrue(settings.original_baseline)
        settings.reset_original()
        self.assertTrue(settings.original_baseline)

    def test_intentional_modern_geometry_does_not_move_original_controls(self):
        menu = start_menu_settings_action()
        self.assertEqual(menu.event, int(ModernStartMenuControl.SETTINGS))
        self.assertEqual(menu.rect, SETTINGS_MENU_RECT)
        self.assertEqual((menu.rect.x, menu.rect.y, menu.rect.width, menu.rect.height),
                         (355, 508, 169, 25))

        actions = settings_surface_actions(FrontEndSettings())
        self.assertEqual(
            tuple(item.event for item in actions),
            (
                int(SettingsControl.RESET_ORIGINAL),
                int(SettingsControl.TOGGLE_FULLSCREEN),
                int(SettingsControl.BACK),
            ),
        )
        self.assertEqual(
            tuple(item.rect for item in actions),
            (SETTINGS_PROFILE_RECT, SETTINGS_FULLSCREEN_RECT, SETTINGS_BACK_RECT),
        )

    def test_settings_pointer_map_is_separate_from_original_control_ids(self):
        self.assertEqual(
            candidate_settings_event(
                FrontEndScreen.START_MENU,
                SETTINGS_MENU_RECT.x,
                SETTINGS_MENU_RECT.y,
            ),
            int(ModernStartMenuControl.SETTINGS),
        )
        for control, rect in (
            (SettingsControl.RESET_ORIGINAL, SETTINGS_PROFILE_RECT),
            (SettingsControl.TOGGLE_FULLSCREEN, SETTINGS_FULLSCREEN_RECT),
            (SettingsControl.BACK, SETTINGS_BACK_RECT),
        ):
            self.assertEqual(
                candidate_settings_event(FrontEndScreen.SETTINGS, rect.x, rect.y),
                int(control),
            )
            self.assertIsNone(
                candidate_settings_event(
                    FrontEndScreen.SETTINGS, rect.right, rect.y
                )
            )
        self.assertIsNone(
            candidate_settings_event(FrontEndScreen.TEAM_SELECT, 355, 508)
        )
        with self.assertRaises(TypeError):
            candidate_settings_event(FrontEndScreen.START_MENU, 355.5, 508)

    def test_verified_zurich_font_renders_all_gate13_settings_captions(self):
        root = Path(__file__).resolve().parents[1] / "original_assets" / "source"
        font_path = root / "Fonts" / "Zurich_BdXCn_BT_20pixel.fnt"
        self.assertEqual(sha256(font_path.read_bytes()).hexdigest(), ZURICH_FONT20_SHA256)
        resources = load_source_styled_settings_resources(root)

        settings = FrontEndSettings()
        specs = (start_menu_settings_action(), *settings_surface_actions(settings))
        for spec in specs:
            with self.subTest(text=spec.text):
                caption = resources.caption(spec.event, spec.text, spec.rect)
                self.assertTrue(caption.modern_extension)
                self.assertEqual(caption.source_idx_position, -1)
                self.assertEqual(caption.control_rect, spec.rect)
                self.assertLessEqual(caption.glyph_mask.width, spec.rect.width)
                self.assertLessEqual(caption.glyph_mask.height, spec.rect.height)

        settings.toggle_fullscreen()
        for spec in settings_surface_actions(settings):
            resources.caption(spec.event, spec.text, spec.rect)


if __name__ == "__main__":
    unittest.main()
