"""Regression coverage for source-backed PPreMatchPanel facts."""
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from ea444_decoder import EA444DecodedImage
from match_detail_mode import MatchDetailMode
from original_prematch_panel import (
    PREMATCH_ALL_EA444_SPECS,
    PREMATCH_BACKGROUND,
    PREMATCH_FONT_PATH,
    PREMATCH_PITCH,
    PREMATCH_SELECTORS,
    PREMATCH_SELECTOR_ATLAS,
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

    def test_only_source_closed_static_placements_are_promoted(self):
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
        self.assertEqual((PREMATCH_BACKGROUND.width, PREMATCH_BACKGROUND.height), (800, 600))
        self.assertEqual((PREMATCH_PITCH.width, PREMATCH_PITCH.height), (261, 374))

        contract = prematch_panel_contract()
        self.assertEqual(contract["native_surface"], (800, 600))
        self.assertEqual(contract["selector_modes_left_to_right"], (0, 1, 2, 3))
        self.assertEqual(
            contract["selector_labels_left_to_right"],
            ("3D Match", "3D Highlights", "FastView", "Quick Match"),
        )
        self.assertTrue(contract["background_resource_owned"])
        self.assertFalse(contract["background_draw_site_source_closed"])
        self.assertFalse(contract["rating_bar_final_layout_source_closed"])
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

    def test_loader_consumes_all_exact_specs_selector_atlas_and_verified_font(self):
        source_payloads = {
            spec.source_path: spec.source_path.encode("ascii")
            for spec in PREMATCH_ALL_EA444_SPECS
        }
        source_payloads[PREMATCH_SELECTOR_ATLAS.source_path] = b"selector-atlas"
        source_payloads[PREMATCH_FONT_PATH] = b"zurich-font"
        seen_decode_paths = []

        def fake_read(_root, source_path, _sha):
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
        self.assertEqual(seen_decode_paths, [
            spec.source_path for spec in PREMATCH_ALL_EA444_SPECS
        ])
        atlas_loader.assert_called_once()
        self.assertIs(loaded.selector_atlas, fake_atlas)
        self.assertIs(loaded.font, fake_font)
        font_loader.assert_called_once_with(b"zurich-font")
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
