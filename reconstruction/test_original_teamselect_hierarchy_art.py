"""Regress raw source ordering of the two recovered TeamSelect hierarchy strips."""
from hashlib import sha256
import os
from pathlib import Path
import unittest

from ea444_decoder import EA444DecodedImage, decode_ea444
from original_front_end_layout import (
    TEAMSELECT_HIERARCHY_ANIM_PATH,
    TEAMSELECT_HIERARCHY_BARS_PATH,
    TEAMSELECT_HIERARCHY_BARS_FRAME_SIZE,
    TEAMSELECT_HIERARCHY_FRAME_SIZE,
)
from original_teamselect_hierarchy_art import (
    HIERARCHY_ANIM_SPEC,
    HIERARCHY_BARS_SPEC,
    OriginalHierarchyStripError,
    OriginalTeamSelectHierarchyArt,
    decode_verified_hierarchy_art,
    decode_verified_hierarchy_strip,
    split_hierarchy_source_strip,
)


def rgba_image(w: int, h: int, rgba: bytes) -> EA444DecodedImage:
    return EA444DecodedImage(w, h, rgba, 0, 0)


class OriginalHierarchyStripTests(unittest.TestCase):
    def test_specs_match_recovered_original_source_bindings(self):
        self.assertEqual(HIERARCHY_ANIM_SPEC.path, TEAMSELECT_HIERARCHY_ANIM_PATH)
        self.assertEqual(HIERARCHY_BARS_SPEC.path, TEAMSELECT_HIERARCHY_BARS_PATH)
        self.assertEqual(
            (HIERARCHY_ANIM_SPEC.frame_width, HIERARCHY_ANIM_SPEC.frame_height),
            TEAMSELECT_HIERARCHY_FRAME_SIZE,
        )
        self.assertEqual(
            (HIERARCHY_BARS_SPEC.frame_width, HIERARCHY_BARS_SPEC.frame_height),
            TEAMSELECT_HIERARCHY_BARS_FRAME_SIZE,
        )
        self.assertEqual(
            HIERARCHY_ANIM_SPEC.source_sha256,
            "de53b9ed410bf0456e79c03b305cfb7a1ccaae4c10fb77a50fefd7106c2d4e22",
        )
        self.assertEqual(
            HIERARCHY_BARS_SPEC.source_sha256,
            "bdf28df3c32275fa59934be8c85f1cea33626d47dc4f2b3e59619278c7ca73fa",
        )

    def test_slicing_preserves_every_pixel_and_original_frame_order(self):
        spec = HIERARCHY_ANIM_SPEC
        per_frame = spec.frame_width * spec.frame_height
        source = (
            bytes((1, 2, 3, 255)) * per_frame +
            bytes((5, 6, 7, 255)) * per_frame
        )
        strip = split_hierarchy_source_strip(
            rgba_image(spec.frame_width, spec.frame_height * 2, source), spec
        )
        self.assertEqual(strip.source_height, 58)
        self.assertEqual(len(strip.frames), 2)
        self.assertEqual(strip.source_frame(0).rgba[:4], bytes((1, 2, 3, 255)))
        self.assertEqual(strip.source_frame(1).rgba[:4], bytes((5, 6, 7, 255)))
        self.assertEqual(b"".join(frame.rgba for frame in strip.frames), source)
        for index in (-1, 2, True, 0.5):
            with self.subTest(index=index):
                with self.assertRaises(OriginalHierarchyStripError):
                    strip.source_frame(index)

    def test_distinct_animation_and_bars_geometry_and_identity(self):
        anim = HIERARCHY_ANIM_SPEC
        bars = HIERARCHY_BARS_SPEC
        animation = split_hierarchy_source_strip(
            rgba_image(
                anim.frame_width, anim.frame_height,
                bytes((8, 9, 10, 255)) * (anim.frame_width * anim.frame_height),
            ),
            anim,
        )
        bar_strip = split_hierarchy_source_strip(
            rgba_image(
                bars.frame_width, bars.frame_height * 3,
                bytes((11, 12, 13, 255)) * (bars.frame_width * bars.frame_height * 3),
            ),
            bars,
        )
        art = OriginalTeamSelectHierarchyArt(animation, bar_strip)
        self.assertEqual(
            (len(art.animation.frames), len(art.bars.frames)), (1, 3)
        )
        with self.assertRaises(OriginalHierarchyStripError):
            OriginalTeamSelectHierarchyArt(bar_strip, animation)

    def test_fail_closed_on_unproven_atlas_geometry_and_hash(self):
        spec = HIERARCHY_ANIM_SPEC
        with self.assertRaisesRegex(OriginalHierarchyStripError, "width"):
            split_hierarchy_source_strip(
                rgba_image(31, 29, bytes(31 * 29 * 4)), spec
            )
        with self.assertRaisesRegex(OriginalHierarchyStripError, "height"):
            split_hierarchy_source_strip(
                rgba_image(30, 30, bytes(30 * 30 * 4)), spec
            )
        with self.assertRaisesRegex(OriginalHierarchyStripError, "checksum"):
            decode_verified_hierarchy_strip(
                b"replacement art is not original",
                spec=spec,
                tables=None, quant=None,
            )

    @unittest.skipUnless(
        os.environ.get("FM2001_ORIGINAL_EXE")
        and os.environ.get("FM2001_ORIGINAL_444_ROOT"),
        "Licensed source bytes intentionally absent from hosted CI",
    )
    def test_opt_in_canonical_source_strips_preserve_complete_decoded_images(self):
        from ea444_quantization import quantization_from_verified_exe_path
        from ea444_tables import tables_from_verified_exe_path

        exe = Path(os.environ["FM2001_ORIGINAL_EXE"])
        root = Path(os.environ["FM2001_ORIGINAL_444_ROOT"])
        tables = tables_from_verified_exe_path(exe)
        quant = quantization_from_verified_exe_path(exe)
        originals = []
        for spec in (HIERARCHY_ANIM_SPEC, HIERARCHY_BARS_SPEC):
            source = (root / spec.path.removeprefix("FM2001_Art/")).read_bytes()
            self.assertEqual(sha256(source).hexdigest(), spec.source_sha256)
            strip = decode_verified_hierarchy_strip(
                source, spec=spec, tables=tables, quant=quant
            )
            decoded = decode_ea444(source, tables=tables, quant=quant)
            self.assertEqual(
                b"".join(frame.rgba for frame in strip.frames), decoded.rgba
            )
            originals.append(source)
        art = decode_verified_hierarchy_art(
            *originals, tables=tables, quant=quant
        )
        self.assertEqual(
            (art.animation.spec, art.bars.spec),
            (HIERARCHY_ANIM_SPEC, HIERARCHY_BARS_SPEC),
        )


if __name__ == "__main__":
    unittest.main()
