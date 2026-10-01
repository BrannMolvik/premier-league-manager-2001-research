"""Regressions for original PLeagueFixtures resources and grid geometry."""
from pathlib import Path
import tempfile
import unittest

from original_league_fixtures_resources import (
    DATE_FIXTURES_BOX,
    FIXTURES_HORIZONTAL_GRID,
    FIXTURES_VERTICAL_GRID,
    LEAGUE_FIXTURES_HORIZONTAL_GRID_POSITIONS,
    LEAGUE_FIXTURES_RESOURCES,
    LEAGUE_FIXTURES_VERTICAL_GRID_POSITIONS,
    OriginalLeagueFixturesResourceError,
    PLAYED_FIXTURES_BOX,
    RED_FIXTURES_BOX,
    TOGGLED_FIXTURES_BOX,
    assert_league_fixtures_panel_identity,
    validate_original_league_fixtures_resources,
)


class OriginalLeagueFixturesResourceTests(unittest.TestCase):
    def test_six_exact_original_resources_are_source_bound(self):
        self.assertEqual(len(LEAGUE_FIXTURES_RESOURCES), 6)
        self.assertEqual(
            [resource.name for resource in LEAGUE_FIXTURES_RESOURCES],
            [
                "date_fixtures_box",
                "played_fixtures_box",
                "red_fixtures_box",
                "toggled_fixtures_box",
                "fixtures_hori_grid",
                "fixtures_vert_grid",
            ],
        )
        self.assertEqual(DATE_FIXTURES_BOX.size, (24, 13))
        self.assertEqual(PLAYED_FIXTURES_BOX.size, (24, 13))
        self.assertEqual(RED_FIXTURES_BOX.size, (24, 13))
        self.assertEqual(TOGGLED_FIXTURES_BOX.size, (24, 13))
        self.assertEqual(FIXTURES_HORIZONTAL_GRID.size, (132, 52))
        self.assertEqual(FIXTURES_VERTICAL_GRID.size, (24, 528))

    def test_exact_wrapper_handles_match_static_loader_chain(self):
        self.assertEqual(
            [resource.wrapper_va for resource in LEAGUE_FIXTURES_RESOURCES],
            [0x944B30, 0x944AF0, 0x944AB0, 0x944A70, 0x944A30, 0x9449F0],
        )
        self.assertEqual(
            [resource.raw_handle_va for resource in LEAGUE_FIXTURES_RESOURCES],
            [0x944B50, 0x944B10, 0x944AD0, 0x944A90, 0x944A50, 0x944A10],
        )

    def test_vertical_grid_positions_are_exact_twelve_by_29_step(self):
        self.assertEqual(len(LEAGUE_FIXTURES_VERTICAL_GRID_POSITIONS), 12)
        self.assertEqual(LEAGUE_FIXTURES_VERTICAL_GRID_POSITIONS[0], (378, 98))
        self.assertEqual(LEAGUE_FIXTURES_VERTICAL_GRID_POSITIONS[-1], (697, 98))
        self.assertTrue(
            all(
                b[0] - a[0] == 29 and a[1] == b[1] == 98
                for a, b in zip(
                    LEAGUE_FIXTURES_VERTICAL_GRID_POSITIONS,
                    LEAGUE_FIXTURES_VERTICAL_GRID_POSITIONS[1:],
                )
            )
        )

    def test_horizontal_grid_positions_are_exact_twenty_four_by_14_step(self):
        self.assertEqual(len(LEAGUE_FIXTURES_HORIZONTAL_GRID_POSITIONS), 24)
        self.assertEqual(LEAGUE_FIXTURES_HORIZONTAL_GRID_POSITIONS[0], (241, 235))
        self.assertEqual(LEAGUE_FIXTURES_HORIZONTAL_GRID_POSITIONS[-1], (241, 557))
        self.assertTrue(
            all(
                b[1] - a[1] == 14 and a[0] == b[0] == 241
                for a, b in zip(
                    LEAGUE_FIXTURES_HORIZONTAL_GRID_POSITIONS,
                    LEAGUE_FIXTURES_HORIZONTAL_GRID_POSITIONS[1:],
                )
            )
        )

    def test_resource_validator_fails_closed_on_synthetic_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for resource in LEAGUE_FIXTURES_RESOURCES:
                path = root / resource.source_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"x" * resource.byte_size)
            with self.assertRaisesRegex(
                OriginalLeagueFixturesResourceError,
                "checksum mismatch",
            ):
                validate_original_league_fixtures_resources(root)

    def test_panel_identity_guard_uses_source_proven_navigation_contract(self):
        assert_league_fixtures_panel_identity()


if __name__ == "__main__":
    unittest.main()
