"""Tests for decoded original FastViewTeam source art."""
from pathlib import Path
import unittest

from ea444_decoder import EA444DecodedImage
from original_fastview_team_art import (
    OriginalFastViewTeamArtError,
    build_fastview_team_art,
)
from original_fastview_team_resources import FASTVIEW_TEAM_TABLE_RESOURCES


def decoded(width: int, height: int, value: int) -> EA444DecodedImage:
    return EA444DecodedImage(
        width=width,
        height=height,
        rgba=bytes([value]) * (width * height * 4),
        consumed_bits=0,
        transparent_pixels=0,
    )


class OriginalFastViewTeamArtTests(unittest.TestCase):
    def setUp(self):
        self.decoded = {
            resource.name: decoded(
                resource.size[0],
                resource.size[1],
                index + 1,
            )
            for index, resource in enumerate(FASTVIEW_TEAM_TABLE_RESOURCES)
        }

    def test_builds_exact_seven_resource_family_in_source_contract_order(self):
        art = build_fastview_team_art(self.decoded)

        self.assertEqual(
            [item.resource_name for item in art.resources],
            [item.name for item in FASTVIEW_TEAM_TABLE_RESOURCES],
        )
        for resource in FASTVIEW_TEAM_TABLE_RESOURCES:
            item = art.resource_named(resource.name)
            self.assertEqual(item.source_path, resource.source_path)
            self.assertEqual((item.width, item.height), resource.size)
            self.assertIs(item.rgba, self.decoded[resource.name].rgba)

    def test_decoded_art_does_not_promote_unrecovered_raster_boundaries(self):
        art = build_fastview_team_art(self.decoded)

        self.assertFalse(art.generic_text_rasterization_available)
        self.assertFalse(art.dynamic_picture_crop_mapping_recovered)
        self.assertFalse(art.cross_component_z_order_recovered)
        self.assertFalse(art.complete_team_table_raster_available)

    def test_missing_or_wrong_decoded_resource_fails_closed(self):
        missing = dict(self.decoded)
        del missing["team_bar_1"]
        with self.assertRaisesRegex(
            OriginalFastViewTeamArtError,
            "Missing decoded FastViewTeam art",
        ):
            build_fastview_team_art(missing)

        wrong = dict(self.decoded)
        wrong["blank_bar"] = decoded(81, 16, 9)
        with self.assertRaisesRegex(
            OriginalFastViewTeamArtError,
            "geometry mismatch",
        ):
            build_fastview_team_art(wrong)

        with self.assertRaisesRegex(
            OriginalFastViewTeamArtError,
            "keyed by source resource name",
        ):
            build_fastview_team_art([])

    def test_art_module_does_not_import_gameplay_or_simulation(self):
        source = Path(__file__).with_name("original_fastview_team_art.py").read_text(
            encoding="utf-8"
        )
        for forbidden in (
            "match_simulation",
            "match_calculator",
            "match_engine_rng",
            "human_gameplay",
            "gameplay_controller",
            "random",
            "commentary_text",
            "sound_effect",
        ):
            self.assertNotIn(f"import {forbidden}", source)
            self.assertNotIn(f"from {forbidden}", source)


if __name__ == "__main__":
    unittest.main()
