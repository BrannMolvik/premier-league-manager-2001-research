"""Verify exact source frame boundaries without inventing button hover states."""
from hashlib import sha256
import os
from pathlib import Path
import unittest

from ea444_decoder import EA444DecodedImage
from original_button_frames import (
    BUTTON_GROUP_LENGTHS,
    ButtonAtlasSpec,
    button_group_subframe_for_source_index,
    OriginalButtonAtlasError,
    OriginalButtonState,
    PSTARTMENU_BUTTON_ATLAS,
    TEAMSELECT_BUTTON_ATLAS,
    decode_verified_original_button_atlas,
    split_original_button_atlas,
)


class OriginalButtonAtlasTests(unittest.TestCase):
    def test_source_frame_inverse_mapping_matches_three_native_groups(self):
        self.assertEqual(
            [button_group_subframe_for_source_index(i) for i in range(23)],
            [(0, i) for i in range(11)]
            + [(1, i) for i in range(11)]
            + [(2, 0)],
        )
        for bad in (-1, 23, True, 1.0):
            with self.subTest(bad=bad):
                with self.assertRaises(OriginalButtonAtlasError):
                    button_group_subframe_for_source_index(bad)

    def test_native_group_mapping_animation_direction_and_disabled_frame(self):
        state = OriginalButtonState()
        self.assertEqual(BUTTON_GROUP_LENGTHS, (11, 11, 1))
        self.assertEqual((state.group, state.subframe, state.source_frame_index), (0, 0, 0))

        state.set_pointer_inside(True)
        for expected in range(1, 11):
            self.assertTrue(state.update())
            self.assertEqual(state.source_frame_index, expected)
        self.assertFalse(state.update())

        state.set_alternate(True)
        self.assertTrue(state.update())
        self.assertEqual((state.group, state.subframe, state.source_frame_index),
                         (1, 10, 21))
        state.set_pointer_inside(False)
        self.assertTrue(state.update())
        self.assertEqual(state.source_frame_index, 20)

        state.set_enabled(False)
        self.assertTrue(state.update())
        self.assertEqual((state.group, state.subframe, state.source_frame_index),
                         (2, 0, 22))
        self.assertFalse(state.update())

        state.set_enabled(True)
        state.set_alternate(False)
        self.assertTrue(state.update())
        self.assertEqual((state.group, state.subframe, state.source_frame_index),
                         (0, 0, 0))

    def test_exact_original_filenames_atlas_geometry_and_frame_count(self):
        self.assertTrue(PSTARTMENU_BUTTON_ATLAS.source_path.endswith("button_type_1.444"))
        self.assertTrue(TEAMSELECT_BUTTON_ATLAS.source_path.endswith("choice_start_anim.444"))
        self.assertEqual(
            (PSTARTMENU_BUTTON_ATLAS.source_width,
             PSTARTMENU_BUTTON_ATLAS.source_height,
             PSTARTMENU_BUTTON_ATLAS.frame_width,
             PSTARTMENU_BUTTON_ATLAS.frame_height,
             PSTARTMENU_BUTTON_ATLAS.frame_count),
            (169, 575, 169, 25, 23),
        )
        self.assertEqual(
            (TEAMSELECT_BUTTON_ATLAS.source_width,
             TEAMSELECT_BUTTON_ATLAS.source_height,
             TEAMSELECT_BUTTON_ATLAS.frame_width,
             TEAMSELECT_BUTTON_ATLAS.frame_height,
             TEAMSELECT_BUTTON_ATLAS.frame_count),
            (150, 736, 150, 32, 23),
        )

    def test_vertical_frames_preserve_every_original_pixel_without_reordering(self):
        spec = ButtonAtlasSpec("synthetic", sha256(b"fixture").hexdigest(), 2, 6, 2, 2)
        rows = [
            bytes((i + 1, i + 2, i + 3, 255)) * 4
            for i in range(3)
        ]
        original = EA444DecodedImage(2, 6, b"".join(rows), 0, 0)
        atlas = split_original_button_atlas(original, spec)
        self.assertEqual(len(atlas.frames), 3)
        for index, row in enumerate(rows):
            self.assertEqual(atlas.frame(index).rgba, row)
            self.assertEqual(
                (atlas.frame(index).width, atlas.frame(index).height), (2, 2)
            )
        self.assertEqual(b"".join(frame.rgba for frame in atlas.frames), original.rgba)
        for bad in (-1, 3, True, 1.0):
            with self.subTest(bad=bad):
                with self.assertRaises(OriginalButtonAtlasError):
                    atlas.frame(bad)

        with self.assertRaisesRegex(OriginalButtonAtlasError, "23-frame"):
            atlas.frame_for_state(OriginalButtonState())

    def test_dimension_mismatch_and_inconsistent_slicing_are_rejected(self):
        original = EA444DecodedImage(2, 6, bytes(48), 0, 0)
        bad_spec = ButtonAtlasSpec("bad", "0" * 64, 2, 7, 2, 2)
        with self.assertRaises(OriginalButtonAtlasError):
            split_original_button_atlas(original, bad_spec)
        with self.assertRaises(OriginalButtonAtlasError):
            split_original_button_atlas(
                original, ButtonAtlasSpec("bad", "0" * 64, 3, 6, 3, 2)
            )

    def test_wrong_source_hash_fails_before_decode_without_fallback_art(self):
        with self.assertRaisesRegex(OriginalButtonAtlasError, "SHA-256 mismatch"):
            decode_verified_original_button_atlas(
                b"made-up replacement bytes",
                spec=PSTARTMENU_BUTTON_ATLAS,
                tables=None,
                quant=None,
            )

    @unittest.skipUnless(
        os.environ.get("FM2001_ORIGINAL_EXE")
        and os.environ.get("FM2001_ORIGINAL_444_ROOT"),
        "Exact licensed source atlas/executable bytes not bundled with CI",
    )
    def test_opt_in_actual_source_menu_and_teamselect_atlas_roundtrip(self):
        from ea444_decoder import decode_ea444
        from ea444_quantization import quantization_from_verified_exe_path
        from ea444_tables import tables_from_verified_exe_path

        exe = Path(os.environ["FM2001_ORIGINAL_EXE"])
        root = Path(os.environ["FM2001_ORIGINAL_444_ROOT"])
        quant = quantization_from_verified_exe_path(exe)
        tables = tables_from_verified_exe_path(exe)
        for spec in (PSTARTMENU_BUTTON_ATLAS, TEAMSELECT_BUTTON_ATLAS):
            with self.subTest(source_path=spec.source_path):
                # Root is the on-disc FM2001_Art directory.
                relative = spec.source_path.removeprefix("FM2001_Art/")
                source = (root / relative).read_bytes()
                self.assertEqual(sha256(source).hexdigest(), spec.source_sha256)
                atlas = decode_verified_original_button_atlas(
                    source, spec=spec, tables=tables, quant=quant
                )
                decoded = decode_ea444(source, tables=tables, quant=quant)
                self.assertEqual(len(atlas.frames), 23)
                self.assertEqual(
                    b"".join(frame.rgba for frame in atlas.frames), decoded.rgba
                )


if __name__ == "__main__":
    unittest.main()
