"""Tests for the exact original FastView TeamTable art boundary."""
from dataclasses import replace
from pathlib import Path
import tempfile
import unittest

from ea444_decoder import EA444DecodedImage
from gate14_fastview_team import (
    TEAM_BAR_1,
    TEAM_NAME_GRID_1,
)
from original_fastview_team_art import (
    FASTVIEW_TEAM_ART_RESOURCES,
    OriginalFastViewTeamArtError,
    _read_verified_resource,
    build_fastview_team_art,
)


def image(width, height, value):
    return EA444DecodedImage(
        width=width,
        height=height,
        rgba=bytes([value]) * (width * height * 4),
        consumed_bits=0,
        transparent_pixels=0,
    )


def complete_decoded():
    return {
        resource.name: image(*resource.size, index + 1)
        for index, resource in enumerate(FASTVIEW_TEAM_ART_RESOURCES)
    }


class OriginalFastViewTeamArtTests(unittest.TestCase):
    def test_exact_seven_resource_order_and_lookup(self):
        art = build_fastview_team_art(complete_decoded())

        self.assertEqual(
            tuple(item.source for item in art.resources),
            FASTVIEW_TEAM_ART_RESOURCES,
        )
        self.assertEqual(len(art.resources), 7)
        self.assertIs(art.image_for(TEAM_NAME_GRID_1), art.resources[0].image)
        self.assertIs(art.image_for(TEAM_BAR_1), art.resources[4].image)
        self.assertEqual(art.image_for(TEAM_NAME_GRID_1).width, 259)
        self.assertEqual(art.image_for(TEAM_BAR_1).width, 82)

    def test_requires_exact_complete_resource_name_set(self):
        decoded = complete_decoded()
        decoded.pop(TEAM_NAME_GRID_1.name)
        with self.assertRaisesRegex(
            OriginalFastViewTeamArtError,
            "differs from the exact source family",
        ):
            build_fastview_team_art(decoded)

        decoded = complete_decoded()
        decoded["replacement_bar"] = image(82, 16, 9)
        with self.assertRaisesRegex(
            OriginalFastViewTeamArtError,
            "differs from the exact source family",
        ):
            build_fastview_team_art(decoded)

    def test_rejects_decoded_geometry_or_rgba_drift(self):
        decoded = complete_decoded()
        decoded[TEAM_NAME_GRID_1.name] = image(258, 16, 1)
        with self.assertRaisesRegex(
            OriginalFastViewTeamArtError,
            "geometry mismatch",
        ):
            build_fastview_team_art(decoded)

        decoded = complete_decoded()
        good = decoded[TEAM_NAME_GRID_1.name]
        decoded[TEAM_NAME_GRID_1.name] = replace(
            good,
            rgba=good.rgba[:-4],
        )
        with self.assertRaisesRegex(
            OriginalFastViewTeamArtError,
            "RGBA payload incomplete",
        ):
            build_fastview_team_art(decoded)

    def test_lookup_is_identity_bound_not_name_only(self):
        art = build_fastview_team_art(complete_decoded())
        impostor = replace(TEAM_BAR_1)
        self.assertEqual(impostor, TEAM_BAR_1)
        self.assertIsNot(impostor, TEAM_BAR_1)
        with self.assertRaisesRegex(
            OriginalFastViewTeamArtError,
            "not loaded",
        ):
            art.image_for(impostor)

    def test_source_reader_rejects_missing_size_and_checksum_mismatch(self):
        resource = TEAM_BAR_1
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / resource.source_path
            path.parent.mkdir(parents=True, exist_ok=True)

            with self.assertRaisesRegex(
                OriginalFastViewTeamArtError,
                "Missing original TeamTable resource",
            ):
                _read_verified_resource(root, resource)

            path.write_bytes(b"x")
            with self.assertRaisesRegex(
                OriginalFastViewTeamArtError,
                "byte-size mismatch",
            ):
                _read_verified_resource(root, resource)

            path.write_bytes(b"x" * resource.byte_size)
            with self.assertRaisesRegex(
                OriginalFastViewTeamArtError,
                "checksum mismatch",
            ):
                _read_verified_resource(root, resource)

    def test_all_source_resources_keep_first_hand_identity_contract(self):
        expected = (
            ("team_name_grid", 3496, (259, 16)),
            ("team_name_grid_2", 3512, (259, 16)),
            ("team_name_grid_3", 3512, (259, 16)),
            ("team_name_grid_4", 3496, (259, 16)),
            ("team_bar_1", 2344, (82, 16)),
            ("blank_bar", 2776, (82, 16)),
            ("team_bar_2", 2312, (82, 16)),
        )
        self.assertEqual(
            tuple(
                (resource.name, resource.byte_size, resource.size)
                for resource in FASTVIEW_TEAM_ART_RESOURCES
            ),
            expected,
        )
        for resource in FASTVIEW_TEAM_ART_RESOURCES:
            self.assertTrue(resource.source_path.startswith("FM2001_Art/FastView/"))
            self.assertEqual(len(resource.sha256), 64)
            self.assertFalse(resource.imported)


if __name__ == "__main__":
    unittest.main()
