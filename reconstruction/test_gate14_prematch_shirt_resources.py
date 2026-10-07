"""Regression coverage for verified PPreMatch shirt resource loading."""
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from gate14_prematch_shirt_resources import (
    PREMATCH_GOALKEEPER_SIZE,
    PREMATCH_NUMBERED_ATLAS_SIZE,
    PrematchNumberedShirtAtlas,
    PrematchShirtResourceError,
    crop_prematch_numbered_shirt_frame,
    load_prematch_goalkeeper_shirt,
    load_prematch_numbered_shirt_atlas,
    prematch_shirt_resource_contract,
)
from gate14_prematch_shirt_selection import (
    PrematchClubShirtState,
    PrematchSideKitContext,
)


def club():
    return PrematchClubShirtState(
        club_id=10,
        graphics_basename="Arsenal",
        primary_template_index=1,
        alternate_template_index=7,
        primary_color_id=1,
        primary_secondary_color_id=2,
        alternate_color_id=3,
        alternate_secondary_color_id=4,
    )


def context(*, alternate=False):
    return PrematchSideKitContext(
        use_alternate=alternate,
        selected_template_index=7 if alternate else 1,
        custom_source_path=(
            None
            if alternate
            else r"fm2001_art\Generic\front-end-shirts\custom\Arsenal.444"
        ),
        generic_template_index=7,
        generic_source_path=r"fm2001_art\Generic\front-end-shirts\generic\Team07.bmp",
    )


def decoded(width, height, marker=0):
    rgba = bytearray(width * height * 4)
    rgba[:4] = bytes((marker, marker, marker, 255))
    return SimpleNamespace(width=width, height=height, rgba=bytes(rgba))


class PrematchShirtResourceTests(unittest.TestCase):
    def _exe(self, root):
        path = Path(root) / "FOOTBAL.EXE"
        path.write_bytes(b"canonical-test-double")
        return path

    def test_contract_keeps_marker_binding_separate(self):
        contract = prematch_shirt_resource_contract()
        self.assertEqual(contract["numbered_atlas_size"], (36, 1280))
        self.assertEqual(contract["numbered_frame_count"], 40)
        self.assertEqual(contract["goalkeeper_size"], (36, 32))
        self.assertTrue(contract["primary_custom_then_generic_fallback"])
        self.assertTrue(contract["alternate_generic_only"])
        self.assertTrue(contract["goalkeeper_dedicated_original"])
        self.assertTrue(contract["alternate_number_initializes_from_primary"])
        self.assertEqual(contract["alternate_number_initializer_va"], 0x418E27)
        self.assertEqual(contract["alternate_number_update_va"], 0x41E400)
        self.assertTrue(contract["source_pixels_staged"])
        self.assertFalse(contract["marker_binding_complete"])
        self.assertFalse(contract["gate14_complete"])

    def test_primary_custom_atlas_wins_before_generic_generation(self):
        with TemporaryDirectory() as td:
            custom = (
                Path(td)
                / "FM2001_Art"
                / "Generic"
                / "Front-End-Shirts"
                / "Custom"
                / "Arsenal.444"
            )
            custom.parent.mkdir(parents=True)
            custom.write_bytes(b"custom-source")
            exe = self._exe(td)
            with (
                patch(
                    "gate14_prematch_shirt_resources.tables_from_original_executable",
                    return_value=object(),
                ),
                patch(
                    "gate14_prematch_shirt_resources.quantization_from_verified_executable",
                    return_value=object(),
                ),
                patch(
                    "gate14_prematch_shirt_resources.decode_ea444",
                    return_value=decoded(36, 1280, 17),
                ) as decode,
                patch(
                    "gate14_prematch_shirt_resources.recolor_prematch_generic_shirt"
                ) as recolor,
            ):
                atlas = load_prematch_numbered_shirt_atlas(
                    club=club(),
                    context=context(),
                    source_root=td,
                    original_executable=exe,
                )

        self.assertEqual(atlas.source_kind, "custom_ea444")
        self.assertEqual(atlas.source_path, context().custom_source_path)
        self.assertFalse(atlas.use_alternate)
        self.assertEqual(tuple(atlas.rgba[:4]), (17, 17, 17, 255))
        decode.assert_called_once()
        recolor.assert_not_called()

    def test_missing_custom_falls_through_to_generic_bmp(self):
        with TemporaryDirectory() as td:
            generic = (
                Path(td)
                / "FM2001_Art"
                / "Generic"
                / "Front-End-Shirts"
                / "Generic"
                / "Team07.bmp"
            )
            generic.parent.mkdir(parents=True)
            generic.write_bytes(b"generic-source")
            exe = self._exe(td)
            generated = SimpleNamespace(
                rgba=bytes(36 * 1280 * 4),
            )
            with (
                patch(
                    "gate14_prematch_shirt_resources.tables_from_original_executable",
                    return_value=object(),
                ),
                patch(
                    "gate14_prematch_shirt_resources.quantization_from_verified_executable",
                    return_value=object(),
                ),
                patch(
                    "gate14_prematch_shirt_resources.recolor_prematch_generic_shirt",
                    return_value=generated,
                ) as recolor,
            ):
                atlas = load_prematch_numbered_shirt_atlas(
                    club=club(),
                    context=context(),
                    source_root=td,
                    original_executable=exe,
                )

        self.assertEqual(atlas.source_kind, "generated_generic_bmp")
        self.assertFalse(atlas.use_alternate)
        recolor.assert_called_once()

    def test_alternate_context_uses_generic_without_custom_probe(self):
        with TemporaryDirectory() as td:
            generic = (
                Path(td)
                / "FM2001_Art"
                / "Generic"
                / "Front-End-Shirts"
                / "Generic"
                / "Team07.bmp"
            )
            generic.parent.mkdir(parents=True)
            generic.write_bytes(b"generic-source")
            exe = self._exe(td)
            generated = SimpleNamespace(rgba=bytes(36 * 1280 * 4))
            with (
                patch(
                    "gate14_prematch_shirt_resources.tables_from_original_executable",
                    return_value=object(),
                ),
                patch(
                    "gate14_prematch_shirt_resources.quantization_from_verified_executable",
                    return_value=object(),
                ),
                patch(
                    "gate14_prematch_shirt_resources.recolor_prematch_generic_shirt",
                    return_value=generated,
                ),
            ):
                atlas = load_prematch_numbered_shirt_atlas(
                    club=club(),
                    context=context(alternate=True),
                    source_root=td,
                    original_executable=exe,
                )
        self.assertEqual(atlas.source_kind, "generated_generic_bmp")
        self.assertTrue(atlas.use_alternate)

    def test_goalkeeper_uses_dedicated_original_36x32_resource(self):
        with TemporaryDirectory() as td:
            keeper = (
                Path(td)
                / "FM2001_Art"
                / "Generic"
                / "Front-End-Shirts"
                / "Custom"
                / "goalkeeper.444"
            )
            keeper.parent.mkdir(parents=True)
            keeper.write_bytes(b"keeper-source")
            exe = self._exe(td)
            with (
                patch(
                    "gate14_prematch_shirt_resources.tables_from_original_executable",
                    return_value=object(),
                ),
                patch(
                    "gate14_prematch_shirt_resources.quantization_from_verified_executable",
                    return_value=object(),
                ),
                patch(
                    "gate14_prematch_shirt_resources.decode_ea444",
                    return_value=decoded(*PREMATCH_GOALKEEPER_SIZE, marker=23),
                ),
            ):
                resource = load_prematch_goalkeeper_shirt(
                    source_root=td,
                    original_executable=exe,
                )
        self.assertEqual(tuple(resource.rgba[:4]), (23, 23, 23, 255))
        self.assertEqual(len(resource.rgba), 36 * 32 * 4)

    def test_crop_selects_exact_numbered_frame_and_default_alternate_state(self):
        rgba = bytearray(36 * 1280 * 4)
        for frame in range(40):
            y0 = frame * 32
            for y in range(y0, y0 + 32):
                start = (y * 36) * 4
                rgba[start:start + 4] = bytes((frame + 1, 0, 0, 255))
        atlas = PrematchNumberedShirtAtlas(
            source_kind="custom_ea444",
            source_path="custom.444",
            source_sha256="0" * 64,
            rgba=bytes(rgba),
            club_id=10,
            use_alternate=False,
        )

        frame = crop_prematch_numbered_shirt_frame(
            atlas,
            player_registered_club_id=10,
            team_club_id=10,
            primary_shirt_number=7,
        )
        self.assertEqual(frame.frame_number, 7)
        self.assertEqual(frame.source_y, 192)
        self.assertEqual(tuple(frame.rgba[:4]), (7, 0, 0, 255))

        # Runtime +0x76 initializes from +0x70, so absent later override is exact.
        away = crop_prematch_numbered_shirt_frame(
            atlas,
            player_registered_club_id=99,
            team_club_id=10,
            primary_shirt_number=7,
            alternate_shirt_number=None,
        )
        self.assertEqual(away.frame_number, 7)

    def test_invalid_frame_number_fails_closed(self):
        atlas = PrematchNumberedShirtAtlas(
            source_kind="generated_generic_bmp",
            source_path="Team07.bmp",
            source_sha256="0" * 64,
            rgba=bytes(36 * 1280 * 4),
            club_id=10,
            use_alternate=True,
        )
        with self.assertRaisesRegex(PrematchShirtResourceError, "outside"):
            crop_prematch_numbered_shirt_frame(
                atlas,
                player_registered_club_id=10,
                team_club_id=10,
                primary_shirt_number=0,
            )


if __name__ == "__main__":
    unittest.main()
