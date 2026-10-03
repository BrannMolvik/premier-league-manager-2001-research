import unittest

from gate14_possession_figures import (
    NEUTRAL_TEXT_RECT,
    SIDE0_TEXT_RECT,
    SIDE1_TEXT_RECT,
    SOURCE_CONSTRUCTOR_VA,
    SOURCE_FASTVIEW_CALLSITE_VA,
    SOURCE_PERCENT_FORMAT,
    SOURCE_RECEIVER_VA,
    SOURCE_TEXT_CONTROL_CONSTRUCTOR_VA,
    SOURCE_TEXT_DRAW_VA,
    SOURCE_TEXT_FONT_LOAD_CALL_VA,
    SOURCE_TEXT_FONT_OBJECT_VA,
    SOURCE_TEXT_FONT_PATH,
    SOURCE_TEXT_FONT_PATH_LITERAL_VA,
    SOURCE_TEXT_HORIZONTAL_ALIGNMENT,
    SOURCE_TEXT_NATIVE_COLOR_16,
    SOURCE_TEXT_RENDER_FLAGS,
    SOURCE_TEXT_STYLE_INDEX,
    SOURCE_TEXT_STYLE_INIT_VA,
    SOURCE_TEXT_STYLE_SELECTOR_VA,
    SOURCE_TEXT_STYLE_WRAPPER_VA,
    SOURCE_TEXT_VERTICAL_ALIGNMENT,
    SOURCE_FIXED_FIXTURE_BUILDER_VA,
    SOURCE_LEAGUE_MATCH_CONSTRUCTOR_VA,
    SOURCE_MATCH_SETUP_VA,
    SOURCE_HOME_TEAM_SUBOBJECT_OFFSET,
    SOURCE_AWAY_TEAM_SUBOBJECT_OFFSET,
    SOURCE_MATCHCALCULATOR_SIDE0_TEAM_OFFSET,
    SOURCE_MATCHCALCULATOR_SIDE1_TEAM_OFFSET,
    SOURCE_SIDE0_ROLE,
    SOURCE_SIDE1_ROLE,
    SOURCE_SIDE0_SCREEN_POSITION,
    SOURCE_SIDE1_SCREEN_POSITION,
    PossessionFiguresError,
    human_screen_position,
    match_role_for_side_index,
    possession_figures_text_layout,
    screen_position_for_side_index,
)


class PossessionFiguresTests(unittest.TestCase):
    def test_source_addresses_format_and_rectangles(self):
        self.assertEqual(SOURCE_CONSTRUCTOR_VA, 0x51E7E0)
        self.assertEqual(SOURCE_RECEIVER_VA, 0x51EA80)
        self.assertEqual(SOURCE_FASTVIEW_CALLSITE_VA, 0x520802)
        self.assertEqual(SOURCE_PERCENT_FORMAT, "%u%%")
        self.assertEqual(SIDE1_TEXT_RECT, (311, 181, 351, 199))
        self.assertEqual(NEUTRAL_TEXT_RECT, (382, 181, 422, 199))
        self.assertEqual(SIDE0_TEXT_RECT, (454, 181, 494, 199))
        self.assertEqual(SOURCE_TEXT_CONTROL_CONSTRUCTOR_VA, 0x527960)
        self.assertEqual(SOURCE_TEXT_STYLE_SELECTOR_VA, 0x527BA0)
        self.assertEqual(SOURCE_TEXT_STYLE_INDEX, 1)
        self.assertEqual(SOURCE_TEXT_STYLE_WRAPPER_VA, 0x87BE90)
        self.assertEqual(SOURCE_TEXT_STYLE_INIT_VA, 0x603670)
        self.assertEqual(SOURCE_TEXT_FONT_OBJECT_VA, 0x9197E0)
        self.assertEqual(SOURCE_TEXT_FONT_LOAD_CALL_VA, 0x6042F5)
        self.assertEqual(SOURCE_TEXT_FONT_PATH_LITERAL_VA, 0x839F00)
        self.assertEqual(
            SOURCE_TEXT_FONT_PATH,
            "Fonts/Zurich_BdXCn_BT_18pixel.fnt",
        )
        self.assertEqual(SOURCE_TEXT_RENDER_FLAGS, 9)
        self.assertEqual(SOURCE_TEXT_NATIVE_COLOR_16, 0xFFFF)
        self.assertEqual(SOURCE_TEXT_DRAW_VA, 0x64F090)
        self.assertEqual(SOURCE_TEXT_HORIZONTAL_ALIGNMENT, "left")
        self.assertEqual(SOURCE_TEXT_VERTICAL_ALIGNMENT, "top")

    def test_layout_preserves_source_side_index_order_not_human_orientation(self):
        rows = possession_figures_text_layout(45, 20)
        self.assertEqual(
            [
                (
                    r.source_byte_offset,
                    r.accessor_va,
                    r.percent,
                    r.text,
                    r.rect,
                    r.side_index,
                )
                for r in rows
            ],
            [
                (0x0F, 0x51A720, 35, "35%", (311, 181, 351, 199), 1),
                (0x0E, 0x51A710, 20, "20%", (382, 181, 422, 199), None),
                (0x0D, 0x51A700, 45, "45%", (454, 181, 494, 199), 0),
            ],
        )

    def test_source_side_identity_is_home_right_and_away_left(self):
        self.assertEqual(SOURCE_FIXED_FIXTURE_BUILDER_VA, 0x6173D0)
        self.assertEqual(SOURCE_LEAGUE_MATCH_CONSTRUCTOR_VA, 0x5104F0)
        self.assertEqual(SOURCE_MATCH_SETUP_VA, 0x510D60)
        self.assertEqual(SOURCE_HOME_TEAM_SUBOBJECT_OFFSET, 0x14)
        self.assertEqual(SOURCE_AWAY_TEAM_SUBOBJECT_OFFSET, 0x28)
        self.assertEqual(SOURCE_MATCHCALCULATOR_SIDE0_TEAM_OFFSET, 0x0000)
        self.assertEqual(SOURCE_MATCHCALCULATOR_SIDE1_TEAM_OFFSET, 0x05B0)
        self.assertEqual(SOURCE_SIDE0_ROLE, "home")
        self.assertEqual(SOURCE_SIDE1_ROLE, "away")
        self.assertEqual(SOURCE_SIDE0_SCREEN_POSITION, "right")
        self.assertEqual(SOURCE_SIDE1_SCREEN_POSITION, "left")
        self.assertEqual(match_role_for_side_index(0), "home")
        self.assertEqual(match_role_for_side_index(1), "away")
        self.assertEqual(screen_position_for_side_index(0), "right")
        self.assertEqual(screen_position_for_side_index(1), "left")
        self.assertEqual(human_screen_position(human_is_home=True), "right")
        self.assertEqual(human_screen_position(human_is_home=False), "left")

    def test_orientation_helpers_fail_closed(self):
        for bad in (-1, 2, True, "0"):
            with self.subTest(bad=bad):
                with self.assertRaises(PossessionFiguresError):
                    match_role_for_side_index(bad)
                with self.assertRaises(PossessionFiguresError):
                    screen_position_for_side_index(bad)
        with self.assertRaises(PossessionFiguresError):
            human_screen_position(human_is_home=1)

    def test_invalid_percentages_fail_closed(self):
        for a, b in ((-1, 0), (101, 0), (80, 30), (True, 20), (45, "20")):
            with self.subTest(side0=a, neutral=b):
                with self.assertRaises(PossessionFiguresError):
                    possession_figures_text_layout(a, b)


if __name__ == "__main__":
    unittest.main()
