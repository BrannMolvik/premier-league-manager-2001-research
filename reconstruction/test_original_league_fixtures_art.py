from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import call, patch

from ea444_decoder import EA444DecodedImage
from original_league_fixtures_art import (
    OriginalLeagueFixturesArtError,
    build_league_fixtures_grid_art,
    load_verified_league_fixtures_grid_art,
)
from original_league_fixtures_resources import (
    FIXTURES_HORIZONTAL_GRID,
    FIXTURES_VERTICAL_GRID,
    LEAGUE_FIXTURES_HORIZONTAL_GRID_POSITIONS,
    LEAGUE_FIXTURES_VERTICAL_GRID_POSITIONS,
)


def image(width: int, height: int, marker: int) -> EA444DecodedImage:
    return EA444DecodedImage(
        width,
        height,
        bytes((marker, marker + 1, marker + 2, 255)) * (width * height),
        consumed_bits=0,
        transparent_pixels=0,
    )


class OriginalLeagueFixturesArtTests(unittest.TestCase):
    def decoded(self):
        return {
            FIXTURES_VERTICAL_GRID.name: image(*FIXTURES_VERTICAL_GRID.size, 7),
            FIXTURES_HORIZONTAL_GRID.name: image(*FIXTURES_HORIZONTAL_GRID.size, 17),
        }

    def test_grid_art_preserves_all_source_setup_positions_and_full_source_sizes(self):
        art = build_league_fixtures_grid_art(self.decoded())

        self.assertEqual(len(art.vertical), 12)
        self.assertEqual(len(art.horizontal), 24)
        self.assertEqual(len(art.placements), 36)
        self.assertEqual(
            tuple((item.x, item.y) for item in art.vertical),
            LEAGUE_FIXTURES_VERTICAL_GRID_POSITIONS,
        )
        self.assertEqual(
            tuple((item.x, item.y) for item in art.horizontal),
            LEAGUE_FIXTURES_HORIZONTAL_GRID_POSITIONS,
        )
        self.assertTrue(
            all(
                (item.width, item.height) == FIXTURES_VERTICAL_GRID.size
                for item in art.vertical
            )
        )
        self.assertTrue(
            all(
                (item.width, item.height) == FIXTURES_HORIZONTAL_GRID.size
                for item in art.horizontal
            )
        )
        self.assertEqual(
            art.vertical[0].rect,
            (
                LEAGUE_FIXTURES_VERTICAL_GRID_POSITIONS[0][0],
                LEAGUE_FIXTURES_VERTICAL_GRID_POSITIONS[0][1],
                *FIXTURES_VERTICAL_GRID.size,
            ),
        )

    def test_grid_art_exposes_only_the_two_position_proven_resource_families(self):
        art = build_league_fixtures_grid_art(self.decoded())

        self.assertEqual(
            art.resource_names,
            (FIXTURES_VERTICAL_GRID.name, FIXTURES_HORIZONTAL_GRID.name),
        )
        self.assertEqual(
            {item.resource_name for item in art.placements},
            set(art.resource_names),
        )
        self.assertNotIn("date_fixtures_box", art.resource_names)
        self.assertNotIn("played_fixtures_box", art.resource_names)
        self.assertNotIn("red_fixtures_box", art.resource_names)
        self.assertNotIn("toggled_fixtures_box", art.resource_names)

    def test_missing_or_wrong_geometry_fails_closed(self):
        decoded = self.decoded()
        del decoded[FIXTURES_VERTICAL_GRID.name]
        with self.assertRaisesRegex(
            OriginalLeagueFixturesArtError,
            "Missing decoded League Fixtures grid art",
        ):
            build_league_fixtures_grid_art(decoded)

        decoded = self.decoded()
        decoded[FIXTURES_HORIZONTAL_GRID.name] = image(1, 1, 3)
        with self.assertRaisesRegex(
            OriginalLeagueFixturesArtError,
            "geometry mismatch",
        ):
            build_league_fixtures_grid_art(decoded)

        with self.assertRaisesRegex(
            OriginalLeagueFixturesArtError,
            "keyed by source resource name",
        ):
            build_league_fixtures_grid_art([])

    def test_loader_uses_exact_resource_specs_and_verified_executable_codec(self):
        vertical = image(*FIXTURES_VERTICAL_GRID.size, 23)
        horizontal = image(*FIXTURES_HORIZONTAL_GRID.size, 31)
        tables = object()
        quant = object()

        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            exe_path = root / "FOOTBAL.EXE"
            exe_path.write_bytes(b"canonical-executable-placeholder")
            with patch(
                "original_league_fixtures_art.tables_from_original_executable",
                return_value=tables,
            ) as table_loader, patch(
                "original_league_fixtures_art.quantization_from_verified_executable",
                return_value=quant,
            ) as quant_loader, patch(
                "original_league_fixtures_art._read_verified_resource",
                side_effect=(b"vertical-source", b"horizontal-source"),
            ) as read_resource, patch(
                "original_league_fixtures_art.decode_ea444",
                side_effect=(vertical, horizontal),
            ) as decoder:
                art = load_verified_league_fixtures_grid_art(root, exe_path)

        table_loader.assert_called_once_with(b"canonical-executable-placeholder")
        quant_loader.assert_called_once_with(b"canonical-executable-placeholder")
        self.assertEqual(
            read_resource.call_args_list,
            [
                call(root, FIXTURES_VERTICAL_GRID),
                call(root, FIXTURES_HORIZONTAL_GRID),
            ],
        )
        self.assertEqual(
            decoder.call_args_list,
            [
                call(b"vertical-source", tables=tables, quant=quant),
                call(b"horizontal-source", tables=tables, quant=quant),
            ],
        )
        self.assertEqual(len(art.placements), 36)

    def test_loader_missing_executable_fails_before_asset_decode(self):
        with tempfile.TemporaryDirectory() as temp_name:
            missing = Path(temp_name) / "FOOTBAL.EXE"
            with self.assertRaisesRegex(
                OriginalLeagueFixturesArtError,
                "Missing original executable",
            ):
                load_verified_league_fixtures_grid_art(
                    Path(temp_name),
                    missing,
                )


if __name__ == "__main__":
    unittest.main()
