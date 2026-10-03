"""Tests for checksum-gated original FastView score/table art loading."""
from dataclasses import replace
from pathlib import Path
import tempfile
import unittest

from ea444_decoder import EA444DecodedImage
from gate14_fastview_scores import CURRENT_FIX_GRID_1
from original_fastview_score_table_art import (
    FASTVIEW_SCORE_TABLE_ART_RESOURCES,
    OriginalFastViewScoreTableArtError,
    _read_verified_score_table_resource,
    build_fastview_score_table_art,
    load_verified_fastview_score_table_art,
)


def image(width, height, value):
    return EA444DecodedImage(
        width=width,
        height=height,
        rgba=bytes((value, value + 1, value + 2, 255)) * (width * height),
        consumed_bits=0,
        transparent_pixels=0,
    )


def exact_decoded():
    return {
        resource.name: image(*resource.size, 10 + index)
        for index, resource in enumerate(FASTVIEW_SCORE_TABLE_ART_RESOURCES)
    }


class OriginalFastViewScoreTableArtTests(unittest.TestCase):
    def test_exact_eight_resource_family_preserves_source_order_and_geometry(self):
        art = build_fastview_score_table_art(exact_decoded())
        self.assertEqual(len(art.resources), 8)
        self.assertEqual(
            tuple(item.source for item in art.resources),
            FASTVIEW_SCORE_TABLE_ART_RESOURCES,
        )
        self.assertEqual(
            tuple(item.source.name for item in art.resources),
            (
                "current_fix_grid_1",
                "current_fix_grid_2",
                "half_time_icon",
                "extra_time_icon",
                "penalties_icon",
                "full_time_icon",
                "current_table_grid_1",
                "current_table_grid_2",
            ),
        )
        for item in art.resources:
            self.assertEqual(
                (item.image.width, item.image.height),
                item.source.size,
            )

    def test_lookup_is_bound_to_exact_source_object_identity(self):
        decoded = exact_decoded()
        art = build_fastview_score_table_art(decoded)
        self.assertIs(
            art.image_for(CURRENT_FIX_GRID_1),
            decoded["current_fix_grid_1"],
        )
        fabricated = replace(CURRENT_FIX_GRID_1)
        with self.assertRaisesRegex(
            OriginalFastViewScoreTableArtError,
            "not loaded",
        ):
            art.image_for(fabricated)

    def test_decoded_family_rejects_missing_unexpected_and_geometry_drift(self):
        decoded = exact_decoded()
        decoded.pop("full_time_icon")
        with self.assertRaisesRegex(
            OriginalFastViewScoreTableArtError,
            "resource set differs",
        ):
            build_fastview_score_table_art(decoded)

        decoded = exact_decoded()
        decoded["replacement"] = decoded.pop("full_time_icon")
        with self.assertRaisesRegex(
            OriginalFastViewScoreTableArtError,
            "resource set differs",
        ):
            build_fastview_score_table_art(decoded)

        decoded = exact_decoded()
        decoded["current_fix_grid_1"] = image(1, 1, 1)
        with self.assertRaisesRegex(
            OriginalFastViewScoreTableArtError,
            "geometry mismatch",
        ):
            build_fastview_score_table_art(decoded)

    def test_source_reader_fails_closed_on_missing_size_and_checksum(self):
        resource = CURRENT_FIX_GRID_1
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / resource.source_path
            path.parent.mkdir(parents=True, exist_ok=True)

            with self.assertRaisesRegex(
                OriginalFastViewScoreTableArtError,
                "missing original",
            ):
                _read_verified_score_table_resource(root, resource)

            path.write_bytes(b"x")
            with self.assertRaisesRegex(
                OriginalFastViewScoreTableArtError,
                "byte-size mismatch",
            ):
                _read_verified_score_table_resource(root, resource)

            path.write_bytes(b"x" * resource.byte_size)
            with self.assertRaisesRegex(
                OriginalFastViewScoreTableArtError,
                "checksum mismatch",
            ):
                _read_verified_score_table_resource(root, resource)

    def test_loader_requires_canonical_executable_before_decode(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with self.assertRaisesRegex(
                OriginalFastViewScoreTableArtError,
                "missing canonical original executable",
            ):
                load_verified_fastview_score_table_art(
                    root,
                    root / "FOOTBAL.EXE",
                )


if __name__ == "__main__":
    unittest.main()
