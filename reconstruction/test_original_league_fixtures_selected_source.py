"""Native-source selected other-league fixture grid integration regressions."""
from __future__ import annotations

from dataclasses import replace
from datetime import date, timedelta
from types import SimpleNamespace
import unittest

from gate13_management_source_data import (
    ManagementPresentationError,
    ManagementSourceDataBridge,
)
from original_league_fixtures_presenter import build_league_fixtures_snapshot
from original_league_fixtures_selected_source import (
    SourceSelectedLeagueFixturesError,
    source_qualified_selected_nonpl_league_fixtures,
)
from original_league_fixtures_selector_context import (
    build_league_fixtures_selection_context,
)
from procedural_league_state import LiveProceduralLeagueState, ProceduralLeagueFixture
from test_original_league_fixtures_primary_live import (
    direct_entry,
    live_conference_fixture_state,
)


def state_two_source_leagues():
    # The managed human remains Southport349 Conference7 throughout.
    state = live_conference_fixture_state()
    state.clubs[10] = SimpleNamespace(name="Alpha", short_name="Alpha", country_id=26)
    state.clubs[11] = SimpleNamespace(name="Beta", short_name="Beta", country_id=26)
    state.club_competition_membership.update({10: 2, 11: 2})
    state.competitions[2].scheduled_matchday_count = 2
    f0, f1 = ("alt", 0), ("alt", 1)
    live = LiveProceduralLeagueState(
        competition_id=2, competition_context=0,
        fixtures={
            f0: ProceduralLeagueFixture(f0, 10, 11),
            f1: ProceduralLeagueFixture(f1, 11, 10),
        },
        club_ids=(11, 10),
    )
    live.record_result(f0, 3, 1)
    state.procedural_leagues[(2, 0)] = live
    day = date(2000, 8, 17)
    state.primary_schedule_shadow.days[day] = (
        direct_entry(f1, 11, 10, league_id=2),
    )
    state.primary_schedule_shadow.days[day + timedelta(days=7)] = (
        direct_entry(f0, 10, 11, league_id=2),
    )
    return state


def context_for(state):
    return build_league_fixtures_selection_context(
        club_id=349,
        clubs=state.clubs,
        membership=state.club_competition_membership,
        competitions=state.competitions.values(),
    )


def selected(state, context):
    return source_qualified_selected_nonpl_league_fixtures(
        human_club_id=349,
        selection=context,
        clubs=state.clubs,
        membership=state.club_competition_membership,
        competitions=state.competitions,
        procedural_leagues=state.procedural_leagues,
        days=state.primary_schedule_shadow.days,
    )


class NativeSelectedOtherSourceFixturesTests(unittest.TestCase):
    def test_alternate_league_source_grid_uses_its_own_sorted_members_and_linked_calendar(self):
        state = state_two_source_leagues()
        initial = context_for(state)
        self.assertEqual(initial.selected_competition_id, 7)
        alt = initial.accept_native_radio_event(10)  # Real England League2.
        self.assertEqual(alt.selected_competition_id, 2)
        grid = selected(state, alt)
        self.assertEqual(grid.competition_id, 2)
        self.assertEqual(grid.member_club_ids, (10, 11))
        self.assertEqual(tuple(f.node_token for f in grid.fixtures_in_source_order),
                         (("alt", 1), ("alt", 0)))
        self.assertEqual(tuple(f.played for f in grid.fixtures_in_source_order),
                         (False, True))
        self.assertEqual((grid.fixtures_in_source_order[1].home_goals,
                          grid.fixtures_in_source_order[1].away_goals), (3, 1))
        self.assertEqual(state.club_competition_membership[349], 7)

    def test_real_bridge_renders_source_selected_division_and_never_forges_native_pmatchinfo(self):
        state = state_two_source_leagues()
        alt = context_for(state).accept_native_radio_event(10)
        bridge = ManagementSourceDataBridge(
            SimpleNamespace(state=state, human=SimpleNamespace(club_id=349)))
        view = bridge.source_selected_nonpl_league_fixtures_grid_source(alt)
        self.assertEqual(view.competition_id, 2)
        self.assertEqual(tuple(x.source_node_token for x in view.fixtures_in_source_order),
                         (("alt", 1), ("alt", 0)))
        self.assertTrue(all(x.fixture_id is None for x in view.fixtures_in_source_order))
        snapshot = build_league_fixtures_snapshot(view)
        self.assertEqual(snapshot.competition_id, 2)
        self.assertEqual(
            sorted(cell.text for cell in snapshot.cells if cell.text is not None),
            ["17.08", "3:1"],
        )
        # Current-manager default is still actual Conference7.
        self.assertEqual(bridge.league_fixtures_grid_source().competition_id, 7)

    def test_source_country_first_zero_radio_cannot_use_conference_fallback(self):
        state = state_two_source_leagues()
        german = context_for(state).accept_native_radio_event(2)
        self.assertNotEqual(german.selected_competition_id, 7)
        with self.assertRaisesRegex(SourceSelectedLeagueFixturesError, "context-zero"):
            selected(state, german)

    def test_tampered_options_or_hidden_indices_fail_closed(self):
        state = state_two_source_leagues()
        alt = context_for(state).accept_native_radio_event(10)
        malformed = replace(alt, selected_league_indices=(0, 9, 0, 0, 0, 0, 0, 0))
        with self.assertRaisesRegex(SourceSelectedLeagueFixturesError, "unconstructed"):
            selected(state, malformed)
        malformed = replace(alt, league_candidates=tuple(
            (((999, "Fabricated"),) if i == 0 else row)
            for i, row in enumerate(alt.league_candidates)))
        with self.assertRaisesRegex(SourceSelectedLeagueFixturesError, "disagree"):
            selected(state, malformed)
        with self.assertRaises(SourceSelectedLeagueFixturesError):
            selected(state, replace(alt, active_country_index=True))

    def test_separate_original_premier_league_fixed_source_does_not_fall_back(self):
        state = state_two_source_leagues()
        first = context_for(state).accept_native_radio_event(9)
        with self.assertRaisesRegex(SourceSelectedLeagueFixturesError, "distinct original"):
            selected(state, first)

    def test_incomplete_selected_roster_rejected_before_any_mock_fixture_is_returned(self):
        state = state_two_source_leagues()
        alt = context_for(state).accept_native_radio_event(10)
        state.club_competition_membership.pop(11)
        with self.assertRaisesRegex(SourceSelectedLeagueFixturesError, "participants disagree"):
            selected(state, alt)

    def test_missing_original_calendar_refuses_bridge_projection(self):
        state = state_two_source_leagues()
        bridge = ManagementSourceDataBridge(
            SimpleNamespace(state=state, human=SimpleNamespace(club_id=349)))
        alt = context_for(state).accept_native_radio_event(10)
        del state.primary_schedule_shadow
        with self.assertRaises(ManagementPresentationError):
            bridge.source_selected_nonpl_league_fixtures_grid_source(alt)


if __name__ == "__main__":
    unittest.main()
