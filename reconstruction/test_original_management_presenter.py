from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import unittest

from front_end_session import FrontEndSession
from front_end_state import StartMenuControl, TeamSelectControl
from gate13_management_source_data import (
    ClubHeaderView,
    FixtureRowView,
    LeagueFixturesGridSourceView,
)
from original_league_fixtures_resources import LEAGUE_FIXTURES_RESOURCES
from original_league_tables_resources import LEAGUE_TABLES_RESOURCES
from original_management_presenter import (
    OriginalManagementPresentationError,
    OriginalManagementPresenter,
    build_fresh_management_snapshot,
    build_management_panel_snapshot,
)


class Backend:
    def select_club(self, club_id):
        return ("manager", club_id)


@dataclass(frozen=True)
class Row:
    source_roster_index: int
    player_id: int
    full_name: str
    current_position: int = 12
    condition: int = 90
    recent_form_average: float = 7.0
    current_role_rating: int = 61


@dataclass(frozen=True)
class TableRow:
    position: int
    club_id: int
    club_name: str
    short_name: str
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int


class Bridge:
    def __init__(self, backend):
        self.backend = backend

    def club_header(self):
        return ClubHeaderView(12, "Source Club", "Source", date(2000, 8, 1))

    def squad_rows(self):
        return tuple(Row(i, 1000 + i, f"Player {i}") for i in range(23))

    def fixture_rows(self):
        return (
            FixtureRowView(
                source_fixture_index=0,
                fixture_id=700,
                round_index=0,
                scheduled_date=date(2000, 8, 19),
                home_club_id=12,
                home_club_name="Source Club",
                away_club_id=13,
                away_club_name="Visitors",
                played=False,
                home_goals=None,
                away_goals=None,
            ),
        )

    def league_fixtures_grid_source(self):
        return LeagueFixturesGridSourceView(
            competition_id=0,
            member_club_ids=(12, 13),
            scheduled_matchday_count=2,
            schedule_cycle_count=2,
            matrix_layer_count=1,
            fixtures_in_source_order=self.fixture_rows(),
        )

    def league_table_rows(self):
        return (
            TableRow(
                position=1,
                club_id=12,
                club_name="Source Club",
                short_name="Source",
                played=1,
                wins=1,
                draws=0,
                losses=0,
                goals_for=2,
                goals_against=0,
                goal_difference=2,
                points=3,
            ),
        )


class OriginalManagementPresenterTests(unittest.TestCase):
    def test_integration_presenter_has_no_direct_simulation_import(self):
        source = Path(__file__).with_name("original_management_presenter.py").read_text(
            encoding="utf-8"
        )
        for forbidden in (
            "human_gameplay",
            "game_state",
            "match_engine",
            "season_scheduler",
        ):
            self.assertNotIn(forbidden, source)

    def started_session(self):
        session = FrontEndSession(Backend)
        session.dispatch(StartMenuControl.NEW_GAME)
        session.choose_club(12)
        session.dispatch(TeamSelectControl.START_CONTINUE)
        return session

    def test_teamselect_start_composes_fresh_team_squad_landing(self):
        snapshot = build_fresh_management_snapshot(
            self.started_session(), bridge_factory=Bridge
        )

        self.assertEqual(snapshot.club.name, "Source Club")
        self.assertEqual(
            (snapshot.menu.selected_root_id, snapshot.menu.selected_child_id),
            (2, 0xCE),
        )
        self.assertEqual(snapshot.menu.rows[0].caption, "Team")
        self.assertEqual(snapshot.menu.rows[1].caption, "Squad")
        self.assertEqual(snapshot.source_squad_count, 23)
        self.assertEqual(snapshot.rows_beyond_initial_viewport, 3)
        self.assertEqual(len(snapshot.squad.rows), 20)
        self.assertEqual(
            tuple(row.player_id for row in snapshot.squad.rows),
            tuple(range(1000, 1020)),
        )

    def test_management_composition_rejects_pre_start_session(self):
        with self.assertRaisesRegex(
            OriginalManagementPresentationError,
            "TeamSelect Start",
        ):
            build_fresh_management_snapshot(
                FrontEndSession(Backend), bridge_factory=Bridge
            )

    def test_first_screen_presenter_method_uses_same_seam(self):
        from original_first_screen_presenter import OriginalFirstScreenPresenter

        presenter = object.__new__(OriginalFirstScreenPresenter)
        presenter.session = self.started_session()
        snapshot = presenter.fresh_management_snapshot(bridge_factory=Bridge)
        self.assertEqual(snapshot.club.club_id, 12)
        self.assertEqual(snapshot.menu.selected_child_id, 0xCE)

    def test_pmenu_navigation_integrates_fixtures_and_league_tables(self):
        fixture_staged = tuple(resource.name for resource in LEAGUE_FIXTURES_RESOURCES)
        table_staged = tuple(resource.name for resource in LEAGUE_TABLES_RESOURCES)
        presenter = OriginalManagementPresenter(
            self.started_session(),
            bridge_factory=Bridge,
            staged_league_fixture_resource_names=fixture_staged,
            staged_league_table_resource_names=table_staged,
        )

        fresh = presenter.snapshot()
        self.assertEqual((fresh.panel_code, fresh.panel_class), (0xCE, "PSquadScreen"))
        self.assertIsNotNone(fresh.squad)
        self.assertEqual(fresh.fixtures_in_source_order, ())
        self.assertIsNone(fresh.league_tables)

        fixtures = presenter.navigate(0x25C)
        self.assertEqual(
            (fixtures.panel_code, fixtures.panel_class),
            (0x25C, "PLeagueFixtures"),
        )
        self.assertEqual(fixtures.menu.selected_child_id, 0x25C)
        self.assertEqual(
            tuple(row.fixture_id for row in fixtures.fixtures_in_source_order),
            (700,),
        )
        self.assertIsNotNone(fixtures.league_fixtures)
        self.assertEqual(fixtures.league_fixtures.member_club_ids, (12, 13))
        self.assertEqual(fixtures.league_fixtures.matrix_layer_count, 1)
        self.assertTrue(fixtures.league_fixtures.exact_art_staged)
        fixture_cell = next(
            cell for cell in fixtures.league_fixtures.cells
            if cell.fixture_id == 700
        )
        self.assertEqual(fixture_cell.text, "19.08")
        self.assertEqual(fixture_cell.resource_name, "date_fixtures_box")
        self.assertIsNone(fixtures.squad)
        self.assertIsNone(fixtures.league_tables)

        league = presenter.navigate(0x25A)
        self.assertEqual(
            (league.panel_code, league.panel_class),
            (0x25A, "PLeagueTables"),
        )
        self.assertEqual(league.menu.selected_child_id, 0x25A)
        self.assertIsNotNone(league.league_tables)
        self.assertEqual(len(league.league_tables.rows), 1)
        self.assertTrue(league.league_tables.exact_art_staged)
        self.assertEqual(league.fixtures_in_source_order, ())

    def test_navigation_is_transactional_and_fails_closed_for_unintegrated_panel(self):
        presenter = OriginalManagementPresenter(
            self.started_session(), bridge_factory=Bridge
        )
        self.assertEqual(presenter.selected_child_id, 0xCE)

        with self.assertRaisesRegex(
            OriginalManagementPresentationError,
            "no integrated source-backed",
        ):
            presenter.navigate(0x25B)

        self.assertEqual(presenter.selected_child_id, 0xCE)
        self.assertEqual(presenter.snapshot().panel_class, "PSquadScreen")

    def test_fixture_match_info_action_uses_recovered_two_gate_boundary(self):
        presenter = OriginalManagementPresenter(
            self.started_session(), bridge_factory=Bridge
        )
        with self.assertRaisesRegex(
            OriginalManagementPresentationError,
            "League Fixtures",
        ):
            presenter.fixture_match_info_action(
                fixture_present=True,
                linked_context_available=True,
            )

        presenter.navigate(0x25C)
        self.assertIsNone(
            presenter.fixture_match_info_action(
                fixture_present=False,
                linked_context_available=True,
            )
        )
        self.assertIsNone(
            presenter.fixture_match_info_action(
                fixture_present=True,
                linked_context_available=False,
            )
        )
        action = presenter.fixture_match_info_action(
            fixture_present=True,
            linked_context_available=True,
        )
        self.assertIsNotNone(action)
        self.assertEqual(action.panel_class, "PMatchInfo")
        self.assertEqual(action.size, (760, 500))

    def test_direct_builder_rejects_non_integer_child_id(self):
        with self.assertRaisesRegex(
            OriginalManagementPresentationError,
            "must be an integer",
        ):
            build_management_panel_snapshot(
                self.started_session(),
                True,
                bridge_factory=Bridge,
            )


if __name__ == "__main__":
    unittest.main()
