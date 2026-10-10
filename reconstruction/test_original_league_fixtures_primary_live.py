"""Native-source-linked non-PL fixture matrix integration and strict boundaries."""

from __future__ import annotations

from dataclasses import replace
from datetime import date, timedelta
from types import SimpleNamespace
import unittest

from gate13_management_source_data import (
    ManagementPresentationError,
    ManagementSourceDataBridge,
)
from original_league_fixtures_presenter import (
    OriginalLeagueFixturesPresentationError,
    build_league_fixtures_snapshot,
)
from original_league_fixtures_prepared_members import original_current_league_fixtures_prepared_members
from original_league_fixtures_primary_live import (
    SourcePrimaryLeagueFixturesError,
    qualified_primary_league_fixtures,
)
from original_league_fixtures_resources import LEAGUE_FIXTURES_RESOURCES
from test_original_league_fixtures_prepared_members import source


def direct_entry(token, home, away, *, bits=0, league_id=7, cache=None):
    if cache is None:
        cache = (home, away)
    return SimpleNamespace(
        node_kind="league_match",
        competition_id=league_id,
        competition_context=0,
        node_token=token,
        payload_filter_bits=bits,
        side_club_cache=cache,
    )


def live_conference_fixture_state():
    """Two-club synthetic miniature using actual Conference/Scotland IDs.

    The 22-member real Conference identity and radio 13 are separately proven
    in test_original_league_fixtures_prepared_members. These two club cases
    exercise the native 373-head/grid data path without inventing 462 original
    scores, historical dates or hidden match-info report identities.
    """
    state = source(member_count=2)
    state.competitions[7].scheduled_matchday_count = 2
    original = state.procedural_leagues[(7, 0)]
    # Source fixture tokens: ("fixture",0) 349(home)→200,
    # ("fixture",1) 200(home)→349.
    token0, token1 = ("fixture", 0), ("fixture", 1)
    original.record_result(token0, 2, 1)
    day0 = date(2000, 8, 19)
    day1 = date(2000, 8, 26)
    state.primary_schedule_shadow = SimpleNamespace(days={
        day0: (
            direct_entry(("scottish",), 999, 998, league_id=27),
            direct_entry(token1, 200, 349),
        ),
        day1: (direct_entry(token0, 349, 200),),
    })
    return state


def live_candidates(state):
    member = original_current_league_fixtures_prepared_members(
        human_club_id=349,
        membership=state.club_competition_membership,
        clubs=state.clubs,
        competitions=state.competitions,
        procedural_leagues=state.procedural_leagues,
    )
    return qualified_primary_league_fixtures(
        competition_id=7,
        member_club_ids=member.member_club_ids,
        scheduled_matchday_count=state.competitions[7].scheduled_matchday_count,
        live=state.procedural_leagues[(7, 0)],
        days=state.primary_schedule_shadow.days,
    )


class SourceLiveConferenceFixturesTests(unittest.TestCase):
    def test_nonpl_uses_original_373_head_encounter_and_real_scores(self):
        state = live_conference_fixture_state()
        result = live_candidates(state)
        self.assertEqual(result.competition_id, 7)
        self.assertEqual(result.member_club_ids, (349, 200))
        self.assertEqual(result.schedule_cycle_count, 2)
        self.assertEqual(result.matrix_layer_count, 1)
        self.assertEqual(
            tuple(f.node_token for f in result.fixtures_in_source_order),
            (("fixture", 1), ("fixture", 0)),
        )
        self.assertEqual(
            tuple(f.native_encounter_index for f in result.fixtures_in_source_order),
            (1, 2),
        )
        self.assertFalse(result.fixtures_in_source_order[0].played)
        self.assertTrue(result.fixtures_in_source_order[1].played)
        self.assertEqual(
            (result.fixtures_in_source_order[1].home_goals,
             result.fixtures_in_source_order[1].away_goals), (2, 1),
        )
        self.assertEqual(len(state.procedural_leagues[(7, 0)].results), 1)

    def test_real_management_bridge_and_rendered_matrix_without_fake_native_id(self):
        state = live_conference_fixture_state()
        controller = SimpleNamespace(
            state=state,
            human=SimpleNamespace(club_id=349),
        )
        bridge = ManagementSourceDataBridge(controller)
        source_view = bridge.league_fixtures_grid_source()
        self.assertEqual(source_view.competition_id, 7)
        self.assertEqual(source_view.member_club_ids, (349, 200))
        self.assertEqual(
            tuple(row.source_fixture_index for row in source_view.fixtures_in_source_order),
            (1, 2),
        )
        self.assertTrue(all(row.fixture_id is None
                            and type(row.source_node_token) is tuple
                            for row in source_view.fixtures_in_source_order))
        self.assertEqual(tuple(row.round_index for row
                               in source_view.fixtures_in_source_order), (None, None))
        surface = build_league_fixtures_snapshot(
            source_view,
            staged_resource_names=tuple(x.name for x in LEAGUE_FIXTURES_RESOURCES),
        )
        self.assertEqual(surface.competition_id, 7)
        self.assertTrue(surface.exact_art_staged)
        cells = {(cell.row, cell.column): cell for cell in surface.cells}
        # Native standings reorder the selected League after a 2:1 result:
        # source row0=Southport349, row1=club200.
        self.assertIsNone(cells[(1, 0)].fixture_id)
        self.assertEqual(cells[(1, 0)].source_node_token, ("fixture", 1))
        self.assertEqual(cells[(1, 0)].text, "19.08")
        self.assertIsNone(cells[(0, 1)].fixture_id)
        self.assertEqual(cells[(0, 1)].source_node_token, ("fixture", 0))
        self.assertEqual(cells[(0, 1)].text, "2:1")
        self.assertEqual(cells[(0, 0)].resource_name, "red_fixtures_box")

    def test_right_click_cannot_forge_native_numeric_report_pointer(self):
        state = live_conference_fixture_state()
        src = ManagementSourceDataBridge(SimpleNamespace(
            state=state, human=SimpleNamespace(club_id=349),
        )).league_fixtures_grid_source()
        tampered = replace(src, fixtures_in_source_order=(
            replace(src.fixtures_in_source_order[0], fixture_id=123),
            src.fixtures_in_source_order[1],
        ))
        with self.assertRaisesRegex(
            OriginalLeagueFixturesPresentationError, "fabricated native"
        ):
            build_league_fixtures_snapshot(tampered)
        tampered2 = replace(src, fixtures_in_source_order=(
            replace(src.fixtures_in_source_order[0], source_node_token=None),
            src.fixtures_in_source_order[1],
        ))
        with self.assertRaisesRegex(
            OriginalLeagueFixturesPresentationError, "opaque source token"
        ):
            build_league_fixtures_snapshot(tampered2)

    def test_unknown_source_status_fails_closed_without_noop_fixtures(self):
        state = live_conference_fixture_state()
        old = state.primary_schedule_shadow.days
        date0 = min(old)
        old[date0] = (old[date0][0], replace_or_copy(
            old[date0][1], payload_filter_bits=None))
        with self.assertRaisesRegex(
            SourcePrimaryLeagueFixturesError, "source status bits are unknown"
        ):
            live_candidates(state)

    def test_original_source_excluded_status_bit20_filters_only_that_match(self):
        state = live_conference_fixture_state()
        days = state.primary_schedule_shadow.days
        day1 = max(days)
        days[day1] = (replace_or_copy(days[day1][0], payload_filter_bits=0x20),)
        result = live_candidates(state)
        self.assertEqual(tuple(x.node_token for x in result.fixtures_in_source_order),
                         (("fixture", 1),))

    def test_unrepresented_or_repeated_source_token_is_rejected(self):
        state = live_conference_fixture_state()
        state.primary_schedule_shadow.days.pop(max(state.primary_schedule_shadow.days))
        with self.assertRaisesRegex(
            SourcePrimaryLeagueFixturesError, "omit live selected-League"
        ):
            live_candidates(state)
        state = live_conference_fixture_state()
        days = state.primary_schedule_shadow.days
        day1 = max(days)
        days[day1] = (days[day1][0], days[day1][0])
        with self.assertRaisesRegex(
            SourcePrimaryLeagueFixturesError, "duplicate or unmapped"
        ):
            live_candidates(state)

    def test_partial_schedule_does_not_pretend_complete_original_season(self):
        state = live_conference_fixture_state()
        state.competitions[7].scheduled_matchday_count = 42
        with self.assertRaisesRegex(
            SourcePrimaryLeagueFixturesError, "schedule is incomplete"
        ):
            live_candidates(state)

    def test_ambiguous_side_cache_and_unknown_member_reject_source_join(self):
        state = live_conference_fixture_state()
        days = state.primary_schedule_shadow.days
        day1 = max(days)
        days[day1] = (replace_or_copy(days[day1][0], side_club_cache=(200, 349)),)
        with self.assertRaisesRegex(
            SourcePrimaryLeagueFixturesError, "cache disagrees"
        ):
            live_candidates(state)
        state = live_conference_fixture_state()
        state.procedural_leagues[(7, 0)].fixtures[("fixture", 0)] = SimpleNamespace(
            node_token=("fixture", 0), home_club_id=999, away_club_id=200,
        )
        with self.assertRaisesRegex(
            SourcePrimaryLeagueFixturesError, "do not resolve"
        ):
            live_candidates(state)

    def test_manager_scottish_league_does_not_fall_back_to_conference_or_pl(self):
        state = live_conference_fixture_state()
        state.club_competition_membership[349] = 27
        controller = SimpleNamespace(state=state, human=SimpleNamespace(club_id=349))
        with self.assertRaises(ManagementPresentationError):
            ManagementSourceDataBridge(controller).league_fixtures_grid_source()

    def test_native_repeat_slot_enforces_source_layer_capacity(self):
        state = live_conference_fixture_state()
        state.procedural_leagues[(7, 0)].fixtures[("fixture", 1)] = SimpleNamespace(
            node_token=("fixture", 1), home_club_id=349, away_club_id=200,
        )
        days = state.primary_schedule_shadow.days
        day0 = min(days)
        days[day0] = (days[day0][0], direct_entry(("fixture", 1), 349, 200))
        with self.assertRaisesRegex(
            SourcePrimaryLeagueFixturesError, "exceeds its native"
        ):
            live_candidates(state)


def replace_or_copy(obj, **kwargs):
    values = vars(obj).copy()
    values.update(kwargs)
    return SimpleNamespace(**values)


if __name__ == "__main__":
    unittest.main()
