from __future__ import annotations

from datetime import date
from types import SimpleNamespace
import unittest

from gate13_management_source_data import FixtureRowView, LeagueFixturesGridSourceView
from original_league_fixtures_presenter import (
    OriginalLeagueFixturesPresentationError,
    build_league_fixtures_snapshot,
)
from original_league_fixtures_resources import LEAGUE_FIXTURES_RESOURCES


class OriginalLeagueFixturesPresenterTests(unittest.TestCase):
    def source(self):
        members = tuple(range(20))
        return LeagueFixturesGridSourceView(
            competition_id=0,
            member_club_ids=members,
            scheduled_matchday_count=38,
            schedule_cycle_count=2,
            matrix_layer_count=1,
            fixtures_in_source_order=(
                FixtureRowView(
                    source_fixture_index=0,
                    fixture_id=100,
                    round_index=0,
                    scheduled_date=date(2000, 8, 19),
                    home_club_id=0,
                    home_club_name="Club 0",
                    away_club_id=1,
                    away_club_name="Club 1",
                    played=True,
                    home_goals=2,
                    away_goals=1,
                ),
                FixtureRowView(
                    source_fixture_index=1,
                    fixture_id=101,
                    round_index=1,
                    scheduled_date=date(2000, 8, 26),
                    home_club_id=1,
                    home_club_name="Club 1",
                    away_club_id=0,
                    away_club_name="Club 0",
                    played=False,
                    home_goals=None,
                    away_goals=None,
                ),
            ),
        )

    def test_premier_league_matrix_uses_one_exact_directed_pair_layer(self):
        staged = tuple(resource.name for resource in LEAGUE_FIXTURES_RESOURCES)
        snapshot = build_league_fixtures_snapshot(
            self.source(),
            staged_resource_names=staged,
        )

        self.assertEqual(snapshot.member_club_ids, tuple(range(20)))
        self.assertEqual(snapshot.schedule_cycle_count, 2)
        self.assertEqual(snapshot.matrix_layer_count, 1)
        self.assertEqual(snapshot.visible_column_club_ids, tuple(range(12)))
        self.assertEqual(snapshot.visible_row_club_ids, tuple(range(20)))
        self.assertEqual(len(snapshot.vertical_grid_positions), 12)
        self.assertEqual(len(snapshot.horizontal_grid_positions), 20)
        self.assertEqual(len(snapshot.cells), 20 * 12)
        self.assertTrue(snapshot.exact_art_staged)

        cells = {(cell.row, cell.column): cell for cell in snapshot.cells}
        self.assertEqual(cells[(0, 1)].fixture_id, 100)
        self.assertTrue(cells[(0, 1)].played)
        self.assertEqual(cells[(0, 1)].text, "2:1")
        self.assertEqual(cells[(0, 1)].resource_name, "played_fixtures_box")

        self.assertEqual(cells[(1, 0)].fixture_id, 101)
        self.assertFalse(cells[(1, 0)].played)
        self.assertEqual(cells[(1, 0)].text, "26.08")
        self.assertEqual(cells[(1, 0)].resource_name, "date_fixtures_box")

        self.assertIsNone(cells[(0, 0)].fixture_id)
        self.assertIsNone(cells[(0, 0)].text)
        self.assertEqual(cells[(0, 0)].resource_name, "red_fixtures_box")
        self.assertEqual(cells[(2, 3)].resource_name, "date_fixtures_box")

    def test_second_column_page_preserves_member_order_and_matrix_identity(self):
        snapshot = build_league_fixtures_snapshot(self.source(), column_offset=8)
        self.assertEqual(snapshot.visible_column_club_ids, tuple(range(8, 20)))
        self.assertEqual(len(snapshot.cells), 20 * 12)
        cell = next(
            cell for cell in snapshot.cells
            if cell.row == 0 and cell.column == 0
        )
        self.assertEqual((cell.row_club_id, cell.column_club_id), (0, 8))
        self.assertEqual(cell.matrix_slot, 8)

    def test_selected_cell_uses_exact_toggled_overlay(self):
        snapshot = build_league_fixtures_snapshot(
            self.source(), selected_cell=(1, 0)
        )
        cell = next(
            cell for cell in snapshot.cells
            if cell.row == 0 and cell.column == 1
        )
        self.assertTrue(cell.selected)
        self.assertEqual(cell.resource_name, "toggled_fixtures_box")
        self.assertEqual(cell.text, "2:1")

    def test_duplicate_directed_pair_fails_when_source_allocated_layer_is_full(self):
        source = self.source()
        duplicate = FixtureRowView(
            source_fixture_index=2,
            fixture_id=102,
            round_index=2,
            scheduled_date=date(2000, 9, 2),
            home_club_id=0,
            home_club_name="Club 0",
            away_club_id=1,
            away_club_name="Club 1",
            played=False,
            home_goals=None,
            away_goals=None,
        )
        broken = SimpleNamespace(
            competition_id=source.competition_id,
            member_club_ids=source.member_club_ids,
            scheduled_matchday_count=source.scheduled_matchday_count,
            schedule_cycle_count=source.schedule_cycle_count,
            matrix_layer_count=source.matrix_layer_count,
            fixtures_in_source_order=source.fixtures_in_source_order + (duplicate,),
        )
        with self.assertRaisesRegex(
            OriginalLeagueFixturesPresentationError,
            "exceeds the source-allocated",
        ):
            build_league_fixtures_snapshot(broken)

    def test_unplayed_fixture_without_recovered_date_fails_closed(self):
        source = self.source()
        fixture = source.fixtures_in_source_order[1]
        broken_fixture = FixtureRowView(
            source_fixture_index=fixture.source_fixture_index,
            fixture_id=fixture.fixture_id,
            round_index=fixture.round_index,
            scheduled_date=None,
            home_club_id=fixture.home_club_id,
            home_club_name=fixture.home_club_name,
            away_club_id=fixture.away_club_id,
            away_club_name=fixture.away_club_name,
            played=False,
            home_goals=None,
            away_goals=None,
        )
        broken = SimpleNamespace(
            competition_id=0,
            member_club_ids=source.member_club_ids,
            scheduled_matchday_count=38,
            schedule_cycle_count=2,
            matrix_layer_count=1,
            fixtures_in_source_order=(broken_fixture,),
        )
        with self.assertRaisesRegex(
            OriginalLeagueFixturesPresentationError,
            "scheduled date",
        ):
            build_league_fixtures_snapshot(broken)

    def test_layer_count_must_match_recovered_helper_divide_by_two(self):
        source = self.source()
        broken = SimpleNamespace(
            competition_id=0,
            member_club_ids=source.member_club_ids,
            scheduled_matchday_count=38,
            schedule_cycle_count=2,
            matrix_layer_count=2,
            fixtures_in_source_order=(),
        )
        with self.assertRaisesRegex(
            OriginalLeagueFixturesPresentationError,
            "0x616F40 / 2",
        ):
            build_league_fixtures_snapshot(broken)


if __name__ == "__main__":
    unittest.main()
