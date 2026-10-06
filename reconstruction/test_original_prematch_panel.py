"""Regression coverage for source-backed PPreMatchPanel facts."""
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from ea444_decoder import EA444DecodedImage
from original_prematch_panel import (
    PREMATCH_ALL_EA444_SPECS,
    PREMATCH_FONT_PATH,
    PREMATCH_DATE_FORMAT,
    PREMATCH_DATE_FORMAT_VA,
    PREMATCH_DATE_BUFFER_OFFSET,
    PREMATCH_WEATHER_TEMPERATURE_FORMAT,
    PREMATCH_WEATHER_TEMPERATURE_FORMAT_VA,
    PREMATCH_DATE_WEATHER_FORMAT,
    PREMATCH_DATE_WEATHER_LANGUAGE_GLOBAL_VA,
    PREMATCH_DATE_WEATHER_BUFFER_OFFSET,
    PREMATCH_FIXTURE_HEADER_FORMAT,
    PREMATCH_FIXTURE_HEADER_LANGUAGE_GLOBAL_VA,
    PREMATCH_FIXTURE_HEADER_BUFFER_OFFSET,
    PREMATCH_FRIENDLY_LABEL,
    PREMATCH_FRIENDLY_LANGUAGE_GLOBAL_VA,
    PREMATCH_VERSUS_LABEL,
    PREMATCH_VERSUS_LANGUAGE_GLOBAL_VA,
    PREMATCH_WEATHER_LABELS,
    PREMATCH_WEATHER_LANGUAGE_GLOBALS,
    PREMATCH_RATING_LABELS,
    PREMATCH_RATING_LANGUAGE_GLOBALS,
    PREMATCH_FIXTURE_HEADER_RECT,
    PREMATCH_DATE_WEATHER_RECT,
    PREMATCH_BADGE_RECTS,
    PREMATCH_TEAM_IDENTITY_RECTS,
    PREMATCH_HEADER_TEXT_STYLE_WRAPPER_VA,
    PREMATCH_TEAM_TEXT_STYLE_WRAPPER_VAS,
    PREMATCH_RATING_TEXT_STYLE_WRAPPER_VA,
    PREMATCH_RATING_CAPTION_RECTS,
    PREMATCH_CHILD_SETUP_VA,
    PREMATCH_CHILD_ARRAY_OFFSET,
    PREMATCH_CHILD_COUNT_OFFSET,
    PREMATCH_CHILD_ARRAY_BYTES,
    PREMATCH_CHILD_COUNT,
    PREMATCH_GENERIC_FORWARD_TRAVERSAL_VA,
    PREMATCH_CHILD_ORDER_RANGES,
    PREMATCH_SELECTOR_CHILD_MODES,
    PREMATCH_TEAM_BADGE_ROOT,
    PREMATCH_TEAM_BADGE_VARIANT_KEY,
    PREMATCH_TEAM_BADGE_FALLBACK,
    PREMATCH_TEAM_BADGE_RESOURCE_OFFSETS,
    PREMATCH_TEAM_BADGE_ACTIVE_OFFSETS,
    PREMATCH_PLAYER_SLOTS_PER_SIDE,
    PREMATCH_STARTERS_PER_SIDE,
    PREMATCH_SIDE_PLAYER_COUNT_MATCH_OFFSETS,
    PREMATCH_SIDE_PLAYER_ARRAY_MATCH_OFFSETS,
    PREMATCH_PLAYER_NAME_LENGTH_FUNCTION_VA,
    PREMATCH_PLAYER_NAME_FORMAT_FUNCTION_VA,
    PREMATCH_PLAYER_FULL_NAME_FORMAT,
    PREMATCH_PLAYER_FULL_NAME_FORMAT_VA,
    PREMATCH_LIVE_BACKGROUND_BUILDER_VA,
    PREMATCH_LIVE_BACKGROUND_RECT,
    PREMATCH_LIVE_BACKGROUND_ROOT,
    PREMATCH_LIVE_BACKGROUND_SOURCE_ACCESSOR_VA,
    PREMATCH_PITCH,
    PREMATCH_RATING_ROWS,
    PREMATCH_SELECTORS,
    PREMATCH_SELECTOR_ATLAS,
    PREMATCH_SHIPPED_BACKGROUND,
    PREMATCH_STATIC_PLACEMENTS,
    OriginalPrematchPanelError,
    _read_verified,
    load_verified_original_prematch_resources,
    prematch_panel_contract,
)


def decoded(width, height):
    return EA444DecodedImage(
        width=width,
        height=height,
        rgba=bytes(width * height * 4),
        consumed_bits=1,
        transparent_pixels=0,
    )


class OriginalPrematchPanelTests(unittest.TestCase):
    def test_four_choice_row_is_exact_source_order(self):
        self.assertEqual(
            tuple(
                (
                    int(item.mode),
                    item.label,
                    item.event_id,
                    (item.rect.x, item.rect.y, item.rect.width, item.rect.height),
                    item.language_global_va,
                )
                for item in PREMATCH_SELECTORS
            ),
            (
                (0, "3D Match", 4, (176, 107, 106, 25), 0x981DD4),
                (1, "3D Highlights", 3, (290, 107, 106, 25), 0x981DD0),
                (2, "FastView", 2, (404, 107, 106, 25), 0x981DCC),
                (3, "Quick Match", 1, (518, 107, 106, 25), 0x981DC8),
            ),
        )

    def test_selector_uses_button_type_14_not_adjacent_type_15(self):
        self.assertTrue(PREMATCH_SELECTOR_ATLAS.source_path.endswith("button_type_14.444"))
        self.assertNotIn("button_type_15", PREMATCH_SELECTOR_ATLAS.source_path)
        self.assertEqual(
            (
                PREMATCH_SELECTOR_ATLAS.source_width,
                PREMATCH_SELECTOR_ATLAS.source_height,
                PREMATCH_SELECTOR_ATLAS.frame_width,
                PREMATCH_SELECTOR_ATLAS.frame_height,
                PREMATCH_SELECTOR_ATLAS.frame_count,
            ),
            (106, 575, 106, 25, 23),
        )
        self.assertEqual(
            PREMATCH_SELECTOR_ATLAS.source_sha256,
            "7b0148bfa65adaa7cabf08e000050ba9add3cf852a03e66423051603c4b85930",
        )

    def test_static_placements_live_background_and_rating_rows_are_exact(self):
        self.assertEqual(
            tuple(
                (
                    item.role,
                    (item.rect.x, item.rect.y, item.rect.width, item.rect.height),
                )
                for item in PREMATCH_STATIC_PLACEMENTS
            ),
            (
                ("top_bar", (0, 0, 800, 95)),
                ("pitch", (269, 152, 261, 374)),
                ("active_left", (36, 152, 200, 16)),
                ("active_right", (563, 152, 200, 16)),
                ("disabled_left", (36, 358, 200, 16)),
                ("disabled_right", (563, 358, 200, 16)),
            ),
        )
        self.assertEqual((PREMATCH_PITCH.width, PREMATCH_PITCH.height), (261, 374))
        self.assertEqual(
            (
                PREMATCH_LIVE_BACKGROUND_ROOT,
                (
                    PREMATCH_LIVE_BACKGROUND_RECT.x,
                    PREMATCH_LIVE_BACKGROUND_RECT.y,
                    PREMATCH_LIVE_BACKGROUND_RECT.width,
                    PREMATCH_LIVE_BACKGROUND_RECT.height,
                ),
                PREMATCH_LIVE_BACKGROUND_BUILDER_VA,
                PREMATCH_LIVE_BACKGROUND_SOURCE_ACCESSOR_VA,
            ),
            (
                "FM2001_Art/Generic/Team_Backgrounds",
                (0, 0, 800, 600),
                0x5D3490,
                0x5D3510,
            ),
        )
        self.assertEqual(
            tuple(
                (
                    row.native_width_function_va,
                    row.native_record_discriminator,
                    row.left_x,
                    row.right_x,
                    row.y,
                    row.full_width,
                    row.height,
                )
                for row in PREMATCH_RATING_ROWS
            ),
            (
                (0x49A3D0, 3, 65, 564, 497, 171, 16),
                (0x49A460, 0, 65, 564, 515, 171, 16),
                (0x49A4F0, 1, 65, 564, 533, 171, 16),
                (0x49A580, 2, 65, 564, 551, 171, 16),
            ),
        )

    def test_shipped_prematch_background_is_not_promoted_as_live_background(self):
        self.assertTrue(
            PREMATCH_SHIPPED_BACKGROUND.source_path.endswith(
                "pre_match/prematch_bground.444"
            )
        )
        self.assertNotIn(PREMATCH_SHIPPED_BACKGROUND, PREMATCH_ALL_EA444_SPECS)
        contract = prematch_panel_contract()
        self.assertEqual(contract["native_surface"], (800, 600))
        self.assertEqual(contract["selector_modes_left_to_right"], (0, 1, 2, 3))
        self.assertEqual(
            contract["selector_labels_left_to_right"],
            ("3D Match", "3D Highlights", "FastView", "Quick Match"),
        )
        self.assertEqual(
            contract["live_background_root"],
            "FM2001_Art/Generic/Team_Backgrounds",
        )
        self.assertEqual(contract["live_background_rect"], (0, 0, 800, 600))
        self.assertFalse(
            contract["shipped_prematch_background_is_live_panel_background"]
        )
        self.assertTrue(contract["live_background_contract_source_closed"])
        self.assertTrue(contract["rating_bar_layout_source_closed"])
        self.assertFalse(contract["management_launch_trigger_recovered"])
        self.assertFalse(contract["complete_prematch_frame"])
        self.assertFalse(contract["gate14_complete"])

    def test_identity_text_and_roster_contract_is_exact(self):
        self.assertEqual(
            (
                PREMATCH_DATE_FORMAT,
                PREMATCH_DATE_FORMAT_VA,
                PREMATCH_DATE_BUFFER_OFFSET,
            ),
            ("%Df %Mf %Yf", 0x81D5B8, 0x70),
        )
        self.assertEqual(
            (
                PREMATCH_WEATHER_TEMPERATURE_FORMAT,
                PREMATCH_WEATHER_TEMPERATURE_FORMAT_VA,
            ),
            ("%s %d°C", 0x81D5B0),
        )
        self.assertEqual(
            (
                PREMATCH_DATE_WEATHER_FORMAT,
                PREMATCH_DATE_WEATHER_LANGUAGE_GLOBAL_VA,
                PREMATCH_DATE_WEATHER_BUFFER_OFFSET,
            ),
            ("%s %s", 0x98204C, 0x270),
        )
        self.assertEqual(
            (
                PREMATCH_FIXTURE_HEADER_FORMAT,
                PREMATCH_FIXTURE_HEADER_LANGUAGE_GLOBAL_VA,
                PREMATCH_FIXTURE_HEADER_BUFFER_OFFSET,
                PREMATCH_FRIENDLY_LABEL,
                PREMATCH_FRIENDLY_LANGUAGE_GLOBAL_VA,
                PREMATCH_VERSUS_LABEL,
                PREMATCH_VERSUS_LANGUAGE_GLOBAL_VA,
            ),
            (
                "%s MATCH TODAY AT %s",
                0x982050,
                0x170,
                "Friendly",
                0x9830C8,
                "V",
                0x9830C4,
            ),
        )
        self.assertEqual(
            PREMATCH_WEATHER_LABELS,
            ("Clear", "Sunny", "Raining", "Sleet", "Snowy"),
        )
        self.assertEqual(
            PREMATCH_WEATHER_LANGUAGE_GLOBALS,
            (0x98252C, 0x982534, 0x982524, 0x9821E0, 0x982520),
        )
        self.assertEqual(PREMATCH_RATING_LABELS, ("GK", "DEF", "MID", "ATT"))
        self.assertEqual(
            PREMATCH_RATING_LANGUAGE_GLOBALS,
            (0x983BE4, 0x983B70, 0x983B6C, 0x983B68),
        )
        self.assertEqual(
            (
                PREMATCH_TEAM_BADGE_ROOT,
                PREMATCH_TEAM_BADGE_VARIANT_KEY,
                PREMATCH_TEAM_BADGE_FALLBACK,
                PREMATCH_TEAM_BADGE_RESOURCE_OFFSETS,
                PREMATCH_TEAM_BADGE_ACTIVE_OFFSETS,
            ),
            (
                r"FM2001_art\generic\team_badge_stills",
                "badge_2",
                r"fm2001_art\generic\team_badge_stills\generic.444",
                (0x600, 0x624),
                (0x840, 0x890),
            ),
        )
        self.assertEqual(PREMATCH_PLAYER_SLOTS_PER_SIDE, 18)
        self.assertEqual(PREMATCH_STARTERS_PER_SIDE, 11)
        self.assertEqual(PREMATCH_SIDE_PLAYER_COUNT_MATCH_OFFSETS, (0x5A4, 0xB54))
        self.assertEqual(PREMATCH_SIDE_PLAYER_ARRAY_MATCH_OFFSETS, (0x004, 0x5B4))
        self.assertEqual(PREMATCH_PLAYER_NAME_LENGTH_FUNCTION_VA, 0x417A90)
        self.assertEqual(PREMATCH_PLAYER_NAME_FORMAT_FUNCTION_VA, 0x417AE0)
        self.assertEqual(PREMATCH_PLAYER_FULL_NAME_FORMAT, "%s %s")
        self.assertEqual(PREMATCH_PLAYER_FULL_NAME_FORMAT_VA, 0x81858C)

        contract = prematch_panel_contract()
        self.assertEqual(contract["date_format"], "%Df %Mf %Yf")
        self.assertEqual(contract["weather_temperature_format"], "%s %d°C")
        self.assertEqual(contract["date_weather_format"], "%s %s")
        self.assertEqual(contract["date_weather_buffer_offset"], 0x270)
        self.assertEqual(contract["fixture_header_format"], "%s MATCH TODAY AT %s")
        self.assertEqual(contract["fixture_header_buffer_offset"], 0x170)
        self.assertEqual(contract["friendly_label"], "Friendly")
        self.assertEqual(contract["versus_label"], "V")
        self.assertEqual(contract["weather_labels"], PREMATCH_WEATHER_LABELS)
        self.assertEqual(contract["rating_labels"], PREMATCH_RATING_LABELS)
        self.assertEqual(contract["player_slots_per_side"], 18)
        self.assertEqual(contract["starters_per_side"], 11)
        self.assertTrue(contract["identity_controls_source_closed"])
        self.assertFalse(contract["management_launch_trigger_recovered"])
        self.assertFalse(contract["complete_prematch_frame"])
        self.assertFalse(contract["gate14_complete"])

    def test_identity_control_geometry_and_styles_are_exact(self):
        def rect(r):
            return (r.x, r.y, r.width, r.height)

        self.assertEqual(rect(PREMATCH_FIXTURE_HEADER_RECT), (250, 45, 300, 30))
        self.assertEqual(rect(PREMATCH_DATE_WEATHER_RECT), (250, 70, 300, 16))
        self.assertEqual(
            tuple(rect(r) for r in PREMATCH_BADGE_RECTS),
            ((38, 1, 135, 93), (627, 1, 135, 93)),
        )
        self.assertEqual(
            tuple(rect(r) for r in PREMATCH_TEAM_IDENTITY_RECTS),
            ((184, 4, 185, 39), (374, 5, 52, 37), (429, 4, 185, 39)),
        )
        self.assertEqual(PREMATCH_HEADER_TEXT_STYLE_WRAPPER_VA, 0x87BE30)
        self.assertEqual(
            PREMATCH_TEAM_TEXT_STYLE_WRAPPER_VAS,
            (0x87BE80, 0x87BE70, 0x87BE80),
        )
        self.assertEqual(PREMATCH_RATING_TEXT_STYLE_WRAPPER_VA, 0x87BEA0)
        self.assertEqual(
            tuple(rect(r) for r in PREMATCH_RATING_CAPTION_RECTS),
            (
                (37, 498, 25, 14),
                (37, 516, 25, 14),
                (37, 534, 25, 14),
                (37, 552, 25, 14),
                (737, 498, 25, 14),
                (737, 516, 25, 14),
                (737, 534, 25, 14),
                (737, 552, 25, 14),
            ),
        )

    def test_child_array_is_complete_forward_native_draw_order(self):
        self.assertEqual(PREMATCH_CHILD_SETUP_VA, 0x4967F0)
        self.assertEqual(PREMATCH_CHILD_ARRAY_OFFSET, 0x1C)
        self.assertEqual(PREMATCH_CHILD_COUNT_OFFSET, 0x38)
        self.assertEqual(PREMATCH_CHILD_ARRAY_BYTES, 0x2D8)
        self.assertEqual(PREMATCH_CHILD_COUNT, 182)
        self.assertEqual(PREMATCH_CHILD_ARRAY_BYTES, PREMATCH_CHILD_COUNT * 4)
        self.assertEqual(PREMATCH_GENERIC_FORWARD_TRAVERSAL_VA, 0x6533A0)

        self.assertEqual(PREMATCH_CHILD_ORDER_RANGES[0], ("live_background", 0, 0))
        self.assertEqual(PREMATCH_CHILD_ORDER_RANGES[-1], ("match_detail_selectors", 178, 181))
        flattened = []
        for _name, start, end in PREMATCH_CHILD_ORDER_RANGES:
            flattened.extend(range(start, end + 1))
        self.assertEqual(flattened, list(range(PREMATCH_CHILD_COUNT)))
        self.assertEqual(
            tuple(int(mode) for mode in PREMATCH_SELECTOR_CHILD_MODES),
            (3, 2, 1, 0),
        )

        contract = prematch_panel_contract()
        self.assertEqual(contract["child_count"], 182)
        self.assertEqual(contract["child_order_ranges"], PREMATCH_CHILD_ORDER_RANGES)
        self.assertEqual(contract["selector_child_modes"], (3, 2, 1, 0))
        self.assertTrue(contract["child_draw_order_source_closed"])
        self.assertFalse(contract["management_launch_trigger_recovered"])
        self.assertFalse(contract["complete_prematch_frame"])
        self.assertFalse(contract["gate14_complete"])

    def test_hash_gate_rejects_substituted_source_bytes(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            path = root / "asset.444"
            path.write_bytes(b"replacement")
            with self.assertRaisesRegex(
                OriginalPrematchPanelError, "checksum mismatch"
            ):
                _read_verified(root, "asset.444", "0" * 64)

    def test_loader_consumes_only_live_seam_assets_selector_atlas_and_font(self):
        source_payloads = {
            spec.source_path: spec.source_path.encode("ascii")
            for spec in PREMATCH_ALL_EA444_SPECS
        }
        source_payloads[PREMATCH_SELECTOR_ATLAS.source_path] = b"selector-atlas"
        source_payloads[PREMATCH_FONT_PATH] = b"zurich-font"
        seen_decode_paths = []

        def fake_read(_root, source_path, _sha):
            self.assertNotEqual(source_path, PREMATCH_SHIPPED_BACKGROUND.source_path)
            return source_payloads[source_path]

        def fake_decode(raw, *, tables, quant):
            source_path = raw.decode("ascii")
            seen_decode_paths.append(source_path)
            spec = next(
                item for item in PREMATCH_ALL_EA444_SPECS
                if item.source_path == source_path
            )
            return decoded(spec.width, spec.height)

        fake_atlas = SimpleNamespace(
            spec=PREMATCH_SELECTOR_ATLAS,
            frames=(object(),) * 23,
        )
        fake_font = object()

        with TemporaryDirectory() as td:
            exe = Path(td) / "FOOTBAL.EXE"
            exe.write_bytes(b"canonical-test-double")
            with (
                patch("original_prematch_panel._read_verified", side_effect=fake_read),
                patch(
                    "original_prematch_panel.tables_from_original_executable",
                    return_value="tables",
                ) as table_loader,
                patch(
                    "original_prematch_panel.quantization_from_verified_executable",
                    return_value="quant",
                ) as quant_loader,
                patch(
                    "original_prematch_panel.decode_ea444",
                    side_effect=fake_decode,
                ),
                patch(
                    "original_prematch_panel.decode_verified_original_button_atlas",
                    return_value=fake_atlas,
                ) as atlas_loader,
                patch(
                    "original_prematch_panel.EAFont.from_bytes",
                    return_value=fake_font,
                ) as font_loader,
            ):
                loaded = load_verified_original_prematch_resources(
                    source_root=td,
                    original_executable=exe,
                )

        table_loader.assert_called_once_with(b"canonical-test-double")
        quant_loader.assert_called_once_with(b"canonical-test-double")
        self.assertEqual(
            seen_decode_paths,
            [spec.source_path for spec in PREMATCH_ALL_EA444_SPECS],
        )
        self.assertNotIn(PREMATCH_SHIPPED_BACKGROUND.source_path, seen_decode_paths)
        atlas_loader.assert_called_once()
        self.assertIs(loaded.selector_atlas, fake_atlas)
        self.assertIs(loaded.font, fake_font)
        font_loader.assert_called_once_with(b"zurich-font")
        self.assertTrue(loaded.live_background_contract_source_closed)
        self.assertTrue(loaded.rating_bar_layout_source_closed)
        self.assertFalse(loaded.management_launch_trigger_recovered)
        self.assertFalse(loaded.complete_prematch_frame)
        self.assertFalse(loaded.gate14_complete)

    def test_loader_rejects_wrong_decoded_geometry(self):
        source_payloads = {
            spec.source_path: spec.source_path.encode("ascii")
            for spec in PREMATCH_ALL_EA444_SPECS
        }
        source_payloads[PREMATCH_SELECTOR_ATLAS.source_path] = b"selector-atlas"
        source_payloads[PREMATCH_FONT_PATH] = b"zurich-font"

        def fake_read(_root, source_path, _sha):
            return source_payloads[source_path]

        def bad_decode(raw, *, tables, quant):
            source_path = raw.decode("ascii")
            spec = next(
                item for item in PREMATCH_ALL_EA444_SPECS
                if item.source_path == source_path
            )
            if spec is PREMATCH_PITCH:
                return decoded(260, 374)
            return decoded(spec.width, spec.height)

        with TemporaryDirectory() as td:
            exe = Path(td) / "FOOTBAL.EXE"
            exe.write_bytes(b"canonical-test-double")
            with (
                patch("original_prematch_panel._read_verified", side_effect=fake_read),
                patch(
                    "original_prematch_panel.tables_from_original_executable",
                    return_value=object(),
                ),
                patch(
                    "original_prematch_panel.quantization_from_verified_executable",
                    return_value=object(),
                ),
                patch("original_prematch_panel.decode_ea444", side_effect=bad_decode),
            ):
                with self.assertRaisesRegex(
                    OriginalPrematchPanelError, "geometry mismatch"
                ):
                    load_verified_original_prematch_resources(
                        source_root=td,
                        original_executable=exe,
                    )


if __name__ == "__main__":
    unittest.main()
