"""Headless tests of recovered original TeamSelect resource composition."""
from hashlib import sha256
import os
from pathlib import Path
import tempfile
import unittest

from ea444_decoder import EA444DecodedImage
from original_button_frames import (
    OriginalButtonAtlas,
    PSTARTMENU_BUTTON_ATLAS,
    TEAMSELECT_BUTTON_ATLAS,
    split_original_button_atlas,
)
from original_front_end_layout import (
    TEAMSELECT_HIERARCHY_ROW_ORIGINS,
    TEAMSELECT_BACK_EVENT,
    TEAMSELECT_START_EVENT,
    TEAMSELECT_BACK_RECT,
    TEAMSELECT_START_RECT,
)
from original_teamselect_resources import (
    OriginalTeamSelectResourceError,
    TEAMSELECT_COMPOSED_BACKGROUND_RGBA_SHA256,
    _read_verified_art,
    assemble_original_teamselect_inputs,
    load_verified_original_teamselect_inputs,
)


def solid(width, height, pixel):
    return EA444DecodedImage(width, height, bytes(pixel) * (width * height), 0, 0)


def fixture():
    base = solid(800, 600, (1, 2, 3, 255))
    team = solid(800, 558, (4, 5, 6, 255))
    spec = TEAMSELECT_BUTTON_ATLAS
    atlas = solid(spec.source_width, spec.source_height, (11, 22, 33, 255))
    return base, team, split_original_button_atlas(atlas, spec)


class OriginalTeamSelectResourceTests(unittest.TestCase):
    def test_overlay_action_atlas_and_proven_row_origins(self):
        result = assemble_original_teamselect_inputs(*fixture())
        self.assertEqual(len(result.background_rgba), 800 * 600 * 4)
        self.assertEqual(len(result.action_atlas.frames), 23)
        self.assertEqual(result.hierarchy_row_origins, TEAMSELECT_HIERARCHY_ROW_ORIGINS)
        self.assertEqual(len(result.hierarchy_row_origins), 16)
        self.assertEqual(result.hierarchy_row_origins[0], (20, 78))
        self.assertEqual(result.hierarchy_row_origins[-1], (20, 528))
        self.assertEqual(
            result.proven_actions,
            ((TEAMSELECT_BACK_EVENT, TEAMSELECT_BACK_RECT),
             (TEAMSELECT_START_EVENT, TEAMSELECT_START_RECT)),
        )

        def pixel(x, y):
            offset = (y * 800 + x) * 4
            return result.background_rgba[offset:offset + 4]

        self.assertEqual(pixel(0, 0), bytes((4, 5, 6, 255)))
        self.assertEqual(pixel(799, 557), bytes((4, 5, 6, 255)))
        self.assertEqual(pixel(0, 558), bytes((1, 2, 3, 255)))
        self.assertEqual(pixel(799, 599), bytes((1, 2, 3, 255)))

    def test_rejects_unrelated_atlas_and_missing_original_source_frames(self):
        base, team, buttons = fixture()
        for invalid in (
            OriginalButtonAtlas(PSTARTMENU_BUTTON_ATLAS, buttons.frames),
            OriginalButtonAtlas(TEAMSELECT_BUTTON_ATLAS, buttons.frames[:-1]),
        ):
            with self.subTest(spec=invalid.spec):
                with self.assertRaises(OriginalTeamSelectResourceError):
                    assemble_original_teamselect_inputs(base, team, invalid)

    def test_wrong_source_bytes_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            asset = root / "Generic/team_choice/background.444"
            asset.parent.mkdir(parents=True)
            asset.write_bytes(b"replacement-art")
            with self.assertRaisesRegex(
                OriginalTeamSelectResourceError, "checksum mismatch"
            ):
                _read_verified_art(
                    root,
                    "FM2001_Art/Generic/team_choice/background.444",
                    "0" * 64,
                )

    @unittest.skipUnless(
        os.environ.get("FM2001_ORIGINAL_EXE")
        and os.environ.get("FM2001_ORIGINAL_444_ROOT"),
        "Licensed original executable and disc images not bundled with CI",
    )
    def test_opt_in_real_original_teamselect_background_and_frames(self):
        original = load_verified_original_teamselect_inputs(
            original_art_dir=Path(os.environ["FM2001_ORIGINAL_444_ROOT"]),
            original_executable=Path(os.environ["FM2001_ORIGINAL_EXE"]),
        )
        self.assertEqual(
            sha256(original.background_rgba).hexdigest(),
            TEAMSELECT_COMPOSED_BACKGROUND_RGBA_SHA256,
        )
        self.assertEqual(len(original.action_atlas.frames), 23)
        self.assertEqual(
            original.hierarchy_row_origins,
            TEAMSELECT_HIERARCHY_ROW_ORIGINS,
        )


if __name__ == "__main__":
    unittest.main()
