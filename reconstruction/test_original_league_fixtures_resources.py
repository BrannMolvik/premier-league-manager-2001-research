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
    LEAGUE_FIXTURES_TOP_HEADER_ARRAY_OFFSET,
    LEAGUE_FIXTURES_SIDE_HEADER_ARRAY_OFFSET,
    LEAGUE_FIXTURES_HEADER_STRIDE,
    LEAGUE_FIXTURES_HEADER_IDENTITY_OFFSET,
    PLEAGUE_GRID_CLASS,
    PLEAGUE_GRID_TYPE_DESCRIPTOR_VA,
    PLEAGUE_GRID_VFTABLE_VA,
    LEAGUE_FIXTURE_STATUS_COMPLETE_BIT,
    LEAGUE_FIXTURE_SCORE_FORMAT,
    LEAGUE_FIXTURE_DATE_FORMAT,
    OriginalLeagueFixturesResourceError,
    PLAYED_FIXTURES_BOX,
    RED_FIXTURES_BOX,
    TOGGLED_FIXTURES_BOX,
    assert_league_fixtures_panel_identity,
    league_fixture_base_box,
    league_fixture_box_for_cell,
    league_fixture_visible_text,
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

    def test_grid_header_arrays_store_same_club_identity_at_plus_48(self):
        self.assertEqual(PLEAGUE_GRID_CLASS, "PLeagueGrid")
        self.assertEqual(PLEAGUE_GRID_TYPE_DESCRIPTOR_VA, 0x81C510)
        self.assertEqual(PLEAGUE_GRID_VFTABLE_VA, 0x7C23D0)
        self.assertEqual(LEAGUE_FIXTURES_TOP_HEADER_ARRAY_OFFSET, 0x9A0)
        self.assertEqual(LEAGUE_FIXTURES_SIDE_HEADER_ARRAY_OFFSET, 0x15D0)
        self.assertEqual(LEAGUE_FIXTURES_HEADER_STRIDE, 0x4C)
        self.assertEqual(LEAGUE_FIXTURES_HEADER_IDENTITY_OFFSET, 0x48)

    def test_populated_fixture_box_uses_completion_bit_only(self):
        self.assertIs(
            league_fixture_base_box(fixture_present=True, fixture_status_bits=0),
            DATE_FIXTURES_BOX,
        )
        self.assertIs(
            league_fixture_base_box(
                fixture_present=True,
                fixture_status_bits=LEAGUE_FIXTURE_STATUS_COMPLETE_BIT,
            ),
            PLAYED_FIXTURES_BOX,
        )
        # Unrelated status bits do not alter this source branch.
        self.assertIs(
            league_fixture_base_box(fixture_present=True, fixture_status_bits=0x20),
            DATE_FIXTURES_BOX,
        )

    def test_same_club_diagonal_remains_neutral_and_source_exact(self):
        self.assertIs(
            league_fixture_base_box(
                fixture_present=False,
                same_club_diagonal=False,
            ),
            DATE_FIXTURES_BOX,
        )
        self.assertIs(
            league_fixture_base_box(
                fixture_present=False,
                same_club_diagonal=True,
            ),
            RED_FIXTURES_BOX,
        )

    def test_selected_cell_overlay_has_precedence_over_base_box(self):
        for fixture_present, status, red in (
            (True, 0, False),
            (True, LEAGUE_FIXTURE_STATUS_COMPLETE_BIT, False),
            (False, 0, False),
            (False, 0, True),
        ):
            with self.subTest(
                fixture_present=fixture_present,
                status=status,
                red=red,
            ):
                self.assertIs(
                    league_fixture_box_for_cell(
                        fixture_present=fixture_present,
                        fixture_status_bits=status,
                        same_club_diagonal=red,
                        selected=True,
                    ),
                    TOGGLED_FIXTURES_BOX,
                )

    def test_visible_text_switches_between_date_and_score_at_completion_bit(self):
        self.assertEqual(LEAGUE_FIXTURE_SCORE_FORMAT, "%i:%i")
        self.assertEqual(LEAGUE_FIXTURE_DATE_FORMAT, "%02i.%02i")
        self.assertEqual(
            league_fixture_visible_text(
                fixture_status_bits=0,
                date_day=7,
                date_month=10,
            ),
            "07.10",
        )
        self.assertEqual(
            league_fixture_visible_text(
                fixture_status_bits=LEAGUE_FIXTURE_STATUS_COMPLETE_BIT,
                score_left=2,
                score_right=1,
            ),
            "2:1",
        )

    def test_box_and_text_helpers_fail_closed_on_invalid_types(self):
        bad_calls = (
            lambda: league_fixture_base_box(fixture_present=1),
            lambda: league_fixture_base_box(
                fixture_present=True, fixture_status_bits=True
            ),
            lambda: league_fixture_base_box(
                fixture_present=False, same_club_diagonal=1
            ),
            lambda: league_fixture_box_for_cell(
                fixture_present=True, selected=1
            ),
            lambda: league_fixture_visible_text(
                fixture_status_bits=True, date_day=1, date_month=1
            ),
            lambda: league_fixture_visible_text(
                fixture_status_bits=0, date_day=None, date_month=1
            ),
            lambda: league_fixture_visible_text(
                fixture_status_bits=LEAGUE_FIXTURE_STATUS_COMPLETE_BIT,
                score_left=1,
                score_right=None,
            ),
        )
        for call in bad_calls:
            with self.assertRaises(OriginalLeagueFixturesResourceError):
                call()

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
