"""Regression coverage for first-hand PPreMatch text style/font mappings."""
import unittest

from gate14_prematch_text_style import (
    PREMATCH_DATE_WEATHER_FLAGS,
    PREMATCH_FIXTURE_HEADER_FLAGS,
    PREMATCH_HEADER_STYLE,
    PREMATCH_LEFT_PLAYER_NAME_FLAGS,
    PREMATCH_LEFT_TEAM_IDENTITY_FLAGS,
    PREMATCH_PLAYER_NUMBER_FLAGS,
    PREMATCH_RATING_CAPTION_FLAGS,
    PREMATCH_RIGHT_PLAYER_NAME_FLAGS,
    PREMATCH_RIGHT_TEAM_IDENTITY_FLAGS,
    PREMATCH_ROW_STYLE,
    PREMATCH_TEAM_STYLE,
    PREMATCH_TEXT_CONTROL_STYLE_USES,
    PREMATCH_TEXT_STYLES,
    PREMATCH_VERSUS_FLAGS,
    PREMATCH_VERSUS_STYLE,
    TEXT_NATIVE_COLOR_16,
    TEXT_STYLE_OBJECT_VTABLE_VA,
    prematch_text_style_contract,
)


class PrematchTextStyleTests(unittest.TestCase):
    def test_four_source_wrappers_bind_exact_font_objects_and_files(self):
        self.assertEqual(TEXT_STYLE_OBJECT_VTABLE_VA, 0x7D7034)
        self.assertEqual(
            tuple(
                (
                    style.semantic,
                    style.wrapper_va,
                    style.wrapper_initializer_va,
                    style.font_object_va,
                    style.source_path_va,
                    style.source_path_use_va,
                    style.font_loader_call_va,
                    style.source_path,
                    style.source_size,
                    style.source_sha256,
                    style.atlas_size,
                    style.native_line_height,
                )
                for style in PREMATCH_TEXT_STYLES
            ),
            (
                (
                    "header_date_regular_16",
                    0x87BE30,
                    0x603790,
                    0x8CAB80,
                    0x839E30,
                    0x6044AC,
                    0x6044F9,
                    r"Fonts\Zurich_XCn_BT_16pixel.fnt",
                    75_217,
                    "e0fbe91421642a489721ab167ce3d2db1738802ef0f1e198df3c90ce25ec3d18",
                    (1261, 17),
                    18,
                ),
                (
                    "team_identity_bold_20",
                    0x87BE80,
                    0x6036A0,
                    0x90C5D0,
                    0x839EDC,
                    0x6042FE,
                    0x60434B,
                    r"Fonts\Zurich_BdXCn_BT_20pixel.fnt",
                    91_349,
                    "47e3b21f07a3013ba19d257f31e1e876c9b03856c930a8fa5fe58103974ed166",
                    (1789, 21),
                    21,
                ),
                (
                    "versus_bold_25",
                    0x87BE70,
                    0x6036D0,
                    0x8FF3C0,
                    0x839EB8,
                    0x604354,
                    0x6043A1,
                    r"Fonts\Zurich_BdXCn_BT_25pixel.fnt",
                    99_705,
                    "b16bc57d81f35f38e02db102bd17af0032295328cf6c04251c89f4feb021f2de",
                    (1837, 25),
                    26,
                ),
                (
                    "row_caption_bold_16",
                    0x87BEA0,
                    0x603640,
                    0x9269F0,
                    0x839F24,
                    0x604252,
                    0x60429F,
                    r"Fonts\Zurich_BdXCn_BT_16pixel.fnt",
                    79_722,
                    "9dc371caba34823b0d6ba6fd4c5e82f94775de1168daa5dad936b70a6e4f9732",
                    (1526, 17),
                    18,
                ),
            ),
        )

    def test_prematch_constructor_flags_stay_raw_and_source_owned(self):
        self.assertEqual(
            (
                PREMATCH_FIXTURE_HEADER_FLAGS,
                PREMATCH_DATE_WEATHER_FLAGS,
                PREMATCH_LEFT_TEAM_IDENTITY_FLAGS,
                PREMATCH_VERSUS_FLAGS,
                PREMATCH_RIGHT_TEAM_IDENTITY_FLAGS,
                PREMATCH_LEFT_PLAYER_NAME_FLAGS,
                PREMATCH_RIGHT_PLAYER_NAME_FLAGS,
                PREMATCH_PLAYER_NUMBER_FLAGS,
                PREMATCH_RATING_CAPTION_FLAGS,
            ),
            (0x24, 0x24, 0x22, 0x24, 0x21, 0x21, 0x22, 0x24, 0x24),
        )
        self.assertEqual(
            tuple(
                (item.semantic, item.wrapper_va, item.raw_flags, item.native_color_16)
                for item in PREMATCH_TEXT_CONTROL_STYLE_USES
            ),
            (
                ("fixture_header", 0x87BE30, 0x24, 0xFFFF),
                ("date_weather", 0x87BE30, 0x24, 0xFFFF),
                ("left_team_identity", 0x87BE80, 0x22, 0xFFFF),
                ("versus", 0x87BE70, 0x24, 0xFFFF),
                ("right_team_identity", 0x87BE80, 0x21, 0xFFFF),
                ("left_player_name", 0x87BEA0, 0x21, 0xFFFF),
                ("right_player_name", 0x87BEA0, 0x22, 0xFFFF),
                ("player_number", 0x87BEA0, 0x24, 0xFFFF),
                ("rating_caption", 0x87BEA0, 0x24, 0xFFFF),
            ),
        )
        self.assertEqual(TEXT_NATIVE_COLOR_16, 0xFFFF)

    def test_contract_keeps_alignment_and_pixels_fail_closed(self):
        contract = prematch_text_style_contract()
        self.assertTrue(contract["font_identity_source_closed"])
        self.assertTrue(contract["raw_control_flags_source_closed"])
        self.assertFalse(contract["alignment_bit_semantics_source_closed"])
        self.assertFalse(contract["text_pixels_rasterized"])
        self.assertFalse(contract["complete_prematch_frame"])
        self.assertFalse(contract["gate14_complete"])

    def test_semantic_styles_match_expected_wrappers(self):
        self.assertEqual(PREMATCH_HEADER_STYLE.wrapper_va, 0x87BE30)
        self.assertEqual(PREMATCH_TEAM_STYLE.wrapper_va, 0x87BE80)
        self.assertEqual(PREMATCH_VERSUS_STYLE.wrapper_va, 0x87BE70)
        self.assertEqual(PREMATCH_ROW_STYLE.wrapper_va, 0x87BEA0)


if __name__ == "__main__":
    unittest.main()
