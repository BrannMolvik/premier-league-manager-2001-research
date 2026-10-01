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
    LEAGUE_FIXTURE_STATUS_COMPLETE_BIT,
    LEAGUE_FIXTURE_MATRIX_EXCLUDED_STATUS_BIT,
    LEAGUE_FIXTURE_MATRIX_KIND_CODE,
    LEAGUE_FIXTURES_GLOBAL_FIXTURE_BUCKET_COUNT,
    LEAGUE_FIXTURES_VISIBLE_COLUMNS,
    LEAGUE_FIXTURES_VISIBLE_ROWS,
    LEAGUE_FIXTURE_SCORE_FORMAT,
    LEAGUE_FIXTURE_DATE_FORMAT,
    OriginalLeagueFixturesResourceError,
    PLAYED_FIXTURES_BOX,
    RED_FIXTURES_BOX,
    TOGGLED_FIXTURES_BOX,
    assert_league_fixtures_panel_identity,
    league_fixture_base_box,
    league_fixture_empty_slot_is_self_match,
    league_fixture_first_free_repeat_slot,
    league_fixture_matrix_accepts_candidate,
    league_fixture_matrix_slot,
    league_fixtures_column_page_offset,
    league_fixtures_grid_indices_from_point,
    validate_league_fixtures_grid_selection_index,
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

    def test_empty_slot_red_box_is_exact_same_club_diagonal(self):
        self.assertFalse(league_fixture_empty_slot_is_self_match(4, 7))
        self.assertTrue(league_fixture_empty_slot_is_self_match(4, 4))
        self.assertIs(
            league_fixture_base_box(
                fixture_present=False,
                empty_slot_same_club=False,
            ),
            DATE_FIXTURES_BOX,
        )
        self.assertIs(
            league_fixture_base_box(
                fixture_present=False,
                empty_slot_same_club=True,
            ),
            RED_FIXTURES_BOX,
        )
        for bad in (True, -1, None, "4"):
            with self.subTest(bad=bad):
                with self.assertRaises(OriginalLeagueFixturesResourceError):
                    league_fixture_empty_slot_is_self_match(bad, 4)

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
                        empty_slot_same_club=red,
                        selected=True,
                    ),
                    TOGGLED_FIXTURES_BOX,
                )

    def test_matrix_candidate_filter_is_exact_and_status_bit_0x20_stays_neutral(self):
        base = dict(
            kind_code=LEAGUE_FIXTURE_MATRIX_KIND_CODE,
            fixture_competition_identity=6,
            selected_competition_identity=6,
            fixture_status_bits=0,
            left_club_identity=2,
            right_club_identity=9,
        )
        self.assertTrue(league_fixture_matrix_accepts_candidate(**base))

        rejected = (
            {**base, "kind_code": 0},
            {**base, "fixture_competition_identity": 5},
            {**base, "fixture_status_bits": LEAGUE_FIXTURE_MATRIX_EXCLUDED_STATUS_BIT},
            {**base, "left_club_identity": None},
            {**base, "right_club_identity": None},
        )
        for case in rejected:
            with self.subTest(case=case):
                self.assertFalse(league_fixture_matrix_accepts_candidate(**case))

        # Unrelated completion/status bit 0 is not one of this builder's filters.
        self.assertTrue(
            league_fixture_matrix_accepts_candidate(
                **{**base, "fixture_status_bits": LEAGUE_FIXTURE_STATUS_COMPLETE_BIT}
            )
        )

    def test_matrix_slot_is_pair_major_with_n_squared_repeat_layers(self):
        self.assertEqual(
            league_fixture_matrix_slot(
                club_count=20,
                left_member_index=3,
                right_member_index=7,
                repeat_layer=0,
            ),
            67,
        )
        self.assertEqual(
            league_fixture_matrix_slot(
                club_count=20,
                left_member_index=3,
                right_member_index=7,
                repeat_layer=1,
            ),
            467,
        )

    def test_repeated_pair_uses_first_free_n_squared_layer(self):
        club_count = 4
        layers = 3
        occupied = [False] * (club_count * club_count * layers)
        first = league_fixture_matrix_slot(
            club_count=club_count,
            left_member_index=1,
            right_member_index=2,
            repeat_layer=0,
        )
        second = league_fixture_matrix_slot(
            club_count=club_count,
            left_member_index=1,
            right_member_index=2,
            repeat_layer=1,
        )
        occupied[first] = True
        self.assertEqual(
            league_fixture_first_free_repeat_slot(
                occupied,
                club_count=club_count,
                left_member_index=1,
                right_member_index=2,
                layer_count=layers,
            ),
            second,
        )
        occupied[second] = True
        occupied[
            league_fixture_matrix_slot(
                club_count=club_count,
                left_member_index=1,
                right_member_index=2,
                repeat_layer=2,
            )
        ] = True
        with self.assertRaisesRegex(
            OriginalLeagueFixturesResourceError,
            "all source-allocated repeat layers",
        ):
            league_fixture_first_free_repeat_slot(
                occupied,
                club_count=club_count,
                left_member_index=1,
                right_member_index=2,
                layer_count=layers,
            )

    def test_fixture_chain_scan_has_exact_373_head_slots(self):
        self.assertEqual(LEAGUE_FIXTURES_GLOBAL_FIXTURE_BUCKET_COUNT, 373)

    def test_column_paging_moves_exactly_twelve_and_clamps_to_last_window(self):
        self.assertEqual(LEAGUE_FIXTURES_VISIBLE_COLUMNS, 12)
        self.assertEqual(league_fixtures_column_page_offset(0, 20, 1), 8)
        self.assertEqual(league_fixtures_column_page_offset(8, 20, -1), 0)
        self.assertEqual(league_fixtures_column_page_offset(0, 36, 1), 12)
        self.assertEqual(league_fixtures_column_page_offset(12, 36, 1), 24)
        self.assertEqual(league_fixtures_column_page_offset(24, 36, 1), 24)
        self.assertEqual(league_fixtures_column_page_offset(0, 8, 1), 0)

    def test_grid_point_mapping_uses_exact_29_by_14_steps(self):
        self.assertEqual(
            league_fixtures_grid_indices_from_point(
                x=100,
                y=200,
                origin_x=100,
                origin_y=200,
            ),
            (0, 0),
        )
        self.assertEqual(
            league_fixtures_grid_indices_from_point(
                x=100 + 29 * 11 + 28,
                y=200 + 14 * 23 + 13,
                origin_x=100,
                origin_y=200,
            ),
            (11, 23),
        )
        for x, y in (
            (99, 200),
            (100, 199),
            (100 + 29 * 12, 200),
            (100, 200 + 14 * 24),
        ):
            with self.subTest(x=x, y=y):
                with self.assertRaises(OriginalLeagueFixturesResourceError):
                    league_fixtures_grid_indices_from_point(
                        x=x,
                        y=y,
                        origin_x=100,
                        origin_y=200,
                    )

    def test_dispatch_selector_ranges_are_twelve_columns_and_twenty_four_rows(self):
        self.assertEqual(LEAGUE_FIXTURES_VISIBLE_ROWS, 24)
        for index in range(12):
            self.assertEqual(
                validate_league_fixtures_grid_selection_index(index, axis="column"),
                index,
            )
        for index in range(24):
            self.assertEqual(
                validate_league_fixtures_grid_selection_index(index, axis="row"),
                index,
            )
        for index, axis in ((12, "column"), (24, "row"), (-1, "row")):
            with self.assertRaises(OriginalLeagueFixturesResourceError):
                validate_league_fixtures_grid_selection_index(index, axis=axis)

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
                fixture_present=False, empty_slot_same_club=1
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
